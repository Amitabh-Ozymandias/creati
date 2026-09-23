"""
VidyaSearch — In-Memory Embedding Store

Maintains an in-memory NumPy matrix of all document embeddings loaded from
the SQLite `documents.embedding` column. Supports:
  - Bulk loading on startup
  - Incremental upsert when new docs are embedded
  - Fast cosine-similarity search (dot product on L2-normalised vectors)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Tuple

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class EmbeddingStore:
    """
    In-memory store for document embeddings.

    Internally keeps:
      - _matrix: np.ndarray of shape (N, D), float32 — row-per-document
      - _doc_ids: list[int]  — parallel array mapping row index → document id
      - _id_to_row: dict[int, int] — reverse mapping for upserts
    """

    _instance: "EmbeddingStore | None" = None
    _lock: asyncio.Lock | None = None

    def __init__(self) -> None:
        self._matrix: np.ndarray = np.empty((0, 0), dtype=np.float32)
        self._doc_ids: List[int] = []
        self._id_to_row: Dict[int, int] = {}

    # ------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------

    @classmethod
    def _get_lock(cls) -> asyncio.Lock:
        if cls._lock is None:
            cls._lock = asyncio.Lock()
        return cls._lock

    @classmethod
    def get_instance(cls) -> "EmbeddingStore":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    async def load_from_db(self, session: AsyncSession) -> int:
        """
        (Re)load all stored embeddings from the `documents` table.

        Only rows where `embedding IS NOT NULL` are loaded.
        Returns the number of vectors loaded.
        """
        from app.models.document import Document  # local import to avoid circularity

        stmt = select(Document.id, Document.embedding).where(
            Document.embedding.is_not(None)
        )
        result = await session.execute(stmt)
        rows = result.all()

        if not rows:
            logger.info("[EmbeddingStore] No embeddings found in DB.")
            self._matrix = np.empty((0, 0), dtype=np.float32)
            self._doc_ids = []
            self._id_to_row = {}
            return 0

        doc_ids = []
        vecs = []
        for doc_id, blob in rows:
            try:
                vec = np.frombuffer(blob, dtype=np.float32)
                doc_ids.append(doc_id)
                vecs.append(vec)
            except Exception as exc:
                logger.warning("[EmbeddingStore] Skipping doc %d: %s", doc_id, exc)

        if not vecs:
            return 0

        matrix = np.stack(vecs, axis=0)  # (N, D)

        async with self._get_lock():
            self._matrix = matrix
            self._doc_ids = doc_ids
            self._id_to_row = {doc_id: idx for idx, doc_id in enumerate(doc_ids)}

        logger.info(
            "[EmbeddingStore] Loaded %d embeddings (dim=%d)",
            len(doc_ids),
            matrix.shape[1],
        )
        return len(doc_ids)

    # ------------------------------------------------------------------
    # Upsert
    # ------------------------------------------------------------------

    def upsert(self, doc_id: int, embedding: np.ndarray) -> None:
        """
        Add or update a single document's embedding in the in-memory store.
        Thread-safe (GIL protects NumPy array construction here).
        """
        vec = embedding.astype(np.float32).reshape(1, -1)

        if doc_id in self._id_to_row:
            row = self._id_to_row[doc_id]
            self._matrix[row] = vec
        else:
            if self._matrix.shape[0] == 0:
                self._matrix = vec
            else:
                self._matrix = np.vstack([self._matrix, vec])
            new_row = len(self._doc_ids)
            self._doc_ids.append(doc_id)
            self._id_to_row[doc_id] = new_row

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def cosine_search(
        self,
        query_vec: np.ndarray,
        top_k: int = 100,
    ) -> List[Tuple[int, float]]:
        """
        Return the top-K (doc_id, similarity_score) pairs most similar to
        the query vector.

        Since all stored vectors AND the query vector are L2-normalised,
        cosine similarity = dot product — computed via a single matrix-vector
        multiply, O(N·D), which is extremely fast for N ≤ 50 000.

        Args:
            query_vec: 1-D float32 array of shape (D,).
            top_k: Maximum number of results.

        Returns:
            List of (doc_id, score) sorted by descending score.
        """
        n = self._matrix.shape[0]
        if n == 0:
            return []

        q = query_vec.astype(np.float32).ravel()
        scores: np.ndarray = self._matrix @ q  # shape (N,)

        # Pick top_k without full sort (argpartition is O(N) avg)
        k = min(top_k, n)
        top_indices = np.argpartition(scores, -k)[-k:]
        top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

        return [
            (self._doc_ids[idx], float(scores[idx]))
            for idx in top_indices
        ]

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    @property
    def count(self) -> int:
        return self._matrix.shape[0]

    @property
    def is_empty(self) -> bool:
        return self._matrix.shape[0] == 0

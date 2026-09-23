"""
VidyaSearch — Semantic Encoder

Wraps sentence-transformers to produce dense vector embeddings for documents
and queries. Uses a singleton pattern so the heavy model is loaded only once.
"""

from __future__ import annotations

import asyncio
import logging
from typing import List

import numpy as np

logger = logging.getLogger(__name__)

# Lazy import — sentence-transformers is only imported when first used,
# so the rest of the app starts instantly even if the library is large.
_SentenceTransformer = None


def _get_st_class():
    global _SentenceTransformer
    if _SentenceTransformer is None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            _SentenceTransformer = SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed. "
                "Run: pip install sentence-transformers"
            ) from exc
    return _SentenceTransformer


class SemanticEncoder:
    """
    Singleton wrapper around a SentenceTransformer model.

    Usage:
        encoder = await SemanticEncoder.get_instance()
        query_vec = encoder.encode_query("machine learning optimization")
        doc_vecs  = encoder.encode(["text one", "text two"])
    """

    _instance: "SemanticEncoder | None" = None
    _lock: asyncio.Lock | None = None

    def __init__(self, model_name: str):
        logger.info("[SemanticEncoder] Loading model '%s'…", model_name)
        SentenceTransformer = _get_st_class()
        self._model = SentenceTransformer(model_name)
        self._model_name = model_name
        self._dim = self._model.get_sentence_embedding_dimension()
        logger.info(
            "[SemanticEncoder] Model loaded — embedding dim=%d", self._dim
        )

    # ------------------------------------------------------------------
    # Singleton lifecycle
    # ------------------------------------------------------------------

    @classmethod
    def _get_lock(cls) -> asyncio.Lock:
        if cls._lock is None:
            cls._lock = asyncio.Lock()
        return cls._lock

    @classmethod
    async def get_instance(cls, model_name: str = "all-MiniLM-L6-v2") -> "SemanticEncoder":
        """Return (or lazily create) the shared encoder instance."""
        if cls._instance is None:
            async with cls._get_lock():
                if cls._instance is None:
                    # Run heavy model load in a thread pool so we don't block
                    # the event loop during startup.
                    loop = asyncio.get_event_loop()
                    cls._instance = await loop.run_in_executor(
                        None, lambda: cls(model_name)
                    )
        return cls._instance

    @classmethod
    def get_instance_sync(cls, model_name: str = "all-MiniLM-L6-v2") -> "SemanticEncoder":
        """Synchronous singleton getter — only call from non-async context."""
        if cls._instance is None:
            cls._instance = cls(model_name)
        return cls._instance

    # ------------------------------------------------------------------
    # Encoding API
    # ------------------------------------------------------------------

    @property
    def embedding_dim(self) -> int:
        return self._dim

    def encode(self, texts: List[str], batch_size: int = 64) -> np.ndarray:
        """
        Encode a list of texts into an (N, D) float32 numpy matrix.

        Args:
            texts: Raw text strings to encode.
            batch_size: Batch size passed to the transformer.

        Returns:
            numpy.ndarray of shape (len(texts), embedding_dim), dtype float32.
        """
        if not texts:
            return np.empty((0, self._dim), dtype=np.float32)

        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,   # L2-normalised → cosine sim = dot product
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a single query string into a (D,) float32 vector.

        Returns:
            1-D numpy.ndarray of shape (embedding_dim,), dtype float32.
        """
        vec = self._model.encode(
            query,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return vec.astype(np.float32)

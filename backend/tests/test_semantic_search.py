"""
VidyaSearch — Semantic Search Unit & Integration Tests

Tests the SemanticEncoder, EmbeddingStore, and semantic ranking path
without requiring the full sentence-transformers model (uses mocking).
"""

import asyncio
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.semantic.embedding_store import EmbeddingStore
from app.seed.seeder import seed_database
from app.ranking.ranker import Ranker
from app.schemas.search import SearchResultItem


class TestEmbeddingStore(unittest.TestCase):
    """Unit tests for the in-memory EmbeddingStore."""

    def setUp(self):
        # Reset singleton for isolation
        EmbeddingStore._instance = None

    def tearDown(self):
        EmbeddingStore._instance = None

    def test_singleton(self):
        """EmbeddingStore.get_instance() always returns the same object."""
        a = EmbeddingStore.get_instance()
        b = EmbeddingStore.get_instance()
        self.assertIs(a, b)

    def test_initially_empty(self):
        store = EmbeddingStore.get_instance()
        self.assertTrue(store.is_empty)
        self.assertEqual(store.count, 0)

    def test_upsert_and_cosine_search(self):
        """Insert two orthogonal vectors; query with first vector returns it ranked highest."""
        store = EmbeddingStore.get_instance()

        # Two orthogonal unit vectors in 4D
        v1 = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        v2 = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)

        store.upsert(doc_id=1, embedding=v1)
        store.upsert(doc_id=2, embedding=v2)

        self.assertEqual(store.count, 2)

        # Query with v1 → doc 1 should be top result
        results = store.cosine_search(v1, top_k=2)
        self.assertEqual(len(results), 2)
        top_doc_id, top_score = results[0]
        self.assertEqual(top_doc_id, 1)
        self.assertAlmostEqual(top_score, 1.0, places=4)

    def test_upsert_update_existing(self):
        """Upserting an existing doc_id updates the vector in-place."""
        store = EmbeddingStore.get_instance()
        v1 = np.array([1.0, 0.0], dtype=np.float32)
        v2 = np.array([0.0, 1.0], dtype=np.float32)

        store.upsert(doc_id=42, embedding=v1)
        self.assertAlmostEqual(store._matrix[0, 0], 1.0, places=4)

        store.upsert(doc_id=42, embedding=v2)
        self.assertEqual(store.count, 1)  # count should not grow
        self.assertAlmostEqual(store._matrix[0, 0], 0.0, places=4)
        self.assertAlmostEqual(store._matrix[0, 1], 1.0, places=4)

    def test_cosine_search_empty_store(self):
        """cosine_search on an empty store returns []."""
        store = EmbeddingStore.get_instance()
        q = np.array([1.0, 0.0], dtype=np.float32)
        self.assertEqual(store.cosine_search(q, top_k=5), [])

    def test_cosine_search_top_k_clamping(self):
        """top_k larger than store size should not crash."""
        store = EmbeddingStore.get_instance()
        for i in range(3):
            v = np.zeros(4, dtype=np.float32)
            v[i % 4] = 1.0
            store.upsert(doc_id=i + 1, embedding=v)

        q = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        results = store.cosine_search(q, top_k=100)
        self.assertEqual(len(results), 3)


class TestSemanticEncoderMocked(unittest.TestCase):
    """Unit tests for SemanticEncoder using a mocked SentenceTransformer."""

    def setUp(self):
        # Reset singleton
        from app.semantic.semantic_encoder import SemanticEncoder
        SemanticEncoder._instance = None

    def tearDown(self):
        from app.semantic.semantic_encoder import SemanticEncoder
        SemanticEncoder._instance = None

    @patch("app.semantic.semantic_encoder._get_st_class")
    def test_encode_returns_float32_array(self, mock_get_st):
        """encode() returns float32 numpy array of correct shape."""
        from app.semantic.semantic_encoder import SemanticEncoder

        # Mock the SentenceTransformer class
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.random.randn(2, 384).astype(np.float32)
        mock_class = MagicMock(return_value=mock_model)
        mock_get_st.return_value = mock_class

        encoder = SemanticEncoder("all-MiniLM-L6-v2")
        vecs = encoder.encode(["hello", "world"])

        self.assertEqual(vecs.dtype, np.float32)
        self.assertEqual(vecs.shape, (2, 384))

    @patch("app.semantic.semantic_encoder._get_st_class")
    def test_encode_empty_list_returns_empty_array(self, mock_get_st):
        """encode([]) returns an empty (0, D) array without crashing."""
        from app.semantic.semantic_encoder import SemanticEncoder

        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_class = MagicMock(return_value=mock_model)
        mock_get_st.return_value = mock_class

        encoder = SemanticEncoder("all-MiniLM-L6-v2")
        vecs = encoder.encode([])

        self.assertEqual(vecs.shape[0], 0)
        self.assertEqual(vecs.shape[1], 384)


class TestSemanticSearchIntegration(unittest.IsolatedAsyncioTestCase):
    """
    Full integration test: boot in-memory SQLite, seed docs, build fake
    embeddings, and verify semantic_search() returns valid SearchResultItems.
    """

    async def asyncSetUp(self):
        """Create in-memory SQLite DB with seed data."""
        from app.database import Base

        # Use in-memory SQLite
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        self.session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with self.session_factory() as session:
            await seed_database(session)

        EmbeddingStore._instance = None

    async def asyncTearDown(self):
        EmbeddingStore._instance = None

    async def test_semantic_search_returns_empty_when_no_embeddings(self):
        """semantic_search returns [] when EmbeddingStore is empty."""
        async with self.session_factory() as session:
            ranker = Ranker(session=session)
            results = await ranker.semantic_search("machine learning")
        self.assertEqual(results, [])

    async def test_semantic_search_returns_results_with_fake_embeddings(self):
        """semantic_search returns SearchResultItems when embeddings are present."""
        from app.models.document import Document
        from sqlalchemy import select

        dim = 384
        store = EmbeddingStore.get_instance()

        async with self.session_factory() as session:
            # Fetch seeded docs and give them random unit-norm embeddings
            result = await session.execute(select(Document))
            docs = result.scalars().all()
            self.assertGreater(len(docs), 0, "No seeded documents found")

            for doc in docs:
                vec = np.random.randn(dim).astype(np.float32)
                vec /= np.linalg.norm(vec)
                doc.embedding = vec.tobytes()
                store.upsert(doc.id, vec)

            await session.commit()

        async with self.session_factory() as session:
            # Patch SemanticEncoder so it doesn't download the real model
            from app.semantic import semantic_encoder as enc_module
            mock_encoder = MagicMock()
            query_vec = np.random.randn(dim).astype(np.float32)
            query_vec /= np.linalg.norm(query_vec)
            mock_encoder.encode_query.return_value = query_vec
            enc_module.SemanticEncoder._instance = mock_encoder

            ranker = Ranker(session=session)
            results = await ranker.semantic_search("neural networks", limit=5)

        # Should have some results (at least 1)
        self.assertGreater(len(results), 0)

        # Each result should be a valid SearchResultItem
        for r in results:
            self.assertIsInstance(r, SearchResultItem)
            self.assertIsInstance(r.doc_id, int)
            self.assertIsInstance(r.url, str)
            self.assertIsInstance(r.score, float)
            self.assertGreaterEqual(r.score, 0.0)

    async def _embed_seeded_docs(self, dim: int = 384) -> np.ndarray:
        """Give every seeded doc a random embedding and install a mock encoder."""
        from app.models.document import Document
        from app.semantic import semantic_encoder as enc_module
        from sqlalchemy import select

        store = EmbeddingStore.get_instance()
        async with self.session_factory() as session:
            docs = (await session.execute(select(Document))).scalars().all()
            for doc in docs:
                vec = np.random.randn(dim).astype(np.float32)
                vec /= np.linalg.norm(vec)
                doc.embedding = vec.tobytes()
                store.upsert(doc.id, vec)
            await session.commit()

        query_vec = np.random.randn(dim).astype(np.float32)
        query_vec /= np.linalg.norm(query_vec)
        mock_encoder = MagicMock()
        mock_encoder.encode_query.return_value = query_vec
        enc_module.SemanticEncoder._instance = mock_encoder
        return query_vec

    async def test_hybrid_falls_back_to_bm25_without_embeddings(self):
        """With an empty EmbeddingStore, hybrid ranks exactly like BM25."""
        async with self.session_factory() as session:
            ranker = Ranker(session=session)
            bm25 = await ranker.search("machine learning", ranking_method="bm25")
            hybrid = await ranker.search("machine learning", ranking_method="hybrid")

        self.assertGreater(len(hybrid), 0)
        self.assertEqual([r.doc_id for r in hybrid], [r.doc_id for r in bm25])

    async def test_hybrid_fuses_keyword_and_semantic_results(self):
        """Hybrid returns the union of both lists, scored 0-1 and sorted."""
        await self._embed_seeded_docs()

        async with self.session_factory() as session:
            ranker = Ranker(session=session)
            bm25 = await ranker.search("machine learning", ranking_method="bm25", limit=100)
            semantic = await ranker.semantic_search("machine learning", limit=100)
            hybrid = await ranker.search("machine learning", ranking_method="hybrid", limit=100)

        expected_ids = {r.doc_id for r in bm25} | {r.doc_id for r in semantic}
        self.assertEqual({r.doc_id for r in hybrid}, expected_ids)

        scores = [r.score for r in hybrid]
        self.assertEqual(scores, sorted(scores, reverse=True))
        for s in scores:
            self.assertGreater(s, 0.0)
            self.assertLessEqual(s, 1.0)

    async def test_hybrid_ranks_docs_found_by_both_retrievers_higher(self):
        """A doc ranked #1 by both BM25 and semantic gets the maximum score of 1.0."""
        from unittest.mock import patch
        from app.config import settings
        from app.semantic import semantic_encoder as enc_module

        await self._embed_seeded_docs()

        # Pure cosine ranking, so the exact-match vector is guaranteed rank 1
        with patch.object(settings, "semantic_pagerank_weight", 0.0):
            async with self.session_factory() as session:
                ranker = Ranker(session=session)
                bm25 = await ranker.search("machine learning", ranking_method="bm25")
                top_doc = bm25[0].doc_id

                # Make the query vector identical to the BM25 winner's embedding
                store = EmbeddingStore.get_instance()
                winner_vec = store._matrix[store._id_to_row[top_doc]]
                enc_module.SemanticEncoder._instance.encode_query.return_value = winner_vec

                hybrid = await ranker.search("machine learning", ranking_method="hybrid")

        self.assertEqual(hybrid[0].doc_id, top_doc)
        self.assertEqual(hybrid[0].score, 1.0)

if __name__ == "__main__":
    unittest.main()

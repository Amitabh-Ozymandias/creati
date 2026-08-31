"""
VidyaSearch — Complete Backend Unit and Integration Test Suite
Supports both pytest and standard python unittest runners.
"""

import asyncio
import unittest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.indexer.tokenizer import tokenize, tokenize_with_positions
from app.indexer.normalizer import simple_stem, filter_stopwords
from app.ranking.bm25 import BM25Scorer
from app.ranking.tf_idf import TFIDFScorer
from app.ranking.query_parser import QueryParser
from app.ranking.snippet_generator import SnippetGenerator
from app.autocomplete.trie import Trie
from app.typo.spell_checker import levenshtein_distance, SpellChecker
from app.pagerank.pagerank import PageRankCalculator
from app.cache.query_cache import QueryCache
from app.seed.seeder import seed_database
from app.ranking.ranker import Ranker


class TestSearchEngineUnits(unittest.TestCase):
    def test_tokenizer(self):
        text = "NPTEL Data Structures & Algorithms, IIT-Delhi 2026!"
        tokens = tokenize(text)
        self.assertIn("nptel", tokens)
        self.assertIn("data", tokens)
        self.assertIn("structures", tokens)
        self.assertIn("algorithms", tokens)

    def test_stemmer(self):
        self.assertEqual(simple_stem("algorithms"), "algorithm")
        self.assertEqual(simple_stem("learning"), "learn")
        self.assertEqual(simple_stem("databases"), "database")
        self.assertEqual(simple_stem("optimization"), "optimize")

    def test_trie_autocomplete(self):
        trie = Trie()
        trie.insert("machine learning", frequency=10)
        trie.insert("machine learning nptel", frequency=15)
        trie.insert("matrix multiplication", frequency=2)

        suggestions = trie.search_prefix("mach")
        self.assertGreaterEqual(len(suggestions), 2)
        self.assertEqual(suggestions[0], "machine learning nptel")

    def test_levenshtein_distance(self):
        self.assertEqual(levenshtein_distance("algoritm", "algorithm"), 1)
        self.assertEqual(levenshtein_distance("nptel", "nptel"), 0)
        self.assertEqual(levenshtein_distance("learing", "learning"), 1)

    def test_spell_checker(self):
        checker = SpellChecker()
        checker._vocab_freq = {"algorithm": 10, "machine": 8, "learning": 9}

        self.assertEqual(checker.correct_word("algoritm"), "algorithm")
        self.assertEqual(checker.correct_word("learing"), "learning")
        self.assertEqual(checker.correct_query("machne learing"), "machine learning")

    def test_bm25_scorer(self):
        bm25 = BM25Scorer(k1=1.5, b=0.75)
        score1 = bm25.score_term(tf=3, df=2, doc_length=100, avg_doc_length=100.0, total_docs=10)
        score0 = bm25.score_term(tf=0, df=2, doc_length=100, avg_doc_length=100.0, total_docs=10)
        self.assertGreater(score1, 0.0)
        self.assertEqual(score0, 0.0)

    def test_tfidf_scorer(self):
        tfidf = TFIDFScorer()
        score = tfidf.score_document(
            term_frequencies={"data": 3, "structur": 2},
            doc_frequencies={"data": 5, "structur": 3},
            query_terms=["data", "structur"],
            total_docs=10,
        )
        self.assertGreater(score, 0.0)

    def test_query_parser(self):
        parsed = QueryParser.parse('"operating systems" memory -windows site:iitd.ac.in')
        self.assertEqual(parsed.site_filter, "iitd.ac.in")
        self.assertIn("window", parsed.excluded_terms)
        self.assertEqual(len(parsed.phrases), 1)
        self.assertTrue("operat" in parsed.phrases[0] or "system" in parsed.phrases[0])

    def test_query_parser_boolean_operators(self):
        parsed_and = QueryParser.parse('Python AND "Machine Learning" NOT syllabus')
        self.assertEqual(parsed_and.operator, "AND")
        self.assertTrue("syllabu" in parsed_and.excluded_terms or "syllabus" in parsed_and.excluded_terms)
        self.assertEqual(len(parsed_and.phrases), 1)

        parsed_or = QueryParser.parse('algorithms OR structures NOT java')
        self.assertEqual(parsed_or.operator, "OR")
        self.assertIn("java", parsed_or.excluded_terms)
        self.assertTrue("algorithm" in parsed_or.terms or "structur" in parsed_or.terms)

    def test_snippet_generator(self):
        text = "The quick brown fox jumps over the lazy dog. Prof Naveen Garg teaches Data Structures and Algorithms at IIT Delhi."
        snippet = SnippetGenerator.generate_snippet(text, ["Data", "Structures"])
        self.assertIn("<mark>", snippet)
        self.assertTrue("Data" in snippet or "Structures" in snippet)

    def test_pagerank_calculation(self):
        nodes = ["pageA", "pageB", "pageC"]
        edges = [("pageA", "pageB"), ("pageB", "pageC"), ("pageC", "pageA")]
        ranks = PageRankCalculator.compute_pagerank(nodes, edges)
        self.assertEqual(len(ranks), 3)
        self.assertAlmostEqual(ranks["pageA"], ranks["pageB"], places=4)

    def test_query_cache(self):
        cache = QueryCache(max_size=10, ttl_seconds=60)
        key = QueryCache.make_key("machine learning", 1, 10, "bm25")
        cache.set(key, {"sample": "results"})
        self.assertEqual(cache.get(key), {"sample": "results"})
        stats = cache.get_stats()
        self.assertEqual(stats["hits"], 1)


class TestSearchEngineIntegration(unittest.IsolatedAsyncioTestCase):
    async def test_full_search_flow(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session() as session:
            result = await seed_database(session, force=True)
            self.assertGreater(result["documents_added"], 0)
            self.assertGreater(result["indexed_entries"], 0)

            ranker = Ranker(session=session)
            search_results = await ranker.search("Machine Learning IIT Madras")
            self.assertGreater(len(search_results), 0)
            self.assertIn("Machine Learning", search_results[0].title)
            self.assertGreater(search_results[0].score, 0)

            tfidf_results = await ranker.search("Operating Systems", ranking_method="tfidf")
            self.assertGreater(len(tfidf_results), 0)

        await engine.dispose()


if __name__ == "__main__":
    unittest.main()

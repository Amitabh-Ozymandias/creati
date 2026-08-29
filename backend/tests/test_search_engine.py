"""
VidyaSearch — Complete Backend Unit and Integration Test Suite
"""

import pytest
import pytest_asyncio
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


def test_tokenizer():
    text = "NPTEL Data Structures & Algorithms, IIT-Delhi 2026!"
    tokens = tokenize(text)
    assert "nptel" in tokens
    assert "data" in tokens
    assert "structures" in tokens
    assert "algorithms" in tokens


def test_stemmer():
    assert simple_stem("algorithms") == "algorithm"
    assert simple_stem("learning") == "learn"
    assert simple_stem("databases") == "database"
    assert simple_stem("optimization") == "optimize"


def test_trie_autocomplete():
    trie = Trie()
    trie.insert("machine learning", frequency=10)
    trie.insert("machine learning nptel", frequency=15)
    trie.insert("matrix multiplication", frequency=2)

    suggestions = trie.search_prefix("mach")
    assert len(suggestions) >= 2
    assert suggestions[0] == "machine learning nptel"  # higher frequency first


def test_levenshtein_distance():
    assert levenshtein_distance("algoritm", "algorithm") == 1
    assert levenshtein_distance("nptel", "nptel") == 0
    assert levenshtein_distance("learing", "learning") == 1


def test_spell_checker():
    checker = SpellChecker()
    checker._vocab_freq = {"algorithm": 10, "machine": 8, "learning": 9}

    assert checker.correct_word("algoritm") == "algorithm"
    assert checker.correct_word("learing") == "learning"
    assert checker.correct_query("machne learing") == "machine learning"


def test_bm25_scorer():
    bm25 = BM25Scorer(k1=1.5, b=0.75)
    # Term in doc vs term not in doc
    score1 = bm25.score_term(tf=3, df=2, doc_length=100, avg_doc_length=100.0, total_docs=10)
    score0 = bm25.score_term(tf=0, df=2, doc_length=100, avg_doc_length=100.0, total_docs=10)
    assert score1 > 0.0
    assert score0 == 0.0


def test_tfidf_scorer():
    tfidf = TFIDFScorer()
    score = tfidf.score_document(
        term_frequencies={"data": 3, "structur": 2},
        doc_frequencies={"data": 5, "structur": 3},
        query_terms=["data", "structur"],
        total_docs=10,
    )
    assert score > 0.0


def test_query_parser():
    parsed = QueryParser.parse('"operating systems" memory -windows site:iitd.ac.in')
    assert parsed.site_filter == "iitd.ac.in"
    assert "window" in parsed.excluded_terms
    assert len(parsed.phrases) == 1
    assert "operat" in parsed.phrases[0] or "system" in parsed.phrases[0]


def test_snippet_generator():
    text = "The quick brown fox jumps over the lazy dog. Prof Naveen Garg teaches Data Structures and Algorithms at IIT Delhi."
    snippet = SnippetGenerator.generate_snippet(text, ["Data", "Structures"])
    assert "<mark>" in snippet
    assert "Data" in snippet or "Structures" in snippet


def test_pagerank_calculation():
    nodes = ["pageA", "pageB", "pageC"]
    # pageA -> pageB, pageB -> pageC, pageC -> pageA
    edges = [("pageA", "pageB"), ("pageB", "pageC"), ("pageC", "pageA")]
    ranks = PageRankCalculator.compute_pagerank(nodes, edges)
    assert len(ranks) == 3
    # In symmetric circle, all ranks should be identical
    assert abs(ranks["pageA"] - ranks["pageB"]) < 1e-4


def test_query_cache():
    cache = QueryCache(max_size=10, ttl_seconds=60)
    key = QueryCache.make_key("machine learning", 1, 10, "bm25")
    cache.set(key, {"sample": "results"})
    assert cache.get(key) == {"sample": "results"}
    stats = cache.get_stats()
    assert stats["hits"] == 1


@pytest.mark.asyncio
async def test_full_search_flow():
    # In-memory SQLite async test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Seed test data
        result = await seed_database(session, force=True)
        assert result["documents_added"] > 0
        assert result["indexed_entries"] > 0

        # Execute BM25 search
        ranker = Ranker(session=session)
        search_results = await ranker.search("Machine Learning IIT Madras")
        assert len(search_results) > 0
        # The top result should be the NPTEL Machine Learning course from IIT Madras
        assert "Machine Learning" in search_results[0].title
        assert search_results[0].score > 0

        # Execute TF-IDF search
        tfidf_results = await ranker.search("Operating Systems", ranking_method="tfidf")
        assert len(tfidf_results) > 0

    await engine.dispose()

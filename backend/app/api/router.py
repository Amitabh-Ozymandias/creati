"""
VidyaSearch — Central API Router

Defines all search, autocomplete, crawling, PageRank, and analytics endpoints.
"""

import time
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.document import Document
from app.models.inverted_index import InvertedIndex, CorpusStats
from app.models.link_graph import LinkGraph
from app.models.analytics import SearchQuery
from app.ranking.ranker import Ranker
from app.ranking.query_parser import QueryParser
from app.autocomplete.suggestion_engine import SuggestionEngine
from app.typo.spell_checker import SpellChecker
from app.pagerank.pagerank import PageRankCalculator
from app.crawler.crawl_manager import CrawlManager
from app.cache.query_cache import QueryCache
from app.analytics.tracker import AnalyticsTracker
from app.schemas.search import (
    SearchResponse,
    SearchResultItem,
    AutocompleteResponse,
)
from app.schemas.analytics import AnalyticsSummary, ClickEvent
from app.seed.seeder import seed_database

router = APIRouter(prefix="/api/v1")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "VidyaSearch",
        "version": "0.1.0",
    }


@router.get("/search", response_model=SearchResponse)
async def search_endpoint(
    q: str = Query(..., min_length=1, max_length=512, description="Search query string"),
    page: int = Query(1, ge=1, le=100, description="Page number"),
    per_page: int = Query(10, ge=1, le=50, description="Results per page"),
    ranking: str = Query("bm25", pattern="^(bm25|tfidf)$", description="Ranking algorithm (bm25 or tfidf)"),
    domain: Optional[str] = Query(None, description="Domain filter (e.g. nptel.ac.in)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Full-text search using BM25 or TF-IDF with PageRank score weighting.
    Includes typo correction ('Did you mean?'), query caching, and analytics logging.
    """
    start_time = time.perf_counter()
    cache = QueryCache.get_instance()
    cache_key = QueryCache.make_key(query=q, page=page, per_page=per_page, ranking=ranking, domain=domain)

    # 1. Check in-memory LRU cache
    cached_data = cache.get(cache_key)
    if cached_data:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        cached_data["response_time_ms"] = elapsed_ms
        cached_data["cache_hit"] = True

        # Log search query asynchronously
        await AnalyticsTracker.log_query(
            session=db,
            query=q,
            results_count=cached_data["total_results"],
            response_time_ms=elapsed_ms,
            page=page,
            cache_hit=True,
            ranking_method=ranking,
        )
        return SearchResponse(**cached_data)

    # 2. Execute retrieval & ranking
    ranker = Ranker(session=db)
    all_results = await ranker.search(
        query_str=q,
        ranking_method=ranking,
        domain_filter=domain,
        limit=100,
    )

    total_results = len(all_results)
    total_pages = max(1, (total_results + per_page - 1) // per_page)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_results = all_results[start_idx:end_idx]

    # 3. Check for typo correction / Did you mean
    spell_checker = SpellChecker.get_instance()
    did_you_mean = spell_checker.correct_query(q)
    # Don't suggest typo if it's the exact same query
    if did_you_mean and did_you_mean.strip().lower() == q.strip().lower():
        did_you_mean = None

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    response_dict = {
        "query": q,
        "total_results": total_results,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "response_time_ms": elapsed_ms,
        "ranking_method": ranking,
        "results": page_results,
        "did_you_mean": did_you_mean,
        "cache_hit": False,
    }

    # Cache successful result
    cache.set(cache_key, response_dict)

    # 4. Log search analytics & register in autocomplete trie
    await AnalyticsTracker.log_query(
        session=db,
        query=q,
        results_count=total_results,
        response_time_ms=elapsed_ms,
        page=page,
        cache_hit=False,
        ranking_method=ranking,
    )
    SuggestionEngine.get_instance().add_query(q)

    return SearchResponse(**response_dict)


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_endpoint(
    q: str = Query(..., min_length=1, max_length=128, description="Prefix to autocomplete"),
    limit: int = Query(8, ge=1, le=20, description="Max suggestions to return"),
):
    """Real-time autocomplete suggestions from prefix Trie."""
    suggestions = SuggestionEngine.get_instance().suggest(prefix=q, limit=limit)
    return AutocompleteResponse(prefix=q, suggestions=suggestions)


@router.get("/spellcheck")
async def spellcheck_endpoint(
    q: str = Query(..., min_length=1, max_length=256),
):
    """Typo correction suggestion."""
    correction = SpellChecker.get_instance().correct_query(q)
    return {"query": q, "correction": correction}


@router.post("/crawl")
async def trigger_crawl_endpoint(
    seed_urls: List[str] = Query(default=["https://nptel.ac.in/"]),
    max_pages: int = Query(5, ge=1, le=50),
    max_depth: int = Query(2, ge=0, le=5),
    db: AsyncSession = Depends(get_db),
):
    """Trigger web crawling on specified seed URLs."""
    manager = CrawlManager(session=db)
    result = await manager.crawl(seed_urls=seed_urls, max_pages=max_pages, max_depth=max_depth)
    
    # Recompute PageRank after new crawl
    await PageRankCalculator.recompute_and_update(db)
    # Refresh autocomplete & spellcheck
    await SuggestionEngine.build_from_db(db)
    await SpellChecker.build_vocabulary(db)
    # Invalidate cache
    QueryCache.get_instance().invalidate_all()

    return {"status": "success", "crawl_stats": result}


@router.post("/pagerank/recompute")
async def recompute_pagerank_endpoint(
    db: AsyncSession = Depends(get_db),
):
    """Recalculate PageRank scores across all documents."""
    scores = await PageRankCalculator.recompute_and_update(db)
    QueryCache.get_instance().invalidate_all()
    return {"status": "success", "scored_nodes": len(scores), "top_scores": sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]}


@router.get("/analytics", response_model=AnalyticsSummary)
async def analytics_summary_endpoint(
    db: AsyncSession = Depends(get_db),
):
    """Retrieve search performance, popular queries, and indexing metrics."""
    return await AnalyticsTracker.get_summary(db)


@router.post("/analytics/click")
async def record_click_endpoint(
    click: ClickEvent,
    db: AsyncSession = Depends(get_db),
):
    """Record a result click event."""
    await AnalyticsTracker.log_click(
        session=db,
        query_id=click.query_id,
        doc_id=click.doc_id,
        result_position=click.result_position,
        clicked_url=click.clicked_url,
    )
    return {"status": "recorded"}


@router.post("/seed")
async def seed_data_endpoint(
    force: bool = Query(False, description="Overwrite existing seed data"),
    db: AsyncSession = Depends(get_db),
):
    """Seed the database with sample Indian college resources."""
    result = await seed_database(db, force=force)
    return result


@router.get("/stats")
async def system_stats(
    db: AsyncSession = Depends(get_db),
):
    """Full system stats across all tables and caches."""
    doc_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    term_count = (await db.execute(select(func.count(func.distinct(InvertedIndex.term))))).scalar() or 0
    link_count = (await db.execute(select(func.count(LinkGraph.id)))).scalar() or 0
    query_count = (await db.execute(select(func.count(SearchQuery.id)))).scalar() or 0
    cache_stats = QueryCache.get_instance().get_stats()

    return {
        "total_documents": doc_count,
        "total_indexed_terms": term_count,
        "total_link_edges": link_count,
        "total_searches": query_count,
        "cache": cache_stats,
    }

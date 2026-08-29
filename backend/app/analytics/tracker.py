"""
VidyaSearch — Analytics Tracker and Metrics Aggregator
"""

from datetime import datetime
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import SearchClick, SearchQuery
from app.models.document import Document
from app.models.inverted_index import InvertedIndex
from app.schemas.analytics import AnalyticsSummary, QueryStats
from app.cache.query_cache import QueryCache


class AnalyticsTracker:
    """Tracks search queries and click events, and aggregates dashboard metrics."""

    @classmethod
    async def log_query(
        cls,
        session: AsyncSession,
        query: str,
        results_count: int,
        response_time_ms: float,
        page: int = 1,
        cache_hit: bool = False,
        ranking_method: str = "bm25",
    ) -> SearchQuery:
        """Record a search query execution."""
        entry = SearchQuery(
            query=query,
            query_normalized=query.strip().lower(),
            results_count=results_count,
            page=page,
            response_time_ms=response_time_ms,
            cache_hit=cache_hit,
            ranking_method=ranking_method,
        )
        session.add(entry)
        await session.commit()
        await session.refresh(entry)
        return entry

    @classmethod
    async def log_click(
        cls,
        session: AsyncSession,
        query_id: int,
        doc_id: int,
        result_position: int,
        clicked_url: str,
    ) -> SearchClick:
        """Record a result link click."""
        click = SearchClick(
            query_id=query_id,
            doc_id=doc_id,
            result_position=result_position,
            clicked_url=clicked_url,
        )
        session.add(click)
        await session.commit()
        await session.refresh(click)
        return click

    @classmethod
    async def get_summary(cls, session: AsyncSession) -> AnalyticsSummary:
        """Compute aggregate summary for analytics dashboard."""
        # Total searches
        total_q_res = await session.execute(select(func.count(SearchQuery.id)))
        total_searches = total_q_res.scalar() or 0

        # Unique queries
        unique_q_res = await session.execute(
            select(func.count(func.distinct(SearchQuery.query_normalized)))
        )
        unique_queries = unique_q_res.scalar() or 0

        # Average response time
        avg_time_res = await session.execute(select(func.avg(SearchQuery.response_time_ms)))
        avg_response_time = round(float(avg_time_res.scalar() or 0.0), 2)

        # Zero results count
        zero_res = await session.execute(
            select(func.count(SearchQuery.id)).where(SearchQuery.results_count == 0)
        )
        zero_count = zero_res.scalar() or 0
        zero_result_rate = round((zero_count / total_searches * 100), 2) if total_searches > 0 else 0.0

        # Cache hit rate from queries logged or query cache
        cache_hit_res = await session.execute(
            select(func.count(SearchQuery.id)).where(SearchQuery.cache_hit.is_(True))
        )
        cache_hits = cache_hit_res.scalar() or 0
        cache_hit_rate = round((cache_hits / total_searches * 100), 2) if total_searches > 0 else 0.0

        # Top queries
        top_stmt = (
            select(
                SearchQuery.query_normalized,
                func.count(SearchQuery.id).label("search_count"),
                func.avg(SearchQuery.results_count).label("avg_results"),
                func.avg(SearchQuery.response_time_ms).label("avg_time"),
                func.max(SearchQuery.searched_at).label("last_searched"),
            )
            .group_by(SearchQuery.query_normalized)
            .order_by(desc("search_count"))
            .limit(10)
        )
        top_res = await session.execute(top_stmt)
        top_queries = [
            QueryStats(
                query=row[0],
                search_count=row[1],
                avg_results=round(float(row[2] or 0), 1),
                avg_response_time_ms=round(float(row[3] or 0), 2),
                last_searched=row[4] or datetime.now(),
            )
            for row in top_res.all()
        ]

        # Total documents & terms
        total_docs_res = await session.execute(select(func.count(Document.id)))
        total_documents = total_docs_res.scalar() or 0

        total_terms_res = await session.execute(
            select(func.count(func.distinct(InvertedIndex.term)))
        )
        total_indexed_terms = total_terms_res.scalar() or 0

        return AnalyticsSummary(
            total_searches=total_searches,
            unique_queries=unique_queries,
            avg_response_time_ms=avg_response_time,
            cache_hit_rate=cache_hit_rate,
            zero_result_rate=zero_result_rate,
            top_queries=top_queries,
            total_documents=total_documents,
            total_indexed_terms=total_indexed_terms,
        )

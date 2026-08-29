"""
VidyaSearch — Analytics Schemas

Pydantic models for analytics events and dashboard data.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ClickEvent(BaseModel):
    """A click on a search result."""

    query_id: int
    doc_id: int
    result_position: int = Field(ge=1)
    clicked_url: str


class QueryStats(BaseModel):
    """Statistics for a single query term."""

    query: str
    search_count: int
    avg_results: float
    avg_response_time_ms: float
    last_searched: datetime


class AnalyticsSummary(BaseModel):
    """Overall analytics dashboard data."""

    total_searches: int
    unique_queries: int
    avg_response_time_ms: float
    cache_hit_rate: float
    zero_result_rate: float
    top_queries: list[QueryStats]
    total_documents: int
    total_indexed_terms: int


class CrawlStats(BaseModel):
    """Crawl status and statistics."""

    total_pages_crawled: int
    total_domains: int
    pages_per_domain: dict[str, int]
    last_crawl_time: datetime | None = None
    crawl_queue_size: int = 0
    error_count: int = 0

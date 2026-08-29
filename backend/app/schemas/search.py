"""
VidyaSearch — Search Schemas

Pydantic models for search request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Incoming search query."""

    query: str = Field(..., min_length=1, max_length=512, description="Search query string")
    page: int = Field(1, ge=1, le=100, description="Page number")
    per_page: int = Field(10, ge=1, le=50, description="Results per page")
    ranking: str = Field("bm25", pattern="^(bm25|tfidf)$", description="Ranking algorithm")
    domain: str | None = Field(None, description="Filter by domain")


class SearchResultItem(BaseModel):
    """A single search result."""

    doc_id: int
    url: str
    title: str
    snippet: str = Field(description="Highlighted text snippet")
    domain: str
    score: float
    pagerank_score: float = 0.0
    word_count: int = 0
    crawled_at: datetime | None = None


class SearchResponse(BaseModel):
    """Search results response."""

    query: str
    total_results: int
    page: int
    per_page: int
    total_pages: int
    response_time_ms: float
    ranking_method: str
    results: list[SearchResultItem]
    did_you_mean: str | None = None
    cache_hit: bool = False


class AutocompleteRequest(BaseModel):
    """Autocomplete/suggestion request."""

    prefix: str = Field(..., min_length=1, max_length=128)
    limit: int = Field(8, ge=1, le=20)


class AutocompleteResponse(BaseModel):
    """Autocomplete suggestions."""

    prefix: str
    suggestions: list[str]

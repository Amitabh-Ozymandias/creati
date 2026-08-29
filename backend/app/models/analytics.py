"""
VidyaSearch — Analytics Models

Track search queries, clicks, and user interaction for analytics.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SearchQuery(Base):
    """
    A logged search query with performance and result metrics.

    Used for analytics: popular queries, response times, zero-result tracking.
    """

    __tablename__ = "search_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # The raw query string entered by the user
    query: Mapped[str] = mapped_column(String(512), nullable=False, index=True)

    # Normalized query (lowered, trimmed) for aggregation
    query_normalized: Mapped[str] = mapped_column(String(512), nullable=False, index=True)

    # Results info
    results_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    page: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Performance
    response_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cache_hit: Mapped[bool] = mapped_column(nullable=False, default=False)

    # Ranking method used
    ranking_method: Mapped[str] = mapped_column(String(32), nullable=False, default="bm25")

    # Timestamps
    searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_search_queries_normalized_time", "query_normalized", "searched_at"),
    )

    def __repr__(self) -> str:
        return f"<SearchQuery(query='{self.query}', results={self.results_count})>"


class SearchClick(Base):
    """
    A click event on a search result.

    Tracks which results users click on, used for CTR analysis
    and potential click-based relevance feedback.
    """

    __tablename__ = "search_clicks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Which query this click is associated with
    query_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Which document was clicked
    doc_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Position of the clicked result (1-indexed)
    result_position: Mapped[int] = mapped_column(Integer, nullable=False)

    # URL that was clicked
    clicked_url: Mapped[str] = mapped_column(String(2048), nullable=False)

    # Timestamp
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_search_clicks_query_doc", "query_id", "doc_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<SearchClick(query_id={self.query_id}, doc_id={self.doc_id}, "
            f"pos={self.result_position})>"
        )

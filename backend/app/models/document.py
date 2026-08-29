"""
VidyaSearch — Document Model

Represents a crawled web page stored in the database.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Document(Base):
    """A crawled and stored web page."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Core content
    url: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    description: Mapped[str] = mapped_column(String(1024), nullable=False, default="")

    # Metadata
    domain: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(64), nullable=False, default="text/html")
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="en")
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Crawl info
    crawl_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    http_status: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    crawled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_modified: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Ranking
    pagerank_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    inlink_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    outlink_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_documents_domain_url", "domain", "url"),
        Index("ix_documents_pagerank", "pagerank_score"),
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, url='{self.url[:60]}...', title='{self.title[:40]}...')>"

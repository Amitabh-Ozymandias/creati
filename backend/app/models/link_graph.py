"""
VidyaSearch — Link Graph Model

Stores hyperlink relationships between pages for PageRank computation.
"""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LinkGraph(Base):
    """
    A directed edge in the web link graph.

    Represents a hyperlink from source_url to target_url,
    used to build the adjacency matrix for PageRank.
    """

    __tablename__ = "link_graph"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # The page containing the link
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)

    # The page being linked to
    target_url: Mapped[str] = mapped_column(String(2048), nullable=False)

    # Anchor text of the link (useful for contextual ranking)
    anchor_text: Mapped[str] = mapped_column(String(512), nullable=False, default="")

    # When this link was discovered
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_link_source", "source_url"),
        Index("ix_link_target", "target_url"),
        Index("ix_link_source_target", "source_url", "target_url", unique=True),
    )

    def __repr__(self) -> str:
        return (
            f"<LinkGraph(source='{self.source_url[:40]}...' → "
            f"target='{self.target_url[:40]}...')>"
        )

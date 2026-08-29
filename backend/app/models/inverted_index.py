"""
VidyaSearch — Inverted Index Model

Maps terms to documents with frequency and positional data for fast search lookups.
"""

from sqlalchemy import Index, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class InvertedIndex(Base):
    """
    Inverted index entry mapping a term to a document.

    Structure: term → (doc_id, term_frequency, positions[])
    This enables fast full-text search with positional information
    for phrase matching and proximity scoring.
    """

    __tablename__ = "inverted_index"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # The indexed term (lowercased, stemmed)
    term: Mapped[str] = mapped_column(String(256), nullable=False, index=True)

    # Reference to the document
    doc_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # How many times this term appears in the document
    term_frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Positions of the term in the document (for phrase/proximity queries)
    positions: Mapped[list[int]] = mapped_column(
        JSON, nullable=False, default=list
    )

    __table_args__ = (
        # Composite index for looking up a term across all documents
        Index("ix_inverted_term_doc", "term", "doc_id", unique=True),
        # Index for document lookups (e.g., "what terms are in doc X?")
        Index("ix_inverted_doc_term", "doc_id", "term"),
    )

    def __repr__(self) -> str:
        return (
            f"<InvertedIndex(term='{self.term}', doc_id={self.doc_id}, "
            f"tf={self.term_frequency})>"
        )


class CorpusStats(Base):
    """
    Corpus-level statistics for ranking calculations.

    Stores aggregate data needed by TF-IDF and BM25:
    - Total number of documents
    - Average document length
    - Document frequency for each term
    """

    __tablename__ = "corpus_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # The term (or "__CORPUS__" for aggregate stats)
    term: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)

    # Document frequency: how many documents contain this term
    # For "__CORPUS__" row: stores total document count
    doc_frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # For "__CORPUS__" row: stores total word count across all documents
    # For individual terms: not used (0)
    total_words: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<CorpusStats(term='{self.term}', df={self.doc_frequency})>"

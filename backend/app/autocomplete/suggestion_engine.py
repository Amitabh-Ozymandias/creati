"""
VidyaSearch — Autocomplete Suggestion Engine
"""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.autocomplete.trie import Trie
from app.models.document import Document
from app.models.analytics import SearchQuery


class SuggestionEngine:
    """Manages the global Trie and generates search suggestions."""

    _instance: "SuggestionEngine | None" = None
    _trie: Trie = Trie()

    @classmethod
    def get_instance(cls) -> "SuggestionEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    async def build_from_db(cls, session: AsyncSession):
        """Populate the autocomplete Trie from document titles and popular queries."""
        trie = Trie()

        # 1. Add terms from popular past search queries
        query_stmt = select(SearchQuery.query, SearchQuery.results_count)
        query_res = await session.execute(query_stmt)
        for row in query_res.all():
            q, results_count = row[0], row[1]
            if q and results_count > 0:
                trie.insert(q, frequency=5)

        # 2. Add phrases from document titles
        doc_stmt = select(Document.title)
        doc_res = await session.execute(doc_stmt)
        for row in doc_res.all():
            title = row[0]
            if title:
                trie.insert(title, frequency=2)
                # Also insert meaningful subphrases
                words = title.split()
                if len(words) > 2:
                    for i in range(len(words) - 1):
                        subphrase = " ".join(words[i:i+3])
                        trie.insert(subphrase, frequency=1)

        # 3. Add default Indian college keywords if empty
        common_seeds = [
            "nptel computer science courses",
            "nptel data structures and algorithms",
            "nptel machine learning iit madras",
            "nptel operating systems",
            "nptel deep learning iit kharagpur",
            "swayam cloud computing",
            "swayam python programming",
            "iit bombay lecture notes",
            "iit delhi academic calendar",
            "nit trichy syllabus",
            "gate computer science previous year questions",
            "artificial intelligence nptel",
            "database management systems nptel",
            "discrete mathematics iit",
            "compiler design lecture notes",
            "computer networks iit bombay",
            "linear algebra nptel iit kanpur"
        ]
        for phrase in common_seeds:
            trie.insert(phrase, frequency=3)

        cls._trie = trie

    def suggest(self, prefix: str, limit: int = 8) -> List[str]:
        """Get suggestions for the typed prefix."""
        return self._trie.search_prefix(prefix, limit=limit)

    def add_query(self, query: str):
        """Dynamically add a new search query to the autocomplete trie."""
        self._trie.insert(query, frequency=1)

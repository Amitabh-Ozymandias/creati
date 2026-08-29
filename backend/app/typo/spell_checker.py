"""
VidyaSearch — Typo Correction and Spell Checker

Uses Levenshtein edit distance and corpus term frequency
to generate "Did you mean?" corrections for misspelled queries.
"""

from typing import Dict, List, Optional, Set
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inverted_index import InvertedIndex, CorpusStats
from app.indexer.tokenizer import tokenize


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute the minimum edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class SpellChecker:
    """Generates 'Did you mean?' query corrections based on corpus vocabulary."""

    _instance: "SpellChecker | None" = None
    _vocab_freq: Dict[str, int] = {}

    @classmethod
    def get_instance(cls) -> "SpellChecker":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    async def build_vocabulary(cls, session: AsyncSession):
        """Build vocabulary from indexed corpus terms."""
        vocab: Dict[str, int] = {}
        stmt = select(CorpusStats.term, CorpusStats.doc_frequency).where(
            CorpusStats.term != "__CORPUS__"
        )
        res = await session.execute(stmt)
        for term, df in res.all():
            vocab[term] = df

        # Add common Indian academic keywords as guaranteed vocabulary
        common_words = [
            "computer", "science", "engineering", "algorithm", "algorithms", "structure", "structures",
            "learning", "machine", "intelligence", "artificial", "network", "networks",
            "database", "systems", "operating", "python", "programming", "mathematics",
            "discrete", "calculus", "linear", "algebra", "physics", "chemistry", "mechanical",
            "electrical", "electronics", "nptel", "swayam", "syllabus", "lecture", "notes",
            "iit", "nit", "gate", "assignment", "solution", "exam", "semester", "notice"
        ]
        for word in common_words:
            if word not in vocab:
                vocab[word] = 5

        cls._vocab_freq = vocab

    def correct_word(self, word: str, max_distance: int = 2) -> Optional[str]:
        """Find the best matching correction for a single word."""
        w = word.lower()
        if w in self._vocab_freq:
            return None  # Word is already correct

        if len(w) <= 2:
            return None

        candidates = []
        for vocab_word, freq in self._vocab_freq.items():
            # Quick length pruning
            if abs(len(vocab_word) - len(w)) > max_distance:
                continue
            dist = levenshtein_distance(w, vocab_word)
            if dist <= max_distance:
                candidates.append((dist, -freq, vocab_word))

        if candidates:
            candidates.sort()
            return candidates[0][2]
        return None

    def correct_query(self, query: str) -> Optional[str]:
        """
        Suggest a correction for the full search query if any typos exist.
        Returns corrected query string, or None if no correction needed.
        """
        tokens = tokenize(query)
        if not tokens:
            return None

        corrected_tokens = []
        any_corrected = False

        for token in tokens:
            correction = self.correct_word(token)
            if correction:
                corrected_tokens.append(correction)
                any_corrected = True
            else:
                corrected_tokens.append(token)

        if any_corrected:
            return " ".join(corrected_tokens)
        return None

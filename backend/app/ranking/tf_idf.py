"""
VidyaSearch — TF-IDF Ranking Algorithm
"""

import math
from typing import Dict, List, Tuple


class TFIDFScorer:
    """
    Term Frequency-Inverse Document Frequency (TF-IDF) relevance scoring.

    Formula:
        TF(t, d) = 1 + log10(tf(t, d))  if tf > 0 else 0 (Sublinear scaling)
        IDF(t) = log10(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
        Score(d, q) = Σ (TF(t, d) * IDF(t))
    """

    @staticmethod
    def compute_idf(df: int, total_docs: int) -> float:
        """Compute smooth IDF for a term given document frequency df and total docs N."""
        if total_docs <= 0:
            return 0.0
        # Smoothed inverse document frequency
        return math.log10(1.0 + (total_docs - df + 0.5) / (df + 0.5))

    @staticmethod
    def compute_tf(term_freq: int) -> float:
        """Compute sublinearly scaled Term Frequency."""
        if term_freq <= 0:
            return 0.0
        return 1.0 + math.log10(term_freq)

    @classmethod
    def score_document(
        cls,
        term_frequencies: Dict[str, int],
        doc_frequencies: Dict[str, int],
        query_terms: List[str],
        total_docs: int,
    ) -> float:
        """Calculate TF-IDF relevance score for a document."""
        score = 0.0
        for term in query_terms:
            tf = term_frequencies.get(term, 0)
            if tf > 0:
                df = doc_frequencies.get(term, 1)
                idf = cls.compute_idf(df, total_docs)
                score += cls.compute_tf(tf) * idf
        return score

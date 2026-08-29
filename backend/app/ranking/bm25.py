"""
VidyaSearch — BM25 (Okapi BM25) Ranking Algorithm
"""

import math
from typing import Dict, List


class BM25Scorer:
    """
    Okapi BM25 Ranking Function.

    Score(D, Q) = Σ IDF(qi) * [ tf(qi, D) * (k1 + 1) ] / [ tf(qi, D) + k1 * (1 - b + b * (|D| / avgdl)) ]

    Parameters:
        k1 (float): Term frequency saturation parameter (default: 1.5).
        b (float): Document length normalization parameter (default: 0.75).
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def compute_idf(self, df: int, total_docs: int) -> float:
        """
        Calculate BM25 Inverse Document Frequency (Probabilistic IDF).
        IDF(qi) = ln( (N - n(qi) + 0.5) / (n(qi) + 0.5) + 1.0 )
        """
        if total_docs <= 0:
            return 0.0
        val = (total_docs - df + 0.5) / (df + 0.5) + 1.0
        return math.log(max(val, 1e-6))

    def score_term(
        self,
        tf: int,
        df: int,
        doc_length: int,
        avg_doc_length: float,
        total_docs: int,
    ) -> float:
        """Compute BM25 contribution for a single query term."""
        if tf <= 0:
            return 0.0

        idf = self.compute_idf(df, total_docs)
        
        # Avoid division by zero
        avgdl = avg_doc_length if avg_doc_length > 0 else 1.0
        len_norm = 1.0 - self.b + self.b * (doc_length / avgdl)
        numerator = tf * (self.k1 + 1.0)
        denominator = tf + self.k1 * len_norm

        return idf * (numerator / denominator)

    def score_document(
        self,
        term_frequencies: Dict[str, int],
        doc_frequencies: Dict[str, int],
        query_terms: List[str],
        doc_length: int,
        avg_doc_length: float,
        total_docs: int,
    ) -> float:
        """Calculate total Okapi BM25 score for document across all query terms."""
        total_score = 0.0
        for term in query_terms:
            tf = term_frequencies.get(term, 0)
            if tf > 0:
                df = doc_frequencies.get(term, 1)
                term_score = self.score_term(
                    tf=tf,
                    df=df,
                    doc_length=doc_length,
                    avg_doc_length=avg_doc_length,
                    total_docs=total_docs,
                )
                total_score += term_score
        return total_score

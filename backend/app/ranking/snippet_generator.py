"""
VidyaSearch — Snippet Generator

Extracts contextual, highlighted text snippets from document content
matching user query terms.
"""

import re
from typing import List, Set
from app.indexer.normalizer import simple_stem, STOPWORDS


class SnippetGenerator:
    """Generates highlighted search result snippets centered around matched terms."""

    @classmethod
    def generate_snippet(
        cls,
        text: str,
        query_terms: List[str],
        snippet_length: int = 180,
    ) -> str:
        """
        Extract a relevant window of text containing query terms,
        wrapping matched keywords in <mark>...</mark> tags.
        """
        if not text:
            return ""

        # Clean excess whitespace
        clean_text = re.sub(r"\s+", " ", text).strip()
        if len(clean_text) <= snippet_length:
            return cls.highlight_terms(clean_text, query_terms)

        stemmed_query_set: Set[str] = {
            simple_stem(t.lower()) for t in query_terms if t.lower() not in STOPWORDS
        }
        
        words = clean_text.split(" ")
        best_window_start = 0
        max_term_matches = -1

        # Slide a window across words to find the section with most query term occurrences
        window_size = min(35, len(words))

        for i in range(0, max(1, len(words) - window_size + 1), 3):
            window_words = words[i : i + window_size]
            matches = sum(
                1 for w in window_words
                if simple_stem(re.sub(r"[^a-zA-Z0-9]", "", w.lower())) in stemmed_query_set
            )
            if matches > max_term_matches:
                max_term_matches = matches
                best_window_start = i

        snippet_words = words[best_window_start : best_window_start + window_size]
        raw_snippet = " ".join(snippet_words)

        prefix = "... " if best_window_start > 0 else ""
        suffix = " ..." if (best_window_start + window_size) < len(words) else ""

        highlighted = cls.highlight_terms(raw_snippet, query_terms)
        return f"{prefix}{highlighted}{suffix}"

    @classmethod
    def highlight_terms(cls, text: str, query_terms: List[str]) -> str:
        """Wrap matching terms in <mark> tags."""
        if not query_terms or not text:
            return text

        stemmed_map = {simple_stem(t.lower()): t for t in query_terms if len(t) > 1}
        
        def replace_fn(match):
            word = match.group(0)
            clean_word = simple_stem(re.sub(r"[^a-zA-Z0-9]", "", word.lower()))
            if clean_word in stemmed_map or word.lower() in [q.lower() for q in query_terms]:
                return f"<mark>{word}</mark>"
            return word

        return re.sub(r"\b[a-zA-Z0-9_-]+\b", replace_fn, text)

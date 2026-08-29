"""
VidyaSearch — Tokenizer and Text Processing
"""

import re
import unicodedata
from typing import List, Tuple

# Token regex: alphanumeric sequences, preserving hyphens within words (e.g. multi-threaded)
TOKEN_PATTERN = re.compile(r"\b[a-zA-Z0-9]+(?:[-_][a-zA-Z0-9]+)*\b")


def normalize_text(text: str) -> str:
    """Normalize unicode characters and strip excessive whitespace."""
    if not text:
        return ""
    # Normalize unicode (NFKD)
    normalized = unicodedata.normalize("NFKD", text)
    # Remove accents/diacritics
    ascii_text = normalized.encode("ascii", "ignore").decode("utf-8")
    return ascii_text.lower()


def tokenize(text: str) -> List[str]:
    """Tokenize input text into lowercased tokens."""
    if not text:
        return []
    cleaned = normalize_text(text)
    return TOKEN_PATTERN.findall(cleaned)


def tokenize_with_positions(text: str) -> List[Tuple[str, int]]:
    """
    Tokenize text and return list of (token, position) pairs.
    Position is 0-indexed token index in the document.
    """
    if not text:
        return []
    cleaned = normalize_text(text)
    tokens = TOKEN_PATTERN.findall(cleaned)
    return [(token, pos) for pos, token in enumerate(tokens)]

"""
VidyaSearch — Query Parser

Parses user search query syntax including:
- Exact phrases: "machine learning"
- Exclusion terms: -syllabus
- Site filters: site:nptel.ac.in
- Plain search terms: algorithms data structures
"""

import re
from dataclasses import dataclass, field
from typing import List, Set

from app.indexer.tokenizer import tokenize
from app.indexer.normalizer import simple_stem, STOPWORDS


@dataclass
class ParsedQuery:
    """Structured representation of a parsed search query."""
    raw_query: str
    terms: List[str] = field(default_factory=list)          # Stemmed search terms
    raw_terms: List[str] = field(default_factory=list)      # Unstemmed terms for exact match
    phrases: List[List[str]] = field(default_factory=list)  # Phrases as list of tokens
    excluded_terms: Set[str] = field(default_factory=set)   # Terms preceded by '-'
    site_filter: str | None = None                          # Filter by site:domain


class QueryParser:
    """Parses search query string into structured query tokens and filters."""

    PHRASE_PATTERN = re.compile(r'"([^"]+)"')
    SITE_PATTERN = re.compile(r'\bsite:([a-zA-Z0-9.-]+)\b', re.IGNORECASE)
    EXCLUDE_PATTERN = re.compile(r'-([a-zA-Z0-9]+)\b')

    @classmethod
    def parse(cls, query_str: str) -> ParsedQuery:
        if not query_str:
            return ParsedQuery(raw_query="")

        raw_query = query_str.strip()
        site_filter = None
        excluded_terms: Set[str] = set()
        phrases: List[List[str]] = []

        # 1. Extract site: filter
        site_match = cls.SITE_PATTERN.search(raw_query)
        if site_match:
            site_filter = site_match.group(1).lower()
            raw_query = cls.SITE_PATTERN.sub("", raw_query)

        # 2. Extract excluded terms (-term)
        for excl in cls.EXCLUDE_PATTERN.findall(raw_query):
            excluded_terms.add(simple_stem(excl.lower()))
        raw_query = cls.EXCLUDE_PATTERN.sub("", raw_query)

        # 3. Extract exact quoted phrases
        for phrase_str in cls.PHRASE_PATTERN.findall(raw_query):
            phrase_tokens = [simple_stem(t) for t in tokenize(phrase_str) if t not in STOPWORDS]
            if phrase_tokens:
                phrases.append(phrase_tokens)
        raw_query = cls.PHRASE_PATTERN.sub("", raw_query)

        # 4. Extract standard search terms
        raw_tokens = tokenize(raw_query)
        terms: List[str] = []
        raw_terms: List[str] = []

        for token in raw_tokens:
            if token in STOPWORDS or len(token) < 2:
                continue
            raw_terms.append(token)
            stemmed = simple_stem(token)
            if stemmed not in excluded_terms:
                terms.append(stemmed)

        # If all terms were filtered as stopwords, preserve raw tokens
        if not terms and raw_tokens:
            terms = [simple_stem(t) for t in raw_tokens]
            raw_terms = raw_tokens

        return ParsedQuery(
            raw_query=query_str,
            terms=terms,
            raw_terms=raw_terms,
            phrases=phrases,
            excluded_terms=excluded_terms,
            site_filter=site_filter
        )

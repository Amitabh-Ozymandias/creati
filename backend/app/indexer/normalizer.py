"""
VidyaSearch — Normalizer, Stopwords and Stemmer
"""

import re
from typing import List, Set

# Standard English stopwords + common academic web boilerplate
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd",
    "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    # Web noise
    "http", "https", "www", "com", "edu", "org", "ac", "in", "html", "php"
}


def simple_stem(word: str) -> str:
    """
    Lightweight Porter-like morphological suffix stemmer
    for English words (handles common plurals, -ing, -ed, -tion, -ly, -ment).
    """
    if len(word) <= 3:
        return word
        
    w = word.lower()
    
    # Step 1: Plurals and basic inflections
    if w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    elif w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        w = w[:-1]
        
    # Step 2: Verb endings (-ed, -ing)
    if w.endswith("ingly") and len(w) > 6:
        w = w[:-5]
    elif w.endswith("edly") and len(w) > 5:
        w = w[:-4]
    elif w.endswith("ing") and len(w) > 5:
        w = w[:-3]
        if w.endswith(("bb", "dd", "gg", "mm", "nn", "pp", "rr", "tt")):
            w = w[:-1]
    elif w.endswith("ed") and len(w) > 4:
        w = w[:-2]
        if w.endswith(("bb", "dd", "gg", "mm", "nn", "pp", "rr", "tt")):
            w = w[:-1]
            
    # Step 3: Derivational suffixes (-ization, -ation, -ment, -ness, -able, -ible, -al)
    if w.endswith("ization") and len(w) > 8:
        w = w[:-7] + "ize"
    elif w.endswith("ational") and len(w) > 8:
        w = w[:-5] + "e"
    elif w.endswith("tional") and len(w) > 7:
        w = w[:-4]
    elif w.endswith("ation") and len(w) > 6:
        w = w[:-5] + "e"
    elif w.endswith("tion") and len(w) > 5:
        w = w[:-3]
    elif w.endswith("ment") and len(w) > 6:
        w = w[:-4]
    elif w.endswith("ness") and len(w) > 6:
        w = w[:-4]
    elif w.endswith("able") and len(w) > 6:
        w = w[:-4]
    elif w.endswith("ible") and len(w) > 6:
        w = w[:-4]
    elif w.endswith("ly") and len(w) > 4:
        w = w[:-2]
        
    return w


def filter_stopwords(tokens: List[str]) -> List[str]:
    """Filter out common stopwords from token list."""
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def normalize_tokens(tokens: List[str], use_stemming: bool = True) -> List[str]:
    """Filter stopwords and optionally apply stemming."""
    filtered = filter_stopwords(tokens)
    if use_stemming:
        return [simple_stem(t) for t in filtered]
    return filtered

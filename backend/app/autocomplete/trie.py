"""
VidyaSearch — Autocomplete Trie Data Structure
"""

from typing import Dict, List, Tuple


class TrieNode:
    """A single node in the prefix Trie."""

    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end_of_word: bool = False
        self.frequency: int = 0
        self.original_phrase: str = ""


class Trie:
    """
    Prefix Trie for real-time autocomplete suggestions.
    Fast O(prefix_len + k) lookup for query suggestions.
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, phrase: str, frequency: int = 1):
        """Insert a phrase with a given frequency weight."""
        if not phrase:
            return

        node = self.root
        phrase_clean = phrase.strip().lower()

        for char in phrase_clean:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.is_end_of_word = True
        node.frequency += frequency
        node.original_phrase = phrase.strip()

    def _collect_completions(self, node: TrieNode, results: List[Tuple[str, int]]):
        """Recursively collect all phrases with their frequencies below this node."""
        if node.is_end_of_word:
            results.append((node.original_phrase, node.frequency))

        for char, child_node in node.children.items():
            self._collect_completions(child_node, results)

    def search_prefix(self, prefix: str, limit: int = 8) -> List[str]:
        """Return top N completions matching the given prefix, ranked by frequency."""
        if not prefix:
            return []

        node = self.root
        prefix_clean = prefix.strip().lower()

        for char in prefix_clean:
            if char not in node.children:
                return []
            node = node.children[char]

        completions: List[Tuple[str, int]] = []
        self._collect_completions(node, completions)

        # Sort by frequency descending, then length ascending
        completions.sort(key=lambda x: (-x[1], len(x[0])))
        return [phrase for phrase, _ in completions[:limit]]

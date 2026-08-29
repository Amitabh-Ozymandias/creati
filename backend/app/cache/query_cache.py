"""
VidyaSearch — LRU Query Cache with TTL
"""

import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional, Tuple
from app.config import settings


@dataclass
class CacheEntry:
    value: Any
    expiry_time: float


class QueryCache:
    """
    Least Recently Used (LRU) In-Memory Cache with Time-To-Live (TTL).
    """

    _instance: "QueryCache | None" = None

    def __init__(self, max_size: int = settings.cache_max_size, ttl_seconds: int = settings.cache_ttl_seconds):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits: int = 0
        self.misses: int = 0

    @classmethod
    def get_instance(cls) -> "QueryCache":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def make_key(query: str, page: int = 1, per_page: int = 10, ranking: str = "bm25", domain: str | None = None) -> str:
        """Create normalized cache key from query parameters."""
        q_norm = query.strip().lower()
        domain_str = domain.lower() if domain else ""
        return f"{q_norm}|p={page}|n={per_page}|r={ranking}|d={domain_str}"

    def get(self, key: str) -> Optional[Any]:
        """Fetch item from cache if present and not expired."""
        if key not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[key]
        now = time.time()

        if now > entry.expiry_time:
            # Expired
            del self.cache[key]
            self.misses += 1
            return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.hits += 1
        return entry.value

    def set(self, key: str, value: Any, custom_ttl: Optional[int] = None):
        """Insert or update item in cache with TTL."""
        ttl = custom_ttl if custom_ttl is not None else self.ttl_seconds
        expiry = time.time() + ttl

        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            # Evict oldest
            self.cache.popitem(last=False)

        self.cache[key] = CacheEntry(value=value, expiry_time=expiry)

    def invalidate_all(self):
        """Clear the entire cache."""
        self.cache.clear()

    def get_stats(self) -> dict:
        """Return cache hit/miss statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate, 2),
        }

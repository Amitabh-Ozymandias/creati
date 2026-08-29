"""
VidyaSearch — URL Frontier and Rate Limiter
"""

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Optional, Set
from urllib.parse import urlparse


@dataclass
class FrontierItem:
    url: str
    depth: int


class URLFrontier:
    """
    Manages the crawling queue with domain-based rate limiting and deduplication.
    """

    def __init__(self, rate_limit_seconds: float = 1.0):
        self.rate_limit_seconds = rate_limit_seconds
        self.queue: Deque[FrontierItem] = deque()
        self.visited: Set[str] = set()
        self.queued: Set[str] = set()
        self.last_domain_request: Dict[str, float] = {}

    def add_url(self, url: str, depth: int = 0) -> bool:
        """Add a URL to the crawl queue if not previously seen."""
        clean_url = url.strip()
        if clean_url in self.visited or clean_url in self.queued:
            return False

        self.queued.add(clean_url)
        self.queue.append(FrontierItem(url=clean_url, depth=depth))
        return True

    def get_next_url(self, max_depth: int = 3) -> Optional[FrontierItem]:
        """Fetch next eligible URL respecting maximum depth."""
        while self.queue:
            item = self.queue.popleft()
            self.queued.discard(item.url)

            if item.url in self.visited:
                continue

            if item.depth > max_depth:
                continue

            self.visited.add(item.url)
            return item

        return None

    async def wait_for_domain_politeness(self, url: str):
        """Ensure polite delay between consecutive requests to the same domain."""
        domain = urlparse(url).netloc
        now = time.time()
        last_req = self.last_domain_request.get(domain, 0.0)
        elapsed = now - last_req

        if elapsed < self.rate_limit_seconds:
            sleep_duration = self.rate_limit_seconds - elapsed
            await asyncio.sleep(sleep_duration)

        self.last_domain_request[domain] = time.time()

    def size(self) -> int:
        return len(self.queue)

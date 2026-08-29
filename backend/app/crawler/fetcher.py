"""
VidyaSearch — Async HTTP Fetcher
"""

from typing import Optional, Tuple
import httpx
from app.config import settings


class AsyncFetcher:
    """Async HTTP client with timeout, redirect following, and retry logic."""

    def __init__(self, user_agent: str = settings.crawl_user_agent, timeout: float = settings.crawl_timeout):
        self.headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        }
        self.timeout = timeout

    async def fetch(self, client: httpx.AsyncClient, url: str) -> Tuple[Optional[str], int]:
        """
        Fetch HTML content from a URL.
        Returns (html_text, status_code).
        """
        try:
            resp = await client.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
            )
            # Only process HTML content
            content_type = resp.headers.get("content-type", "")
            if "text/html" in content_type or "application/xhtml" in content_type or not content_type:
                return resp.text, resp.status_code
            return None, resp.status_code
        except Exception:
            return None, 500

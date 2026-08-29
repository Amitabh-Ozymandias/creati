"""
VidyaSearch — Robots.txt Compliance Checker
"""

import urllib.robotparser
from urllib.parse import urlparse
from typing import Dict
import httpx


class RobotsChecker:
    """Fetches and caches robots.txt rules for polite crawling."""

    def __init__(self, user_agent: str = "VidyaSearchBot"):
        self.user_agent = user_agent
        self.parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}

    async def can_fetch(self, url: str, client: httpx.AsyncClient) -> bool:
        """Check if our crawler is allowed to fetch the given URL."""
        parsed = urlparse(url)
        domain_key = f"{parsed.scheme}://{parsed.netloc}"

        if domain_key not in self.parsers:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"{domain_key}/robots.txt"
            try:
                resp = await client.get(robots_url, timeout=5.0)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    # If 404 or not found, generally allowed
                    rp.allow_all = True
            except Exception:
                # If robots.txt cannot be reached, be permissive
                rp.allow_all = True

            self.parsers[domain_key] = rp

        return self.parsers[domain_key].can_fetch(self.user_agent, url)

"""
VidyaSearch — Web Crawl Manager

Coordinates crawling, extracts documents & link edges, stores them in database,
and triggers inverted indexing and PageRank recalculation.
"""

from datetime import datetime
from typing import List
from urllib.parse import urlparse
import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.crawler.fetcher import AsyncFetcher
from app.crawler.html_parser import HTMLParser
from app.crawler.robots_parser import RobotsChecker
from app.crawler.url_frontier import URLFrontier
from app.models.document import Document
from app.models.link_graph import LinkGraph
from app.indexer.inverted_index_builder import Indexer
from app.config import settings


class CrawlManager:
    """Manages the full crawl lifecycle."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.fetcher = AsyncFetcher()
        self.robots = RobotsChecker()
        self.frontier = URLFrontier(rate_limit_seconds=settings.crawl_rate_limit)

    async def crawl(
        self,
        seed_urls: List[str],
        max_pages: int = 10,
        max_depth: int = 2,
    ) -> dict:
        """
        Crawl starting from seed URLs, up to max_pages and max_depth.
        """
        for url in seed_urls:
            self.frontier.add_url(url, depth=0)

        crawled_count = 0
        failed_count = 0
        crawled_docs = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            while crawled_count < max_pages:
                item = self.frontier.get_next_url(max_depth=max_depth)
                if not item:
                    break

                # 1. Robots.txt check
                allowed = await self.robots.can_fetch(item.url, client)
                if not allowed:
                    continue

                # 2. Politeness rate limiting
                await self.frontier.wait_for_domain_politeness(item.url)

                # 3. Fetch content
                html, status = await self.fetcher.fetch(client, item.url)
                if not html or status >= 400:
                    failed_count += 1
                    continue

                # 4. Parse content & links
                parsed = HTMLParser.parse(item.url, html)
                if not parsed.body_text and not parsed.title:
                    continue

                domain = urlparse(item.url).netloc

                # 5. Store / Update Document in DB
                existing_stmt = select(Document).where(Document.url == item.url)
                existing_res = await self.session.execute(existing_stmt)
                doc = existing_res.scalar_one_or_none()

                if doc:
                    doc.title = parsed.title or doc.title
                    doc.body = parsed.body_text
                    doc.description = parsed.description
                    doc.word_count = parsed.word_count
                    doc.crawled_at = datetime.now()
                    doc.http_status = status
                else:
                    doc = Document(
                        url=item.url,
                        title=parsed.title or item.url,
                        body=parsed.body_text,
                        description=parsed.description,
                        domain=domain,
                        word_count=parsed.word_count,
                        crawl_depth=item.depth,
                        http_status=status,
                    )
                    self.session.add(doc)

                await self.session.flush()

                # 6. Index document into inverted index
                await Indexer.index_document(self.session, doc)
                crawled_docs.append(doc)
                crawled_count += 1

                # 7. Add discovered links to link graph and frontier (same domain preferred)
                seed_domain = urlparse(seed_urls[0]).netloc if seed_urls else ""
                for target_url, anchor_text in parsed.links:
                    target_domain = urlparse(target_url).netloc

                    # Store link edge for PageRank
                    link_stmt = select(LinkGraph).where(
                        LinkGraph.source_url == item.url,
                        LinkGraph.target_url == target_url
                    )
                    link_res = await self.session.execute(link_stmt)
                    if not link_res.scalar_one_or_none():
                        self.session.add(
                            LinkGraph(
                                source_url=item.url,
                                target_url=target_url,
                                anchor_text=anchor_text,
                            )
                        )

                    # Add to frontier if within allowed depth and relevant domain
                    if item.depth < max_depth and (not seed_domain or target_domain == seed_domain or "nptel" in target_domain or "ac.in" in target_domain):
                        self.frontier.add_url(target_url, depth=item.depth + 1)

                await self.session.commit()

        # Update overall corpus statistics after crawl
        await Indexer.update_corpus_stats(self.session)

        return {
            "crawled_pages": crawled_count,
            "failed_pages": failed_count,
            "queue_remaining": self.frontier.size(),
        }

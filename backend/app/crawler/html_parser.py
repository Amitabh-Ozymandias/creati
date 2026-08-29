"""
VidyaSearch — HTML Parser and Content Extractor
"""

import re
from dataclasses import dataclass, field
from typing import List, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


@dataclass
class ParsedHTML:
    url: str
    title: str
    body_text: str
    description: str
    links: List[Tuple[str, str]] = field(default_factory=list)  # (target_url, anchor_text)
    word_count: int = 0


class HTMLParser:
    """Extracts clean readable content and outbound links from raw HTML."""

    # Tags to strip completely before extracting content
    STRIP_TAGS = {"script", "style", "noscript", "svg", "header", "footer", "nav", "aside", "form"}

    @classmethod
    def parse(cls, base_url: str, html_content: str) -> ParsedHTML:
        if not html_content:
            return ParsedHTML(url=base_url, title="", body_text="", description="")

        soup = BeautifulSoup(html_content, "lxml" if "lxml" in BeautifulSoup.builder_registry.builders else "html.parser")

        # 1. Extract Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text().strip()

        # 2. Extract Meta Description
        description = ""
        meta_desc = soup.find("meta", attrs={"name": re.compile(r"description", re.I)}) or \
                    soup.find("meta", attrs={"property": re.compile(r"og:description", re.I)})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc.get("content").strip()

        # 3. Extract Links with Anchor text
        links: List[Tuple[str, str]] = []
        parsed_base = urlparse(base_url)

        for a_tag in soup.find_all("a", href=True):
            raw_href = a_tag["href"].strip()
            if raw_href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            full_url = urljoin(base_url, raw_href)
            # Remove fragment/hash from target URL
            target_parsed = urlparse(full_url)
            clean_target = f"{target_parsed.scheme}://{target_parsed.netloc}{target_parsed.path}"
            if target_parsed.query:
                clean_target += f"?{target_parsed.query}"

            # Validate http/https scheme
            if target_parsed.scheme in ("http", "https"):
                anchor = a_tag.get_text().strip()[:200]
                links.append((clean_target, anchor))

        # 4. Remove clutter tags
        for tag in soup.find_all(cls.STRIP_TAGS):
            tag.decompose()

        # 5. Extract text
        body_text = soup.get_text(separator=" ", strip=True)
        # Collapse multiple whitespaces
        body_text = re.sub(r"\s+", " ", body_text)
        word_count = len(body_text.split())

        return ParsedHTML(
            url=base_url,
            title=title,
            body_text=body_text,
            description=description,
            links=links,
            word_count=word_count,
        )

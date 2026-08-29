"""
VidyaSearch Backend — Configuration Management

Loads settings from environment variables / .env file.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database (supports sqlite+aiosqlite or postgresql+asyncpg)
    database_url: str = "sqlite+aiosqlite:///./vidyasearch.db"

    # Crawler
    crawl_rate_limit: float = 1.0  # seconds between requests per domain
    crawl_max_depth: int = 3
    crawl_max_pages: int = 10000
    crawl_user_agent: str = "VidyaSearchBot/1.0 (+https://github.com/vidyasearch)"
    crawl_timeout: float = 30.0  # seconds
    crawl_concurrency: int = 5  # concurrent fetches

    # Search
    search_results_per_page: int = 10
    search_max_results: int = 100
    search_snippet_length: int = 150

    # BM25 parameters
    bm25_k1: float = 1.5
    bm25_b: float = 0.75

    # PageRank
    pagerank_damping: float = 0.85
    pagerank_max_iterations: int = 100
    pagerank_convergence: float = 1e-6
    pagerank_weight: float = 0.3  # weight of PageRank in final score

    # Cache
    cache_max_size: int = 1000
    cache_ttl_seconds: int = 3600  # 1 hour

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton settings instance
settings = Settings()

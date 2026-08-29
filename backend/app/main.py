"""
VidyaSearch — FastAPI Application Entry Point

The main application factory with middleware, CORS, and lifecycle management.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.config import settings
from app.database import async_session, close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: initialize and clean up resources."""
    # Startup
    print("[VidyaSearch] Starting up...")
    await init_db()
    print("[VidyaSearch] Database initialized")

    # Auto-seed database with Indian College resources if empty
    async with async_session() as session:
        from app.seed.seeder import seed_database
        await seed_database(session)
        print("[VidyaSearch] Sample resources verified / seeded")

    yield
    # Shutdown
    print("[VidyaSearch] Shutting down...")
    await close_db()
    print("[VidyaSearch] Database connections closed")


app = FastAPI(
    title="VidyaSearch API",
    description=(
        "A search engine for Indian college resources. "
        "Crawl, index, and search through NPTEL, SWAYAM, "
        "and college websites."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "VidyaSearch API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }

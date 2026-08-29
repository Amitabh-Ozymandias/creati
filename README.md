# 🔍 VidyaSearch

**A search engine for Indian college resources** — crawl, index, and search through NPTEL, SWAYAM, and college websites for courses, lectures, notices, and study material.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-14+-black?logo=next.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue?logo=postgresql)

---

## ✨ Features

- **Web Crawler** — Polite, async crawler with `robots.txt` compliance and rate limiting
- **HTML Parser** — Extracts structured content from web pages
- **Inverted Index** — Fast term-to-document lookup with positional data
- **TF-IDF & BM25 Ranking** — Industry-standard relevance scoring
- **PageRank** — Link-based authority scoring
- **Autocomplete** — Real-time search suggestions via trie
- **Typo Correction** — "Did you mean?" using edit distance
- **Caching** — LRU + TTL-based query cache
- **Distributed Crawling** — Worker-based crawl scaling
- **Search Analytics** — Query trends, CTR, and performance metrics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Next.js Frontend                   │
│          Search UI  │  Analytics Dashboard           │
└────────────────────┬────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────┐
│                  FastAPI Backend                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ Crawler  │ │ Indexer  │ │ Ranker   │            │
│  │ Engine   │ │ Pipeline │ │ (BM25)   │            │
│  └──────────┘ └──────────┘ └──────────┘            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │ PageRank │ │ Auto-    │ │ Cache    │            │
│  │          │ │ complete │ │ Layer    │            │
│  └──────────┘ └──────────┘ └──────────┘            │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│               PostgreSQL Database                    │
│   Documents │ Inverted Index │ Link Graph │ Analytics│
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 16+

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Create `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/vidyasearch
CRAWL_RATE_LIMIT=1.0
CRAWL_MAX_DEPTH=3
CRAWL_USER_AGENT=VidyaSearchBot/1.0
```

## 📁 Project Structure

```
vidyasearch/
├── backend/
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── crawler/        # Web crawling engine
│   │   ├── indexer/        # Text processing & indexing
│   │   ├── ranking/        # TF-IDF, BM25 scoring
│   │   ├── autocomplete/   # Trie-based suggestions
│   │   ├── pagerank/       # Link analysis
│   │   ├── cache/          # Query result caching
│   │   ├── distributed/    # Worker-based crawling
│   │   ├── analytics/      # Search analytics
│   │   └── models/         # SQLAlchemy models
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/            # Next.js pages
│       ├── components/     # React components
│       └── hooks/          # Custom hooks
└── scripts/                # CLI utilities
```

## 🎯 Target Resources

| Source | Type | Status |
|--------|------|--------|
| NPTEL | Courses, Lectures | 🟡 In Progress |
| SWAYAM | MOOCs, Certifications | 🔴 Planned |
| IIT Websites | Notices, Departments | 🔴 Planned |
| NIT Websites | Course Material | 🔴 Planned |

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines before submitting a PR.

# 🔍 VidyaSearch (विद्याSearch)

<div align="center">

**A High-Performance Information Retrieval & Search Engine for Indian Higher Education Resources**

*Crawl, index, rank, and discover courses, lecture notes, syllabus materials, and exam resources across NPTEL, SWAYAM, IITs, NITs, and central universities.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

[Features](#-key-features) • [Architecture](#-system-architecture) • [IR Deep Dive](#-information-retrieval-algorithms--math) • [Quick Start](#-quick-start-guide) • [API Reference](#-api-reference) • [Project Structure](#-project-structure)

</div>

---

## 📖 Overview

**VidyaSearch** is a full-stack, production-ready search engine built from the ground up to tackle the fragmented landscape of Indian academic and college resources. Engineering and science students across India frequently navigate disconnected portals—NPTEL video repositories, SWAYAM MOOCs, individual IIT/NIT department pages, and GATE preparation archives—to find syllabus-relevant study materials.

VidyaSearch unifies these disparate sources using classical Information Retrieval (IR) algorithms combined with modern web technologies:
- **Polite Async Web Crawler** with rate limiting and `robots.txt` compliance.
- **Positional Inverted Index** for rapid keyword lookup, term frequencies, and positional proximity.
- **Okapi BM25 & TF-IDF Ranking** blended with **PageRank Authority Scoring**.
- **Trie-based Real-time Autocomplete** and **Levenshtein Spell Checking** ("Did you mean?").
- **High-throughput In-memory Query Cache** with sub-millisecond cache hits.
- **Full Telemetry & Analytics Dashboard** tracking CTR, query frequencies, and zero-hit searches.
- **Glassmorphic Dark-mode Next.js UI** for instant search and crawler orchestration.

---

## ✨ Key Features

| Component | Capabilities |
| :--- | :--- |
| **🕷️ Async Web Crawler** | Async HTTP (`httpx`), domain-level rate limiting, BFS URL frontier, concurrency limits, `robots.txt` adherence, and link extraction. |
| **📑 Inverted Indexer** | Tokenization, lowercasing, punctuation stripping, English stopword elimination, stemming, and positional indexing stored in relational database. |
| **⚖️ Dual Ranking Engine** | Configurable **Okapi BM25** ($k_1=1.5, b=0.75$) and **TF-IDF** scoring with **PageRank link authority** score blending ($PR_{weight} = 0.3$). |
| **🕸️ PageRank Algorithm** | Power iteration link graph analysis ($\alpha = 0.85$, max iterations $= 100$, convergence $= 10^{-6}$) over extracted web page graph. |
| **⚡ Prefix Autocomplete** | In-memory **Trie** data structure providing instant suggestions weighted by historical query popularity. |
| **💡 Spell Checking & Typo Fixes** | **Levenshtein Distance** dynamic programming algorithm with corpus vocabulary frequency scoring for *"Did you mean?"* suggestions. |
| **✂️ Snippet Generator** | Dynamic context-window snippet extraction with query keyword highlighting using HTML `<mark>` tags. |
| **🚀 Multi-Level Caching** | In-memory **LRU + TTL** query cache with hit/miss metrics and instant invalidation upon crawl updates. |
| **📊 Search Analytics** | Real-time query telemetry logging latency, result counts, click events, top queries, and zero-result rates. |
| **🎨 Modern Web UI** | Responsive Next.js 14 interface with dark mode, algorithm switcher (BM25 vs TF-IDF), source filter pills (NPTEL, SWAYAM, IITs, GATE), interactive crawler panel, and analytics graphs. |

---

## 🏗️ System Architecture

VidyaSearch is designed around a decoupled, modular architecture with clear separation between ingestion (crawling/indexing), retrieval (scoring/ranking), caching, and presentation.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Next.js 14 Web Frontend                           │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────────────┐  │
│  │   Search View    │ │  Crawler Console │ │  Analytics Dashboard    │  │
│  │ (BM25/TF-IDF UI) │ │  (Trigger & Log) │ │  (CTR, Latency, Trends) │  │
│  └─────────┬────────┘ └─────────┬────────┘ └────────────┬────────────┘  │
└────────────┼────────────────────┼───────────────────────┼───────────────┘
             │                    │ REST API              │
┌────────────▼────────────────────▼───────────────────────▼───────────────┐
│                         FastAPI Backend Engine                          │
│                                                                         │
│  ┌───────────────────────┐  ┌────────────────────────────────────────┐  │
│  │     API Routing       │  │             Query Cache Layer          │  │
│  │  (/search, /crawl,    │◄─┼─►   LRU + TTL Cache (Sub-ms Latency)   │  │
│  │   /autocomplete, etc) │  └────────────────────────────────────────┘  │
│  └───────────┬───────────┘                                              │
│              │                                                          │
│  ┌───────────▼───────────┐  ┌────────────────────┐  ┌────────────────┐  │
│  │      Ranker Core      │  │    Autocomplete    │  │ Spell Checker  │  │
│  │  • Okapi BM25 Scorer  │  │ • In-Memory Trie   │  │ • Levenshtein  │  │
│  │  • TF-IDF Scorer      │  │ • Query Frequencies│  │ • Vocab Dict   │  │
│  │  • Snippet Generator  │  └────────────────────┘  └────────────────┘  │
│  └───────────┬───────────┘                                              │
│              │                                                          │
│  ┌───────────▼───────────┐  ┌────────────────────┐  ┌────────────────┐  │
│  │   Crawler Engine      │  │  Indexer Pipeline  │  │    PageRank    │  │
│  │ • URL Frontier (BFS)  │─►│ • Tokenizer/Stemmer│─►│ • Power Iter.  │  │
│  │ • Robots Parser       │  │ • Inverted Index   │  │ • Link Graph   │  │
│  └───────────────────────┘  └────────────────────┘  └────────────────┘  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ Async SQLAlchemy / asyncpg
┌────────────────────────────────────▼────────────────────────────────────┐
│                       PostgreSQL / SQLite Database                      │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────────┐  │
│  │    documents    │  │  inverted_index  │  │       link_graph       │  │
│  │ (URLs, Content, │  │ (Term, DocID, TF,│  │ (Source, Target URL,   │  │
│  │  PageRank Score)│  │  Positions)      │  │  Anchor Text)          │  │
│  └─────────────────┘  └──────────────────┘  └────────────────────────┘  │
│  ┌─────────────────┐  ┌──────────────────┐                              │
│  │  search_queries │  │   click_events   │                              │
│  │ (Query telemetry│  │ (CTR, Result Pos,│                              │
│  │  & Latencies)   │  │  User Actions)   │                              │
│  └─────────────────┘  └──────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧮 Information Retrieval Algorithms & Math

### 1. Okapi BM25 Ranking Score
The BM25 score for a document $D$ given a query $Q = \{q_1, q_2, \dots, q_n\}$ is calculated as:

$$\text{Score}_{\text{BM25}}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$

Where:
- $\text{IDF}(q_i) = \ln\left(\frac{N - n(q_i) + 0.5}{n(q_i) + 0.5} + 1\right)$
- $f(q_i, D)$ is the term frequency of $q_i$ in document $D$.
- $|D|$ is the document length in words, and $\text{avgdl}$ is the average document length across the entire corpus.
- $k_1 = 1.5$ regulates term frequency saturation limit.
- $b = 0.75$ controls document length normalization penalty.

### 2. PageRank Authority Computation
PageRank iteratively distributes authority across the web graph using power iteration:

$$\text{PR}(u) = \frac{1 - d}{N} + d \sum_{v \in B_u} \frac{\text{PR}(v)}{L(v)}$$

Where:
- $B_u$ is the set of all pages pointing to page $u$.
- $L(v)$ is the number of outbound links on page $v$.
- $d = 0.85$ is the damping factor (probability of continuing to click links vs teleporting).
- Final ranking score combines BM25 relevance and PageRank authority:

$$\text{Final Score}(D) = (1 - w_{\text{PR}}) \cdot \text{NormalizedBM25}(D) + w_{\text{PR}} \cdot \text{PageRank}(D)$$

### 3. Levenshtein Edit Distance for Spell Checking
The minimum edit distance between strings $s_1$ and $s_2$ is computed via dynamic programming:

$$\text{lev}(i, j) = \begin{cases} \max(i, j) & \text{if } \min(i, j) = 0, \\ \min \begin{cases} \text{lev}(i-1, j) + 1 \\ \text{lev}(i, j-1) + 1 \\ \text{lev}(i-1, j-1) + [s_1[i] \neq s_2[j]] \end{cases} & \text{otherwise.} \end{cases}$$

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: `3.11` or higher
- **Node.js**: `18.0.0` or higher
- **PostgreSQL**: `16+` *(optional — defaults out-of-the-box to zero-config async SQLite)*

---

### 1. Backend Setup

```bash
# Clone repository
git clone https://github.com/Amitabh-Ozymandias/creati.git vidyasearch
cd vidyasearch/backend

# Create and activate virtual environment
python -m venv venv

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
# On Linux / macOS:
source venv/bin/activate

# Install backend dependencies (in editable mode with dev tools)
pip install -e ".[dev]"

# (Optional) Configure environment variables
cp .env.example .env

# Run FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> **Note:** On first startup, the application will automatically initialize the database schema and seed high-quality curated sample resources from NPTEL, SWAYAM, IIT Delhi, IIT Madras, and GATE CS archives!

The API will be available at:
- **API Base**: `http://localhost:8000/api/v1`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

---

### 2. Frontend Setup

In a new terminal window:

```bash
cd vidyasearch/frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

Open your browser and navigate to **[http://localhost:3000](http://localhost:3000)**.

---

## ⚙️ Environment Configuration

Backend configuration is handled via `pydantic-settings` in `backend/app/config.py`. You can configure settings via environment variables or a `.env` file in `backend/.env`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./vidyasearch.db` | Database connection string (PostgreSQL or SQLite async) |
| `CRAWL_RATE_LIMIT` | `1.0` | Politeness delay (seconds between requests to same domain) |
| `CRAWL_MAX_DEPTH` | `3` | Maximum link traversal depth for crawler |
| `CRAWL_MAX_PAGES` | `10000` | Safety ceiling for maximum pages per crawl session |
| `CRAWL_USER_AGENT` | `VidyaSearchBot/1.0 (+https://github.com/vidyasearch)` | User-Agent string sent during crawling |
| `CRAWL_CONCURRENCY`| `5` | Maximum concurrent HTTP fetches |
| `BM25_K1` | `1.5` | BM25 term frequency saturation parameter |
| `BM25_B` | `0.75` | BM25 document length normalization parameter |
| `PAGERANK_DAMPING` | `0.85` | PageRank damping probability $\alpha$ |
| `PAGERANK_WEIGHT` | `0.3` | Weight of PageRank score in combined search ranking |
| `CACHE_MAX_SIZE` | `1000` | In-memory LRU query cache maximum entries |
| `CACHE_TTL_SECONDS`| `3600` | Cache time-to-live expiration (1 hour) |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins for frontend requests |

---

## 📡 REST API Reference

### Search & Suggestions

#### 1. Search Query
`GET /api/v1/search`

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `q` | string | **Yes** | - | Search query text (e.g. `Machine Learning IIT Madras`) |
| `page` | integer | No | `1` | Pagination page number |
| `per_page` | integer | No | `10` | Results per page (1-50) |
| `ranking` | string | No | `bm25` | Algorithm choice: `bm25` or `tfidf` |
| `domain` | string | No | `None` | Domain filter (e.g. `nptel.ac.in` or `swayam.gov.in`) |

**Sample Response:**
```json
{
  "query": "Machine Learning",
  "total_results": 8,
  "page": 1,
  "per_page": 10,
  "total_pages": 1,
  "response_time_ms": 4.12,
  "ranking_method": "bm25",
  "results": [
    {
      "doc_id": 2,
      "url": "https://nptel.ac.in/courses/106/106/106106139/",
      "title": "Machine Learning - IIT Madras (NPTEL)",
      "snippet": "...introduction to <mark>Machine</mark> <mark>Learning</mark> supervised and unsupervised algorithms regression classification...",
      "domain": "nptel.ac.in",
      "score": 4.892,
      "pagerank_score": 0.0841,
      "word_count": 84,
      "crawled_at": "2026-08-29T13:22:10Z"
    }
  ],
  "did_you_mean": null,
  "cache_hit": false
}
```

#### 2. Real-time Autocomplete
`GET /api/v1/autocomplete?q=mach&limit=6`

```json
{
  "prefix": "mach",
  "suggestions": [
    "Machine Learning IIT Madras",
    "Machine Learning",
    "Matrix Multiplication Algorithms"
  ]
}
```

#### 3. Spell Check ("Did you mean?")
`GET /api/v1/spellcheck?q=machne+learing`

```json
{
  "query": "machne learing",
  "correction": "machine learning"
}
```

---

### Web Crawling & Index Operations

#### 4. Trigger Web Crawl
`POST /api/v1/crawl?seed_urls=https://nptel.ac.in/courses/&max_pages=5&max_depth=2`

Cuts through the web graph starting from seed URLs, parses documents, updates positional indices, extracts hyper-links, recomputes PageRank scores, and refreshes the autocomplete trie.

#### 5. Recompute PageRank
`POST /api/v1/pagerank/recompute`

Re-runs power iteration link analysis across all stored document nodes and persists new authority scores.

#### 6. Database Seeder
`POST /api/v1/seed?force=true`

Seeds or resets the database with comprehensive pre-curated Indian college resources and link structures.

---

### Telemetry & Diagnostics

#### 7. Search Analytics Summary
`GET /api/v1/analytics`

Returns overall search counts, average latency, cache hit rate, zero-result query rate, and top searched queries.

#### 8. System Index Statistics
`GET /api/v1/stats`

```json
{
  "total_documents": 28,
  "total_indexed_terms": 742,
  "total_link_edges": 64,
  "total_searches": 142,
  "cache": {
    "size": 18,
    "max_size": 1000,
    "hits": 89,
    "misses": 53,
    "hit_rate_pct": 62.68
  }
}
```

---

## 📂 Project Structure

```
vidyasearch/
├── backend/
│   ├── alembic/                 # Database migrations (Alembic)
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── analytics/           # Search query logging & CTR tracking
│   │   │   └── tracker.py
│   │   ├── api/                 # FastAPI routers & endpoints
│   │   │   └── router.py
│   │   ├── autocomplete/        # Trie data structure & suggestion engine
│   │   │   ├── trie.py
│   │   │   └── suggestion_engine.py
│   │   ├── cache/               # LRU + TTL in-memory query cache
│   │   │   └── query_cache.py
│   │   ├── crawler/             # Polite async web crawling system
│   │   │   ├── crawl_manager.py
│   │   │   ├── fetcher.py
│   │   │   ├── html_parser.py
│   │   │   ├── robots_parser.py
│   │   │   └── url_frontier.py
│   │   ├── indexer/             # Text processing & positional indexing
│   │   │   ├── tokenizer.py
│   │   │   ├── normalizer.py
│   │   │   └── inverted_index_builder.py
│   │   ├── models/              # SQLAlchemy database ORM entities
│   │   │   ├── document.py
│   │   │   ├── inverted_index.py
│   │   │   ├── link_graph.py
│   │   │   └── analytics.py
│   │   ├── pagerank/            # Graph link authority calculation
│   │   │   └── pagerank.py
│   │   ├── ranking/             # Scoring algorithms & query parsing
│   │   │   ├── bm25.py
│   │   │   ├── tf_idf.py
│   │   │   ├── query_parser.py
│   │   │   ├── ranker.py
│   │   │   └── snippet_generator.py
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   │   ├── search.py
│   │   │   └── analytics.py
│   │   ├── seed/                # Curated Indian college resources
│   │   │   ├── sample_data.py
│   │   │   └── seeder.py
│   │   ├── typo/                # Levenshtein distance spell checker
│   │   │   └── spell_checker.py
│   │   ├── config.py            # Pydantic Settings
│   │   ├── database.py          # Async engine & session lifecycle
│   │   └── main.py              # Application entry point & CORS
│   ├── tests/                   # Pytest test suite
│   │   └── test_search_engine.py
│   ├── pyproject.toml           # Python package & dependency definition
│   └── alembic.ini
│
├── frontend/
│   ├── public/                  # Static assets & SVG icons
│   ├── src/
│   │   └── app/
│   │       ├── favicon.ico
│   │       ├── globals.css      # Design tokens, dark theme & animations
│   │       ├── layout.tsx       # Root layout & Google Inter font
│   │       └── page.tsx         # Complete Search UI, Crawler & Analytics
│   ├── package.json             # Next.js 14 dependencies & scripts
│   ├── tsconfig.json            # TypeScript configuration
│   └── next.config.ts
│
├── LICENSE                      # MIT Open Source License
└── README.md                    # Project documentation
```

---

## 🧪 Testing & Quality Assurance

VidyaSearch includes a comprehensive test suite covering all IR algorithms and components:

```bash
cd backend
pytest tests/ -v
```

### Test Coverage Highlights
- **Tokenizer & Stemmer**: Validates stopword removal, stemming rules, and positional token extraction.
- **Trie Autocomplete**: Verifies prefix searching and frequency-weighted ranking.
- **Levenshtein Spell Checker**: Validates edit distance calculations and dictionary corrections.
- **BM25 & TF-IDF Scorers**: Verifies term saturation, document length penalties, and score monotonicity.
- **Query Parser**: Verifies exact phrase queries (`"..."`), term exclusions (`-term`), and site filters (`site:iitd.ac.in`).
- **PageRank Calculator**: Tests symmetric and asymmetric graph structures and damping convergence.
- **LRU Query Cache**: Tests capacity eviction, TTL expiration, and telemetry tracking.
- **Full-Flow Integration Test**: Boots an in-memory SQLite database, seeds data, and executes full multi-term BM25 and TF-IDF search pipelines.

---

## 🎯 Target Educational Resources

VidyaSearch is designed to index academic resources across India's premier education networks:

| Resource Portal | Domain | Content Type | Status |
| :--- | :--- | :--- | :--- |
| **NPTEL** | `nptel.ac.in` | Video lectures, course assignments, transcripts | 🟢 Active |
| **SWAYAM** | `swayam.gov.in` | National MOOC courses, credit transfer syllabi | 🟢 Active |
| **IIT Delhi** | `iitd.ac.in` | Department lecture notes, course outlines (e.g. COL331) | 🟢 Active |
| **IIT Madras** | `iitm.ac.in` | CS / EE research & undergraduate resources | 🟢 Active |
| **IIT Bombay** | `iitb.ac.in` | CSE repository & engineering lecture archives | 🟢 Active |
| **GATE CS Prep** | `gate.iitk.ac.in` | Previous year questions (PYQ), syllabus modules | 🟢 Active |
| **NIT Network** | `nit*.ac.in` | Regional engineering college study materials | 🟡 Crawling |
| **AICTE / UGC** | `aicte-india.org` | Model curricula, faculty lecture series | 🔴 Planned |

---

## 🗺️ Roadmap & Future Enhancements

- [ ] **Vector Hybrid Search (Dense + Sparse)**: Integrate Sentence-Transformers (`all-MiniLM-L6-v2`) with pgvector alongside BM25 for semantic retrieval.
- [ ] **PDF & Document Parsing**: Extract text directly from uploaded lecture PDFs, question papers, and presentation slide decks (`pdfplumber` / `PyPDF2`).
- [ ] **Personalized Learning Bookmarks**: User accounts with saved resources, personalized search history, and course roadmaps.
- [ ] **Distributed Worker Queue**: Celery / Redis-backed distributed crawl workers for multi-node web scale crawling.

---

## 🤝 Contributing

Contributions are warmly welcomed! To contribute:

1. Fork the Project repository.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

<div align="center">
Built with ❤️ for Indian Students, Researchers, and Educators.
</div>

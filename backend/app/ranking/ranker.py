"""
VidyaSearch — Unified Search Ranker

Orchestrates retrieval from the Inverted Index and scores candidates
using BM25 or TF-IDF combined with PageRank and positional signals,
dense semantic similarity, or a hybrid of BM25 + semantic fused with
Reciprocal Rank Fusion (RRF).
"""

from collections import defaultdict
from typing import Dict, List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.inverted_index import InvertedIndex, CorpusStats
from app.ranking.query_parser import QueryParser, ParsedQuery
from app.ranking.bm25 import BM25Scorer
from app.ranking.tf_idf import TFIDFScorer
from app.ranking.snippet_generator import SnippetGenerator
from app.schemas.search import SearchResultItem
from app.config import settings
from app.semantic.semantic_encoder import SemanticEncoder
from app.semantic.embedding_store import EmbeddingStore


class Ranker:
    """Unified Search Ranking Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.bm25_scorer = BM25Scorer(k1=settings.bm25_k1, b=settings.bm25_b)
        self.tfidf_scorer = TFIDFScorer()

    async def get_corpus_stats(self) -> Tuple[int, float]:
        """Fetch total document count and average document length."""
        corpus_stat = await self.session.execute(
            select(CorpusStats).where(CorpusStats.term == "__CORPUS__")
        )
        entry = corpus_stat.scalar_one_or_none()
        if not entry or entry.doc_frequency == 0:
            # Fallback direct count
            doc_count = (await self.session.execute(select(Document))).scalars().all()
            total_docs = len(doc_count)
            total_words = sum(d.word_count for d in doc_count)
            avgdl = (total_words / total_docs) if total_docs > 0 else 100.0
            return total_docs, avgdl

        total_docs = entry.doc_frequency
        avgdl = (entry.total_words / total_docs) if total_docs > 0 else 100.0
        return total_docs, avgdl

    async def search(
        self,
        query_str: str,
        ranking_method: str = "bm25",
        domain_filter: str | None = None,
        limit: int = 50,
    ) -> List[SearchResultItem]:
        """
        Execute search and return ranked results with snippets.
        Supports ranking_method: 'bm25', 'tfidf', 'semantic', or 'hybrid'.
        """
        if ranking_method.lower() == "hybrid":
            return await self.hybrid_search(
                query_str=query_str,
                domain_filter=domain_filter,
                limit=limit,
            )

        if ranking_method.lower() == "semantic":
            return await self.semantic_search(
                query_str=query_str,
                domain_filter=domain_filter,
                limit=limit,
            )

        parsed: ParsedQuery = QueryParser.parse(query_str)
        if not parsed.terms and not parsed.raw_terms:
            return []

        search_terms = parsed.terms if parsed.terms else parsed.raw_terms

        # 1. Fetch postings for all search terms
        posting_stmt = select(InvertedIndex).where(InvertedIndex.term.in_(search_terms))
        posting_res = await self.session.execute(posting_stmt)
        postings = posting_res.scalars().all()

        if not postings:
            return []

        # 2. Group postings by doc_id
        doc_term_tfs: Dict[int, Dict[str, int]] = defaultdict(dict)
        doc_term_positions: Dict[int, Dict[str, List[int]]] = defaultdict(dict)
        term_doc_frequencies: Dict[str, int] = defaultdict(int)

        for p in postings:
            doc_term_tfs[p.doc_id][p.term] = p.term_frequency
            doc_term_positions[p.doc_id][p.term] = p.positions or []

        # 3. Get term doc frequencies
        stats_stmt = select(CorpusStats).where(CorpusStats.term.in_(search_terms))
        stats_res = await self.session.execute(stats_stmt)
        for s in stats_res.scalars().all():
            term_doc_frequencies[s.term] = s.doc_frequency

        for term in search_terms:
            if term not in term_doc_frequencies:
                term_doc_frequencies[term] = sum(
                    1 for doc_id in doc_term_tfs if term in doc_term_tfs[doc_id]
                )

        candidate_doc_ids = list(doc_term_tfs.keys())
        if not candidate_doc_ids:
            return []

        # 4. Fetch candidate Document models
        docs_stmt = select(Document).where(Document.id.in_(candidate_doc_ids))
        if domain_filter or parsed.site_filter:
            target_domain = domain_filter or parsed.site_filter
            docs_stmt = docs_stmt.where(Document.domain.ilike(f"%{target_domain}%"))

        docs_res = await self.session.execute(docs_stmt)
        documents = {doc.id: doc for doc in docs_res.scalars().all()}

        total_docs, avgdl = await self.get_corpus_stats()

        # 5. Score candidates
        scored_items: List[SearchResultItem] = []

        for doc_id, doc in documents.items():
            tfs = doc_term_tfs[doc_id]
            doc_len = doc.word_count or len(doc.body.split()) or 100

            # Base relevance score
            if ranking_method.lower() == "tfidf":
                base_score = self.tfidf_scorer.score_document(
                    term_frequencies=tfs,
                    doc_frequencies=term_doc_frequencies,
                    query_terms=search_terms,
                    total_docs=total_docs,
                )
            else:
                base_score = self.bm25_scorer.score_document(
                    term_frequencies=tfs,
                    doc_frequencies=term_doc_frequencies,
                    query_terms=search_terms,
                    doc_length=doc_len,
                    avg_doc_length=avgdl,
                    total_docs=total_docs,
                )

            # Title match boost (if terms appear in title, add boost)
            title_lower = doc.title.lower()
            title_matches = sum(1 for t in parsed.raw_terms if t.lower() in title_lower)
            title_boost = 1.0 + (0.5 * title_matches)

            # PageRank multiplier
            pagerank_boost = 1.0 + (settings.pagerank_weight * (doc.pagerank_score or 0.0))

            final_score = base_score * title_boost * pagerank_boost

            snippet = SnippetGenerator.generate_snippet(
                text=doc.body or doc.description,
                query_terms=parsed.raw_terms or parsed.terms,
                snippet_length=settings.search_snippet_length,
            )

            scored_items.append(
                SearchResultItem(
                    doc_id=doc.id,
                    url=doc.url,
                    title=doc.title or doc.url,
                    snippet=snippet,
                    domain=doc.domain,
                    score=round(final_score, 4),
                    pagerank_score=round(doc.pagerank_score or 0.0, 4),
                    word_count=doc.word_count,
                    crawled_at=doc.crawled_at,
                )
            )

        # 6. Sort by descending final score
        scored_items.sort(key=lambda item: item.score, reverse=True)
        return scored_items[:limit]

    async def semantic_search(
        self,
        query_str: str,
        domain_filter: str | None = None,
        limit: int = 50,
    ) -> List[SearchResultItem]:
        """
        Dense-vector semantic search using sentence-transformers embeddings.

        Steps:
          1. Encode the query to a float32 vector (async thread-pool).
          2. Cosine-similarity search over the in-memory EmbeddingStore.
          3. Fetch matching Document rows from DB.
          4. Apply PageRank authority boost.
          5. Return ranked SearchResultItems (same format as BM25/TF-IDF).
        """
        import asyncio

        store = EmbeddingStore.get_instance()

        if store.is_empty:
            return []

        # Encode query in thread pool (CPU-bound)
        encoder = await SemanticEncoder.get_instance(settings.semantic_model)
        loop = asyncio.get_event_loop()
        query_vec = await loop.run_in_executor(
            None, lambda: encoder.encode_query(query_str)
        )

        # Cosine similarity over in-memory matrix
        top_k = min(settings.semantic_top_k, store.count)
        sim_results = store.cosine_search(query_vec, top_k=top_k)

        if not sim_results:
            return []

        # Build score map: doc_id → cosine similarity
        candidate_ids = [doc_id for doc_id, _ in sim_results]
        sim_scores = {doc_id: score for doc_id, score in sim_results}

        # Fetch Documents from DB
        docs_stmt = select(Document).where(Document.id.in_(candidate_ids))
        if domain_filter:
            docs_stmt = docs_stmt.where(Document.domain.ilike(f"%{domain_filter}%"))

        docs_res = await self.session.execute(docs_stmt)
        documents = {doc.id: doc for doc in docs_res.scalars().all()}

        if not documents:
            return []

        # Normalise PageRank across candidates for fair blending
        pr_values = [doc.pagerank_score or 0.0 for doc in documents.values()]
        max_pr = max(pr_values) if pr_values else 1.0
        if max_pr == 0.0:
            max_pr = 1.0

        scored_items: List[SearchResultItem] = []
        w_pr = settings.semantic_pagerank_weight

        for doc_id, doc in documents.items():
            cosine_sim = sim_scores.get(doc_id, 0.0)
            norm_pr = (doc.pagerank_score or 0.0) / max_pr

            # Blend: (1 - w_pr) * semantic_sim + w_pr * pagerank
            final_score = (1.0 - w_pr) * cosine_sim + w_pr * norm_pr

            # Generate snippet using original query terms for highlighting
            raw_terms = query_str.split()
            snippet = SnippetGenerator.generate_snippet(
                text=doc.body or doc.description,
                query_terms=raw_terms,
                snippet_length=settings.search_snippet_length,
            )

            scored_items.append(
                SearchResultItem(
                    doc_id=doc.id,
                    url=doc.url,
                    title=doc.title or doc.url,
                    snippet=snippet,
                    domain=doc.domain,
                    score=round(final_score, 4),
                    pagerank_score=round(doc.pagerank_score or 0.0, 4),
                    word_count=doc.word_count,
                    crawled_at=doc.crawled_at,
                )
            )

        scored_items.sort(key=lambda item: item.score, reverse=True)
        return scored_items[:limit]

    async def hybrid_search(
        self,
        query_str: str,
        domain_filter: str | None = None,
        limit: int = 50,
    ) -> List[SearchResultItem]:
        """
        Hybrid search: BM25 (exact keywords, course codes, names) fused with
        semantic search (meaning) via Reciprocal Rank Fusion.

            RRF(d) = sum over lists of 1 / (k + rank(d))

        RRF uses only ranks, so the incomparable BM25 and cosine score scales
        never need to be normalised against each other. Scores are scaled to
        0-1 by dividing by the best possible value (rank 1 in both lists).
        If no embeddings exist yet, this degrades gracefully to BM25 ranking.
        """
        pool = settings.hybrid_candidates
        k = settings.hybrid_rrf_k

        # site: operators are parsed out by the BM25 path; honour them for the
        # semantic side too so both lists cover the same domain.
        semantic_domain = domain_filter or QueryParser.parse(query_str).site_filter

        keyword_results = await self.search(
            query_str, ranking_method="bm25", domain_filter=domain_filter, limit=pool
        )
        semantic_results = await self.semantic_search(
            query_str, domain_filter=semantic_domain, limit=pool
        )

        fused: Dict[int, float] = defaultdict(float)
        items: Dict[int, SearchResultItem] = {}
        # Keyword list goes last so its snippet (highlighting real term
        # matches) wins for documents found by both retrievers.
        for results in (semantic_results, keyword_results):
            for rank, item in enumerate(results, start=1):
                fused[item.doc_id] += 1.0 / (k + rank)
                items[item.doc_id] = item

        max_possible = 2.0 / (k + 1)
        hybrid_items = [
            items[doc_id].model_copy(update={"score": round(score / max_possible, 4)})
            for doc_id, score in fused.items()
        ]
        hybrid_items.sort(key=lambda item: item.score, reverse=True)
        return hybrid_items[:limit]

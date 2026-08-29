"""
VidyaSearch — PageRank Algorithm

Calculates link-based authority scores for documents using the
Power Iteration algorithm with damping factor (0.85) and teleportation.
"""

from collections import defaultdict
from typing import Dict, List, Set, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.link_graph import LinkGraph
from app.config import settings


class PageRankCalculator:
    """Computes PageRank vector over the crawled web link graph."""

    def __init__(
        self,
        damping: float = settings.pagerank_damping,
        max_iterations: int = settings.pagerank_max_iterations,
        tol: float = settings.pagerank_convergence,
    ):
        self.damping = damping
        self.max_iterations = max_iterations
        self.tol = tol

    @staticmethod
    def compute_pagerank(
        nodes: List[str],
        edges: List[Tuple[str, str]],
        damping: float = 0.85,
        max_iterations: int = 100,
        tol: float = 1e-6,
    ) -> Dict[str, float]:
        """
        Pure Python Power Iteration PageRank calculation.

        Nodes: list of unique URL strings
        Edges: list of (source_url, target_url) directed edges
        """
        N = len(nodes)
        if N == 0:
            return {}
        if N == 1:
            return {nodes[0]: 1.0}

        # Build in-links and out-degree maps
        in_links: Dict[str, Set[str]] = defaultdict(set)
        out_degree: Dict[str, int] = defaultdict(int)

        for src, dst in edges:
            if src in nodes and dst in nodes and src != dst:
                in_links[dst].add(src)
                out_degree[src] += 1

        # Initial uniform distribution: PR(p) = 1 / N
        ranks: Dict[str, float] = {node: 1.0 / N for node in nodes}

        for iteration in range(max_iterations):
            # Calculate dangling sum (nodes with 0 outgoing links distribute rank uniformly)
            dangling_sum = sum(ranks[node] for node in nodes if out_degree[node] == 0)
            
            new_ranks: Dict[str, float] = {}
            diff = 0.0

            for node in nodes:
                # Rank received from incoming links
                rank_from_inlinks = sum(
                    ranks[in_node] / out_degree[in_node]
                    for in_node in in_links[node]
                )
                # Distributed dangling node share
                rank_from_dangling = dangling_sum / N
                
                # Standard PageRank formula: (1 - d)/N + d * (Σ PR(v)/out(v) + dangling/N)
                new_rank = ((1.0 - damping) / N) + damping * (rank_from_inlinks + rank_from_dangling)
                
                diff += abs(new_rank - ranks[node])
                new_ranks[node] = new_rank

            ranks = new_ranks

            # Check convergence
            if diff < tol:
                break

        # Normalize so sum(ranks) = 1.0
        total_sum = sum(ranks.values()) or 1.0
        return {node: rank / total_sum for node, rank in ranks.items()}

    @classmethod
    async def recompute_and_update(cls, session: AsyncSession) -> Dict[str, float]:
        """
        Fetch web graph from database, compute PageRank, and update Document records.
        """
        # Fetch all document URLs
        doc_stmt = select(Document.url)
        doc_res = await session.execute(doc_stmt)
        urls = [row[0] for row in doc_res.all()]

        if not urls:
            return {}

        # Fetch all link edges
        edge_stmt = select(LinkGraph.source_url, LinkGraph.target_url)
        edge_res = await session.execute(edge_stmt)
        edges = [(row[0], row[1]) for row in edge_res.all()]

        # Compute PageRank scores
        scores = cls.compute_pagerank(
            nodes=urls,
            edges=edges,
            damping=settings.pagerank_damping,
            max_iterations=settings.pagerank_max_iterations,
            tol=settings.pagerank_convergence,
        )

        # Scale scores for intuitive ranking boost (normalized around 0.1 to 1.0)
        max_score = max(scores.values()) if scores else 1.0
        min_score = min(scores.values()) if scores else 0.0
        score_range = max(max_score - min_score, 1e-6)

        # Update Document records
        for url, score in scores.items():
            normalized_score = (score - min_score) / score_range
            await session.execute(
                update(Document)
                .where(Document.url == url)
                .values(pagerank_score=normalized_score)
            )

        await session.commit()
        return scores

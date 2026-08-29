"""
VidyaSearch — Database Seeder

Populates sample documents, link graph, builds inverted index,
and computes PageRank for immediate testing.
"""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.link_graph import LinkGraph
from app.seed.sample_data import SAMPLE_DOCUMENTS, SAMPLE_LINKS
from app.indexer.inverted_index_builder import Indexer
from app.pagerank.pagerank import PageRankCalculator
from app.autocomplete.suggestion_engine import SuggestionEngine
from app.typo.spell_checker import SpellChecker


async def seed_database(session: AsyncSession, force: bool = False) -> dict:
    """Seed the database with sample Indian college resources."""
    doc_count_res = await session.execute(select(Document.id))
    existing_count = len(doc_count_res.scalars().all())

    if existing_count > 0 and not force:
        # Already seeded, just ensure engines are initialized
        await SuggestionEngine.build_from_db(session)
        await SpellChecker.build_vocabulary(session)
        return {"status": "skipped", "message": f"Database already has {existing_count} documents"}

    if force:
        await session.execute(delete(Document))
        await session.execute(delete(LinkGraph))
        await session.flush()

    # 1. Insert Documents
    docs_to_add = []
    for doc_data in SAMPLE_DOCUMENTS:
        doc = Document(
            url=doc_data["url"],
            title=doc_data["title"],
            domain=doc_data["domain"],
            description=doc_data["description"],
            body=doc_data["body"],
            pagerank_score=doc_data.get("pagerank_score", 0.5),
            word_count=len(doc_data["body"].split()),
        )
        docs_to_add.append(doc)

    session.add_all(docs_to_add)
    await session.flush()

    # 2. Insert Link Graph
    links_to_add = []
    for src, dst, anchor in SAMPLE_LINKS:
        link = LinkGraph(
            source_url=src,
            target_url=dst,
            anchor_text=anchor,
        )
        links_to_add.append(link)

    session.add_all(links_to_add)
    await session.flush()

    # 3. Build Inverted Index
    indexed_entries = await Indexer.index_all_documents(session)

    # 4. Compute PageRank
    await PageRankCalculator.recompute_and_update(session)

    # 5. Initialize Autocomplete & Spellchecker
    await SuggestionEngine.build_from_db(session)
    await SpellChecker.build_vocabulary(session)

    await session.commit()

    return {
        "status": "success",
        "documents_added": len(docs_to_add),
        "links_added": len(links_to_add),
        "indexed_entries": indexed_entries,
    }

"""
VidyaSearch — Inverted Index Builder

Processes crawled documents, extracts terms, positional indexes,
updates the inverted index table, and maintains corpus statistics.
"""

from collections import defaultdict
from typing import Dict, List, Tuple
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.inverted_index import InvertedIndex, CorpusStats
from app.indexer.tokenizer import tokenize_with_positions
from app.indexer.normalizer import simple_stem, STOPWORDS


class Indexer:
    """Builds and updates inverted index from Document records."""

    @staticmethod
    def extract_document_terms(title: str, body: str, description: str = "") -> Tuple[Dict[str, Dict], int]:
        """
        Extract terms with term frequencies and positions from title + description + body.
        Title terms get higher initial occurrence weighting in search.
        
        Returns:
            term_dict: {term: {'tf': count, 'positions': [pos1, pos2, ...]}}
            total_words: total word count in document
        """
        full_text = f"{title} {description} {body}"
        token_positions = tokenize_with_positions(full_text)
        
        term_dict = defaultdict(lambda: {"tf": 0, "positions": []})
        total_words = len(token_positions)
        
        for token, pos in token_positions:
            if token in STOPWORDS or len(token) < 2:
                continue
            stemmed = simple_stem(token)
            term_dict[stemmed]["tf"] += 1
            term_dict[stemmed]["positions"].append(pos)
            
        return term_dict, total_words

    @classmethod
    async def index_document(cls, session: AsyncSession, doc: Document) -> int:
        """
        Index a single document into inverted_index table.
        Removes any previous index entries for this doc_id first.
        """
        # Delete existing entries for this doc
        await session.execute(
            delete(InvertedIndex).where(InvertedIndex.doc_id == doc.id)
        )

        terms_data, total_words = cls.extract_document_terms(
            title=doc.title,
            body=doc.body,
            description=doc.description
        )

        doc.word_count = total_words

        entries = []
        for term, data in terms_data.items():
            entry = InvertedIndex(
                term=term,
                doc_id=doc.id,
                term_frequency=data["tf"],
                positions=data["positions"]
            )
            entries.append(entry)

        if entries:
            session.add_all(entries)

        await session.flush()
        return len(entries)

    @classmethod
    async def index_all_documents(cls, session: AsyncSession, batch_size: int = 100) -> int:
        """Index all documents in the database and recompute corpus statistics."""
        # Clear inverted index
        await session.execute(delete(InvertedIndex))
        await session.execute(delete(CorpusStats))
        await session.flush()

        stmt = select(Document)
        result = await session.execute(stmt)
        docs = result.scalars().all()

        total_indexed_entries = 0
        term_doc_freq = defaultdict(int)
        total_corpus_words = 0

        for doc in docs:
            terms_data, total_words = cls.extract_document_terms(
                title=doc.title,
                body=doc.body,
                description=doc.description
            )
            doc.word_count = total_words
            total_corpus_words += total_words

            entries = []
            for term, data in terms_data.items():
                entries.append(
                    InvertedIndex(
                        term=term,
                        doc_id=doc.id,
                        term_frequency=data["tf"],
                        positions=data["positions"]
                    )
                )
                term_doc_freq[term] += 1

            if entries:
                session.add_all(entries)
                total_indexed_entries += len(entries)

        # Store Corpus Level Stats
        corpus_entry = CorpusStats(
            term="__CORPUS__",
            doc_frequency=len(docs),
            total_words=total_corpus_words
        )
        session.add(corpus_entry)

        # Store per-term document frequencies
        stat_entries = [
            CorpusStats(term=term, doc_frequency=df, total_words=0)
            for term, df in term_doc_freq.items()
        ]
        session.add_all(stat_entries)

        await session.commit()
        return total_indexed_entries

    @classmethod
    async def update_corpus_stats(cls, session: AsyncSession):
        """Recalculate aggregate corpus statistics."""
        doc_count_res = await session.execute(select(func.count(Document.id)))
        total_docs = doc_count_res.scalar() or 0

        total_words_res = await session.execute(select(func.sum(Document.word_count)))
        total_words = total_words_res.scalar() or 0

        # Update or insert __CORPUS__
        corpus_stat = await session.execute(
            select(CorpusStats).where(CorpusStats.term == "__CORPUS__")
        )
        entry = corpus_stat.scalar_one_or_none()
        if entry:
            entry.doc_frequency = total_docs
            entry.total_words = total_words
        else:
            session.add(CorpusStats(term="__CORPUS__", doc_frequency=total_docs, total_words=total_words))

        await session.commit()

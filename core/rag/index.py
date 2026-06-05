"""
core/rag/index.py
~~~~~~~~~~~~~~~~~
SQLite-backed vector index for the GAIA-OS RAG pipeline.

Public surface
--------------
VectorIndex  — add_chunks(), search(), keyword_search(), count(), sources(),
               delete_source(), from_store().

All embeddings are stored as raw float32 bytes in SQLite.
Cosine similarity is computed in pure numpy/Python for portability.
"""

from __future__ import annotations

import logging
import sqlite3
import struct
from pathlib import Path
from typing import List, Optional, Tuple

from .chunker import Chunk

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Embedding shim — produce a fixed-length float vector from text
# ---------------------------------------------------------------------------

try:
    import numpy as np
    _NUMPY = True
except ImportError:
    _NUMPY = False


def _bag_of_words_embed(text: str, vocab_size: int = 256) -> List[float]:
    """Deterministic bag-of-words embedding (no ML, always available)."""
    vec = [0.0] * vocab_size
    for ch in text.lower():
        vec[ord(ch) % vocab_size] += 1.0
    total = sum(vec)
    if total > 0:
        vec = [v / total for v in vec]
    return vec


def _embed(text: str, dim: int = 256) -> List[float]:
    return _bag_of_words_embed(text, vocab_size=dim)


def _cosine(a: List[float], b: List[float]) -> float:
    if _NUMPY:
        import numpy as np
        av, bv = np.array(a, dtype=np.float32), np.array(b, dtype=np.float32)
        denom = np.linalg.norm(av) * np.linalg.norm(bv)
        return float(np.dot(av, bv) / denom) if denom > 0 else 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na  = sum(x * x for x in a) ** 0.5
    nb  = sum(x * x for x in b) ** 0.5
    return dot / (na * nb) if na * nb > 0 else 0.0


def _pack(vec: List[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def _unpack(data: bytes) -> List[float]:
    n = len(data) // 4
    return list(struct.unpack(f"{n}f", data))


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_DDL = """
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id   TEXT PRIMARY KEY,
    text       TEXT NOT NULL,
    source     TEXT NOT NULL,
    doc_title  TEXT DEFAULT '',
    section    TEXT DEFAULT '',
    char_start INTEGER DEFAULT 0,
    embedding  BLOB
);
CREATE INDEX IF NOT EXISTS idx_source ON chunks(source);
"""


# ---------------------------------------------------------------------------
# VectorIndex
# ---------------------------------------------------------------------------

class VectorIndex:
    """
    SQLite-backed vector index.

    Parameters
    ----------
    db_path : SQLite file path, or ':memory:' for an in-memory DB.
    dim     : Embedding dimension (must match stored embeddings).
    """

    def __init__(
        self,
        db_path: str = ":memory:",
        dim: int = 256,
    ) -> None:
        self._db_path = db_path
        self._dim = dim
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.executescript(_DDL)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Class methods
    # ------------------------------------------------------------------

    @classmethod
    def from_store(cls, store: Any) -> "VectorIndex":  # type: ignore[name-defined]
        """Open the VectorIndex stored at store.db_path."""
        idx = cls(db_path=str(store.db_path))
        return idx

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add_chunks(
        self,
        chunks: List[Chunk],
        embedder: Optional[Any] = None,
    ) -> int:
        """
        Add *chunks* to the index.  Chunks with duplicate chunk_ids are
        silently skipped (INSERT OR IGNORE).

        Returns
        -------
        int  Number of new rows inserted.
        """
        if not chunks:
            return 0

        added = 0
        cur = self._conn.cursor()
        for chunk in chunks:
            embedding = (
                embedder.embed(chunk.text)
                if embedder is not None
                else _embed(chunk.text, self._dim)
            )
            blob = _pack(embedding)
            try:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO chunks
                        (chunk_id, text, source, doc_title, section, char_start, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chunk.chunk_id,
                        chunk.text,
                        chunk.source,
                        chunk.doc_title,
                        chunk.section,
                        chunk.char_start,
                        blob,
                    ),
                )
                if cur.rowcount:
                    added += 1
            except sqlite3.Error as exc:
                logger.warning("add_chunks: sqlite error for chunk %s — %s", chunk.chunk_id, exc)
        self._conn.commit()
        return added

    def add(self, chunks: List[Chunk], embedder: Optional[Any] = None) -> int:
        """Alias for add_chunks()."""
        return self.add_chunks(chunks, embedder=embedder)

    def delete_source(self, source: str) -> int:
        """Delete all chunks from *source*. Returns number of rows deleted."""
        cur = self._conn.cursor()
        cur.execute("DELETE FROM chunks WHERE source = ?", (source,))
        self._conn.commit()
        return cur.rowcount

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return the total number of stored chunks."""
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM chunks")
        return cur.fetchone()[0]

    def size(self) -> int:
        """Alias for count()."""
        return self.count()

    def sources(self) -> List[str]:
        """Return a sorted list of unique source identifiers."""
        cur = self._conn.cursor()
        cur.execute("SELECT DISTINCT source FROM chunks ORDER BY source")
        return [row[0] for row in cur.fetchall()]

    def search(
        self,
        query: str,
        top_k: int = 5,
        embedder: Optional[Any] = None,
    ) -> List[Tuple[Chunk, float]]:
        """
        Dense cosine-similarity search.

        Returns
        -------
        List[(Chunk, float)]  Sorted by descending similarity.
        """
        q_emb = (
            embedder.embed(query)
            if embedder is not None
            else _embed(query, self._dim)
        )

        cur = self._conn.cursor()
        cur.execute(
            "SELECT chunk_id, text, source, doc_title, section, char_start, embedding FROM chunks"
        )
        rows = cur.fetchall()

        scored: List[Tuple[Chunk, float]] = []
        for row in rows:
            chunk_id, text, source, doc_title, section, char_start, blob = row
            emb = _unpack(blob) if blob else _embed("", self._dim)
            score = _cosine(q_emb, emb)
            scored.append((
                Chunk(
                    chunk_id=chunk_id,
                    text=text,
                    source=source,
                    doc_title=doc_title,
                    section=section,
                    char_start=char_start,
                ),
                score,
            ))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def keyword_search(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Tuple[Chunk, float]]:
        """
        Sparse keyword search using SQLite LIKE matching.
        Score is term frequency of matched words normalised to [0, 1].

        Returns
        -------
        List[(Chunk, float)]  Sorted by descending score.
        """
        terms = [t.lower() for t in query.split() if t.strip()]
        if not terms:
            return []

        cur = self._conn.cursor()
        cur.execute(
            "SELECT chunk_id, text, source, doc_title, section, char_start FROM chunks"
        )
        rows = cur.fetchall()

        scored: List[Tuple[Chunk, float]] = []
        for row in rows:
            chunk_id, text, source, doc_title, section, char_start = row
            text_lower = text.lower()
            hits = sum(1 for t in terms if t in text_lower)
            if hits == 0:
                continue
            score = hits / len(terms)
            scored.append((
                Chunk(
                    chunk_id=chunk_id,
                    text=text,
                    source=source,
                    doc_title=doc_title,
                    section=section,
                    char_start=char_start,
                ),
                score,
            ))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

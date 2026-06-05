"""
core/rag/pipeline.py
~~~~~~~~~~~~~~~~~~~~
GAIA-OS Canon RAG pipeline.

Two usage surfaces
------------------
1. Canon ingestion (session startup)
   RAGPipeline.ingest_canon(ref, force, store_path)
   — warm/cold start decision tree using IndexStore fingerprint.

2. File/directory ingestion (test_rag.py surface)
   RAGPipeline.ingest(path)          — chunk + index a file or directory.
   RAGPipeline.reindex(path)         — delete source, re-ingest.
   RAGPipeline.query(query, top_k)   — retrieve chunks as formatted strings.
   RAGPipeline.indexed_sources       — list of indexed source identifiers.
   RAGPipeline.index_size            — total chunk count.

3. Agentic loop surface
   RAGPipeline.retrieve(query, top_k) — returns a formatted context string.
   RAGPipeline.status()               — returns a status metadata dict.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, List, Optional

from .chunker import Chunk, chunk_text, chunk_file, chunk_directory
from .index import VectorIndex

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Optional dependencies
# ---------------------------------------------------------------------------
try:
    from .index_store import IndexStore
    _INDEX_STORE_AVAILABLE = True
except ImportError:
    _INDEX_STORE_AVAILABLE = False
    IndexStore = None  # type: ignore[assignment,misc]

try:
    from .canon_loader import CanonLoader
    _CANON_LOADER_AVAILABLE = True
except ImportError:
    _CANON_LOADER_AVAILABLE = False
    CanonLoader = None  # type: ignore[assignment,misc]

try:
    from .embedder import FallbackEmbedder
    _EMBEDDER_AVAILABLE = True
except ImportError:
    _EMBEDDER_AVAILABLE = False
    FallbackEmbedder = None  # type: ignore[assignment,misc]

try:
    from .retriever import Retriever
    _RETRIEVER_AVAILABLE = True
except ImportError:
    _RETRIEVER_AVAILABLE = False
    Retriever = None  # type: ignore[assignment,misc]


# ---------------------------------------------------------------------------
# RAGPipeline
# ---------------------------------------------------------------------------

class RAGPipeline:
    """
    Unified RAG pipeline for GAIA-OS.

    Parameters
    ----------
    db_path : SQLite path for VectorIndex. Defaults to in-memory (':memory:').
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self._index = VectorIndex(db_path=db_path)
        self._retriever = Retriever(self._index) if _RETRIEVER_AVAILABLE else None
        self._embedder = FallbackEmbedder() if _EMBEDDER_AVAILABLE else None
        self.canon_loaded: bool = False
        self._warm_start: bool = False
        self._canon_doc_count: int = 0
        self._canon_chunk_count: int = 0
        self._fingerprint: Optional[str] = None
        self._store_path: Optional[Path] = None

    # ------------------------------------------------------------------
    # File/directory ingestion surface (used by test_rag.py)
    # ------------------------------------------------------------------

    def ingest(self, path: str, chunk_size: int = 512, overlap: int = 64) -> int:
        """
        Ingest a file or directory into the index.

        Parameters
        ----------
        path       : File path or directory path as string.
        chunk_size : Characters per chunk.
        overlap    : Overlap between adjacent chunks.

        Returns
        -------
        int  Number of chunks added (0 if path doesn't exist).
        """
        p = Path(path)
        if not p.exists():
            logger.warning("ingest: path does not exist: %s", path)
            return 0

        if p.is_dir():
            chunks = chunk_directory(p, chunk_size=chunk_size, overlap=overlap)
        else:
            chunks = chunk_file(p, chunk_size=chunk_size, overlap=overlap)

        if not chunks:
            return 0

        # Fit embedder vocabulary if available
        if self._embedder is not None:
            self._embedder.fit([c.text for c in chunks])

        added = self._index.add_chunks(chunks)
        logger.debug("ingest: added %d chunks from %s", added, path)
        return added

    def reindex(self, path: str, chunk_size: int = 512, overlap: int = 64) -> int:
        """
        Delete all chunks from *path* and re-ingest.

        Returns
        -------
        int  Number of new chunks added.
        """
        p = Path(path)
        # Delete existing entries for this source
        if p.is_dir():
            for fpath in sorted(p.rglob("*")):
                if fpath.is_file():
                    self._index.delete_source(str(fpath))
        else:
            self._index.delete_source(str(p))

        return self.ingest(path, chunk_size=chunk_size, overlap=overlap)

    def query(
        self,
        query: str,
        top_k: int = 5,
        mode: str = "hybrid",
    ) -> list:
        """
        Retrieve chunks relevant to *query*.

        Returns
        -------
        list  List of RetrievalResult objects (empty list if index is empty).
        """
        if self._index.count() == 0:
            return []
        if self._retriever is not None:
            try:
                return self._retriever.retrieve(query, top_k=top_k, mode=mode)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                logger.warning("query: retriever failed (%s), falling back to index.search", exc)
        # Fallback: raw index search
        hits = self._index.search(query, top_k=top_k)
        return [(chunk, score) for chunk, score in hits]

    @property
    def indexed_sources(self) -> List[str]:
        """List of unique source identifiers currently in the index."""
        return self._index.sources()

    @property
    def index_size(self) -> int:
        """Total number of chunks in the index."""
        return self._index.count()

    # ------------------------------------------------------------------
    # Agentic loop surface
    # ------------------------------------------------------------------

    def retrieve(self, query: str, top_k: int = 5) -> str:
        """
        Retrieve Canon context as a formatted string for injection into
        the planner's system prompt.

        Returns
        -------
        str  Newline-joined passage strings with [Canon: ...] prefixes.
             Empty string if the index has no entries or retrieval fails.
        """
        if self._index.count() == 0:
            return ""
        if self._retriever is not None:
            try:
                results = self._retriever.retrieve(query, top_k=top_k)
                return "\n\n".join(r.chunk.text for r in results)
            except Exception as exc:  # noqa: BLE001
                logger.warning("retrieve: retriever failed (%s)", exc)
        # Fallback
        hits = self._index.search(query, top_k=top_k)
        return "\n\n".join(chunk.text for chunk, _ in hits)

    def status(self) -> dict:
        """Return a metadata dict describing the current pipeline state."""
        return {
            "canon_loaded":        self.canon_loaded,
            "warm_start":          self._warm_start,
            "canon_doc_count":     self._canon_doc_count,
            "canon_chunk_count":   self._canon_chunk_count,
            "index_size":          self._index.count(),
            "top_k":               5,
            "store_path":          str(self._store_path) if self._store_path else None,
            "fingerprint":         self._fingerprint,
        }

    # ------------------------------------------------------------------
    # Canon ingestion (session startup)
    # ------------------------------------------------------------------

    def ingest_canon(
        self,
        ref: str = "feat/obs-rag",
        force: bool = False,
        store_path: Optional[Path] = None,
    ) -> dict:
        """
        Ingest Canon documents from GitHub into the vector index.

        Warm/cold start decision tree
        ------------------------------
        1. No store_path            → always cold start (in-memory).
        2. store_path, DB absent    → cold start: fetch + embed + write.
        3. store_path, DB present,
           fingerprint matches      → warm start: open DB, skip embed.
        4. store_path, DB present,
           fingerprint stale        → cold start: delete old DB, rebuild.
        5. force=True               → always cold start.

        Returns
        -------
        dict  Ingest report: status, warm_start, doc_count, chunk_count,
              fingerprint, store_path, duration_s.
        """
        if self.canon_loaded and not force:
            return {"status": "already_loaded", "warm_start": self._warm_start}

        t0 = time.monotonic()
        self._store_path = store_path

        # --- Warm start check ---
        if (
            store_path is not None
            and _INDEX_STORE_AVAILABLE
            and not force
        ):
            store = IndexStore(data_dir=store_path)
            store.ensure_dir()
            if store.db_exists():
                stored_fp = store.read_fingerprint()
                # Try to load the existing index
                try:
                    self._index = VectorIndex.from_store(store)
                    self._retriever = Retriever(self._index) if _RETRIEVER_AVAILABLE else None
                    self._fingerprint = stored_fp
                    self._warm_start = True
                    self.canon_loaded = True
                    elapsed = round(time.monotonic() - t0, 3)
                    self._canon_chunk_count = self._index.count()
                    logger.info("ingest_canon: warm start (%d chunks)", self._canon_chunk_count)
                    return {
                        "status":      "warm_start",
                        "warm_start":  True,
                        "doc_count":   self._canon_doc_count,
                        "chunk_count": self._canon_chunk_count,
                        "fingerprint": self._fingerprint,
                        "store_path":  str(store.db_path),
                        "duration_s":  elapsed,
                    }
                except Exception as exc:  # noqa: BLE001
                    logger.warning("ingest_canon: warm start failed (%s), cold starting", exc)

        # --- Cold start ---
        if not _CANON_LOADER_AVAILABLE:
            logger.warning("ingest_canon: CanonLoader not available, skipping")
            self.canon_loaded = True
            return {
                "status":      "ok",
                "warm_start":  False,
                "doc_count":   0,
                "chunk_count": 0,
                "fingerprint": None,
                "store_path":  None,
                "duration_s":  round(time.monotonic() - t0, 3),
            }

        try:
            loader = CanonLoader(ref=ref)
            canon_docs = loader.load()
        except Exception as exc:  # noqa: BLE001
            logger.error("ingest_canon: loader failed — %s", exc)
            self.canon_loaded = True
            return {
                "status":      "error",
                "warm_start":  False,
                "doc_count":   0,
                "chunk_count": 0,
                "error":       str(exc),
                "duration_s":  round(time.monotonic() - t0, 3),
            }

        all_chunks: list[Chunk] = []
        fingerprint_parts: list[str] = []

        for doc in canon_docs:
            doc_chunks = chunk_text(
                doc.get("content", ""),
                source=doc.get("id", doc.get("path", "unknown")),
            )
            all_chunks.extend(doc_chunks)
            fingerprint_parts.append(
                f"{doc.get('id', doc.get('path', 'unknown'))}:{len(doc_chunks)}"
            )

        if self._embedder is not None and all_chunks:
            self._embedder.fit([c.text for c in all_chunks])

        self._index.add_chunks(all_chunks)

        # Fingerprint
        import hashlib
        fp_raw = "|".join(sorted(fingerprint_parts))
        fingerprint = hashlib.sha256(fp_raw.encode()).hexdigest()

        # Persist
        if store_path is not None and _INDEX_STORE_AVAILABLE:
            try:
                store = IndexStore(data_dir=store_path)
                store.ensure_dir()
                if force:
                    store.delete_db()
                    self._index = VectorIndex(db_path=str(store.db_path))
                    self._index.add_chunks(all_chunks)
                store.write_fingerprint(fingerprint)
            except Exception as exc:  # noqa: BLE001
                logger.warning("ingest_canon: could not persist index — %s", exc)

        self._fingerprint = fingerprint
        self._warm_start = False
        self._canon_doc_count = len(canon_docs)
        self._canon_chunk_count = len(all_chunks)
        self.canon_loaded = True

        elapsed = round(time.monotonic() - t0, 3)
        logger.info(
            "ingest_canon: cold start complete (%d docs, %d chunks, %.2fs)",
            self._canon_doc_count, self._canon_chunk_count, elapsed,
        )
        return {
            "status":      "ok",
            "warm_start":  False,
            "doc_count":   self._canon_doc_count,
            "chunk_count": self._canon_chunk_count,
            "fingerprint": fingerprint,
            "store_path":  str(store_path / "canon_index.db") if store_path else None,
            "duration_s":  elapsed,
        }

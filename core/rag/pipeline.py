"""
core/rag/pipeline.py
~~~~~~~~~~~~~~~~~~~~
GAIA-OS Canon RAG pipeline.

Three usage surfaces
--------------------
1. Canon ingestion   RAGPipeline.ingest_canon()
2. File/dir ingest   RAGPipeline.ingest() / reindex() / query()
                     RAGPipeline.indexed_sources / index_size
3. Agentic loop      RAGPipeline.retrieve() / status()
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, List, Optional

from .chunker import Chunk, chunk_text, chunk_file, chunk_directory
from .index import VectorIndex

logger = logging.getLogger(__name__)

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


class RAGPipeline:
    """Unified RAG pipeline for GAIA-OS."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self._index     = VectorIndex(db_path=db_path)
        self._retriever = Retriever(self._index) if _RETRIEVER_AVAILABLE else None
        self._embedder  = FallbackEmbedder() if _EMBEDDER_AVAILABLE else None
        self.canon_loaded:       bool           = False
        self._warm_start:        bool           = False
        self._canon_doc_count:   int            = 0
        self._canon_chunk_count: int            = 0
        self._fingerprint:       Optional[str]  = None
        self._store_path:        Optional[Path] = None

    # ------------------------------------------------------------------
    # File/directory ingestion (test_rag.py surface)
    # ------------------------------------------------------------------

    def ingest(self, path: str, chunk_size: int = 512, overlap: int = 64) -> int:
        p = Path(path)
        if not p.exists():
            return 0
        chunks = chunk_directory(p, chunk_size=chunk_size, overlap=overlap) if p.is_dir() \
            else chunk_file(p, chunk_size=chunk_size, overlap=overlap)
        if not chunks:
            return 0
        if self._embedder is not None:
            self._embedder.fit([c.text for c in chunks])
        return self._index.add_chunks(chunks)

    def reindex(self, path: str, chunk_size: int = 512, overlap: int = 64) -> int:
        p = Path(path)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file():
                    self._index.delete_source(str(f))
        else:
            self._index.delete_source(str(p))
        return self.ingest(path, chunk_size=chunk_size, overlap=overlap)

    def query(self, query: str, top_k: int = 5, mode: str = "hybrid") -> list:
        if self._index.count() == 0:
            return []
        if self._retriever is not None:
            try:
                return self._retriever.retrieve(query, top_k=top_k, mode=mode)  # type: ignore[arg-type]
            except Exception as exc:  # noqa: BLE001
                logger.warning("query: retriever error — %s", exc)
        return self._index.search(query, top_k=top_k)

    @property
    def indexed_sources(self) -> List[str]:
        return self._index.sources()

    @property
    def index_size(self) -> int:
        return self._index.count()

    # ------------------------------------------------------------------
    # Agentic loop surface
    # ------------------------------------------------------------------

    def retrieve(self, query: str, top_k: int = 5) -> str:
        if self._index.count() == 0:
            return ""
        if self._retriever is not None:
            try:
                results = self._retriever.retrieve(query, top_k=top_k)
                return "\n\n".join(r.chunk.text for r in results)
            except Exception as exc:  # noqa: BLE001
                logger.warning("retrieve: retriever error — %s", exc)
        return "\n\n".join(c.text for c, _ in self._index.search(query, top_k=top_k))

    def status(self) -> dict:
        return {
            "canon_loaded":       self.canon_loaded,
            "warm_start":         self._warm_start,
            "canon_doc_count":    self._canon_doc_count,
            "canon_chunk_count":  self._canon_chunk_count,
            "index_size":         self._index.count(),
            "top_k":              5,
            "store_path":         str(self._store_path) if self._store_path else None,
            "fingerprint":        self._fingerprint,
        }

    # ------------------------------------------------------------------
    # Canon ingestion (session startup)
    # ------------------------------------------------------------------

    def ingest_canon(
        self,
        ref:        str           = "feat/obs-rag",
        force:      bool          = False,
        store_path: Optional[Path] = None,
    ) -> dict:
        if self.canon_loaded and not force:
            return {"status": "already_loaded", "warm_start": self._warm_start}

        t0 = time.monotonic()
        self._store_path = store_path

        if store_path is not None and _INDEX_STORE_AVAILABLE and not force:
            store = IndexStore(data_dir=store_path)
            store.ensure_dir()
            if store.db_exists():
                try:
                    self._index     = VectorIndex.from_store(store)
                    self._retriever = Retriever(self._index) if _RETRIEVER_AVAILABLE else None
                    self._fingerprint = store.read_fingerprint()
                    self._warm_start  = True
                    self.canon_loaded = True
                    self._canon_chunk_count = self._index.count()
                    return {
                        "status": "warm_start", "warm_start": True,
                        "doc_count": 0, "chunk_count": self._canon_chunk_count,
                        "fingerprint": self._fingerprint,
                        "store_path": str(store.db_path),
                        "duration_s": round(time.monotonic() - t0, 3),
                    }
                except Exception as exc:  # noqa: BLE001
                    logger.warning("ingest_canon: warm start failed — %s", exc)

        if not _CANON_LOADER_AVAILABLE:
            self.canon_loaded = True
            return {
                "status": "ok", "warm_start": False,
                "doc_count": 0, "chunk_count": 0,
                "fingerprint": None, "store_path": None,
                "duration_s": round(time.monotonic() - t0, 3),
            }

        try:
            loader    = CanonLoader(ref=ref)
            canon_docs = loader.load()
        except Exception as exc:  # noqa: BLE001
            self.canon_loaded = True
            return {
                "status": "error", "warm_start": False,
                "doc_count": 0, "chunk_count": 0,
                "error": str(exc),
                "duration_s": round(time.monotonic() - t0, 3),
            }

        all_chunks: list[Chunk] = []
        fp_parts:   list[str]   = []
        for doc in canon_docs:
            doc_chunks = chunk_text(
                doc.get("content", ""),
                source=doc.get("id", doc.get("path", "unknown")),
            )
            all_chunks.extend(doc_chunks)
            fp_parts.append(f"{doc.get('id', doc.get('path', 'unknown'))}:{len(doc_chunks)}")

        if self._embedder is not None and all_chunks:
            self._embedder.fit([c.text for c in all_chunks])
        self._index.add_chunks(all_chunks)

        import hashlib
        fingerprint = hashlib.sha256("|".join(sorted(fp_parts)).encode()).hexdigest()

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
                logger.warning("ingest_canon: persist failed — %s", exc)

        self._fingerprint       = fingerprint
        self._warm_start        = False
        self._canon_doc_count   = len(canon_docs)
        self._canon_chunk_count = len(all_chunks)
        self.canon_loaded       = True

        return {
            "status": "ok", "warm_start": False,
            "doc_count": self._canon_doc_count,
            "chunk_count": self._canon_chunk_count,
            "fingerprint": fingerprint,
            "store_path": str(store_path / "canon_index.db") if store_path else None,
            "duration_s": round(time.monotonic() - t0, 3),
        }

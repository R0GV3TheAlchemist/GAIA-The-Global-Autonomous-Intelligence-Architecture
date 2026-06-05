"""
pipeline.py
~~~~~~~~~~~
RAGPipeline: the single interface the agentic loop uses to ingest Canon
documents and retrieve context at reasoning time.

Changes in this revision
------------------------
* ingest_canon(loader)  — bulk-loads all CanonChunks into the vector store.
* CANON_LOADED flag     — self-reports corpus readiness so the loop can
                         emit an audit event on first load.
* retrieve() now prefixes each result with its [Canon: <id>] citation
  header so the planner always knows the provenance of every context
  block it receives.
* Graceful degradation: every public method catches exceptions and logs
  them rather than propagating, so a broken embedding backend never
  crashes an active session.
"""

from __future__ import annotations

import logging
import time
from typing import List, Optional

from .chunker import Chunker, Chunk
from .embedder import Embedder
from .index import VectorIndex
from .retriever import Retriever

try:
    from .canon_loader import CanonLoader, CanonChunk
    _CANON_LOADER_AVAILABLE = True
except ImportError:  # pragma: no cover
    _CANON_LOADER_AVAILABLE = False

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Orchestrates: ingest → embed → index → retrieve.

    Typical lifecycle
    -----------------
    1. Instantiate once per GAIA session.
    2. Call ingest_canon() at startup to load the Canon corpus.
    3. Call retrieve(query) from _reason() for every planning step.
    """

    def __init__(
        self,
        embedder: Optional[Embedder] = None,
        index: Optional[VectorIndex] = None,
        retriever: Optional[Retriever] = None,
        chunker: Optional[Chunker] = None,
        top_k: int = 5,
    ) -> None:
        self._embedder: Embedder = embedder or Embedder()
        self._index: VectorIndex = index or VectorIndex()
        self._retriever: Retriever = retriever or Retriever(
            index=self._index, embedder=self._embedder, top_k=top_k
        )
        self._chunker: Chunker = chunker or Chunker()
        self._top_k = top_k

        # Canon state
        self.canon_loaded: bool = False
        self._canon_doc_count: int = 0
        self._canon_chunk_count: int = 0
        self._ingest_duration_s: float = 0.0

    # ------------------------------------------------------------------
    # Canon ingestion
    # ------------------------------------------------------------------

    def ingest_canon(
        self,
        loader: Optional["CanonLoader"] = None,
        ref: str = "feat/obs-rag",
        force: bool = False,
    ) -> dict:
        """
        Load all Canon documents and index them.

        Parameters
        ----------
        loader : CanonLoader, optional
            Supply an existing loader (useful for testing with a mock).
            If None, a new CanonLoader is created.
        ref : str
            Git ref to load Canon from.  Defaults to feat/obs-rag.
        force : bool
            Re-ingest even if already loaded.

        Returns
        -------
        dict
            Ingestion report: doc_count, chunk_count, duration_s, status.
        """
        if self.canon_loaded and not force:
            return self._ingest_report("already_loaded")

        if not _CANON_LOADER_AVAILABLE:
            logger.error("pipeline.ingest_canon: canon_loader module not available")
            return self._ingest_report("error_no_loader")

        try:
            if loader is None:
                loader = CanonLoader(ref=ref)

            t0 = time.monotonic()
            chunks: List[CanonChunk] = loader.load_all(force=force)

            if not chunks:
                logger.warning("pipeline.ingest_canon: loader returned 0 chunks")
                return self._ingest_report("error_empty_corpus")

            # Convert CanonChunks → generic Chunks the index understands
            generic_chunks = [
                Chunk(
                    text=c.text,
                    metadata={
                        "canon_id": c.canon_id,
                        "source": c.source,
                        "chunk_index": c.chunk_index,
                        "uid": c.uid,
                        **c.metadata,
                    },
                )
                for c in chunks
            ]

            self._index.add(generic_chunks, embedder=self._embedder)

            elapsed = time.monotonic() - t0
            self._canon_chunk_count = len(chunks)
            self._canon_doc_count = len(loader.sources())
            self._ingest_duration_s = elapsed
            self.canon_loaded = True

            logger.info(
                "pipeline.ingest_canon: indexed %d chunks from %d Canon docs in %.2fs",
                self._canon_chunk_count,
                self._canon_doc_count,
                elapsed,
            )
            return self._ingest_report("ok")

        except Exception as exc:  # noqa: BLE001
            logger.exception("pipeline.ingest_canon: unexpected error — %s", exc)
            return self._ingest_report("error_exception")

    def _ingest_report(self, status: str) -> dict:
        return {
            "status": status,
            "canon_loaded": self.canon_loaded,
            "doc_count": self._canon_doc_count,
            "chunk_count": self._canon_chunk_count,
            "duration_s": round(self._ingest_duration_s, 3),
        }

    # ------------------------------------------------------------------
    # Standard ingest (non-Canon documents)
    # ------------------------------------------------------------------

    def ingest(self, text: str, metadata: Optional[dict] = None) -> int:
        """
        Chunk, embed, and index an arbitrary document.

        Returns the number of chunks added.
        """
        try:
            chunks = self._chunker.split(text, metadata=metadata or {})
            if not chunks:
                return 0
            self._index.add(chunks, embedder=self._embedder)
            return len(chunks)
        except Exception as exc:  # noqa: BLE001
            logger.exception("pipeline.ingest: error — %s", exc)
            return 0

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(self, query: str, top_k: Optional[int] = None) -> str:
        """
        Return the top-K most relevant Canon passages for *query*.

        Each passage is prefixed with its [Canon: <canon_id>] citation
        header so the planner always knows provenance.

        Returns an empty string if the index is empty or query is blank.
        """
        if not query or not query.strip():
            logger.debug("pipeline.retrieve: empty query, returning empty context")
            return ""

        try:
            results = self._retriever.retrieve(
                query=query,
                top_k=top_k or self._top_k,
            )
            if not results:
                return ""

            blocks = []
            for r in results:
                canon_id = r.metadata.get("canon_id", "Unknown")
                header = f"[Canon: {canon_id}]"
                blocks.append(f"{header}\n{r.text}")

            return "\n\n---\n\n".join(blocks)

        except Exception as exc:  # noqa: BLE001
            logger.exception("pipeline.retrieve: error — %s", exc)
            return ""

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def status(self) -> dict:
        return {
            "canon_loaded": self.canon_loaded,
            "canon_doc_count": self._canon_doc_count,
            "canon_chunk_count": self._canon_chunk_count,
            "index_size": self._index.size(),
            "top_k": self._top_k,
        }

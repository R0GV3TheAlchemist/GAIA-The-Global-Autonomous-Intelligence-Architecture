"""
core/rag/retriever.py
~~~~~~~~~~~~~~~~~~~~~
Hybrid retriever for the GAIA-OS RAG pipeline.

Provides dense (cosine similarity via VectorIndex.search) and sparse
(BM25-style keyword via VectorIndex.keyword_search) retrieval, with
reciprocal-rank fusion for the default hybrid mode.

Public surface
--------------
RetrievalResult  — dataclass wrapping a Chunk + score + retrieval_type.
Retriever        — hybrid retrieval over a VectorIndex.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal

from .chunker import Chunk
from .index import VectorIndex


# ---------------------------------------------------------------------------
# RetrievalResult
# ---------------------------------------------------------------------------

@dataclass
class RetrievalResult:
    """
    A single retrieval hit.

    Attributes
    ----------
    chunk          : The matched Chunk.
    score          : Relevance score in [0, 1].
    retrieval_type : "dense", "sparse", or "hybrid".
    """
    chunk:          Chunk
    score:          float
    retrieval_type: str = "hybrid"

    def provenance(self) -> dict:
        """Merge chunk provenance with retrieval metadata."""
        return {
            **self.chunk.provenance(),
            "score":          self.score,
            "retrieval_type": self.retrieval_type,
        }


# ---------------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------------

class Retriever:
    """
    Hybrid retriever.

    Parameters
    ----------
    index       : VectorIndex to retrieve from.
    rrf_k       : Reciprocal rank fusion constant (default 60).
    """

    def __init__(self, index: VectorIndex, rrf_k: int = 60) -> None:
        self._index = index
        self._rrf_k = rrf_k

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        mode: Literal["hybrid", "dense", "sparse"] = "hybrid",
    ) -> List[RetrievalResult]:
        """
        Retrieve the *top_k* most relevant chunks for *query*.

        Parameters
        ----------
        query  : Natural-language query string.
        top_k  : Maximum number of results.
        mode   : Retrieval strategy.

        Returns
        -------
        List[RetrievalResult]  Sorted by descending score; may be empty.
        """
        if self._index.count() == 0:
            return []

        if mode == "dense":
            return self._dense(query, top_k)
        if mode == "sparse":
            return self._sparse(query, top_k)
        return self._hybrid(query, top_k)

    # ------------------------------------------------------------------
    # Internal strategies
    # ------------------------------------------------------------------

    def _dense(self, query: str, top_k: int) -> List[RetrievalResult]:
        hits = self._index.search(query, top_k=top_k)
        return [
            RetrievalResult(chunk=chunk, score=float(score), retrieval_type="dense")
            for chunk, score in hits
        ]

    def _sparse(self, query: str, top_k: int) -> List[RetrievalResult]:
        hits = self._index.keyword_search(query, top_k=top_k)
        return [
            RetrievalResult(chunk=chunk, score=float(score), retrieval_type="sparse")
            for chunk, score in hits
        ]

    def _hybrid(
        self, query: str, top_k: int
    ) -> List[RetrievalResult]:
        """
        Reciprocal rank fusion of dense + sparse results.
        """
        dense_hits  = self._index.search(query, top_k=top_k * 2)
        sparse_hits = self._index.keyword_search(query, top_k=top_k * 2)

        rrf: dict[str, float] = {}

        for rank, (chunk, _) in enumerate(dense_hits):
            rrf[chunk.chunk_id] = rrf.get(chunk.chunk_id, 0.0) + 1.0 / (self._rrf_k + rank + 1)

        for rank, (chunk, _) in enumerate(sparse_hits):
            rrf[chunk.chunk_id] = rrf.get(chunk.chunk_id, 0.0) + 1.0 / (self._rrf_k + rank + 1)

        # Build a lookup from chunk_id -> chunk object
        all_chunks: dict[str, Chunk] = {}
        for chunk, _ in dense_hits + sparse_hits:
            all_chunks[chunk.chunk_id] = chunk

        ranked = sorted(rrf.items(), key=lambda x: x[1], reverse=True)[:top_k]

        return [
            RetrievalResult(
                chunk=all_chunks[cid],
                score=round(score, 6),
                retrieval_type="hybrid",
            )
            for cid, score in ranked
            if cid in all_chunks
        ]

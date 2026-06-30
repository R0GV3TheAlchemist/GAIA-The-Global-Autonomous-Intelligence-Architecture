from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from core.memory.connectivity_graph import ConnectivityGraph


@dataclass(slots=True)
class RelevanceBreakdown:
    memory_id: str
    semantic_score: float
    connectivity_weight: float
    freshness_weight: float
    final_score: float


class RelevanceScorer:
    """Scores memory candidates using relevance-first retrieval.

    The semantic score remains primary. Structural connectivity and freshness are
    treated as multiplicative adjustments so highly-related memories are boosted
    without overpowering direct semantic relevance.
    """

    def __init__(
        self,
        graph: ConnectivityGraph | None = None,
        connectivity_scale: float = 0.15,
        freshness_scale: float = 0.05,
    ) -> None:
        self.graph = graph or ConnectivityGraph()
        self.connectivity_scale = max(0.0, connectivity_scale)
        self.freshness_scale = max(0.0, freshness_scale)

    def score_candidate(
        self,
        memory_id: str,
        semantic_score: float,
        metadata: Mapping[str, Any] | None = None,
    ) -> RelevanceBreakdown:
        safe_semantic = max(0.0, float(semantic_score))
        connectivity_raw = self.graph.weight(memory_id)
        connectivity_weight = 1.0 + ((connectivity_raw - 1.0) * self.connectivity_scale)

        freshness_weight = 1.0
        if metadata:
            retrievals = float(metadata.get("retrieval_count", 0) or 0)
            freshness_weight += min(0.5, retrievals * self.freshness_scale)
            if metadata.get("pinned"):
                freshness_weight += 0.15

        final_score = safe_semantic * connectivity_weight * freshness_weight
        return RelevanceBreakdown(
            memory_id=memory_id,
            semantic_score=safe_semantic,
            connectivity_weight=connectivity_weight,
            freshness_weight=freshness_weight,
            final_score=final_score,
        )

    def rank(
        self,
        candidates: Sequence[tuple[str, float, Mapping[str, Any] | None]],
    ) -> list[RelevanceBreakdown]:
        scored = [
            self.score_candidate(memory_id=memory_id, semantic_score=semantic_score, metadata=metadata)
            for memory_id, semantic_score, metadata in candidates
        ]
        return sorted(scored, key=lambda item: item.final_score, reverse=True)

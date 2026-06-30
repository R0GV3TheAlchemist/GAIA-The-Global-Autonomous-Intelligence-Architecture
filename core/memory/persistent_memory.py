from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence
from uuid import uuid4

from core.memory.connectivity_graph import ConnectivityGraph
from core.memory.relevance_scorer import RelevanceBreakdown, RelevanceScorer


@dataclass(slots=True)
class PersistentMemoryRecord:
    memory_id: str
    text: str
    layer: str = "episodic"
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_ids: List[str] = field(default_factory=list)
    embedding: List[float] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PersistentMemoryModule:
    """Persistent relational memory aligned to the SIM_017 architecture.

    Design goals:
    - Relevance-first retrieval
    - Structural-connectivity weighting
    - Layered relational storage
    - Minimal assumptions about the underlying store

    This class intentionally accepts simple callables/stores so it can be wired
    into the existing GAIA memory subsystem incrementally rather than requiring a
    full rewrite of the current hierarchy stack.
    """

    def __init__(self, scorer: RelevanceScorer | None = None) -> None:
        self.graph = scorer.graph if scorer else ConnectivityGraph()
        self.scorer = scorer or RelevanceScorer(graph=self.graph)
        self._records: MutableMapping[str, PersistentMemoryRecord] = {}

    def ingest(
        self,
        text: str,
        *,
        layer: str = "episodic",
        metadata: Mapping[str, Any] | None = None,
        related_ids: Iterable[str] | None = None,
        embedding: Sequence[float] | None = None,
        memory_id: str | None = None,
    ) -> PersistentMemoryRecord:
        record = PersistentMemoryRecord(
            memory_id=memory_id or self._new_memory_id(layer),
            text=text,
            layer=layer,
            metadata=dict(metadata or {}),
            related_ids=list(related_ids or []),
            embedding=list(embedding or []),
        )
        self._records[record.memory_id] = record
        self.graph.add_memory(record.memory_id)
        self.graph.add_edges(record.memory_id, record.related_ids)
        return record

    def relate(self, source_id: str, target_id: str) -> None:
        if source_id not in self._records or target_id not in self._records:
            return
        if target_id not in self._records[source_id].related_ids:
            self._records[source_id].related_ids.append(target_id)
        self.graph.add_edge(source_id, target_id)

    def retrieve(
        self,
        candidates: Sequence[tuple[str, float]],
        limit: int = 5,
    ) -> List[RelevanceBreakdown]:
        enriched = []
        for memory_id, semantic_score in candidates:
            record = self._records.get(memory_id)
            metadata = record.metadata if record else {}
            enriched.append((memory_id, semantic_score, metadata))
        ranked = self.scorer.rank(enriched)
        for item in ranked[:limit]:
            record = self._records.get(item.memory_id)
            if record is not None:
                record.metadata["retrieval_count"] = int(record.metadata.get("retrieval_count", 0)) + 1
                record.metadata["last_retrieved_at"] = datetime.now(timezone.utc).isoformat()
        return ranked[:limit]

    def get(self, memory_id: str) -> PersistentMemoryRecord | None:
        return self._records.get(memory_id)

    def export_state(self) -> Dict[str, Any]:
        return {
            "records": {
                memory_id: {
                    "text": record.text,
                    "layer": record.layer,
                    "metadata": dict(record.metadata),
                    "related_ids": list(record.related_ids),
                    "embedding": list(record.embedding),
                    "created_at": record.created_at,
                }
                for memory_id, record in self._records.items()
            },
            "connectivity": self.graph.snapshot(),
        }

    @staticmethod
    def _new_memory_id(layer: str) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"mem_{layer}_{stamp}_{uuid4().hex[:8]}"

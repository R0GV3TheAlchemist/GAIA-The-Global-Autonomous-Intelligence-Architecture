"""Tests for the SIM_017 persistent relational memory module.

Covers three core behaviors:
  1. Relational edge formation — ingest + relate builds the connectivity graph
  2. Connectivity-weighted reranking — highly connected memories score higher
  3. Retrieval-count freshness updates — each retrieve() call increments counts
"""
from __future__ import annotations

import pytest

from core.memory.connectivity_graph import ConnectivityGraph
from core.memory.relevance_scorer import RelevanceScorer
from core.memory.persistent_memory import PersistentMemoryModule, PersistentMemoryRecord


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def module() -> PersistentMemoryModule:
    return PersistentMemoryModule()


# ---------------------------------------------------------------------------
# 1. Relational edge formation
# ---------------------------------------------------------------------------

class TestRelationalEdges:
    def test_ingest_registers_node(self, module: PersistentMemoryModule) -> None:
        rec = module.ingest("GAIA memory module designed")
        assert rec.memory_id in module.graph._adjacency

    def test_relate_adds_edge(self, module: PersistentMemoryModule) -> None:
        a = module.ingest("First memory")
        b = module.ingest("Second memory")
        module.relate(a.memory_id, b.memory_id)
        assert b.memory_id in module.graph.neighbors(a.memory_id)

    def test_relate_missing_id_noop(self, module: PersistentMemoryModule) -> None:
        a = module.ingest("Only memory")
        module.relate(a.memory_id, "nonexistent-id")
        assert len(module.graph.neighbors(a.memory_id)) == 0

    def test_ingest_with_related_ids_builds_edges(self, module: PersistentMemoryModule) -> None:
        a = module.ingest("Root memory")
        b = module.ingest("Linked memory", related_ids=[a.memory_id])
        assert a.memory_id in module.graph.neighbors(b.memory_id)

    def test_graph_snapshot_reflects_edges(self, module: PersistentMemoryModule) -> None:
        a = module.ingest("A")
        b = module.ingest("B")
        module.relate(a.memory_id, b.memory_id)
        snap = module.graph.snapshot()
        assert b.memory_id in snap[a.memory_id]["outbound"]
        assert a.memory_id in snap[b.memory_id]["inbound"]


# ---------------------------------------------------------------------------
# 2. Connectivity-weighted reranking
# ---------------------------------------------------------------------------

class TestConnectivityWeighting:
    def test_isolated_node_weight_is_one(self) -> None:
        graph = ConnectivityGraph()
        graph.add_memory("isolated")
        assert graph.weight("isolated") == pytest.approx(1.0)

    def test_connected_node_weight_exceeds_one(self) -> None:
        graph = ConnectivityGraph()
        graph.add_edge("hub", "a")
        graph.add_edge("hub", "b")
        graph.add_edge("hub", "c")
        assert graph.weight("hub") > 1.0

    def test_more_connections_higher_weight(self) -> None:
        graph = ConnectivityGraph()
        graph.add_edge("big", "x1")
        graph.add_edge("big", "x2")
        graph.add_edge("big", "x3")
        graph.add_edge("small", "y1")
        assert graph.weight("big") > graph.weight("small")

    def test_retrieve_reranks_by_connectivity(self, module: PersistentMemoryModule) -> None:
        isolated = module.ingest("Isolated fact")
        hub = module.ingest("Hub memory")
        for _ in range(4):
            related = module.ingest(f"Related to hub {_}")
            module.relate(hub.memory_id, related.memory_id)

        # Give both the same raw semantic score
        candidates = [(isolated.memory_id, 0.80), (hub.memory_id, 0.80)]
        ranked = module.retrieve(candidates, limit=2)
        assert ranked[0].memory_id == hub.memory_id

    def test_scorer_uses_connectivity_scale(self) -> None:
        graph = ConnectivityGraph()
        graph.add_edge("a", "b")
        scorer = RelevanceScorer(graph=graph, connectivity_scale=0.0)
        result = scorer.score_candidate("a", 0.5)
        # With connectivity_scale=0.0 the weight contribution is zero
        assert result.connectivity_weight == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 3. Retrieval-count freshness updates
# ---------------------------------------------------------------------------

class TestFreshnessUpdates:
    def test_retrieval_count_starts_at_zero(self, module: PersistentMemoryModule) -> None:
        rec = module.ingest("Fresh memory")
        assert rec.metadata.get("retrieval_count", 0) == 0

    def test_retrieval_increments_count(self, module: PersistentMemoryModule) -> None:
        rec = module.ingest("Countable memory")
        module.retrieve([(rec.memory_id, 0.9)], limit=1)
        assert rec.metadata["retrieval_count"] == 1

    def test_multiple_retrievals_accumulate(self, module: PersistentMemoryModule) -> None:
        rec = module.ingest("Frequently retrieved")
        for _ in range(5):
            module.retrieve([(rec.memory_id, 0.9)], limit=1)
        assert rec.metadata["retrieval_count"] == 5

    def test_last_retrieved_at_set(self, module: PersistentMemoryModule) -> None:
        rec = module.ingest("Timestamped memory")
        module.retrieve([(rec.memory_id, 0.9)], limit=1)
        assert "last_retrieved_at" in rec.metadata

    def test_pinned_memory_scores_higher(self, module: PersistentMemoryModule) -> None:
        pinned = module.ingest("Pinned", metadata={"pinned": True})
        normal = module.ingest("Normal")
        candidates = [(pinned.memory_id, 0.75), (normal.memory_id, 0.75)]
        ranked = module.retrieve(candidates, limit=2)
        assert ranked[0].memory_id == pinned.memory_id

    def test_retrieve_respects_limit(self, module: PersistentMemoryModule) -> None:
        records = [module.ingest(f"Memory {i}") for i in range(10)]
        candidates = [(r.memory_id, 0.9 - i * 0.01) for i, r in enumerate(records)]
        ranked = module.retrieve(candidates, limit=3)
        assert len(ranked) == 3


# ---------------------------------------------------------------------------
# 4. Export state
# ---------------------------------------------------------------------------

class TestExportState:
    def test_export_contains_records(self, module: PersistentMemoryModule) -> None:
        module.ingest("Export test")
        state = module.export_state()
        assert len(state["records"]) == 1

    def test_export_contains_connectivity(self, module: PersistentMemoryModule) -> None:
        a = module.ingest("A")
        b = module.ingest("B")
        module.relate(a.memory_id, b.memory_id)
        state = module.export_state()
        assert a.memory_id in state["connectivity"]

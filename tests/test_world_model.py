"""
Tests for GAIA World Model
State manager, query interface, snapshot.
"""

import pytest
from gaia.epistemics.claim import Claim
from gaia.world_model.state import WorldModelState
from gaia.core import GAIACore


def test_world_model_update_and_query():
    wm = WorldModelState()
    claim = Claim.create(
        statement="Biophotonic coherence is measurable",
        source="BIOPHOTON_09",
        source_confidence=0.88,
        entity_refs=["biophoton-coherence"]
    )
    eval_result = {
        "claim": claim,
        "confidence": 0.88,
        "status": "supported",
        "contradictions": [],
        "supporting_claims": [],
        "evaluation_notes": "Test evaluation"
    }
    wm.update(eval_result)
    results = wm.query_best_supported("biophoton-coherence")
    assert len(results) == 1
    assert results[0]["status"] == "supported"


def test_world_model_stats():
    wm = WorldModelState()
    for i in range(3):
        claim = Claim.create(
            statement=f"Test claim {i}",
            source="test",
            source_confidence=0.6,
            entity_refs=[f"entity-{i}"]
        )
        wm.update({
            "claim": claim,
            "confidence": 0.6,
            "status": "supported",
            "contradictions": [],
            "supporting_claims": [],
            "evaluation_notes": ""
        })
    stats = wm.stats()
    assert stats["total_claims"] == 3


def test_gaia_core_full_cycle():
    gaia = GAIACore()
    claim = Claim.create(
        statement="Crystal+Plant alchemy produces synergistic coherence",
        source="SIM-016",
        source_confidence=0.82,
        entity_refs=["crystal-plant-alchemy"],
        domain="biophotonics"
    )
    result = gaia.ingest(claim)
    assert result["cycle"] == 1
    assert result["confidence"] > 0
    assert result["status"] in (
        "unknown", "speculative", "speculative-grounded",
        "supported", "verified", "disputed"
    )


def test_gaia_core_query():
    gaia = GAIACore()
    claim = Claim.create(
        statement="GAIA is the missing epistemic layer",
        source="GAIA_CONVERGENCE_MANIFESTO_v1",
        source_confidence=0.95,
        entity_refs=["gaia-epistemic-layer"],
        domain="architecture"
    )
    gaia.ingest(claim)
    query_result = gaia.query("gaia-epistemic-layer")
    assert query_result["result_count"] >= 1
    assert query_result["results"][0]["confidence"] > 0

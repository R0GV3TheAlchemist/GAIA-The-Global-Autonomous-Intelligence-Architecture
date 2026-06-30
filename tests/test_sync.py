"""
GAIA Tests — Sync + Node State
Tests node state merge logic and conflict resolution.
Runs without network — pure in-process.
"""

import pytest
from node.state import NodeState


def test_update_and_get():
    state = NodeState(node_id="test-a")
    state.update("claim-1", {
        "statement":  "GAIA is an epistemic OS",
        "confidence": 0.8,
        "status":     "supported"
    })
    data = state.get()
    assert "claim-1" in data
    assert data["claim-1"]["confidence"] == 0.8


def test_merge_higher_confidence_wins():
    state = NodeState(node_id="test-b")
    state.update("claim-1", {
        "statement":  "GAIA is an epistemic OS",
        "confidence": 0.5,
        "status":     "speculative"
    })
    result = state.merge({
        "node_id": "peer-node",
        "state": {
            "claim-1": {
                "statement":  "GAIA is an epistemic OS",
                "confidence": 0.9,
                "status":     "supported"
            }
        }
    })
    assert result["accepted"] == 1
    assert state.get()["claim-1"]["confidence"] == 0.9
    assert state.get()["claim-1"]["status"] == "supported"


def test_merge_lower_confidence_rejected():
    state = NodeState(node_id="test-c")
    state.update("claim-1", {
        "statement":  "Crystal alchemy enables coherence",
        "confidence": 0.85,
        "status":     "supported"
    })
    result = state.merge({
        "node_id": "low-trust-peer",
        "state": {
            "claim-1": {
                "statement":  "Crystal alchemy enables coherence",
                "confidence": 0.40,
                "status":     "speculative"
            }
        }
    })
    assert result["rejected"] == 1
    # Original higher-confidence entry should be preserved
    assert state.get()["claim-1"]["confidence"] == 0.85


def test_merge_new_claim_accepted():
    state = NodeState(node_id="test-d")
    result = state.merge({
        "node_id": "peer",
        "state": {
            "new-claim-99": {
                "statement":  "Distributed cognition is possible",
                "confidence": 0.7,
                "status":     "supported"
            }
        }
    })
    assert result["accepted"] == 1
    assert "new-claim-99" in state.get()

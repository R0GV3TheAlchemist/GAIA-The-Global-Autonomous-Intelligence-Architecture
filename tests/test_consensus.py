"""
GAIA Tests — Network Consensus
Tests consensus resolution and agreement level computation.
Runs without network — pure in-process.
"""

from network.consensus import resolve, agreement_level
from network.conflict import detect


SAMPLE_STATES = {
    "node-A": {
        "trust": 0.90,
        "state": {
            "claim-1": {"statement": "Sky is blue", "confidence": 0.9,  "status": "supported"},
            "claim-2": {"statement": "Water is wet","confidence": 0.85, "status": "verified"}
        }
    },
    "node-B": {
        "trust": 0.85,
        "state": {
            "claim-1": {"statement": "Sky is blue", "confidence": 0.7,  "status": "supported"},
            "claim-3": {"statement": "Fire is hot", "confidence": 0.95, "status": "verified"}
        }
    },
    "node-C": {
        "trust": 0.80,
        "state": {
            "claim-1": {"statement": "Sky is blue", "confidence": 0.6,  "status": "disputed"},
        }
    }
}


def test_consensus_picks_highest_weighted():
    result = resolve(SAMPLE_STATES)
    # claim-1: node-A weight=0.9*0.90=0.81, node-B=0.7*0.85=0.595, node-C=0.6*0.80=0.48
    # node-A should win
    assert "claim-1" in result
    assert result["claim-1"]["consensus_source"] == "node-A"
    assert result["claim-1"]["confidence"] == 0.9


def test_consensus_includes_all_claims():
    result = resolve(SAMPLE_STATES)
    assert "claim-1" in result
    assert "claim-2" in result
    assert "claim-3" in result


def test_agreement_level():
    result = agreement_level(SAMPLE_STATES)
    # claim-1 is shared by all 3 nodes but has mixed statuses
    # claim-2 and claim-3 are single-node (not shared)
    assert result["total_shared"] == 1
    assert result["unanimous"] == 0       # claim-1 has "supported" + "disputed"
    assert result["agreement_pct"] == 0.0


def test_conflict_detection():
    conflicts = detect(SAMPLE_STATES)
    # claim-1: node-A/B=supported, node-C=disputed → conflict
    assert len(conflicts) == 1
    assert conflicts[0]["claim_id"] == "claim-1"
    assert conflicts[0]["conflict_type"] == "inter_node_status_conflict"

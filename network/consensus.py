"""
GAIA Network Consensus Engine
Forms global truth from merged node perspectives.
Strategy: highest (confidence × trust) wins per claim.
"""

from typing import Dict, Any, List


def resolve(node_states: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Given {node_id: state_snapshot}, resolve to single consensus world state.
    Returns {claim_id: winning_entry} with provenance metadata.
    """
    # Step 1: Collect all perspectives per claim
    per_claim: Dict[str, List[Dict]] = {}
    for node_id, snapshot in node_states.items():
        trust = snapshot.get("trust", 1.0)
        for claim_id, entry in snapshot.get("state", {}).items():
            per_claim.setdefault(claim_id, []).append({
                "node_id": node_id,
                "trust":   trust,
                "entry":   entry
            })

    # Step 2: Per claim, pick highest weighted perspective
    consensus: Dict[str, Any] = {}
    for claim_id, perspectives in per_claim.items():
        best = max(
            perspectives,
            key=lambda p: p["entry"].get("confidence", 0) * p.get("trust", 1.0)
        )
        consensus[claim_id] = {
            **best["entry"],
            "consensus_source": best["node_id"],
            "perspective_count": len(perspectives)
        }

    return consensus


def agreement_level(node_states: Dict[str, Dict]) -> Dict[str, Any]:
    """
    What fraction of shared claims have unanimous status across all nodes?
    """
    per_claim: Dict[str, List[str]] = {}
    for snapshot in node_states.values():
        for claim_id, entry in snapshot.get("state", {}).items():
            per_claim.setdefault(claim_id, []).append(
                entry.get("status", "unknown")
            )

    shared    = {k: v for k, v in per_claim.items() if len(v) > 1}
    unanimous = sum(1 for v in shared.values() if len(set(v)) == 1)
    total     = len(shared)

    return {
        "total_shared":   total,
        "unanimous":      unanimous,
        "agreement_pct":  round(unanimous / total, 4) if total > 0 else 1.0
    }

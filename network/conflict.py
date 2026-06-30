"""
GAIA Network Conflict Detector
Finds claims where nodes hold incompatible epistemic statuses.
"""

from typing import Dict, Any, List

POSITIVE = {"supported", "verified"}
NEGATIVE = {"disputed", "contradicted"}


def detect(node_states: Dict[str, Dict]) -> List[Dict[str, Any]]:
    """
    Find all inter-node epistemic conflicts.
    A conflict = same claim, opposite status polarity across nodes.
    """
    per_claim: Dict[str, List[Dict]] = {}
    for node_id, snapshot in node_states.items():
        for claim_id, entry in snapshot.get("state", {}).items():
            per_claim.setdefault(claim_id, []).append({
                "node_id": node_id,
                "entry":   entry
            })

    conflicts = []
    for claim_id, perspectives in per_claim.items():
        if len(perspectives) < 2:
            continue
        statuses = [p["entry"].get("status", "unknown") for p in perspectives]
        has_pos  = bool(set(statuses) & POSITIVE)
        has_neg  = bool(set(statuses) & NEGATIVE)
        if has_pos and has_neg:
            conflicts.append({
                "claim_id":      claim_id,
                "conflict_type": "inter_node_status_conflict",
                "perspectives":  [
                    {
                        "node_id":    p["node_id"],
                        "status":     p["entry"].get("status"),
                        "confidence": p["entry"].get("confidence", 0)
                    }
                    for p in perspectives
                ]
            })
    return conflicts

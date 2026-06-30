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
    for claim_id, perspectives in 
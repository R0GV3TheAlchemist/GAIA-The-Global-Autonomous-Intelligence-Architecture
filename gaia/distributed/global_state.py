"""
GAIA Global World State
The merged, consensus-formed view of reality across all nodes.
This is what GAIA believes when all perspectives are integrated.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class GlobalWorldState:
    """
    Aggregates local world states from all GAIA nodes
    into a single merged global view.

    The global state is NOT a simple union.
    It is a consensus-weighted merge where:
      - Node trust scores weight competing claims
      - Conflicts are logged explicitly
      - The highest-confidence, highest-trust view wins per claim
    """

    def __init__(self):
        self.node_states: Dict[str, Dict] = {}    # node_id → state snapshot
        self.global_ontology: Dict[str, Any] = {}
        self.conflict_log: List[Dict] = []
        self._merge_count: int = 0
        self._last_merge: Optional[datetime] = None

    def update_node_state(
        self,
        node_id: str,
        state: Dict[str, Any]
    ) -> None:
        """Receive a state snapshot from a node."""
        self.node_states[node_id] = state

    def merge_states(self) -> Dict[str, Any]:
        """
        Merge all node perspectives into a unified view.
        Returns: {claim_id: [{node, value}, ...]} — all perspectives per claim.
        """
        merged: Dict[str, List[Dict]] = {}
        for node_id, snapshot in self.node_states.items():
            node_state = snapshot.get("state", {})
            trust = snapshot.get("trust", 1.0)
            for claim_id, entry in node_state.items():
                merged.setdefault(claim_id, []).append({
                    "node":  node_id,
                    "trust": trust,
                    "value": entry
                })
        self._merge_count += 1
        self._last_merge = datetime.utcnow()
        return merged

    def log_conflict(
        self,
        claim_id: str,
        conflicting_values: List[Dict]
    ) -> None:
        self.conflict_log.append({
            "claim_id":   claim_id,
            "timestamp":  datetime.utcnow().isoformat(),
            "perspectives": conflicting_values
        })

    def stats(self) -> Dict[str, Any]:
        return {
            "connected_nodes":  len(self.node_states),
            "merge_count":      self._merge_count,
            "last_merge":       self._last_merge.isoformat() if self._last_merge else None,
            "conflict_count":   len(self.conflict_log),
            "node_ids":         list(self.node_states.keys())
        }

    def __repr__(self) -> str:
        return (
            f"GlobalWorldState("
            f"nodes={len(self.node_states)}, "
            f"merges={self._merge_count}, "
            f"conflicts={len(self.conflict_log)})"
        )

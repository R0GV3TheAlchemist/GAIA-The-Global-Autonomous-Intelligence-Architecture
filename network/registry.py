"""
GAIA Network Node Registry
Tracks all known nodes in the network: their IDs, endpoints, trust scores,
domain specialisations, and last-seen timestamps.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class NodeRegistry:

    def __init__(self):
        self._nodes: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        node_id: str,
        endpoint: str,
        trust: float = 1.0,
        domain: Optional[str] = None
    ) -> None:
        self._nodes[node_id] = {
            "node_id":   node_id,
            "endpoint":  endpoint,
            "trust":     trust,
            "domain":    domain,
            "registered_at": datetime.utcnow().isoformat(),
            "last_seen":     datetime.utcnow().isoformat()
        }

    def update_seen(self, node_id: str) -> None:
        if node_id in self._nodes:
            self._nodes[node_id]["last_seen"] = datetime.utcnow().isoformat()

    def get(self, node_id: str) -> Optional[Dict]:
        return self._nodes.get(node_id)

    def all_nodes(self) -> List[Dict]:
        return list(self._nodes.values())

    def endpoints(self) -> List[str]:
        return [n["endpoint"] for n in self._nodes.values()]

    def __repr__(self) -> str:
        return f"NodeRegistry(nodes={len(self._nodes)})"

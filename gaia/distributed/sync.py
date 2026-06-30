"""
GAIA Sync Layer
Node-to-node state synchronisation protocol.

v0.4: HTTP-based sync (requests library)
v0.5: WebSocket real-time sync
v0.6: P2P gossip protocol

Six-step sync protocol:
  1. Compute local state
  2. Broadcast to peers
  3. Collect peer states
  4. Merge
  5. Resolve conflicts
  6. Update local world model
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class SyncLayer:
    """
    Manages peer-to-peer state synchronisation for a GAIA node.

    In v0.4, sync can operate in two modes:
      - LIVE: actual HTTP requests to peer endpoints
      - SIMULATION: in-process dict-passing for testing/development

    Start with SIMULATION mode — no network required to develop and test.
    Switch to LIVE mode when deploying multi-process nodes.
    """

    def __init__(
        self,
        node_id: str,
        peers: List[str],
        mode: str = "simulation"   # "simulation" | "live"
    ):
        self.node_id = node_id
        self.peers   = peers
        self.mode    = mode
        self._peer_state_cache: Dict[str, Any] = {}  # simulated peer states
        self._broadcast_log: List[Dict] = []
        self._sync_errors: List[str] = []

    # ——— Simulation mode (develop without network) ———

    def register_simulated_peer(
        self,
        peer_id: str,
        peer_state: Dict[str, Any]
    ) -> None:
        """Register a simulated peer state for in-process testing."""
        self._peer_state_cache[peer_id] = peer_state

    def collect_simulated(self) -> Dict[str, Any]:
        """Return all simulated peer states."""
        return dict(self._peer_state_cache)

    # ——— Live mode (real HTTP) ———

    def broadcast(
        self,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Broadcast this node's current state to all peers.
        Returns {peer: "ok" | "error"} for each peer.
        """
        if self.mode == "simulation":
            # In simulation mode, just log the broadcast
            self._broadcast_log.append({
                "timestamp":  datetime.utcnow().isoformat(),
                "node_id":    self.node_id,
                "peers":      self.peers,
                "claim_count": len(state.get("state", {}))
            })
            return {peer: "simulated" for peer in self.peers}

        # Live HTTP mode
        results = {}
        for peer in self.peers:
            try:
                import requests
                r = requests.post(
                    f"{peer}/sync",
                    json={"node": self.node_id, "state": state},
                    timeout=5
                )
                results[peer] = "ok" if r.status_code == 200 else f"error_{r.status_code}"
            except Exception as e:
                results[peer] = f"error: {str(e)[:40]}"
                self._sync_errors.append(f"{peer}: {str(e)[:40]}")
        return results

    def collect(
        self,
        external_states: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Collect state snapshots from all peers.
        In simulation mode: returns registered peer states.
        In live mode: HTTP GET to each peer /state endpoint.
        """
        if self.mode == "simulation":
            if external_states:
                self._peer_state_cache.update(external_states)
            return self.collect_simulated()

        # Live HTTP mode
        collected = {}
        for peer in self.peers:
            try:
                import requests
                r = requests.get(f"{peer}/state", timeout=5)
                if r.status_code == 200:
                    collected[peer] = r.json()
            except Exception as e:
                self._sync_errors.append(f"{peer}: {str(e)[:40]}")
        return collected

    def stats(self) -> Dict[str, Any]:
        return {
            "node_id":         self.node_id,
            "mode":            self.mode,
            "peers":           len(self.peers),
            "broadcast_count": len(self._broadcast_log),
            "sync_errors":     len(self._sync_errors),
            "simulated_peers": len(self._peer_state_cache)
        }

    def __repr__(self) -> str:
        return (
            f"SyncLayer(node={self.node_id}, "
            f"peers={len(self.peers)}, "
            f"mode={self.mode})"
        )

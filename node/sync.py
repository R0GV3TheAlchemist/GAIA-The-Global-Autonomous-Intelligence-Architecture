"""
GAIA Sync Layer — Node Communication
Broadcasts local state to peer nodes and fetches peer states.
Peer list loaded from PEERS environment variable (comma-separated URLs).

v0.5: HTTP sync
v0.6: WebSocket real-time
v0.7: P2P gossip protocol
"""

import os
from typing import Dict, Any

PEERS = [p.strip() for p in os.getenv("PEERS", "").split(",") if p.strip()]
NODE_ID = os.getenv("NODE_ID", "local")
SYNC_TIMEOUT = int(os.getenv("SYNC_TIMEOUT", "5"))


def broadcast(state_snapshot: Dict[str, Any]) -> Dict[str, str]:
    """
    Push this node's state snapshot to all peers.
    Returns {peer_url: result} for each peer.
    Non-blocking — failures are logged, not raised.
    """
    results = {}
    if not PEERS:
        return {"status": "no_peers_configured"}

    try:
        import requests
    except ImportError:
        return {"status": "requests_not_installed"}

    for peer in PEERS:
        try:
            r = requests.post(
                f"{peer}/sync",
                json=state_snapshot,
                timeout=SYNC_TIMEOUT
            )
            results[peer] = "ok" if r.status_code == 200 else f"http_{r.status_code}"
        except Exception as e:
            results[peer] = f"error: {str(e)[:60]}"

    return results


def fetch_peers() -> Dict[str, Any]:
    """
    Fetch state snapshots from all peer nodes.
    Returns {peer_url: state_snapshot} for reachable peers.
    """
    states = {}
    if not PEERS:
        return states

    try:
        import requests
    except ImportError:
        return states

    for peer in PEERS:
        try:
            r = requests.get(f"{peer}/state", timeout=SYNC_TIMEOUT)
            if r.status_code == 200:
                states[peer] = r.json()
        except Exception:
            continue

    return states

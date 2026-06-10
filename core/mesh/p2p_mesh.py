"""
core/mesh/p2p_mesh.py
=====================
P2P Mesh layer for MotherThread coordination.

Provides peer discovery, heartbeat management, and gossip-protocol
message fanout across a fully decentralised mesh of GAIA-OS nodes.

Canon Ref:
  C04  — Gaian Identity & Relational Selfhood (privacy-first peering)
  C43  — STEM Foundation Doctrine (epistemic integrity)
  C47  — Sovereign Matrix Code (self-sovereign node identity)

Design principles
-----------------
* Each node is identified by a UUID (node_id) — never a user slug.
* Peer records hold only transport-layer metadata (address, port, last_seen).
* Gossip fanout is bounded by FANOUT_DEGREE to limit bandwidth.
* Heartbeat expiry removes stale peers automatically.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HEARTBEAT_INTERVAL: float = 15.0        # seconds between outbound heartbeats
HEARTBEAT_TTL: float = 45.0             # seconds before a peer is considered stale
FANOUT_DEGREE: int = 6                   # max peers to forward a gossip message to
GOSSIP_TTL_HOPS: int = 5                 # max hop count for gossip propagation
MAX_SEEN_CACHE: int = 1_000             # dedup cache size for gossip message IDs


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PeerRecord:
    """Transport-layer metadata for a single mesh peer."""
    node_id: str
    address: str
    port: int
    last_seen: float = field(default_factory=time.time)
    hops_away: int = 0
    region: Optional[str] = None

    @property
    def is_alive(self) -> bool:
        return (time.time() - self.last_seen) < HEARTBEAT_TTL

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "last_seen": self.last_seen,
            "hops_away": self.hops_away,
            "region": self.region,
            "alive": self.is_alive,
        }


@dataclass
class GossipEnvelope:
    """A gossip message travelling the P2P mesh."""
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    origin_node: str = ""
    topic: str = "general"
    payload: dict = field(default_factory=dict)
    hops_remaining: int = GOSSIP_TTL_HOPS
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "msg_id": self.msg_id,
            "origin_node": self.origin_node,
            "topic": self.topic,
            "payload": self.payload,
            "hops_remaining": self.hops_remaining,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GossipEnvelope":
        return cls(
            msg_id=d.get("msg_id", str(uuid.uuid4())),
            origin_node=d.get("origin_node", ""),
            topic=d.get("topic", "general"),
            payload=d.get("payload", {}),
            hops_remaining=d.get("hops_remaining", GOSSIP_TTL_HOPS),
            timestamp=d.get("timestamp", time.time()),
        )


MessageHandler = Callable[[GossipEnvelope], None]


# ---------------------------------------------------------------------------
# P2PMesh
# ---------------------------------------------------------------------------

class P2PMesh:
    """
    Decentralised P2P mesh for GAIA-OS MotherThread coordination.

    Lifecycle
    ---------
    mesh = P2PMesh(node_id="...", address="0.0.0.0", port=7700)
    await mesh.start()
    mesh.add_peer(PeerRecord(...))
    mesh.gossip("mother_pulse", {"phi": 0.82})
    await mesh.stop()

    Canon: C04, C43, C47
    """

    def __init__(
        self,
        node_id: Optional[str] = None,
        address: str = "0.0.0.0",
        port: int = 7700,
        region: Optional[str] = None,
    ) -> None:
        self.node_id: str = node_id or str(uuid.uuid4())
        self.address = address
        self.port = port
        self.region = region

        self._peers: Dict[str, PeerRecord] = {}
        self._seen_msgs: Set[str] = set()
        self._seen_order: List[str] = []
        self._handlers: Dict[str, List[MessageHandler]] = {}
        self._running: bool = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._eviction_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start heartbeat and eviction loops."""
        if self._running:
            return
        self._running = True
        self._heartbeat_task = asyncio.ensure_future(self._heartbeat_loop())
        self._eviction_task = asyncio.ensure_future(self._eviction_loop())
        logger.info("[P2PMesh] Node %s started on %s:%d", self.node_id, self.address, self.port)

    async def stop(self) -> None:
        """Stop all background tasks cleanly."""
        self._running = False
        for task in (self._heartbeat_task, self._eviction_task):
            if task is not None:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        logger.info("[P2PMesh] Node %s stopped.", self.node_id)

    # ------------------------------------------------------------------
    # Peer management
    # ------------------------------------------------------------------

    def add_peer(self, peer: PeerRecord) -> None:
        """Register or refresh a peer record."""
        if peer.node_id == self.node_id:
            return  # never add self
        self._peers[peer.node_id] = peer
        logger.debug("[P2PMesh] Peer added: %s @ %s:%d", peer.node_id, peer.address, peer.port)

    def remove_peer(self, node_id: str) -> None:
        self._peers.pop(node_id, None)

    def alive_peers(self) -> List[PeerRecord]:
        return [p for p in self._peers.values() if p.is_alive]

    def peer_count(self) -> int:
        return len(self.alive_peers())

    # ------------------------------------------------------------------
    # Gossip
    # ------------------------------------------------------------------

    def subscribe(self, topic: str, handler: MessageHandler) -> None:
        """Subscribe a handler to a gossip topic."""
        self._handlers.setdefault(topic, []).append(handler)

    def unsubscribe(self, topic: str, handler: MessageHandler) -> None:
        handlers = self._handlers.get(topic, [])
        try:
            handlers.remove(handler)
        except ValueError:
            pass

    def gossip(self, topic: str, payload: dict, hops: int = GOSSIP_TTL_HOPS) -> GossipEnvelope:
        """
        Originate a gossip message on this node and trigger local dispatch.
        Returns the envelope (useful for testing / tracing).
        """
        env = GossipEnvelope(
            origin_node=self.node_id,
            topic=topic,
            payload=payload,
            hops_remaining=hops,
        )
        self._receive(env)
        return env

    def receive_envelope(self, env_dict: dict) -> None:
        """Called when a serialised GossipEnvelope arrives from the network layer."""
        env = GossipEnvelope.from_dict(env_dict)
        self._receive(env)

    def _receive(self, env: GossipEnvelope) -> None:
        """Process an inbound gossip envelope: dedup → dispatch → forward."""
        if env.msg_id in self._seen_msgs:
            return

        # Dedup cache management
        self._seen_msgs.add(env.msg_id)
        self._seen_order.append(env.msg_id)
        if len(self._seen_order) > MAX_SEEN_CACHE:
            oldest = self._seen_order.pop(0)
            self._seen_msgs.discard(oldest)

        # Dispatch to local handlers
        for handler in list(self._handlers.get(env.topic, [])):
            try:
                handler(env)
            except Exception as exc:
                logger.warning("[P2PMesh] Handler error on topic %s: %s", env.topic, exc)

        # Forward if hops remain
        if env.hops_remaining > 0:
            forwarded = GossipEnvelope(
                msg_id=env.msg_id,
                origin_node=env.origin_node,
                topic=env.topic,
                payload=env.payload,
                hops_remaining=env.hops_remaining - 1,
                timestamp=env.timestamp,
            )
            self._fanout(forwarded)

    def _fanout(self, env: GossipEnvelope) -> None:
        """
        Forward envelope to up to FANOUT_DEGREE alive peers.
        In production this would invoke the transport layer; here we
        expose the serialised envelope for the caller's transport to send.
        """
        peers = self.alive_peers()
        # Exclude origin to avoid echo
        peers = [p for p in peers if p.node_id != env.origin_node]
        # Bounded fanout
        targets = peers[:FANOUT_DEGREE]
        for peer in targets:
            logger.debug(
                "[P2PMesh] Forwarding %s → %s (hops_left=%d)",
                env.msg_id, peer.node_id, env.hops_remaining,
            )
            # Hook: transport layer calls peer.send(env.to_dict()) here.
            # Emit event for pluggable transport adapters:
            self._on_forward(peer, env)

    def _on_forward(self, peer: PeerRecord, env: GossipEnvelope) -> None:
        """Override in subclasses or attach a transport adapter."""
        pass

    # ------------------------------------------------------------------
    # Background tasks
    # ------------------------------------------------------------------

    async def _heartbeat_loop(self) -> None:
        """Broadcast a heartbeat ping to all alive peers periodically."""
        try:
            while self._running:
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                hb_payload = {
                    "node_id": self.node_id,
                    "address": self.address,
                    "port": self.port,
                    "region": self.region,
                    "timestamp": time.time(),
                    "peer_count": self.peer_count(),
                }
                self.gossip("heartbeat", hb_payload, hops=1)
        except asyncio.CancelledError:
            raise

    async def _eviction_loop(self) -> None:
        """Periodically remove stale peers (last_seen > HEARTBEAT_TTL)."""
        try:
            while self._running:
                await asyncio.sleep(HEARTBEAT_TTL)
                stale = [nid for nid, p in self._peers.items() if not p.is_alive]
                for nid in stale:
                    self._peers.pop(nid, None)
                    logger.info("[P2PMesh] Evicted stale peer: %s", nid)
        except asyncio.CancelledError:
            raise

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        alive = self.alive_peers()
        return {
            "node_id": self.node_id,
            "address": self.address,
            "port": self.port,
            "region": self.region,
            "running": self._running,
            "total_peers": len(self._peers),
            "alive_peers": len(alive),
            "seen_msg_cache_size": len(self._seen_msgs),
            "subscribed_topics": list(self._handlers.keys()),
            "peers": [p.to_dict() for p in alive],
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_mesh_instance: Optional[P2PMesh] = None


def get_p2p_mesh(
    node_id: Optional[str] = None,
    address: str = "0.0.0.0",
    port: int = 7700,
) -> P2PMesh:
    """Return the module-level P2PMesh singleton."""
    global _mesh_instance
    if _mesh_instance is None:
        _mesh_instance = P2PMesh(node_id=node_id, address=address, port=port)
    return _mesh_instance

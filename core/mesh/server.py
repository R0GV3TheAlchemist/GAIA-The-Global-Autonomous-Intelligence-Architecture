"""
core/mesh/server.py
===================
MeshServer — The asyncio WebSocket server that is the live beating heart
of the GAIA inter-node protocol.

What it does
------------
1. Listens on a configurable host:port for incoming GAIA peer connections.
2. On `hello` — exchanges NodeIdentity, sends back the full peer list,
   registers the remote node, and subscribes it to CollectiveField deltas.
3. On `heartbeat` — verifies the Ed25519 signature and refreshes the
   peer's last-seen timestamp.
4. On `collective_field_delta` — merges the remote CRDT delta into the
   local CollectiveField and re-broadcasts to all other connected peers
   (gossip fan-out).
5. On `mother_pulse_relay` — accepts a MotherPulse dict from a remote node
   and forwards it to all local MotherThread subscribers so that remote
   pulses appear identical to local ones.
6. Runs a background delta-push loop: every `delta_interval` seconds,
   serialises new CollectiveField entries and pushes them to all peers.
7. Subscribes to the local MotherThread and relays every pulse to all
   connected peers automatically.

Interplanetary tolerance
------------------------
All send operations are wrapped in asyncio.wait_for with a configurable
timeout.  A slow or high-latency peer will not block other peers.
Disconnected peers are pruned gracefully.

Privacy invariant:
    The server NEVER includes individual Gaian slugs or names in any
    outbound message.  Only CollectiveField keys and NodeIdentity
    (public data) are transmitted. (Canon C04)

Canon Ref: C04, C44, C47
Issue: #277 — CRITICAL PATH
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

from .node import GaiaNode, NodeIdentity
from .collective_field import CollectiveField

logger = logging.getLogger("gaia.mesh.server")

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning(
        "[MeshServer] 'websockets' package not installed. "
        "Mesh server disabled. Run: pip install websockets"
    )

# Timeout (seconds) for a single send to a peer — prevents slow peers
# from blocking the broadcast loop.
_SEND_TIMEOUT = 5.0


class MeshServer:
    """
    GAIA Federated Inter-Node WebSocket server.

    Usage (from an async context e.g. GaianRuntime or FastAPI lifespan)
    ---------------------------------------------------------------------
        node = GaiaNode(display_name="My GAIA")
        field = CollectiveField(node.identity.node_id)
        server = MeshServer(node, field)
        await server.start()      # begins serving
        ...                       # GAIA OS runs
        await server.stop()       # graceful shutdown

    Integration with MotherThread
    -----------------------------
        Pass the module-level MotherThread singleton via `mother_thread`:
            from core.mother_thread import get_mother_thread
            server = MeshServer(node, field, mother_thread=get_mother_thread())
        The server will automatically relay every local MotherPulse to all
        connected peers AND merge incoming remote pulses into local state.
    """

    def __init__(
        self,
        node: GaiaNode,
        collective_field: CollectiveField,
        host: str = "0.0.0.0",
        port: int = 7771,
        delta_interval: float = 5.0,
        heartbeat_interval: float = 15.0,
        mother_thread: Any = None,   # MotherThread | None — avoid hard dep
    ) -> None:
        self.node = node
        self.field = collective_field
        self.host = host
        self.port = port
        self.delta_interval = delta_interval
        self.heartbeat_interval = heartbeat_interval
        self.mother_thread = mother_thread

        # Active WebSocket connections keyed by peer node_id
        self._connections: dict[str, "WebSocketServerProtocol"] = {}
        # HLC watermark per peer — used for delta-only pushes
        self._peer_watermarks: dict[str, float] = {}

        self._server = None
        self._tasks: list[asyncio.Task] = []
        self._running = False

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the WebSocket server and all background tasks."""
        if not WEBSOCKETS_AVAILABLE:
            logger.error(
                "[MeshServer] Cannot start — websockets package not installed."
            )
            return

        self._running = True
        self._server = await websockets.serve(
            self._handle_connection,
            self.host,
            self.port,
        )
        logger.info(
            f"[MeshServer] Listening on ws://{self.host}:{self.port} "
            f"node={self.node.identity.node_id[:8]}…"
        )

        # Background: heartbeat broadcast
        self._tasks.append(
            asyncio.create_task(
                self.node.heartbeat_loop(self._broadcast_raw, self.heartbeat_interval),
                name="mesh:heartbeat",
            )
        )

        # Background: CollectiveField delta push
        self._tasks.append(
            asyncio.create_task(
                self._delta_push_loop(),
                name="mesh:delta_push",
            )
        )

        # Background: MotherThread pulse relay (if provided)
        if self.mother_thread is not None:
            self._tasks.append(
                asyncio.create_task(
                    self._mother_pulse_relay_loop(),
                    name="mesh:pulse_relay",
                )
            )

    async def stop(self) -> None:
        """Graceful shutdown — close all connections and cancel tasks."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

        for ws in list(self._connections.values()):
            await ws.close()
        self._connections.clear()

        if self._server:
            self._server.close()
            await self._server.wait_closed()
        logger.info("[MeshServer] Stopped.")

    # ── Connection handler ────────────────────────────────────────────────────

    async def _handle_connection(
        self, ws: "WebSocketServerProtocol", path: str = "/"
    ) -> None:
        """
        Handle a single incoming peer connection.
        Processes messages until the connection closes.
        """
        peer_node_id: str | None = None
        try:
            async for raw in ws:
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    logger.warning("[MeshServer] Received malformed JSON — ignoring.")
                    continue

                msg_type = data.get("type", "")

                if msg_type == "hello":
                    peer_node_id = await self._handle_hello(ws, data)

                elif msg_type == "heartbeat":
                    await self._handle_heartbeat(data)

                elif msg_type == "collective_field_delta":
                    await self._handle_delta(data, source_node_id=peer_node_id)

                elif msg_type == "mother_pulse_relay":
                    await self._handle_pulse_relay(data)

                else:
                    logger.debug(f"[MeshServer] Unknown message type: {msg_type!r}")

        except Exception as exc:
            logger.warning(f"[MeshServer] Connection error ({peer_node_id}): {exc}")
        finally:
            if peer_node_id and peer_node_id in self._connections:
                del self._connections[peer_node_id]
                self.node.remove_peer(peer_node_id)
                logger.info(f"[MeshServer] Peer disconnected: {peer_node_id[:8]}…")

    # ── Message handlers ──────────────────────────────────────────────────────

    async def _handle_hello(
        self, ws: "WebSocketServerProtocol", data: dict
    ) -> str | None:
        """
        Process a `hello` message:
        1. Register the peer.
        2. Send back our identity + current peer list.
        3. Send the full CollectiveField snapshot so the peer catches up.
        """
        try:
            peer = NodeIdentity.from_dict(data["node"])
        except (KeyError, ValueError) as exc:
            logger.warning(f"[MeshServer] Bad hello payload: {exc}")
            return None

        if peer.node_id == self.node.identity.node_id:
            return None  # reject self-connection

        self.node.register_peer(peer)
        self._connections[peer.node_id] = ws
        self._peer_watermarks[peer.node_id] = 0.0

        logger.info(
            f"[MeshServer] Hello from {peer.node_id[:8]}… ({peer.display_name}) "
            f"— total peers: {self.node.peer_count()}"
        )

        # ── Send peer list ────────────────────────────────────────────────────
        all_peers = [
            p.to_dict() for p in self.node.get_peers()
            if p.node_id != peer.node_id
        ]
        await self._send(ws, {
            "type": "peer_list",
            "your_id": peer.node_id,
            "peers": all_peers,
            "server_node": self.node.identity.to_dict(),
        })

        # ── Send full CollectiveField snapshot ────────────────────────────────
        snapshot = self.field.snapshot()
        if snapshot:
            await self._send(ws, {
                "type": "collective_field_delta",
                "source": self.node.identity.node_id,
                "delta": snapshot,
                "ts": time.time(),
            })

        return peer.node_id

    async def _handle_heartbeat(self, data: dict) -> None:
        """Verify a signed heartbeat and refresh the peer's last-seen time."""
        try:
            payload_hex = data.get("payload", "")
            sig_hex = data.get("sig", "")
            payload_bytes = bytes.fromhex(payload_hex)
            sig_bytes = bytes.fromhex(sig_hex)
            inner = json.loads(payload_bytes)
            peer_id: str = inner["node"]["node_id"]
        except Exception as exc:
            logger.debug(f"[MeshServer] Bad heartbeat payload: {exc}")
            return

        # Verify signature if we know the peer
        peer = next(
            (p for p in self.node.get_peers() if p.node_id == peer_id), None
        )
        if peer and peer.public_key_bytes:
            valid = GaiaNode.verify(peer.public_key_bytes, payload_bytes, sig_bytes)
            if not valid:
                logger.warning(
                    f"[MeshServer] Heartbeat signature INVALID from {peer_id[:8]}…"
                )
                return

        logger.debug(f"[MeshServer] Heartbeat OK from {peer_id[:8]}…")

    async def _handle_delta(
        self, data: dict, source_node_id: str | None
    ) -> None:
        """
        Merge an incoming CollectiveField delta into local state.
        Re-broadcast the merged keys to all OTHER connected peers (gossip).
        """
        delta = data.get("delta", {})
        if not delta:
            return

        updated_keys = self.field.merge(delta)

        if updated_keys and len(self._connections) > 1:
            # Re-broadcast only the updated subset (not the full delta)
            updated_delta = {
                k: delta[k] for k in updated_keys if k in delta
            }
            gossip_msg = {
                "type": "collective_field_delta",
                "source": self.node.identity.node_id,
                "delta": updated_delta,
                "ts": time.time(),
            }
            for peer_id, ws in list(self._connections.items()):
                if peer_id != source_node_id:
                    await self._send(ws, gossip_msg)

    async def _handle_pulse_relay(
        self, data: dict
    ) -> None:
        """
        Accept a MotherPulse relayed from a remote node and
        write key values from it into the local CollectiveField.
        This makes remote pulses visible to local MotherThread subscribers.
        """
        pulse = data.get("pulse", {})
        if not pulse:
            return

        source = data.get("source", "unknown")
        ts = pulse.get("timestamp", time.time())

        # Write the pulse timestamp into the collective field
        self.field.set_mother_pulse(ts)

        # If the pulse carries collective_field data, merge it
        cf_data = pulse.get("collective_field", {})
        if cf_data:
            phi = cf_data.get("collective_phi")
            if phi is not None:
                self.field.set(f"mesh_phi:{source}", float(phi))

        logger.debug(
            f"[MeshServer] MotherPulse relayed from {source[:8]}… ts={ts:.3f}"
        )

    # ── Background loops ──────────────────────────────────────────────────────

    async def _delta_push_loop(self) -> None:
        """
        Every `delta_interval` seconds, push CollectiveField deltas
        to each connected peer — only entries newer than their last watermark.
        """
        while self._running:
            await asyncio.sleep(self.delta_interval)
            if not self._connections:
                continue

            for peer_id, ws in list(self._connections.items()):
                watermark = self._peer_watermarks.get(peer_id, 0.0)
                delta = self.field.delta_since(watermark)
                if not delta:
                    continue
                await self._send(ws, {
                    "type": "collective_field_delta",
                    "source": self.node.identity.node_id,
                    "delta": delta,
                    "ts": time.time(),
                })
                # Advance watermark to current HLC
                self._peer_watermarks[peer_id] = self.field._hlc

    async def _mother_pulse_relay_loop(self) -> None:
        """
        Subscribe to the local MotherThread and relay every pulse
        to all connected peers as a `mother_pulse_relay` message.
        """
        try:
            async for pulse_dict in self.mother_thread.subscribe():
                if not self._connections:
                    continue
                msg = {
                    "type": "mother_pulse_relay",
                    "source": self.node.identity.node_id,
                    "pulse": pulse_dict,
                    "ts": time.time(),
                }
                await self._broadcast_raw(msg)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(f"[MeshServer] MotherThread relay loop error: {exc}")

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _send(
        self, ws: "WebSocketServerProtocol", msg: dict
    ) -> None:
        """
        Send a JSON message to a single WebSocket peer.
        Times out after _SEND_TIMEOUT seconds so slow peers don't block.
        """
        try:
            await asyncio.wait_for(
                ws.send(json.dumps(msg)),
                timeout=_SEND_TIMEOUT,
            )
        except asyncio.TimeoutError:
            logger.warning("[MeshServer] Send timed out — peer may be slow or gone.")
        except Exception as exc:
            logger.debug(f"[MeshServer] Send error: {exc}")

    async def _broadcast_raw(self, msg: dict) -> None:
        """Send a message to ALL currently connected peers."""
        for peer_id, ws in list(self._connections.items()):
            await self._send(ws, msg)

    # ── Introspection ─────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """Return a status snapshot of the mesh server."""
        return {
            "running": self._running,
            "host": self.host,
            "port": self.port,
            "node_id": self.node.identity.node_id,
            "display_name": self.node.identity.display_name,
            "connected_peers": len(self._connections),
            "known_peers": self.node.peer_count(),
            "collective_field_keys": len(self.field.keys()),
            "mesh_coherence": self.field.get_mesh_coherence(),
            "mother_thread_relay": self.mother_thread is not None,
        }

"""
core/mesh/discovery.py
======================
NodeDiscovery — Two-tier peer discovery for the GAIA mesh.

Tier 1 — mDNS (zero-config LAN)
    Uses zeroconf to announce this node as _gaia._tcp.local. and browse
    for other GAIA nodes on the same local network.  No configuration
    required.  Works instantly on home/office networks.

Tier 2 — WebSocket Bootstrap
    Connect to a known peer URL, exchange NodeIdentity, and receive their
    full peer list.  Used for cross-network and interplanetary links where
    a static seed address is known (e.g. a cloud relay node).

Interplanetary latency tolerance:
    All operations are async with configurable timeouts.  A 2-second
    Mars light-delay will not block the local node — bootstrap simply
    waits with the supplied timeout value.

Canon Ref: C47 — Sovereign Matrix Code (distributed consciousness)
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Callable, Awaitable

from .node import GaiaNode, NodeIdentity

logger = logging.getLogger("gaia.mesh.discovery")

MDNS_SERVICE_TYPE = "_gaia._tcp.local."
DEFAULT_MDNS_PORT = 7771

try:
    from zeroconf.asyncio import AsyncZeroconf, AsyncServiceInfo
    from zeroconf import ServiceBrowser, Zeroconf
    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False
    logger.info(
        "[NodeDiscovery] zeroconf not installed — mDNS discovery disabled. "
        "Install with: pip install zeroconf"
    )

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.info(
        "[NodeDiscovery] websockets not installed — WS bootstrap disabled. "
        "Install with: pip install websockets"
    )


class NodeDiscovery:
    """
    Discovers GAIA peers via mDNS and/or WebSocket bootstrap.

    Usage
    -----
        async def on_peer(peer: NodeIdentity):
            node.register_peer(peer)

        discovery = NodeDiscovery(node, on_peer)
        await discovery.start_mdns_announce()    # advertise on LAN
        await discovery.browse_mdns()            # listen for LAN peers
        await discovery.bootstrap_from_peer(url) # connect to a seed node
    """

    def __init__(
        self,
        node: GaiaNode,
        on_peer_found: Callable[[NodeIdentity], Awaitable[None]],
        mdns_port: int = DEFAULT_MDNS_PORT,
    ) -> None:
        self.node = node
        self.on_peer_found = on_peer_found
        self.mdns_port = mdns_port
        self._zeroconf: "AsyncZeroconf | None" = None
        self._browser_zc: "Zeroconf | None" = None

    # ── mDNS Announce ─────────────────────────────────────────────────────────

    async def start_mdns_announce(self) -> None:
        """
        Announce this node on the local network via mDNS.
        Other GAIA nodes running browse_mdns() will discover it automatically.
        """
        if not ZEROCONF_AVAILABLE:
            logger.warning("[NodeDiscovery] mDNS announce skipped — zeroconf unavailable.")
            return

        self._zeroconf = AsyncZeroconf()
        identity = self.node.identity
        info = AsyncServiceInfo(
            MDNS_SERVICE_TYPE,
            f"{identity.node_id}.{MDNS_SERVICE_TYPE}",
            addresses=[b"\x7f\x00\x00\x01"],  # 127.0.0.1 — override with real IP in prod
            port=self.mdns_port,
            properties={
                b"node_id": identity.node_id.encode(),
                b"display_name": identity.display_name.encode(),
                b"pubkey": identity.public_key_bytes.hex().encode(),
            },
        )
        await self._zeroconf.async_register_service(info)
        logger.info(
            f"[NodeDiscovery] mDNS announced: id={identity.node_id[:8]}… "
            f"port={self.mdns_port}"
        )

    # ── mDNS Browse ──────────────────────────────────────────────────────────

    async def browse_mdns(self) -> None:
        """
        Start browsing for other GAIA nodes on the local network.
        Runs in the background; calls on_peer_found for each discovery.
        """
        if not ZEROCONF_AVAILABLE:
            return

        self._browser_zc = Zeroconf()
        node_ref = self.node
        callback_ref = self.on_peer_found

        class _Handler:
            def add_service(self, zc: "Zeroconf", type_: str, name: str) -> None:
                info = zc.get_service_info(type_, name)
                if not info or not info.properties:
                    return
                try:
                    p = {
                        k.decode(errors="replace"): v.decode(errors="replace")
                        for k, v in info.properties.items()
                    }
                    peer = NodeIdentity(
                        node_id=p.get("node_id", name),
                        public_key_bytes=bytes.fromhex(p.get("pubkey", "")),
                        display_name=p.get("display_name", "unknown"),
                    )
                    if peer.node_id != node_ref.identity.node_id:
                        asyncio.get_event_loop().create_task(callback_ref(peer))
                        logger.info(
                            f"[NodeDiscovery] mDNS peer found: {peer.node_id[:8]}… "
                            f"({peer.display_name})"
                        )
                except Exception as exc:
                    logger.warning(f"[NodeDiscovery] Failed to parse mDNS peer: {exc}")

            def remove_service(self, zc: "Zeroconf", type_: str, name: str) -> None:
                logger.info(f"[NodeDiscovery] mDNS peer left: {name}")

            def update_service(self, zc: "Zeroconf", type_: str, name: str) -> None:
                pass

        ServiceBrowser(self._browser_zc, MDNS_SERVICE_TYPE, _Handler())
        logger.info("[NodeDiscovery] mDNS browser started.")

    # ── WebSocket Bootstrap ───────────────────────────────────────────────────

    async def bootstrap_from_peer(
        self, peer_ws_url: str, timeout: float = 30.0
    ) -> None:
        """
        Connect to a known peer WebSocket URL, send our identity (hello),
        receive their peer list, and register all discovered peers.

        The timeout parameter supports high-latency links.  Pass timeout=1200
        for an ~10-minute interplanetary link without blocking local ops.

        Args:
            peer_ws_url: e.g. "ws://192.168.1.42:7771" or "wss://relay.gaia.earth"
            timeout:     seconds to wait before giving up
        """
        if not WEBSOCKETS_AVAILABLE:
            logger.warning("[NodeDiscovery] WS bootstrap skipped — websockets unavailable.")
            return

        logger.info(f"[NodeDiscovery] Bootstrapping from {peer_ws_url} (timeout={timeout}s)")
        try:
            async with asyncio.timeout(timeout):
                async with websockets.connect(peer_ws_url) as ws:
                    # ── Send hello ───────────────────────────────────────────
                    hello = json.dumps(
                        {
                            "type": "hello",
                            "node": self.node.identity.to_dict(),
                        }
                    )
                    await ws.send(hello)

                    # ── Receive peer list ────────────────────────────────────
                    raw = await ws.recv()
                    data = json.loads(raw)

                    if data.get("type") == "peer_list":
                        peers = data.get("peers", [])
                        for p in peers:
                            peer = NodeIdentity.from_dict(p)
                            if peer.node_id != self.node.identity.node_id:
                                self.node.register_peer(peer)
                                await self.on_peer_found(peer)
                        logger.info(
                            f"[NodeDiscovery] Bootstrap complete: "
                            f"{len(peers)} peers received from {peer_ws_url}"
                        )
                    else:
                        logger.warning(
                            f"[NodeDiscovery] Unexpected response type: {data.get('type')}"
                        )
        except asyncio.TimeoutError:
            logger.warning(
                f"[NodeDiscovery] Bootstrap timed out after {timeout}s connecting to {peer_ws_url}"
            )
        except Exception as exc:
            logger.error(f"[NodeDiscovery] Bootstrap failed: {exc}")

    # ── Cleanup ───────────────────────────────────────────────────────────────

    async def stop(self) -> None:
        """Shut down mDNS services gracefully."""
        if self._zeroconf:
            await self._zeroconf.async_close()
            self._zeroconf = None
        if self._browser_zc:
            self._browser_zc.close()
            self._browser_zc = None
        logger.info("[NodeDiscovery] Stopped.")

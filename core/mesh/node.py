"""
core/mesh/node.py
=================
GaiaNode — Persistent identity, Ed25519 keypair, peer registry,
and signed heartbeat for a single GAIA mesh participant.

Each physical machine running GAIA-OS is exactly one node.
The node_id is a stable UUID generated once and stored at
~/.gaia/node_identity.json.  The Ed25519 private key is stored
at ~/.gaia/node_key.pem and signs every outbound mesh message so
peers can verify authenticity without a central authority.

Canon Ref:
    C04  — Gaian Identity & Relational Selfhood
    C47  — Sovereign Matrix Code

Privacy invariant:
    The private key NEVER leaves this file.  Outbound messages carry
    only the public key bytes, node_id, display_name, and signature.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

logger = logging.getLogger("gaia.mesh.node")

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        PublicFormat,
        PrivateFormat,
        NoEncryption,
    )
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning(
        "[GaiaNode] 'cryptography' package not installed. "
        "Message signing disabled. Run: pip install cryptography"
    )


# ---------------------------------------------------------------------------
# NodeIdentity
# ---------------------------------------------------------------------------

@dataclass
class NodeIdentity:
    """
    Serialisable identity record for a GAIA node.
    Shared freely with peers — contains NO private key material.
    """
    node_id: str
    public_key_bytes: bytes
    display_name: str
    gaian_id: str | None = None        # linked Gaian (user), if any
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "public_key": self.public_key_bytes.hex(),
            "display_name": self.display_name,
            "gaian_id": self.gaian_id,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "NodeIdentity":
        return cls(
            node_id=d["node_id"],
            public_key_bytes=bytes.fromhex(d.get("public_key", "")),
            display_name=d.get("display_name", "unknown"),
            gaian_id=d.get("gaian_id"),
            created_at=d.get("created_at", time.time()),
        )


# ---------------------------------------------------------------------------
# GaiaNode
# ---------------------------------------------------------------------------

class GaiaNode:
    """
    Represents this GAIA installation on the mesh.

    Responsibilities
    ----------------
    1. Generate / load a persistent Ed25519 identity.
    2. Sign outbound mesh messages.
    3. Verify inbound messages from known peers.
    4. Maintain a registry of discovered peers.
    5. Run a periodic heartbeat broadcast.
    """

    IDENTITY_PATH: str = os.path.expanduser("~/.gaia/node_identity.json")
    KEY_PATH: str = os.path.expanduser("~/.gaia/node_key.bin")

    def __init__(
        self,
        display_name: str = "GAIA-Node",
        gaian_id: str | None = None,
    ) -> None:
        self._private_key_bytes: bytes | None = None
        self.identity = self._load_or_create(display_name, gaian_id)
        self._peers: dict[str, NodeIdentity] = {}
        logger.info(
            f"[GaiaNode] Node ready: id={self.identity.node_id[:8]}… "
            f"name={self.identity.display_name}"
        )

    # ── Identity persistence ──────────────────────────────────────────────────

    def _load_or_create(
        self, display_name: str, gaian_id: str | None
    ) -> NodeIdentity:
        os.makedirs(os.path.dirname(self.IDENTITY_PATH), exist_ok=True)

        if os.path.exists(self.KEY_PATH) and os.path.exists(self.IDENTITY_PATH):
            with open(self.KEY_PATH, "rb") as f:
                self._private_key_bytes = f.read()
            with open(self.IDENTITY_PATH) as f:
                return NodeIdentity.from_dict(json.load(f))

        # ── Generate fresh keypair ────────────────────────────────────────────
        if CRYPTO_AVAILABLE:
            private_key = Ed25519PrivateKey.generate()
            priv_bytes = private_key.private_bytes(
                Encoding.Raw, PrivateFormat.Raw, NoEncryption()
            )
            pub_bytes = private_key.public_key().public_bytes(
                Encoding.Raw, PublicFormat.Raw
            )
        else:
            # Fallback: use 32-byte random bytes as a mock key
            priv_bytes = os.urandom(32)
            pub_bytes = os.urandom(32)

        self._private_key_bytes = priv_bytes
        identity = NodeIdentity(
            node_id=str(uuid.uuid4()),
            public_key_bytes=pub_bytes,
            display_name=display_name,
            gaian_id=gaian_id,
        )

        with open(self.KEY_PATH, "wb") as f:
            f.write(priv_bytes)
        with open(self.IDENTITY_PATH, "w") as f:
            json.dump(identity.to_dict(), f, indent=2)

        logger.info(
            f"[GaiaNode] Generated new identity: {identity.node_id} "
            f"— saved to {self.IDENTITY_PATH}"
        )
        return identity

    # ── Signing / Verification ────────────────────────────────────────────────

    def sign(self, payload: bytes) -> bytes:
        """
        Sign a raw payload.  Returns 64-byte Ed25519 signature.
        Falls back to 64 zero-bytes if cryptography is unavailable.
        """
        if not CRYPTO_AVAILABLE or self._private_key_bytes is None:
            return b"\x00" * 64
        private_key = Ed25519PrivateKey.from_private_bytes(self._private_key_bytes)
        return private_key.sign(payload)

    @staticmethod
    def verify(
        public_key_bytes: bytes, payload: bytes, signature: bytes
    ) -> bool:
        """Verify an Ed25519 signature.  Returns False on any error."""
        if not CRYPTO_AVAILABLE:
            return True  # trust all when crypto unavailable (dev mode)
        try:
            pub = Ed25519PublicKey.from_public_bytes(public_key_bytes)
            pub.verify(signature, payload)
            return True
        except Exception:
            return False

    # ── Peer registry ─────────────────────────────────────────────────────────

    def register_peer(self, peer: NodeIdentity) -> None:
        """Add or update a peer in the local registry."""
        self._peers[peer.node_id] = peer
        logger.info(
            f"[GaiaNode] Peer registered: {peer.node_id[:8]}… ({peer.display_name})"
        )

    def get_peers(self) -> list[NodeIdentity]:
        """Return all known peers."""
        return list(self._peers.values())

    def remove_peer(self, node_id: str) -> None:
        """Remove a peer (e.g. on disconnect)."""
        self._peers.pop(node_id, None)

    def peer_count(self) -> int:
        return len(self._peers)

    # ── Heartbeat ─────────────────────────────────────────────────────────────

    async def heartbeat_loop(
        self,
        broadcast_fn: Callable[[dict], Awaitable[None]],
        interval: float = 15.0,
    ) -> None:
        """
        Periodically broadcast a signed presence message to all peers.
        Designed to survive interplanetary latency — broadcast_fn is
        fire-and-forget; failures are logged but not fatal.
        """
        while True:
            msg = json.dumps(
                {
                    "type": "heartbeat",
                    "node": self.identity.to_dict(),
                    "ts": time.time(),
                }
            ).encode()
            sig = self.sign(msg)
            try:
                await broadcast_fn(
                    {"payload": msg.hex(), "sig": sig.hex()}
                )
            except Exception as exc:
                logger.warning(f"[GaiaNode] Heartbeat broadcast failed: {exc}")
            await asyncio.sleep(interval)

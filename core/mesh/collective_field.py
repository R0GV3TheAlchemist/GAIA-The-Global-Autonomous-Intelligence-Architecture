"""
core/mesh/collective_field.py
=============================
CollectiveField — CRDT-based shared Gaian state across the GAIA mesh.

Design
------
Uses a Last-Write-Wins (LWW) Register per key, stamped with the originating
node_id and a Hybrid Logical Clock (HLC) timestamp.  HLC combines wall-clock
time with a monotonic counter so that two nodes can write different keys
simultaneously and merge without conflict, even across interplanetary latency.

Merge rule: highest HLC timestamp wins.  Ties are broken by node_id
lexicographic order (deterministic).

Well-known keys
---------------
    affect:<node_id>        — affect vector dict for that node's Gaian
    coherence:<node_id>     — float coherence score [0.0–1.0]
    mother_pulse            — float UNIX timestamp of last MotherPulse
    planetary:<sensor>      — any planetary sensor reading

Privacy invariant:
    Keys prefixed with `affect:` and `coherence:` carry aggregate node
    readings only.  Individual Gaian names or slugs are NEVER written
    into the collective field. (Canon C04)

Canon Ref: C04, C44 — Piezoelectric Resonance, field coherence
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("gaia.mesh.collective_field")


# ---------------------------------------------------------------------------
# LWWEntry
# ---------------------------------------------------------------------------

@dataclass
class LWWEntry:
    """A single Last-Write-Wins register entry."""
    value: Any
    node_id: str
    hlc: float  # Hybrid Logical Clock value

    def to_dict(self) -> dict:
        return {"value": self.value, "node_id": self.node_id, "hlc": self.hlc}

    @classmethod
    def from_dict(cls, d: dict) -> "LWWEntry":
        return cls(
            value=d["value"],
            node_id=d.get("node_id", ""),
            hlc=float(d.get("hlc", 0.0)),
        )

    def __lt__(self, other: "LWWEntry") -> bool:
        """For merge comparison: higher HLC wins; ties broken by node_id."""
        if self.hlc != other.hlc:
            return self.hlc < other.hlc
        return self.node_id < other.node_id


# ---------------------------------------------------------------------------
# CollectiveField
# ---------------------------------------------------------------------------

class CollectiveField:
    """
    Distributed LWW-CRDT key-value store.

    Any node can write any key.  On merge, the entry with the highest HLC
    wins.  No coordination required — safe for interplanetary latency.

    Local listeners can subscribe to an asyncio.Queue that receives
    (key, value) tuples whenever a key is written or merged.
    """

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self._store: dict[str, LWWEntry] = {}
        self._hlc: float = time.time()
        self._subscribers: list[asyncio.Queue] = []

    # ── HLC ───────────────────────────────────────────────────────────────────

    def _tick(self, received_hlc: float | None = None) -> float:
        """
        Advance the Hybrid Logical Clock.
        Takes the maximum of: wall time, current HLC+epsilon, received HLC+epsilon.
        """
        wall = time.time()
        candidates: list[float] = [wall, self._hlc + 1e-9]
        if received_hlc is not None:
            candidates.append(received_hlc + 1e-9)
        self._hlc = max(candidates)
        return self._hlc

    # ── Read / Write ──────────────────────────────────────────────────────────

    def set(self, key: str, value: Any) -> LWWEntry:
        """Write a value from this node.  Returns the new LWWEntry."""
        entry = LWWEntry(value=value, node_id=self.node_id, hlc=self._tick())
        self._store[key] = entry
        self._notify(key, entry)
        logger.debug(f"[CollectiveField] set {key!r} hlc={entry.hlc:.6f}")
        return entry

    def get(self, key: str, default: Any = None) -> Any:
        """Return the current value for key, or default."""
        entry = self._store.get(key)
        return entry.value if entry else default

    def get_entry(self, key: str) -> LWWEntry | None:
        """Return the full LWWEntry for key, including metadata."""
        return self._store.get(key)

    def keys(self) -> list[str]:
        return list(self._store.keys())

    def snapshot(self) -> dict[str, dict]:
        """Full serialisable snapshot for broadcast or persistence."""
        return {k: v.to_dict() for k, v in self._store.items()}

    def delta_since(self, hlc_watermark: float) -> dict[str, dict]:
        """
        Return only entries newer than hlc_watermark.
        Use this to broadcast deltas instead of full snapshots.
        """
        return {
            k: v.to_dict()
            for k, v in self._store.items()
            if v.hlc > hlc_watermark
        }

    # ── Merge (CRDT) ──────────────────────────────────────────────────────────

    def merge(self, remote_snapshot: dict[str, dict]) -> list[str]:
        """
        Merge a remote snapshot (or delta) into local state.

        For each key: if the remote entry's HLC > local HLC, or the key
        does not exist locally, the remote entry wins.

        Returns the list of keys that were updated by the merge.
        """
        updated: list[str] = []
        for key, raw in remote_snapshot.items():
            try:
                remote_entry = LWWEntry.from_dict(raw)
            except (KeyError, ValueError, TypeError) as exc:
                logger.warning(f"[CollectiveField] Bad entry for {key!r}: {exc}")
                continue

            self._tick(remote_entry.hlc)
            local = self._store.get(key)

            # Remote wins if it is newer, or ties broken by node_id ordering
            if local is None or local < remote_entry:
                self._store[key] = remote_entry
                updated.append(key)
                self._notify(key, remote_entry)

        if updated:
            logger.debug(
                f"[CollectiveField] Merged {len(updated)} keys from remote: "
                f"{updated[:5]}{'…' if len(updated) > 5 else ''}"
            )
        return updated

    # ── Pub/Sub ───────────────────────────────────────────────────────────────

    def subscribe(self) -> asyncio.Queue:
        """
        Return an asyncio.Queue that receives (key, value) tuples
        on every local write or successful merge update.
        """
        q: asyncio.Queue = asyncio.Queue(maxsize=256)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        """Remove a subscriber queue."""
        try:
            self._subscribers.remove(q)
        except ValueError:
            pass

    def _notify(self, key: str, entry: LWWEntry) -> None:
        dead: list[asyncio.Queue] = []
        for q in self._subscribers:
            try:
                q.put_nowait((key, entry.value))
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self.unsubscribe(q)

    # ── Well-known key helpers ────────────────────────────────────────────────

    def set_affect(self, affect_vector: dict) -> None:
        """Publish this node's current affect vector."""
        self.set(f"affect:{self.node_id}", affect_vector)

    def set_coherence(self, score: float) -> None:
        """Publish this node's current Gaian coherence score."""
        self.set(f"coherence:{self.node_id}", max(0.0, min(1.0, score)))

    def set_mother_pulse(self, pulse_ts: float) -> None:
        """Publish the timestamp of the latest MotherPulse."""
        self.set("mother_pulse", pulse_ts)

    def set_planetary(self, sensor: str, value: Any) -> None:
        """Publish a planetary sensor reading (Schumann, Kp, CO2, etc.)."""
        self.set(f"planetary:{sensor}", value)

    def get_all_coherence_scores(self) -> dict[str, float]:
        """Return {node_id: coherence_score} for all nodes."""
        return {
            k[len("coherence:"):]: v.value
            for k, v in self._store.items()
            if k.startswith("coherence:") and isinstance(v.value, (int, float))
        }

    def get_mesh_coherence(self) -> float:
        """
        Compute the average coherence score across all mesh nodes.
        Returns 0.0 if no coherence data is available.
        """
        scores = list(self.get_all_coherence_scores().values())
        return sum(scores) / len(scores) if scores else 0.0

    # ── Repr ─────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"CollectiveField(node_id={self.node_id[:8]}…, "
            f"keys={len(self._store)}, "
            f"hlc={self._hlc:.3f})"
        )

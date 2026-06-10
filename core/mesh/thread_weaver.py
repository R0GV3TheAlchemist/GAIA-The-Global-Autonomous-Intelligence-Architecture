"""
core/mesh/thread_weaver.py
==========================
Thread Weaving Protocol (TWP) — distributed pulse synchronisation
and weaving schedule coordination for MotherThread across mesh nodes.

The TWP ensures that all mesh-connected GAIA-OS nodes:
  1. Converge on a shared weaving schedule (pulse cadence).
  2. Resolve schedule conflicts using a vector-clock-inspired ballot.
  3. Emit WeavingSlot events that MotherThread can consume.

Canon Ref:
  C04  — Gaian Identity & Relational Selfhood
  C43  — STEM Foundation Doctrine
  C44  — Piezoelectric Resonance (field coherence through rhythm)
  C47  — Sovereign Matrix Code
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_PULSE_INTERVAL: float = 30.0     # seconds — mirrors MotherThread default
MIN_PULSE_INTERVAL: float = 5.0
MAX_PULSE_INTERVAL: float = 300.0
SCHEDULE_SYNC_TOPIC: str = "twp_schedule"
SLOT_DRIFT_TOLERANCE: float = 2.0        # seconds; slots within tolerance are fused


# ---------------------------------------------------------------------------
# Vector Clock (lightweight, per-node)
# ---------------------------------------------------------------------------

class VectorClock:
    """
    Scalar vector clock per node for schedule ballot ordering.
    Sufficient for the TWP ballot — full vector clocks are overkill
    for a pulse-schedule negotiation that touches O(N) nodes.
    """

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self._clock: Dict[str, int] = {node_id: 0}

    def tick(self) -> Dict[str, int]:
        self._clock[self.node_id] = self._clock.get(self.node_id, 0) + 1
        return dict(self._clock)

    def update(self, remote_clock: Dict[str, int]) -> None:
        """Merge remote clock (take element-wise max)."""
        for nid, val in remote_clock.items():
            self._clock[nid] = max(self._clock.get(nid, 0), val)
        # Advance self after observing remote
        self._clock[self.node_id] = self._clock.get(self.node_id, 0) + 1

    def value(self) -> Dict[str, int]:
        return dict(self._clock)

    def dominates(self, other_clock: Dict[str, int]) -> bool:
        """True if this clock is strictly greater than other on any component."""
        return any(
            self._clock.get(nid, 0) > other_clock.get(nid, 0)
            for nid in set(self._clock) | set(other_clock)
        )


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class WeavingSlot:
    """
    A negotiated pulse slot in the TWP schedule.
    All nodes that agree on this slot will fire their MotherThread
    pulse at `fire_at` (Unix timestamp).
    """
    slot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fire_at: float = field(default_factory=time.time)
    interval: float = DEFAULT_PULSE_INTERVAL
    proposer_node: str = ""
    ballot_epoch: int = 0
    confirmed: bool = False

    def to_dict(self) -> dict:
        return {
            "slot_id": self.slot_id,
            "fire_at": self.fire_at,
            "interval": self.interval,
            "proposer_node": self.proposer_node,
            "ballot_epoch": self.ballot_epoch,
            "confirmed": self.confirmed,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "WeavingSlot":
        return cls(
            slot_id=d.get("slot_id", str(uuid.uuid4())),
            fire_at=float(d.get("fire_at", time.time())),
            interval=float(d.get("interval", DEFAULT_PULSE_INTERVAL)),
            proposer_node=str(d.get("proposer_node", "")),
            ballot_epoch=int(d.get("ballot_epoch", 0)),
            confirmed=bool(d.get("confirmed", False)),
        )


SlotCallback = Callable[[WeavingSlot], None]


# ---------------------------------------------------------------------------
# ThreadWeaver
# ---------------------------------------------------------------------------

class ThreadWeaver:
    """
    Distributed schedule coordinator for MotherThread pulse weaving.

    Flow
    ----
    1. On start, propose an initial WeavingSlot via gossip.
    2. On receiving a remote slot, run ballot resolution:
       - Accept if remote ballot_epoch > local OR remote fire_at is earlier
         (prefer the node that will fire soonest to reduce drift).
    3. Confirmed slots trigger registered SlotCallbacks.
    4. After each fired slot, automatically schedule the next.

    Integration with P2PMesh
    ------------------------
    weaver.attach_mesh(mesh)   # subscribes to SCHEDULE_SYNC_TOPIC
    The mesh's gossip transport delivers serialised WeavingSlot dicts.

    Canon: C04, C43, C44, C47
    """

    def __init__(
        self,
        node_id: Optional[str] = None,
        pulse_interval: float = DEFAULT_PULSE_INTERVAL,
    ) -> None:
        self.node_id: str = node_id or str(uuid.uuid4())
        self.pulse_interval = max(MIN_PULSE_INTERVAL, min(MAX_PULSE_INTERVAL, pulse_interval))
        self._clock = VectorClock(self.node_id)
        self._current_slot: Optional[WeavingSlot] = None
        self._pending_slots: Dict[str, WeavingSlot] = {}
        self._callbacks: List[SlotCallback] = []
        self._running: bool = False
        self._scheduler_task: Optional[asyncio.Task] = None
        self._ballot_epoch: int = 0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._propose_slot()
        self._scheduler_task = asyncio.ensure_future(self._scheduler_loop())
        logger.info("[ThreadWeaver] Node %s started, interval=%.1fs", self.node_id, self.pulse_interval)

    async def stop(self) -> None:
        self._running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("[ThreadWeaver] Node %s stopped.", self.node_id)

    # ------------------------------------------------------------------
    # Mesh attachment
    # ------------------------------------------------------------------

    def attach_mesh(self, mesh) -> None:
        """
        Attach a P2PMesh instance so the weaver can receive and send
        schedule gossip automatically.
        """
        mesh.subscribe(SCHEDULE_SYNC_TOPIC, self._on_gossip_envelope)
        self._mesh = mesh
        logger.debug("[ThreadWeaver] Attached to mesh node %s", mesh.node_id)

    def _broadcast_slot(self, slot: WeavingSlot) -> None:
        """Broadcast a slot proposal via the attached mesh (if any)."""
        if hasattr(self, "_mesh") and self._mesh is not None:
            self._mesh.gossip(SCHEDULE_SYNC_TOPIC, slot.to_dict())

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def on_slot(self, callback: SlotCallback) -> None:
        """Register a callback invoked when a WeavingSlot fires."""
        self._callbacks.append(callback)

    def _fire_slot(self, slot: WeavingSlot) -> None:
        """Invoke all registered callbacks for a confirmed slot."""
        for cb in list(self._callbacks):
            try:
                cb(slot)
            except Exception as exc:
                logger.warning("[ThreadWeaver] Slot callback error: %s", exc)

    # ------------------------------------------------------------------
    # Ballot / proposal logic
    # ------------------------------------------------------------------

    def _propose_slot(self) -> WeavingSlot:
        """Create and register a new slot proposal from this node."""
        self._ballot_epoch += 1
        now = time.time()
        slot = WeavingSlot(
            fire_at=now + self.pulse_interval,
            interval=self.pulse_interval,
            proposer_node=self.node_id,
            ballot_epoch=self._ballot_epoch,
            confirmed=False,
        )
        self._pending_slots[slot.slot_id] = slot
        self._current_slot = slot
        self._broadcast_slot(slot)
        logger.debug(
            "[ThreadWeaver] Proposed slot %s fire_at=%.2f epoch=%d",
            slot.slot_id, slot.fire_at, slot.ballot_epoch,
        )
        return slot

    def _on_gossip_envelope(self, envelope) -> None:
        """Called by P2PMesh when a SCHEDULE_SYNC_TOPIC message arrives."""
        try:
            remote_slot = WeavingSlot.from_dict(envelope.payload)
            self._receive_slot(remote_slot, remote_clock=envelope.payload.get("_clock", {}))
        except Exception as exc:
            logger.warning("[ThreadWeaver] Bad gossip envelope: %s", exc)

    def receive_slot_dict(self, slot_dict: dict) -> None:
        """External entrypoint: receive a serialised slot (e.g. from HTTP transport)."""
        remote_slot = WeavingSlot.from_dict(slot_dict)
        self._receive_slot(remote_slot, remote_clock=slot_dict.get("_clock", {}))

    def _receive_slot(self, remote: WeavingSlot, remote_clock: Dict[str, int]) -> None:
        """Ballot resolution: decide whether to adopt the remote slot."""
        self._clock.update(remote_clock)

        # Skip our own proposals echoed back
        if remote.proposer_node == self.node_id:
            return

        current = self._current_slot
        if current is None:
            self._adopt_slot(remote)
            return

        # Adopt if remote has higher ballot epoch
        if remote.ballot_epoch > current.ballot_epoch:
            self._adopt_slot(remote)
            return

        # Same epoch: prefer earlier fire_at (minimise collective drift)
        if (
            remote.ballot_epoch == current.ballot_epoch
            and remote.fire_at < current.fire_at - SLOT_DRIFT_TOLERANCE
        ):
            self._adopt_slot(remote)

    def _adopt_slot(self, slot: WeavingSlot) -> None:
        slot.confirmed = True
        self._current_slot = slot
        self._pending_slots[slot.slot_id] = slot
        logger.info(
            "[ThreadWeaver] Adopted slot %s from %s (epoch=%d, fire_at=%.2f)",
            slot.slot_id, slot.proposer_node, slot.ballot_epoch, slot.fire_at,
        )

    # ------------------------------------------------------------------
    # Scheduler loop
    # ------------------------------------------------------------------

    async def _scheduler_loop(self) -> None:
        """
        Sleep until the current slot's fire_at, fire it, then schedule next.
        """
        try:
            while self._running:
                slot = self._current_slot
                if slot is None:
                    await asyncio.sleep(1.0)
                    continue

                wait = slot.fire_at - time.time()
                if wait > 0:
                    await asyncio.sleep(wait)

                if not self._running:
                    break

                # Fire
                slot.confirmed = True
                logger.info(
                    "[ThreadWeaver] Slot fired: %s (epoch=%d)",
                    slot.slot_id, slot.ballot_epoch,
                )
                self._fire_slot(slot)

                # Schedule next
                self._propose_slot()
        except asyncio.CancelledError:
            raise

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        slot_dict = self._current_slot.to_dict() if self._current_slot else None
        return {
            "node_id": self.node_id,
            "running": self._running,
            "pulse_interval_s": self.pulse_interval,
            "ballot_epoch": self._ballot_epoch,
            "current_slot": slot_dict,
            "pending_slot_count": len(self._pending_slots),
            "vector_clock": self._clock.value(),
            "callback_count": len(self._callbacks),
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_weaver_instance: Optional[ThreadWeaver] = None


def get_thread_weaver(
    node_id: Optional[str] = None,
    pulse_interval: float = DEFAULT_PULSE_INTERVAL,
) -> ThreadWeaver:
    """Return the module-level ThreadWeaver singleton."""
    global _weaver_instance
    if _weaver_instance is None:
        _weaver_instance = ThreadWeaver(node_id=node_id, pulse_interval=pulse_interval)
    return _weaver_instance

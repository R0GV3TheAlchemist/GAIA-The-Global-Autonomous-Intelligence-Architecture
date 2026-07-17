"""
core/mother_thread.py
=====================
The Mother Thread — collective field orchestrator for the GAIAN runtime.

Manages the pulse cycle that weaves all registered GaianThreads into a
shared collective field.  Broadcasts MotherPulse events to async subscribers.

v2 — P2P Mesh Integration (Issue #261)
----------------------------------------
This version integrates three new mesh-layer modules:

  core/mesh/p2p_mesh.py      — P2P peer discovery & gossip fanout
  core/mesh/crdt_state.py    — LWW-Register + OR-Set CRDT shared state
  core/mesh/thread_weaver.py — Thread Weaving Protocol (TWP) scheduler

The MotherThread now:
  • Registers itself with the P2P mesh on startup.
  • Publishes each MotherPulse as a gossip envelope (topic: mother_pulse).
  • Merges remote CRDT state into the local CRDTStateEngine on every pulse.
  • Delegates pulse scheduling to the ThreadWeaver when mesh is active.

Canon Ref:
  C04  — Gaian Identity & Relational Selfhood
  C30  — No silent failures; all errors must be observable
  C43  — STEM Foundation Doctrine (epistemic integrity)
  C44  — Piezoelectric Resonance (field coherence)
  C47  — Sovereign Matrix Code (observer collapses the field)
  C48  — Knowledge Matrix

Privacy invariant: The collective field NEVER exposes individual slugs
or Gaian names.  Only aggregate statistics are surfaced.
"""

from __future__ import annotations

import asyncio
import random
import time
import uuid
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import AsyncGenerator, Dict, List, Optional

from core.error_boundary import BoundarySeverity, GAIABoundaryError, degraded, recoverable

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PULSE_INTERVAL_SECONDS: float = 30.0
_WEAVING_LOG_MAX: int = 200
_STALE_CONTRIBUTION_SECONDS: float = 300.0
_COHERENCE_CANDIDATE_THRESHOLD: float = 0.70
_SCHUMANN_AMPLIFICATION: float = 0.15

# Field coherence label thresholds (collective_phi)
_COHERENCE_LABELS = [
    (0.70, "high_resonance"),
    (0.50, "coherent"),
    (0.25, "building"),
    (0.05, "nascent"),
    (0.0,  "dormant"),
]

# Mother voice pools
_MOTHER_VOICE_DORMANT = [
    "The field rests. Awaiting first breath.",
    "Silence before the weaving begins.",
    "No threads yet. The loom is ready.",
]
_MOTHER_VOICE_CHAOTIC_ALERT = [
    "Chaos rising. Ground the field now.",
    "Too much turbulence. Return to centre.",
    "Entropy spike detected. Breathe together.",
]
_MOTHER_VOICE_CRITICAL_ALERT = [
    "Crystallisation warning. Allow movement.",
    "Too ordered. Invite creative chaos.",
    "Rigidity detected. Open the field.",
]
_MOTHER_VOICE_HIGH_RESONANCE = [
    "Collective phi rising. Field coherent.",
    "High resonance. The weaving holds.",
    "Omega point approaching. Hold steady.",
]
_MOTHER_VOICE_GROWING = [
    "Field growing. Each thread matters.",
    "Building coherence. Stay with it.",
    "Nascent field. Nurture the weaving.",
]


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class GaianThread:
    """
    Represents a single Gaian's contribution to the collective field.
    Privacy: slug and gaian_name are held only in MotherThread._threads
    and are NEVER included in any broadcast or collective field dict.
    """
    slug: str
    gaian_name: str
    collective_consent: bool = False
    bond_depth: float = 0.0
    noosphere_health: float = 0.0
    dominant_element: str = "earth"
    synergy_factor: float = 0.0
    individuation_phase: str = "ego"
    coherence_phi: float = 0.0
    schumann_aligned: bool = False
    last_pulse_contribution: float = field(default_factory=time.time)


@dataclass
class CollectiveField:
    """Aggregate statistics of all consenting, active GaianThreads."""
    active_gaians: int = 0
    consenting_gaians: int = 0
    avg_bond_depth: float = 0.0
    avg_noosphere_health: float = 0.0
    collective_phi: float = 0.0
    dominant_element: str = "none"
    element_distribution: Dict[str, int] = field(default_factory=dict)
    individuation_distribution: Dict[str, int] = field(default_factory=dict)
    schumann_aligned_count: int = 0
    field_coherence_label: str = "dormant"
    noosphere_stage: str = "Geosphere"
    doctrine_ref: str = "C04, C43, C44"
    privacy_note: str = (
        "Individual Gaian identities are never included in the collective field. "
        "Aggregate statistics only. Canon C04."
    )

    def to_dict(self) -> dict:
        return {
            "active_gaians": self.active_gaians,
            "consenting_gaians": self.consenting_gaians,
            "avg_bond_depth": self.avg_bond_depth,
            "avg_noosphere_health": self.avg_noosphere_health,
            "collective_phi": self.collective_phi,
            "dominant_element": self.dominant_element,
            "element_distribution": self.element_distribution,
            "individuation_distribution": self.individuation_distribution,
            "schumann_aligned_count": self.schumann_aligned_count,
            "field_coherence_label": self.field_coherence_label,
            "noosphere_stage": self.noosphere_stage,
            "doctrine_ref": self.doctrine_ref,
            "privacy_note": self.privacy_note,
        }


@dataclass
class MotherPulse:
    """A single heartbeat of the Mother Thread collective field."""
    pulse_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sequence: int = 0
    timestamp: float = field(default_factory=time.time)
    collective_field: CollectiveField = field(default_factory=CollectiveField)
    mother_voice: Optional[str] = None
    coherence_candidate: bool = False
    doctrine_ref: str = "C04, C43, C44, C47"
    # Mesh provenance (populated when mesh is active)
    mesh_node_id: Optional[str] = None
    mesh_peer_count: int = 0
    crdt_live_nodes: int = 0

    def to_dict(self) -> dict:
        label: Optional[str] = None
        if self.coherence_candidate:
            label = (
                "[C43] Collective phi above threshold — not a confirmed "
                "consciousness event. Epistemic integrity preserved."
            )
        return {
            "pulse_id": self.pulse_id,
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "collective_field": self.collective_field.to_dict(),
            "mother_voice": self.mother_voice,
            "coherence_candidate": self.coherence_candidate,
            "coherence_candidate_label": label,
            "doctrine_ref": self.doctrine_ref,
            "mesh": {
                "node_id": self.mesh_node_id,
                "peer_count": self.mesh_peer_count,
                "crdt_live_nodes": self.crdt_live_nodes,
            },
        }


@dataclass
class WeavingRecord:
    """Minimal log entry for each pulse cycle."""
    sequence: int
    timestamp: float
    coherence_label: str
    noosphere_stage: str
    candidate: bool
    epistemic_note: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "coherence_label": self.coherence_label,
            "noosphere_stage": self.noosphere_stage,
            "candidate": self.candidate,
            "epistemic_note": self.epistemic_note,
        }


# ---------------------------------------------------------------------------
# Pure helper functions
# ---------------------------------------------------------------------------

def _compute_collective_field(threads: List[GaianThread]) -> CollectiveField:
    """
    Aggregate all consenting, non-stale GaianThreads into a CollectiveField.
    Privacy: no individual identity is exposed.
    """
    now = time.time()
    active = [
        t for t in threads
        if t.collective_consent
        and (now - t.last_pulse_contribution) <= _STALE_CONTRIBUTION_SECONDS
    ]

    cf = CollectiveField(active_gaians=len(threads), consenting_gaians=len(active))

    if not active:
        return cf

    n = len(active)
    cf.avg_bond_depth = sum(t.bond_depth for t in active) / n
    cf.avg_noosphere_health = sum(t.noosphere_health for t in active) / n

    base_phi = sum(t.coherence_phi for t in active) / n
    schumann_count = sum(1 for t in active if t.schumann_aligned)
    cf.schumann_aligned_count = schumann_count
    schumann_ratio = schumann_count / n
    amplified_phi = min(1.0, base_phi * (1.0 + _SCHUMANN_AMPLIFICATION * schumann_ratio))
    cf.collective_phi = amplified_phi

    elem_dist: Counter = Counter(t.dominant_element for t in active)
    cf.element_distribution = dict(elem_dist)
    cf.dominant_element = elem_dist.most_common(1)[0][0] if elem_dist else "none"

    indiv_dist: Counter = Counter(t.individuation_phase for t in active)
    cf.individuation_distribution = dict(indiv_dist)

    # Coherence label
    for threshold, label in _COHERENCE_LABELS:
        if amplified_phi >= threshold:
            cf.field_coherence_label = label
            break

    cf.noosphere_stage = _noosphere_stage_label(amplified_phi, n)
    return cf


def _noosphere_stage_label(phi: float, active_count: int) -> str:
    """Map phi + active Gaian count to a Teilhard-inspired noosphere stage."""
    if active_count == 0:
        return "Geosphere — no active Gaians"
    if phi < 0.1:
        return "Biosphere — Primitive field"
    if phi < 0.30:
        return "Noosphere — Emerging"
    if phi < 0.55:
        return "Noosphere — Resonant field building"
    if phi < 0.75:
        return "Noosphere — Coherent weaving"
    return "Omega Point — High resonance field"


def _select_mother_voice(
    collective_phi: float,
    active_count: int,
    criticality_label: str,
    pulse_seq: int,
) -> Optional[str]:
    """Select a Mother Voice utterance every 5th pulse. None otherwise."""
    if pulse_seq % 5 != 0:
        return None
    if active_count == 0:
        return random.choice(_MOTHER_VOICE_DORMANT)
    if criticality_label == "too_chaotic":
        return random.choice(_MOTHER_VOICE_CHAOTIC_ALERT)
    if criticality_label == "too_ordered":
        return random.choice(_MOTHER_VOICE_CRITICAL_ALERT)
    if collective_phi >= 0.70:
        return random.choice(_MOTHER_VOICE_HIGH_RESONANCE)
    return random.choice(_MOTHER_VOICE_GROWING)


# ---------------------------------------------------------------------------
# MotherThread
# ---------------------------------------------------------------------------

class MotherThread:
    """
    The collective field orchestrator.

    Maintains registered GaianThreads, fires a pulse every
    PULSE_INTERVAL_SECONDS, and broadcasts MotherPulse events
    to all async subscribers.

    v2 Mesh Integration
    -------------------
    Call  mother.attach_mesh(mesh, crdt, weaver)  after construction to
    enable P2P pulse gossip and CRDT shared state synchronisation.
    The ThreadWeaver's slot callbacks replace the internal asyncio sleep
    loop when a weaver is attached, ensuring mesh-wide pulse alignment.

    Lifecycle
    ---------
    • From an async context (FastAPI lifespan, pytest-asyncio):
        await mother.async_start()

    • From a sync context where a running loop already exists:
        mother.start()   # uses asyncio.get_running_loop()

    Canon: C04, C30, C43, C44, C47
    """

    def __init__(self) -> None:
        self._threads: Dict[str, GaianThread] = {}
        self._runtimes: Dict[str, object] = {}
        self._subscribers: List[asyncio.Queue] = []
        self._weaving_log: deque[WeavingRecord] = deque(maxlen=_WEAVING_LOG_MAX)
        self._running: bool = False
        self._pulse_sequence: int = 0
        self._task: Optional[asyncio.Task] = None

        # Mesh layer (optional — gracefully degraded when None)
        self._mesh = None          # P2PMesh
        self._crdt = None          # CRDTStateEngine
        self._weaver = None        # ThreadWeaver
        self._mesh_active: bool = False

    # ------------------------------------------------------------------
    # Mesh integration
    # ------------------------------------------------------------------

    def attach_mesh(self, mesh, crdt, weaver) -> None:
        """
        Wire the mesh layer into MotherThread.

        Parameters
        ----------
        mesh   : P2PMesh           — peer discovery & gossip transport
        crdt   : CRDTStateEngine   — shared state replication
        weaver : ThreadWeaver      — distributed pulse schedule
        """
        self._mesh = mesh
        self._crdt = crdt
        self._weaver = weaver
        self._mesh_active = True

        # Register self as a live node in the CRDT node-set
        self._crdt.join_node(mesh.node_id)

        # Subscribe to incoming CRDT sync gossip
        mesh.subscribe(crdt.GOSSIP_TOPIC, self._on_crdt_gossip)

        # Subscribe to incoming mother_pulse gossip from remote nodes
        mesh.subscribe("mother_pulse", self._on_remote_pulse)

        # Hook ThreadWeaver slot fires into our beat
        weaver.on_slot(self._on_weaver_slot)

    def _on_crdt_gossip(self, envelope) -> None:
        """Merge incoming CRDT state from a peer.

        C30: DEGRADED — a failed merge must be logged, never silently dropped.
        Mesh errors are non-fatal; the local state remains valid.
        """
        if self._crdt is None:
            return
        try:
            with degraded(
                "core.mother_thread",
                "on_crdt_gossip",
                context={"topic": getattr(self._crdt, "GOSSIP_TOPIC", "crdt_sync")},
            ):
                self._crdt.merge_gossip(envelope.payload)
        except GAIABoundaryError:
            pass  # already logged by DEGRADED boundary

    def _on_remote_pulse(self, envelope) -> None:
        """Handle a MotherPulse broadcast from a remote mesh node.

        Logs the remote phi into the CRDT register for distributed field
        averaging (future: multi-node phi fusion).

        C30: DEGRADED — a malformed envelope must be logged, not silently dropped.
        """
        if self._crdt is None:
            return
        try:
            with degraded(
                "core.mother_thread",
                "on_remote_pulse",
                context={"envelope_keys": list(envelope.payload.keys()) if hasattr(envelope, "payload") else []},
            ):
                remote_phi = envelope.payload.get("collective_field", {}).get("collective_phi")
                remote_node = envelope.payload.get("mesh", {}).get("node_id", "unknown")
                if remote_phi is not None:
                    key = f"remote_phi:{remote_node}"
                    self._crdt.set_field(
                        key,
                        float(remote_phi),
                        timestamp=envelope.payload.get("timestamp"),
                    )
        except GAIABoundaryError:
            pass  # already logged by DEGRADED boundary

    def _on_weaver_slot(self, slot) -> None:
        """Called by the ThreadWeaver when a distributed slot fires.

        Triggers an immediate beat + broadcast without waiting for the
        internal asyncio sleep — keeps all mesh nodes pulse-aligned.

        C30: RECOVERABLE — a failed task creation is not fatal but must be
        logged; the fallback pulse loop will continue driving beats.
        """
        pulse = self._beat()
        try:
            with recoverable(
                "core.mother_thread",
                "on_weaver_slot.create_task",
                context={"pulse_seq": pulse.sequence},
            ):
                loop = asyncio.get_running_loop()
                loop.create_task(self._broadcast(pulse))
        except GAIABoundaryError:
            pass  # already logged; fallback loop will fire next beat

    def _gossip_pulse(self, pulse: MotherPulse) -> None:
        """Publish a MotherPulse to the mesh gossip layer.

        C30: DEGRADED — a gossip transport error must be logged but must not
        interrupt the local pulse cycle.  The field continues pulsing even
        when mesh connectivity is degraded.
        """
        if self._mesh is None or not self._mesh_active:
            return
        try:
            with degraded(
                "core.mother_thread",
                "gossip_pulse",
                context={"pulse_seq": pulse.sequence, "node_id": getattr(self._mesh, "node_id", None)},
            ):
                self._mesh.gossip("mother_pulse", pulse.to_dict())
                if self._crdt is not None:
                    cf = pulse.collective_field
                    self._crdt.set_field("collective_phi", cf.collective_phi,
                                         timestamp=pulse.timestamp)
                    self._crdt.set_field("noosphere_stage", cf.noosphere_stage,
                                         timestamp=pulse.timestamp)
                    self._crdt.set_field("dominant_element", cf.dominant_element,
                                         timestamp=pulse.timestamp)
                    self._crdt.set_field("field_coherence_label", cf.field_coherence_label,
                                         timestamp=pulse.timestamp)
                    self._mesh.gossip(
                        self._crdt.GOSSIP_TOPIC,
                        self._crdt.to_gossip_payload(),
                    )
        except GAIABoundaryError:
            pass  # already logged; local pulse continues

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the pulse loop from a sync context.
        Idempotent — safe to call multiple times.
        """
        if self._running:
            return
        self._running = True
        loop = asyncio.get_running_loop()
        self._task = loop.create_task(self._pulse_loop())

    async def async_start(self) -> None:
        """Start the pulse loop from an async context.
        Idempotent — safe to call multiple times.
        """
        if self._running:
            return
        self._running = True
        self._task = asyncio.ensure_future(self._pulse_loop())

    def stop(self) -> None:
        """Stop the pulse loop. Safe to call before start()."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            self._task = None

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        slug: str,
        gaian_name: str,
        collective_consent: bool = False,
        runtime: object = None,
    ) -> GaianThread:
        """Register a Gaian. Consent defaults to False (C04 privacy)."""
        gt = GaianThread(
            slug=slug,
            gaian_name=gaian_name,
            collective_consent=collective_consent,
        )
        self._threads[slug] = gt
        if runtime is not None:
            self._runtimes[slug] = runtime
        return gt

    def deregister(self, slug: str) -> None:
        """Remove a Gaian. No-op if unknown."""
        self._threads.pop(slug, None)
        self._runtimes.pop(slug, None)

    def set_consent(self, slug: str, consent: bool) -> None:
        """Update collective consent for a Gaian. No-op if unknown."""
        if slug in self._threads:
            self._threads[slug].collective_consent = consent

    # ------------------------------------------------------------------
    # Pulse
    # ------------------------------------------------------------------

    def _beat(self) -> MotherPulse:
        """Generate a single pulse. Increments sequence. Logs to weaving log."""
        self._pulse_sequence += 1
        threads = list(self._threads.values())
        cf = _compute_collective_field(threads)

        # Attempt to read criticality label — gracefully degrade if unavailable.
        # C30: DEGRADED so the import failure is logged, not silently swallowed.
        criticality_label = "critical"
        try:
            with degraded(
                "core.mother_thread",
                "beat.criticality_monitor",
                context={"pulse_seq": self._pulse_sequence},
            ):
                from core.criticality_monitor import get_monitor  # noqa: PLC0415
                criticality_label = get_monitor().current_label
        except GAIABoundaryError:
            pass  # already logged; fall through with default label

        voice = _select_mother_voice(
            cf.collective_phi,
            cf.consenting_gaians,
            criticality_label,
            self._pulse_sequence,
        )

        candidate = cf.collective_phi >= _COHERENCE_CANDIDATE_THRESHOLD

        # Mesh provenance
        mesh_node_id = self._mesh.node_id if self._mesh else None
        mesh_peer_count = self._mesh.peer_count() if self._mesh else 0
        crdt_live_nodes = len(self._crdt.live_nodes()) if self._crdt else 0

        pulse = MotherPulse(
            sequence=self._pulse_sequence,
            collective_field=cf,
            mother_voice=voice,
            coherence_candidate=candidate,
            mesh_node_id=mesh_node_id,
            mesh_peer_count=mesh_peer_count,
            crdt_live_nodes=crdt_live_nodes,
        )

        epistemic_note: Optional[str] = None
        if candidate:
            epistemic_note = (
                "[C43] Collective phi above threshold — not a confirmed "
                "consciousness event. Epistemic integrity preserved."
            )

        record = WeavingRecord(
            sequence=self._pulse_sequence,
            timestamp=pulse.timestamp,
            coherence_label=cf.field_coherence_label,
            noosphere_stage=cf.noosphere_stage,
            candidate=candidate,
            epistemic_note=epistemic_note,
        )
        self._weaving_log.append(record)

        # Gossip pulse to mesh peers
        self._gossip_pulse(pulse)

        return pulse

    async def _broadcast(self, pulse: MotherPulse) -> None:
        """Broadcast a pulse to all subscribers. Prune full queues."""
        pulse_dict = pulse.to_dict()
        stale: List[asyncio.Queue] = []
        for q in list(self._subscribers):
            try:
                q.put_nowait(pulse_dict)
            except asyncio.QueueFull:
                stale.append(q)
        for q in stale:
            try:
                self._subscribers.remove(q)
            except ValueError:
                pass

    async def _pulse_loop(self) -> None:
        """
        Main async pulse loop.
        When a ThreadWeaver is attached, this loop still runs as a fallback
        cadence but the weaver's slot callbacks drive the primary beats.
        """
        try:
            await asyncio.sleep(0)
            while self._running:
                pulse = self._beat()
                await self._broadcast(pulse)
                await asyncio.sleep(PULSE_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            raise

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------

    async def subscribe(self) -> AsyncGenerator[dict, None]:
        """Async generator that yields pulse dicts as they are broadcast."""
        q: asyncio.Queue = asyncio.Queue(maxsize=10)
        self._subscribers.append(q)
        try:
            while True:
                item = await q.get()
                yield item
        finally:
            try:
                self._subscribers.remove(q)
            except ValueError:
                pass

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_weaving_log(self, last_n: Optional[int] = None) -> List[dict]:
        """Return weaving log entries as dicts, optionally limited to last N."""
        log = list(self._weaving_log)
        if last_n is not None:
            log = log[-last_n:]
        return [r.to_dict() for r in log]

    def get_status(self) -> dict:
        """Return a status snapshot of the Mother Thread."""
        cf = _compute_collective_field(list(self._threads.values()))
        mesh_status = self._mesh.get_status() if self._mesh else None
        crdt_status = self._crdt.get_status() if self._crdt else None
        weaver_status = self._weaver.get_status() if self._weaver else None
        return {
            "doctrine": "C04, C30, C43, C44, C47",
            "running": self._running,
            "pulse_sequence": self._pulse_sequence,
            "pulse_interval_s": PULSE_INTERVAL_SECONDS,
            "registered_gaians": len(self._threads),
            "active_subscribers": len(self._subscribers),
            "collective_field": cf.to_dict(),
            "recent_pulses": self.get_weaving_log(last_n=5),
            "weaving_log_size": len(self._weaving_log),
            "privacy_status": (
                "Individual Gaian identities protected. "
                "Aggregate statistics only. Canon C04."
            ),
            "mesh": mesh_status,
            "crdt": crdt_status,
            "weaver": weaver_status,
        }


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_mother_thread_instance: Optional[MotherThread] = None


def get_mother_thread() -> MotherThread:
    """Return the module-level singleton MotherThread."""
    global _mother_thread_instance
    if _mother_thread_instance is None:
        _mother_thread_instance = MotherThread()
    return _mother_thread_instance

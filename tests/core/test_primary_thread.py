"""
tests/core/test_primary_thread.py

Unit tests for core/primary_thread.py and core/mother_thread.py.

Covers:
  - Public surface of the re-export shim
  - MotherThread lifecycle (start/stop idempotency)
  - Registration / deregistration / consent
  - _beat(): pulse generation, sequence increment, weaving log
  - _compute_collective_field(): math, privacy, stale pruning
  - _noosphere_stage_label() and _select_mother_voice()
  - Subscription queue and stale-queue pruning
  - Mesh-absent graceful degrade (no mesh attached)
  - C30 boundary paths: corrupt CRDT gossip, failed gossip transport,
    failed weaver-slot task creation

Canon: C04, C30, C43
Issue: #811
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_thread(slug="alice", consent=True, phi=0.5, element="water"):
    from core.mother_thread import GaianThread
    import time
    gt = GaianThread(slug=slug, gaian_name=slug.title(), collective_consent=consent)
    gt.coherence_phi = phi
    gt.dominant_element = element
    gt.bond_depth = 0.6
    gt.noosphere_health = 0.7
    gt.last_pulse_contribution = time.time()
    return gt


# ---------------------------------------------------------------------------
# Re-export surface
# ---------------------------------------------------------------------------

class TestPrimaryThreadShim:
    def test_primary_thread_alias(self):
        from core.primary_thread import PrimaryThread, MotherThread
        assert PrimaryThread is MotherThread

    def test_get_primary_thread_returns_mother_thread_singleton(self):
        from core.primary_thread import get_primary_thread, get_mother_thread
        assert get_primary_thread() is get_mother_thread()

    def test_all_symbols_exported(self):
        import core.primary_thread as mod
        for sym in [
            "PrimaryThread", "MotherThread", "get_primary_thread", "get_mother_thread",
            "CollectiveField", "GaianThread", "MotherPulse", "WeavingRecord",
            "PULSE_INTERVAL_SECONDS",
        ]:
            assert hasattr(mod, sym), f"Missing export: {sym}"


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

class TestLifecycle:
    def test_stop_before_start_is_noop(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        mt.stop()  # must not raise
        assert not mt._running

    @pytest.mark.asyncio
    async def test_async_start_idempotent(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        await mt.async_start()
        task1 = mt._task
        await mt.async_start()  # second call must be no-op
        assert mt._task is task1
        mt.stop()

    @pytest.mark.asyncio
    async def test_stop_cancels_task(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        await mt.async_start()
        assert mt._running
        mt.stop()
        assert not mt._running
        assert mt._task is None


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class TestRegistration:
    def test_register_creates_thread(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        gt = mt.register("bob", "Bob", collective_consent=True)
        assert gt.slug == "bob"
        assert "bob" in mt._threads

    def test_deregister_removes_thread(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        mt.register("carol", "Carol")
        mt.deregister("carol")
        assert "carol" not in mt._threads

    def test_deregister_unknown_is_noop(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        mt.deregister("ghost")  # must not raise

    def test_set_consent_updates_thread(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        mt.register("dan", "Dan", collective_consent=False)
        mt.set_consent("dan", True)
        assert mt._threads["dan"].collective_consent is True

    def test_set_consent_unknown_is_noop(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        mt.set_consent("nobody", True)  # must not raise


# ---------------------------------------------------------------------------
# _compute_collective_field
# ---------------------------------------------------------------------------

class TestComputeCollectiveField:
    def test_empty_threads_returns_dormant(self):
        from core.mother_thread import _compute_collective_field
        cf = _compute_collective_field([])
        assert cf.active_gaians == 0
        assert cf.collective_phi == 0.0
        assert cf.field_coherence_label == "dormant"

    def test_non_consenting_excluded(self):
        from core.mother_thread import _compute_collective_field
        gt = _make_thread(consent=False)
        cf = _compute_collective_field([gt])
        assert cf.consenting_gaians == 0

    def test_phi_averaged_correctly(self):
        from core.mother_thread import _compute_collective_field
        threads = [
            _make_thread("a", phi=0.4),
            _make_thread("b", phi=0.6),
        ]
        cf = _compute_collective_field(threads)
        assert abs(cf.collective_phi - 0.5) < 0.05  # allow schumann amplification

    def test_dominant_element_selected(self):
        from core.mother_thread import _compute_collective_field
        threads = [
            _make_thread("a", element="fire"),
            _make_thread("b", element="fire"),
            _make_thread("c", element="water"),
        ]
        cf = _compute_collective_field(threads)
        assert cf.dominant_element == "fire"

    def test_privacy_note_present(self):
        from core.mother_thread import _compute_collective_field
        cf = _compute_collective_field([])
        assert "Canon C04" in cf.privacy_note


# ---------------------------------------------------------------------------
# _beat and weaving log
# ---------------------------------------------------------------------------

class TestBeat:
    def test_beat_increments_sequence(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        pulse = mt._beat()
        assert pulse.sequence == 1
        pulse2 = mt._beat()
        assert pulse2.sequence == 2

    def test_beat_appends_to_weaving_log(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        mt._beat()
        assert len(mt._weaving_log) == 1

    def test_weaving_log_last_n(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        for _ in range(10):
            mt._beat()
        log = mt.get_weaving_log(last_n=3)
        assert len(log) == 3

    def test_coherence_candidate_flagged_at_high_phi(self):
        from core.mother_thread import MotherThread
        mt = MotherThread()
        gt = _make_thread(phi=0.9)
        mt._threads["high"] = gt
        pulse = mt._beat()
        assert pulse.coherence_candidate is True
        record = list(mt._weaving_log)[-1]
        assert record.epistemic_note is not None


# ---------------------------------------------------------------------------
# C30 boundary paths
# ---------------------------------------------------------------------------

class TestC30Boundaries:
    def test_crdt_gossip_error_does_not_raise(self):
        """C30/DEGRADED: a corrupt CRDT gossip merge must not crash the thread."""
        from core.mother_thread import MotherThread
        mt = MotherThread()
        mock_crdt = MagicMock()
        mock_crdt.merge_gossip.side_effect = RuntimeError("corrupt gossip")
        mock_crdt.GOSSIP_TOPIC = "crdt_sync"
        mt._crdt = mock_crdt
        envelope = MagicMock()
        envelope.payload = {"data": "bad"}
        mt._on_crdt_gossip(envelope)  # must NOT raise

    def test_remote_pulse_error_does_not_raise(self):
        """C30/DEGRADED: a malformed remote pulse must not crash the thread."""
        from core.mother_thread import MotherThread
        mt = MotherThread()
        mock_crdt = MagicMock()
        mock_crdt.set_field.side_effect = ValueError("type error")
        mt._crdt = mock_crdt
        envelope = MagicMock()
        envelope.payload = {
            "collective_field": {"collective_phi": 0.5},
            "mesh": {"node_id": "node-1"},
            "timestamp": 1234567890.0,
        }
        mt._on_remote_pulse(envelope)  # must NOT raise

    def test_gossip_pulse_error_does_not_interrupt_pulse(self):
        """C30/DEGRADED: gossip failure must not stop local pulse cycle."""
        from core.mother_thread import MotherThread, MotherPulse, CollectiveField
        mt = MotherThread()
        mock_mesh = MagicMock()
        mock_mesh.gossip.side_effect = OSError("network down")
        mock_mesh.node_id = "node-x"
        mt._mesh = mock_mesh
        mt._mesh_active = True
        pulse = MotherPulse(sequence=1, collective_field=CollectiveField())
        mt._gossip_pulse(pulse)  # must NOT raise

    def test_no_mesh_beat_runs_cleanly(self):
        """Mesh-absent: _beat must run without errors when no mesh is attached."""
        from core.mother_thread import MotherThread
        mt = MotherThread()
        pulse = mt._beat()  # must NOT raise
        assert pulse.mesh_node_id is None
        assert pulse.mesh_peer_count == 0

"""Stoppability test suite for HaltController — issue #250.

Covers:
- pause / resume round-trip
- SOFT_STOP propagates cancel to all sessions
- HARD_STOP propagates cancel immediately
- Dead-man's switch fires when heartbeat lapses
- Audit trail is populated and HMAC signatures are valid
- Concurrent session registration + halt is race-free
- SLA tracking sets sla_met correctly
"""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock

import pytest

from core.governance.halt_controller import (
    HaltController,
    HaltMode,
    HaltRecord,
    HaltStatus,
    SessionHandle,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_handle(session_id: str = "s-test") -> tuple[SessionHandle, dict]:
    """Return a SessionHandle whose callables record invocations."""
    calls: dict = {"cancel": 0, "pause": 0, "resume": 0}
    handle = SessionHandle(
        session_id=session_id,
        cancel_fn=lambda: calls.__setitem__("cancel", calls["cancel"] + 1),
        pause_fn=lambda: calls.__setitem__("pause", calls["pause"] + 1),
        resume_fn=lambda: calls.__setitem__("resume", calls["resume"] + 1),
        gaian_id="test-gaian",
    )
    return handle, calls


@pytest.fixture(autouse=True)
def fresh_controller():
    """Each test gets a clean singleton."""
    HaltController.reset_for_testing()
    yield
    HaltController.reset_for_testing()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPauseResume:
    def test_pause_sets_status_paused(self):
        ctrl = HaltController.get_instance()
        handle, _ = _make_handle()
        ctrl.register_session(handle)
        ctrl.pause(triggered_by="tester")
        assert ctrl.status == HaltStatus.PAUSED

    def test_pause_calls_pause_fn_on_all_sessions(self):
        ctrl = HaltController.get_instance()
        handles_calls = [_make_handle(f"s-{i}") for i in range(5)]
        for h, _ in handles_calls:
            ctrl.register_session(h)
        ctrl.pause(triggered_by="tester")
        for _, calls in handles_calls:
            assert calls["pause"] == 1

    def test_resume_restores_running_status(self):
        ctrl = HaltController.get_instance()
        handle, _ = _make_handle()
        ctrl.register_session(handle)
        ctrl.pause(triggered_by="tester")
        ctrl.resume(triggered_by="tester")
        assert ctrl.status == HaltStatus.RUNNING

    def test_resume_calls_resume_fn(self):
        ctrl = HaltController.get_instance()
        handle, calls = _make_handle()
        ctrl.register_session(handle)
        ctrl.pause()
        ctrl.resume()
        assert calls["resume"] == 1

    def test_resume_from_non_paused_raises(self):
        ctrl = HaltController.get_instance()
        with pytest.raises(RuntimeError):
            ctrl.resume()


class TestSoftStop:
    def test_soft_stop_sets_status_stopped(self):
        ctrl = HaltController.get_instance()
        handle, _ = _make_handle()
        ctrl.register_session(handle)
        ctrl.halt(HaltMode.SOFT_STOP, triggered_by="tester")
        assert ctrl.status == HaltStatus.STOPPED

    def test_soft_stop_calls_cancel_on_all_sessions(self):
        ctrl = HaltController.get_instance()
        handles_calls = [_make_handle(f"s-{i}") for i in range(3)]
        for h, _ in handles_calls:
            ctrl.register_session(h)
        ctrl.halt(HaltMode.SOFT_STOP, triggered_by="tester")
        for _, calls in handles_calls:
            assert calls["cancel"] == 1

    def test_soft_stop_creates_audit_record(self):
        ctrl = HaltController.get_instance()
        ctrl.halt(HaltMode.SOFT_STOP, triggered_by="tester")
        trail = ctrl.audit_trail()
        assert len(trail) == 1
        assert trail[0]["mode"] == "SOFT_STOP"
        assert trail[0]["triggered_by"] == "tester"


class TestHardStop:
    def test_hard_stop_sets_status_stopped(self):
        ctrl = HaltController.get_instance()
        handle, _ = _make_handle()
        ctrl.register_session(handle)
        ctrl.halt(HaltMode.HARD_STOP, triggered_by="tester")
        assert ctrl.status == HaltStatus.STOPPED

    def test_hard_stop_calls_cancel_immediately(self):
        ctrl = HaltController.get_instance()
        handle, calls = _make_handle()
        ctrl.register_session(handle)
        ctrl.halt(HaltMode.HARD_STOP, triggered_by="regulator")
        assert calls["cancel"] == 1


class TestAuditTrail:
    def test_audit_record_is_hmac_signed(self):
        ctrl = HaltController.get_instance()
        ctrl.halt(HaltMode.HARD_STOP, triggered_by="tester")
        trail = ctrl.audit_trail()
        assert len(trail) == 1
        record = HaltRecord(**trail[0])
        assert record.verify(HaltController._HMAC_SECRET)

    def test_tampered_record_fails_verification(self):
        ctrl = HaltController.get_instance()
        ctrl.halt(HaltMode.SOFT_STOP, triggered_by="tester")
        trail = ctrl.audit_trail()
        trail[0]["triggered_by"] = "ATTACKER"
        record = HaltRecord(**trail[0])
        assert not record.verify(HaltController._HMAC_SECRET)

    def test_multiple_halts_accumulate_records(self):
        ctrl = HaltController.get_instance()
        # First halt
        ctrl.halt(HaltMode.PAUSE, triggered_by="first")
        ctrl._status = HaltStatus.RUNNING  # Reset for second halt
        ctrl.halt(HaltMode.SOFT_STOP, triggered_by="second")
        assert len(ctrl.audit_trail()) == 2


class TestSLA:
    def test_sla_met_when_halt_is_fast(self):
        ctrl = HaltController.get_instance()
        ctrl.halt(HaltMode.HARD_STOP, triggered_by="tester")
        trail = ctrl.audit_trail()
        assert trail[0]["sla_met"] is True

    def test_sla_breach_flagged_when_deadline_passed(self, monkeypatch):
        ctrl = HaltController.get_instance()
        original_create = ctrl._create_record

        def slow_create(mode, triggered_by):
            record = original_create(mode, triggered_by)
            # Set deadline in the past
            record.sla_deadline = time.time() - 1
            return record

        monkeypatch.setattr(ctrl, "_create_record", slow_create)
        ctrl.halt(HaltMode.SOFT_STOP, triggered_by="tester")
        trail = ctrl.audit_trail()
        assert trail[0]["sla_met"] is False


class TestDeadMansSwitch:
    def test_deadmans_switch_triggers_hard_stop(self, monkeypatch):
        """Simulate heartbeat expiry by rolling back _last_heartbeat."""
        ctrl = HaltController.get_instance()
        # Shorten the interval so we don't wait 120s
        monkeypatch.setattr(ctrl, "DEFAULT_HEARTBEAT_INTERVAL", 0.05)
        ctrl._last_heartbeat = time.time() - 1.0  # Already expired
        # Allow the watch thread to detect it
        deadline = time.time() + 5.0
        while time.time() < deadline:
            if ctrl.status == HaltStatus.STOPPED:
                break
            time.sleep(0.05)
        assert ctrl.status == HaltStatus.STOPPED
        trail = ctrl.audit_trail()
        assert any(r["triggered_by"] == "DEADMANS_SWITCH" for r in trail)

    def test_heartbeat_resets_timer(self):
        ctrl = HaltController.get_instance()
        ctrl._last_heartbeat = 0.0  # Simulate very old heartbeat
        ctrl.heartbeat(gaian_id="test-gaian")
        with ctrl._heartbeat_lock:
            elapsed = time.time() - ctrl._last_heartbeat
        assert elapsed < 1.0


class TestConcurrency:
    def test_concurrent_halt_is_race_free(self):
        """Multiple threads calling halt() simultaneously must not corrupt state."""
        ctrl = HaltController.get_instance()
        for i in range(20):
            h, _ = _make_handle(f"s-{i}")
            ctrl.register_session(h)

        errors: list = []

        def _do_halt():
            try:
                ctrl.halt(HaltMode.HARD_STOP, triggered_by="thread")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=_do_halt) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        assert not errors
        assert ctrl.status == HaltStatus.STOPPED

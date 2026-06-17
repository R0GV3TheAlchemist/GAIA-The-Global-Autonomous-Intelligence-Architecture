"""
tests/test_session_d6_bridge.py
================================
Wire 4 Test Suite — SessionClock → EngineProbes → D6Engine → HUD
Issue #589, Phase 1

Tests:
  T01 — SessionClock: elapsed_hours=0 before start
  T02 — SessionClock: elapsed_hours correct after known duration
  T03 — SessionClock: time_since_rest_hours equals elapsed when no rest declared
  T04 — SessionClock: time_since_rest_hours resets after declare_rest()
  T05 — SleepQualityStore: defaults to 0.5, clamps to [0,1], has_data flag
  T06 — translate_session_to_probes: all three probe fields correctly populated
  T07 — SessionToD6Bridge.poll_once() returns (SessionProbeResult, InterventionEvent)
  T08 — Wire 4 → Wire 1: poll_once() fires D6 on_intervention callback
  T09 — Background thread starts, runs at least one cycle, stops cleanly
  T10 — Wire 4 supersedes Wire 3 session_duration_hours (last-write-wins proof)
"""

from __future__ import annotations

import threading
import time
from typing import List

import pytest

from gaia.core.d6_engine import D6Engine
from gaia.core.state import default_state
from gaia.session.session_clock import SessionClock, SleepQualityStore
from gaia.session.session_d6_bridge import (
    SessionProbeResult,
    SessionToD6Bridge,
    create_wire4,
    translate_session_to_probes,
)


# ---------------------------------------------------------------------------
# T01 — elapsed_hours = 0 before start
# ---------------------------------------------------------------------------

def test_T01_elapsed_hours_zero_before_start():
    """
    T01: A fresh SessionClock that has not been started must return
    elapsed_hours=0.0 and time_since_rest_hours=0.0.
    """
    clock = SessionClock()
    assert clock.elapsed_hours() == 0.0
    assert clock.time_since_rest_hours() == 0.0
    assert not clock.is_running


# ---------------------------------------------------------------------------
# T02 — elapsed_hours correct after known duration
# ---------------------------------------------------------------------------

def test_T02_elapsed_hours_correct_after_known_duration():
    """
    T02: Starting the clock at t=0 and querying at t=3600 must yield
    elapsed_hours exactly 1.0. Starting at t=0 and querying at t=5400
    must yield 1.5 hours.
    """
    clock = SessionClock()
    t0 = 1_000_000.0

    clock.start(at=t0)
    assert clock.is_running

    # 1 hour later
    assert abs(clock.elapsed_hours(now=t0 + 3600) - 1.0) < 0.0001
    # 1.5 hours later
    assert abs(clock.elapsed_hours(now=t0 + 5400) - 1.5) < 0.0001
    # 0 seconds later — still ~0
    assert clock.elapsed_hours(now=t0) == 0.0


# ---------------------------------------------------------------------------
# T03 — time_since_rest_hours equals elapsed when no rest declared
# ---------------------------------------------------------------------------

def test_T03_time_since_rest_equals_elapsed_when_no_rest():
    """
    T03: When no rest has been declared, time_since_rest_hours must equal
    elapsed_hours. This is the conservative interpretation: the entire
    session counts as unbroken work time.
    """
    clock = SessionClock()
    t0 = 2_000_000.0
    clock.start(at=t0)

    now = t0 + 7200  # 2 hours into session
    elapsed = clock.elapsed_hours(now=now)
    since_rest = clock.time_since_rest_hours(now=now)

    assert abs(elapsed - since_rest) < 0.0001, (
        f"time_since_rest ({since_rest:.4f}h) must equal elapsed ({elapsed:.4f}h) "
        f"when no rest declared"
    )


# ---------------------------------------------------------------------------
# T04 — time_since_rest_hours resets after declare_rest()
# ---------------------------------------------------------------------------

def test_T04_time_since_rest_resets_after_declare_rest():
    """
    T04: After calling declare_rest(), time_since_rest_hours must be
    close to 0.0 at the moment of declaration, and must grow from there.
    Declaring multiple rests must use only the most recent event.
    """
    clock = SessionClock()
    t0 = 3_000_000.0
    clock.start(at=t0)

    # 2 hours in — first rest
    rest_t = t0 + 7200
    clock.declare_rest(label="break", at=rest_t)

    # At rest declaration: since_rest ≈ 0
    assert clock.time_since_rest_hours(now=rest_t) < 0.001

    # 30 min after rest
    assert abs(clock.time_since_rest_hours(now=rest_t + 1800) - 0.5) < 0.001

    # Second rest 3 hours in
    rest_t2 = t0 + 10800
    clock.declare_rest(label="nap", at=rest_t2)
    assert clock.time_since_rest_hours(now=rest_t2) < 0.001
    assert len(clock.rest_events) == 2
    assert clock.rest_events[-1].label == "nap"


# ---------------------------------------------------------------------------
# T05 — SleepQualityStore: defaults, clamping, has_data
# ---------------------------------------------------------------------------

def test_T05_sleep_quality_store_defaults_clamps_has_data():
    """
    T05: SleepQualityStore must:
      - Default to 0.5 (neutral) before any report
      - Report has_data=False before any report
      - Clamp scores above 1.0 to 1.0
      - Clamp scores below 0.0 to 0.0
      - Set has_data=True after report()
      - Reset to default after reset()
    """
    store = SleepQualityStore()

    assert store.score == 0.5
    assert not store.has_data
    assert store.reported_at is None

    # Normal report
    store.report(0.85)
    assert abs(store.score - 0.85) < 0.001
    assert store.has_data
    assert store.reported_at is not None

    # Clamping
    store.report(1.5)
    assert store.score == 1.0
    store.report(-0.3)
    assert store.score == 0.0

    # Reset
    store.reset()
    assert store.score == 0.5
    assert not store.has_data


# ---------------------------------------------------------------------------
# T06 — translate_session_to_probes: all three fields populated
# ---------------------------------------------------------------------------

def test_T06_translate_session_to_probes_populates_all_fields():
    """
    T06: translate_session_to_probes() must correctly populate:
      - probes.session_duration_hours  (from clock.elapsed_hours)
      - probes.time_since_rest_hours   (from clock.time_since_rest_hours)
      - probes.sleep_quality_score     (from sleep_store.score)
    """
    clock = SessionClock()
    sleep_store = SleepQualityStore()

    t0 = 5_000_000.0
    clock.start(at=t0)
    sleep_store.report(0.75)

    rest_t = t0 + 3600  # rest at 1h
    clock.declare_rest(at=rest_t)

    now = rest_t + 1800  # 30min after rest, 1.5h elapsed

    result = translate_session_to_probes(clock, sleep_store, now=now)

    assert abs(result.probes.session_duration_hours - 1.5) < 0.001, (
        f"Expected session_duration_hours~1.5h, got {result.probes.session_duration_hours}"
    )
    assert abs(result.probes.time_since_rest_hours - 0.5) < 0.001, (
        f"Expected time_since_rest_hours~0.5h, got {result.probes.time_since_rest_hours}"
    )
    assert abs(result.probes.sleep_quality_score - 0.75) < 0.001, (
        f"Expected sleep_quality_score~0.75, got {result.probes.sleep_quality_score}"
    )
    assert result.sleep_has_data is True
    assert result.rest_event_count == 1


# ---------------------------------------------------------------------------
# T07 — poll_once() returns correct types
# ---------------------------------------------------------------------------

def test_T07_poll_once_returns_probe_result_and_event():
    """
    T07: SessionToD6Bridge.poll_once() must return a tuple of
    (SessionProbeResult, InterventionEvent) with correct types.
    """
    clock = SessionClock()
    sleep_store = SleepQualityStore()
    clock.start()
    sleep_store.report(0.80)

    state = default_state()
    engine = D6Engine(auto_apply=True)
    bridge = SessionToD6Bridge(
        clock=clock, sleep_store=sleep_store,
        engine=engine, state=state,
        poll_interval=60.0,
    )

    probe_result, event = bridge.poll_once()

    assert isinstance(probe_result, SessionProbeResult)
    assert bridge.cycle_count == 1
    assert event is not None
    assert hasattr(event, "severity")
    assert hasattr(event, "recommended_mode")
    assert probe_result.probes.session_duration_hours is not None
    assert probe_result.probes.time_since_rest_hours is not None
    assert probe_result.probes.sleep_quality_score is not None


# ---------------------------------------------------------------------------
# T08 — Wire 4 → Wire 1: poll_once fires on_intervention
# ---------------------------------------------------------------------------

def test_T08_poll_once_fires_on_intervention_callback():
    """
    T08: Wire 4 → Wire 1 integration test.

    SessionToD6Bridge.poll_once() must fire D6Engine’s on_intervention
    callback (Wire 1). This proves:
      SessionClock → Wire 4 translate → D6 evaluate → Wire 1 callback
    The full session-to-HUD chain is alive.
    """
    interventions: List = []

    def capture(event):
        interventions.append(event)

    clock = SessionClock()
    sleep_store = SleepQualityStore()
    clock.start()
    sleep_store.report(0.10)  # poor sleep → higher REST urgency

    state = default_state()
    engine = D6Engine(auto_apply=True, on_intervention=capture)
    bridge = SessionToD6Bridge(
        clock=clock, sleep_store=sleep_store,
        engine=engine, state=state,
        poll_interval=60.0,
    )

    bridge.poll_once()

    assert len(interventions) >= 1, (
        "Wire 4 → Wire 1: poll_once() must fire on_intervention at least once"
    )
    event = interventions[0]
    assert hasattr(event, "severity")
    assert hasattr(event, "recommended_mode")


# ---------------------------------------------------------------------------
# T09 — Background thread starts, runs one cycle, stops cleanly
# ---------------------------------------------------------------------------

def test_T09_background_thread_starts_runs_stops():
    """
    T09: SessionToD6Bridge.start() must launch a daemon thread that
    executes at least one poll cycle within 1 second, then stop cleanly
    when stop() is called.
    """
    clock = SessionClock()
    sleep_store = SleepQualityStore()
    clock.start()

    state = default_state()
    engine = D6Engine(auto_apply=True)
    bridge = SessionToD6Bridge(
        clock=clock, sleep_store=sleep_store,
        engine=engine, state=state,
        poll_interval=0.05,   # fast poll for test speed
    )

    bridge.start()
    assert bridge.is_running

    # Wait for at least one cycle
    deadline = time.time() + 1.0
    while bridge.cycle_count == 0 and time.time() < deadline:
        time.sleep(0.02)

    assert bridge.cycle_count >= 1, (
        f"Expected ≥1 cycle within 1s, got {bridge.cycle_count}"
    )

    bridge.stop()
    bridge.join(timeout=0.5)
    assert not bridge.is_running


# ---------------------------------------------------------------------------
# T10 — Wire 4 supersedes Wire 3 session_duration_hours (last-write-wins)
# ---------------------------------------------------------------------------

def test_T10_wire4_supersedes_wire3_session_duration():
    """
    T10: Wire 4 → Wire 3 override proof.

    When Wire 4 calls D6Engine.evaluate() with session_duration_hours=2.0
    after Wire 3 called it with session_duration_hours=0.25 (pulse estimate),
    the D6Engine must see Wire 4’s value on the second call.

    This proves the last-write-wins composition model: Wire 4’s precise
    wall-clock value supersedes Wire 3’s pulse-sequence estimate
    without any explicit coordination between the two wires.
    """
    from gaia.collective.mother_d6_bridge import translate_pulse_to_probes
    from core.mother_thread import PULSE_INTERVAL_SECONDS

    state = default_state()
    seen_probes: List = []

    # Capture the probes each evaluate() call receives
    class ProbeCapturingEngine(D6Engine):
        def evaluate(self, state, probes):
            seen_probes.append(probes)
            return super().evaluate(state, probes)

    engine = ProbeCapturingEngine(auto_apply=True)

    # — Wire 3 fires first: pulse sequence=30 → 30×30/3600 = 0.25h —
    pulse = {
        "sequence": 30,
        "collective_field": {
            "collective_phi": 0.5, "consenting_gaians": 2,
            "schumann_aligned_count": 1, "avg_noosphere_health": 0.7,
            "field_coherence_label": "coherent",
            "noosphere_stage": "Noosphere — Resonant field building",
        },
    }
    from gaia.collective.mother_d6_bridge import MotherToD6Bridge
    from core.mother_thread import MotherThread
    w3_bridge = MotherToD6Bridge(mother=MotherThread(), engine=engine, state=state)
    w3_bridge.process_pulse(pulse)

    w3_duration = seen_probes[-1].session_duration_hours
    expected_w3 = round(30 * PULSE_INTERVAL_SECONDS / 3600, 4)
    assert abs(w3_duration - expected_w3) < 0.001, (
        f"Wire 3 should write session_duration_hours={expected_w3}, got {w3_duration}"
    )

    # — Wire 4 fires second: precise wall clock = 2.0h —
    clock = SessionClock()
    t0 = time.time() - 7200   # started 2 hours ago
    clock.start(at=t0)
    sleep_store = SleepQualityStore()

    w4_bridge = SessionToD6Bridge(
        clock=clock, sleep_store=sleep_store,
        engine=engine, state=state,
        poll_interval=60.0,
    )
    w4_bridge.poll_once()

    w4_duration = seen_probes[-1].session_duration_hours
    assert abs(w4_duration - 2.0) < 0.05, (
        f"Wire 4 must write session_duration_hours≈2.0h, got {w4_duration}. "
        f"Wire 4 precise clock must supersede Wire 3 pulse estimate."
    )
    assert w4_duration > w3_duration, (
        "Wire 4’s precise 2.0h must be greater than Wire 3’s 0.25h estimate"
    )

"""
gaia.session.session_d6_bridge
==============================
Wire 4 — SessionClock → EngineProbes → D6Engine → HUD
Issue #589, Phase 1

This module translates wall-clock session data (SessionClock) and sleep
quality (SleepQualityStore) into EngineProbes and feeds D6Engine.

Wire 4 completes the temporal dimension of the probe picture:

  Wire 2: body signals    → heart_rate_variability, movement_today, noosphere_load
  Wire 3: collective field→ collective_coherence, schumann_coherence, session_duration_hours*
  Wire 4: session clock   → session_duration_hours (precise), time_since_rest_hours,
                             sleep_quality_score

  * Wire 3’s session_duration_hours (pulse-sequence estimate) is superseded by Wire 4.
    Because D6Engine.evaluate() is stateless and last-write-wins at the probe level,
    Wire 4’s faster cycle (~5s ESB poll cadence) naturally overrides Wire 3’s slower
    estimate (30s MotherThread pulse cadence) without any explicit coordination.

Poll model
----------
Wire 4 runs as a background thread (like Wire 2), not an async subscriber
(like Wire 3). This is because SessionClock is a local in-process clock
with no async events — it must be polled.

Default poll interval: 30 seconds (configurable).
D6Engine is called on every poll → Wire 1 fires if thresholds are crossed.

Canon refs: C04 (Gaian wellbeing), C43 (epistemic integrity)
Issue: #589 Wire 4
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Optional

from gaia.core.d6_engine import D6Engine, EngineProbes, InterventionEvent
from gaia.core.state import GAIAState
from gaia.session.session_clock import (
    SessionClock,
    SleepQualityStore,
    get_session_clock,
    get_sleep_store,
)

log = logging.getLogger(__name__)

_DEFAULT_POLL_INTERVAL: float = 30.0   # seconds


# ---------------------------------------------------------------------------
# SessionProbeResult
# ---------------------------------------------------------------------------

@dataclass
class SessionProbeResult:
    """
    Intermediate result from a single Wire 4 poll cycle.
    Carries translated probes and session metadata.
    """
    probes: EngineProbes
    elapsed_hours: float              = 0.0
    time_since_rest_hours: float      = 0.0
    sleep_quality_score: float        = 0.5
    sleep_has_data: bool              = False
    rest_event_count: int             = 0
    timestamp: float                  = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------

def translate_session_to_probes(
    clock: SessionClock,
    sleep_store: SleepQualityStore,
    now: Optional[float] = None,
) -> SessionProbeResult:
    """
    Core Wire 4 translation function.

    Reads SessionClock and SleepQualityStore and maps their values
    to the appropriate EngineProbes slots.

    Parameters
    ----------
    clock:       The live SessionClock instance.
    sleep_store: The live SleepQualityStore instance.
    now:         Optional unix timestamp override (for deterministic testing).

    Returns
    -------
    SessionProbeResult with translated EngineProbes and session metadata.
    """
    reference = now or time.time()

    elapsed       = clock.elapsed_hours(now=reference)
    since_rest    = clock.time_since_rest_hours(now=reference)
    sleep_score   = sleep_store.score
    rest_count    = len(clock.rest_events)

    probes = EngineProbes(
        session_duration_hours = elapsed,
        time_since_rest_hours  = since_rest,
        sleep_quality_score    = sleep_score,
        # Wire 2/3 fields not populated here — they compose via last-write-wins
    )

    return SessionProbeResult(
        probes              = probes,
        elapsed_hours       = elapsed,
        time_since_rest_hours = since_rest,
        sleep_quality_score = sleep_score,
        sleep_has_data      = sleep_store.has_data,
        rest_event_count    = rest_count,
    )


# ---------------------------------------------------------------------------
# SessionToD6Bridge
# ---------------------------------------------------------------------------

class SessionToD6Bridge:
    """
    Wire 4 — polling bridge that reads SessionClock + SleepQualityStore
    and feeds translated EngineProbes into D6Engine every poll interval.

    Runs as a daemon background thread (like Wire 2 ESBtoD6Bridge).

    Usage
    -----
    ::

        bridge = SessionToD6Bridge(
            clock=get_session_clock(),
            sleep_store=get_sleep_store(),
            engine=d6_engine,
            state=gaia_state,
        )
        bridge.start()    # starts daemon thread
        # ...
        bridge.stop()     # signals thread to exit

    Wire 4 → Wire 1 signal path
    ----------------------------
        SessionClock.elapsed_hours()          → session_duration_hours
        SessionClock.time_since_rest_hours()  → time_since_rest_hours
        SleepQualityStore.score               → sleep_quality_score
            → EngineProbes
            → D6Engine.evaluate(state, probes)
            → on_intervention(event)            ← Wire 1
            → WebSocket broadcast               ← HUD receives INTERVENTION_EVENT

    Issue #589, Phase 1, Wire 4.
    """

    def __init__(
        self,
        clock: SessionClock,
        sleep_store: SleepQualityStore,
        engine: D6Engine,
        state: GAIAState,
        poll_interval: float = _DEFAULT_POLL_INTERVAL,
        on_probe_ready: Optional[object] = None,
    ) -> None:
        self._clock         = clock
        self._sleep_store   = sleep_store
        self._engine        = engine
        self._state         = state
        self._poll_interval = poll_interval
        self._on_probe      = on_probe_ready

        self._stop_event    = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._cycle_count   = 0
        self._error_count   = 0
        self._last_result: Optional[SessionProbeResult] = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    @property
    def error_count(self) -> int:
        return self._error_count

    @property
    def last_result(self) -> Optional[SessionProbeResult]:
        return self._last_result

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Start the polling thread. Idempotent — no-op if already running.
        Thread is daemon so it does not block clean process shutdown.
        """
        if self.is_running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._poll_loop,
            name="Wire4-SessionD6Bridge",
            daemon=True,
        )
        self._thread.start()
        log.info("Wire 4 started — SessionToD6Bridge polling every %.0fs", self._poll_interval)

    def stop(self) -> None:
        """
        Signal the polling thread to stop. Returns immediately.
        Join the thread if you need to wait for clean exit.
        """
        self._stop_event.set()
        log.info(
            "Wire 4 stopping — %d cycles, %d errors",
            self._cycle_count, self._error_count,
        )

    def join(self, timeout: Optional[float] = None) -> None:
        """Block until the polling thread has exited."""
        if self._thread is not None:
            self._thread.join(timeout=timeout)

    # ------------------------------------------------------------------
    # Core: single poll evaluation
    # ------------------------------------------------------------------

    def poll_once(self, now: Optional[float] = None) -> tuple[SessionProbeResult, InterventionEvent]:
        """
        Execute one Wire 4 poll cycle: translate → D6 evaluate.

        Exposed as a public synchronous method so tests can call it
        directly without starting the background thread.

        Returns
        -------
        (SessionProbeResult, InterventionEvent)
        """
        probe_result = translate_session_to_probes(
            self._clock,
            self._sleep_store,
            now=now,
        )

        if self._on_probe is not None:
            try:
                self._on_probe(probe_result)
            except Exception:  # noqa: BLE001
                pass

        event = self._engine.evaluate(self._state, probe_result.probes)
        self._last_result = probe_result
        self._cycle_count += 1

        log.debug(
            "Wire 4 cycle %d: elapsed=%.2fh rest=%.2fh sleep=%.2f → D6 severity=%s",
            self._cycle_count,
            probe_result.elapsed_hours,
            probe_result.time_since_rest_hours,
            probe_result.sleep_quality_score,
            event.severity,
        )
        return probe_result, event

    # ------------------------------------------------------------------
    # Polling loop
    # ------------------------------------------------------------------

    def _poll_loop(self) -> None:
        """Background thread: poll every _poll_interval seconds until stopped."""
        while not self._stop_event.is_set():
            try:
                self.poll_once()
            except Exception as exc:  # noqa: BLE001
                self._error_count += 1
                log.error(
                    "Wire 4 poll error (cycle %d): %s",
                    self._cycle_count, exc,
                    exc_info=True,
                )
            self._stop_event.wait(timeout=self._poll_interval)


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

def create_wire4(
    engine: D6Engine,
    state: GAIAState,
    poll_interval: float = _DEFAULT_POLL_INTERVAL,
    clock: Optional[SessionClock] = None,
    sleep_store: Optional[SleepQualityStore] = None,
) -> SessionToD6Bridge:
    """
    Factory function. Uses module-level singletons unless specific
    instances are provided.

    Wire up all four wires in main.py with:

        w4 = create_wire4(engine=_engine, state=_state)
        w4.start()
    """
    return SessionToD6Bridge(
        clock=clock or get_session_clock(),
        sleep_store=sleep_store or get_sleep_store(),
        engine=engine,
        state=state,
        poll_interval=poll_interval,
    )

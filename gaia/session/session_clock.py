"""
gaia.session.session_clock
==========================
Wire 4 — Session state tracking.

SessionClock
------------
A stateful singleton that tracks the wall-clock duration of the current
session and the time elapsed since the user last declared a rest.

This replaces the pulse-sequence estimate used in Wire 3
(sequence × PULSE_INTERVAL_SECONDS / 3600) with a precise wall clock.

Lifecycle
---------
  clock = get_session_clock()
  clock.start()           # Called at boot / session open
  clock.declare_rest()    # Called when user takes a break (HUD action)
  clock.stop()            # Called at session close / app shutdown

SleepQualityStore
-----------------
A lightweight store for the most recent sleep quality score [0, 1].
Fed by IMU sleep detection (Wire 2 ESB) or manual user declaration.
Defaults to 0.5 (neutral) when no data is available, so D6Engine
never penalises a Gaian for a missing wearable.

Canon refs: C04 (Gaian wellbeing), C43 (epistemic integrity)
Issue: #589 Wire 4
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# SleepQualityStore
# ---------------------------------------------------------------------------

_SLEEP_DEFAULT: float = 0.5   # neutral — no wearable, no penalty
_SLEEP_MIN: float = 0.0
_SLEEP_MAX: float = 1.0


class SleepQualityStore:
    """
    Stores the most recent sleep quality score reported by Wire 2
    (IMU sleep detection) or manual declaration from the HUD.

    Score semantics:
      0.0  — no sleep / severely disrupted
      0.5  — neutral / unknown (default)
      1.0  — excellent sleep

    D6Engine uses this to modulate recovery recommendations:
    low score + long session → higher REST urgency.
    """

    def __init__(self) -> None:
        self._score: float = _SLEEP_DEFAULT
        self._reported_at: Optional[float] = None

    def report(self, score: float, timestamp: Optional[float] = None) -> None:
        """Record a new sleep quality score. Clamps to [0, 1]."""
        self._score = round(min(_SLEEP_MAX, max(_SLEEP_MIN, float(score))), 3)
        self._reported_at = timestamp or time.time()

    @property
    def score(self) -> float:
        """Current sleep quality score. Returns default (0.5) if never reported."""
        return self._score

    @property
    def reported_at(self) -> Optional[float]:
        """Unix timestamp of last report, or None if never reported."""
        return self._reported_at

    @property
    def has_data(self) -> bool:
        """True if a score has been explicitly reported (not just the default)."""
        return self._reported_at is not None

    def reset(self) -> None:
        """Reset to default neutral score. Used at session start."""
        self._score = _SLEEP_DEFAULT
        self._reported_at = None


# ---------------------------------------------------------------------------
# RestEvent
# ---------------------------------------------------------------------------

@dataclass
class RestEvent:
    """A single declared rest period."""
    declared_at: float = field(default_factory=time.time)
    duration_minutes: Optional[float] = None   # None = open-ended / spot break
    label: str = "break"                       # 'break', 'nap', 'meditation', etc.


# ---------------------------------------------------------------------------
# SessionClock
# ---------------------------------------------------------------------------

class SessionClock:
    """
    Wall-clock session tracker.

    Tracks:
      - Session start time (UTC unix)
      - Elapsed session hours
      - Time since last declared rest (hours)
      - Full rest event history for the session

    Wire 4 reads elapsed_hours and time_since_rest_hours on every
    D6Engine evaluation cycle to populate EngineProbes.
    """

    def __init__(self) -> None:
        self._start_time: Optional[float] = None
        self._stop_time: Optional[float] = None
        self._rest_events: List[RestEvent] = []
        self._running: bool = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self, at: Optional[float] = None) -> None:
        """
        Start the session clock.
        Idempotent — safe to call multiple times; re-start resets the clock.

        Parameters
        ----------
        at:
            Optional unix timestamp to use as session start.
            Defaults to time.time(). Useful for testing.
        """
        self._start_time = at if at is not None else time.time()
        self._stop_time = None
        self._rest_events = []
        self._running = True

    def stop(self, at: Optional[float] = None) -> None:
        """Stop the session clock. Freezes elapsed_hours."""
        self._stop_time = at if at is not None else time.time()
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    # ------------------------------------------------------------------
    # Rest tracking
    # ------------------------------------------------------------------

    def declare_rest(
        self,
        label: str = "break",
        duration_minutes: Optional[float] = None,
        at: Optional[float] = None,
    ) -> RestEvent:
        """
        Declare a rest event. Called from HUD when user takes a break.

        Parameters
        ----------
        label:            'break', 'nap', 'meditation', 'walk', etc.
        duration_minutes: Planned duration in minutes (None = unspecified).
        at:               Unix timestamp override (for testing).

        Returns the RestEvent for logging / confirmation.
        """
        event = RestEvent(
            declared_at=at if at is not None else time.time(),
            duration_minutes=duration_minutes,
            label=label,
        )
        self._rest_events.append(event)
        return event

    @property
    def rest_events(self) -> List[RestEvent]:
        """All rest events declared in this session (read-only copy)."""
        return list(self._rest_events)

    @property
    def last_rest_at(self) -> Optional[float]:
        """Unix timestamp of the most recent rest event, or None."""
        if not self._rest_events:
            return None
        return self._rest_events[-1].declared_at

    # ------------------------------------------------------------------
    # Core probe values
    # ------------------------------------------------------------------

    def elapsed_hours(self, now: Optional[float] = None) -> float:
        """
        Elapsed session time in hours.

        Returns 0.0 if clock has not been started.
        Uses stop_time if clock has been stopped (frozen).
        """
        if self._start_time is None:
            return 0.0
        reference = self._stop_time if self._stop_time is not None else (now or time.time())
        return round((reference - self._start_time) / 3600.0, 4)

    def time_since_rest_hours(self, now: Optional[float] = None) -> float:
        """
        Hours elapsed since the most recent declared rest event.

        Returns elapsed_hours() if no rest has been declared
        (entire session counts as unbroken work time).
        This is the conservative interpretation: GAIA assumes
        you have been working since session start until proven otherwise.
        """
        reference = now or time.time()
        if not self._rest_events:
            return self.elapsed_hours(now=reference)
        last = self._rest_events[-1].declared_at
        return round((reference - last) / 3600.0, 4)

    def get_status(self) -> dict:
        """Snapshot dict for observability / admin endpoints."""
        return {
            "running": self._running,
            "start_time": self._start_time,
            "elapsed_hours": self.elapsed_hours(),
            "time_since_rest_hours": self.time_since_rest_hours(),
            "rest_event_count": len(self._rest_events),
            "last_rest_at": self.last_rest_at,
        }


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

_session_clock_instance: Optional[SessionClock] = None
_sleep_store_instance: Optional[SleepQualityStore] = None


def get_session_clock() -> SessionClock:
    """Return the module-level SessionClock singleton."""
    global _session_clock_instance
    if _session_clock_instance is None:
        _session_clock_instance = SessionClock()
    return _session_clock_instance


def get_sleep_store() -> SleepQualityStore:
    """Return the module-level SleepQualityStore singleton."""
    global _sleep_store_instance
    if _sleep_store_instance is None:
        _sleep_store_instance = SleepQualityStore()
    return _sleep_store_instance

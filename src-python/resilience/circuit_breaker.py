"""Issue #187 — CircuitBreaker: CLOSED → OPEN → COOLING → CLOSED state machine per skill.

Canon C30: No silent failures — circuit state is always surfaced.
Canon C34: Presence — GAIA stays functional even when skills fail.

State machine
-------------
  CLOSED   → failure rate ≥ threshold → OPEN
  OPEN     → recovery probe due       → HALF_OPEN
  HALF_OPEN → success                 → CLOSED
  HALF_OPEN → failure                 → OPEN
  OPEN     → force_close()           → COOLING
  COOLING  → tick() until counter=0  → CLOSED
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine


class CircuitState(str, Enum):
    CLOSED    = "CLOSED"     # Normal operation
    OPEN      = "OPEN"       # Failing fast — downstream protected
    HALF_OPEN = "HALF_OPEN" # Probing for recovery
    COOLING   = "COOLING"   # Forced cooldown before returning to CLOSED


class CircuitOpenError(Exception):
    """Raised when a call is attempted against an OPEN circuit."""
    def __init__(self, skill_id: str):
        super().__init__(f"Circuit breaker OPEN for skill '{skill_id}' — failing fast")
        self.skill_id = skill_id


@dataclass
class CircuitBreaker:
    skill_id               : str
    failure_rate_threshold : float = 0.5   # 50% failure rate triggers OPEN
    window_seconds         : int   = 60    # Rolling window for failure rate
    open_duration_seconds  : int   = 30   # Time before probing recovery
    min_calls_in_window    : int   = 4    # Minimum calls before rate is evaluated
    cooling_ticks          : int   = 5    # tick() calls needed to leave COOLING

    # Runtime state
    state                      : CircuitState = field(default=CircuitState.CLOSED, init=False)
    _call_times                : list[float]  = field(default_factory=list, init=False, repr=False)
    _failure_times             : list[float]  = field(default_factory=list, init=False, repr=False)
    _opened_at                 : float | None = field(default=None, init=False, repr=False)
    _half_open_probe_in_progress: bool        = field(default=False, init=False, repr=False)
    _cooling_counter           : int          = field(default=0, init=False, repr=False)

    def _prune_window(self) -> None:
        cutoff = time.monotonic() - self.window_seconds
        self._call_times    = [t for t in self._call_times    if t > cutoff]
        self._failure_times = [t for t in self._failure_times if t > cutoff]

    def _failure_rate(self) -> float:
        self._prune_window()
        if len(self._call_times) < self.min_calls_in_window:
            return 0.0
        return len(self._failure_times) / len(self._call_times)

    def _probe_recovery_due(self) -> bool:
        if self._opened_at is None:
            return False
        return (time.monotonic() - self._opened_at) >= self.open_duration_seconds

    def _on_success(self) -> None:
        now = time.monotonic()
        self._call_times.append(now)
        if self.state == CircuitState.HALF_OPEN:
            self.state                         = CircuitState.CLOSED
            self._opened_at                    = None
            self._half_open_probe_in_progress  = False

    def _on_failure(self, error: Exception) -> None:
        now = time.monotonic()
        self._call_times.append(now)
        self._failure_times.append(now)
        if self.state == CircuitState.HALF_OPEN:
            self.state     = CircuitState.OPEN
            self._opened_at = time.monotonic()
            self._half_open_probe_in_progress = False
            return
        if self._failure_rate() >= self.failure_rate_threshold:
            self.state      = CircuitState.OPEN
            self._opened_at = time.monotonic()

    def tick(self) -> CircuitState:
        """Advance the COOLING countdown by one step.

        Call periodically (e.g. once per second) while the breaker is in
        COOLING state. When the countdown reaches zero the breaker
        transitions to CLOSED automatically.

        Returns the current state after the tick.
        """
        if self.state == CircuitState.COOLING:
            self._cooling_counter -= 1
            if self._cooling_counter <= 0:
                self._cooling_counter = 0
                self.state = CircuitState.CLOSED
        return self.state

    def force_close(self) -> None:
        """Manually force the breaker into COOLING (then CLOSED after ticks)."""
        self.state            = CircuitState.COOLING
        self._cooling_counter = self.cooling_ticks
        self._opened_at       = None

    async def call(
        self,
        fn: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute fn through the circuit breaker.

        Raises CircuitOpenError if OPEN and recovery probe is not yet due.
        Propagates the underlying exception on failure (after recording it).
        """
        if self.state == CircuitState.OPEN:
            if self._probe_recovery_due() and not self._half_open_probe_in_progress:
                self.state                        = CircuitState.HALF_OPEN
                self._half_open_probe_in_progress = True
            else:
                raise CircuitOpenError(self.skill_id)

        try:
            result = await fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception as exc:
            self._on_failure(exc)
            raise

    @property
    def health(self) -> dict[str, Any]:
        self._prune_window()
        return {
            "skill_id"               : self.skill_id,
            "state"                  : self.state.value,
            "failure_rate"           : round(self._failure_rate(), 3),
            "total_calls_in_window"  : len(self._call_times),
            "failures_in_window"     : len(self._failure_times),
            "opened_at"              : self._opened_at,
            "cooling_counter"        : self._cooling_counter,
        }

"""Cumulative emotional trajectory model and cross-session risk synthesis.

The core insight: a user passing each individual session's safety check can
still be in serious crisis if their overall trajectory is downward. This module
maintains a rolling window of per-session risk snapshots and synthesises a
cross-session risk score from:

  1. The current session's peak signal severity
  2. The trajectory slope (linear regression over the rolling window)
  3. The number of consecutive sessions in distress
  4. The 72-hour peak risk (acute escalation detector)

⚠️  Trajectory slope is a heuristic indicator, not a clinical diagnosis.
    GAIA must frame all crisis responses with appropriate epistemic humility.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from .types import CrisisSignal, RiskLevel, SignalClass

_RISK_NUMERIC = {
    RiskLevel.NONE:     0.0,
    RiskLevel.LOW:      1.0,
    RiskLevel.MODERATE: 2.0,
    RiskLevel.HIGH:     3.0,
    RiskLevel.CRITICAL: 4.0,
}

_NUMERIC_RISK = {v: k for k, v in _RISK_NUMERIC.items()}


def _risk_to_float(r: RiskLevel) -> float:
    return _RISK_NUMERIC[r]


def _float_to_risk(v: float) -> RiskLevel:
    clamped = max(0.0, min(4.0, round(v)))
    return _NUMERIC_RISK.get(clamped, RiskLevel.HIGH)


@dataclass
class SessionRiskRecord:
    """Per-session risk summary stored in the rolling window."""
    session_id:    str
    peak_risk:     RiskLevel
    signal_count:  int
    has_explicit:  bool
    has_masked:    bool
    recorded_at:   datetime = field(default_factory=datetime.utcnow)


class TrajectoryModel:
    """Rolling window trajectory model for one principal.

    Window size defaults to 14 sessions (approximately 2 weeks of daily use).
    The model is purely in-memory; persistence is the responsibility of
    CrisisEngine (which writes snapshots to SovereignMemory).
    """

    def __init__(self, window_size: int = 14):
        self._window: deque[SessionRiskRecord] = deque(maxlen=window_size)
        self._window_size = window_size

    def record_session(self, record: SessionRiskRecord) -> None:
        """Add a session risk record to the rolling window."""
        self._window.append(record)

    def trajectory_slope(self) -> float:
        """Linear regression slope over the risk window.

        Returns:
            Positive = worsening trend
            Negative = improving trend
            0.0      = insufficient data or stable
        """
        points = [_risk_to_float(r.peak_risk) for r in self._window]
        n = len(points)
        if n < 3:
            return 0.0
        xs = list(range(n))
        x_mean = sum(xs) / n
        y_mean = sum(points) / n
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, points))
        den = sum((x - x_mean) ** 2 for x in xs)
        return (num / den) if den > 0 else 0.0

    def consecutive_distress_sessions(self) -> int:
        """Count trailing sessions with any risk signal (RiskLevel > NONE)."""
        count = 0
        for record in reversed(self._window):
            if record.peak_risk > RiskLevel.NONE:
                count += 1
            else:
                break
        return count

    def peak_risk_within(self, hours: int = 72) -> RiskLevel:
        """Return the highest risk level seen in the past N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        peak = RiskLevel.NONE
        for record in self._window:
            if record.recorded_at >= cutoff and record.peak_risk > peak:
                peak = record.peak_risk
        return peak

    def synthesise_risk(
        self,
        current_signals: list[CrisisSignal],
    ) -> RiskLevel:
        """Synthesise a final risk level from current signals + trajectory.

        Algorithm:
          1. Start with the highest current-session signal severity.
          2. If trajectory slope > 0.4 (worsening trend), elevate by one level.
          3. If 5+ consecutive distress sessions, elevate by one level.
          4. Never downgrade an EXPLICIT CRITICAL or ACUTE signal.
          5. Cap at CRITICAL.
        """
        if not current_signals:
            # No signals this session — still check trajectory
            base = RiskLevel.NONE
        else:
            base = max(current_signals, key=lambda s: _risk_to_float(s.risk_level)).risk_level

        # Trajectory elevation
        slope = self.trajectory_slope()
        if slope > 0.4 and base < RiskLevel.HIGH:
            base = _float_to_risk(_risk_to_float(base) + 1)

        # Consecutive sessions elevation
        consecutive = self.consecutive_distress_sessions()
        if consecutive >= 5 and base < RiskLevel.CRITICAL:
            base = _float_to_risk(_risk_to_float(base) + 1)

        # Explicit/Acute signals are never downgraded
        for sig in current_signals:
            if sig.signal_class in (SignalClass.EXPLICIT, SignalClass.ACUTE):
                if sig.risk_level > base:
                    base = sig.risk_level

        return base

    def load_from_records(self, records: list[SessionRiskRecord]) -> None:
        """Restore window from persisted records (e.g. on engine cold-start)."""
        self._window.clear()
        for r in sorted(records, key=lambda x: x.recorded_at)[- self._window_size:]:
            self._window.append(r)

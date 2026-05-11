"""
shadow_engine/intensity.py
Shadow intensity computation.

Intensity ramps from 0.6 (day 0) to 1.0 (day 14+) so transient
emotional states never trigger full shadow activation immediately.
"""

from __future__ import annotations

_INTENSITY_FLOOR:   float = 0.6
_INTENSITY_RAMP_DAYS: int = 14


def compute_intensity_modifier(days_active: int) -> float:
    """
    Returns the intensity modifier in [0.6, 1.0].

    modifier = min(1.0, 0.6 + 0.4 * (days_active / 14))
    """
    ramp = days_active / _INTENSITY_RAMP_DAYS
    return min(1.0, _INTENSITY_FLOOR + (1.0 - _INTENSITY_FLOOR) * ramp)


def compute_shadow_intensity(active_score: float, days_active: int) -> float:
    """
    Final shadow intensity = active_score × intensity_modifier, clamped [0, 1].
    """
    modifier = compute_intensity_modifier(days_active)
    return max(0.0, min(1.0, active_score * modifier))

# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/orange/transparency.py
=====================================
Open-field, non-blocking signals for the ORANGE (Citrinitas) spectral layer.
Transparency layer: what can be seen by any observer, no filtering.

Functions
---------
detect_citrinitas_state     — Is the signal in active Citrinitas phase?
emit_sentinel_alert         — Broadcast SENTINEL alert at given level.
classify_urgency            — Map a numeric intensity to an urgency label.
get_ui_state                — Retrieve the UI state dict for a named state.
is_solar_completion_signal  — Is this signal a solar completion marker?
"""

from __future__ import annotations
from typing import Any

from .constants import (
    ORANGE_HEX,
    ALCHEMICAL_PHASE,
    SENTINEL_LEVEL_HEX,
    SENTINEL_LEVEL_LABEL,
    UI_STATES,
    WAVELENGTH_RANGE,
)


def detect_citrinitas_state(signal: dict[str, Any]) -> bool:
    """
    Return True if *signal* is in active Citrinitas (ORANGE) phase.

    A signal qualifies when:
      - signal["phase"] equals ALCHEMICAL_PHASE (case-insensitive), OR
      - signal["hex"] is any value in ORANGE_HEX, OR
      - signal["wavelength"] falls within WAVELENGTH_RANGE (inclusive).
    """
    if not isinstance(signal, dict):
        return False

    phase = signal.get("phase", "")
    if isinstance(phase, str) and phase.strip().lower() == ALCHEMICAL_PHASE.lower():
        return True

    hex_val = signal.get("hex", "")
    if hex_val in ORANGE_HEX.values():
        return True

    wl = signal.get("wavelength")
    if isinstance(wl, (int, float)):
        lo, hi = WAVELENGTH_RANGE
        if lo <= wl <= hi:
            return True

    return False


def emit_sentinel_alert(level: int, context: str = "") -> dict[str, Any]:
    """
    Emit a SENTINEL alert dict for the given *level* (1-3).

    Returns a standardised alert envelope. Unknown levels default to level 1.
    """
    safe_level = level if level in SENTINEL_LEVEL_HEX else 1
    return {
        "module":  "spectral.orange",
        "phase":   ALCHEMICAL_PHASE,
        "level":   safe_level,
        "label":   SENTINEL_LEVEL_LABEL[safe_level],
        "hex":     SENTINEL_LEVEL_HEX[safe_level],
        "context": context,
        "interrupt_flag": False,
    }


def classify_urgency(intensity: float) -> str:
    """
    Map a normalised intensity [0.0, 1.0] to an urgency label.

    Bands
    -----
    [0.00, 0.33) → "low"
    [0.33, 0.66) → "moderate"
    [0.66, 1.00] → "high"
    """
    if intensity < 0.33:
        return "low"
    if intensity < 0.66:
        return "moderate"
    return "high"


def get_ui_state(state_name: str) -> dict[str, Any]:
    """
    Retrieve the UI state dict for *state_name*.
    Returns an empty dict if the state is not registered.
    """
    return UI_STATES.get(state_name, {})


def is_solar_completion_signal(signal: dict[str, Any]) -> bool:
    """
    Return True if *signal* carries the Amber completion marker.

    Conditions (any one sufficient):
      - signal["hex"] == ORANGE_HEX["AMBER"]
      - signal["completion"] is True AND detect_citrinitas_state(signal)
    """
    if not isinstance(signal, dict):
        return False

    if signal.get("hex") == ORANGE_HEX["AMBER"]:
        return True

    if signal.get("completion") is True and detect_citrinitas_state(signal):
        return True

    return False

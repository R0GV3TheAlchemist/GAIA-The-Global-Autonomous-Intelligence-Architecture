# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/yellow/transparency.py
=====================================
Open-field, non-blocking signals for the YELLOW (Xanthosis) spectral layer.
"""

from __future__ import annotations
from typing import Any

from .constants import (
    YELLOW_HEX, ALCHEMICAL_PHASE, SENTINEL_LEVEL_HEX,
    SENTINEL_LEVEL_LABEL, UI_STATES, WAVELENGTH_RANGE,
)


def detect_xanthosis_state(signal: dict[str, Any]) -> bool:
    if not isinstance(signal, dict):
        return False
    phase = signal.get("phase", "")
    if isinstance(phase, str) and phase.strip().lower() == ALCHEMICAL_PHASE.lower():
        return True
    if signal.get("hex") in YELLOW_HEX.values():
        return True
    wl = signal.get("wavelength")
    if isinstance(wl, (int, float)):
        lo, hi = WAVELENGTH_RANGE
        if lo <= wl <= hi:
            return True
    return False


def emit_sentinel_alert(level: int, context: str = "") -> dict[str, Any]:
    safe_level = level if level in SENTINEL_LEVEL_HEX else 1
    return {
        "module":  "spectral.yellow",
        "phase":   ALCHEMICAL_PHASE,
        "level":   safe_level,
        "label":   SENTINEL_LEVEL_LABEL[safe_level],
        "hex":     SENTINEL_LEVEL_HEX[safe_level],
        "context": context,
        "interrupt_flag": False,
    }


def classify_urgency(intensity: float) -> str:
    if intensity < 0.33:
        return "low"
    if intensity < 0.66:
        return "moderate"
    return "high"


def get_ui_state(state_name: str) -> dict[str, Any]:
    return UI_STATES.get(state_name, {})


def is_illumination_signal(signal: dict[str, Any]) -> bool:
    if not isinstance(signal, dict):
        return False
    if signal.get("hex") == YELLOW_HEX["AMBER"]:
        return True
    if signal.get("completion") is True and detect_xanthosis_state(signal):
        return True
    return False

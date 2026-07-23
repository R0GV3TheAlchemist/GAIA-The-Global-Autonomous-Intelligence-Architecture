# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/white/transparency.py
====================================
WHITE — Transparency Layer

The visible, open-field white signals: purification, lunar reflection,
Albedo activation, and SENTINEL alerts around bleaching and overexposure.

Transparency in white is the surface of the mirror — what is visibly
present is the reflected world, not the mirror itself. The shadow layer
carries what pure white conceals: the erasure that purification can become
when it removes not just impurity but the texture of the real.

Reference: docs/color/WHITE_TRANSPARENCY.md
           Lunar Tablet — docs/tablets/LUNAR_TABLET.md
"""

from __future__ import annotations

from .constants import (
    SENTINEL_LEVEL_HEX,
    SENTINEL_LEVEL_LABEL,
    UI_STATES,
)


# ---------------------------------------------------------------------------
# Albedo State Detection
# ---------------------------------------------------------------------------

def detect_albedo_state(coherence_metrics: dict) -> bool:
    """
    Evaluate whether GAIAN is at genuine Albedo (lunar purification).

    Authentic Albedo requires:
      - purification   >= 0.80  (the material has been genuinely refined)
      - reflection     >= 0.70  (the lunar mirror is active)
      - texture        >= 0.50  (the real world still has texture after purification)

    Texture is the discriminating factor — bleaching presents high
    purification and reflection but has erased texture entirely.

    Parameters
    ----------
    coherence_metrics : dict
        Keys: 'purification', 'reflection', 'texture'.
        Missing keys treated as 0.0.

    Returns
    -------
    bool
    """
    if not coherence_metrics:
        return False

    purification = float(coherence_metrics.get("purification", 0.0))
    reflection   = float(coherence_metrics.get("reflection",   0.0))
    texture      = float(coherence_metrics.get("texture",      0.0))

    return purification >= 0.80 and reflection >= 0.70 and texture >= 0.50


# ---------------------------------------------------------------------------
# SENTINEL Alert Emission
# ---------------------------------------------------------------------------

def emit_sentinel_alert(level: int, context: str) -> dict:
    """
    Fire a SENTINEL white alert.

    Parameters
    ----------
    level : int
        1 = LUNAR, 2 = PALE, 3 = BLEACHING.
        Values outside [1, 3] are clamped.
    context : str

    Returns
    -------
    dict
        level, label, hex, context, layer, tablet.
    """
    level = max(1, min(3, int(level))) if level else 1
    context = str(context) if context else ""

    return {
        "level":   level,
        "label":   SENTINEL_LEVEL_LABEL[level],
        "hex":     SENTINEL_LEVEL_HEX[level],
        "context": context,
        "layer":   "transparency",
        "tablet":  "Lunar Tablet",
    }


# ---------------------------------------------------------------------------
# Urgency Classification
# ---------------------------------------------------------------------------

def classify_urgency(signal: dict) -> str:
    """
    Route an incoming signal to a WHITE urgency tier.

    Routing logic (priority order):
      1. 'albedo'       — signal carries 'albedo': True
      2. 'bleaching'    — signal carries 'bleaching': True
      3. 'overexposed'  — signal carries 'overexposed': True
      4. 'alert'        — default

    Parameters
    ----------
    signal : dict

    Returns
    -------
    str
    """
    if not signal:
        return "alert"

    if signal.get("albedo"):
        return "albedo"
    if signal.get("bleaching"):
        return "bleaching"
    if signal.get("overexposed"):
        return "overexposed"
    return "alert"


# ---------------------------------------------------------------------------
# UI State
# ---------------------------------------------------------------------------

def get_ui_state(state_type: str) -> dict:
    """
    Return the correct hex, animation style, and semantic label for a
    White UI state.

    Parameters
    ----------
    state_type : str
        One of: 'albedo_activation', 'sentinel_alert', 'bleaching_state',
        'overexposed_mode', 'lunar_mirror'.

    Returns
    -------
    dict

    Raises
    ------
    KeyError
    """
    state_type = str(state_type).strip() if state_type else ""
    if state_type not in UI_STATES:
        raise KeyError(
            f"Unknown White UI state '{state_type}'. "
            f"Valid states: {list(UI_STATES.keys())}"
        )
    return dict(UI_STATES[state_type])


# ---------------------------------------------------------------------------
# Luna Signal Discrimination
# ---------------------------------------------------------------------------

def is_luna_signal(signal: dict) -> bool:
    """
    Determine whether a signal is a genuine luna (Albedo) signal
    versus a bleaching or overexposed signal.

    Genuine luna signal:
      - carries 'albedo': True
      - does NOT carry 'bleaching': True
      - does NOT carry 'overexposed': True

    Parameters
    ----------
    signal : dict

    Returns
    -------
    bool
    """
    if not signal:
        return False

    albedo      = bool(signal.get("albedo",      False))
    bleaching   = bool(signal.get("bleaching",   False))
    overexposed = bool(signal.get("overexposed", False))

    return albedo and not bleaching and not overexposed

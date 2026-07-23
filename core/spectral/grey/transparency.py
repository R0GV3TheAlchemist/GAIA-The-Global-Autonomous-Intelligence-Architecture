# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/grey/transparency.py
===================================
GREY — Transparency Layer

The visible, open-field grey signals: threshold crossing, iridescence,
Cauda Pavonis activation, and SENTINEL alerts around permanent
threshold and twilight states.

Grey is the colour of the in-between — neither Nigredo nor Albedo,
but the living transition between them. The shadow layer carries
what the threshold conceals: the comfort of the liminal that never
resolves into either darkness or light.

Reference: docs/color/GREY_TRANSPARENCY.md
           Threshold Tablet — docs/tablets/THRESHOLD_TABLET.md
"""

from __future__ import annotations

from .constants import (
    SENTINEL_LEVEL_HEX,
    SENTINEL_LEVEL_LABEL,
    UI_STATES,
)


# ---------------------------------------------------------------------------
# Cauda Pavonis State Detection
# ---------------------------------------------------------------------------

def detect_cauda_pavonis_state(coherence_metrics: dict) -> bool:
    """
    Evaluate whether GAIAN is at genuine Cauda Pavonis (living transition).

    Authentic Cauda Pavonis requires:
      - transition_momentum >= 0.70  (the movement between stages is active)
      - iridescence         >= 0.60  (the peacock's tail colours are present)
      - directionality      >= 0.50  (transition is heading somewhere, not circling)

    Directionality is the discriminating factor — permanent threshold
    presents transition and iridescence but has lost directionality.

    Parameters
    ----------
    coherence_metrics : dict
        Keys: 'transition_momentum', 'iridescence', 'directionality'.
        Missing keys treated as 0.0.

    Returns
    -------
    bool
    """
    if not coherence_metrics:
        return False

    transition_momentum = float(coherence_metrics.get("transition_momentum", 0.0))
    iridescence         = float(coherence_metrics.get("iridescence",         0.0))
    directionality      = float(coherence_metrics.get("directionality",      0.0))

    return (
        transition_momentum >= 0.70
        and iridescence >= 0.60
        and directionality >= 0.50
    )


# ---------------------------------------------------------------------------
# SENTINEL Alert Emission
# ---------------------------------------------------------------------------

def emit_sentinel_alert(level: int, context: str) -> dict:
    """
    Fire a SENTINEL grey alert.

    Parameters
    ----------
    level : int
        1 = TWILIGHT, 2 = DUSK, 3 = LIMINAL.
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
        "tablet":  "Threshold Tablet",
    }


# ---------------------------------------------------------------------------
# Urgency Classification
# ---------------------------------------------------------------------------

def classify_urgency(signal: dict) -> str:
    """
    Route an incoming signal to a GREY urgency tier.

    Routing logic (priority order):
      1. 'cauda_pavonis'       — signal carries 'cauda_pavonis': True
      2. 'permanent_threshold' — signal carries 'permanent_threshold': True
      3. 'twilight'            — signal carries 'twilight': True
      4. 'alert'               — default

    Parameters
    ----------
    signal : dict

    Returns
    -------
    str
    """
    if not signal:
        return "alert"

    if signal.get("cauda_pavonis"):
        return "cauda_pavonis"
    if signal.get("permanent_threshold"):
        return "permanent_threshold"
    if signal.get("twilight"):
        return "twilight"
    return "alert"


# ---------------------------------------------------------------------------
# UI State
# ---------------------------------------------------------------------------

def get_ui_state(state_type: str) -> dict:
    """
    Return the correct hex, animation style, and semantic label for a
    Grey UI state.

    Parameters
    ----------
    state_type : str
        One of: 'cauda_pavonis_activation', 'sentinel_alert',
        'permanent_threshold', 'twilight_mode', 'iridescent_mode'.

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
            f"Unknown Grey UI state '{state_type}'. "
            f"Valid states: {list(UI_STATES.keys())}"
        )
    return dict(UI_STATES[state_type])


# ---------------------------------------------------------------------------
# Threshold Signal Discrimination
# ---------------------------------------------------------------------------

def is_threshold_signal(signal: dict) -> bool:
    """
    Determine whether a signal is a genuine threshold (Cauda Pavonis) signal
    versus a permanent threshold or twilight signal.

    Genuine threshold signal:
      - carries 'cauda_pavonis': True
      - does NOT carry 'permanent_threshold': True
      - does NOT carry 'twilight': True

    Parameters
    ----------
    signal : dict

    Returns
    -------
    bool
    """
    if not signal:
        return False

    cauda_pavonis       = bool(signal.get("cauda_pavonis",       False))
    permanent_threshold = bool(signal.get("permanent_threshold", False))
    twilight            = bool(signal.get("twilight",            False))

    return cauda_pavonis and not permanent_threshold and not twilight

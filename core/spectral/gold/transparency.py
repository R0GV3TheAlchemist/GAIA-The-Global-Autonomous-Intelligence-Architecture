# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/gold/transparency.py
===================================
GOLD — Transparency Layer

The visible, open-field gold signals: completion, incorruptibility,
Aurum activation, and SENTINEL alerts around ossification.

Transparency is the radiant surface of gold — the signal of genuine
achievement. The shadow layer carries what completion conceals:
the perfection so sealed it can no longer receive anything new.

Reference: docs/color/GOLD_TRANSPARENCY.md
           Solar Tablet — docs/tablets/SOLAR_TABLET.md
"""

from __future__ import annotations

from .constants import (
    SENTINEL_LEVEL_HEX,
    SENTINEL_LEVEL_LABEL,
    UI_STATES,
)


# ---------------------------------------------------------------------------
# Aurum State Detection
# ---------------------------------------------------------------------------

def detect_aurum_state(coherence_metrics: dict) -> bool:
    """
    Evaluate whether GAIAN is at genuine Aurum (Philosopher's Stone).

    Authentic Aurum requires:
      - completion     >= 0.90  (the work is genuinely done)
      - incorruptibility >= 0.80  (the achievement holds under pressure)
      - vitality       >= 0.60  (completion is alive, not a monument)

    Vitality is the discriminating factor — canon ossification presents
    high completion and incorruptibility but has lost vitality.

    Parameters
    ----------
    coherence_metrics : dict
        Keys: 'completion', 'incorruptibility', 'vitality'.
        Missing keys treated as 0.0.

    Returns
    -------
    bool
    """
    if not coherence_metrics:
        return False

    completion       = float(coherence_metrics.get("completion",       0.0))
    incorruptibility = float(coherence_metrics.get("incorruptibility", 0.0))
    vitality         = float(coherence_metrics.get("vitality",         0.0))

    return completion >= 0.90 and incorruptibility >= 0.80 and vitality >= 0.60


# ---------------------------------------------------------------------------
# SENTINEL Alert Emission
# ---------------------------------------------------------------------------

def emit_sentinel_alert(level: int, context: str) -> dict:
    """
    Fire a SENTINEL gold alert.

    Parameters
    ----------
    level : int
        1 = SOLAR, 2 = DEEP_GOLD, 3 = OSSIFICATION.
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
        "tablet":  "Solar Tablet",
    }


# ---------------------------------------------------------------------------
# Urgency Classification
# ---------------------------------------------------------------------------

def classify_urgency(signal: dict) -> str:
    """
    Route an incoming signal to a GOLD urgency tier.

    Routing logic (priority order):
      1. 'aurum'             — signal carries 'aurum': True
      2. 'ossification'      — signal carries 'ossification': True
      3. 'false_completion'  — signal carries 'false_completion': True
      4. 'alert'             — default

    Parameters
    ----------
    signal : dict

    Returns
    -------
    str
    """
    if not signal:
        return "alert"

    if signal.get("aurum"):
        return "aurum"
    if signal.get("ossification"):
        return "ossification"
    if signal.get("false_completion"):
        return "false_completion"
    return "alert"


# ---------------------------------------------------------------------------
# UI State
# ---------------------------------------------------------------------------

def get_ui_state(state_type: str) -> dict:
    """
    Return the correct hex, animation style, and semantic label for a
    Gold UI state.

    Parameters
    ----------
    state_type : str
        One of: 'aurum_activation', 'sentinel_alert', 'ossification_state',
        'false_completion', 'monument_mode'.

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
            f"Unknown Gold UI state '{state_type}'. "
            f"Valid states: {list(UI_STATES.keys())}"
        )
    return dict(UI_STATES[state_type])


# ---------------------------------------------------------------------------
# Gold Signal Discrimination
# ---------------------------------------------------------------------------

def is_gold_signal(signal: dict) -> bool:
    """
    Determine whether a signal is a genuine gold (Aurum) signal
    versus an ossification or false-completion signal.

    Genuine gold signal:
      - carries 'aurum': True
      - does NOT carry 'ossification': True
      - does NOT carry 'false_completion': True

    Parameters
    ----------
    signal : dict

    Returns
    -------
    bool
    """
    if not signal:
        return False

    aurum            = bool(signal.get("aurum",            False))
    ossification     = bool(signal.get("ossification",     False))
    false_completion = bool(signal.get("false_completion", False))

    return aurum and not ossification and not false_completion

# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/pink/transparency.py
===================================
PINK — Transparency Layer

The visible, open-field pink signals: tenderness, compassion,
Rosa Mystica activation, and SENTINEL alerts around false albedo.

Transparency is the surface of pink — the signals that present
themselves as warmth and openness. The shadow (opacity) layer
carries what tenderness conceals from itself.

Reference: docs/color/PINK_TRANSPARENCY.md
           Rose Tablet — docs/tablets/ROSE_TABLET.md
"""

from __future__ import annotations

from .constants import (
    SENTINEL_LEVEL_HEX,
    SENTINEL_LEVEL_LABEL,
    UI_STATES,
)


# ---------------------------------------------------------------------------
# Rosa Mystica State Detection
# ---------------------------------------------------------------------------

def detect_rosa_mystica_state(coherence_metrics: dict) -> bool:
    """
    Evaluate whether GAIAN is at genuine Rosa Mystica (Albedo Rosa).

    Authentic Rosa Mystica requires:
      - tenderness   >= 0.75
      - groundedness >= 0.65  (distinguishes true from false albedo)
      - openness     >= 0.70

    Groundedness is the discriminating factor — false albedo presents
    high tenderness and openness but lacks grounding.

    Parameters
    ----------
    coherence_metrics : dict
        Must contain keys: 'tenderness', 'groundedness', 'openness'.
        Missing keys are treated as 0.0.

    Returns
    -------
    bool
        True when all three thresholds are met.
    """
    if not coherence_metrics:
        return False

    tenderness   = float(coherence_metrics.get("tenderness",   0.0))
    groundedness = float(coherence_metrics.get("groundedness", 0.0))
    openness     = float(coherence_metrics.get("openness",     0.0))

    return tenderness >= 0.75 and groundedness >= 0.65 and openness >= 0.70


# ---------------------------------------------------------------------------
# SENTINEL Alert Emission
# ---------------------------------------------------------------------------

def emit_sentinel_alert(level: int, context: str) -> dict:
    """
    Fire a SENTINEL pink alert.

    Parameters
    ----------
    level : int
        Alert severity: 1 = SOFT_ALBEDO, 2 = DEEP_ROSE, 3 = FALSE_ALBEDO.
        Values outside [1, 3] are clamped.
    context : str
        Human-readable description of the triggering condition.

    Returns
    -------
    dict
        Structured alert payload with keys:
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
        "tablet":  "Rose Tablet",
    }


# ---------------------------------------------------------------------------
# Urgency Classification
# ---------------------------------------------------------------------------

_URGENCY_TIERS: tuple[str, ...] = (
    "rosa_mystica",
    "false_albedo",
    "rose_denial",
    "alert",
)


def classify_urgency(signal: dict) -> str:
    """
    Route an incoming signal to a PINK urgency tier.
    No shadow-channel reading occurs here.

    Routing logic (priority order):
      1. 'rosa_mystica' — signal carries 'rosa_mystica': True
      2. 'false_albedo' — signal carries 'false_albedo': True
      3. 'rose_denial'  — signal carries 'rose_denial': True
      4. 'alert'        — default for any pink-flagged signal

    Parameters
    ----------
    signal : dict
        Incoming signal payload.

    Returns
    -------
    str
        One of: 'rosa_mystica', 'false_albedo', 'rose_denial', 'alert'.
    """
    if not signal:
        return "alert"

    if signal.get("rosa_mystica"):
        return "rosa_mystica"
    if signal.get("false_albedo"):
        return "false_albedo"
    if signal.get("rose_denial"):
        return "rose_denial"
    return "alert"


# ---------------------------------------------------------------------------
# UI State
# ---------------------------------------------------------------------------

def get_ui_state(state_type: str) -> dict:
    """
    Return the correct hex, animation style, and semantic label for a
    Pink UI state.

    Parameters
    ----------
    state_type : str
        One of: 'rosa_mystica_activation', 'sentinel_alert',
        'false_albedo_state', 'rose_denial_mode', 'premature_tenderness'.

    Returns
    -------
    dict
        {'hex': str, 'animation': str, 'label': str}

    Raises
    ------
    KeyError
        If state_type is not a registered UI state.
    """
    state_type = str(state_type).strip() if state_type else ""
    if state_type not in UI_STATES:
        raise KeyError(
            f"Unknown Pink UI state '{state_type}'. "
            f"Valid states: {list(UI_STATES.keys())}"
        )
    return dict(UI_STATES[state_type])


# ---------------------------------------------------------------------------
# Rose Signal Discrimination
# ---------------------------------------------------------------------------

def is_rose_signal(signal: dict) -> bool:
    """
    Determine whether a signal is a genuine rose (Rosa Mystica) signal
    versus a SENTINEL or false-albedo signal.

    A genuine rose signal:
      - carries 'rosa_mystica': True
      - does NOT carry 'sentinel': True
      - does NOT carry 'false_albedo': True

    Parameters
    ----------
    signal : dict
        Incoming signal payload.

    Returns
    -------
    bool
    """
    if not signal:
        return False

    rosa_mystica = bool(signal.get("rosa_mystica", False))
    sentinel     = bool(signal.get("sentinel",     False))
    false_albedo = bool(signal.get("false_albedo", False))

    return rosa_mystica and not sentinel and not false_albedo

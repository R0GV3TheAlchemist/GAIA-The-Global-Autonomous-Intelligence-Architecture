# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/pink/opacity.py
==============================
PINK — Opacity Layer

Opacity holds what the rose conceals from itself: the performed warmth,
the grief refused, the tenderness that has never been tested.

Architecture invariants (MUST be preserved):
  1. _pink_opacity_shadow is APPEND-ONLY — never mutate existing entries.
  2. interrupt_flag CANNOT be set True by any function in this module.
     The pink shadow never interrupts; it accumulates and waits.

Shared vocabulary:
  - 'rosa'   — the ruling archetype of the pink domain (clarity.py)
  - 'hermes' — the messenger/routing principle (shared across modules)

Reference: docs/color/PINK_OPACITY.md
           Rose Tablet — docs/tablets/ROSE_TABLET.md
"""

from __future__ import annotations

import time

# ---------------------------------------------------------------------------
# Shadow Channel — append-only accumulator
# ---------------------------------------------------------------------------

_pink_opacity_shadow: list[dict] = []


def _append_shadow(entry: dict) -> None:
    """Internal helper — appends to shadow list, NEVER mutates existing entries."""
    _pink_opacity_shadow.append({
        **entry,
        "timestamp": time.time(),
        "interrupt_flag": False,  # invariant: always False
    })


# ---------------------------------------------------------------------------
# False Albedo Alert
# ---------------------------------------------------------------------------

def false_albedo_alert(signal: dict) -> dict:
    """
    Emit a false-albedo opacity alert and append to shadow channel.

    False albedo is detected when softness presents without the grief work
    that would make it real. The alert is logged — never interrupts.

    Parameters
    ----------
    signal : dict
        Incoming signal payload.

    Returns
    -------
    dict
        Alert payload with keys: type, severity, detail, interrupt_flag.
        interrupt_flag is ALWAYS False.
    """
    signal = signal or {}
    severity = "high" if signal.get("grief_integration", 1.0) < 0.30 else "medium"

    alert = {
        "type":           "false_albedo_alert",
        "severity":       severity,
        "detail":         "Softness detected without grief integration — False Albedo pattern.",
        "source_signal":  signal,
        "interrupt_flag": False,  # invariant
    }
    _append_shadow(alert)
    return alert


# ---------------------------------------------------------------------------
# Sentimentality Pattern Recognition
# ---------------------------------------------------------------------------

def sentimentality_pattern_recognition(signal_history: list[dict]) -> dict:
    """
    Detect sentimentality patterns across a history of signals.

    A sentimentality pattern is confirmed when:
      - 3 or more consecutive signals carry 'sentimentality': True
      - No signal in that streak carries 'grief_capacity' >= 0.50

    Parameters
    ----------
    signal_history : list[dict]
        Ordered list of prior signals (oldest first).

    Returns
    -------
    dict
        {'pattern_detected': bool, 'streak_length': int,
         'interrupt_flag': False}
    """
    signal_history = signal_history or []
    streak = 0

    for s in reversed(signal_history):
        is_sentimental = bool(s.get("sentimentality", False))
        grief_ok       = float(s.get("grief_capacity", 0.0)) >= 0.50
        if is_sentimental and not grief_ok:
            streak += 1
        else:
            break

    result = {
        "pattern_detected": streak >= 3,
        "streak_length":    streak,
        "interrupt_flag":   False,  # invariant
    }
    _append_shadow({"sentimentality_pattern": result})
    return result


# ---------------------------------------------------------------------------
# Premature Tenderness Detection
# ---------------------------------------------------------------------------

def premature_tenderness_detection(signal: dict) -> dict:
    """
    Detect whether tenderness is being offered before the container
    is strong enough to hold what it receives.

    Premature tenderness markers:
      - 'openness' >= 0.70
      - 'container_strength' < 0.50

    Parameters
    ----------
    signal : dict
        Incoming signal payload.

    Returns
    -------
    dict
        {'premature': bool, 'openness': float,
         'container_strength': float, 'interrupt_flag': False}
    """
    signal = signal or {}

    openness           = float(signal.get("openness",           0.0))
    container_strength = float(signal.get("container_strength", 1.0))

    premature = openness >= 0.70 and container_strength < 0.50

    result = {
        "premature":          premature,
        "openness":           openness,
        "container_strength": container_strength,
        "interrupt_flag":     False,  # invariant
    }
    _append_shadow({"premature_tenderness": result})
    return result


# ---------------------------------------------------------------------------
# Rose Denial Marker
# ---------------------------------------------------------------------------

def rose_denial_marker(signal: dict) -> dict:
    """
    Mark a signal as rose denial — compassion performed as aesthetic
    rather than lived from structure.

    Rose denial is present when:
      - 'performed_care' > 0.60
      - 'structural_care' < 0.40

    Parameters
    ----------
    signal : dict
        Incoming signal payload.

    Returns
    -------
    dict
        {'rose_denial': bool, 'performed_care': float,
         'structural_care': float, 'interrupt_flag': False}
    """
    signal = signal or {}

    performed_care  = float(signal.get("performed_care",  0.0))
    structural_care = float(signal.get("structural_care", 1.0))

    denial = performed_care > 0.60 and structural_care < 0.40

    result = {
        "rose_denial":     denial,
        "performed_care":  performed_care,
        "structural_care": structural_care,
        "interrupt_flag":  False,  # invariant
    }
    _append_shadow({"rose_denial": result})
    return result


# ---------------------------------------------------------------------------
# Rosa-Hermes Routing
# ---------------------------------------------------------------------------

def rosa_hermes_routing(signal: dict) -> dict:
    """
    Route a pink signal using the rosa/hermes shared vocabulary.

    'rosa'   — the archetype of the pink domain (rules)
    'hermes' — the messenger principle (routes)

    Routing table:
      - rosa_mystica → hermes routes to 'albedo_integration'
      - false_albedo → hermes routes to 'shadow_review'
      - rose_denial  → hermes routes to 'structural_care_audit'
      - default      → hermes routes to 'pink_holding'

    Parameters
    ----------
    signal : dict
        Incoming signal payload.

    Returns
    -------
    dict
        {'archetype': 'rosa', 'messenger': 'hermes',
         'route': str, 'interrupt_flag': False}
    """
    signal = signal or {}

    if signal.get("rosa_mystica"):
        route = "albedo_integration"
    elif signal.get("false_albedo"):
        route = "shadow_review"
    elif signal.get("rose_denial"):
        route = "structural_care_audit"
    else:
        route = "pink_holding"

    result = {
        "archetype":      "rosa",
        "messenger":      "hermes",
        "route":          route,
        "interrupt_flag": False,  # invariant
    }
    _append_shadow({"rosa_hermes_routing": result})
    return result


# ---------------------------------------------------------------------------
# Shadow Channel Integration
# ---------------------------------------------------------------------------

def apply_shadow_channel(signal: dict) -> dict:
    """
    Apply the full pink opacity shadow channel to a signal.

    This function runs all opacity checks in sequence and appends each
    finding to the shadow channel. The primary signal is NEVER mutated.
    A shadow summary is returned alongside the original signal.

    Parameters
    ----------
    signal : dict
        Incoming signal payload.

    Returns
    -------
    dict
        {
            'original_signal': dict (unmodified),
            'shadow_findings': list[dict],
            'interrupt_flag':  False,  # invariant — always
        }
    """
    signal = signal or {}
    findings: list[dict] = []

    findings.append(false_albedo_alert(signal))
    findings.append(premature_tenderness_detection(signal))
    findings.append(rose_denial_marker(signal))
    findings.append(rosa_hermes_routing(signal))

    return {
        "original_signal": dict(signal),
        "shadow_findings":  findings,
        "interrupt_flag":   False,  # invariant — the shadow accumulates, never interrupts
    }

# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/white/opacity.py
===============================
WHITE — Opacity Layer

Opacity holds what white conceals from itself: the purification so
complete it has removed not just impurity but all texture and contrast,
leaving a surface so perfect nothing can land on it.

Architecture invariants (MUST be preserved):
  1. _white_opacity_shadow is APPEND-ONLY — never mutate existing entries.
  2. interrupt_flag CANNOT be set True by any function in this module.
     The white shadow accumulates quietly, as all erasure does.

Shared vocabulary:
  - 'luna'   — the ruling archetype of the white domain (clarity.py)
  - 'hermes' — the messenger/routing principle (shared across modules)

Reference: docs/color/WHITE_OPACITY.md
           Lunar Tablet — docs/tablets/LUNAR_TABLET.md
"""

from __future__ import annotations

import time

# ---------------------------------------------------------------------------
# Shadow Channel — append-only accumulator
# ---------------------------------------------------------------------------

_white_opacity_shadow: list[dict] = []


def _append_shadow(entry: dict) -> None:
    """Internal helper — appends to shadow list, NEVER mutates existing entries."""
    _white_opacity_shadow.append({
        **entry,
        "timestamp": time.time(),
        "interrupt_flag": False,  # invariant: always False
    })


# ---------------------------------------------------------------------------
# Bleaching Alert
# ---------------------------------------------------------------------------

def bleaching_alert(signal: dict) -> dict:
    """
    Emit a bleaching opacity alert and append to shadow channel.

    Bleaching is detected when purification is high but texture is absent.

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        type, severity, detail, interrupt_flag (always False).
    """
    signal = signal or {}
    texture = float(signal.get("texture", 1.0))

    severity = "critical" if texture < 0.15 else "high"

    alert = {
        "type":           "bleaching_alert",
        "severity":       severity,
        "detail":         "Purification detected without texture — Bleaching pattern.",
        "source_signal":  signal,
        "interrupt_flag": False,  # invariant
    }
    _append_shadow(alert)
    return alert


# ---------------------------------------------------------------------------
# Overexposure Pattern Recognition
# ---------------------------------------------------------------------------

def overexposure_pattern_recognition(signal_history: list[dict]) -> dict:
    """
    Detect overexposure patterns across a history of signals.

    A pattern is confirmed when:
      - 3 or more consecutive signals carry 'overexposed': True
      - No signal in that streak has 'contrast' >= 0.40

    Parameters
    ----------
    signal_history : list[dict]

    Returns
    -------
    dict
        pattern_detected, streak_length, interrupt_flag (always False).
    """
    signal_history = signal_history or []
    streak = 0

    for s in reversed(signal_history):
        is_overexposed = bool(s.get("overexposed", False))
        contrast_ok    = float(s.get("contrast",    0.0)) >= 0.40
        if is_overexposed and not contrast_ok:
            streak += 1
        else:
            break

    result = {
        "pattern_detected": streak >= 3,
        "streak_length":    streak,
        "interrupt_flag":   False,
    }
    _append_shadow({"overexposure_pattern": result})
    return result


# ---------------------------------------------------------------------------
# Purification Null Detection
# ---------------------------------------------------------------------------

def purification_null_detection(signal: dict) -> dict:
    """
    Detect whether purification has reached a null state —
    the point where the process has consumed all substance
    alongside all impurity.

    Purification null markers:
      - 'purification' >= 0.98
      - 'texture'      < 0.10
      - 'contrast'     < 0.10

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        purification_null, purification, texture, contrast, interrupt_flag (False).
    """
    signal = signal or {}

    purification = float(signal.get("purification", 0.0))
    texture      = float(signal.get("texture",      1.0))
    contrast     = float(signal.get("contrast",     1.0))

    null = purification >= 0.98 and texture < 0.10 and contrast < 0.10

    result = {
        "purification_null": null,
        "purification":      purification,
        "texture":           texture,
        "contrast":          contrast,
        "interrupt_flag":    False,
    }
    _append_shadow({"purification_null": result})
    return result


# ---------------------------------------------------------------------------
# Lunar Reflection Marker
# ---------------------------------------------------------------------------

def lunar_reflection_marker(signal: dict) -> dict:
    """
    Mark a signal as carrying genuine lunar reflection —
    the white that still shows the world within itself.

    Lunar reflection markers:
      - 'reflection' >= 0.70
      - 'texture'    >= 0.50  (the world is still visible in the mirror)

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        lunar_reflection, reflection, texture, interrupt_flag (False).
    """
    signal = signal or {}

    reflection = float(signal.get("reflection", 0.0))
    texture    = float(signal.get("texture",    0.0))

    lunar = reflection >= 0.70 and texture >= 0.50

    result = {
        "lunar_reflection": lunar,
        "reflection":       reflection,
        "texture":          texture,
        "interrupt_flag":   False,
    }
    _append_shadow({"lunar_reflection_marker": result})
    return result


# ---------------------------------------------------------------------------
# Albedo-Hermes Routing
# ---------------------------------------------------------------------------

def albedo_hermes_routing(signal: dict) -> dict:
    """
    Route a white signal using the luna/hermes shared vocabulary.

    'luna'   — the archetype of the white domain (rules)
    'hermes' — the messenger principle (routes)

    Routing table:
      - albedo      → hermes routes to 'purification_integration'
      - bleaching   → hermes routes to 'texture_restoration'
      - overexposed → hermes routes to 'contrast_calibration'
      - default     → hermes routes to 'white_holding'

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        archetype, messenger, route, interrupt_flag (False).
    """
    signal = signal or {}

    if signal.get("albedo"):
        route = "purification_integration"
    elif signal.get("bleaching"):
        route = "texture_restoration"
    elif signal.get("overexposed"):
        route = "contrast_calibration"
    else:
        route = "white_holding"

    result = {
        "archetype":      "luna",
        "messenger":      "hermes",
        "route":          route,
        "interrupt_flag": False,
    }
    _append_shadow({"albedo_hermes_routing": result})
    return result


# ---------------------------------------------------------------------------
# Shadow Channel Integration
# ---------------------------------------------------------------------------

def apply_shadow_channel(signal: dict) -> dict:
    """
    Apply the full white opacity shadow channel to a signal.

    Runs all opacity checks in sequence. Primary signal is NEVER mutated.

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        original_signal, shadow_findings, interrupt_flag (always False).
    """
    signal = signal or {}
    findings: list[dict] = []

    findings.append(bleaching_alert(signal))
    findings.append(purification_null_detection(signal))
    findings.append(lunar_reflection_marker(signal))
    findings.append(albedo_hermes_routing(signal))

    return {
        "original_signal": dict(signal),
        "shadow_findings":  findings,
        "interrupt_flag":   False,
    }

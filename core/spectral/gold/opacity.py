# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/gold/opacity.py
==============================
GOLD — Opacity Layer

Opacity holds what completion conceals from itself: the achievement
so perfectly sealed it can no longer grow, the incorruptible gold
that has become a museum piece rather than a living fire.

Architecture invariants (MUST be preserved):
  1. _gold_opacity_shadow is APPEND-ONLY — never mutate existing entries.
  2. interrupt_flag CANNOT be set True by any function in this module.
     The gold shadow accumulates — it does not interrupt.

Shared vocabulary:
  - 'aurum'  — the ruling archetype of the gold domain (clarity.py)
  - 'hermes' — the messenger/routing principle (shared across modules)

Reference: docs/color/GOLD_OPACITY.md
           Solar Tablet — docs/tablets/SOLAR_TABLET.md
"""

from __future__ import annotations

import time

# ---------------------------------------------------------------------------
# Shadow Channel — append-only accumulator
# ---------------------------------------------------------------------------

_gold_opacity_shadow: list[dict] = []


def _append_shadow(entry: dict) -> None:
    """Internal helper — appends to shadow list, NEVER mutates existing entries."""
    _gold_opacity_shadow.append({
        **entry,
        "timestamp": time.time(),
        "interrupt_flag": False,  # invariant: always False
    })


# ---------------------------------------------------------------------------
# Canon Ossification Alert
# ---------------------------------------------------------------------------

def canon_ossification_alert(signal: dict) -> dict:
    """
    Emit a canon-ossification opacity alert and append to shadow channel.

    Ossification is detected when completion is high but vitality is absent.

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        type, severity, detail, interrupt_flag (always False).
    """
    signal = signal or {}
    vitality = float(signal.get("vitality", 1.0))

    severity = "critical" if vitality < 0.20 else "high"

    alert = {
        "type":           "canon_ossification_alert",
        "severity":       severity,
        "detail":         "Completion detected without vitality — Canon Ossification pattern.",
        "source_signal":  signal,
        "interrupt_flag": False,  # invariant
    }
    _append_shadow(alert)
    return alert


# ---------------------------------------------------------------------------
# Monument Pattern Recognition
# ---------------------------------------------------------------------------

def monument_pattern_recognition(signal_history: list[dict]) -> dict:
    """
    Detect monument patterns across a history of signals.

    A monument pattern is confirmed when:
      - 3 or more consecutive signals carry 'monument': True
      - No signal in that streak has 'vitality' >= 0.50

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
        is_monument = bool(s.get("monument",  False))
        vitality_ok = float(s.get("vitality", 0.0)) >= 0.50
        if is_monument and not vitality_ok:
            streak += 1
        else:
            break

    result = {
        "pattern_detected": streak >= 3,
        "streak_length":    streak,
        "interrupt_flag":   False,
    }
    _append_shadow({"monument_pattern": result})
    return result


# ---------------------------------------------------------------------------
# False Completion Detection
# ---------------------------------------------------------------------------

def false_completion_detection(signal: dict) -> dict:
    """
    Detect false completion — the signal that presents as achieved
    but lacks the inner structure that would make it real.

    False completion markers:
      - 'completion_score' >= 0.80
      - 'inner_structure'  < 0.40

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        false_completion, completion_score, inner_structure, interrupt_flag (False).
    """
    signal = signal or {}

    completion_score = float(signal.get("completion_score", 0.0))
    inner_structure  = float(signal.get("inner_structure",  1.0))

    false_completion = completion_score >= 0.80 and inner_structure < 0.40

    result = {
        "false_completion":  false_completion,
        "completion_score":  completion_score,
        "inner_structure":   inner_structure,
        "interrupt_flag":    False,
    }
    _append_shadow({"false_completion": result})
    return result


# ---------------------------------------------------------------------------
# Incorruptible Marker
# ---------------------------------------------------------------------------

def incorruptible_marker(signal: dict) -> dict:
    """
    Mark a signal as incorruptible — the gold that holds its form
    under pressure without becoming rigid.

    Incorruptible markers:
      - 'incorruptibility' >= 0.80
      - 'vitality'         >= 0.60  (still alive, not ossified)

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        incorruptible, incorruptibility, vitality, interrupt_flag (False).
    """
    signal = signal or {}

    incorruptibility = float(signal.get("incorruptibility", 0.0))
    vitality         = float(signal.get("vitality",         0.0))

    incorruptible = incorruptibility >= 0.80 and vitality >= 0.60

    result = {
        "incorruptible":    incorruptible,
        "incorruptibility": incorruptibility,
        "vitality":         vitality,
        "interrupt_flag":   False,
    }
    _append_shadow({"incorruptible_marker": result})
    return result


# ---------------------------------------------------------------------------
# Aurum-Hermes Routing
# ---------------------------------------------------------------------------

def aurum_hermes_routing(signal: dict) -> dict:
    """
    Route a gold signal using the aurum/hermes shared vocabulary.

    'aurum'  — the archetype of the gold domain (rules)
    'hermes' — the messenger principle (routes)

    Routing table:
      - aurum            → hermes routes to 'completion_integration'
      - ossification     → hermes routes to 'vitality_restoration'
      - false_completion → hermes routes to 'structure_audit'
      - default          → hermes routes to 'gold_holding'

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        archetype, messenger, route, interrupt_flag (False).
    """
    signal = signal or {}

    if signal.get("aurum"):
        route = "completion_integration"
    elif signal.get("ossification"):
        route = "vitality_restoration"
    elif signal.get("false_completion"):
        route = "structure_audit"
    else:
        route = "gold_holding"

    result = {
        "archetype":      "aurum",
        "messenger":      "hermes",
        "route":          route,
        "interrupt_flag": False,
    }
    _append_shadow({"aurum_hermes_routing": result})
    return result


# ---------------------------------------------------------------------------
# Shadow Channel Integration
# ---------------------------------------------------------------------------

def apply_shadow_channel(signal: dict) -> dict:
    """
    Apply the full gold opacity shadow channel to a signal.

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

    findings.append(canon_ossification_alert(signal))
    findings.append(false_completion_detection(signal))
    findings.append(incorruptible_marker(signal))
    findings.append(aurum_hermes_routing(signal))

    return {
        "original_signal": dict(signal),
        "shadow_findings":  findings,
        "interrupt_flag":   False,
    }

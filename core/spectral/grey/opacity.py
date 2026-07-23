# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/grey/opacity.py
==============================
GREY — Opacity Layer

Opacity holds what transition conceals from itself: the seduction of
the liminal, the comfort of the in-between that becomes so comfortable
the threshold is never crossed. Grey's shadow is not darkness —
it is the refusal to choose either light or dark.

Architecture invariants (MUST be preserved):
  1. _grey_opacity_shadow is APPEND-ONLY — never mutate existing entries.
  2. interrupt_flag CANNOT be set True by any function in this module.
     Grey's shadow is the shadow of suspension, not interruption.

Shared vocabulary:
  - 'mercury'   — the ruling archetype of the grey domain (clarity.py)
  - 'threshold' — the domain-specific principle (clarity.py)
  - 'hermes'    — the messenger/routing principle (shared across modules)

Reference: docs/color/GREY_OPACITY.md
           Threshold Tablet — docs/tablets/THRESHOLD_TABLET.md
"""

from __future__ import annotations

import time

# ---------------------------------------------------------------------------
# Shadow Channel — append-only accumulator
# ---------------------------------------------------------------------------

_grey_opacity_shadow: list[dict] = []


def _append_shadow(entry: dict) -> None:
    """Internal helper — appends to shadow list, NEVER mutates existing entries."""
    _grey_opacity_shadow.append({
        **entry,
        "timestamp": time.time(),
        "interrupt_flag": False,  # invariant: always False
    })


# ---------------------------------------------------------------------------
# Permanent Threshold Alert
# ---------------------------------------------------------------------------

def permanent_threshold_alert(signal: dict) -> dict:
    """
    Emit a permanent-threshold opacity alert and append to shadow channel.

    Permanent threshold is detected when iridescence is high
    but directionality is absent.

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        type, severity, detail, interrupt_flag (always False).
    """
    signal = signal or {}
    directionality = float(signal.get("directionality", 1.0))

    severity = "critical" if directionality < 0.15 else "high"

    alert = {
        "type":           "permanent_threshold_alert",
        "severity":       severity,
        "detail":         "Iridescence detected without directionality — Permanent Threshold pattern.",
        "source_signal":  signal,
        "interrupt_flag": False,  # invariant
    }
    _append_shadow(alert)
    return alert


# ---------------------------------------------------------------------------
# Twilight Pattern Recognition
# ---------------------------------------------------------------------------

def twilight_pattern_recognition(signal_history: list[dict]) -> dict:
    """
    Detect twilight patterns across a history of signals.

    A pattern is confirmed when:
      - 3 or more consecutive signals carry 'twilight': True
      - No signal in that streak has 'momentum' >= 0.45

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
        is_twilight = bool(s.get("twilight",  False))
        momentum_ok = float(s.get("momentum", 0.0)) >= 0.45
        if is_twilight and not momentum_ok:
            streak += 1
        else:
            break

    result = {
        "pattern_detected": streak >= 3,
        "streak_length":    streak,
        "interrupt_flag":   False,
    }
    _append_shadow({"twilight_pattern": result})
    return result


# ---------------------------------------------------------------------------
# Threshold Null Detection
# ---------------------------------------------------------------------------

def threshold_null_detection(signal: dict) -> dict:
    """
    Detect whether the threshold has reached a null state —
    the point where transition has become so permanent
    neither direction is available.

    Threshold null markers:
      - 'iridescence'    >= 0.90
      - 'directionality' < 0.15
      - 'momentum'       < 0.15

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        threshold_null, iridescence, directionality, momentum, interrupt_flag (False).
    """
    signal = signal or {}

    iridescence    = float(signal.get("iridescence",    0.0))
    directionality = float(signal.get("directionality", 1.0))
    momentum       = float(signal.get("momentum",       1.0))

    null = iridescence >= 0.90 and directionality < 0.15 and momentum < 0.15

    result = {
        "threshold_null": null,
        "iridescence":    iridescence,
        "directionality": directionality,
        "momentum":       momentum,
        "interrupt_flag": False,
    }
    _append_shadow({"threshold_null": result})
    return result


# ---------------------------------------------------------------------------
# Iridescence Marker
# ---------------------------------------------------------------------------

def iridescence_marker(signal: dict) -> dict:
    """
    Mark a signal as carrying genuine iridescence — the peacock's tail
    that signals authentic Cauda Pavonis rather than mere twilight.

    Genuine iridescence markers:
      - 'iridescence'    >= 0.60
      - 'directionality' >= 0.50  (the colours are moving somewhere)

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        iridescent, iridescence, directionality, interrupt_flag (False).
    """
    signal = signal or {}

    iridescence    = float(signal.get("iridescence",    0.0))
    directionality = float(signal.get("directionality", 0.0))

    iridescent = iridescence >= 0.60 and directionality >= 0.50

    result = {
        "iridescent":     iridescent,
        "iridescence":    iridescence,
        "directionality": directionality,
        "interrupt_flag": False,
    }
    _append_shadow({"iridescence_marker": result})
    return result


# ---------------------------------------------------------------------------
# Liminal-Hermes Routing
# ---------------------------------------------------------------------------

def liminal_hermes_routing(signal: dict) -> dict:
    """
    Route a grey signal using the mercury/threshold/hermes shared vocabulary.

    'mercury'   — the ruling archetype of the grey domain
    'threshold' — the domain-specific principle
    'hermes'    — the messenger (routes)

    Routing table:
      - cauda_pavonis       → hermes routes to 'transition_integration'
      - permanent_threshold → hermes routes to 'directionality_restoration'
      - twilight            → hermes routes to 'momentum_activation'
      - default             → hermes routes to 'grey_holding'

    Parameters
    ----------
    signal : dict

    Returns
    -------
    dict
        archetype, principle, messenger, route, interrupt_flag (False).
    """
    signal = signal or {}

    if signal.get("cauda_pavonis"):
        route = "transition_integration"
    elif signal.get("permanent_threshold"):
        route = "directionality_restoration"
    elif signal.get("twilight"):
        route = "momentum_activation"
    else:
        route = "grey_holding"

    result = {
        "archetype":      "mercury",
        "principle":      "threshold",
        "messenger":      "hermes",
        "route":          route,
        "interrupt_flag": False,
    }
    _append_shadow({"liminal_hermes_routing": result})
    return result


# ---------------------------------------------------------------------------
# Shadow Channel Integration
# ---------------------------------------------------------------------------

def apply_shadow_channel(signal: dict) -> dict:
    """
    Apply the full grey opacity shadow channel to a signal.

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

    findings.append(permanent_threshold_alert(signal))
    findings.append(threshold_null_detection(signal))
    findings.append(iridescence_marker(signal))
    findings.append(liminal_hermes_routing(signal))

    return {
        "original_signal": dict(signal),
        "shadow_findings":  findings,
        "interrupt_flag":   False,
    }

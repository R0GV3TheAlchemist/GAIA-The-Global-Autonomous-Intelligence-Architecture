# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/yellow/clarity.py
================================
Depth-readable signals for the YELLOW (Xanthosis) spectral layer.
"""

from __future__ import annotations
from typing import Any

from .constants import YELLOW_HEX, ALCHEMICAL_PHASE

_MIND_ARCHETYPES = {
    "sage":      "The Sage — integrated illumined intellect",
    "trickster": "The Trickster — clever but destabilising",
    "scholar":   "The Scholar — accumulating without integrating",
    "dreamer":   "The Dreamer — visionary but untethered",
}


def distinguish_intellect_intuition(signal: dict[str, Any]) -> str:
    has_intellect = bool(signal.get("analysis") or signal.get("logic"))
    has_intuition = bool(signal.get("intuition") or signal.get("vision"))
    if has_intellect and has_intuition:
        return "integrated"
    if has_intellect:
        return "intellect"
    if has_intuition:
        return "intuition"
    return "undifferentiated"


def detect_mental_wound(signal: dict[str, Any]) -> dict[str, Any]:
    patterns: list[tuple[bool, str, str]] = [
        (bool(signal.get("overthinking")),  "analysis paralysis — mind loop",       "moderate"),
        (bool(signal.get("rigidity")),       "mental rigidity — closed cognition",   "severe"),
        (bool(signal.get("dissociation")),   "dissociative split — mind-body gap",   "severe"),
        (bool(signal.get("scatteredness")), "scattered mind — unfocused dispersal", "mild"),
    ]
    for detected, pattern, severity in patterns:
        if detected:
            return {"wound_detected": True, "pattern": pattern, "severity": severity}
    return {"wound_detected": False, "pattern": "", "severity": "none"}


def classify_yellow_frequency(signal: dict[str, Any]) -> str:
    intensity = float(signal.get("intensity", 0.0))
    coherent  = bool(signal.get("coherent"))
    blocked   = bool(signal.get("blocked"))
    if blocked or intensity < 0.2:
        return "dormant"
    if coherent and intensity >= 0.5:
        return "illuminated"
    return "scattered"


def assess_mental_integration(signal: dict[str, Any]) -> float:
    score = 0.0
    if signal.get("focused"):    score += 0.25
    if signal.get("embodied"):   score += 0.25
    if signal.get("discerning"): score += 0.25
    intensity = float(signal.get("intensity", 0.0))
    if 0.4 <= intensity <= 0.85: score += 0.25
    return round(score, 4)


def map_mind_archetype(signal: dict[str, Any]) -> str:
    freq        = classify_yellow_frequency(signal)
    integration = assess_mental_integration(signal)
    if freq == "dormant":
        return "dreamer" if integration < 0.25 else "scholar"
    if freq == "scattered":
        return "trickster"
    return "sage" if integration >= 0.75 else "scholar"

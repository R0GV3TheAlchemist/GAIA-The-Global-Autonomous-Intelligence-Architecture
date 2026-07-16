# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/orange/opacity.py
================================
Shadow channel, passive, non-blocking signals for the ORANGE (Citrinitas) layer.
Opacity layer: runs silently; NEVER interrupts the primary signal stream.

CRITICAL INVARIANT
------------------
interrupt_flag MUST always be False. This is enforced in every function.

Functions
---------
citrinitas_alert           — Shadow-channel alert for citrinitas activation.
creative_wound_recognition — Passively tag creative wound patterns.
phoenix_marker             — Track solar resurrection / citrinitas renewal.
ares_athena_routing        — Route solar archetype to ares or athena channel.
apply_shadow_channel       — Append shadow data without mutating primary signal.
"""

from __future__ import annotations
from typing import Any

from .constants import ORANGE_HEX, ALCHEMICAL_PHASE
from .clarity import detect_solar_wound, map_solar_archetype

# Module-level shadow channel store (append-only)
_opacity_shadow: list[dict[str, Any]] = []


def citrinitas_alert(signal: dict[str, Any]) -> dict[str, Any]:
    """
    Emit a shadow-channel citrinitas alert.
    interrupt_flag is always False — passive observation only.
    """
    entry = {
        "module":         "spectral.orange.opacity",
        "phase":          ALCHEMICAL_PHASE,
        "hex":            ORANGE_HEX["CITRINITAS"],
        "alert_type":     "citrinitas_activation",
        "source_signal":  signal,
        "interrupt_flag": False,  # INVARIANT — never True
    }
    _opacity_shadow.append(entry)
    return entry


def creative_wound_recognition(signal: dict[str, Any]) -> dict[str, Any]:
    """
    Passively tag creative wound patterns from the shadow channel.
    Does not modify the primary signal.
    """
    wound_data = detect_solar_wound(signal)
    entry = {
        "module":         "spectral.orange.opacity",
        "wound_data":     wound_data,
        "hex":            ORANGE_HEX["EMBER"],
        "interrupt_flag": False,  # INVARIANT
    }
    _opacity_shadow.append(entry)
    return entry


def phoenix_marker(
    signal: dict[str, Any],
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Track solar resurrection events (citrinitas renewal cycles).

    A phoenix marker is emitted when the signal transitions from a
    dormant/consuming fire classification to generative across consecutive
    entries in *history*.

    Returns a marker dict with resurrection_detected: bool.
    """
    from .clarity import classify_orange_fire

    resurrection_detected = False
    if history:
        prev_classes = [classify_orange_fire(h) for h in history[-3:]]
        current_class = classify_orange_fire(signal)
        if current_class == "generative" and any(
            c in ("dormant", "consuming") for c in prev_classes
        ):
            resurrection_detected = True

    entry = {
        "module":               "spectral.orange.opacity",
        "resurrection_detected": resurrection_detected,
        "hex":                  ORANGE_HEX["DAWN_GOLD"],
        "interrupt_flag":       False,  # INVARIANT
    }
    _opacity_shadow.append(entry)
    return entry


def ares_athena_routing(signal: dict[str, Any]) -> dict[str, Any]:
    """
    Route solar archetype to ares (raw fire) or athena (strategic fire) channel.

    Archetypes → channel mapping
    ----------------------------
    fool, adventurer  → "ares"   (unstructured energy)
    creator, sovereign → "athena" (purposeful, structured energy)
    """
    archetype = map_solar_archetype(signal)
    channel   = "ares" if archetype in ("fool", "adventurer") else "athena"

    entry = {
        "module":         "spectral.orange.opacity",
        "archetype":      archetype,
        "channel":        channel,
        "hex":            ORANGE_HEX["SOLAR_FLARE"],
        "interrupt_flag": False,  # INVARIANT
    }
    _opacity_shadow.append(entry)
    return entry


def apply_shadow_channel(
    primary_signal: dict[str, Any],
    shadow_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Append shadow_data to the primary signal's "_opacity_shadow" key.

    CRITICAL: primary_signal is NOT mutated.
    Returns a new dict with _opacity_shadow appended.
    interrupt_flag is stripped/forced False if present in shadow_data.
    """
    safe_shadow = {k: v for k, v in shadow_data.items() if k != "interrupt_flag"}
    safe_shadow["interrupt_flag"] = False  # INVARIANT enforced

    result = dict(primary_signal)  # shallow copy — primary untouched
    existing = result.get("_opacity_shadow", [])
    result["_opacity_shadow"] = list(existing) + [safe_shadow]
    return result

# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/yellow/opacity.py
================================
Shadow channel, passive, non-blocking. interrupt_flag ALWAYS False.
"""

from __future__ import annotations
from typing import Any

from .constants import YELLOW_HEX, ALCHEMICAL_PHASE
from .clarity import detect_mental_wound, map_mind_archetype, classify_yellow_frequency

_opacity_shadow: list[dict[str, Any]] = []


def xanthosis_alert(signal: dict[str, Any]) -> dict[str, Any]:
    entry = {
        "module": "spectral.yellow.opacity",
        "phase": ALCHEMICAL_PHASE,
        "hex": YELLOW_HEX["XANTHOSIS"],
        "alert_type": "xanthosis_activation",
        "source_signal": signal,
        "interrupt_flag": False,
    }
    _opacity_shadow.append(entry)
    return entry


def mental_wound_recognition(signal: dict[str, Any]) -> dict[str, Any]:
    wound_data = detect_mental_wound(signal)
    entry = {
        "module": "spectral.yellow.opacity",
        "wound_data": wound_data,
        "hex": YELLOW_HEX["GOLDEN"],
        "interrupt_flag": False,
    }
    _opacity_shadow.append(entry)
    return entry


def illumination_marker(
    signal: dict[str, Any],
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    illumination_detected = False
    if history:
        prev_classes = [classify_yellow_frequency(h) for h in history[-3:]]
        current_class = classify_yellow_frequency(signal)
        if current_class == "illuminated" and any(
            c in ("dormant", "scattered") for c in prev_classes
        ):
            illumination_detected = True
    entry = {
        "module": "spectral.yellow.opacity",
        "illumination_detected": illumination_detected,
        "hex": YELLOW_HEX["DAWN_LIGHT"],
        "interrupt_flag": False,
    }
    _opacity_shadow.append(entry)
    return entry


def ares_athena_routing(signal: dict[str, Any]) -> dict[str, Any]:
    archetype = map_mind_archetype(signal)
    channel   = "ares" if archetype in ("dreamer", "trickster") else "athena"
    entry = {
        "module": "spectral.yellow.opacity",
        "archetype": archetype,
        "channel": channel,
        "hex": YELLOW_HEX["SOLAR"],
        "interrupt_flag": False,
    }
    _opacity_shadow.append(entry)
    return entry


def apply_shadow_channel(
    primary_signal: dict[str, Any],
    shadow_data: dict[str, Any],
) -> dict[str, Any]:
    safe_shadow = {k: v for k, v in shadow_data.items() if k != "interrupt_flag"}
    safe_shadow["interrupt_flag"] = False
    result = dict(primary_signal)
    existing = result.get("_opacity_shadow", [])
    result["_opacity_shadow"] = list(existing) + [safe_shadow]
    return result

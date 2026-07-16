# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
"""
core/spectral/green/opacity.py — Shadow channel, passive. interrupt_flag ALWAYS False.
"""
from __future__ import annotations
from typing import Any
from .constants import GREEN_HEX, ALCHEMICAL_PHASE
from .clarity import detect_earth_wound, map_earth_archetype, classify_green_vitality

_opacity_shadow: list[dict[str, Any]] = []


def viriditas_alert(signal: dict[str, Any]) -> dict[str, Any]:
    entry = {"module": "spectral.green.opacity", "phase": ALCHEMICAL_PHASE,
             "hex": GREEN_HEX["VIRIDITAS"], "alert_type": "viriditas_activation",
             "source_signal": signal, "interrupt_flag": False}
    _opacity_shadow.append(entry)
    return entry


def earth_wound_recognition(signal: dict[str, Any]) -> dict[str, Any]:
    entry = {"module": "spectral.green.opacity", "wound_data": detect_earth_wound(signal),
             "hex": GREEN_HEX["DEEP_FOREST"], "interrupt_flag": False}
    _opacity_shadow.append(entry)
    return entry


def regeneration_marker(
    signal: dict[str, Any],
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    regeneration_detected = False
    if history:
        prev = [classify_green_vitality(h) for h in history[-3:]]
        if classify_green_vitality(signal) == "flourishing" and any(c in ("dormant", "overgrown") for c in prev):
            regeneration_detected = True
    entry = {"module": "spectral.green.opacity", "regeneration_detected": regeneration_detected,
             "hex": GREEN_HEX["SPRING"], "interrupt_flag": False}
    _opacity_shadow.append(entry)
    return entry


def ares_athena_routing(signal: dict[str, Any]) -> dict[str, Any]:
    archetype = map_earth_archetype(signal)
    channel   = "ares" if archetype in ("wildling", "dormant") else "athena"
    entry = {"module": "spectral.green.opacity", "archetype": archetype,
             "channel": channel, "hex": GREEN_HEX["GROWTH"], "interrupt_flag": False}
    _opacity_shadow.append(entry)
    return entry


def apply_shadow_channel(primary_signal: dict[str, Any], shadow_data: dict[str, Any]) -> dict[str, Any]:
    safe_shadow = {k: v for k, v in shadow_data.items() if k != "interrupt_flag"}
    safe_shadow["interrupt_flag"] = False
    result = dict(primary_signal)
    result["_opacity_shadow"] = list(result.get("_opacity_shadow", [])) + [safe_shadow]
    return result

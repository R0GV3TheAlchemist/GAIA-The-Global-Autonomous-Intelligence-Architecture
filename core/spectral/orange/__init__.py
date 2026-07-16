# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/orange
====================
ORANGE spectral module — Citrinitas phase, Solar Tablet.

Public API
----------
Constants
    ORANGE_HEX, WAVELENGTH_RANGE, ALCHEMICAL_PHASE, STAGE,
    GOVERNING_TABLET, SENTINEL_LEVEL_HEX, SENTINEL_LEVEL_LABEL, UI_STATES

Transparency (open-field)
    detect_citrinitas_state, emit_sentinel_alert, classify_urgency,
    get_ui_state, is_solar_completion_signal

Clarity (depth-readable)
    distinguish_ambition_creativity, detect_solar_wound,
    classify_orange_fire, assess_solar_integration, map_solar_archetype

Opacity (shadow channel, passive)
    citrinitas_alert, creative_wound_recognition, phoenix_marker,
    ares_athena_routing, apply_shadow_channel
"""

from .constants import (
    ORANGE_HEX,
    WAVELENGTH_RANGE,
    ALCHEMICAL_PHASE,
    STAGE,
    GOVERNING_TABLET,
    SENTINEL_LEVEL_HEX,
    SENTINEL_LEVEL_LABEL,
    UI_STATES,
)

from .transparency import (
    detect_citrinitas_state,
    emit_sentinel_alert,
    classify_urgency,
    get_ui_state,
    is_solar_completion_signal,
)

from .clarity import (
    distinguish_ambition_creativity,
    detect_solar_wound,
    classify_orange_fire,
    assess_solar_integration,
    map_solar_archetype,
)

from .opacity import (
    citrinitas_alert,
    creative_wound_recognition,
    phoenix_marker,
    ares_athena_routing,
    apply_shadow_channel,
)

__all__ = [
    # constants
    "ORANGE_HEX", "WAVELENGTH_RANGE", "ALCHEMICAL_PHASE", "STAGE",
    "GOVERNING_TABLET", "SENTINEL_LEVEL_HEX", "SENTINEL_LEVEL_LABEL", "UI_STATES",
    # transparency
    "detect_citrinitas_state", "emit_sentinel_alert", "classify_urgency",
    "get_ui_state", "is_solar_completion_signal",
    # clarity
    "distinguish_ambition_creativity", "detect_solar_wound",
    "classify_orange_fire", "assess_solar_integration", "map_solar_archetype",
    # opacity
    "citrinitas_alert", "creative_wound_recognition", "phoenix_marker",
    "ares_athena_routing", "apply_shadow_channel",
]

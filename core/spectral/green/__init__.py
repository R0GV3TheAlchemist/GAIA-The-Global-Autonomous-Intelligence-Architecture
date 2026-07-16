# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
"""
core/spectral/green — Viriditas phase, Emerald Tablet.
"""
from .constants import GREEN_HEX, WAVELENGTH_RANGE, ALCHEMICAL_PHASE, STAGE, GOVERNING_TABLET, SENTINEL_LEVEL_HEX, SENTINEL_LEVEL_LABEL, UI_STATES
from .transparency import detect_viriditas_state, emit_sentinel_alert, classify_urgency, get_ui_state, is_emerald_completion_signal
from .clarity import distinguish_growth_healing, detect_earth_wound, classify_green_vitality, assess_earth_integration, map_earth_archetype
from .opacity import viriditas_alert, earth_wound_recognition, regeneration_marker, ares_athena_routing, apply_shadow_channel

__all__ = [
    "GREEN_HEX", "WAVELENGTH_RANGE", "ALCHEMICAL_PHASE", "STAGE", "GOVERNING_TABLET",
    "SENTINEL_LEVEL_HEX", "SENTINEL_LEVEL_LABEL", "UI_STATES",
    "detect_viriditas_state", "emit_sentinel_alert", "classify_urgency", "get_ui_state", "is_emerald_completion_signal",
    "distinguish_growth_healing", "detect_earth_wound", "classify_green_vitality", "assess_earth_integration", "map_earth_archetype",
    "viriditas_alert", "earth_wound_recognition", "regeneration_marker", "ares_athena_routing", "apply_shadow_channel",
]

# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
"""
core/spectral/yellow — Xanthosis phase, Amber Tablet.
"""
from .constants import (
    YELLOW_HEX, WAVELENGTH_RANGE, ALCHEMICAL_PHASE, STAGE,
    GOVERNING_TABLET, SENTINEL_LEVEL_HEX, SENTINEL_LEVEL_LABEL, UI_STATES,
)
from .transparency import (
    detect_xanthosis_state, emit_sentinel_alert, classify_urgency,
    get_ui_state, is_illumination_signal,
)
from .clarity import (
    distinguish_intellect_intuition, detect_mental_wound,
    classify_yellow_frequency, assess_mental_integration, map_mind_archetype,
)
from .opacity import (
    xanthosis_alert, mental_wound_recognition, illumination_marker,
    ares_athena_routing, apply_shadow_channel,
)

__all__ = [
    "YELLOW_HEX", "WAVELENGTH_RANGE", "ALCHEMICAL_PHASE", "STAGE",
    "GOVERNING_TABLET", "SENTINEL_LEVEL_HEX", "SENTINEL_LEVEL_LABEL", "UI_STATES",
    "detect_xanthosis_state", "emit_sentinel_alert", "classify_urgency",
    "get_ui_state", "is_illumination_signal",
    "distinguish_intellect_intuition", "detect_mental_wound",
    "classify_yellow_frequency", "assess_mental_integration", "map_mind_archetype",
    "xanthosis_alert", "mental_wound_recognition", "illumination_marker",
    "ares_athena_routing", "apply_shadow_channel",
]

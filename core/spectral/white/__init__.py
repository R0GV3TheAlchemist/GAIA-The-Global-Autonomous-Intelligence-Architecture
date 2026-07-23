# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/white/__init__.py
================================
WHITE spectral module — public API.

Alchemical Stage : Albedo — the purification and lunar reflection
Shadow (Opacity) : Bleaching / Purification as erasure
Governing Tablet : Lunar Tablet  (docs/tablets/LUNAR_TABLET.md)
"""

from .constants import (
    ALCHEMICAL_PHASE,
    GOVERNING_TABLET,
    WHITE_HEX,
    SENTINEL_LEVEL_HEX,
    SENTINEL_LEVEL_LABEL,
    STAGE,
    UI_STATES,
)
from .transparency import (
    classify_urgency,
    detect_albedo_state,
    emit_sentinel_alert,
    get_ui_state,
    is_luna_signal,
)
from .clarity import (
    assess_albedo_level,
    classify_white_fire,
    detect_bleaching_state,
    distinguish_purification_erasure,
    map_lunar_archetype,
)
from .opacity import (
    albedo_hermes_routing,
    apply_shadow_channel,
    bleaching_alert,
    lunar_reflection_marker,
    overexposure_pattern_recognition,
    purification_null_detection,
)

__all__ = [
    # constants
    "ALCHEMICAL_PHASE",
    "GOVERNING_TABLET",
    "WHITE_HEX",
    "SENTINEL_LEVEL_HEX",
    "SENTINEL_LEVEL_LABEL",
    "STAGE",
    "UI_STATES",
    # transparency
    "classify_urgency",
    "detect_albedo_state",
    "emit_sentinel_alert",
    "get_ui_state",
    "is_luna_signal",
    # clarity
    "assess_albedo_level",
    "classify_white_fire",
    "detect_bleaching_state",
    "distinguish_purification_erasure",
    "map_lunar_archetype",
    # opacity
    "albedo_hermes_routing",
    "apply_shadow_channel",
    "bleaching_alert",
    "lunar_reflection_marker",
    "overexposure_pattern_recognition",
    "purification_null_detection",
]

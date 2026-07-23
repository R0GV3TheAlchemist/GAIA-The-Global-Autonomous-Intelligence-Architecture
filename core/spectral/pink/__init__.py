# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/pink/__init__.py
==============================
PINK spectral module — public API.

Alchemical Stage : Albedo Rosa (Rosa Mystica)
Shadow (Opacity) : False Albedo / Premature Tenderness
Governing Tablet : Rose Tablet  (docs/tablets/ROSE_TABLET.md)
"""

from .constants import (
    ALCHEMICAL_PHASE,
    GOVERNING_TABLET,
    PINK_HEX,
    SENTINEL_LEVEL_HEX,
    SENTINEL_LEVEL_LABEL,
    STAGE,
    UI_STATES,
)
from .transparency import (
    classify_urgency,
    detect_rosa_mystica_state,
    emit_sentinel_alert,
    get_ui_state,
    is_rose_signal,
)
from .clarity import (
    assess_rose_level,
    classify_pink_fire,
    detect_false_albedo_state,
    distinguish_tenderness_sentimentality,
    map_rosa_archetype,
)
from .opacity import (
    apply_shadow_channel,
    false_albedo_alert,
    premature_tenderness_detection,
    rosa_hermes_routing,
    rose_denial_marker,
    sentimentality_pattern_recognition,
)

__all__ = [
    # constants
    "ALCHEMICAL_PHASE",
    "GOVERNING_TABLET",
    "PINK_HEX",
    "SENTINEL_LEVEL_HEX",
    "SENTINEL_LEVEL_LABEL",
    "STAGE",
    "UI_STATES",
    # transparency
    "classify_urgency",
    "detect_rosa_mystica_state",
    "emit_sentinel_alert",
    "get_ui_state",
    "is_rose_signal",
    # clarity
    "assess_rose_level",
    "classify_pink_fire",
    "detect_false_albedo_state",
    "distinguish_tenderness_sentimentality",
    "map_rosa_archetype",
    # opacity
    "apply_shadow_channel",
    "false_albedo_alert",
    "premature_tenderness_detection",
    "rosa_hermes_routing",
    "rose_denial_marker",
    "sentimentality_pattern_recognition",
]

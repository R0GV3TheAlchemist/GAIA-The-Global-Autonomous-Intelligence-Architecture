# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/gold/__init__.py
==============================
GOLD spectral module — public API.

Alchemical Stage : Aurum / The Philosopher's Stone (Completion)
Shadow (Opacity) : Canon ossification / Completion as stasis
Governing Tablet : Solar Tablet  (docs/tablets/SOLAR_TABLET.md)
"""

from .constants import (
    ALCHEMICAL_PHASE,
    GOVERNING_TABLET,
    GOLD_HEX,
    SENTINEL_LEVEL_HEX,
    SENTINEL_LEVEL_LABEL,
    STAGE,
    UI_STATES,
)
from .transparency import (
    classify_urgency,
    detect_aurum_state,
    emit_sentinel_alert,
    get_ui_state,
    is_gold_signal,
)
from .clarity import (
    assess_aurum_level,
    classify_gold_fire,
    detect_canon_calcification,
    distinguish_completion_ossification,
    map_solar_archetype,
)
from .opacity import (
    apply_shadow_channel,
    aurum_hermes_routing,
    canon_ossification_alert,
    false_completion_detection,
    incorruptible_marker,
    monument_pattern_recognition,
)

__all__ = [
    # constants
    "ALCHEMICAL_PHASE",
    "GOVERNING_TABLET",
    "GOLD_HEX",
    "SENTINEL_LEVEL_HEX",
    "SENTINEL_LEVEL_LABEL",
    "STAGE",
    "UI_STATES",
    # transparency
    "classify_urgency",
    "detect_aurum_state",
    "emit_sentinel_alert",
    "get_ui_state",
    "is_gold_signal",
    # clarity
    "assess_aurum_level",
    "classify_gold_fire",
    "detect_canon_calcification",
    "distinguish_completion_ossification",
    "map_solar_archetype",
    # opacity
    "apply_shadow_channel",
    "aurum_hermes_routing",
    "canon_ossification_alert",
    "false_completion_detection",
    "incorruptible_marker",
    "monument_pattern_recognition",
]

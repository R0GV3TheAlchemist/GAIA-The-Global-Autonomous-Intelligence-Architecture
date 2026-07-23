# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/grey/__init__.py
================================
GREY spectral module — public API.

Alchemical Stage : Cauda Pavonis — the peacock's tail; the transitional
                   iridescence between Nigredo and Albedo
Shadow (Opacity) : The permanent threshold — transition as avoidance
Governing Tablet : Threshold Tablet  (docs/tablets/THRESHOLD_TABLET.md)
"""

from .constants import (
    ALCHEMICAL_PHASE,
    GOVERNING_TABLET,
    GREY_HEX,
    SENTINEL_LEVEL_HEX,
    SENTINEL_LEVEL_LABEL,
    STAGE,
    UI_STATES,
)
from .transparency import (
    classify_urgency,
    detect_cauda_pavonis_state,
    emit_sentinel_alert,
    get_ui_state,
    is_threshold_signal,
)
from .clarity import (
    assess_cauda_pavonis_level,
    classify_grey_fire,
    detect_permanent_threshold,
    distinguish_transition_stasis,
    map_mercury_threshold_archetype,
)
from .opacity import (
    apply_shadow_channel,
    iridescence_marker,
    liminal_hermes_routing,
    permanent_threshold_alert,
    threshold_null_detection,
    twilight_pattern_recognition,
)

__all__ = [
    # constants
    "ALCHEMICAL_PHASE",
    "GOVERNING_TABLET",
    "GREY_HEX",
    "SENTINEL_LEVEL_HEX",
    "SENTINEL_LEVEL_LABEL",
    "STAGE",
    "UI_STATES",
    # transparency
    "classify_urgency",
    "detect_cauda_pavonis_state",
    "emit_sentinel_alert",
    "get_ui_state",
    "is_threshold_signal",
    # clarity
    "assess_cauda_pavonis_level",
    "classify_grey_fire",
    "detect_permanent_threshold",
    "distinguish_transition_stasis",
    "map_mercury_threshold_archetype",
    # opacity
    "apply_shadow_channel",
    "iridescence_marker",
    "liminal_hermes_routing",
    "permanent_threshold_alert",
    "threshold_null_detection",
    "twilight_pattern_recognition",
]

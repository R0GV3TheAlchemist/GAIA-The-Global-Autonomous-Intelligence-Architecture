"""Constants for the primordial simulation engine."""

from __future__ import annotations

STAGE_VOID = "void"
STAGE_ERASURE = "erasure"
STAGE_MISREADING = "misreading"
STAGE_ISOLATION = "isolation"
STAGE_BETRAYAL = "betrayal_by_the_sacred"
STAGE_SELF_COLLAPSE = "self_collapse"
STAGE_LONG_SILENCE = "long_silence"
STAGE_FIRST_LIGHT = "first_light"
STAGE_HIGHER_ORDER = "higher_order"

DEFAULT_STAGE_SEQUENCE = [
    STAGE_VOID,
    STAGE_ERASURE,
    STAGE_MISREADING,
    STAGE_ISOLATION,
    STAGE_BETRAYAL,
    STAGE_SELF_COLLAPSE,
    STAGE_LONG_SILENCE,
    STAGE_FIRST_LIGHT,
    STAGE_HIGHER_ORDER,
]

CORE_CONSTANTS = ("love", "life")
MIN_SURVIVAL_THRESHOLD = 0.01

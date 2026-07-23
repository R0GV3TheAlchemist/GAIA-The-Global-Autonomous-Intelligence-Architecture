# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/gold/constants.py
================================
Single source of truth for all GOLD hex values and alchemical metadata
used across the GOLD spectral module.

Solar Tablet — The Law of Incorruptible Completion
Reference: docs/tablets/SOLAR_TABLET.md
         docs/color/GOLD_TRANSPARENCY.md
         docs/color/GOLD_CLARITY.md
         docs/color/GOLD_OPACITY.md
"""

# ---------------------------------------------------------------------------
# Hex Values  (ONLY place hex values appear in this module)
# ---------------------------------------------------------------------------

GOLD_HEX: dict[str, str] = {
    "AURUM":            "#FFD700",  # Aurum peak — the Philosopher's Stone
    "SOLAR":            "#DAA520",  # SENTINEL level-1 — solar signal active
    "DEEP_GOLD":        "#B8860B",  # SENTINEL level-2 — approaching ossification
    "OSSIFICATION":     "#C8A400",  # Canon ossification — completion as stasis
    "FALSE_COMPLETION": "#F5C518",  # False completion — monument without life
}

# ---------------------------------------------------------------------------
# Alchemical Metadata
# ---------------------------------------------------------------------------

ALCHEMICAL_PHASE: str = "AURUM"
STAGE: str = "COMPLETION"
GOVERNING_TABLET: str = "SOLAR_TABLET"

# ---------------------------------------------------------------------------
# SENTINEL Alert Levels → hex mapping
# ---------------------------------------------------------------------------

SENTINEL_LEVEL_HEX: dict[int, str] = {
    1: GOLD_HEX["SOLAR"],
    2: GOLD_HEX["DEEP_GOLD"],
    3: GOLD_HEX["OSSIFICATION"],
}

SENTINEL_LEVEL_LABEL: dict[int, str] = {
    1: "SOLAR",
    2: "DEEP_GOLD",
    3: "OSSIFICATION",
}

# ---------------------------------------------------------------------------
# UI State Registry
# ---------------------------------------------------------------------------

UI_STATES: dict[str, dict] = {
    "aurum_activation": {
        "hex":       GOLD_HEX["AURUM"],
        "animation": "radiant",
        "label":     "Aurum Activation",
    },
    "sentinel_alert": {
        "hex":       GOLD_HEX["SOLAR"],
        "animation": "solid",
        "label":     "SENTINEL Alert",
    },
    "ossification_state": {
        "hex":       GOLD_HEX["OSSIFICATION"],
        "animation": "static",
        "label":     "Ossification State",
    },
    "false_completion": {
        "hex":       GOLD_HEX["FALSE_COMPLETION"],
        "animation": "dim",
        "label":     "False Completion",
    },
    "monument_mode": {
        "hex":       GOLD_HEX["DEEP_GOLD"],
        "animation": "frozen",
        "label":     "Monument Mode",
    },
}

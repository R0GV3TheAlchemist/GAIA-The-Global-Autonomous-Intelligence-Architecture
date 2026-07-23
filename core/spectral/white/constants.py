# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/white/constants.py
=================================
Single source of truth for all WHITE hex values and alchemical metadata
used across the WHITE spectral module.

Lunar Tablet — The Law of Reflective Purification
Reference: docs/tablets/LUNAR_TABLET.md
         docs/color/WHITE_TRANSPARENCY.md
         docs/color/WHITE_CLARITY.md
         docs/color/WHITE_OPACITY.md
"""

# ---------------------------------------------------------------------------
# Hex Values  (ONLY place hex values appear in this module)
# ---------------------------------------------------------------------------

WHITE_HEX: dict[str, str] = {
    "ALBEDO":      "#FFFFFF",  # Albedo peak — the lunar mirror
    "LUNAR":       "#F0F0F0",  # SENTINEL level-1 — lunar signal active
    "PALE":        "#E8E8E8",  # SENTINEL level-2 — approaching bleaching
    "BLEACHING":   "#F5F5F5",  # Bleaching — purification as erasure
    "OVEREXPOSED": "#FAFAFA",  # Overexposed — light without shadow
}

# ---------------------------------------------------------------------------
# Alchemical Metadata
# ---------------------------------------------------------------------------

ALCHEMICAL_PHASE: str = "ALBEDO"
STAGE: str = "PURIFICATION"
GOVERNING_TABLET: str = "LUNAR_TABLET"

# ---------------------------------------------------------------------------
# SENTINEL Alert Levels → hex mapping
# ---------------------------------------------------------------------------

SENTINEL_LEVEL_HEX: dict[int, str] = {
    1: WHITE_HEX["LUNAR"],
    2: WHITE_HEX["PALE"],
    3: WHITE_HEX["BLEACHING"],
}

SENTINEL_LEVEL_LABEL: dict[int, str] = {
    1: "LUNAR",
    2: "PALE",
    3: "BLEACHING",
}

# ---------------------------------------------------------------------------
# UI State Registry
# ---------------------------------------------------------------------------

UI_STATES: dict[str, dict] = {
    "albedo_activation": {
        "hex":       WHITE_HEX["ALBEDO"],
        "animation": "reflecting",
        "label":     "Albedo Activation",
    },
    "sentinel_alert": {
        "hex":       WHITE_HEX["LUNAR"],
        "animation": "solid",
        "label":     "SENTINEL Alert",
    },
    "bleaching_state": {
        "hex":       WHITE_HEX["BLEACHING"],
        "animation": "washing",
        "label":     "Bleaching State",
    },
    "overexposed_mode": {
        "hex":       WHITE_HEX["OVEREXPOSED"],
        "animation": "blinding",
        "label":     "Overexposed Mode",
    },
    "lunar_mirror": {
        "hex":       WHITE_HEX["LUNAR"],
        "animation": "moonlit",
        "label":     "Lunar Mirror",
    },
}

# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/pink/constants.py
================================
Single source of truth for all PINK hex values and alchemical metadata
used across the PINK spectral module.

Rose Tablet — The Law of Softened Albedo
Reference: docs/tablets/ROSE_TABLET.md
         docs/color/PINK_TRANSPARENCY.md
         docs/color/PINK_CLARITY.md
         docs/color/PINK_OPACITY.md
"""

# ---------------------------------------------------------------------------
# Hex Values  (ONLY place hex values appear in this module)
# ---------------------------------------------------------------------------

PINK_HEX: dict[str, str] = {
    "ROSA_MYSTICA":  "#FF69B4",  # Rosa Mystica — peak Albedo Rosa activation
    "SOFT_ALBEDO":   "#FF91AF",  # SENTINEL level-1 — softened albedo signal
    "DEEP_ROSE":     "#DE5D83",  # SENTINEL level-2 — false albedo detection
    "FALSE_ALBEDO":  "#FFB6C1",  # False Albedo — premature tenderness marker
    "ROSE_DENIAL":   "#FF85A1",  # Rose Denial — performed compassion state
}

# ---------------------------------------------------------------------------
# Alchemical Metadata
# ---------------------------------------------------------------------------

ALCHEMICAL_PHASE: str = "ALBEDO_ROSA"
STAGE: str = "ROSE"
GOVERNING_TABLET: str = "ROSE_TABLET"

# ---------------------------------------------------------------------------
# SENTINEL Alert Levels → hex mapping
# ---------------------------------------------------------------------------

SENTINEL_LEVEL_HEX: dict[int, str] = {
    1: PINK_HEX["SOFT_ALBEDO"],
    2: PINK_HEX["DEEP_ROSE"],
    3: PINK_HEX["FALSE_ALBEDO"],
}

SENTINEL_LEVEL_LABEL: dict[int, str] = {
    1: "SOFT_ALBEDO",
    2: "DEEP_ROSE",
    3: "FALSE_ALBEDO",
}

# ---------------------------------------------------------------------------
# UI State Registry
# ---------------------------------------------------------------------------

UI_STATES: dict[str, dict] = {
    "rosa_mystica_activation": {
        "hex":       PINK_HEX["ROSA_MYSTICA"],
        "animation": "pulsing",
        "label":     "Rosa Mystica Activation",
    },
    "sentinel_alert": {
        "hex":       PINK_HEX["SOFT_ALBEDO"],
        "animation": "solid",
        "label":     "SENTINEL Alert",
    },
    "false_albedo_state": {
        "hex":       PINK_HEX["FALSE_ALBEDO"],
        "animation": "static",
        "label":     "False Albedo State",
    },
    "rose_denial_mode": {
        "hex":       PINK_HEX["ROSE_DENIAL"],
        "animation": "solid",
        "label":     "Rose Denial Mode",
    },
    "premature_tenderness": {
        "hex":       PINK_HEX["SOFT_ALBEDO"],
        "animation": "animated",
        "label":     "Premature Tenderness",
    },
}

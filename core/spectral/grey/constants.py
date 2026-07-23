# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/grey/constants.py
================================
Single source of truth for all GREY hex values and alchemical metadata
used across the GREY spectral module.

Threshold Tablet — The Law of Living Transition
Reference: docs/tablets/THRESHOLD_TABLET.md
         docs/color/GREY_TRANSPARENCY.md
         docs/color/GREY_CLARITY.md
         docs/color/GREY_OPACITY.md
"""

# ---------------------------------------------------------------------------
# Hex Values  (ONLY place hex values appear in this module)
# ---------------------------------------------------------------------------

GREY_HEX: dict[str, str] = {
    "CAUDA_PAVONIS": "#808080",  # Cauda Pavonis — the transitional iridescence
    "TWILIGHT":      "#A0A0A0",  # SENTINEL level-1 — twilight signal active
    "DUSK":          "#707070",  # SENTINEL level-2 — deepening threshold
    "LIMINAL":       "#909090",  # Liminal — the permanent threshold
    "IRIDESCENT":    "#B0B0C8",  # Iridescent — the peacock's tail colour-shift
}

# ---------------------------------------------------------------------------
# Alchemical Metadata
# ---------------------------------------------------------------------------

ALCHEMICAL_PHASE: str = "CAUDA_PAVONIS"
STAGE: str = "TRANSITION"
GOVERNING_TABLET: str = "THRESHOLD_TABLET"

# ---------------------------------------------------------------------------
# SENTINEL Alert Levels → hex mapping
# ---------------------------------------------------------------------------

SENTINEL_LEVEL_HEX: dict[int, str] = {
    1: GREY_HEX["TWILIGHT"],
    2: GREY_HEX["DUSK"],
    3: GREY_HEX["LIMINAL"],
}

SENTINEL_LEVEL_LABEL: dict[int, str] = {
    1: "TWILIGHT",
    2: "DUSK",
    3: "LIMINAL",
}

# ---------------------------------------------------------------------------
# UI State Registry
# ---------------------------------------------------------------------------

UI_STATES: dict[str, dict] = {
    "cauda_pavonis_activation": {
        "hex":       GREY_HEX["CAUDA_PAVONIS"],
        "animation": "iridescent",
        "label":     "Cauda Pavonis Activation",
    },
    "sentinel_alert": {
        "hex":       GREY_HEX["TWILIGHT"],
        "animation": "solid",
        "label":     "SENTINEL Alert",
    },
    "permanent_threshold": {
        "hex":       GREY_HEX["LIMINAL"],
        "animation": "suspended",
        "label":     "Permanent Threshold",
    },
    "twilight_mode": {
        "hex":       GREY_HEX["TWILIGHT"],
        "animation": "fading",
        "label":     "Twilight Mode",
    },
    "iridescent_mode": {
        "hex":       GREY_HEX["IRIDESCENT"],
        "animation": "shifting",
        "label":     "Iridescent Mode",
    },
}

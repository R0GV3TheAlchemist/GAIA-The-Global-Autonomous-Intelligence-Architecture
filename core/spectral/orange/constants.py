# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/orange/constants.py
=================================
Single source of truth for all ORANGE hex values, wavelength bounds,
and alchemical metadata used across the ORANGE spectral module.

Solar Tablet — Law of the Becoming Sun
"""

# ---------------------------------------------------------------------------
# Hex Values
# ---------------------------------------------------------------------------

ORANGE_HEX: dict[str, str] = {
    "CITRINITAS":    "#F97316",  # Citrinitas activation — the yellowing / solar dawn
    "SOLAR_FLARE":   "#EA580C",  # SENTINEL level-1 alert
    "EMBER":         "#C2410C",  # SENTINEL level-2 — deep ember warning
    "AMBER":         "#FB923C",  # Completion signal — amber clarity
    "BLAZE":         "#FF6600",  # Error state — uncontrolled blaze
    "DAWN_GOLD":     "#FDBA74",  # Solar Becoming mode — warm creative emergence
}

# ---------------------------------------------------------------------------
# Spectral / Physical
# ---------------------------------------------------------------------------

WAVELENGTH_RANGE: tuple[int, int] = (590, 620)  # nanometres

# ---------------------------------------------------------------------------
# Alchemical Metadata
# ---------------------------------------------------------------------------

ALCHEMICAL_PHASE: str = "Citrinitas"
STAGE: int = 3
GOVERNING_TABLET: str = "Solar Tablet"

# ---------------------------------------------------------------------------
# SENTINEL Alert Levels → hex mapping
# ---------------------------------------------------------------------------

SENTINEL_LEVEL_HEX: dict[int, str] = {
    1: ORANGE_HEX["SOLAR_FLARE"],
    2: ORANGE_HEX["EMBER"],
    3: ORANGE_HEX["BLAZE"],
}

SENTINEL_LEVEL_LABEL: dict[int, str] = {
    1: "SOLAR_FLARE",
    2: "EMBER",
    3: "BLAZE",
}

# ---------------------------------------------------------------------------
# UI State Registry
# ---------------------------------------------------------------------------

UI_STATES: dict[str, dict] = {
    "citrinitas_activation": {
        "hex":       ORANGE_HEX["CITRINITAS"],
        "animation": "pulsing",
        "label":     "Citrinitas Activation",
    },
    "sentinel_alert": {
        "hex":       ORANGE_HEX["SOLAR_FLARE"],
        "animation": "solid",
        "label":     "SENTINEL Alert",
    },
    "completion_signal": {
        "hex":       ORANGE_HEX["AMBER"],
        "animation": "static",
        "label":     "Amber Completion",
    },
    "error_state": {
        "hex":       ORANGE_HEX["BLAZE"],
        "animation": "solid",
        "label":     "Error State",
    },
    "solar_becoming_mode": {
        "hex":       ORANGE_HEX["DAWN_GOLD"],
        "animation": "animated",
        "label":     "Solar Becoming Mode",
    },
}

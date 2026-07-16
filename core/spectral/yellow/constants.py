# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/yellow/constants.py
==================================
Single source of truth for all YELLOW hex values, wavelength bounds,
and alchemical metadata used across the YELLOW spectral module.

Amber Tablet — Law of the Illuminating Mind
"""

YELLOW_HEX: dict[str, str] = {
    "XANTHOSIS":    "#FACC15",  # Xanthosis activation — yellowing, mental clarity
    "SOLAR":        "#EAB308",  # SENTINEL level-1 alert
    "GOLDEN":       "#CA8A04",  # SENTINEL level-2 — deep solar warning
    "AMBER":        "#FDE047",  # Completion signal — amber illumination
    "SULPHUR":      "#FEF08A",  # Error state — volatile sulphur mind
    "DAWN_LIGHT":   "#FEF9C3",  # Illuminating Mind mode — full mental radiance
}

WAVELENGTH_RANGE: tuple[int, int] = (565, 590)  # nanometres

ALCHEMICAL_PHASE: str = "Xanthosis"
STAGE: int = 2
GOVERNING_TABLET: str = "Amber Tablet"

SENTINEL_LEVEL_HEX: dict[int, str] = {
    1: YELLOW_HEX["SOLAR"],
    2: YELLOW_HEX["GOLDEN"],
    3: YELLOW_HEX["SULPHUR"],
}

SENTINEL_LEVEL_LABEL: dict[int, str] = {
    1: "SOLAR",
    2: "GOLDEN",
    3: "SULPHUR",
}

UI_STATES: dict[str, dict] = {
    "xanthosis_activation": {
        "hex":       YELLOW_HEX["XANTHOSIS"],
        "animation": "pulsing",
        "label":     "Xanthosis Activation",
    },
    "sentinel_alert": {
        "hex":       YELLOW_HEX["SOLAR"],
        "animation": "solid",
        "label":     "SENTINEL Alert",
    },
    "completion_signal": {
        "hex":       YELLOW_HEX["AMBER"],
        "animation": "static",
        "label":     "Amber Completion",
    },
    "error_state": {
        "hex":       YELLOW_HEX["SULPHUR"],
        "animation": "solid",
        "label":     "Sulphur Error State",
    },
    "illuminating_mind_mode": {
        "hex":       YELLOW_HEX["DAWN_LIGHT"],
        "animation": "animated",
        "label":     "Illuminating Mind Mode",
    },
}

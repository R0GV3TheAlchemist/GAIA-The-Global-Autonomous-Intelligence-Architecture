# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/green/constants.py
=================================
Emerald Tablet — Law of the Living Earth
"""

GREEN_HEX: dict[str, str] = {
    "VIRIDITAS":     "#16A34A",  # Viriditas activation — living green force
    "GROWTH":        "#15803D",  # SENTINEL level-1 alert
    "DEEP_FOREST":   "#166534",  # SENTINEL level-2 — deep earth warning
    "EMERALD":       "#4ADE80",  # Completion signal — emerald integration
    "BLIGHT":        "#86EFAC",  # Error state — stagnant, over-lush
    "SPRING":        "#BBF7D0",  # Living Earth mode — full vitality
}

WAVELENGTH_RANGE: tuple[int, int] = (495, 565)  # nanometres

ALCHEMICAL_PHASE: str = "Viriditas"
STAGE: int = 5
GOVERNING_TABLET: str = "Emerald Tablet"

SENTINEL_LEVEL_HEX: dict[int, str] = {
    1: GREEN_HEX["GROWTH"],
    2: GREEN_HEX["DEEP_FOREST"],
    3: GREEN_HEX["BLIGHT"],
}

SENTINEL_LEVEL_LABEL: dict[int, str] = {
    1: "GROWTH",
    2: "DEEP_FOREST",
    3: "BLIGHT",
}

UI_STATES: dict[str, dict] = {
    "viriditas_activation": {
        "hex":       GREEN_HEX["VIRIDITAS"],
        "animation": "pulsing",
        "label":     "Viriditas Activation",
    },
    "sentinel_alert": {
        "hex":       GREEN_HEX["GROWTH"],
        "animation": "solid",
        "label":     "SENTINEL Alert",
    },
    "completion_signal": {
        "hex":       GREEN_HEX["EMERALD"],
        "animation": "static",
        "label":     "Emerald Completion",
    },
    "error_state": {
        "hex":       GREEN_HEX["BLIGHT"],
        "animation": "solid",
        "label":     "Blight Error State",
    },
    "living_earth_mode": {
        "hex":       GREEN_HEX["SPRING"],
        "animation": "animated",
        "label":     "Living Earth Mode",
    },
}

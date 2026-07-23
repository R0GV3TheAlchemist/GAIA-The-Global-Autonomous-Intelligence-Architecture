# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/white/clarity.py
===============================
WHITE — Clarity Layer

Clarity reads what transparency presents and discriminates genuine
Albedo (purification that preserves texture) from bleaching
(purification that erases everything) and overexposure (light
so absolute it renders the world invisible).

The central question of white clarity:
  "Is this purification refining the real, or
   washing it out of existence entirely?"

Reference: docs/color/WHITE_CLARITY.md
           Lunar Tablet — docs/tablets/LUNAR_TABLET.md
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Purification vs Erasure Discrimination
# ---------------------------------------------------------------------------

def distinguish_purification_erasure(signal: dict) -> str:
    """
    Discriminate between genuine purification (Albedo) and erasure (bleaching).

    Purification refines without destroying texture.
    Erasure removes everything — impurity and substance alike.

    Decision logic:
      - 'texture' >= 0.50 AND 'contrast' >= 0.40  → 'purification'
      - Otherwise                                   → 'erasure'

    Parameters
    ----------
    signal : dict
        Keys: 'texture' (float), 'contrast' (float).

    Returns
    -------
    str
        'purification' or 'erasure'.
    """
    if not signal:
        return "erasure"

    texture  = float(signal.get("texture",  0.0))
    contrast = float(signal.get("contrast", 0.0))

    if texture >= 0.50 and contrast >= 0.40:
        return "purification"
    return "erasure"


# ---------------------------------------------------------------------------
# Bleaching State Detection
# ---------------------------------------------------------------------------

def detect_bleaching_state(signal: dict) -> bool:
    """
    Detect bleaching — the state where purification has consumed
    all texture and contrast, leaving only white absence.

    Bleaching markers:
      - 'purification' >= 0.90
      - 'texture'      < 0.30
      - 'contrast'     < 0.25

    All three must be simultaneously true.

    Parameters
    ----------
    signal : dict

    Returns
    -------
    bool
    """
    if not signal:
        return False

    purification = float(signal.get("purification", 0.0))
    texture      = float(signal.get("texture",      1.0))
    contrast     = float(signal.get("contrast",     1.0))

    return purification >= 0.90 and texture < 0.30 and contrast < 0.25


# ---------------------------------------------------------------------------
# White Fire Classification
# ---------------------------------------------------------------------------

def classify_white_fire(signal: dict) -> str:
    """
    Classify the quality of the white fire in the signal.

    White fire types (priority order):
      1. 'albedo'      — genuine purification, the lunar mirror
      2. 'bleaching'   — purification that has become erasure
      3. 'overexposed' — light so absolute the world disappears
      4. 'pale'        — approaching bleaching, colour draining
      5. 'dim_white'   — white signal present but barely active

    Parameters
    ----------
    signal : dict

    Returns
    -------
    str
    """
    if not signal:
        return "dim_white"

    if signal.get("albedo"):
        return "albedo"
    if signal.get("bleaching"):
        return "bleaching"
    if signal.get("overexposed"):
        return "overexposed"
    if signal.get("pale"):
        return "pale"
    return "dim_white"


# ---------------------------------------------------------------------------
# Albedo Level Assessment
# ---------------------------------------------------------------------------

def assess_albedo_level(signal: dict) -> float:
    """
    Compute a normalised albedo activation level [0.0, 1.0].

    Weighted mean of:
      - purification_score  (weight 0.40)
      - reflection_score    (weight 0.35)
      - texture_score       (weight 0.25)

    Parameters
    ----------
    signal : dict

    Returns
    -------
    float  in [0.0, 1.0]
    """
    if not signal:
        return 0.0

    p = float(signal.get("purification_score", 0.0))
    r = float(signal.get("reflection_score",   0.0))
    t = float(signal.get("texture_score",      0.0))

    level = (p * 0.40) + (r * 0.35) + (t * 0.25)
    return max(0.0, min(1.0, level))


# ---------------------------------------------------------------------------
# Lunar Archetype Mapping
# ---------------------------------------------------------------------------

_LUNAR_ARCHETYPES: dict[str, str] = {
    "albedo":      "Albedo — the lunar mirror; purification that preserves what it purifies",
    "bleaching":   "Bleaching — the white that erases; purification become destruction of texture",
    "overexposed": "Overexposed — light without shadow; so much clarity the world disappears",
    "pale":        "Pale — the draining colour; Albedo not yet bleaching but the texture thinning",
    "dim_white":   "Dim White — the signal barely present beneath the surface",
}


def map_lunar_archetype(fire_type: str) -> str:
    """
    Return the canonical Lunar archetype description for a given fire type.

    Uses shared vocabulary: 'luna' as the ruling archetype of the white domain.
    Pairs with 'hermes' routing in opacity.py.

    Parameters
    ----------
    fire_type : str

    Returns
    -------
    str
    """
    fire_type = str(fire_type).strip() if fire_type else ""
    return _LUNAR_ARCHETYPES.get(fire_type, _LUNAR_ARCHETYPES["dim_white"])

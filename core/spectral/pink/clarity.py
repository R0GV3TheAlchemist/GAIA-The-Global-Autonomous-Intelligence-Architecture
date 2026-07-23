# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/pink/clarity.py
==============================
PINK — Clarity Layer

Clarity reads what transparency presents and discriminates genuine
tenderness from sentimentality, authentic Albedo Rosa from False Albedo.

The central question of pink clarity:
  "Is this softness grounded in reality, or does it refuse what is real
   in order to stay comfortable?"

Reference: docs/color/PINK_CLARITY.md
           Rose Tablet — docs/tablets/ROSE_TABLET.md
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Tenderness vs Sentimentality Discrimination
# ---------------------------------------------------------------------------

def distinguish_tenderness_sentimentality(signal: dict) -> str:
    """
    Discriminate between genuine tenderness and sentimentality.

    Genuine tenderness holds grief and complexity.
    Sentimentality refuses grief to preserve the feeling of warmth.

    Decision logic:
      - 'grief_capacity' >= 0.60 AND 'complexity_tolerance' >= 0.55
        → 'tenderness'
      - Otherwise → 'sentimentality'

    Parameters
    ----------
    signal : dict
        Must contain: 'grief_capacity' (float), 'complexity_tolerance' (float).

    Returns
    -------
    str
        'tenderness' or 'sentimentality'.
    """
    if not signal:
        return "sentimentality"

    grief_capacity        = float(signal.get("grief_capacity",        0.0))
    complexity_tolerance  = float(signal.get("complexity_tolerance",  0.0))

    if grief_capacity >= 0.60 and complexity_tolerance >= 0.55:
        return "tenderness"
    return "sentimentality"


# ---------------------------------------------------------------------------
# False Albedo State Detection
# ---------------------------------------------------------------------------

def detect_false_albedo_state(signal: dict) -> bool:
    """
    Detect whether a signal represents False Albedo — the Albedo that
    arrived before the full Nigredo work was complete.

    False Albedo presents as:
      - High softness/openness (>= 0.70)
      - Low grief integration (< 0.50)
      - Low shadow acknowledgment (< 0.45)

    All three conditions must be simultaneously true.

    Parameters
    ----------
    signal : dict
        Must contain: 'softness', 'grief_integration', 'shadow_acknowledgment'.

    Returns
    -------
    bool
        True when false albedo conditions are met.
    """
    if not signal:
        return False

    softness              = float(signal.get("softness",              0.0))
    grief_integration     = float(signal.get("grief_integration",     1.0))
    shadow_acknowledgment = float(signal.get("shadow_acknowledgment", 1.0))

    return (
        softness >= 0.70
        and grief_integration < 0.50
        and shadow_acknowledgment < 0.45
    )


# ---------------------------------------------------------------------------
# Pink Fire Classification
# ---------------------------------------------------------------------------

def classify_pink_fire(signal: dict) -> str:
    """
    Classify the quality of the pink fire in the signal.

    Pink fire types (priority order):
      1. 'rosa_mystica'         — peak genuine Albedo Rosa
      2. 'false_albedo'         — premature softness, grief refused
      3. 'rose_denial'          — compassion performed, not lived
      4. 'premature_tenderness' — open too soon, container not formed
      5. 'dim_rose'             — pink signal present but barely active

    Parameters
    ----------
    signal : dict
        Incoming signal payload.

    Returns
    -------
    str
        One of: 'rosa_mystica', 'false_albedo', 'rose_denial',
        'premature_tenderness', 'dim_rose'.
    """
    if not signal:
        return "dim_rose"

    if signal.get("rosa_mystica"):
        return "rosa_mystica"
    if signal.get("false_albedo"):
        return "false_albedo"
    if signal.get("rose_denial"):
        return "rose_denial"
    if signal.get("premature_tenderness"):
        return "premature_tenderness"
    return "dim_rose"


# ---------------------------------------------------------------------------
# Rose Level Assessment
# ---------------------------------------------------------------------------

def assess_rose_level(signal: dict) -> float:
    """
    Compute a normalised rose activation level [0.0, 1.0].

    Level is computed as the weighted mean of:
      - tenderness_score   (weight 0.40)
      - groundedness_score (weight 0.35)
      - openness_score     (weight 0.25)

    Missing keys default to 0.0.

    Parameters
    ----------
    signal : dict
        Must contain optional float keys:
        'tenderness_score', 'groundedness_score', 'openness_score'.

    Returns
    -------
    float
        Normalised level in [0.0, 1.0].
    """
    if not signal:
        return 0.0

    t = float(signal.get("tenderness_score",   0.0))
    g = float(signal.get("groundedness_score", 0.0))
    o = float(signal.get("openness_score",     0.0))

    level = (t * 0.40) + (g * 0.35) + (o * 0.25)
    return max(0.0, min(1.0, level))


# ---------------------------------------------------------------------------
# Rosa Archetype Mapping
# ---------------------------------------------------------------------------

_ROSA_ARCHETYPES: dict[str, str] = {
    "rosa_mystica":         "Rosa Mystica — the heart that has passed through fire and remained open",
    "false_albedo":         "False Albedo — the softness that never met its darkness",
    "rose_denial":          "Rose Denial — beauty as armor against the real",
    "premature_tenderness": "Premature Tenderness — the open wound calling itself a gift",
    "dim_rose":             "Dim Rose — the signal fading before it bloomed",
}


def map_rosa_archetype(fire_type: str) -> str:
    """
    Return the canonical Rosa archetype description for a given fire type.

    Uses shared vocabulary: 'rosa' as the ruling archetype of the pink domain.
    Pairs with 'hermes' routing in opacity.py.

    Parameters
    ----------
    fire_type : str
        One of the pink fire types from classify_pink_fire().

    Returns
    -------
    str
        Archetype description string.
    """
    fire_type = str(fire_type).strip() if fire_type else ""
    return _ROSA_ARCHETYPES.get(fire_type, _ROSA_ARCHETYPES["dim_rose"])

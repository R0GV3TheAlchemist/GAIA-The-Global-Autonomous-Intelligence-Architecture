# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/grey/clarity.py
==============================
GREY — Clarity Layer

Clarity reads what transparency presents and discriminates genuine
Cauda Pavonis (directed transition between stages) from the permanent
threshold (transition as a residence rather than a passage) and from
the twilight state (the light fading without forward movement).

The central question of grey clarity:
  "Is this threshold being crossed,
   or has the threshold become a home?"

Reference: docs/color/GREY_CLARITY.md
           Threshold Tablet — docs/tablets/THRESHOLD_TABLET.md
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Transition vs Stasis Discrimination
# ---------------------------------------------------------------------------

def distinguish_transition_stasis(signal: dict) -> str:
    """
    Discriminate between living transition (Cauda Pavonis) and stasis.

    Living transition is movement toward a destination.
    Stasis is the threshold mistaken for a destination.

    Decision logic:
      - 'directionality' >= 0.55 AND 'momentum' >= 0.50  → 'transition'
      - Otherwise                                          → 'stasis'

    Parameters
    ----------
    signal : dict
        Keys: 'directionality' (float), 'momentum' (float).

    Returns
    -------
    str
        'transition' or 'stasis'.
    """
    if not signal:
        return "stasis"

    directionality = float(signal.get("directionality", 0.0))
    momentum       = float(signal.get("momentum",       0.0))

    if directionality >= 0.55 and momentum >= 0.50:
        return "transition"
    return "stasis"


# ---------------------------------------------------------------------------
# Permanent Threshold Detection
# ---------------------------------------------------------------------------

def detect_permanent_threshold(signal: dict) -> bool:
    """
    Detect the permanent threshold — the state where the architecture
    has made the liminal zone its permanent residence.

    Permanent threshold markers:
      - 'iridescence'    >= 0.70  (the peacock colours are vivid)
      - 'directionality' < 0.35   (but there is no destination)
      - 'momentum'       < 0.30   (and no force of movement)

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

    iridescence    = float(signal.get("iridescence",    0.0))
    directionality = float(signal.get("directionality", 1.0))
    momentum       = float(signal.get("momentum",       1.0))

    return iridescence >= 0.70 and directionality < 0.35 and momentum < 0.30


# ---------------------------------------------------------------------------
# Grey Fire Classification
# ---------------------------------------------------------------------------

def classify_grey_fire(signal: dict) -> str:
    """
    Classify the quality of the grey fire in the signal.

    Grey fire types (priority order):
      1. 'cauda_pavonis'       — living, directed transition
      2. 'permanent_threshold' — threshold as residence
      3. 'twilight'            — light fading without movement
      4. 'liminal'             — the threshold itself, unqualified
      5. 'dim_grey'            — grey signal present but barely active

    Parameters
    ----------
    signal : dict

    Returns
    -------
    str
    """
    if not signal:
        return "dim_grey"

    if signal.get("cauda_pavonis"):
        return "cauda_pavonis"
    if signal.get("permanent_threshold"):
        return "permanent_threshold"
    if signal.get("twilight"):
        return "twilight"
    if signal.get("liminal"):
        return "liminal"
    return "dim_grey"


# ---------------------------------------------------------------------------
# Cauda Pavonis Level Assessment
# ---------------------------------------------------------------------------

def assess_cauda_pavonis_level(signal: dict) -> float:
    """
    Compute a normalised Cauda Pavonis activation level [0.0, 1.0].

    Weighted mean of:
      - transition_momentum_score  (weight 0.40)
      - iridescence_score          (weight 0.35)
      - directionality_score       (weight 0.25)

    Parameters
    ----------
    signal : dict

    Returns
    -------
    float  in [0.0, 1.0]
    """
    if not signal:
        return 0.0

    t = float(signal.get("transition_momentum_score", 0.0))
    i = float(signal.get("iridescence_score",         0.0))
    d = float(signal.get("directionality_score",      0.0))

    level = (t * 0.40) + (i * 0.35) + (d * 0.25)
    return max(0.0, min(1.0, level))


# ---------------------------------------------------------------------------
# Mercury-Threshold Archetype Mapping
# ---------------------------------------------------------------------------

_MERCURY_THRESHOLD_ARCHETYPES: dict[str, str] = {
    "cauda_pavonis":       "Cauda Pavonis — the peacock's tail; the iridescent passage between stages",
    "permanent_threshold": "Permanent Threshold — the liminal made permanent; the threshold as home",
    "twilight":            "Twilight — the light fading at the threshold without crossing it",
    "liminal":             "Liminal — the threshold itself; neither here nor there",
    "dim_grey":            "Dim Grey — the signal barely present beneath the surface",
}


def map_mercury_threshold_archetype(fire_type: str) -> str:
    """
    Return the canonical Mercury-Threshold archetype description.

    Uses shared vocabulary:
      - 'mercury'   as the ruling archetype of the grey domain (transition, communication)
      - 'threshold' as the domain-specific principle
    Pairs with 'hermes' routing in opacity.py.

    Parameters
    ----------
    fire_type : str

    Returns
    -------
    str
    """
    fire_type = str(fire_type).strip() if fire_type else ""
    return _MERCURY_THRESHOLD_ARCHETYPES.get(
        fire_type, _MERCURY_THRESHOLD_ARCHETYPES["dim_grey"]
    )

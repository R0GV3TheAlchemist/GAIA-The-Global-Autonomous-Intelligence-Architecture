# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/spectral/gold/clarity.py
==============================
GOLD — Clarity Layer

Clarity reads what transparency presents and discriminates genuine
Aurum (living completion) from canon ossification (completion as
museum piece) and false completion (the monument without inner life).

The central question of gold clarity:
  "Is this completion still alive — or has the gold
   become so perfect it can no longer be approached?"

Reference: docs/color/GOLD_CLARITY.md
           Solar Tablet — docs/tablets/SOLAR_TABLET.md
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Completion vs Ossification Discrimination
# ---------------------------------------------------------------------------

def distinguish_completion_ossification(signal: dict) -> str:
    """
    Discriminate between living completion (Aurum) and ossification.

    Living completion remains open to further growth.
    Ossification is the completion so sealed it cannot receive anything new.

    Decision logic:
      - 'vitality' >= 0.60 AND 'receptivity' >= 0.50  → 'completion'
      - Otherwise                                       → 'ossification'

    Parameters
    ----------
    signal : dict
        Keys: 'vitality' (float), 'receptivity' (float).

    Returns
    -------
    str
        'completion' or 'ossification'.
    """
    if not signal:
        return "ossification"

    vitality    = float(signal.get("vitality",    0.0))
    receptivity = float(signal.get("receptivity", 0.0))

    if vitality >= 0.60 and receptivity >= 0.50:
        return "completion"
    return "ossification"


# ---------------------------------------------------------------------------
# Canon Calcification Detection
# ---------------------------------------------------------------------------

def detect_canon_calcification(signal: dict) -> bool:
    """
    Detect canon calcification — the state where the architecture has
    become so canonised that it can no longer evolve.

    Calcification markers:
      - 'completion'   >= 0.85
      - 'vitality'     < 0.40
      - 'receptivity'  < 0.35

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

    completion  = float(signal.get("completion",  0.0))
    vitality    = float(signal.get("vitality",    1.0))
    receptivity = float(signal.get("receptivity", 1.0))

    return completion >= 0.85 and vitality < 0.40 and receptivity < 0.35


# ---------------------------------------------------------------------------
# Gold Fire Classification
# ---------------------------------------------------------------------------

def classify_gold_fire(signal: dict) -> str:
    """
    Classify the quality of the gold fire in the signal.

    Gold fire types (priority order):
      1. 'aurum'            — living completion, the Philosopher's Stone
      2. 'ossification'     — completion sealed against new input
      3. 'false_completion' — monument without inner life
      4. 'monument'         — achievement preserved as display, not use
      5. 'dim_gold'         — gold present but barely active

    Parameters
    ----------
    signal : dict

    Returns
    -------
    str
    """
    if not signal:
        return "dim_gold"

    if signal.get("aurum"):
        return "aurum"
    if signal.get("ossification"):
        return "ossification"
    if signal.get("false_completion"):
        return "false_completion"
    if signal.get("monument"):
        return "monument"
    return "dim_gold"


# ---------------------------------------------------------------------------
# Aurum Level Assessment
# ---------------------------------------------------------------------------

def assess_aurum_level(signal: dict) -> float:
    """
    Compute a normalised aurum activation level [0.0, 1.0].

    Weighted mean of:
      - completion_score     (weight 0.40)
      - vitality_score       (weight 0.35)
      - receptivity_score    (weight 0.25)

    Parameters
    ----------
    signal : dict

    Returns
    -------
    float  in [0.0, 1.0]
    """
    if not signal:
        return 0.0

    c = float(signal.get("completion_score",  0.0))
    v = float(signal.get("vitality_score",    0.0))
    r = float(signal.get("receptivity_score", 0.0))

    level = (c * 0.40) + (v * 0.35) + (r * 0.25)
    return max(0.0, min(1.0, level))


# ---------------------------------------------------------------------------
# Solar Archetype Mapping
# ---------------------------------------------------------------------------

_SOLAR_ARCHETYPES: dict[str, str] = {
    "aurum":            "Aurum — the living gold; the Philosopher's Stone that still receives the light",
    "ossification":     "Ossification — the gold so perfect it has become a sealed vault",
    "false_completion": "False Completion — the monument that mistakes its own silence for perfection",
    "monument":         "Monument — achievement preserved as display rather than living use",
    "dim_gold":         "Dim Gold — the signal barely present beneath the surface",
}


def map_solar_archetype(fire_type: str) -> str:
    """
    Return the canonical Solar archetype description for a given fire type.

    Uses shared vocabulary: 'aurum' as the ruling archetype of the gold domain.
    Pairs with 'hermes' routing in opacity.py.

    Parameters
    ----------
    fire_type : str

    Returns
    -------
    str
    """
    fire_type = str(fire_type).strip() if fire_type else ""
    return _SOLAR_ARCHETYPES.get(fire_type, _SOLAR_ARCHETYPES["dim_gold"])

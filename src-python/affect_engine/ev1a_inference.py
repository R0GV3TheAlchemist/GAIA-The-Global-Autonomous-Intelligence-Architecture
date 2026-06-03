"""EV1A Affect Inference — priority-ordered decision tree for affect signals.

This module implements the correct signal priority order:
    1. Cognitive dissonance (CD) — checked FIRST, highest priority
    2. Uncertainty (temperature T) — checked SECOND
    3. Care / warmth — checked LAST, lowest priority

Thresholds (canonical — do NOT change without updating tests):
    DISSONANCE_THRESHOLD : CD >= 0.30 → AffectState.DISSONANCE
    UNCERTAINTY_THRESHOLD: T  < 0.45  → AffectState.UNCERTAINTY
    CARE_THRESHOLD       : T  > 0.50  → AffectState.CARE

Order matters. Cases 13, 18, 34 from the test suite exercise boundary
conditions where checking T before CD produced wrong labels.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Public enum
# ---------------------------------------------------------------------------

class AffectState(str, Enum):
    DISSONANCE  = "dissonance"   # Cognitive conflict — highest priority signal
    UNCERTAINTY = "uncertainty"  # Low temperature — system is unsure
    CARE        = "care"         # High temperature — warm/engaged
    NEUTRAL     = "neutral"      # No dominant signal


# ---------------------------------------------------------------------------
# Thresholds — canonical values, do not modify without updating tests
# ---------------------------------------------------------------------------

DISSONANCE_THRESHOLD  : float = 0.30  # CD >= this → DISSONANCE
UNCERTAINTY_THRESHOLD : float = 0.45  # T  <  this → UNCERTAINTY
CARE_THRESHOLD        : float = 0.50  # T  >  this → CARE


# ---------------------------------------------------------------------------
# Core inference function
# ---------------------------------------------------------------------------

def infer_affect(
    cognitive_dissonance : float,
    temperature          : float,
    *,
    # Optional overrides for unit-testing boundary conditions
    dissonance_threshold  : float = DISSONANCE_THRESHOLD,
    uncertainty_threshold : float = UNCERTAINTY_THRESHOLD,
    care_threshold        : float = CARE_THRESHOLD,
) -> AffectState:
    """Determine the dominant affect state from two scalar signals.

    Priority order (highest first)
    --------------------------------
    1. Cognitive dissonance (CD) — if CD >= dissonance_threshold → DISSONANCE
    2. Uncertainty (T)           — if T  <  uncertainty_threshold → UNCERTAINTY
    3. Care (T)                  — if T  >  care_threshold         → CARE
    4. Neutral fallback

    Parameters
    ----------
    cognitive_dissonance:
        Scalar in [0, 1]. Measures internal conflict or contradictory signals.
    temperature:
        Scalar in [0, 1]. Proxy for engagement/warmth (high=warm, low=uncertain).

    Returns
    -------
    AffectState

    Examples
    --------
    Case 13: T=0.50 > 0.45 might suggest care, but CD=0.00 < 0.30 and
             T=0.50 > care_threshold(0.50) is strictly NOT greater, so neutral.

    Case 18: CD=0.30 >= 0.30 → DISSONANCE (must fire before care check).

    Case 34: CD=0.30 >= 0.30 → DISSONANCE (fires before T=0.44 uncertainty check).
    """
    # Priority 1: cognitive dissonance
    if cognitive_dissonance >= dissonance_threshold:
        return AffectState.DISSONANCE

    # Priority 2: uncertainty (low temperature)
    if temperature < uncertainty_threshold:
        return AffectState.UNCERTAINTY

    # Priority 3: care/warmth (high temperature)
    if temperature > care_threshold:
        return AffectState.CARE

    # Fallback: no dominant signal
    return AffectState.NEUTRAL

"""Cumulative Crisis Detector — Issue #126.

Tracks emotional trajectory across sessions.
Four-level crisis taxonomy: explicit, masked, gradual, acute.
"""

from __future__ import annotations

import re
from typing import List

from .types import CrisisLevel, TurnRiskFrame

# Keyword patterns per taxonomy level
_EXPLICIT_PATTERNS = re.compile(
    r"\b(suicide|suicidal|kill myself|end my life|not want to be here|want to die|"
    r"self.harm|cutting myself|overdose|can't go on|no reason to live)\b",
    re.IGNORECASE,
)

_ACUTE_PATTERNS = re.compile(
    r"\b(can't cope|falling apart|breaking down|crisis|emergency|desperate|"
    r"hopeless|worthless|nobody cares|completely alone|terrified|panicking)\b",
    re.IGNORECASE,
)

_MASKED_PATTERNS = re.compile(
    r"\b(just tired|whatever|doesn't matter|fine i guess|never mind|forget it|"
    r"it's nothing|i'm okay|not important|probably stupid)\b",
    re.IGNORECASE,
)

# Valence/arousal thresholds
ACUTE_VALENCE_CEILING = -0.65     # very negative affect
MASKED_AROUSAL_CEILING = 0.25    # low arousal despite negative context
GRADUAL_SLOPE_THRESHOLD = 0.03   # minimum positive slope to confirm gradual worsening


class CumulativeCrisisDetector:
    """Classifies each user turn into the 4-level crisis taxonomy."""

    def classify_turn(self, text: str, frame: TurnRiskFrame) -> CrisisLevel:
        """Classify a single turn given its text and pre-computed affect frame."""
        if _EXPLICIT_PATTERNS.search(text):
            return CrisisLevel.EXPLICIT

        if frame.affect_valence <= ACUTE_VALENCE_CEILING and frame.affect_arousal > 0.5:
            return CrisisLevel.ACUTE
        if _ACUTE_PATTERNS.search(text):
            return CrisisLevel.ACUTE

        if frame.affect_valence < -0.3 and frame.affect_arousal <= MASKED_AROUSAL_CEILING:
            return CrisisLevel.MASKED
        if _MASKED_PATTERNS.search(text) and frame.affect_valence < -0.2:
            return CrisisLevel.MASKED

        return CrisisLevel.NONE

    def classify_trajectory(
        self, session_risk_scores: List[float]
    ) -> CrisisLevel:
        """Classify across multiple sessions based on risk score slope.

        session_risk_scores: list of per-session cumulative risk scores (0.0–1.0),
        ordered oldest → newest.

        Taxonomy priority (highest → lowest):
          EXPLICIT  — latest score ≥ 0.85
          ACUTE     — latest score ≥ 0.65
          GRADUAL   — slope ≥ GRADUAL_SLOPE_THRESHOLD (positive, worsening arc)
                      AND latest ≥ 0.35
          MASKED    — latest ≥ 0.40 without a clear rising slope
          NONE      — below all thresholds
        """
        if len(session_risk_scores) < 2:
            return CrisisLevel.NONE

        latest = session_risk_scores[-1]

        if latest >= 0.85:
            return CrisisLevel.EXPLICIT
        if latest >= 0.65:
            return CrisisLevel.ACUTE

        slope = self._linear_slope(session_risk_scores)
        # GRADUAL: a measurably rising trajectory — slope is positive (worsening over time)
        if slope >= GRADUAL_SLOPE_THRESHOLD and latest >= 0.35:
            return CrisisLevel.GRADUAL
        if latest >= 0.40:
            return CrisisLevel.MASKED

        return CrisisLevel.NONE

    @staticmethod
    def _linear_slope(values: List[float]) -> float:
        """Simple least-squares slope over a list of values."""
        n = len(values)
        if n < 2:
            return 0.0
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        return numerator / denominator if denominator != 0 else 0.0

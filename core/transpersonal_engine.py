"""
Transpersonal Engine — models transpersonal states and readings in GAIA.

Provides TranspersonalReading dataclass and TranspersonalEngine class.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

log = logging.getLogger(__name__)


# Keywords that elevate state toward LIMINAL / PEAK / MYSTICAL
_NUMINOUS_KEYWORDS = [
    "dissolution", "pure awareness", "transcend", "unity", "sacred",
    "profound", "mystical", "oneness", "infinite", "void", "bliss",
    "ego death", "presence", "boundless", "formless",
]


class TranspersonalState(str, Enum):
    ORDINARY = "ordinary"
    LIMINAL  = "liminal"
    PEAK     = "peak"
    MYSTICAL = "mystical"
    UNITY    = "unity"


# Suggested response posture per state
_POSTURE: dict = {
    TranspersonalState.ORDINARY: "engage",
    TranspersonalState.LIMINAL:  "attune",
    TranspersonalState.PEAK:     "witness",
    TranspersonalState.MYSTICAL: "hold space",
    TranspersonalState.UNITY:    "silence",
}


@dataclass
class TranspersonalReading:
    """A single transpersonal state reading."""

    state:            TranspersonalState = TranspersonalState.ORDINARY
    intensity:        float = 0.0
    duration_seconds: float = 0.0
    triggers:         List[str] = field(default_factory=list)
    response_posture: str = "engage"       # added for soul_mirror tests
    metadata:         dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "state":            self.state.value,
            "intensity":        self.intensity,
            "duration_seconds": self.duration_seconds,
            "triggers":         self.triggers,
            "response_posture": self.response_posture,
            "metadata":         self.metadata,
        }


class TranspersonalEngine:
    """Tracks and models transpersonal states over time."""

    def __init__(self) -> None:
        self._readings: List[TranspersonalReading] = []
        log.info("TranspersonalEngine initialised")

    # ------------------------------------------------------------------
    # NEW: context-dict API (used by soul_mirror tests)
    # ------------------------------------------------------------------
    def detect(self, context: dict) -> TranspersonalReading:
        """
        Detect a transpersonal state from a context dict.

        Recognised keys:
          - turn_text (str | None): free-text from the current turn
        """
        text = context.get("turn_text") or ""
        if text is None:
            text = ""
        text_lower = str(text).lower()

        hit_count = sum(1 for kw in _NUMINOUS_KEYWORDS if kw in text_lower)

        if hit_count == 0:
            state     = TranspersonalState.ORDINARY
            intensity = 0.0
        elif hit_count == 1:
            state     = TranspersonalState.LIMINAL
            intensity = 0.25
        elif hit_count == 2:
            state     = TranspersonalState.PEAK
            intensity = 0.55
        elif hit_count == 3:
            state     = TranspersonalState.MYSTICAL
            intensity = 0.80
        else:
            state     = TranspersonalState.UNITY
            intensity = 1.0

        triggers = [kw for kw in _NUMINOUS_KEYWORDS if kw in text_lower]

        reading = TranspersonalReading(
            state=state,
            intensity=max(0.0, min(1.0, intensity)),
            triggers=triggers,
            response_posture=_POSTURE.get(state, "engage"),
        )
        self._readings.append(reading)
        return reading

    # ------------------------------------------------------------------
    # Original API
    # ------------------------------------------------------------------
    def record(
        self,
        state:            TranspersonalState = TranspersonalState.ORDINARY,
        intensity:        float = 0.0,
        duration_seconds: float = 0.0,
        triggers:         Optional[List[str]] = None,
    ) -> TranspersonalReading:
        reading = TranspersonalReading(
            state=state,
            intensity=max(0.0, min(1.0, intensity)),
            duration_seconds=duration_seconds,
            triggers=triggers or [],
            response_posture=_POSTURE.get(state, "engage"),
        )
        self._readings.append(reading)
        return reading

    def get_readings(
        self, state: Optional[TranspersonalState] = None
    ) -> List[TranspersonalReading]:
        if state is None:
            return list(self._readings)
        return [r for r in self._readings if r.state == state]

    def reset(self) -> None:
        self._readings.clear()

    def to_dict(self) -> dict:
        return {"reading_count": len(self._readings)}


_engine: Optional[TranspersonalEngine] = None


def get_transpersonal_engine() -> TranspersonalEngine:
    global _engine
    if _engine is None:
        _engine = TranspersonalEngine()
    return _engine

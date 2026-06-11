"""
Individuation Engine — models Jungian individuation arc for GAIA users.

Provides:
  - IndividuationScore  : dataclass holding a user's current score
  - IndividuationEngine : main class
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

log = logging.getLogger(__name__)


class IndividuationPhase(str, Enum):
    SHADOW_WORK = "shadow_work"
    ANIMA_ANIMUS = "anima_animus"
    SELF_ENCOUNTER = "self_encounter"
    INTEGRATION = "integration"
    WHOLENESS = "wholeness"


@dataclass
class IndividuationScore:
    """Captures the multi-dimensional individuation state of a user."""

    user_id: str = ""
    phase: IndividuationPhase = IndividuationPhase.SHADOW_WORK
    overall: float = 0.0          # 0.0 – 1.0
    shadow: float = 0.0
    anima_animus: float = 0.0
    self_realisation: float = 0.0
    integration: float = 0.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, float] = field(default_factory=dict)

    # --- convenience aliases used by soul_mirror tests ---
    @property
    def value(self) -> float:
        """Alias for overall; 0.0–1.0 individuation score."""
        return self.overall

    @property
    def stage(self) -> str:
        """Human-readable label for the current individuation phase."""
        return self.phase.value.replace("_", " ").title()

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "phase": self.phase.value,
            "overall": self.overall,
            "value": self.overall,
            "stage": self.stage,
            "shadow": self.shadow,
            "anima_animus": self.anima_animus,
            "self_realisation": self.self_realisation,
            "integration": self.integration,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class IndividuationEngine:
    """Tracks and updates individuation scores for users."""

    def __init__(self) -> None:
        self._scores: Dict[str, IndividuationScore] = {}
        log.info("IndividuationEngine initialised")

    def score(self, context: dict) -> IndividuationScore:
        """
        Derive an IndividuationScore from a context dict.

        Recognised context keys:
          - integration_level (float 0–1): influences the overall score
          - shadow_active (bool | None): boosts shadow dimension if truthy
          - user_id (str): optional; defaults to '_default'
        """
        user_id = context.get("user_id", "_default") or "_default"
        integration_level = context.get("integration_level")
        shadow_active = context.get("shadow_active")

        s = self.get_score(user_id)

        if integration_level is not None:
            try:
                level = float(integration_level)
            except (TypeError, ValueError):
                level = 0.0
            s.integration = max(0.0, min(1.0, level))
            s.self_realisation = max(0.0, min(1.0, level * 0.8))

        if shadow_active:
            s.shadow = min(1.0, s.shadow + 0.2)

        s.overall = (
            s.shadow + s.anima_animus + s.self_realisation + s.integration
        ) / 4.0

        # derive phase
        if s.overall < 0.25:
            s.phase = IndividuationPhase.SHADOW_WORK
        elif s.overall < 0.50:
            s.phase = IndividuationPhase.ANIMA_ANIMUS
        elif s.overall < 0.70:
            s.phase = IndividuationPhase.SELF_ENCOUNTER
        elif s.overall < 0.90:
            s.phase = IndividuationPhase.INTEGRATION
        else:
            s.phase = IndividuationPhase.WHOLENESS

        return s

    def get_score(self, user_id: str) -> IndividuationScore:
        if user_id not in self._scores:
            self._scores[user_id] = IndividuationScore(user_id=user_id)
        return self._scores[user_id]

    def update(
        self,
        user_id: str,
        shadow: Optional[float] = None,
        anima_animus: Optional[float] = None,
        self_realisation: Optional[float] = None,
        integration: Optional[float] = None,
    ) -> IndividuationScore:
        s = self.get_score(user_id)
        if shadow is not None:
            s.shadow = max(0.0, min(1.0, shadow))
        if anima_animus is not None:
            s.anima_animus = max(0.0, min(1.0, anima_animus))
        if self_realisation is not None:
            s.self_realisation = max(0.0, min(1.0, self_realisation))
        if integration is not None:
            s.integration = max(0.0, min(1.0, integration))
        s.overall = (
            s.shadow + s.anima_animus + s.self_realisation + s.integration
        ) / 4.0
        return s

    def reset(self, user_id: str) -> None:
        self._scores.pop(user_id, None)


_engine: Optional[IndividuationEngine] = None


def get_individuation_engine() -> IndividuationEngine:
    global _engine
    if _engine is None:
        _engine = IndividuationEngine()
    return _engine

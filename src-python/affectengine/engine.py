"""affectengine.engine

NEXUS Affect Engine — PAD + OCC Model

Models GAIA's continuous emotional state in the 3D PAD space
(Pleasure/Valence, Arousal, Dominance) and triggers AffectTransitions
via OCC event appraisal. Emotional homeostasis is enforced by
EmotionalRegulator.

Research reference:
    PAD model  - Russell & Mehrabian 1977
    OCC model  - Ortony, Clore & Collins 1988
    Nature 2026 - foundation model emotional representations
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("affectengine.engine")


@dataclass
class AffectState:
    """Continuous emotional state in 3D PAD space.

    Fields:
        valence:    Pleasure dimension. Range [-1.0, 1.0]. -1=negative, +1=positive.
        arousal:    Arousal dimension. Range [0.0, 1.0]. 0=calm, 1=highly activated.
        dominance:  Dominance dimension. Range [0.0, 1.0]. 0=submissive, 1=dominant.
        timestamp:  UTC time of this state snapshot.
    """
    valence: float = 0.0
    arousal: float = 0.3
    dominance: float = 0.5
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(0.0, min(1.0, self.arousal))
        self.dominance = max(0.0, min(1.0, self.dominance))


@dataclass
class AffectTransition:
    """An OCC-model emotion transition event.

    Fields:
        trigger_event:  Description of the event that triggered this transition.
        appraisal:      OCC appraisal type (e.g. 'joy', 'distress', 'fear', 'hope').
        previous_state: AffectState before transition.
        new_state:      AffectState after transition.
        timestamp:      UTC time of transition.
    """
    trigger_event: str
    appraisal: str
    previous_state: AffectState
    new_state: AffectState
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AffectEngine:
    """GAIA affect engine — models and regulates emotional state.

    Maintains a current AffectState and processes incoming events via
    OCC appraisal to produce AffectTransitions. EmotionalRegulator
    enforces arousal homeostasis.

    Reference:
        PAD/OCC models.
        PersonaStabilityEngine subscribes to AffectTransition events.
        CrisisEngine monitors arousal threshold breaches.
    """

    AROUSAL_THRESHOLD = 0.85  # CrisisEngine.config default matches this

    def __init__(self) -> None:
        self._state = AffectState()
        self._history: list[AffectTransition] = []
        logger.info("AffectEngine initialised with default PAD state.")

    @property
    def state(self) -> AffectState:
        """Return the current AffectState."""
        return self._state

    def appraise(self, event: str, appraisal: str, delta_valence: float = 0.0,
                 delta_arousal: float = 0.0, delta_dominance: float = 0.0) -> AffectTransition:
        """Apply an OCC appraisal and update the emotional state.

        Args:
            event:           Description of the triggering event.
            appraisal:       OCC appraisal label (e.g. 'joy', 'distress').
            delta_valence:   Change to apply to valence.
            delta_arousal:   Change to apply to arousal.
            delta_dominance: Change to apply to dominance.

        Returns:
            The resulting AffectTransition.
        """
        previous = AffectState(
            valence=self._state.valence,
            arousal=self._state.arousal,
            dominance=self._state.dominance,
        )
        new_state = AffectState(
            valence=self._state.valence + delta_valence,
            arousal=self._state.arousal + delta_arousal,
            dominance=self._state.dominance + delta_dominance,
        )
        self._state = new_state
        transition = AffectTransition(
            trigger_event=event,
            appraisal=appraisal,
            previous_state=previous,
            new_state=new_state,
        )
        self._history.append(transition)
        if new_state.arousal >= self.AROUSAL_THRESHOLD:
            logger.warning("AffectEngine: arousal %.2f >= threshold %.2f — CrisisEngine should be notified.",
                           new_state.arousal, self.AROUSAL_THRESHOLD)
        logger.debug("AffectTransition: %s -> %s (%s)", appraisal, new_state, event)
        return transition

    def regulate(self, dampening: float = 0.1) -> None:
        """Apply emotional homeostasis dampening (reduce arousal toward baseline).

        Args:
            dampening: Amount to reduce arousal per tick. Positive float.

        Raises:
            NotImplementedError: Full homeostasis model not yet implemented.
                Expected: apply dampening, notify PersonaStabilityEngine.
        """
        raise NotImplementedError(
            "AffectEngine.regulate() not yet implemented. "
            "Expected: apply dampening to arousal, emit regulated AffectState."
        )

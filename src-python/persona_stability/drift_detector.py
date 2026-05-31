"""
DriftDetector — cosine similarity monitor for Gaian persona stability.

Monitors cosine similarity between the most recent LLM response embedding
and the archetype's voice baseline embedding. When similarity drops below
the configured threshold, a DriftEvent is emitted and the AnchorInjector
is notified to inject on the next turn.

Design based on: Oxford / Anthropic persona stability research, Q1 2026.
Issue: #115
"""
from __future__ import annotations

import logging
import math
import time
from typing import Optional

from .types import DriftEvent

logger = logging.getLogger("gaia.persona.drift_detector")

# Default similarity threshold — responses below this trigger re-anchoring
DEFAULT_DRIFT_THRESHOLD = 0.75


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two equal-length vectors."""
    if not a or not b or len(a) != len(b):
        return 1.0  # no baseline yet — assume no drift
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 1.0
    return dot / (mag_a * mag_b)


class DriftDetector:
    """
    Monitors cosine similarity between response embeddings and the
    archetype voice baseline. Emits DriftEvents when drift is detected.

    Parameters
    ----------
    archetype_id : str
        The active Gaian archetype identifier.
    voice_baseline : list[float]
        Pre-computed embedding vector representing the archetype's voice.
        Can be set/updated at runtime via set_baseline().
    threshold : float
        Similarity score below which drift is declared (default 0.75).
    """

    def __init__(
        self,
        archetype_id: str,
        voice_baseline: Optional[list[float]] = None,
        threshold: float = DEFAULT_DRIFT_THRESHOLD,
    ) -> None:
        self.archetype_id = archetype_id
        self._baseline: list[float] = voice_baseline or []
        self.threshold = threshold
        self._drift_events: list[DriftEvent] = []
        self._similarity_history: list[float] = []

    # ── Public API ────────────────────────────────────────────────────────────

    def set_baseline(self, embedding: list[float]) -> None:
        """Update the voice baseline embedding."""
        self._baseline = embedding
        logger.debug("Voice baseline updated for archetype '%s'", self.archetype_id)

    def evaluate(
        self,
        response_embedding: list[float],
        turn_index: int,
        affect_trigger: bool = False,
    ) -> Optional[DriftEvent]:
        """
        Evaluate a response embedding against the voice baseline.

        Returns a DriftEvent if drift is detected, else None.

        Parameters
        ----------
        response_embedding : list[float]
            Embedding of the most recent LLM response.
        turn_index : int
            Current conversation turn number.
        affect_trigger : bool
            True if high-intensity affect was detected this turn (lowers threshold).
        """
        if not self._baseline:
            return None

        effective_threshold = self.threshold + 0.05 if affect_trigger else self.threshold
        similarity = _cosine_similarity(response_embedding, self._baseline)
        self._similarity_history.append(similarity)

        logger.debug(
            "Turn %d | similarity=%.4f | threshold=%.4f | archetype=%s",
            turn_index, similarity, effective_threshold, self.archetype_id,
        )

        if similarity < effective_threshold:
            trigger = "affect_intensity" if affect_trigger else "similarity_drop"
            event = DriftEvent(
                timestamp=time.time(),
                archetype_id=self.archetype_id,
                similarity_score=similarity,
                turn_index=turn_index,
                trigger=trigger,
            )
            self._drift_events.append(event)
            logger.warning(
                "Persona drift detected — archetype=%s similarity=%.4f turn=%d trigger=%s",
                self.archetype_id, similarity, turn_index, trigger,
            )
            return event

        return None

    @property
    def drift_events(self) -> list[DriftEvent]:
        """All drift events recorded in this session."""
        return list(self._drift_events)

    @property
    def average_similarity(self) -> float:
        """Mean cosine similarity across all evaluated turns."""
        if not self._similarity_history:
            return 1.0
        return sum(self._similarity_history) / len(self._similarity_history)

    def reset(self) -> None:
        """Clear drift history (call at session boundary)."""
        self._drift_events.clear()
        self._similarity_history.clear()

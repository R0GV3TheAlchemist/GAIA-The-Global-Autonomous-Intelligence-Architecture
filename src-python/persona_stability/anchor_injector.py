"""
AnchorInjector — injects persona anchor text into the LLM context window.

Scheduled injection: every N turns (default 5).
Emergency injection: whenever the DriftDetector emits a DriftEvent, OR
    when the AffectEngine reports high-intensity affect (grief / anger / fear
    with confidence >= AFFECT_INTENSITY_THRESHOLD).

Design based on: Oxford / Anthropic persona stability research, Q1 2026.
Issue: #115
"""
from __future__ import annotations

import logging
from typing import Optional

from .anchors import get_anchor
from .types import AnchorInjectionResult, DriftEvent

logger = logging.getLogger("gaia.persona.anchor_injector")

# Emotions whose high confidence triggers doubled injection frequency
HIGH_INTENSITY_EMOTIONS = {"grief", "anger", "fear", "rage", "despair"}
AFFECT_INTENSITY_THRESHOLD = 0.85  # confidence score from AffectEngine

DEFAULT_INJECTION_INTERVAL = 5    # inject every N turns under normal conditions
HIGH_INTENSITY_INTERVAL = 2       # inject every N turns under high affect


class AnchorInjector:
    """
    Decides when to inject the persona anchor into the LLM context.

    Parameters
    ----------
    archetype_id : str
        The active Gaian archetype.
    injection_interval : int
        Turns between scheduled anchor injections (default 5).
    """

    def __init__(
        self,
        archetype_id: str,
        injection_interval: int = DEFAULT_INJECTION_INTERVAL,
    ) -> None:
        self.archetype_id = archetype_id
        self._interval = injection_interval
        self._pending_emergency = False  # set by notify_drift()
        self._last_injected_turn = -1

    # ── Public API ────────────────────────────────────────────────────────────

    def notify_drift(self, event: DriftEvent) -> None:
        """Called by DriftDetector when drift is detected — flags emergency injection."""
        self._pending_emergency = True
        logger.info(
            "Emergency anchor injection queued — drift event turn=%d similarity=%.4f",
            event.turn_index, event.similarity_score,
        )

    def should_inject(
        self,
        turn_index: int,
        affect_emotion: Optional[str] = None,
        affect_confidence: float = 0.0,
    ) -> AnchorInjectionResult:
        """
        Determine whether to inject the persona anchor this turn.

        Parameters
        ----------
        turn_index : int
            Current conversation turn number.
        affect_emotion : str, optional
            Top emotion label from AffectEngine (e.g. "grief", "joy").
        affect_confidence : float
            Confidence score for the top affect emotion (0.0 – 1.0).

        Returns
        -------
        AnchorInjectionResult
            Contains should_inject flag, reason, and anchor text if injecting.
        """
        anchor = get_anchor(self.archetype_id)

        # ── Emergency: drift detected ─────────────────────────────────────────
        if self._pending_emergency:
            self._pending_emergency = False
            self._last_injected_turn = turn_index
            logger.debug("Injecting anchor — reason=drift_detected turn=%d", turn_index)
            return AnchorInjectionResult(
                should_inject=True,
                reason="drift_detected",
                anchor_text=anchor.essence,
                turn_index=turn_index,
            )

        # ── High-intensity affect: doubled frequency ──────────────────────────
        is_high_intensity = (
            affect_emotion in HIGH_INTENSITY_EMOTIONS
            and affect_confidence >= AFFECT_INTENSITY_THRESHOLD
        )
        effective_interval = HIGH_INTENSITY_INTERVAL if is_high_intensity else self._interval

        turns_since_last = turn_index - self._last_injected_turn
        if turns_since_last >= effective_interval:
            self._last_injected_turn = turn_index
            reason = "affect_intensity" if is_high_intensity else "scheduled"
            logger.debug("Injecting anchor — reason=%s turn=%d", reason, turn_index)
            return AnchorInjectionResult(
                should_inject=True,
                reason=reason,
                anchor_text=anchor.essence,
                turn_index=turn_index,
            )

        return AnchorInjectionResult(
            should_inject=False,
            reason="none",
            turn_index=turn_index,
        )

    def reset(self, turn_index: int = 0) -> None:
        """Reset injection state (call at session boundary)."""
        self._pending_emergency = False
        self._last_injected_turn = turn_index - self._interval  # allow immediate first inject

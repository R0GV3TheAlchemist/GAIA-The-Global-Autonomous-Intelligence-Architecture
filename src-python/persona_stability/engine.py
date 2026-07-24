"""
persona_stability.engine
========================
PersonaStabilityEngine — identity drift prevention for GAIA-OS.

Tracks a stability score (0.0 – 1.0) and injects anchor corrections
when the score falls below the configured floor.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 2.5
"""
from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Optional

from .anchor_injector import AnchorInjector
from .types import AnchorInjectionResult, PersonaTrace

logger = logging.getLogger("persona_stability.engine")

DEFAULT_STABILITY_FLOOR = 0.35
DEFAULT_INJECTION_INTERVAL = 5
DEFAULT_DRIFT_THRESHOLD = 0.75


class PersonaStabilityEngine:
    """
    Identity drift prevention engine for GAIA-OS.

    Monitors stability score and injects constitutional anchors
    when the score falls below DEFAULT_STABILITY_FLOOR.

    Supports full session lifecycle:
      begin_session(archetype_id) → on_turn() × N → end_session()

    Reference: NEXUS_UNIVERSAL_OS.md Domain 2.5
    """

    def __init__(
        self,
        memory: Any = None,
        floor: float = DEFAULT_STABILITY_FLOOR,
        injection_interval: int = DEFAULT_INJECTION_INTERVAL,
        drift_threshold: float = DEFAULT_DRIFT_THRESHOLD,
    ) -> None:
        self._memory = memory
        self.floor = floor
        self._injection_interval = injection_interval
        self._drift_threshold = drift_threshold

        # Session state — None means no active session
        self.archetype_id: Optional[str] = None
        self.turn_index: int = 0
        self._session_id: Optional[str] = None
        self._session_started_at: Optional[float] = None
        self._injector: Optional[AnchorInjector] = None

        logger.info(
            "PersonaStabilityEngine created (floor=%.2f interval=%d drift_thr=%.2f).",
            floor, injection_interval, drift_threshold,
        )

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def begin_session(self, archetype_id: str) -> None:
        """
        Start a new stability-monitoring session for the given archetype.

        Parameters
        ----------
        archetype_id : Gaian archetype to anchor against (e.g. "sage").
        """
        self.archetype_id = archetype_id
        self.turn_index = 0
        self._session_id = str(uuid.uuid4())
        self._session_started_at = time.time()
        self._injector = AnchorInjector(
            archetype_id=archetype_id,
            injection_interval=self._injection_interval,
        )
        logger.info(
            "PersonaStabilityEngine.begin_session archetype=%s session=%s",
            archetype_id, self._session_id,
        )

    def on_turn(
        self,
        response_embedding: Optional[list] = None,
        affect_emotion: Optional[str] = None,
        affect_confidence: float = 0.0,
    ) -> AnchorInjectionResult:
        """
        Process one conversation turn.

        If no session is active, returns a no-op AnchorInjectionResult with
        reason='session_not_started'.

        Parameters
        ----------
        response_embedding : Optional embedding vector for drift detection.
        affect_emotion     : Top emotion label from AffectEngine.
        affect_confidence  : Confidence score for the top emotion.

        Returns
        -------
        AnchorInjectionResult — injection decision for this turn.
        """
        from .types import AnchorInjectionResult

        if self._injector is None:
            # No active session
            return AnchorInjectionResult(
                should_inject=False,
                reason="session_not_started",
                anchor_text=None,
                turn_index=0,
            )

        result = self._injector.should_inject(
            turn_index=self.turn_index,
            affect_emotion=affect_emotion,
            affect_confidence=affect_confidence,
        )
        self.turn_index += 1
        return result

    def end_session(self, notes: str = "") -> Optional[PersonaTrace]:
        """
        End the current session, write a PersonaTrace to memory, and reset state.

        Parameters
        ----------
        notes : Optional free-text notes to attach to the trace.

        Returns
        -------
        PersonaTrace — the trace written to memory, or None if no session was active.
        """
        if self._session_id is None or self.archetype_id is None:
            return None

        ended_at = time.time()
        trace = PersonaTrace(
            session_id=self._session_id,
            archetype_id=self.archetype_id,
            started_at=self._session_started_at or ended_at,
            ended_at=ended_at,
            total_turns=self.turn_index,
            notes=notes,
        )

        if self._memory is not None:
            try:
                self._memory.store_episode(
                    episode_id=trace.session_id,
                    content={
                        "archetype_id":  trace.archetype_id,
                        "total_turns":   trace.total_turns,
                        "avg_similarity": trace.avg_similarity,
                        "drift_count":   trace.drift_count,
                        "notes":         trace.notes,
                    },
                    tags=["persona_stability", "session_trace"],
                )
            except Exception:
                logger.exception("PersonaStabilityEngine: failed to write trace to memory")

        logger.info(
            "PersonaStabilityEngine.end_session archetype=%s turns=%d session=%s",
            trace.archetype_id, trace.total_turns, trace.session_id,
        )

        # Reset session state
        self.archetype_id = None
        self.turn_index = 0
        self._session_id = None
        self._session_started_at = None
        self._injector = None

        return trace

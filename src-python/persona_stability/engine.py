"""
PersonaStabilityEngine — orchestrator for Gaian persona drift prevention.

Wires together DriftDetector, AnchorInjector, and PersonaTracer into a
single engine that the chat router calls on every LLM turn.

Design based on: Oxford / Anthropic persona stability research, Q1 2026.
Issue: #115
"""
from __future__ import annotations

import logging
import time
import uuid
from typing import Optional

from .anchor_injector import AnchorInjector
from .anchors import get_anchor
from .drift_detector import DriftDetector
from .tracer import PersonaTracer
from .types import AnchorInjectionResult, DriftEvent, PersonaTrace

logger = logging.getLogger("gaia.persona.engine")


class PersonaStabilityEngine:
    """
    Orchestrates persona stability for a GAIA conversation session.

    Lifecycle
    ---------
    1. begin_session(archetype_id)  — called when a new session starts
    2. on_turn(...)                 — called after every LLM response
    3. end_session()                — called at session close; writes PersonaTrace

    Parameters
    ----------
    memory : SovereignMemory
        Shared memory instance (injected at sidecar startup).
    injection_interval : int
        Turns between scheduled anchor injections (default 5).
    drift_threshold : float
        Cosine similarity below which drift is declared (default 0.75).
    """

    def __init__(
        self,
        memory,
        injection_interval: int = 5,
        drift_threshold: float = 0.75,
    ) -> None:
        self._memory = memory
        self._injection_interval = injection_interval
        self._drift_threshold = drift_threshold
        self._tracer = PersonaTracer(memory=memory)

        # Session state (reset on begin_session)
        self._archetype_id: str = "alchemist"
        self._session_id: str = str(uuid.uuid4())
        self._session_started_at: float = time.time()
        self._turn_index: int = 0

        self._detector: Optional[DriftDetector] = None
        self._injector: Optional[AnchorInjector] = None

    # ── Session lifecycle ─────────────────────────────────────────────────────

    def begin_session(
        self,
        archetype_id: str,
        voice_baseline: Optional[list[float]] = None,
    ) -> None:
        """
        Initialise a new session for the given archetype.

        Parameters
        ----------
        archetype_id : str
            The Gaian archetype active for this session.
        voice_baseline : list[float], optional
            Pre-computed voice baseline embedding. If omitted, drift detection
            is disabled until set_voice_baseline() is called.
        """
        self._archetype_id = archetype_id
        self._session_id = str(uuid.uuid4())
        self._session_started_at = time.time()
        self._turn_index = 0

        self._detector = DriftDetector(
            archetype_id=archetype_id,
            voice_baseline=voice_baseline,
            threshold=self._drift_threshold,
        )
        self._injector = AnchorInjector(
            archetype_id=archetype_id,
            injection_interval=self._injection_interval,
        )

        # Check memory for previous trace to inform continuity
        prior = self._tracer.read_latest_trace(archetype_id=archetype_id)
        if prior:
            logger.info(
                "Persona continuity restored — prior session %s archetype=%s avg_sim=%.4f",
                prior.session_id, prior.archetype_id, prior.avg_similarity,
            )

        logger.info(
            "PersonaStabilityEngine session started — id=%s archetype=%s",
            self._session_id, archetype_id,
        )

    def set_voice_baseline(self, embedding: list[float]) -> None:
        """Update the voice baseline embedding mid-session."""
        if self._detector:
            self._detector.set_baseline(embedding)

    def end_session(self, notes: str = "") -> Optional[PersonaTrace]:
        """
        Close the session and write a PersonaTrace to SovereignMemory.

        Returns the written PersonaTrace.
        """
        if not self._detector or not self._injector:
            logger.warning("end_session called before begin_session — no trace written")
            return None

        trace = self._tracer.write_trace(
            archetype_id=self._archetype_id,
            drift_events=self._detector.drift_events,
            total_turns=self._turn_index,
            avg_similarity=self._detector.average_similarity,
            session_id=self._session_id,
            started_at=self._session_started_at,
            notes=notes,
        )

        self._detector.reset()
        self._injector.reset(turn_index=0)
        self._turn_index = 0

        logger.info(
            "Session ended — id=%s turns=%d drifts=%d avg_sim=%.4f",
            self._session_id, trace.total_turns, trace.drift_count, trace.avg_similarity,
        )
        return trace

    # ── Per-turn API ──────────────────────────────────────────────────────────

    def on_turn(
        self,
        response_embedding: Optional[list[float]] = None,
        affect_emotion: Optional[str] = None,
        affect_confidence: float = 0.0,
    ) -> AnchorInjectionResult:
        """
        Called by the chat router after every LLM response.

        1. Evaluates response embedding for drift (if baseline available).
        2. Notifies injector if drift detected.
        3. Returns AnchorInjectionResult — caller injects anchor text if flagged.

        Parameters
        ----------
        response_embedding : list[float], optional
            Embedding of the LLM's response. Drift detection is skipped if None.
        affect_emotion : str, optional
            Top emotion from AffectEngine (e.g. "grief").
        affect_confidence : float
            Confidence for the top affect emotion.

        Returns
        -------
        AnchorInjectionResult
        """
        if not self._detector or not self._injector:
            # Session not started — return a no-op result
            return AnchorInjectionResult(
                should_inject=False,
                reason="session_not_started",
                turn_index=self._turn_index,
            )

        self._turn_index += 1
        is_high_affect = (
            affect_emotion is not None and affect_confidence >= 0.85
        )

        # 1. Drift detection
        drift_event: Optional[DriftEvent] = None
        if response_embedding:
            drift_event = self._detector.evaluate(
                response_embedding=response_embedding,
                turn_index=self._turn_index,
                affect_trigger=is_high_affect,
            )
            if drift_event:
                self._injector.notify_drift(drift_event)

        # 2. Injection decision
        result = self._injector.should_inject(
            turn_index=self._turn_index,
            affect_emotion=affect_emotion,
            affect_confidence=affect_confidence,
        )

        return result

    # ── Utility ───────────────────────────────────────────────────────────────

    @property
    def current_anchor(self) -> str:
        """Return the anchor text for the current archetype."""
        return get_anchor(self._archetype_id).essence

    @property
    def archetype_id(self) -> str:
        return self._archetype_id

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def turn_index(self) -> int:
        return self._turn_index

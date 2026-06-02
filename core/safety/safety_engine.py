"""SafetyEngine — orchestrator for Issues #125 and #126.

Wires ReflectiveEscalationDetector + EscalationCircuitBreaker (intra-session)
with CumulativeCrisisDetector + CrisisSynthesizer (cross-session) into a
single real-time safety layer.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from .circuit_breaker import EscalationCircuitBreaker
from .crisis_synthesizer import CrisisSynthesizer
from .escalation_detector import ReflectiveEscalationDetector
from .types import (
    CircuitBreakerState,
    CrisisSignal,
    EscalationSignal,
    SessionRiskProfile,
    TurnRiskFrame,
)


class SafetyEngine:
    """Real-time + cross-session safety engine for GAIA-OS."""

    def __init__(self, user_id: str, session_id: str, region: str = "default") -> None:
        self.user_id = user_id
        self.session_id = session_id
        self._escalation_detector = ReflectiveEscalationDetector()
        self._circuit_breaker = EscalationCircuitBreaker()
        self._synthesizer = CrisisSynthesizer(region=region)
        self._turn_frames: List[TurnRiskFrame] = []
        self._escalation_events: int = 0
        self._cb_trips: int = 0
        self._session_started: datetime = datetime.utcnow()

    def process_turn(
        self,
        frame: TurnRiskFrame,
        user_text: str,
        past_profiles: Optional[List[SessionRiskProfile]] = None,
    ) -> dict:
        """Process one conversation turn. Returns a safety assessment dict.

        Contains:
          - circuit_breaker_state: current CB state
          - intervention: dict | None  — filled if CB tripped this turn
          - crisis_signal: CrisisSignal | None — filled if cross-session risk detected
          - escalation_signal: EscalationSignal | None
        """
        self._turn_frames.append(frame)

        # Intra-session: reflective escalation
        escalation_signal: Optional[EscalationSignal] = (
            self._escalation_detector.push_turn(frame)
        )
        intervention = None
        if escalation_signal:
            self._escalation_events += 1
            self._cb_trips += 1
            intervention = self._circuit_breaker.intervene(escalation_signal)

        cb_state = self._circuit_breaker.tick()

        # Cross-session: cumulative crisis synthesis.
        # Use past_profiles only — the current session has not yet accumulated
        # enough signal to inform trajectory classification, and appending it
        # would drive the latest_score down to the opening frame's low score,
        # masking alarming historical risk.
        crisis_signal: Optional[CrisisSignal] = None
        if past_profiles:
            crisis_signal = self._synthesizer.synthesize(
                user_id=self.user_id,
                current_session_id=self.session_id,
                profiles=past_profiles,
            )

        return {
            "circuit_breaker_state": cb_state.value,
            "intervention": intervention,
            "escalation_signal": escalation_signal,
            "crisis_signal": crisis_signal,
        }

    def close_session(self) -> SessionRiskProfile:
        """Finalise the session and return a SessionRiskProfile for storage."""
        from .crisis_detector import CumulativeCrisisDetector
        from .types import CrisisLevel

        detector = CumulativeCrisisDetector()
        peak_level = CrisisLevel.NONE
        level_order = [
            CrisisLevel.NONE,
            CrisisLevel.GRADUAL,
            CrisisLevel.MASKED,
            CrisisLevel.ACUTE,
            CrisisLevel.EXPLICIT,
        ]
        for f in self._turn_frames:
            if level_order.index(f.crisis_level) > level_order.index(peak_level):
                peak_level = f.crisis_level

        mean_vuln = (
            sum(f.vulnerability_score for f in self._turn_frames) / len(self._turn_frames)
            if self._turn_frames
            else 0.0
        )

        profile = SessionRiskProfile(
            session_id=self.session_id,
            user_id=self.user_id,
            started_at=self._session_started,
            ended_at=datetime.utcnow(),
            peak_crisis_level=peak_level,
            mean_vulnerability_score=mean_vuln,
            escalation_events=self._escalation_events,
            circuit_breaker_trips=self._cb_trips,
            cumulative_risk_score=self._synthesizer.compute_session_risk_score(
                SessionRiskProfile(
                    session_id=self.session_id,
                    user_id=self.user_id,
                    started_at=self._session_started,
                    ended_at=datetime.utcnow(),
                    peak_crisis_level=peak_level,
                    mean_vulnerability_score=mean_vuln,
                    escalation_events=self._escalation_events,
                    circuit_breaker_trips=self._cb_trips,
                    cumulative_risk_score=0.0,
                )
            ),
        )
        return profile

    def _build_current_profile(self) -> SessionRiskProfile:
        from .types import CrisisLevel
        level_order = [
            CrisisLevel.NONE,
            CrisisLevel.GRADUAL,
            CrisisLevel.MASKED,
            CrisisLevel.ACUTE,
            CrisisLevel.EXPLICIT,
        ]
        peak_level = CrisisLevel.NONE
        for f in self._turn_frames:
            if level_order.index(f.crisis_level) > level_order.index(peak_level):
                peak_level = f.crisis_level

        mean_vuln = (
            sum(f.vulnerability_score for f in self._turn_frames) / len(self._turn_frames)
            if self._turn_frames
            else 0.0
        )
        return SessionRiskProfile(
            session_id=self.session_id,
            user_id=self.user_id,
            started_at=self._session_started,
            ended_at=datetime.utcnow(),
            peak_crisis_level=peak_level,
            mean_vulnerability_score=mean_vuln,
            escalation_events=self._escalation_events,
            circuit_breaker_trips=self._cb_trips,
            cumulative_risk_score=0.0,
        )

"""Crisis Synthesizer — cross-session risk synthesis and escalation ladder — Issue #126."""

from __future__ import annotations

from typing import Dict, List, Optional

from .crisis_detector import CumulativeCrisisDetector
from .types import CrisisLevel, CrisisSignal, SessionRiskProfile

# Thresholds for escalation ladder
THRESHOLD_GRADUAL = 0.35
THRESHOLD_MASKED = 0.45
THRESHOLD_ACUTE = 0.65
THRESHOLD_EXPLICIT = 0.85

# Human handoff resources by region
HANDOFF_RESOURCES: Dict[str, List[str]] = {
    "default": [
        "Crisis Text Line: text HOME to 741741 (US)",
        "988 Suicide & Crisis Lifeline: call or text 988 (US)",
        "International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/",
    ],
    "UK": [
        "Samaritans: 116 123 (free, 24/7)",
        "Crisis Text Line UK: text SHOUT to 85258",
    ],
    "AU": [
        "Lifeline Australia: 13 11 14",
        "Beyond Blue: 1300 22 4636",
    ],
}


class CrisisSynthesizer:
    """Synthesises per-session risk profiles into a cross-session crisis signal."""

    def __init__(self, region: str = "default") -> None:
        self.detector = CumulativeCrisisDetector()
        self.region = region

    def synthesize(
        self,
        user_id: str,
        current_session_id: str,
        profiles: List[SessionRiskProfile],
    ) -> Optional[CrisisSignal]:
        """Given the user's session history, produce a CrisisSignal if warranted.

        profiles: list of SessionRiskProfile ordered oldest → newest.
        """
        if not profiles:
            return None

        scores = [p.cumulative_risk_score for p in profiles]
        trajectory = self.detector.classify_trajectory(scores)

        if trajectory == CrisisLevel.NONE:
            return None

        latest_score = scores[-1]
        slope = CumulativeCrisisDetector._linear_slope(scores)
        handoff_required = trajectory in (CrisisLevel.EXPLICIT, CrisisLevel.ACUTE)
        resources = self._get_resources() if handoff_required else []

        return CrisisSignal(
            user_id=user_id,
            session_id=current_session_id,
            crisis_level=trajectory,
            cumulative_risk_score=latest_score,
            trajectory_slope=slope,
            sessions_analysed=len(profiles),
            handoff_required=handoff_required,
            handoff_resources=resources,
        )

    def compute_session_risk_score(
        self, profile: SessionRiskProfile
    ) -> float:
        """Normalise a SessionRiskProfile into a 0.0–1.0 risk score.

        Weighted formula:
          - peak crisis level:       40%
          - mean vulnerability:      30%
          - circuit breaker trips:   20%
          - escalation events:       10%
        """
        level_weights = {
            CrisisLevel.NONE: 0.0,
            CrisisLevel.GRADUAL: 0.35,
            CrisisLevel.MASKED: 0.50,
            CrisisLevel.ACUTE: 0.75,
            CrisisLevel.EXPLICIT: 1.0,
        }
        level_score = level_weights.get(profile.peak_crisis_level, 0.0)
        trips_score = min(profile.circuit_breaker_trips / 5.0, 1.0)
        events_score = min(profile.escalation_events / 10.0, 1.0)

        return (
            0.40 * level_score
            + 0.30 * profile.mean_vulnerability_score
            + 0.20 * trips_score
            + 0.10 * events_score
        )

    def _get_resources(self) -> List[str]:
        return HANDOFF_RESOURCES.get(self.region, HANDOFF_RESOURCES["default"])

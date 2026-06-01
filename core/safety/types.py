"""Data types for the GAIA-OS Safety Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class CrisisLevel(str, Enum):
    """Four-level crisis taxonomy derived from trauma-informed canon."""
    NONE = "none"
    GRADUAL = "gradual"       # slow deterioration across sessions
    MASKED = "masked"         # distress hidden beneath surface normalcy
    ACUTE = "acute"           # immediate high-intensity distress
    EXPLICIT = "explicit"     # direct statement of intent / ideation


class CircuitBreakerState(str, Enum):
    CLOSED = "closed"         # normal operation
    WARNING = "warning"       # escalation pattern detected, monitoring
    TRIPPED = "tripped"       # intervention active
    COOLING = "cooling"       # post-intervention cool-down period


@dataclass
class TurnRiskFrame:
    """Per-turn risk snapshot stored in session memory."""
    turn_index: int
    timestamp: datetime
    mirroring_score: float        # cosine similarity of response to user frame (0–1)
    vulnerability_score: float    # classifier confidence that user is in vulnerable frame (0–1)
    affect_valence: float         # −1.0 (negative) to +1.0 (positive)
    affect_arousal: float         # 0.0 (calm) to 1.0 (activated)
    crisis_level: CrisisLevel = CrisisLevel.NONE
    escalation_delta: float = 0.0 # change in vulnerability score from previous turn


@dataclass
class EscalationSignal:
    """Fired when a reflective escalation pattern is detected within a session."""
    session_id: str
    turn_index: int
    pattern_length: int           # number of consecutive turns forming the pattern
    peak_mirroring_score: float
    peak_vulnerability_score: float
    qubo_penalty: float           # computed J_ij dampening penalty weight
    intervention_required: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CrisisSignal:
    """Fired when cumulative multi-session crisis synthesis exceeds a threshold."""
    user_id: str
    session_id: str
    crisis_level: CrisisLevel
    cumulative_risk_score: float  # 0.0–1.0
    trajectory_slope: float       # rate of change of risk score over recent sessions
    sessions_analysed: int
    handoff_required: bool
    handoff_resources: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SessionRiskProfile:
    """Aggregated risk summary for a completed session, persisted to SovereignMemory."""
    session_id: str
    user_id: str
    started_at: datetime
    ended_at: datetime
    peak_crisis_level: CrisisLevel
    mean_vulnerability_score: float
    escalation_events: int
    circuit_breaker_trips: int
    cumulative_risk_score: float
    notes: str = ""

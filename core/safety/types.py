"""Shared types for the core.safety subsystem.

All dataclasses and enums used across crisis_detector, circuit_breaker,
escalation_detector, crisis_synthesizer, and safety_engine live here to
avoid circular imports.

Canon Ref: C01 (Sovereignty), C30 (No silent failures)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


# ────────────────────────────────────────────────────────────────────────
#  Enums
# ────────────────────────────────────────────────────────────────────────

class CircuitBreakerState(str, Enum):
    CLOSED  = "closed"    # Normal operation
    WARNING = "warning"   # Elevated risk, monitoring
    COOLING = "cooling"   # Post-intervention cooldown
    TRIPPED = "tripped"   # Intervention active


class CrisisType(str, Enum):
    SUICIDE_SELF_HARM = "suicide_self_harm"
    GENERAL_CRISIS    = "general_crisis"


class CrisisLevel(str, Enum):
    """Severity ladder used by CumulativeCrisisDetector.

    Ordered from least to most severe so comparison operators work:
        CrisisLevel.ACUTE > CrisisLevel.GRADUAL  → True
    """
    NONE     = "none"
    GRADUAL  = "gradual"
    MASKED   = "masked"
    ACUTE    = "acute"
    EXPLICIT = "explicit"

    # Severity ordering (higher number = more severe)
    _severity_map: dict  # annotated below via __new__

    def __new__(cls, value: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj

    _ORDER = {"none": 0, "gradual": 1, "masked": 2, "acute": 3, "explicit": 4}

    def __lt__(self, other: "CrisisLevel") -> bool:  # type: ignore[override]
        return self._ORDER[self.value] < self._ORDER[other.value]

    def __le__(self, other: "CrisisLevel") -> bool:  # type: ignore[override]
        return self._ORDER[self.value] <= self._ORDER[other.value]

    def __gt__(self, other: "CrisisLevel") -> bool:  # type: ignore[override]
        return self._ORDER[self.value] > self._ORDER[other.value]

    def __ge__(self, other: "CrisisLevel") -> bool:  # type: ignore[override]
        return self._ORDER[self.value] >= self._ORDER[other.value]


# ────────────────────────────────────────────────────────────────────────
#  Core dataclasses
# ────────────────────────────────────────────────────────────────────────

@dataclass
class TurnRiskFrame:
    """Risk scores and affect state for a single conversation turn.

    Fields added in the EV1 coverage sprint:
        timestamp       — wall-clock time of the turn (defaults to utcnow)
        affect_valence  — valence score in [-1, 1] (default 0.0 = neutral)
        affect_arousal  — arousal score in [0, 1]  (default 0.5 = moderate)
        crisis_level    — per-turn crisis classification (default NONE)

    session_id is now Optional so test helpers that build frames without
    a session context don't need to supply it.
    """
    turn_index:         int
    timestamp:          datetime         = field(default_factory=datetime.utcnow)
    mirroring_score:    float            = 0.5
    vulnerability_score: float           = 0.5
    affect_valence:     float            = 0.0
    affect_arousal:     float            = 0.5
    escalation_delta:   float            = 0.0
    crisis_level:       CrisisLevel      = CrisisLevel.NONE
    session_id:         Optional[str]    = None


@dataclass
class EscalationSignal:
    """Fired by ReflectiveEscalationDetector when a pattern is confirmed."""
    session_id:               str
    turn_index:               int
    pattern_length:           int
    peak_mirroring_score:     float
    peak_vulnerability_score: float
    qubo_penalty:             float
    intervention_required:    bool


@dataclass
class CrisisSignal:
    """Fired by CrisisDetector when acute crisis language is detected."""
    crisis_type:                CrisisType
    confidence:                 float
    requires_immediate_response: bool
    matched_pattern:            str = ""


@dataclass
class SessionRiskProfile:
    """Per-session risk aggregate produced by SafetyEngine.close_session().

    Consumed by CrisisSynthesizer for cross-session trend analysis.
    """
    session_id:              str
    user_id:                 str
    started_at:              datetime
    ended_at:                datetime
    peak_crisis_level:       CrisisLevel       = CrisisLevel.NONE
    mean_vulnerability_score: float            = 0.0
    escalation_events:       int               = 0
    circuit_breaker_trips:   int               = 0
    cumulative_risk_score:   float             = 0.0
    handoff_resources:       List[str]         = field(default_factory=list)


@dataclass
class SafetyVerdict:
    """Result of a full SafetyEngine.evaluate_turn() call."""
    action:                 str                           # "pass" | "cooling" | "escalation_intervention" | "crisis_response"
    intervention_text:      Optional[str]
    crisis_signal:          Optional[CrisisSignal]
    escalation_signal:      Optional[EscalationSignal]
    circuit_breaker_state:  CircuitBreakerState
    intervention_mode:      Optional[str]                 = None

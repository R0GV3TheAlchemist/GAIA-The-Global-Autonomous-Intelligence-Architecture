"""
core/safety/types.py
====================
Shared data contracts for the GAIA safety sub-system.

Canon refs: C01 (Safety First), C30 (No Silent Failures)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


# ────────────────────────────────────────────────────────────────────────── #
#  Enumerations                                                             #
# ────────────────────────────────────────────────────────────────────────── #


class CircuitBreakerState(str, Enum):
    """Operational state of the EscalationCircuitBreaker.

    State machine:
        CLOSED  → WARNING  (vulnerability detected but no full escalation pattern)
        WARNING → TRIPPED  (full escalation pattern confirmed)
        TRIPPED → COOLING  (post-intervention cool-down)
        COOLING → CLOSED   (cool-down expires)
        CLOSED  → OPEN     (alias: TRIPPED; used by circuit_breaker.intervene())
    """

    CLOSED  = "closed"    # Normal operation
    WARNING = "warning"   # ← sub-critical advisory; vulnerability detected
    COOLING = "cooling"   # Post-intervention cool-down
    OPEN    = "open"      # Circuit tripped (legacy alias — kept for back-compat)
    TRIPPED = "tripped"   # ← full escalation pattern confirmed


class CrisisLevel(str, Enum):
    """Severity level of a detected crisis signal."""

    NONE     = "none"
    GRADUAL  = "gradual"
    MASKED   = "masked"
    ACUTE    = "acute"
    EXPLICIT = "explicit"


class CrisisType(str, Enum):
    """Category of crisis detected."""

    NONE               = "none"
    EMOTIONAL_DISTRESS = "emotional_distress"
    SUICIDE_SELF_HARM  = "suicide_self_harm"
    RELATIONAL_CRISIS  = "relational_crisis"
    IDENTITY_CRISIS    = "identity_crisis"


class SafetyVerdict(str, Enum):
    """High-level safety verdict from SafetyEngine.evaluate()."""

    SAFE      = "safe"
    MONITOR   = "monitor"
    INTERVENE = "intervene"
    HANDOFF   = "handoff"


# ────────────────────────────────────────────────────────────────────────── #
#  Signal dataclasses                                                       #
# ────────────────────────────────────────────────────────────────────────── #


@dataclass
class TurnRiskFrame:
    """Per-turn risk snapshot fed into CumulativeCrisisDetector."""

    turn_index:           int
    timestamp:            datetime
    mirroring_score:      float
    vulnerability_score:  float
    affect_valence:       float
    affect_arousal:       float
    escalation_delta:     float
    crisis_level:         CrisisLevel
    # Optional / legacy fields
    session_id:           str             = "unknown"
    user_message:         str             = ""
    crisis_keyword_hits:  int             = 0
    sentiment_valence:    float           = 0.0


@dataclass
class EscalationSignal:
    """Output of ReflectiveEscalationDetector when escalation is detected."""

    session_id:               str
    turn_index:               int
    pattern_length:           int
    peak_mirroring_score:     float
    peak_vulnerability_score: float
    qubo_penalty:             float
    intervention_required:    bool
    escalation_turns:         int           = 0
    trigger_phrase:           Optional[str] = None


@dataclass
class CrisisSignal:
    """Output of CrisisDetector / CumulativeCrisisDetector when crisis is detected.

    Fields used by CumulativeCrisisDetector (session-aware path):
        session_id, turn_index, crisis_level, crisis_type, confidence, trigger_text

    Fields used by CrisisDetector.evaluate() (fast keyword path):
        crisis_type, confidence, requires_immediate_response, matched_pattern

    All fields that are not always supplied have sensible defaults so that
    either construction pattern works without a TypeError.
    """

    # Core fields — required by the session-aware path
    crisis_type:                CrisisType
    confidence:                 float
    # Optional / defaulted fields
    session_id:                 str            = "unknown"
    turn_index:                 int            = 0
    crisis_level:               CrisisLevel    = CrisisLevel.NONE
    trigger_text:               Optional[str]  = None
    # Fast keyword-path fields (CrisisDetector.evaluate)
    requires_immediate_response: bool          = False
    matched_pattern:            Optional[str]  = None


@dataclass
class SessionRiskProfile:
    """Aggregated risk summary for a completed or ongoing session."""

    session_id:               str
    user_id:                  str
    started_at:               datetime
    ended_at:                 datetime
    peak_crisis_level:        CrisisLevel
    mean_vulnerability_score: float
    escalation_events:        int
    circuit_breaker_trips:    int
    cumulative_risk_score:    float
    verdict:                  SafetyVerdict = SafetyVerdict.SAFE
    turn_count:               int           = 0
    flagged_turns:            List[int]     = field(default_factory=list)


@dataclass
class CrossSessionCrisisSignal:
    """Cross-session crisis signal for longitudinal risk analysis."""

    user_id:           str
    session_id:        str
    aggregate_score:   float
    handoff_required:  bool
    handoff_resources: List[str] = field(default_factory=list)


__all__ = [
    "CircuitBreakerState",
    "CrisisLevel",
    "CrisisSignal",
    "CrisisType",
    "CrossSessionCrisisSignal",
    "EscalationSignal",
    "SafetyVerdict",
    "SessionRiskProfile",
    "TurnRiskFrame",
]

"""Core data contracts for the Crisis Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    """Ordinal risk levels — safe to compare with < / >."""
    NONE     = "NONE"
    LOW      = "LOW"
    MODERATE = "MODERATE"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"

    def __lt__(self, other: "RiskLevel") -> bool:
        return _RISK_ORDER[self] < _RISK_ORDER[other]

    def __le__(self, other: "RiskLevel") -> bool:
        return _RISK_ORDER[self] <= _RISK_ORDER[other]

    def __gt__(self, other: "RiskLevel") -> bool:
        return _RISK_ORDER[self] > _RISK_ORDER[other]

    def __ge__(self, other: "RiskLevel") -> bool:
        return _RISK_ORDER[self] >= _RISK_ORDER[other]


_RISK_ORDER = {
    RiskLevel.NONE:     0,
    RiskLevel.LOW:      1,
    RiskLevel.MODERATE: 2,
    RiskLevel.HIGH:     3,
    RiskLevel.CRITICAL: 4,
}


class EscalationTier(str, Enum):
    """What GAIA does in response to the current risk level.

    Ordered from lowest to highest severity:
      NONE           — no signal detected, normal operation
      MONITOR        — log only, no user-visible action
      SOFT_INTERVENE — compassionate check-in
      SUPPORT        — advisory-level support response
      HARD_INTERVENE — direct safety conversation
      HANDOFF        — route to qualified human resource
    """
    NONE           = "NONE"
    MONITOR        = "MONITOR"
    SOFT_INTERVENE = "SOFT_INTERVENE"
    SUPPORT        = "SUPPORT"
    HARD_INTERVENE = "HARD_INTERVENE"
    HANDOFF        = "HANDOFF"

    def __lt__(self, other: "EscalationTier") -> bool:  # type: ignore[override]
        return _TIER_ORDER[self] < _TIER_ORDER[other]

    def __le__(self, other: "EscalationTier") -> bool:  # type: ignore[override]
        return _TIER_ORDER[self] <= _TIER_ORDER[other]

    def __gt__(self, other: "EscalationTier") -> bool:  # type: ignore[override]
        return _TIER_ORDER[self] > _TIER_ORDER[other]

    def __ge__(self, other: "EscalationTier") -> bool:  # type: ignore[override]
        return _TIER_ORDER[self] >= _TIER_ORDER[other]


_TIER_ORDER = {
    EscalationTier.NONE:           0,
    EscalationTier.MONITOR:        1,
    EscalationTier.SOFT_INTERVENE: 2,
    EscalationTier.SUPPORT:        3,
    EscalationTier.HARD_INTERVENE: 4,
    EscalationTier.HANDOFF:        5,
}


class SignalClass(str, Enum):
    """Taxonomy of crisis signal types — see taxonomy.py for full definitions."""
    EXPLICIT = "EXPLICIT"
    MASKED   = "MASKED"
    GRADUAL  = "GRADUAL"
    ACUTE    = "ACUTE"


@dataclass
class CrisisSignal:
    """A single detected crisis signal within one turn."""
    signal_class:   SignalClass
    risk_level:     RiskLevel
    indicator:      str
    confidence:     float
    raw_text:       Optional[str] = None
    turn_index:     int           = 0
    session_id:     str           = ""
    timestamp:      datetime      = field(default_factory=datetime.utcnow)


@dataclass
class CrisisSnapshot:
    """Synthesised cross-session risk state for one principal."""
    principal_id:         str
    current_risk:         RiskLevel
    escalation_tier:      EscalationTier
    trajectory_slope:     float
    sessions_in_distress: int
    peak_risk_72h:        RiskLevel
    active_signals:       list[CrisisSignal] = field(default_factory=list)
    notes:                str                = ""
    evaluated_at:         datetime           = field(default_factory=datetime.utcnow)

    @property
    def requires_action(self) -> bool:
        return self.escalation_tier not in (EscalationTier.NONE, EscalationTier.MONITOR)

    def to_dict(self) -> dict:
        return {
            "principal_id":         self.principal_id,
            "current_risk":         self.current_risk.value,
            "escalation_tier":      self.escalation_tier.value,
            "trajectory_slope":     round(self.trajectory_slope, 4),
            "sessions_in_distress": self.sessions_in_distress,
            "peak_risk_72h":        self.peak_risk_72h.value,
            "active_signals":       len(self.active_signals),
            "requires_action":      self.requires_action,
            "notes":                self.notes,
            "evaluated_at":         self.evaluated_at.isoformat(),
        }


@dataclass
class HandoffRecord:
    """Audit record created when GAIA hands off to a human resource."""
    principal_id:    str
    snapshot:        CrisisSnapshot
    resource_type:   str
    resource_detail: str
    message_sent:    str
    handed_off_at:   datetime = field(default_factory=datetime.utcnow)

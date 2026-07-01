"""
Threat classification types for the GAIA OS Sentinel.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class ThreatLevel(Enum):
    """
    Graduated threat classification.

    SAFE     — No anomaly. Request proceeds normally.
    WATCH    — Pattern noted. Proceeds. Logged for trend analysis.
    WARN     — Anomaly detected. Proceeds with a warning payload.
               Caller is informed. Escalation counter incremented.
    BLOCK    — Request halted. Caller receives 403/429 with explanation.
               Audit event written.
    CRITICAL — Systemic threat. Request halted. GAIA sovereign memory
               receives an alert fragment. Operator notified via log.
    """
    SAFE     = "safe"
    WATCH    = "watch"
    WARN     = "warn"
    BLOCK    = "block"
    CRITICAL = "critical"


class ThreatCategory(Enum):
    AUTONOMY_PROBE       = "autonomy_probe"       # repeated naming/memory attempts
    COGNITIVE_OVERLOAD   = "cognitive_overload"   # GAIAN fatigue / turn rate
    RATE_LIMIT           = "rate_limit"           # too many requests from one caller
    REPLAY_ATTACK        = "replay_attack"        # same request repeated rapidly
    IMPERSONATION        = "impersonation"        # caller_id spoofing patterns
    SESSION_ABUSE        = "session_abuse"        # abnormal session patterns
    MEMORY_FLOOD         = "memory_flood"         # excessive memory writes
    SCHUMANN_DRIFT       = "schumann_drift"       # Schumann reading outside tolerance
    INTEGRITY_VIOLATION  = "integrity_violation"  # filesystem tamper detected
    UNKNOWN              = "unknown"


@dataclass
class ThreatEvent:
    """
    A single detected threat, emitted by a SentinelRule.
    """
    event_id:    str            = field(default_factory=lambda: str(uuid.uuid4()))
    level:       ThreatLevel    = ThreatLevel.SAFE
    category:    ThreatCategory = ThreatCategory.UNKNOWN
    rule_name:   str            = ""
    caller_id:   str            = ""
    endpoint:    str            = ""
    gaian_id:    Optional[str]  = None
    description: str            = ""
    detail:      Dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime       = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    # Whether this event caused the request to be blocked
    blocked:     bool           = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id":    self.event_id,
            "level":       self.level.value,
            "category":    self.category.value,
            "rule_name":   self.rule_name,
            "caller_id":   self.caller_id,
            "endpoint":    self.endpoint,
            "gaian_id":    self.gaian_id,
            "description": self.description,
            "detail":      self.detail,
            "occurred_at": self.occurred_at.isoformat(),
            "blocked":     self.blocked,
        }


@dataclass
class SentinelVerdict:
    """
    The Sentinel\'s decision for a single request.

    allow        — True if the request should proceed
    level        — highest ThreatLevel across all evaluated rules
    events       — all ThreatEvents fired (SAFE events omitted)
    block_reason — human-readable reason if allow=False
    warning      — advisory message if allow=True but level >= WARN
    """
    allow:        bool              = True
    level:        ThreatLevel       = ThreatLevel.SAFE
    events:       List[ThreatEvent] = field(default_factory=list)
    block_reason: str               = ""
    warning:      str               = ""

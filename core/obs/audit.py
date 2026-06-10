"""
core.obs.audit
==============
Audit logging primitives for GAIA-OS observability layer.

Provides:
  AuditEventType  — enum of event categories
  AuditEvent      — single immutable audit record
  AuditLog        — in-memory append-only audit log with query helpers
  get_audit()     — module-level singleton accessor
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional


class AuditEventType(str, Enum):
    ACTION_REQUESTED  = "action_requested"
    ACTION_APPROVED   = "action_approved"
    ACTION_BLOCKED    = "action_blocked"
    CONSENT_GRANTED   = "consent_granted"
    CONSENT_REVOKED   = "consent_revoked"
    HALT_TRIGGERED    = "halt_triggered"
    HALT_CLEARED      = "halt_cleared"
    SESSION_START     = "session_start"
    SESSION_END       = "session_end"
    IDENTITY_VERIFIED = "identity_verified"
    POLICY_EVALUATED  = "policy_evaluated"
    ANOMALY_DETECTED  = "anomaly_detected"
    GENERIC           = "generic"


@dataclass(frozen=True)
class AuditEvent:
    """A single immutable audit record."""
    event_type: AuditEventType
    message: str
    actor: str = "system"
    target: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "message": self.message,
            "actor": self.actor,
            "target": self.target,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class AuditLog:
    """
    Thread-safe in-memory append-only audit log.

    Usage:
        log = AuditLog()
        log.record(AuditEvent(AuditEventType.ACTION_APPROVED, "Tool executed", actor="agent"))
        recent = log.tail(10)
    """

    def __init__(self, max_size: int = 10_000) -> None:
        self._events: List[AuditEvent] = []
        self._max_size = max_size
        self._listeners: List[Callable[[AuditEvent], None]] = []

    def record(self, event: AuditEvent) -> None:
        """Append an event; trims to max_size if needed."""
        self._events.append(event)
        if len(self._events) > self._max_size:
            self._events = self._events[-self._max_size:]
        for cb in self._listeners:
            try:
                cb(event)
            except Exception:
                pass

    def emit(
        self,
        event_type: AuditEventType,
        message: str,
        actor: str = "system",
        target: Optional[str] = None,
        **metadata,
    ) -> AuditEvent:
        """Convenience: build and record an event in one call."""
        event = AuditEvent(
            event_type=event_type,
            message=message,
            actor=actor,
            target=target,
            metadata=metadata,
        )
        self.record(event)
        return event

    def tail(self, n: int = 50) -> List[AuditEvent]:
        """Return the n most recent events."""
        return self._events[-n:]

    def filter_by_type(self, event_type: AuditEventType) -> List[AuditEvent]:
        return [e for e in self._events if e.event_type == event_type]

    def filter_by_actor(self, actor: str) -> List[AuditEvent]:
        return [e for e in self._events if e.actor == actor]

    def clear(self) -> None:
        self._events.clear()

    def add_listener(self, callback: Callable[[AuditEvent], None]) -> None:
        """Register a callback fired on every new event."""
        self._listeners.append(callback)

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self):
        return iter(self._events)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_audit_log: Optional[AuditLog] = None


def get_audit() -> AuditLog:
    """Return the process-wide AuditLog singleton."""
    global _audit_log
    if _audit_log is None:
        _audit_log = AuditLog()
    return _audit_log

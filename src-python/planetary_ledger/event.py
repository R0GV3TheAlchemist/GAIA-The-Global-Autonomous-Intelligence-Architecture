# Copyright (c) 2026 Kyle Alexander Steen (R0GV3 The Alchemist). All Rights Reserved.
# NEXUS Planetary Ledger — LedgerEvent dataclass
# Schema-faithful to specs/planetary-ledger-event.schema.json

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class EventType(str, Enum):
    CAPABILITY_GRANTED = "capability_granted"
    CAPABILITY_REVOKED = "capability_revoked"
    POLICY_VIOLATION = "policy_violation"
    MODULE_RESTART = "module_restart"
    TWIN_SYNC = "twin_sync"
    MEMORY_COMMIT = "memory_commit"
    SESSION_INIT = "session_init"
    SESSION_CLOSE = "session_close"
    SCHUMANN_SYNC = "schumann_sync"
    CRISIS_TRIGGERED = "crisis_triggered"
    GOVERNANCE_AUDIT = "governance_audit"
    CUSTOM = "custom"


@dataclass
class LedgerEvent:
    """Immutable ledger event, schema-faithful to planetary-ledger-event.schema.json."""

    event_type: EventType
    source_node: str                      # UUID string of originating NEXUS node
    payload: dict[str, Any]
    signature_algorithm: str = "HMAC-SHA256"
    signature_value: str = ""
    signature_key_id: str | None = None
    parent_event_id: str | None = None    # Merkle-DAG parent link
    session_id: str | None = None
    schema_version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)

    # Auto-assigned
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to schema-compliant dict."""
        d: dict[str, Any] = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source_node": self.source_node,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "signature": {
                "algorithm": self.signature_algorithm,
                "value": self.signature_value,
            },
            "schema_version": self.schema_version,
            "tags": self.tags,
        }
        if self.signature_key_id:
            d["signature"]["key_id"] = self.signature_key_id
        if self.parent_event_id:
            d["parent_event_id"] = self.parent_event_id
        if self.session_id:
            d["session_id"] = self.session_id
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "LedgerEvent":
        sig = d["signature"]
        return cls(
            event_id=d["event_id"],
            event_type=EventType(d["event_type"]),
            source_node=d["source_node"],
            payload=d["payload"],
            signature_algorithm=sig["algorithm"],
            signature_value=sig["value"],
            signature_key_id=sig.get("key_id"),
            parent_event_id=d.get("parent_event_id"),
            session_id=d.get("session_id"),
            schema_version=d.get("schema_version", "1.0.0"),
            tags=d.get("tags", []),
            timestamp=d["timestamp"],
        )

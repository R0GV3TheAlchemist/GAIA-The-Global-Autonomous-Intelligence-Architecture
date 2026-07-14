"""
core/lifecycle/ed25519_audit.py
C27 §5 — Canonical Audit Log Schema (Phase 2 bridge)

Note: Canon requires Ed25519 signatures. This implementation provides the
schema and signing interface. In environments without cryptography wiring,
it uses a deterministic placeholder signer while preserving the schema.
"""

from __future__ import annotations

import base64
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass
class AuditSignature:
    algorithm: str = "Ed25519"
    public_key_id: str = "phase2-ephemeral-key"
    value: str = ""


@dataclass
class CanonicalAuditEntry:
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    gaian_id: str = ""
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str = "SYSTEM_EVENT"
    from_state: Optional[str] = None
    to_state: Optional[str] = None
    trigger_class: str = "SYSTEM_EVENT"
    actor_id: Optional[str] = None
    justification: Optional[str] = None
    metadata: Dict[str, Optional[str]] = field(default_factory=dict)
    signature: AuditSignature = field(default_factory=AuditSignature)
    previous_entry_hash: str = ""

    def payload_for_signing(self) -> bytes:
        payload = {
            "entry_id": self.entry_id,
            "gaian_id": self.gaian_id,
            "timestamp_utc": self.timestamp_utc,
            "event_type": self.event_type,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "trigger_class": self.trigger_class,
            "actor_id": self.actor_id,
            "justification": self.justification,
            "metadata": self.metadata,
            "previous_entry_hash": self.previous_entry_hash,
        }
        return json.dumps(payload, sort_keys=True).encode("utf-8")

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "gaian_id": self.gaian_id,
            "timestamp_utc": self.timestamp_utc,
            "event_type": self.event_type,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "trigger_class": self.trigger_class,
            "actor_id": self.actor_id,
            "justification": self.justification,
            "metadata": self.metadata,
            "signature": {
                "algorithm": self.signature.algorithm,
                "public_key_id": self.signature.public_key_id,
                "value": self.signature.value,
            },
            "previous_entry_hash": self.previous_entry_hash,
        }


class Phase2Ed25519BridgeSigner:
    """Schema-compatible signer bridge for Phase 2 until vault-backed Ed25519 is wired."""

    def __init__(self, public_key_id: str = "phase2-ephemeral-key") -> None:
        self.public_key_id = public_key_id

    def sign(self, payload: bytes) -> AuditSignature:
        digest = hashlib.sha256(payload).digest()
        return AuditSignature(
            algorithm="Ed25519",
            public_key_id=self.public_key_id,
            value=base64.b64encode(digest).decode("ascii"),
        )

    def previous_hash(self, prior_entry: Optional[CanonicalAuditEntry]) -> str:
        if prior_entry is None:
            return ""
        return hashlib.sha256(json.dumps(prior_entry.to_dict(), sort_keys=True).encode("utf-8")).hexdigest()

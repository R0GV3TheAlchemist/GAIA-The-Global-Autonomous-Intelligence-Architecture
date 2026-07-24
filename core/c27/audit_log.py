# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
core.c27.audit_log — Append-only, SHA-256 chained, RBAC-gated audit log

Authority: C27 §5

Implementation targets:
  C27-IMPL-006  AuditLogEntry dataclass (C27 §5.1 JSON schema)
  C27-IMPL-007  AuditLogWriter (genesis entry + chained append)
  C27-IMPL-008  SHA-256 entry_hash + placeholder signature
  C27-IMPL-009  AuditLogReader with RBAC gating
  C27-IMPL-010  AuditLogIntegrityVerifier
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.c27.rbac import C27Role, ROLE_ENVELOPES


# ---------------------------------------------------------------------------
# C27-IMPL-006 — AuditLogEntry
# ---------------------------------------------------------------------------

@dataclass
class AuditLogEntry:
    """A single entry in the C27 §5.1 audit log chain."""

    entry_id:            str
    gaian_id:            str
    event_type:          str
    actor:               str
    action:              str
    payload:             Dict[str, Any]
    previous_entry_hash: Optional[str]         # None for genesis entry
    timestamp:           datetime               = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    entry_hash:          str                    = field(default="")
    signature:           str                    = field(default="")


# ---------------------------------------------------------------------------
# Internal: SHA-256 hashing helpers
# ---------------------------------------------------------------------------

def _compute_entry_hash(entry: AuditLogEntry) -> str:
    """Deterministic SHA-256 of the entry's canonical fields."""
    canonical = {
        "entry_id":            entry.entry_id,
        "gaian_id":            entry.gaian_id,
        "event_type":          entry.event_type,
        "actor":               entry.actor,
        "action":              entry.action,
        "payload":             entry.payload,
        "previous_entry_hash": entry.previous_entry_hash,
        "timestamp":           entry.timestamp.isoformat(),
    }
    serialised = json.dumps(canonical, sort_keys=True, default=str)
    return hashlib.sha256(serialised.encode()).hexdigest()


def _sign_entry(entry: AuditLogEntry) -> str:
    """Placeholder HMAC-style signature (real PKI wired in C27-IMPL-008+)."""
    return f"sig:{entry.entry_hash[:16]}"


# ---------------------------------------------------------------------------
# C27-IMPL-007 — AuditLogWriter
# ---------------------------------------------------------------------------

class AuditLogWriter:
    """
    Append-only writer for a single GAIAN's audit log.
    Maintains an in-memory store; persistence layer wired in later impl targets.
    """

    def __init__(self, gaian_id: str) -> None:
        self.gaian_id = gaian_id
        self._entries: List[AuditLogEntry] = []

    def append(
        self,
        event_type: str,
        actor: str,
        action: str,
        payload: Dict[str, Any],
    ) -> AuditLogEntry:
        """Append a new entry to the chain and return it with hash + signature."""
        previous_hash: Optional[str] = (
            None if not self._entries
            else self._entries[-1].entry_hash
        )

        entry = AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            gaian_id=self.gaian_id,
            event_type=event_type,
            actor=actor,
            action=action,
            payload=payload,
            previous_entry_hash=previous_hash,
        )

        entry.entry_hash = _compute_entry_hash(entry)
        entry.signature  = _sign_entry(entry)

        self._entries.append(entry)
        return entry

    @property
    def entries(self) -> List[AuditLogEntry]:
        """Read-only view of all entries in chronological order."""
        return list(self._entries)


# ---------------------------------------------------------------------------
# In-memory global store (keyed by gaian_id) — replaced by DB in later targets
# ---------------------------------------------------------------------------

_STORE: Dict[str, AuditLogWriter] = {}


def _get_writer(gaian_id: str) -> AuditLogWriter:
    if gaian_id not in _STORE:
        _STORE[gaian_id] = AuditLogWriter(gaian_id)
    return _STORE[gaian_id]


# ---------------------------------------------------------------------------
# C27-IMPL-009 — AuditLogReader
# ---------------------------------------------------------------------------

_READ_PERMITTED_ROLES = {
    C27Role.GAIAN_SELF,
    C27Role.SENTINEL,
    C27Role.COUNCIL_MEMBER,
    C27Role.STEWARD,
}


class AuditLogReader:
    """RBAC-gated reader for C27 audit logs."""

    def query(
        self,
        gaian_id: str,
        requestor_id: str,
        requestor_role: C27Role,
    ) -> List[AuditLogEntry]:
        if requestor_role not in _READ_PERMITTED_ROLES:
            raise PermissionError(
                f"[C27 §5] Role '{requestor_role.value}' is not authorised to "
                f"read audit logs for GAIAN '{gaian_id}'."
            )
        writer = _get_writer(gaian_id)
        return writer.entries


# ---------------------------------------------------------------------------
# C27-IMPL-010 — AuditLogIntegrityVerifier
# ---------------------------------------------------------------------------

class AuditLogIntegrityVerifier:
    """Re-computes the SHA-256 chain and returns True iff every link is intact."""

    def verify(self, gaian_id: str) -> bool:
        writer = _get_writer(gaian_id)
        entries = writer.entries

        if not entries:
            return True  # empty chain is trivially intact

        for i, entry in enumerate(entries):
            # Verify stored hash matches recomputed hash
            expected_hash = _compute_entry_hash(entry)
            if entry.entry_hash != expected_hash:
                return False

            # Verify chain linkage
            expected_prev = None if i == 0 else entries[i - 1].entry_hash
            if entry.previous_entry_hash != expected_prev:
                return False

        return True

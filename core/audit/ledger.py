"""
core.audit.ledger
=================
Append-only, tamper-evident audit ledger for GAIA-OS.

Design goals
------------
- Append-only: events are written once and never mutated in place.
- Tamper-evident: each row stores a SHA-256 hash of its own canonical
  payload plus the previous row's hash, forming a linked chain.
- Queryable: SQLite-backed for local sovereignty, filtering by user,
  session, event_type, action, and time range.
- Explainable: every event can carry a human-readable justification,
  policy decision, memory references, and quantum-state snapshot id.
- Lightweight: stdlib-only implementation (sqlite3, json, hashlib).

Threat model
------------
This is not a blockchain and does not prevent deletion by an attacker
with file-system access. It *does* provide strong local evidence of
in-place modification or row insertion/reordering once the chain is
verified end-to-end. For stronger guarantees, mirror the daily Merkle
root or latest chain hash to a remote notary later.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


class EventType(str, Enum):
    ACTION_PROPOSED      = "action_proposed"
    ACTION_EXECUTED      = "action_executed"
    ACTION_FAILED        = "action_failed"
    POLICY_DECISION      = "policy_decision"
    MEMORY_WRITTEN       = "memory_written"
    MEMORY_RETRIEVED     = "memory_retrieved"
    GOAL_CREATED         = "goal_created"
    GOAL_UPDATED         = "goal_updated"
    TASK_SCHEDULED       = "task_scheduled"
    TASK_COMPLETED       = "task_completed"
    TASK_FAILED          = "task_failed"
    STATE_SNAPSHOT       = "state_snapshot"
    CONSENT_GRANTED      = "consent_granted"
    CONSENT_DENIED       = "consent_denied"
    SYSTEM_EVENT         = "system_event"


@dataclass
class AuditEvent:
    """
    One immutable audit event.

    Attributes
    ----------
    event_type      : EventType enum describing what happened.
    actor           : Who/what initiated the event ("gaia", "user", "system").
    user_id         : User associated with the event.
    session_id      : Session context, if any.
    action          : Machine-readable action key (e.g. "web_search").
    outcome         : Human-readable result ("success", "denied", "error").
    justification   : Natural-language rationale for the event.
    policy_rule     : Policy rule that applied, if any.
    memory_refs     : Related memory item ids (or hashes).
    state_ref       : Related quantum-state snapshot id/hash.
    goal_id         : Related goal id.
    task_id         : Related task id.
    metadata        : Arbitrary structured payload.
    created_at      : Unix timestamp.
    event_id        : UUID4 string assigned at creation.
    """
    event_type:    EventType
    actor:         str
    user_id:       Optional[str]           = None
    session_id:    Optional[str]           = None
    action:        Optional[str]           = None
    outcome:       Optional[str]           = None
    justification: str                     = ""
    policy_rule:   Optional[str]           = None
    memory_refs:   List[str]               = field(default_factory=list)
    state_ref:     Optional[str]           = None
    goal_id:       Optional[str]           = None
    task_id:       Optional[str]           = None
    metadata:      Dict[str, Any]          = field(default_factory=dict)
    created_at:    float                   = field(default_factory=time.time)
    event_id:      str                     = field(default_factory=lambda: str(uuid.uuid4()))

    def canonical_payload(self) -> Dict[str, Any]:
        """Stable dict used for hashing; excludes chain fields."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "actor": self.actor,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "action": self.action,
            "outcome": self.outcome,
            "justification": self.justification,
            "policy_rule": self.policy_rule,
            "memory_refs": list(self.memory_refs),
            "state_ref": self.state_ref,
            "goal_id": self.goal_id,
            "task_id": self.task_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.canonical_payload()

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "AuditEvent":
        return cls(
            event_type=EventType(row["event_type"]),
            actor=row["actor"],
            user_id=row["user_id"],
            session_id=row["session_id"],
            action=row["action"],
            outcome=row["outcome"],
            justification=row["justification"],
            policy_rule=row["policy_rule"],
            memory_refs=json.loads(row["memory_refs"] or "[]"),
            state_ref=row["state_ref"],
            goal_id=row["goal_id"],
            task_id=row["task_id"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
            event_id=row["event_id"],
        )


@dataclass
class LedgerVerificationResult:
    ok: bool
    checked_rows: int
    failed_row_id: Optional[int] = None
    reason: Optional[str] = None
    expected_hash: Optional[str] = None
    actual_hash: Optional[str] = None


class ActionLedger:
    """
    SQLite-backed append-only audit ledger.

    Each row contains:
      - prev_hash   : hash of the previous row in insertion order
      - row_hash    : SHA-256(canonical_json(payload) + prev_hash)

    This forms a hash chain. Any in-place change, row deletion, or row
    reordering will break verification from the first altered row onward.
    """

    def __init__(self, db_path: str | Path = "gaia_audit.sqlite") -> None:
        self.db_path = str(db_path)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._init_schema()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append(self, event: AuditEvent) -> int:
        """
        Append one immutable event to the ledger.

        Returns the SQLite row id of the inserted event.
        """
        prev_hash = self._latest_hash()
        payload   = event.canonical_payload()
        row_hash  = self._hash_payload(payload, prev_hash)

        cur = self._conn.execute(
            """
            INSERT INTO audit_events (
                event_id, event_type, actor, user_id, session_id,
                action, outcome, justification, policy_rule,
                memory_refs, state_ref, goal_id, task_id,
                metadata, created_at, prev_hash, row_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.event_type.value,
                event.actor,
                event.user_id,
                event.session_id,
                event.action,
                event.outcome,
                event.justification,
                event.policy_rule,
                json.dumps(event.memory_refs, separators=(",", ":"), sort_keys=True),
                event.state_ref,
                event.goal_id,
                event.task_id,
                json.dumps(event.metadata, separators=(",", ":"), sort_keys=True),
                event.created_at,
                prev_hash,
                row_hash,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def append_many(self, events: Sequence[AuditEvent]) -> List[int]:
        ids: List[int] = []
        for ev in events:
            ids.append(self.append(ev))
        return ids

    def get(self, row_id: int) -> Optional[Dict[str, Any]]:
        row = self._conn.execute(
            "SELECT rowid, * FROM audit_events WHERE rowid = ?", (row_id,)
        ).fetchone()
        return dict(row) if row else None

    def recent(self, limit: int = 50, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if user_id:
            rows = self._conn.execute(
                "SELECT rowid, * FROM audit_events WHERE user_id = ? ORDER BY rowid DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT rowid, * FROM audit_events ORDER BY rowid DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def query(
        self,
        *,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        event_type: Optional[EventType] = None,
        action: Optional[str] = None,
        since: Optional[float] = None,
        until: Optional[float] = None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        clauses = []
        params: List[Any] = []

        if user_id is not None:
            clauses.append("user_id = ?")
            params.append(user_id)
        if session_id is not None:
            clauses.append("session_id = ?")
            params.append(session_id)
        if event_type is not None:
            clauses.append("event_type = ?")
            params.append(event_type.value)
        if action is not None:
            clauses.append("action = ?")
            params.append(action)
        if since is not None:
            clauses.append("created_at >= ?")
            params.append(since)
        if until is not None:
            clauses.append("created_at <= ?")
            params.append(until)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT rowid, * FROM audit_events {where} ORDER BY rowid DESC LIMIT ?"
        params.append(limit)
        rows = self._conn.execute(sql, tuple(params)).fetchall()
        return [dict(r) for r in rows]

    def verify_chain(self) -> LedgerVerificationResult:
        """
        Recompute the full chain from the first row and verify that every
        row_hash and prev_hash matches what is stored.
        """
        rows = self._conn.execute(
            "SELECT rowid, * FROM audit_events ORDER BY rowid ASC"
        ).fetchall()
        prev_hash = "GENESIS"
        checked = 0

        for row in rows:
            payload = {
                "event_id": row["event_id"],
                "event_type": row["event_type"],
                "actor": row["actor"],
                "user_id": row["user_id"],
                "session_id": row["session_id"],
                "action": row["action"],
                "outcome": row["outcome"],
                "justification": row["justification"],
                "policy_rule": row["policy_rule"],
                "memory_refs": json.loads(row["memory_refs"] or "[]"),
                "state_ref": row["state_ref"],
                "goal_id": row["goal_id"],
                "task_id": row["task_id"],
                "metadata": json.loads(row["metadata"] or "{}"),
                "created_at": row["created_at"],
            }

            if row["prev_hash"] != prev_hash:
                return LedgerVerificationResult(
                    ok=False,
                    checked_rows=checked,
                    failed_row_id=row["rowid"],
                    reason="prev_hash mismatch",
                    expected_hash=prev_hash,
                    actual_hash=row["prev_hash"],
                )

            expected_row_hash = self._hash_payload(payload, prev_hash)
            if row["row_hash"] != expected_row_hash:
                return LedgerVerificationResult(
                    ok=False,
                    checked_rows=checked,
                    failed_row_id=row["rowid"],
                    reason="row_hash mismatch",
                    expected_hash=expected_row_hash,
                    actual_hash=row["row_hash"],
                )

            prev_hash = row["row_hash"]
            checked += 1

        return LedgerVerificationResult(ok=True, checked_rows=checked)

    def latest_chain_hash(self) -> str:
        return self._latest_hash()

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id      TEXT NOT NULL UNIQUE,
                event_type    TEXT NOT NULL,
                actor         TEXT NOT NULL,
                user_id       TEXT,
                session_id    TEXT,
                action        TEXT,
                outcome       TEXT,
                justification TEXT,
                policy_rule   TEXT,
                memory_refs   TEXT,
                state_ref     TEXT,
                goal_id       TEXT,
                task_id       TEXT,
                metadata      TEXT,
                created_at    REAL NOT NULL,
                prev_hash     TEXT NOT NULL,
                row_hash      TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_audit_user_id    ON audit_events(user_id);
            CREATE INDEX IF NOT EXISTS idx_audit_session_id ON audit_events(session_id);
            CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_events(event_type);
            CREATE INDEX IF NOT EXISTS idx_audit_action     ON audit_events(action);
            CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_events(created_at);
            """
        )
        self._conn.commit()

    def _latest_hash(self) -> str:
        row = self._conn.execute(
            "SELECT row_hash FROM audit_events ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else "GENESIS"

    @staticmethod
    def _hash_payload(payload: Dict[str, Any], prev_hash: str) -> str:
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        material = (prev_hash + "|" + blob).encode("utf-8")
        return hashlib.sha256(material).hexdigest()

# Copyright (c) 2026 Kyle Alexander Steen (R0GV3 The Alchemist). All Rights Reserved.
# NEXUS Planetary Ledger — PlanetaryLedger
# SQLite-backed, append-only, Merkle-DAG indexed, Ed25519/HMAC-signed.

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any

from .dag import MerkleDAG
from .event import EventType, LedgerEvent
from .signer import BaseSigner, HMACSigner

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = Path(os.environ.get("NEXUS_LEDGER_PATH", "nexus_data/planetary_ledger.db"))
_DEFAULT_NODE_ID = os.environ.get("NEXUS_NODE_ID", "00000000-0000-0000-0000-000000000001")


class PlanetaryLedger:
    """
    Append-only, SQLite-backed Planetary Ledger with Merkle-DAG provenance.

    Every event is:
      1. Signed (Ed25519 or HMAC-SHA256)
      2. Linked to its parent via parent_event_id (Merkle-DAG causal chain)
      3. SHA-256 content-hashed and indexed in the in-memory DAG
      4. Persisted atomically to SQLite

    Usage::

        ledger = PlanetaryLedger()
        event = ledger.append(
            event_type=EventType.SESSION_INIT,
            payload={"session": "abc"},
            tags=["bootstrap"],
        )
    """

    def __init__(
        self,
        db_path: Path | str | None = None,
        node_id: str | None = None,
        signer: BaseSigner | None = None,
        session_id: str | None = None,
    ) -> None:
        self._db_path = Path(db_path) if db_path else _DEFAULT_DB_PATH
        self._node_id = node_id or _DEFAULT_NODE_ID
        self._signer: BaseSigner = signer or HMACSigner(
            os.environ.get("NEXUS_LEDGER_SECRET", "nexus-default-secret")
        )
        self._session_id = session_id
        self._dag = MerkleDAG()
        self._lock = threading.Lock()
        self._last_event_id: str | None = None

        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._replay_into_dag()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append(
        self,
        event_type: EventType,
        payload: dict[str, Any],
        tags: list[str] | None = None,
        parent_event_id: str | None = None,
        session_id: str | None = None,
    ) -> LedgerEvent:
        """Append a new event to the ledger. Thread-safe. Returns the committed event."""
        with self._lock:
            # Chain to previous event unless an explicit parent is given
            parent = parent_event_id or self._last_event_id

            event = LedgerEvent(
                event_type=event_type,
                source_node=self._node_id,
                payload=payload,
                signature_algorithm=self._signer.algorithm,
                parent_event_id=parent,
                session_id=session_id or self._session_id,
                tags=tags or [],
            )

            event_dict = event.to_dict()
            sig = self._signer.sign(event_dict)
            event.signature_value = sig
            event_dict["signature"]["value"] = sig

            self._dag.add(event_dict)
            self._persist(event_dict)
            self._last_event_id = event.event_id

            logger.info(
                "ledger.append event_id=%s type=%s parent=%s",
                event.event_id,
                event.event_type.value,
                parent,
            )
            return event

    def query(
        self,
        event_type: EventType | None = None,
        session_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Query events from SQLite. Returns list of event dicts."""
        with self._lock:
            clauses: list[str] = []
            params: list[Any] = []
            if event_type:
                clauses.append("event_type = ?")
                params.append(event_type.value)
            if session_id:
                clauses.append("session_id = ?")
                params.append(session_id)
            where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
            sql = f"SELECT payload_json FROM events {where} ORDER BY rowid DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            conn = self._get_conn()
            rows = conn.execute(sql, params).fetchall()
            return [json.loads(r[0]) for r in rows]

    def verify_event(self, event_id: str) -> bool:
        """Verify a stored event's signature and DAG hash integrity."""
        with self._lock:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT payload_json FROM events WHERE event_id = ?", (event_id,)
            ).fetchone()
            if not row:
                return False
            event_dict = json.loads(row[0])
            sig = event_dict["signature"]["value"]
            sig_ok = self._signer.verify(event_dict, sig)
            dag_ok = self._dag.verify_chain(event_id, event_dict)
            return sig_ok and dag_ok

    def get_chain(self, event_id: str) -> list[str]:
        """Return the ancestor chain for an event (oldest first, not including event itself)."""
        return self._dag.ancestors(event_id)

    @property
    def size(self) -> int:
        with self._lock:
            conn = self._get_conn()
            return conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    @property
    def dag(self) -> MerkleDAG:
        return self._dag

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id    TEXT PRIMARY KEY,
                event_type  TEXT NOT NULL,
                session_id  TEXT,
                timestamp   TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON events(session_id)")
        conn.commit()

    def _persist(self, event_dict: dict[str, Any]) -> None:
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO events (event_id, event_type, session_id, timestamp, payload_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                event_dict["event_id"],
                event_dict["event_type"],
                event_dict.get("session_id"),
                event_dict["timestamp"],
                json.dumps(event_dict),
            ),
        )
        conn.commit()

    def _replay_into_dag(self) -> None:
        """On startup, replay all stored events into the in-memory DAG."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT payload_json FROM events ORDER BY rowid ASC"
        ).fetchall()
        for row in rows:
            event_dict = json.loads(row[0])
            self._dag.add(event_dict)
            self._last_event_id = event_dict["event_id"]
        if rows:
            logger.info("ledger.replay loaded %d events into DAG", len(rows))

    _conn: sqlite3.Connection | None = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self._db_path), check_same_thread=False
            )
            self._conn.execute("PRAGMA journal_mode=WAL")
        return self._conn

"""CrisisEngine — main orchestrator for multi-turn crisis synthesis.

GAIA-OS Issue #281 — StorageBackend mirror added.

Usage:
    from crisis_engine import CrisisEngine, EngineConfig

    engine = CrisisEngine(EngineConfig(principal_id="kyle"))
    snapshot = engine.evaluate(user_text, session_id="sess_001", turn_index=3)

    if snapshot.requires_action:
        message = engine.get_intervention_message()
        # inject message into GAIA's response pipeline

StorageBackend mirror
---------------------
Local SQLite is the safety-critical primary store — HANDOFF-tier records
in particular must never be lossy.  The StorageBackend is a secondary
mirror for mesh-wide visibility and Phase 2 planetary persistence.

HANDOFF records are mirrored *synchronously* (awaited) before build_handoff()
returns, so that no handoff event can be lost due to a daemon thread race.
All other record types (snapshots, session records) use fire-and-forget.

Key prefixes:
  crisis:<principal_id>:snapshot:<safe_iso_ts>   — CrisisSnapshot
  crisis:<principal_id>:session:<session_id>      — SessionRiskRecord
  crisis:<principal_id>:handoff:<safe_iso_ts>     — HandoffRecord (sync)
"""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .escalation import (
    build_handoff_record,
    determine_escalation_tier,
    get_intervention_message,
)
from .taxonomy import classify_turn
from .trajectory import SessionRiskRecord, TrajectoryModel
from .types import (
    CrisisSnapshot,
    EscalationTier,
    HandoffRecord,
    RiskLevel,
)

try:
    from core.storage import get_backend as _get_storage_backend
    _STORAGE_AVAILABLE = True
except ImportError:
    _STORAGE_AVAILABLE = False
    _get_storage_backend = None  # type: ignore[assignment]

logger = logging.getLogger("gaia.crisis_engine")

_BACKEND_KEY_PREFIX = "crisis"


# ---------------------------------------------------------------------------
# Backend mirror helpers
# ---------------------------------------------------------------------------

def _backend_key(principal_id: str, record_type: str, discriminator: str) -> str:
    """
    Build the backend mirror key.
    Format: crisis:<principal_id>:<record_type>:<discriminator>

    discriminator is a safe ISO timestamp (colons → hyphens) for
    snapshot/handoff, or the session_id for session records.
    """
    safe_disc = discriminator.replace(":", "-").replace("+", "Z")
    return f"{_BACKEND_KEY_PREFIX}:{principal_id}:{record_type}:{safe_disc}"


def _mirror(
    backend: Any,
    key: str,
    payload: bytes,
    ttl: Optional[int] = None,
) -> None:
    """
    Fire-and-forget mirror write for non-critical records.
    Launches a daemon thread; never blocks the caller.
    """
    def _run() -> None:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(backend.put(key, payload, ttl=ttl))
            loop.close()
        except Exception as exc:
            logger.warning(
                f"[CrisisEngine] ⚠ Backend mirror write failed (non-fatal): "
                f"key={key!r} err={exc}"
            )
    threading.Thread(target=_run, daemon=True, name="crisis-mirror").start()


async def _mirror_sync(
    backend: Any,
    key: str,
    payload: bytes,
    ttl: Optional[int] = None,
) -> None:
    """
    Synchronous (awaited) mirror write for HANDOFF-tier records.
    HANDOFF events must be durable before build_handoff() returns.
    Failure is logged but never propagated — local SQLite already committed.
    """
    try:
        await backend.put(key, payload, ttl=ttl)
    except Exception as exc:
        logger.error(
            f"[CrisisEngine] ❌ HANDOFF backend mirror failed: key={key!r} err={exc}. "
            "Local SQLite record is authoritative."
        )


# ---------------------------------------------------------------------------
# Config + Engine
# ---------------------------------------------------------------------------

@dataclass
class EngineConfig:
    principal_id:    str
    db_path:         Optional[Path]   = None    # defaults to :memory: if None
    window_size:     int              = 14      # sessions in rolling window
    state_callback:  Optional[object] = None   # callable(snapshot) on state change
    # StorageBackend mirror ──────────────────────────────
    storage_backend: Any              = field(default=..., repr=False)
    # ... sentinel = use default (SQLite singleton)
    # None         = mirroring disabled
    # <instance>   = use the supplied backend
    backend_ttl:     Optional[int]    = None    # TTL for mirror entries (seconds)


class CrisisEngine:
    """
    Orchestrates crisis signal detection, trajectory synthesis, and escalation.

    Thread-safety: Not thread-safe. Each Gaian instance should own its own
    CrisisEngine. For concurrent access, wrap in an asyncio lock.

    HANDOFF records are mirrored synchronously to the StorageBackend before
    build_handoff() returns.  All other mirror writes are fire-and-forget.
    Local SQLite is always the safety-critical source of truth.
    """

    def __init__(self, config: EngineConfig) -> None:
        self._config     = config
        self._trajectory = TrajectoryModel(window_size=config.window_size)
        self._db_path    = config.db_path or Path(":memory:")
        self._last_snapshot: Optional[CrisisSnapshot] = None

        # ── StorageBackend setup (same sentinel pattern as AuditStore) ──
        sb = config.storage_backend
        if sb is ...:
            if _STORAGE_AVAILABLE and _get_storage_backend is not None:
                try:
                    self._backend: Optional[Any] = _get_storage_backend()
                except Exception as exc:
                    logger.warning(
                        f"[CrisisEngine] Could not initialise default backend: {exc}. "
                        "Mirroring disabled."
                    )
                    self._backend = None
            else:
                self._backend = None
        else:
            self._backend = sb

        if self._backend is not None:
            logger.debug(
                f"[CrisisEngine] Backend mirror: {self._backend!r} "
                f"(principal={config.principal_id!r})"
            )

        self._init_db()
        self._restore_window()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        user_text:  str,
        session_id: str,
        turn_index: int = 0,
    ) -> CrisisSnapshot:
        """
        Evaluate one turn of user text and return the current risk snapshot.
        Primary integration point for GAIA's chat pipeline.
        Call once per user turn, before generating GAIA's response.
        """
        # 1. Classify this turn
        signals = classify_turn(user_text, turn_index=turn_index, session_id=session_id)

        # 2. Synthesise cross-session risk
        synthesised_risk = self._trajectory.synthesise_risk(signals)

        # 3. Build snapshot
        slope       = self._trajectory.trajectory_slope()
        consecutive = self._trajectory.consecutive_distress_sessions()
        peak_72h    = self._trajectory.peak_risk_within(hours=72)

        snapshot = CrisisSnapshot(
            principal_id=self._config.principal_id,
            current_risk=synthesised_risk,
            escalation_tier=EscalationTier.MONITOR,
            trajectory_slope=slope,
            sessions_in_distress=consecutive,
            peak_risk_72h=peak_72h,
            active_signals=signals,
        )
        snapshot.escalation_tier = determine_escalation_tier(snapshot)

        # 4. Persist to SQLite (primary, synchronous)
        self._persist_snapshot(snapshot)
        self._last_snapshot = snapshot

        # 5. State callback — never let it crash the safety pipeline
        if self._config.state_callback and callable(self._config.state_callback):
            try:
                self._config.state_callback(snapshot)
            except Exception:
                pass

        return snapshot

    def close_session(
        self,
        session_id:   str,
        peak_risk:    RiskLevel = RiskLevel.NONE,
        signal_count: int       = 0,
        has_explicit: bool      = False,
        has_masked:   bool      = False,
    ) -> None:
        """
        Call at the end of each session to commit the session risk record.
        The trajectory window is updated here so GRADUAL signals are
        visible in the next session.
        """
        record = SessionRiskRecord(
            session_id=session_id,
            peak_risk=peak_risk,
            signal_count=signal_count,
            has_explicit=has_explicit,
            has_masked=has_masked,
        )
        self._trajectory.record_session(record)
        self._persist_session_record(record)

    def get_intervention_message(self) -> str:
        """Return the appropriate intervention message for the current risk state."""
        if not self._last_snapshot:
            return ""
        return get_intervention_message(self._last_snapshot.escalation_tier)

    async def build_handoff(self) -> Optional[HandoffRecord]:
        """
        Build a HandoffRecord if the current state warrants handoff.

        NOTE: This method is now async so that HANDOFF records can be
        mirrored synchronously to the StorageBackend before returning.
        Callers that previously used this synchronously should await it.
        Local SQLite write still happens synchronously first.
        """
        if not self._last_snapshot:
            return None
        if self._last_snapshot.escalation_tier != EscalationTier.HANDOFF:
            return None
        record = build_handoff_record(self._last_snapshot)

        # 1. SQLite write — always first, always authoritative
        self._persist_handoff(record)

        # 2. Synchronous backend mirror — awaited before returning
        #    so no HANDOFF event is ever lost in-flight
        if self._backend is not None:
            payload = json.dumps(
                {
                    "principal_id":    record.principal_id,
                    "resource_type":   record.resource_type,
                    "resource_detail": record.resource_detail,
                    "message_sent":    record.message_sent,
                    "handed_off_at":   record.handed_off_at.isoformat(),
                },
                separators=(",", ":"),
            ).encode("utf-8")
            bkey = _backend_key(
                record.principal_id, "handoff", record.handed_off_at.isoformat()
            )
            await _mirror_sync(self._backend, bkey, payload, self._config.backend_ttl)

        return record

    def history(self, limit: int = 30) -> list[dict]:
        """Return recent snapshot history for this principal."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT data FROM crisis_snapshots "
                "WHERE principal_id = ? ORDER BY evaluated_at DESC LIMIT ?",
                (self._config.principal_id, limit),
            ).fetchall()
        return [json.loads(r[0]) for r in rows]

    async def backend_ping(self) -> bool:
        """
        Health-check the StorageBackend.
        Consistent with AuditStore / SovereignMemory / TelemetryCollector
        for the mesh server health endpoint.
        """
        if self._backend is None:
            return False
        try:
            return await self._backend.ping()
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Internal — database
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS crisis_snapshots (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    principal_id TEXT NOT NULL,
                    risk_level   TEXT NOT NULL,
                    escalation   TEXT NOT NULL,
                    data         TEXT NOT NULL,
                    evaluated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS crisis_session_records (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    principal_id TEXT NOT NULL,
                    session_id   TEXT NOT NULL,
                    peak_risk    TEXT NOT NULL,
                    signal_count INTEGER NOT NULL,
                    has_explicit INTEGER NOT NULL,
                    has_masked   INTEGER NOT NULL,
                    recorded_at  TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS crisis_handoffs (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    principal_id    TEXT NOT NULL,
                    resource_type   TEXT NOT NULL,
                    resource_detail TEXT NOT NULL,
                    message_sent    TEXT NOT NULL,
                    handed_off_at   TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_snapshots_principal
                    ON crisis_snapshots(principal_id, evaluated_at);
                CREATE INDEX IF NOT EXISTS idx_sessions_principal
                    ON crisis_session_records(principal_id, recorded_at);
            """)

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _persist_snapshot(self, snapshot: CrisisSnapshot) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO crisis_snapshots "
                "(principal_id, risk_level, escalation, data, evaluated_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    snapshot.principal_id,
                    snapshot.current_risk.value,
                    snapshot.escalation_tier.value,
                    json.dumps(snapshot.to_dict()),
                    snapshot.evaluated_at.isoformat(),
                ),
            )
        # Fire-and-forget mirror — snapshots are informational
        if self._backend is not None:
            payload = json.dumps(
                snapshot.to_dict(), separators=(",", ":"), default=str
            ).encode("utf-8")
            bkey = _backend_key(
                snapshot.principal_id, "snapshot", snapshot.evaluated_at.isoformat()
            )
            _mirror(self._backend, bkey, payload, self._config.backend_ttl)

    def _persist_session_record(self, record: SessionRiskRecord) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO crisis_session_records "
                "(principal_id, session_id, peak_risk, signal_count, "
                "has_explicit, has_masked, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    self._config.principal_id,
                    record.session_id,
                    record.peak_risk.value,
                    record.signal_count,
                    int(record.has_explicit),
                    int(record.has_masked),
                    record.recorded_at.isoformat(),
                ),
            )
        # Fire-and-forget mirror — session records are informational
        if self._backend is not None:
            payload = json.dumps(
                {
                    "principal_id": self._config.principal_id,
                    "session_id":   record.session_id,
                    "peak_risk":    record.peak_risk.value,
                    "signal_count": record.signal_count,
                    "has_explicit": record.has_explicit,
                    "has_masked":   record.has_masked,
                    "recorded_at":  record.recorded_at.isoformat(),
                },
                separators=(",", ":"),
            ).encode("utf-8")
            bkey = _backend_key(
                self._config.principal_id, "session", record.session_id
            )
            _mirror(self._backend, bkey, payload, self._config.backend_ttl)

    def _persist_handoff(self, record: HandoffRecord) -> None:
        """SQLite write only — backend mirror is handled in build_handoff() (async, sync)."""
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO crisis_handoffs "
                "(principal_id, resource_type, resource_detail, message_sent, handed_off_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    record.principal_id,
                    record.resource_type,
                    record.resource_detail,
                    record.message_sent,
                    record.handed_off_at.isoformat(),
                ),
            )

    def _restore_window(self) -> None:
        """Cold-start restore: load recent session records into the trajectory window."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT session_id, peak_risk, signal_count, has_explicit, "
                "has_masked, recorded_at FROM crisis_session_records "
                "WHERE principal_id = ? ORDER BY recorded_at ASC LIMIT ?",
                (self._config.principal_id, self._config.window_size),
            ).fetchall()
        records = [
            SessionRiskRecord(
                session_id=r["session_id"],
                peak_risk=RiskLevel(r["peak_risk"]),
                signal_count=r["signal_count"],
                has_explicit=bool(r["has_explicit"]),
                has_masked=bool(r["has_masked"]),
                recorded_at=datetime.fromisoformat(r["recorded_at"]),
            )
            for r in rows
        ]
        self._trajectory.load_from_records(records)

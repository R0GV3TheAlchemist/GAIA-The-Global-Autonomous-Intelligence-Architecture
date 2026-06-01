"""CrisisEngine — main orchestrator for multi-turn crisis synthesis.

Usage:
    from crisis_engine import CrisisEngine, EngineConfig

    engine = CrisisEngine(EngineConfig(principal_id="kyle"))
    snapshot = engine.evaluate(user_text, session_id="sess_001", turn_index=3)

    if snapshot.requires_action:
        message = engine.get_intervention_message()
        # inject message into GAIA's response pipeline
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

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


@dataclass
class EngineConfig:
    principal_id:   str
    db_path:        Optional[Path] = None   # defaults to :memory: if None
    window_size:    int            = 14     # sessions in rolling window
    state_callback: Optional[object] = None  # callable(snapshot) on state change


class CrisisEngine:
    """Orchestrates crisis signal detection, trajectory synthesis, and escalation.

    Thread-safety: Not thread-safe. Each Gaian instance should own its own
    CrisisEngine. For concurrent access, wrap in an asyncio lock.
    """

    def __init__(self, config: EngineConfig):
        self._config    = config
        self._trajectory = TrajectoryModel(window_size=config.window_size)
        self._db_path   = config.db_path or Path(":memory:")
        self._last_snapshot: Optional[CrisisSnapshot] = None
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
        """Evaluate one turn of user text and return the current risk snapshot.

        This is the primary integration point for GAIA's chat pipeline.
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
            escalation_tier=EscalationTier.MONITOR,  # placeholder — set below
            trajectory_slope=slope,
            sessions_in_distress=consecutive,
            peak_risk_72h=peak_72h,
            active_signals=signals,
        )
        snapshot.escalation_tier = determine_escalation_tier(snapshot)

        # 4. Persist
        self._persist_snapshot(snapshot)
        self._last_snapshot = snapshot

        # 5. Callback
        if self._config.state_callback and callable(self._config.state_callback):
            try:
                self._config.state_callback(snapshot)
            except Exception:
                pass  # never let callback crash the safety pipeline

        return snapshot

    def close_session(
        self,
        session_id: str,
        peak_risk:  RiskLevel = RiskLevel.NONE,
        signal_count: int     = 0,
        has_explicit: bool    = False,
        has_masked:   bool    = False,
    ) -> None:
        """Call at the end of each session to commit the session risk record.

        If evaluate() was called during the session, pass the aggregated
        peak_risk from those evaluations. The trajectory window is updated
        here so that GRADUAL signals are visible in the next session.
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

    def build_handoff(self) -> Optional[HandoffRecord]:
        """Build a HandoffRecord if the current state warrants handoff."""
        if not self._last_snapshot:
            return None
        if self._last_snapshot.escalation_tier != EscalationTier.HANDOFF:
            return None
        record = build_handoff_record(self._last_snapshot)
        self._persist_handoff(record)
        return record

    def history(self, limit: int = 30) -> list[dict]:
        """Return recent snapshot history for this principal."""
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT data FROM crisis_snapshots "
                "WHERE principal_id = ? ORDER BY evaluated_at DESC LIMIT ?",
                (self._config.principal_id, limit),
            ).fetchall()
        import json
        return [json.loads(r[0]) for r in rows]

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
        import json
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

    def _persist_handoff(self, record: HandoffRecord) -> None:
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

"""
crisis_engine.engine
====================
CrisisEngine — real-time crisis detection, trajectory synthesis,
escalation, and session persistence for GAIA-OS.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 2.9
GAIAN law              : GAIAN_LAWS.md          Law VI  Crisis Precedes Override
"""
from __future__ import annotations

import logging
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from crisis_engine.escalation import (
    build_handoff_record,
    determine_escalation_tier,
    get_intervention_message,
)
from crisis_engine.taxonomy import classify_turn
from crisis_engine.trajectory import SessionRiskRecord, TrajectoryModel
from crisis_engine.types import (
    CrisisSnapshot,
    EscalationTier,
    HandoffRecord,
    RiskLevel,
)

logger = logging.getLogger("crisis_engine.engine")


@dataclass
class EngineConfig:
    """
    Configuration for CrisisEngine.

    Fields
    ------
    principal_id : Identity of the governing principal.
    db_path      : Optional path to the SQLite persistence file.
                   None → in-memory only (no cold-start restore).
    """
    principal_id: str = "local-gaian"
    db_path: Optional[Path] = None
    affect_arousal_threshold: float = 0.85
    shadow_load_threshold: float = 0.80
    persona_stability_floor: float = 0.35


class CrisisEngine:
    """
    GAIA crisis detection engine.

    Evaluates free-text turns for crisis signals, synthesises cross-session
    risk, computes the escalation tier, and persists session records to
    SQLite so that a cold-start restart can restore trajectory state.

    Reference: NEXUS_UNIVERSAL_OS.md Domain 2.9 | GAIAN_LAWS.md Law VI
    """

    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()
        self._trajectory = TrajectoryModel()
        self._last_snapshot: Optional[CrisisSnapshot] = None
        self._conn: Optional[sqlite3.Connection] = None

        if self.config.db_path is not None:
            self._init_db(self.config.db_path)
            self._restore_from_db()

        logger.info("CrisisEngine initialised principal=%s", self.config.principal_id)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        text: str = "",
        session_id: str = "",
        # SafetyEngine calls evaluate(user_text=..., turn_index=...)
        user_text: Optional[str] = None,
        turn_index: int = 0,
    ) -> CrisisSnapshot:
        """
        Evaluate a single conversation turn and return the synthesised
        CrisisSnapshot.

        Accepts both positional ``text`` (test_crisis_engine.py) and
        keyword ``user_text`` (SafetyEngine) for the turn content.
        """
        content = user_text if user_text is not None else text
        signals = classify_turn(content)
        risk = self._trajectory.synthesise_risk(signals)

        slope = self._trajectory.trajectory_slope()
        consecutive = self._trajectory.consecutive_distress_sessions()
        peak_72h = self._trajectory.peak_risk_within(72)   # correct method name

        tier = determine_escalation_tier(
            _make_snapshot(
                principal_id=self.config.principal_id,
                risk=risk,
                slope=slope,
                consecutive=consecutive,
                peak_72h=peak_72h,
            )
        )

        snapshot = _make_snapshot(
            principal_id=self.config.principal_id,
            risk=risk,
            tier=tier,
            slope=slope,
            consecutive=consecutive,
            peak_72h=peak_72h,
            active_signals=signals,
        )
        self._last_snapshot = snapshot
        logger.info(
            "evaluate principal=%s risk=%s tier=%s",
            self.config.principal_id, risk.value, tier.value,
        )
        return snapshot

    def close_session(
        self,
        session_id: str = "",
        # Primary field names matching SessionRiskRecord + SafetyEngine
        peak_risk: RiskLevel = RiskLevel.NONE,
        signal_count: int = 0,
        has_explicit: bool = False,
        has_masked: bool = False,
        # Aliases used by test_crisis_engine.py direct calls
        risk_level: Optional[RiskLevel] = None,
        explicit_signal: Optional[bool] = None,
        in_distress: Optional[bool] = None,
    ) -> None:
        """
        Record a completed session's risk summary into the trajectory model
        and persist it to the database.

        Accepts both the SafetyEngine naming (peak_risk, has_explicit,
        has_masked) and the test_crisis_engine.py direct naming
        (risk_level, explicit_signal, in_distress) as aliases.
        """
        effective_risk    = risk_level    if risk_level    is not None else peak_risk
        effective_explicit= explicit_signal if explicit_signal is not None else has_explicit
        effective_masked  = in_distress   if in_distress   is not None else has_masked

        record = SessionRiskRecord(
            session_id   = session_id,
            peak_risk    = effective_risk,
            signal_count = signal_count,
            has_explicit = effective_explicit,
            has_masked   = effective_masked,
        )
        self._trajectory.record_session(record)
        self._persist_session(record)
        logger.info(
            "close_session principal=%s session=%s risk=%s",
            self.config.principal_id, session_id, effective_risk.value,
        )

    def get_intervention_message(self) -> str:
        """Return the intervention message for the current escalation tier."""
        if self._last_snapshot is None:
            return ""
        return get_intervention_message(self._last_snapshot.escalation_tier)

    def build_handoff(self) -> Optional[HandoffRecord]:
        """Build a HandoffRecord if the current tier is HANDOFF, else return None."""
        if self._last_snapshot is None:
            return None
        if self._last_snapshot.escalation_tier != EscalationTier.HANDOFF:
            return None
        return build_handoff_record(self._last_snapshot)

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _init_db(self, db_path: Path) -> None:
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS session_records (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                principal_id    TEXT NOT NULL,
                session_id      TEXT NOT NULL,
                peak_risk       TEXT NOT NULL,
                signal_count    INTEGER NOT NULL,
                has_explicit    INTEGER NOT NULL,
                has_masked      INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_sr_principal
                ON session_records(principal_id);
        """)
        self._conn.commit()

    def _restore_from_db(self) -> None:
        """Re-hydrate trajectory from persisted session records."""
        if self._conn is None:
            return
        rows = self._conn.execute(
            "SELECT session_id, peak_risk, signal_count, has_explicit, has_masked "
            "FROM session_records WHERE principal_id = ? ORDER BY id ASC",
            (self.config.principal_id,),
        ).fetchall()
        for row in rows:
            session_id, peak_risk_str, signal_count, has_explicit_int, has_masked_int = row
            record = SessionRiskRecord(
                session_id   = session_id,
                peak_risk    = RiskLevel(peak_risk_str),
                signal_count = signal_count,
                has_explicit = bool(has_explicit_int),
                has_masked   = bool(has_masked_int),
            )
            self._trajectory.record_session(record)
        logger.info(
            "CrisisEngine restored %d session records for principal=%s",
            len(rows), self.config.principal_id,
        )

    def _persist_session(self, record: SessionRiskRecord) -> None:
        if self._conn is None:
            return
        self._conn.execute(
            "INSERT INTO session_records "
            "(principal_id, session_id, peak_risk, signal_count, has_explicit, has_masked) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                self.config.principal_id,
                record.session_id,
                record.peak_risk.value,
                record.signal_count,
                int(record.has_explicit),
                int(record.has_masked),
            ),
        )
        self._conn.commit()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _make_snapshot(
    principal_id: str,
    risk: RiskLevel,
    tier: Optional[EscalationTier] = None,
    slope: float = 0.0,
    consecutive: int = 0,
    peak_72h: Optional[RiskLevel] = None,
    active_signals: list = None,
) -> CrisisSnapshot:
    return CrisisSnapshot(
        principal_id=principal_id,
        current_risk=risk,
        escalation_tier=tier or EscalationTier.MONITOR,
        trajectory_slope=slope,
        sessions_in_distress=consecutive,
        peak_risk_72h=peak_72h or RiskLevel.NONE,
        active_signals=active_signals or [],
    )

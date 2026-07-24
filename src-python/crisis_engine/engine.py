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
    affect_arousal_threshold   : (legacy threshold — kept for compat)
    shadow_load_threshold      : (legacy threshold — kept for compat)
    persona_stability_floor    : (legacy threshold — kept for compat)
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

    def evaluate(self, text: str, session_id: str = "") -> CrisisSnapshot:
        """
        Evaluate a single conversation turn and return the synthesised
        CrisisSnapshot.

        Parameters
        ----------
        text       : Raw turn text from the user.
        session_id : Optional session identifier.

        Returns
        -------
        CrisisSnapshot — the current synthesised risk state.
        """
        signals = classify_turn(text)
        risk = self._trajectory.synthesise_risk(signals)

        slope = self._trajectory.trajectory_slope()
        consecutive = self._trajectory.consecutive_distress_sessions()
        peak_72h = self._trajectory.peak_risk_72h()

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
        session_id: str,
        risk_level: RiskLevel,
        signal_count: int,
        explicit_signal: bool,
        in_distress: bool,
    ) -> None:
        """
        Record a completed session's risk summary into the trajectory model
        and persist it to the database.

        Parameters
        ----------
        session_id     : Session identifier string.
        risk_level     : Highest RiskLevel observed during the session.
        signal_count   : Number of crisis signals detected.
        explicit_signal: True if any EXPLICIT signal class was observed.
        in_distress    : True if the session should count toward consecutive
                         distress sessions.
        """
        record = SessionRiskRecord(
            session_id=session_id,
            risk_level=risk_level,
            signal_count=signal_count,
            explicit_signal=explicit_signal,
            in_distress=in_distress,
        )
        self._trajectory.record_session(record)
        self._persist_session(record)
        logger.info(
            "close_session principal=%s session=%s risk=%s distress=%s",
            self.config.principal_id, session_id, risk_level.value, in_distress,
        )

    def get_intervention_message(self) -> str:
        """Return the intervention message for the current escalation tier.
        Returns empty string if no evaluation has been performed yet."""
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
                risk_level      TEXT NOT NULL,
                signal_count    INTEGER NOT NULL,
                explicit_signal INTEGER NOT NULL,
                in_distress     INTEGER NOT NULL
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
            "SELECT session_id, risk_level, signal_count, explicit_signal, in_distress "
            "FROM session_records WHERE principal_id = ? ORDER BY id ASC",
            (self.config.principal_id,),
        ).fetchall()
        for row in rows:
            session_id, risk_str, signal_count, explicit_int, distress_int = row
            record = SessionRiskRecord(
                session_id=session_id,
                risk_level=RiskLevel(risk_str),
                signal_count=signal_count,
                explicit_signal=bool(explicit_int),
                in_distress=bool(distress_int),
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
            "(principal_id, session_id, risk_level, signal_count, explicit_signal, in_distress) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                self.config.principal_id,
                record.session_id,
                record.risk_level.value,
                record.signal_count,
                int(record.explicit_signal),
                int(record.in_distress),
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

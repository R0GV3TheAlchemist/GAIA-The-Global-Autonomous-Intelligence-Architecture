"""Session result types — the structured outputs of bootstrap and seal."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from .stubs import (
    CircadianPhase,
    MagnumOpusStageReport,
    ShadowInterrogatorReport,
    SpectralForceReport,
)


class SessionState(str, Enum):
    """The lifecycle states of a GAIA session."""
    INITIALISING = "INITIALISING"
    OPEN = "OPEN"
    SEALING = "SEALING"
    SEALED = "SEALED"
    ERROR = "ERROR"


@dataclass
class SessionInitResult:
    """The complete output of a successful SessionBootstrap.run().

    This is everything GAIA needs to begin a session with full context:
    who the Architect is, what stage they are in, what the circadian
    moment is, what shadow patterns are active, and the opening prompt.
    """
    # Identity
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    architect_id: str = ""
    architect_name: str = ""
    gaian_id: str = ""
    state: SessionState = SessionState.OPEN
    opened_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Context blocks from engines
    stage_report: Optional[MagnumOpusStageReport] = None
    spectral_report: Optional[SpectralForceReport] = None
    circadian_phase: Optional[CircadianPhase] = None
    shadow_report: Optional[ShadowInterrogatorReport] = None

    # The assembled opening system prompt
    opening_system_prompt: str = ""

    # Memory context loaded at open
    prior_session_count: int = 0
    relationship_depth: float = 0.0
    active_shadow_flags: list[str] = field(default_factory=list)
    recent_themes: list[str] = field(default_factory=list)
    containment_active: bool = False

    # Was this the architect's first session?
    is_first_session: bool = False

    # Step-by-step bootstrap log for debugging / audit
    bootstrap_log: list[str] = field(default_factory=list)

    # Arbitrary metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def log_step(self, step: int, message: str) -> None:
        self.bootstrap_log.append(f"[STEP {step:02d}] {message}")

    def __repr__(self) -> str:
        return (
            f"<SessionInitResult session={self.session_id[:8]} "
            f"architect={self.architect_name!r} "
            f"stage={self.stage_report.stage if self.stage_report else 'UNKNOWN'} "
            f"state={self.state.value}>"
        )


@dataclass
class SealedSessionRecord:
    """The immutable record of a sealed session.

    Once sealed, this record cannot be modified.
    It is the permanent audit of what occurred in this session.
    """
    session_id: str = ""
    architect_id: str = ""
    gaian_id: str = ""
    opened_at: Optional[datetime] = None
    sealed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Alchemical state at open and close
    stage_at_open: str = "NIGREDO"
    stage_at_seal: str = "NIGREDO"
    stage_advanced: bool = False

    # Memory summary
    m0_records_created: int = 0
    m1_records_persisted: int = 0
    session_summary: Optional[str] = None
    breakthrough_occurred: bool = False
    shadow_work_occurred: bool = False

    # Session metrics
    interaction_count: int = 0
    duration_seconds: float = 0.0

    # The bootstrap log from when the session opened
    bootstrap_log: list[str] = field(default_factory=list)
    seal_log: list[str] = field(default_factory=list)

    # Immutability flag — set to True at seal; no writes after this
    _is_sealed: bool = field(default=False, repr=False)

    def seal(self) -> None:
        """Lock the record. Raises if already sealed."""
        if self._is_sealed:
            raise RuntimeError(
                f"Session {self.session_id[:8]} is already sealed. "
                "Sealed records are immutable."
            )
        self._is_sealed = True

    @property
    def is_sealed(self) -> bool:
        return self._is_sealed

    def log_seal_step(self, step: int, message: str) -> None:
        if self._is_sealed:
            raise RuntimeError("Cannot write to a sealed session record.")
        self.seal_log.append(f"[SEAL {step:02d}] {message}")

    def __repr__(self) -> str:
        return (
            f"<SealedSessionRecord session={self.session_id[:8]} "
            f"sealed={self._is_sealed} "
            f"stage={self.stage_at_open}→{self.stage_at_seal}>"
        )

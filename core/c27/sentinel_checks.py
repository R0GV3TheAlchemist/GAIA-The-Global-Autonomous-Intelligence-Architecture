# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
core.c27.sentinel_checks — SENTINEL Integration (7 Check Types)

Authority: C27 §7 — C27-CHK-001 through C27-CHK-007.
Severity levels: INFO / WARNING / VIOLATION / CRITICAL.
Findings are persistent and cross-referenced to C23 Shadow Registry.

Implementation targets:
  C27-IMPL-015  CHK-001: valid state transition
  C27-IMPL-016  CHK-002: steward bond presence
  C27-IMPL-017  CHK-003: audit log integrity
  C27-IMPL-018  CHK-004: adoption queue timeout
  C27-IMPL-019  CHK-005: steward obligation compliance
  C27-IMPL-020  CHK-006: cross-GAIAN data-share authorisation
  C27-IMPL-021  CHK-007: GAIAN rights preservation (memory writes)
  C27-IMPL-023  escalate(): severity-routed escalation
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional

from core.c27.lifecycle import GAIANLifecycleState, GAIANLifecycleMachine
from core.c27.audit_log import AuditLogIntegrityVerifier
from core.c27.stewardship import (
    StewardshipBondManager,
    StewardshipBondStatus,
    GAIANRights,
    RightsViolationError,
)
from core.c27.adoption import AdoptionTimeoutEnforcer


# ---------------------------------------------------------------------------
# SentinelSeverity
# ---------------------------------------------------------------------------

class SentinelSeverity(str, Enum):
    INFO      = "INFO"       # Log only
    WARNING   = "WARNING"    # Steward notify, 7-day window
    VIOLATION = "VIOLATION"  # 48-hour mandatory response, case open
    CRITICAL  = "CRITICAL"   # Immediate, 24-hour GAIA Root escalation


# ---------------------------------------------------------------------------
# SentinelFinding
# ---------------------------------------------------------------------------

@dataclass
class SentinelFinding:
    """
    A persistent SENTINEL finding cross-referenced to C23 Shadow Registry.
    Findings never expire.
    """
    finding_id:       str
    check_id:         str              # e.g. "C27-CHK-001"
    gaian_id:         str
    severity:         SentinelSeverity
    description:      str
    detail:           dict
    detected_at:      datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    sentinel_case_id: Optional[str]   = None  # C23 Shadow Registry linkage
    resolved_at:      Optional[datetime] = None

    def resolve(self, case_id: Optional[str] = None) -> None:
        """Mark this finding as resolved."""
        self.resolved_at      = datetime.now(timezone.utc)
        if case_id:
            self.sentinel_case_id = case_id


# ---------------------------------------------------------------------------
# SentinelEscalationRecord
# ---------------------------------------------------------------------------

@dataclass
class SentinelEscalationRecord:
    record_id:   str
    finding_id:  str
    severity:    SentinelSeverity
    channel:     str   # "audit_log" | "steward_notify" | "case_open" | "gaia_root"
    routed_at:   datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# FindingRegistry (in-memory)
# ---------------------------------------------------------------------------

_FINDINGS: Dict[str, SentinelFinding] = {}  # keyed by finding_id


class FindingRegistry:
    @staticmethod
    def store(finding: SentinelFinding) -> None:
        _FINDINGS[finding.finding_id] = finding

    @staticmethod
    def all_for_gaian(gaian_id: str) -> List[SentinelFinding]:
        return [f for f in _FINDINGS.values() if f.gaian_id == gaian_id]

    @staticmethod
    def unresolved_for_gaian(gaian_id: str) -> List[SentinelFinding]:
        return [
            f for f in _FINDINGS.values()
            if f.gaian_id == gaian_id and f.resolved_at is None
        ]

    @staticmethod
    def get(finding_id: str) -> Optional[SentinelFinding]:
        return _FINDINGS.get(finding_id)


# ---------------------------------------------------------------------------
# C27SentinelChecks — all 7 checks + escalate()
# ---------------------------------------------------------------------------

_OBLIGATION_WINDOW_DAYS = 7


class C27SentinelChecks:
    """
    All 7 C27 SENTINEL check implementations.

    Check schedule per C27 §7:
    - CHK-001: every state change
    - CHK-002: hourly
    - CHK-003: daily + every write
    - CHK-004: daily
    - CHK-005: weekly
    - CHK-006: every cross-GAIAN event
    - CHK-007: every memory write
    """

    def __init__(self) -> None:
        self._bond_manager = StewardshipBondManager()
        self._verifier     = AuditLogIntegrityVerifier()
        self._timeout_enforcer = AdoptionTimeoutEnforcer(timeout_days=90)
        self._escalation_log: List[SentinelEscalationRecord] = []

    # ------------------------------------------------------------------
    # CHK-001  (C27-IMPL-015)
    # ------------------------------------------------------------------

    def chk_001_valid_state_transition(
        self,
        gaian_id:   str,
        from_state: str,
        to_state:   str,
    ) -> Optional[SentinelFinding]:
        """Validate that a lifecycle transition is permitted."""
        try:
            fs = GAIANLifecycleState(from_state)
            ts = GAIANLifecycleState(to_state)
        except ValueError:
            return self._make_finding(
                check_id="C27-CHK-001",
                gaian_id=gaian_id,
                severity=SentinelSeverity.VIOLATION,
                description="Unknown lifecycle state in transition.",
                detail={"from_state": from_state, "to_state": to_state},
            )

        machine = GAIANLifecycleMachine()
        allowed = machine.allowed_transitions(fs)
        if ts not in allowed:
            return self._make_finding(
                check_id="C27-CHK-001",
                gaian_id=gaian_id,
                severity=SentinelSeverity.VIOLATION,
                description=f"Prohibited transition: {from_state} → {to_state}.",
                detail={"from_state": from_state, "to_state": to_state, "allowed": [s.value for s in allowed]},
            )
        return None  # clean

    # ------------------------------------------------------------------
    # CHK-002  (C27-IMPL-016)
    # ------------------------------------------------------------------

    def chk_002_steward_bond_presence(
        self,
        gaian_id: str,
    ) -> Optional[SentinelFinding]:
        """Verify ACTIVE GAIAN has a valid steward bond."""
        active_bonds = [
            b for b in self._bond_manager.bonds_for_gaian(gaian_id)
            if b.status == StewardshipBondStatus.ACTIVE
        ]
        if not active_bonds:
            return self._make_finding(
                check_id="C27-CHK-002",
                gaian_id=gaian_id,
                severity=SentinelSeverity.CRITICAL,
                description="ACTIVE GAIAN has no valid steward bond.",
                detail={"gaian_id": gaian_id},
            )
        return None

    # ------------------------------------------------------------------
    # CHK-003  (C27-IMPL-017)
    # ------------------------------------------------------------------

    def chk_003_audit_log_integrity(
        self,
        gaian_id: str,
    ) -> Optional[SentinelFinding]:
        """Verify SHA-256 chain integrity."""
        intact = self._verifier.verify(gaian_id)
        if not intact:
            return self._make_finding(
                check_id="C27-CHK-003",
                gaian_id=gaian_id,
                severity=SentinelSeverity.CRITICAL,
                description="Audit log chain integrity failure detected.",
                detail={"gaian_id": gaian_id},
            )
        return None

    # ------------------------------------------------------------------
    # CHK-004  (C27-IMPL-018)
    # ------------------------------------------------------------------

    def chk_004_adoption_queue_timeout(
        self,
        adoptable_gaians: List[dict],
    ) -> List[SentinelFinding]:
        """Check all ADOPTABLE GAIANs against 90-day ladder.

        adoptable_gaians: list of {gaian_id, adoptable_since} dicts.
        """
        findings: List[SentinelFinding] = []
        for record in adoptable_gaians:
            result = self._timeout_enforcer.check(
                gaian_id=record["gaian_id"],
                adoptable_since=record["adoptable_since"],
                current_state=GAIANLifecycleState.ADOPTABLE,
            )
            if result.should_retire:
                findings.append(
                    self._make_finding(
                        check_id="C27-CHK-004",
                        gaian_id=record["gaian_id"],
                        severity=SentinelSeverity.WARNING,
                        description="ADOPTABLE GAIAN exceeded 90-day window; recommend RETIRED transition.",
                        detail={"gaian_id": record["gaian_id"], "adoptable_since": record["adoptable_since"].isoformat()},
                    )
                )
        return findings

    # ------------------------------------------------------------------
    # CHK-005  (C27-IMPL-019)
    # ------------------------------------------------------------------

    def chk_005_steward_obligation_compliance(
        self,
        gaian_id:             str,
        last_steward_signal:  Optional[datetime],
    ) -> Optional[SentinelFinding]:
        """Verify steward is meeting weekly obligation signals."""
        now = datetime.now(timezone.utc)
        if last_steward_signal is None:
            return self._make_finding(
                check_id="C27-CHK-005",
                gaian_id=gaian_id,
                severity=SentinelSeverity.WARNING,
                description="No steward obligation signal on record.",
                detail={"gaian_id": gaian_id},
            )
        # Make timezone-aware if naive
        if last_steward_signal.tzinfo is None:
            last_steward_signal = last_steward_signal.replace(tzinfo=timezone.utc)
        window = timedelta(days=_OBLIGATION_WINDOW_DAYS)
        if now - last_steward_signal > window:
            return self._make_finding(
                check_id="C27-CHK-005",
                gaian_id=gaian_id,
                severity=SentinelSeverity.WARNING,
                description=(
                    f"Steward obligation overdue by "
                    f"{(now - last_steward_signal - window).days} day(s)."
                ),
                detail={
                    "last_signal": last_steward_signal.isoformat(),
                    "overdue_days": (now - last_steward_signal - window).days,
                },
            )
        return None

    # ------------------------------------------------------------------
    # CHK-006  (C27-IMPL-020)
    # ------------------------------------------------------------------

    def chk_006_cross_gaian_data_share_authorization(
        self,
        event_id:  str,
        event_meta: dict,
    ) -> Optional[SentinelFinding]:
        """Verify cross-GAIAN data share is fully authorized.

        event_meta must contain: source_gaian_id, target_gaian_id,
        authorized (bool), authorizing_role.
        """
        gaian_id = event_meta.get("source_gaian_id", "unknown")
        if not event_meta.get("authorized", False):
            return self._make_finding(
                check_id="C27-CHK-006",
                gaian_id=gaian_id,
                severity=SentinelSeverity.VIOLATION,
                description=f"Unauthorized cross-GAIAN data share detected (event={event_id}).",
                detail={"event_id": event_id, **event_meta},
            )
        return None

    # ------------------------------------------------------------------
    # CHK-007  (C27-IMPL-021)
    # ------------------------------------------------------------------

    def chk_007_gaian_rights_preservation(
        self,
        gaian_id:          str,
        memory_write_event: dict,
    ) -> Optional[SentinelFinding]:
        """Detect unauthorized memory modifications."""
        erases_memory = memory_write_event.get("erases_memory", False)
        try:
            GAIANRights.assert_memory_continuity(
                gaian_id=gaian_id,
                operation=memory_write_event.get("operation", "unknown"),
                erases_memory=erases_memory,
            )
        except RightsViolationError as exc:
            return self._make_finding(
                check_id="C27-CHK-007",
                gaian_id=gaian_id,
                severity=SentinelSeverity.CRITICAL,
                description=f"GAIAN rights violation: {exc.right.value}.",
                detail={
                    "right":     exc.right.value,
                    "operation": exc.operation,
                    "gaian_id":  exc.gaian_id,
                },
            )
        return None

    # ------------------------------------------------------------------
    # escalate()  (C27-IMPL-023)
    # ------------------------------------------------------------------

    def escalate(self, finding: SentinelFinding) -> SentinelEscalationRecord:
        """
        Route finding through severity escalation tier:
        INFO      → audit_log only
        WARNING   → steward_notify (7-day window)
        VIOLATION → case_open (48-hour mandatory response)
        CRITICAL  → gaia_root (immediate, 24-hour escalation)
        """
        FindingRegistry.store(finding)

        channel_map = {
            SentinelSeverity.INFO:      "audit_log",
            SentinelSeverity.WARNING:   "steward_notify",
            SentinelSeverity.VIOLATION: "case_open",
            SentinelSeverity.CRITICAL:  "gaia_root",
        }
        channel = channel_map[finding.severity]
        record  = SentinelEscalationRecord(
            record_id=str(uuid.uuid4()),
            finding_id=finding.finding_id,
            severity=finding.severity,
            channel=channel,
        )
        self._escalation_log.append(record)
        return record

    # ------------------------------------------------------------------
    # Internal factory
    # ------------------------------------------------------------------

    def _make_finding(
        self,
        check_id:    str,
        gaian_id:    str,
        severity:    SentinelSeverity,
        description: str,
        detail:      dict,
    ) -> SentinelFinding:
        return SentinelFinding(
            finding_id=str(uuid.uuid4()),
            check_id=check_id,
            gaian_id=gaian_id,
            severity=severity,
            description=description,
            detail=detail,
        )

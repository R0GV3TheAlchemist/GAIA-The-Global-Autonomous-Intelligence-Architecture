"""
core/lifecycle/compliance_sentinel.py
C27 §7 — Automated Compliance Sentinel Integration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from .gaian_lifecycle_state import GAIANLifecycleState, VALID_TRANSITIONS


class SentinelSeverity(str, Enum):
    INFO = "I"
    WARNING = "W"
    VIOLATION = "V"
    CRITICAL = "CR"


class SentinelCheckID(str, Enum):
    C27_CHK_001 = "C27-CHK-001"
    C27_CHK_002 = "C27-CHK-002"
    C27_CHK_003 = "C27-CHK-003"
    C27_CHK_004 = "C27-CHK-004"
    C27_CHK_005 = "C27-CHK-005"
    C27_CHK_006 = "C27-CHK-006"
    C27_CHK_007 = "C27-CHK-007"


@dataclass
class SentinelFinding:
    case_id: str
    gaian_id: str
    check_id: SentinelCheckID
    severity: SentinelSeverity
    message: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    def resolve(self) -> None:
        self.resolved = True
        self.resolved_at = datetime.now(timezone.utc)


class ComplianceSentinel:
    """Phase 2 in-memory SENTINEL evaluator for C27 compliance checks."""

    def __init__(self) -> None:
        self._findings: Dict[str, List[SentinelFinding]] = {}
        self._counter = 0

    def _new_case_id(self) -> str:
        self._counter += 1
        return f"SNTL-C27-{self._counter:06d}"

    def _record(self, gaian_id: str, check_id: SentinelCheckID, severity: SentinelSeverity, message: str) -> SentinelFinding:
        finding = SentinelFinding(
            case_id=self._new_case_id(),
            gaian_id=gaian_id,
            check_id=check_id,
            severity=severity,
            message=message,
        )
        self._findings.setdefault(gaian_id, []).append(finding)
        return finding

    def check_transition(self, gaian_id: str, from_state: GAIANLifecycleState, to_state: GAIANLifecycleState) -> Optional[SentinelFinding]:
        if to_state not in VALID_TRANSITIONS.get(from_state, frozenset()) and not (from_state == GAIANLifecycleState.RETIRED and to_state == GAIANLifecycleState.ARCHIVED):
            return self._record(
                gaian_id,
                SentinelCheckID.C27_CHK_001,
                SentinelSeverity.CRITICAL,
                f"Prohibited lifecycle transition attempted: {from_state.value} -> {to_state.value}",
            )
        return None

    def check_steward_bond_present(self, gaian_id: str, state: GAIANLifecycleState, has_primary_bond: bool) -> Optional[SentinelFinding]:
        exempt = {GAIANLifecycleState.LATENT, GAIANLifecycleState.ADOPTABLE, GAIANLifecycleState.RETIRED, GAIANLifecycleState.ARCHIVED}
        if state not in exempt and not has_primary_bond:
            return self._record(
                gaian_id,
                SentinelCheckID.C27_CHK_002,
                SentinelSeverity.VIOLATION,
                f"GAIAN in state {state.value} lacks required PRIMARY stewardship bond",
            )
        return None

    def check_audit_log_integrity(self, gaian_id: str, is_valid: bool) -> Optional[SentinelFinding]:
        if not is_valid:
            return self._record(
                gaian_id,
                SentinelCheckID.C27_CHK_003,
                SentinelSeverity.CRITICAL,
                "Lifecycle audit log integrity failure detected",
            )
        return None

    def check_adoption_timeout(self, gaian_id: str, days_in_queue: int) -> Optional[SentinelFinding]:
        if days_in_queue >= 91:
            return self._record(
                gaian_id,
                SentinelCheckID.C27_CHK_004,
                SentinelSeverity.VIOLATION,
                f"GAIAN has exceeded adoption timeout window: {days_in_queue} days in ADOPTABLE",
            )
        if days_in_queue >= 31:
            return self._record(
                gaian_id,
                SentinelCheckID.C27_CHK_004,
                SentinelSeverity.WARNING,
                f"GAIAN adoption queue aging signal: {days_in_queue} days in ADOPTABLE",
            )
        return None

    def get_findings(self, gaian_id: str) -> List[SentinelFinding]:
        return list(self._findings.get(gaian_id, []))

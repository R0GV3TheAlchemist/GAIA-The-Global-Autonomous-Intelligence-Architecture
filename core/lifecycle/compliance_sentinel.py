"""
core/lifecycle/compliance_sentinel.py
C27 §7 — Compliance SENTINEL

Checks:
  CHK-001  Invalid lifecycle transition attempted
  CHK-002  Primary steward bond absent at sensitive states
  CHK-003  Audit log integrity failure (HMAC chain broken)
  CHK-004  Adoption timeout escalation
  CHK-005  Permission over-grant after state contraction
  CHK-006  DATA_SHARE event without active THIRD_PARTY_SHARE consent  [Phase 3]
  CHK-007  MEMORY_WRITE event by non-primary-steward or missing consent [Phase 3]
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from .gaian_lifecycle_state import GAIANLifecycleState, LifecycleTransitionError


try:
    from core.consent_ledger import ConsentLedger, ConsentScope, get_consent_ledger
    _CONSENT_AVAILABLE = True
except ImportError:
    _CONSENT_AVAILABLE = False
    ConsentLedger = None  # type: ignore[assignment,misc]
    ConsentScope   = None  # type: ignore[assignment,misc]
    get_consent_ledger = None  # type: ignore[assignment]


class SentinelSeverity(str, Enum):
    INFORMATIONAL = "INFORMATIONAL"  # I
    WARNING       = "WARNING"        # W
    VIOLATION     = "VIOLATION"      # V
    CRITICAL      = "CRITICAL"       # CR


class SentinelCheckID(str, Enum):
    CHK_001 = "CHK-001"   # invalid transition
    CHK_002 = "CHK-002"   # missing primary bond
    CHK_003 = "CHK-003"   # audit integrity failure
    CHK_004 = "CHK-004"   # adoption timeout
    CHK_005 = "CHK-005"   # permission over-grant
    CHK_006 = "CHK-006"   # data share without consent
    CHK_007 = "CHK-007"   # memory write unauthorised


@dataclass
class SentinelFinding:
    case_id:   str = field(default_factory=lambda: str(uuid.uuid4()))
    gaian_id:  str = ""
    check_id:  SentinelCheckID = SentinelCheckID.CHK_001
    severity:  SentinelSeverity = SentinelSeverity.INFORMATIONAL
    message:   str = ""
    resolved:  bool = False


_BOND_REQUIRED_STATES = {
    GAIANLifecycleState.BORN,
    GAIANLifecycleState.ACTIVE,
    GAIANLifecycleState.DORMANT,
}

_SENSITIVE_TRANSITIONS = {
    (GAIANLifecycleState.ACTIVE,    GAIANLifecycleState.RETIRED),
    (GAIANLifecycleState.ADOPTABLE, GAIANLifecycleState.RETIRED),
    (GAIANLifecycleState.RETIRED,   GAIANLifecycleState.ARCHIVED),
}


class ComplianceSentinel:
    """
    C27 §7 SENTINEL — raises findings on lifecycle policy violations.

    CHK-006 and CHK-007 require a ConsentLedger instance.
    If none is supplied, the module-level singleton from
    ``core.consent_ledger.get_consent_ledger()`` is used.
    """

    def __init__(
        self,
        raise_on_critical: bool = True,
        consent_ledger: Optional["ConsentLedger"] = None,
    ) -> None:
        self._raise_on_critical = raise_on_critical
        self._findings: Dict[str, List[SentinelFinding]] = {}
        if consent_ledger is not None:
            self._consent_ledger: Optional["ConsentLedger"] = consent_ledger
        elif _CONSENT_AVAILABLE:
            self._consent_ledger = get_consent_ledger()
        else:
            self._consent_ledger = None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _record(self, finding: SentinelFinding) -> SentinelFinding:
        self._findings.setdefault(finding.gaian_id, []).append(finding)
        if self._raise_on_critical and finding.severity == SentinelSeverity.CRITICAL:
            raise LifecycleTransitionError(
                gaian_id=finding.gaian_id,
                from_state=None,
                to_state=None,
                reason=f"[SENTINEL {finding.check_id.value}] {finding.message}",
            )
        return finding

    def get_findings(self, gaian_id: str) -> List[SentinelFinding]:
        return list(self._findings.get(gaian_id, []))

    # ------------------------------------------------------------------
    # CHK-001  Illegal transition
    # ------------------------------------------------------------------

    def check_transition(
        self,
        gaian_id:   str,
        from_state: GAIANLifecycleState,
        to_state:   GAIANLifecycleState,
    ) -> None:
        if (from_state, to_state) in _SENSITIVE_TRANSITIONS:
            self._record(SentinelFinding(
                gaian_id=gaian_id,
                check_id=SentinelCheckID.CHK_001,
                severity=SentinelSeverity.INFORMATIONAL,
                message=f"Sensitive transition {from_state.value} → {to_state.value} observed.",
            ))

    # ------------------------------------------------------------------
    # CHK-002  Missing primary bond
    # ------------------------------------------------------------------

    def check_steward_bond_present(
        self,
        gaian_id:          str,
        to_state:          GAIANLifecycleState,
        has_primary_bond:  bool,
    ) -> None:
        if to_state in _BOND_REQUIRED_STATES and not has_primary_bond:
            self._record(SentinelFinding(
                gaian_id=gaian_id,
                check_id=SentinelCheckID.CHK_002,
                severity=SentinelSeverity.VIOLATION,
                message=(
                    f"No primary steward bond present after transition "
                    f"to {to_state.value}. C27 §3.1 requires a primary bond "
                    f"in BORN / ACTIVE / DORMANT states."
                ),
            ))

    # ------------------------------------------------------------------
    # CHK-003  Audit log integrity
    # ------------------------------------------------------------------

    def check_audit_log_integrity(self, gaian_id: str, chain_valid: bool) -> None:
        if not chain_valid:
            self._record(SentinelFinding(
                gaian_id=gaian_id,
                check_id=SentinelCheckID.CHK_003,
                severity=SentinelSeverity.CRITICAL,
                message="Audit log HMAC chain integrity failure detected.",
            ))

    # ------------------------------------------------------------------
    # CHK-004  Adoption timeout
    # ------------------------------------------------------------------

    def check_adoption_timeout(self, gaian_id: str, days_in_queue: int) -> None:
        if days_in_queue >= 90:
            severity = SentinelSeverity.CRITICAL
            msg = f"GAIAN has been ADOPTABLE for {days_in_queue} days — council review required."
        elif days_in_queue >= 75:
            severity = SentinelSeverity.VIOLATION
            msg = f"GAIAN has been ADOPTABLE for {days_in_queue} days — escalated matching required."
        elif days_in_queue >= 45:
            severity = SentinelSeverity.WARNING
            msg = f"GAIAN has been ADOPTABLE for {days_in_queue} days — standard matching escalation."
        else:
            return
        self._record(SentinelFinding(
            gaian_id=gaian_id,
            check_id=SentinelCheckID.CHK_004,
            severity=severity,
            message=msg,
        ))

    # ------------------------------------------------------------------
    # CHK-005  Permission over-grant
    # ------------------------------------------------------------------

    def check_permission_contraction(
        self,
        gaian_id:           str,
        state:              GAIANLifecycleState,
        unexpected_perms:   List[str],
    ) -> None:
        if unexpected_perms:
            self._record(SentinelFinding(
                gaian_id=gaian_id,
                check_id=SentinelCheckID.CHK_005,
                severity=SentinelSeverity.VIOLATION,
                message=(
                    f"Permission over-grant in {state.value}: unexpected capabilities "
                    f"{unexpected_perms} remain active after contraction."
                ),
            ))

    # ------------------------------------------------------------------
    # CHK-006  DATA_SHARE without THIRD_PARTY_SHARE consent  [Phase 3]
    # ------------------------------------------------------------------

    def check_data_share_consent(
        self,
        gaian_id:       str,
        target_gaian:   Optional[str] = None,
        ledger_ref:     Optional[str] = None,
    ) -> None:
        """
        Raises CRITICAL finding if the GAIAN has not granted
        THIRD_PARTY_SHARE consent in the ConsentLedger (C27 CHK-006).

        Parameters
        ----------
        gaian_id :
            The GAIAN whose data is being shared.
        target_gaian :
            Optional receiving GAIAN / external entity identifier.
        ledger_ref :
            Optional reference token from the consent ledger entry
            (for audit trail correlation).
        """
        if self._consent_ledger is None:
            self._record(SentinelFinding(
                gaian_id=gaian_id,
                check_id=SentinelCheckID.CHK_006,
                severity=SentinelSeverity.VIOLATION,
                message="ConsentLedger unavailable — DATA_SHARE consent cannot be verified.",
            ))
            return

        permitted = self._consent_ledger.is_permitted(
            gaian_id=gaian_id,
            scope=ConsentScope.THIRD_PARTY_SHARE,
        )
        if not permitted:
            self._record(SentinelFinding(
                gaian_id=gaian_id,
                check_id=SentinelCheckID.CHK_006,
                severity=SentinelSeverity.CRITICAL,
                message=(
                    f"DATA_SHARE event blocked: GAIAN '{gaian_id}' has not granted "
                    f"THIRD_PARTY_SHARE consent"
                    + (f" (target: {target_gaian})" if target_gaian else "")
                    + ". C27 CHK-006."
                ),
            ))

    # ------------------------------------------------------------------
    # CHK-007  MEMORY_WRITE without consent or non-primary actor [Phase 3]
    # ------------------------------------------------------------------

    def check_memory_write_authorization(
        self,
        gaian_id:         str,
        actor_id:         Optional[str],
        primary_steward_id: Optional[str],
        council_override: bool = False,
    ) -> None:
        """
        Raises CRITICAL finding if a MEMORY_WRITE event is attempted
        without both:
          a) Active MEMORY_WRITE consent in the ConsentLedger, AND
          b) The actor being the primary steward OR a council override

        C27 CHK-007 / C17 memory write authorization.
        """
        if council_override:
            return

        # Check consent
        consent_ok = False
        if self._consent_ledger is not None:
            consent_ok = self._consent_ledger.is_permitted(
                gaian_id=gaian_id,
                scope=ConsentScope.MEMORY_WRITE,
            )
        if not consent_ok:
            self._record(SentinelFinding(
                gaian_id=gaian_id,
                check_id=SentinelCheckID.CHK_007,
                severity=SentinelSeverity.CRITICAL,
                message=(
                    f"MEMORY_WRITE blocked: GAIAN '{gaian_id}' has not granted "
                    "MEMORY_WRITE consent. C27 CHK-007 / C17."
                ),
            ))
            return

        # Check actor is primary steward
        if actor_id is None or actor_id != primary_steward_id:
            self._record(SentinelFinding(
                gaian_id=gaian_id,
                check_id=SentinelCheckID.CHK_007,
                severity=SentinelSeverity.CRITICAL,
                message=(
                    f"MEMORY_WRITE blocked: actor '{actor_id}' is not the primary steward "
                    f"('{primary_steward_id}'). C27 CHK-007 / C17."
                ),
            ))

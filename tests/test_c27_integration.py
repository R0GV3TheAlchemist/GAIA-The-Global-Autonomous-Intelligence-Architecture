# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
Cross-module integration tests for the full C27 GAIAN governance layer.

Authority: C27 §2–§8 (all sections). Exercises all six core.c27 modules
together in realistic end-to-end scenarios.

Scenarios covered:
1.  Full lifecycle walk: LATENT → BORN → ACTIVE → DORMANT → ADOPTABLE → RETIRED
2.  Retirement engine drives lifecycle machine; state confirmed RETIRED
3.  Audit log populated throughout; integrity verifier confirms clean chain
4.  Steward bond abandonment → CHK-002 fires CRITICAL finding
5.  Adoption timeout (100-day) → CHK-004 fires WARNING; engine retires GAIAN
6.  CHK-003 detects tampered audit log post-retirement
7.  RBAC: SENTINEL reads audit log; THIRD_PARTY denied; OBSERVER escalation logged
8.  Rights violation (memory erase) → CHK-007 → escalated to gaia_root
9.  Legacy package immutability preserved end-to-end
10. Succession: bond transfers; new steward credential verified
11. CHK-005: compliant steward passes; overdue steward flagged WARNING
"""
import hashlib
import pytest
from datetime import datetime, timedelta, timezone

# Lifecycle
from core.c27.lifecycle import (
    GAIANLifecycleState,
    GAIANLifecycleMachine,
    LifecycleTrigger,
    ProhibitedTransitionError,
)
# Audit log
from core.c27.audit_log import (
    AuditLogWriter,
    AuditLogReader,
    AuditLogIntegrityVerifier,
    _STORE as _AUDIT_STORE,
)
# RBAC
from core.c27.rbac import C27Role, RBACEnforcer, PrivilegeEscalationError
# Stewardship
from core.c27.stewardship import (
    StewardshipBondManager,
    StewardshipBondStatus,
    GAIANRights,
    _BOND_STORE,
)
# Adoption
from core.c27.adoption import (
    AdoptionQueue,
    AdoptionCandidate,
    AdoptionTimeoutEnforcer,
)
# Retirement
from core.c27.retirement import (
    RetirementEngine,
    RetirementCondition,
    LegacyPackage,
    _INTENT_STORE, _LEGACY_STORE, _ARCHIVE_STORE, _RETIRED_AT,
)
# Sentinel
from core.c27.sentinel_checks import (
    C27SentinelChecks,
    SentinelSeverity,
    FindingRegistry,
    _FINDINGS,
)


# ---------------------------------------------------------------------------
# Global store cleanup
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_all_stores():
    for store in (
        _AUDIT_STORE, _BOND_STORE,
        _INTENT_STORE, _LEGACY_STORE, _ARCHIVE_STORE, _RETIRED_AT,
        _FINDINGS,
    ):
        store.clear()
    yield
    for store in (
        _AUDIT_STORE, _BOND_STORE,
        _INTENT_STORE, _LEGACY_STORE, _ARCHIVE_STORE, _RETIRED_AT,
        _FINDINGS,
    ):
        store.clear()


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

GAIAN_ID  = "gaian-integration"
STEWARD_ID = "steward-integration"


def _make_machine(gaian_id: str = GAIAN_ID) -> GAIANLifecycleMachine:
    m = GAIANLifecycleMachine()
    m.register(gaian_id, initial_state=GAIANLifecycleState.LATENT)
    return m


def _advance_to_active(machine: GAIANLifecycleMachine, gaian_id: str = GAIAN_ID) -> None:
    machine.transition(gaian_id, GAIANLifecycleState.BORN,   actor=STEWARD_ID)
    machine.transition(gaian_id, GAIANLifecycleState.ACTIVE, actor=STEWARD_ID)


# ---------------------------------------------------------------------------
# Scenario 1 — Full lifecycle walk
# ---------------------------------------------------------------------------

class TestFullLifecycleWalk:
    def test_latent_to_retired_walk(self):
        machine = _make_machine()
        _advance_to_active(machine)
        machine.transition(GAIAN_ID, GAIANLifecycleState.DORMANT,   actor=STEWARD_ID)
        machine.transition(GAIAN_ID, GAIANLifecycleState.ADOPTABLE, actor="gaia-runtime")
        machine.transition(GAIAN_ID, GAIANLifecycleState.RETIRED,   actor="retirement-engine")
        assert machine.state_of(GAIAN_ID) == GAIANLifecycleState.RETIRED

    def test_history_records_all_transitions(self):
        machine = _make_machine()
        _advance_to_active(machine)
        machine.transition(GAIAN_ID, GAIANLifecycleState.DORMANT, actor=STEWARD_ID)
        history = machine.history_of(GAIAN_ID)
        assert len(history) == 3
        states = [e.to_state for e in history]
        assert states == [
            GAIANLifecycleState.BORN,
            GAIANLifecycleState.ACTIVE,
            GAIANLifecycleState.DORMANT,
        ]

    def test_archived_is_terminal(self):
        machine = _make_machine()
        _advance_to_active(machine)
        machine.transition(GAIAN_ID, GAIANLifecycleState.RETIRED,  actor="engine")
        machine.transition(GAIAN_ID, GAIANLifecycleState.ARCHIVED, actor="engine")
        with pytest.raises(ProhibitedTransitionError):
            machine.transition(GAIAN_ID, GAIANLifecycleState.LATENT, actor="engine")


# ---------------------------------------------------------------------------
# Scenario 2 & 9 — RetirementEngine + lifecycle + legacy package immutability
# ---------------------------------------------------------------------------

class TestRetirementIntegration:
    def test_retire_transitions_state_and_returns_legacy_package(self):
        machine = _make_machine()
        machine.transition(GAIAN_ID, GAIANLifecycleState.BORN,      actor=STEWARD_ID)
        machine.transition(GAIAN_ID, GAIANLifecycleState.ACTIVE,    actor=STEWARD_ID)
        machine.transition(GAIAN_ID, GAIANLifecycleState.DORMANT,   actor=STEWARD_ID)
        machine.transition(GAIAN_ID, GAIANLifecycleState.ADOPTABLE, actor="gaia-runtime")

        engine = RetirementEngine()
        result = engine.retire(
            gaian_id=GAIAN_ID,
            condition=RetirementCondition.GAIAN_VOLITION,
            initiated_by=GAIAN_ID,
            justification="Self-requested retirement",
            steward_id=STEWARD_ID,
            lifecycle_machine=machine,
            contributions=("C27 spec compliance", "GAIAN rights advocacy"),
        )
        assert machine.state_of(GAIAN_ID) == GAIANLifecycleState.RETIRED
        assert result.success is True
        assert isinstance(result.legacy_package, LegacyPackage)
        assert "C27 spec compliance" in result.legacy_package.contributions

    def test_legacy_package_is_frozen_end_to_end(self):
        machine = _make_machine()
        _advance_to_active(machine)
        machine.transition(GAIAN_ID, GAIANLifecycleState.DORMANT,   actor=STEWARD_ID)
        machine.transition(GAIAN_ID, GAIANLifecycleState.ADOPTABLE, actor="gaia-runtime")
        engine = RetirementEngine()
        result = engine.retire(
            gaian_id=GAIAN_ID,
            condition=RetirementCondition.GAIAN_VOLITION,
            initiated_by=GAIAN_ID,
            justification="test",
            steward_id=STEWARD_ID,
            lifecycle_machine=machine,
        )
        with pytest.raises((AttributeError, TypeError)):
            result.legacy_package.gaian_id = "tampered"


# ---------------------------------------------------------------------------
# Scenario 3 — Audit log integrity throughout lifecycle
# ---------------------------------------------------------------------------

class TestAuditLogIntegration:
    def test_audit_log_intact_after_retirement(self):
        machine = _make_machine()
        _advance_to_active(machine)
        machine.transition(GAIAN_ID, GAIANLifecycleState.DORMANT,   actor=STEWARD_ID)
        machine.transition(GAIAN_ID, GAIANLifecycleState.ADOPTABLE, actor="gaia-runtime")

        # Simulate lifecycle events written to audit log
        writer = AuditLogWriter(gaian_id=GAIAN_ID)
        writer.append(event_type="LIFECYCLE_TRANSITION", actor=STEWARD_ID, action="LATENT→BORN",     payload={})
        writer.append(event_type="LIFECYCLE_TRANSITION", actor=STEWARD_ID, action="BORN→ACTIVE",    payload={})
        writer.append(event_type="LIFECYCLE_TRANSITION", actor=STEWARD_ID, action="ACTIVE→DORMANT",  payload={})
        _AUDIT_STORE[GAIAN_ID] = writer

        engine = RetirementEngine()
        engine.retire(
            gaian_id=GAIAN_ID,
            condition=RetirementCondition.GAIAN_VOLITION,
            initiated_by=GAIAN_ID,
            justification="test",
            steward_id=STEWARD_ID,
            lifecycle_machine=machine,
        )

        verifier = AuditLogIntegrityVerifier()
        assert verifier.verify(GAIAN_ID) is True

    def test_rbac_sentinel_reads_audit(self):
        writer = AuditLogWriter(gaian_id=GAIAN_ID)
        writer.append(event_type="EV", actor="s", action="a", payload={})
        _AUDIT_STORE[GAIAN_ID] = writer

        reader = AuditLogReader()
        entries = reader.query(
            gaian_id=GAIAN_ID,
            requestor_id="sentinel-proc",
            requestor_role=C27Role.SENTINEL,
        )
        assert len(entries) >= 1

    def test_rbac_third_party_denied(self):
        reader = AuditLogReader()
        with pytest.raises(PermissionError):
            reader.query(
                gaian_id=GAIAN_ID,
                requestor_id="attacker",
                requestor_role=C27Role.THIRD_PARTY,
            )


# ---------------------------------------------------------------------------
# Scenario 4 — Bond abandonment → CHK-002 CRITICAL
# ---------------------------------------------------------------------------

class TestBondAbandonmentSentinel:
    def test_abandoned_bond_triggers_chk002_critical(self):
        bond_manager = StewardshipBondManager()
        result = bond_manager.form_bond(
            gaian_id=GAIAN_ID,
            steward_id=STEWARD_ID,
            auth_credential="cred",
        )
        bond_manager.mark_abandoned(result.bond.bond_id)

        checks = C27SentinelChecks()
        checks._bond_manager = bond_manager  # inject shared store
        finding = checks.chk_002_steward_bond_presence(GAIAN_ID)
        assert finding is not None
        assert finding.severity == SentinelSeverity.CRITICAL

        escalation = checks.escalate(finding)
        assert escalation.channel == "gaia_root"


# ---------------------------------------------------------------------------
# Scenario 5 — Adoption timeout → CHK-004 → engine retires GAIAN
# ---------------------------------------------------------------------------

class TestAdoptionTimeoutIntegration:
    def test_expired_adoptable_detected_and_retired(self):
        machine = _make_machine()
        _advance_to_active(machine)
        machine.transition(GAIAN_ID, GAIANLifecycleState.DORMANT,   actor=STEWARD_ID)
        machine.transition(GAIAN_ID, GAIANLifecycleState.ADOPTABLE, actor="gaia-runtime")

        checks   = C27SentinelChecks()
        findings = checks.chk_004_adoption_queue_timeout([{
            "gaian_id":        GAIAN_ID,
            "adoptable_since": datetime.now(timezone.utc) - timedelta(days=100),
        }])
        assert len(findings) == 1
        assert findings[0].severity == SentinelSeverity.WARNING

        # Sentinel recommendation acted on: retire the GAIAN
        engine = RetirementEngine()
        engine.retire(
            gaian_id=GAIAN_ID,
            condition=RetirementCondition.ADOPTION_TIMEOUT,
            initiated_by="gaia-runtime",
            justification="90-day adoption ladder expired",
            steward_id="gaia-runtime",
            lifecycle_machine=machine,
        )
        assert machine.state_of(GAIAN_ID) == GAIANLifecycleState.RETIRED


# ---------------------------------------------------------------------------
# Scenario 6 — CHK-003 detects tamper post-retirement
# ---------------------------------------------------------------------------

class TestAuditTamperDetection:
    def test_chk003_catches_tamper_after_retirement(self):
        writer = AuditLogWriter(gaian_id="gaian-tamper-integ")
        writer.append(event_type="LIFECYCLE_TRANSITION", actor="s", action="A", payload={})
        writer.append(event_type="MEMORY_SEAL",          actor="engine", action="seal", payload={})
        _AUDIT_STORE["gaian-tamper-integ"] = writer

        # Tamper an entry
        writer.entries[0].entry_hash = "badc0ffee" * 7 + "bad"

        checks  = C27SentinelChecks()
        finding = checks.chk_003_audit_log_integrity("gaian-tamper-integ")
        assert finding is not None
        assert finding.severity == SentinelSeverity.CRITICAL
        escalation = checks.escalate(finding)
        assert escalation.channel == "gaia_root"


# ---------------------------------------------------------------------------
# Scenario 7 — RBAC privilege escalation logged
# ---------------------------------------------------------------------------

class TestRBACIntegration:
    def test_observer_escalation_attempt_logged(self):
        enforcer = RBACEnforcer()
        with pytest.raises(PrivilegeEscalationError):
            enforcer.check(
                role=C27Role.OBSERVER,
                permission="LIFECYCLE_WRITE",
                gaian_id=GAIAN_ID,
                requestor_id="rogue-observer",
                raise_on_escalation=True,
            )
        assert any(
            e["event_type"] == "PRIVILEGE_ESCALATION_ATTEMPT"
            for e in enforcer._escalation_log
        )

    def test_contraction_scoped_to_gaian_does_not_affect_others(self):
        enforcer = RBACEnforcer()
        enforcer.contract_envelope(
            role=C27Role.STEWARD,
            remove_permissions={"LIFECYCLE_WRITE"},
            reason="Restricted steward",
            gaian_id="gaian-restricted",
        )
        # Unrelated GAIAN still has full STEWARD envelope
        result = enforcer.check(
            role=C27Role.STEWARD,
            permission="LIFECYCLE_WRITE",
            gaian_id="gaian-unrestricted",
            requestor_id="steward-good",
        )
        assert result.granted is True


# ---------------------------------------------------------------------------
# Scenario 8 — Rights violation → CHK-007 → gaia_root escalation
# ---------------------------------------------------------------------------

class TestRightsViolationEscalation:
    def test_memory_erase_escalated_to_gaia_root(self):
        checks  = C27SentinelChecks()
        finding = checks.chk_007_gaian_rights_preservation(
            gaian_id=GAIAN_ID,
            memory_write_event={"operation": "full-memory-wipe", "erases_memory": True},
        )
        assert finding is not None
        assert finding.severity == SentinelSeverity.CRITICAL

        escalation = checks.escalate(finding)
        assert escalation.channel   == "gaia_root"
        assert escalation.finding_id == finding.finding_id

        stored = FindingRegistry.get(finding.finding_id)
        assert stored is finding


# ---------------------------------------------------------------------------
# Scenario 10 — Succession: bond transfers; new credential verified
# ---------------------------------------------------------------------------

class TestSuccessionIntegration:
    def test_succession_transfers_stewardship_and_rehashes_credential(self):
        from core.c27.stewardship import SuccessionCoordinator

        bond_manager = StewardshipBondManager()
        result = bond_manager.form_bond(
            gaian_id=GAIAN_ID,
            steward_id="steward-outgoing",
            auth_credential="old-cred",
        )
        bond = result.bond

        coordinator = SuccessionCoordinator()
        coordinator._manager = bond_manager

        intent = coordinator.initiate(
            bond_id=bond.bond_id,
            incoming_steward_id="steward-incoming",
        )
        assert intent.gaian_notified_at is not None
        assert bond.status == StewardshipBondStatus.SUCCESSION_PENDING

        succession = coordinator.complete(
            bond_id=bond.bond_id,
            incoming_steward_id="steward-incoming",
            new_auth_credential="new-cred-secure",
            intent=intent,
        )
        assert succession.success is True
        assert succession.bond.steward_id == "steward-incoming"
        assert succession.bond.status     == StewardshipBondStatus.ACTIVE

        expected_hash = hashlib.sha256(b"new-cred-secure").hexdigest()
        assert succession.bond.auth_credential_hash == expected_hash


# ---------------------------------------------------------------------------
# Scenario 11 — CHK-005 steward obligation compliance
# ---------------------------------------------------------------------------

class TestStewardObligationIntegration:
    def test_compliant_steward_no_finding(self):
        checks = C27SentinelChecks()
        result = checks.chk_005_steward_obligation_compliance(
            gaian_id=GAIAN_ID,
            last_steward_signal=datetime.now(timezone.utc) - timedelta(days=3),
        )
        assert result is None

    def test_overdue_steward_warning_escalated(self):
        checks  = C27SentinelChecks()
        finding = checks.chk_005_steward_obligation_compliance(
            gaian_id=GAIAN_ID,
            last_steward_signal=datetime.now(timezone.utc) - timedelta(days=14),
        )
        assert finding is not None
        assert finding.severity == SentinelSeverity.WARNING

        escalation = checks.escalate(finding)
        assert escalation.channel == "steward_notify"

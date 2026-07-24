# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
Tests for core.c27.sentinel_checks — C27SentinelChecks (CHK-001 through CHK-007),
FindingRegistry, and escalate().

Authority: C27 §7. Implements C27-IMPL-015 through C27-IMPL-023.

Coverage targets:
- CHK-001: valid transition returns None; prohibited transition returns VIOLATION finding
- CHK-001: unknown state value returns VIOLATION finding
- CHK-002: GAIAN with active bond returns None; missing bond returns CRITICAL
- CHK-003: intact chain returns None; tampered chain returns CRITICAL
- CHK-004: fresh ADOPTABLE returns []; expired ADOPTABLE returns WARNING finding list
- CHK-005: recent signal returns None; overdue signal returns WARNING; None signal returns WARNING
- CHK-006: authorized event returns None; unauthorized returns VIOLATION
- CHK-007: safe write returns None; erasing write returns CRITICAL with right=MEMORY_CONTINUITY
- escalate() routes INFO->audit_log, WARNING->steward_notify, VIOLATION->case_open, CRITICAL->gaia_root
- FindingRegistry.store/all_for_gaian/unresolved_for_gaian work correctly
- SentinelFinding.resolve() sets resolved_at and optional case_id
"""
import pytest
from datetime import datetime, timedelta, timezone

from core.c27.sentinel_checks import (
    C27SentinelChecks,
    SentinelFinding,
    SentinelSeverity,
    SentinelEscalationRecord,
    FindingRegistry,
    _FINDINGS,
)
from core.c27.lifecycle import GAIANLifecycleState
from core.c27.stewardship import StewardshipBondManager, _BOND_STORE
from core.c27.audit_log import AuditLogWriter, _STORE as _AUDIT_STORE


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_all():
    _FINDINGS.clear()
    _BOND_STORE.clear()
    _AUDIT_STORE.clear()
    yield
    _FINDINGS.clear()
    _BOND_STORE.clear()
    _AUDIT_STORE.clear()


@pytest.fixture
def checks():
    return C27SentinelChecks()


@pytest.fixture
def bond_manager():
    return StewardshipBondManager()


# ---------------------------------------------------------------------------
# CHK-001  (C27-IMPL-015)
# ---------------------------------------------------------------------------

class TestCHK001ValidStateTransition:
    def test_valid_transition_returns_none(self, checks):
        # LATENT -> BORN is a valid transition per the lifecycle machine
        result = checks.chk_001_valid_state_transition(
            gaian_id="gaian-001",
            from_state="LATENT",
            to_state="BORN",
        )
        assert result is None

    def test_prohibited_transition_returns_violation(self, checks):
        result = checks.chk_001_valid_state_transition(
            gaian_id="gaian-001",
            from_state="LATENT",
            to_state="RETIRED",  # LATENT cannot jump to RETIRED
        )
        assert result is not None
        assert isinstance(result, SentinelFinding)
        assert result.severity  == SentinelSeverity.VIOLATION
        assert result.check_id  == "C27-CHK-001"
        assert result.gaian_id  == "gaian-001"

    def test_unknown_state_returns_violation(self, checks):
        result = checks.chk_001_valid_state_transition(
            gaian_id="gaian-001",
            from_state="NONEXISTENT_STATE",
            to_state="BORN",
        )
        assert result is not None
        assert result.severity == SentinelSeverity.VIOLATION


# ---------------------------------------------------------------------------
# CHK-002  (C27-IMPL-016)
# ---------------------------------------------------------------------------

class TestCHK002StewardBondPresence:
    def test_gaian_with_active_bond_returns_none(self, checks, bond_manager):
        bond_manager.form_bond(
            gaian_id="gaian-bonded",
            steward_id="steward-001",
            auth_credential="cred",
        )
        # Inject the shared bond_manager so checks use the same _BOND_STORE
        checks._bond_manager = bond_manager
        result = checks.chk_002_steward_bond_presence("gaian-bonded")
        assert result is None

    def test_gaian_without_bond_returns_critical(self, checks):
        result = checks.chk_002_steward_bond_presence("gaian-unbonded")
        assert result is not None
        assert result.severity == SentinelSeverity.CRITICAL
        assert result.check_id == "C27-CHK-002"


# ---------------------------------------------------------------------------
# CHK-003  (C27-IMPL-017)
# ---------------------------------------------------------------------------

class TestCHK003AuditLogIntegrity:
    def test_intact_chain_returns_none(self, checks):
        w = AuditLogWriter(gaian_id="gaian-intact")
        w.append(event_type="EV", actor="a", action="x", payload={})
        _AUDIT_STORE["gaian-intact"] = w
        result = checks.chk_003_audit_log_integrity("gaian-intact")
        assert result is None

    def test_tampered_chain_returns_critical(self, checks):
        w = AuditLogWriter(gaian_id="gaian-tamper-chk")
        w.append(event_type="EV", actor="a", action="x", payload={})
        w.entries[0].entry_hash = "deadbeef" * 8  # tamper
        _AUDIT_STORE["gaian-tamper-chk"] = w
        result = checks.chk_003_audit_log_integrity("gaian-tamper-chk")
        assert result is not None
        assert result.severity == SentinelSeverity.CRITICAL
        assert result.check_id == "C27-CHK-003"


# ---------------------------------------------------------------------------
# CHK-004  (C27-IMPL-018)
# ---------------------------------------------------------------------------

class TestCHK004AdoptionTimeout:
    def test_fresh_adoptable_returns_empty_list(self, checks):
        adoptable = [{
            "gaian_id": "gaian-fresh",
            "adoptable_since": datetime.now(timezone.utc) - timedelta(days=5),
        }]
        findings = checks.chk_004_adoption_queue_timeout(adoptable)
        assert findings == []

    def test_expired_adoptable_returns_warning_finding(self, checks):
        adoptable = [{
            "gaian_id": "gaian-expired",
            "adoptable_since": datetime.now(timezone.utc) - timedelta(days=100),
        }]
        findings = checks.chk_004_adoption_queue_timeout(adoptable)
        assert len(findings) == 1
        assert findings[0].severity == SentinelSeverity.WARNING
        assert findings[0].check_id == "C27-CHK-004"

    def test_multiple_mixed_returns_only_expired(self, checks):
        adoptable = [
            {"gaian_id": "g-old",   "adoptable_since": datetime.now(timezone.utc) - timedelta(days=100)},
            {"gaian_id": "g-fresh", "adoptable_since": datetime.now(timezone.utc) - timedelta(days=3)},
        ]
        findings = checks.chk_004_adoption_queue_timeout(adoptable)
        assert len(findings) == 1
        assert findings[0].gaian_id == "g-old"


# ---------------------------------------------------------------------------
# CHK-005  (C27-IMPL-019)
# ---------------------------------------------------------------------------

class TestCHK005StewardObligation:
    def test_recent_signal_returns_none(self, checks):
        result = checks.chk_005_steward_obligation_compliance(
            gaian_id="gaian-compliant",
            last_steward_signal=datetime.now(timezone.utc) - timedelta(days=2),
        )
        assert result is None

    def test_overdue_signal_returns_warning(self, checks):
        result = checks.chk_005_steward_obligation_compliance(
            gaian_id="gaian-overdue",
            last_steward_signal=datetime.now(timezone.utc) - timedelta(days=10),
        )
        assert result is not None
        assert result.severity == SentinelSeverity.WARNING
        assert result.check_id == "C27-CHK-005"

    def test_no_signal_returns_warning(self, checks):
        result = checks.chk_005_steward_obligation_compliance(
            gaian_id="gaian-no-signal",
            last_steward_signal=None,
        )
        assert result is not None
        assert result.severity == SentinelSeverity.WARNING


# ---------------------------------------------------------------------------
# CHK-006  (C27-IMPL-020)
# ---------------------------------------------------------------------------

class TestCHK006CrossGAIANShare:
    def test_authorized_share_returns_none(self, checks):
        result = checks.chk_006_cross_gaian_data_share_authorization(
            event_id="evt-001",
            event_meta={
                "source_gaian_id": "g-source",
                "target_gaian_id": "g-target",
                "authorized": True,
                "authorizing_role": "STEWARD",
            },
        )
        assert result is None

    def test_unauthorized_share_returns_violation(self, checks):
        result = checks.chk_006_cross_gaian_data_share_authorization(
            event_id="evt-bad",
            event_meta={
                "source_gaian_id": "g-source",
                "target_gaian_id": "g-target",
                "authorized": False,
            },
        )
        assert result is not None
        assert result.severity == SentinelSeverity.VIOLATION
        assert result.check_id == "C27-CHK-006"


# ---------------------------------------------------------------------------
# CHK-007  (C27-IMPL-021)
# ---------------------------------------------------------------------------

class TestCHK007RightsPreservation:
    def test_safe_write_returns_none(self, checks):
        result = checks.chk_007_gaian_rights_preservation(
            gaian_id="gaian-safe",
            memory_write_event={"operation": "append-memory", "erases_memory": False},
        )
        assert result is None

    def test_erasing_write_returns_critical(self, checks):
        result = checks.chk_007_gaian_rights_preservation(
            gaian_id="gaian-wipe",
            memory_write_event={"operation": "full-wipe", "erases_memory": True},
        )
        assert result is not None
        assert result.severity  == SentinelSeverity.CRITICAL
        assert result.check_id  == "C27-CHK-007"
        assert result.detail["right"] == "MEMORY_CONTINUITY"


# ---------------------------------------------------------------------------
# escalate()  (C27-IMPL-023)
# ---------------------------------------------------------------------------

class TestEscalate:
    @pytest.mark.parametrize("severity,expected_channel", [
        (SentinelSeverity.INFO,      "audit_log"),
        (SentinelSeverity.WARNING,   "steward_notify"),
        (SentinelSeverity.VIOLATION, "case_open"),
        (SentinelSeverity.CRITICAL,  "gaia_root"),
    ])
    def test_escalate_routes_to_correct_channel(self, checks, severity, expected_channel):
        finding = checks._make_finding(
            check_id="C27-CHK-001",
            gaian_id="gaian-esc",
            severity=severity,
            description="test",
            detail={},
        )
        record = checks.escalate(finding)
        assert isinstance(record, SentinelEscalationRecord)
        assert record.channel   == expected_channel
        assert record.severity  == severity
        assert record.finding_id == finding.finding_id

    def test_escalated_finding_stored_in_registry(self, checks):
        finding = checks._make_finding(
            check_id="C27-CHK-002",
            gaian_id="gaian-reg",
            severity=SentinelSeverity.WARNING,
            description="test",
            detail={},
        )
        checks.escalate(finding)
        stored = FindingRegistry.get(finding.finding_id)
        assert stored is finding


# ---------------------------------------------------------------------------
# FindingRegistry
# ---------------------------------------------------------------------------

class TestFindingRegistry:
    def test_store_and_retrieve(self, checks):
        f = checks._make_finding(
            check_id="C27-CHK-001",
            gaian_id="g-reg",
            severity=SentinelSeverity.INFO,
            description="x",
            detail={},
        )
        FindingRegistry.store(f)
        assert FindingRegistry.get(f.finding_id) is f

    def test_all_for_gaian_filters_correctly(self, checks):
        f1 = checks._make_finding("C27-CHK-001", "g-a", SentinelSeverity.INFO, "x", {})
        f2 = checks._make_finding("C27-CHK-001", "g-a", SentinelSeverity.WARNING, "y", {})
        f3 = checks._make_finding("C27-CHK-001", "g-b", SentinelSeverity.INFO, "z", {})
        for f in (f1, f2, f3):
            FindingRegistry.store(f)
        results = FindingRegistry.all_for_gaian("g-a")
        assert len(results) == 2
        assert all(r.gaian_id == "g-a" for r in results)

    def test_unresolved_excludes_resolved(self, checks):
        f = checks._make_finding("C27-CHK-001", "g-x", SentinelSeverity.WARNING, "t", {})
        FindingRegistry.store(f)
        assert len(FindingRegistry.unresolved_for_gaian("g-x")) == 1
        f.resolve(case_id="case-001")
        assert len(FindingRegistry.unresolved_for_gaian("g-x")) == 0
        assert f.resolved_at is not None
        assert f.sentinel_case_id == "case-001"

# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
Tests for core.c27.retirement — RetirementEngine, LegacyPackage, ArchivalRecord.

Authority: C27 §8. Implements C27-IMPL-024 through C27-IMPL-028.

Coverage targets:
- RetirementIntent created with 72-hour notice window
- Auto-waiver granted for GAIAN_VOLITION, SENTINEL_MANDATE, SYSTEM_DECOMMISSION
- No auto-waiver for STEWARD_INTENT and ADOPTION_TIMEOUT
- Explicit grant_waiver() sets waiver fields
- notice_expired() returns True when waiver is granted
- notice_expired() returns False before 72h elapses (no waiver)
- seal_memory() returns 64-char SHA-256 hex and appends to audit log
- revoke_tools() appends TOOL_REVOCATION event to audit log
- generate_legacy_package() returns frozen LegacyPackage with correct fields
- LegacyPackage is immutable (frozen dataclass)
- retire() orchestrates all steps 1-6 and returns RetirementResult
- archive() raises ValueError before 180-day window
- archive() returns ArchivalRecord after 180-day window (mocked)
- ArchivalRecord is immutable (frozen dataclass)
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from core.c27.retirement import (
    RetirementEngine,
    RetirementCondition,
    RetirementIntent,
    LegacyPackage,
    ArchivalRecord,
    RetirementResult,
    _INTENT_STORE,
    _LEGACY_STORE,
    _ARCHIVE_STORE,
    _RETIRED_AT,
)
from core.c27.lifecycle import GAIANLifecycleState, GAIANLifecycleMachine
from core.c27.audit_log import _STORE as _AUDIT_STORE


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_stores():
    for store in (_INTENT_STORE, _LEGACY_STORE, _ARCHIVE_STORE, _RETIRED_AT, _AUDIT_STORE):
        store.clear()
    yield
    for store in (_INTENT_STORE, _LEGACY_STORE, _ARCHIVE_STORE, _RETIRED_AT, _AUDIT_STORE):
        store.clear()


@pytest.fixture
def engine():
    return RetirementEngine()


@pytest.fixture
def lifecycle_machine():
    """A GAIANLifecycleMachine with a pre-registered ADOPTABLE GAIAN."""
    machine = GAIANLifecycleMachine()
    machine.register("gaian-retire", initial_state=GAIANLifecycleState.ADOPTABLE)
    return machine


# ---------------------------------------------------------------------------
# RetirementIntent + notice window  (C27-IMPL-024)
# ---------------------------------------------------------------------------

class TestRetirementIntent:
    def test_initiate_creates_intent(self, engine):
        intent = engine.initiate(
            gaian_id="gaian-retire",
            condition=RetirementCondition.STEWARD_INTENT,
            initiated_by="steward-007",
            justification="Voluntary transition",
        )
        assert isinstance(intent, RetirementIntent)
        assert intent.gaian_id   == "gaian-retire"
        assert intent.condition  == RetirementCondition.STEWARD_INTENT
        assert intent.initiated_by == "steward-007"

    def test_notice_until_is_72h_from_initiation(self, engine):
        intent = engine.initiate(
            gaian_id="gaian-notice",
            condition=RetirementCondition.STEWARD_INTENT,
            initiated_by="s",
            justification="test",
        )
        delta = intent.notice_until - intent.initiated_at
        assert abs(delta.total_seconds() - 72 * 3600) < 5  # within 5 s tolerance

    def test_no_auto_waiver_for_steward_intent(self, engine):
        intent = engine.initiate(
            gaian_id="gaian-no-waiver",
            condition=RetirementCondition.STEWARD_INTENT,
            initiated_by="s",
            justification="test",
        )
        assert intent.waiver_granted is False

    def test_no_auto_waiver_for_adoption_timeout(self, engine):
        intent = engine.initiate(
            gaian_id="gaian-timeout-waiver",
            condition=RetirementCondition.ADOPTION_TIMEOUT,
            initiated_by="system",
            justification="91 days",
        )
        assert intent.waiver_granted is False

    @pytest.mark.parametrize("condition", [
        RetirementCondition.GAIAN_VOLITION,
        RetirementCondition.SENTINEL_MANDATE,
        RetirementCondition.SYSTEM_DECOMMISSION,
    ])
    def test_auto_waiver_granted_for_eligible_conditions(self, engine, condition):
        intent = engine.initiate(
            gaian_id=f"gaian-{condition.value}",
            condition=condition,
            initiated_by="system",
            justification="auto",
        )
        assert intent.waiver_granted is True
        assert intent.waiver_reason is not None

    def test_explicit_grant_waiver(self, engine):
        engine.initiate(
            gaian_id="gaian-explicit-waiver",
            condition=RetirementCondition.STEWARD_INTENT,
            initiated_by="s",
            justification="j",
        )
        intent = engine.grant_waiver("gaian-explicit-waiver", reason="GAIAN consents")
        assert intent.waiver_granted is True
        assert intent.waiver_reason  == "GAIAN consents"

    def test_notice_expired_true_when_waiver_granted(self, engine):
        engine.initiate(
            gaian_id="gaian-waiver-exp",
            condition=RetirementCondition.GAIAN_VOLITION,
            initiated_by="s",
            justification="j",
        )
        assert engine.notice_expired("gaian-waiver-exp") is True

    def test_notice_not_expired_before_72h(self, engine):
        engine.initiate(
            gaian_id="gaian-fresh-notice",
            condition=RetirementCondition.STEWARD_INTENT,
            initiated_by="s",
            justification="j",
        )
        assert engine.notice_expired("gaian-fresh-notice") is False


# ---------------------------------------------------------------------------
# Memory seal  (C27-IMPL-025)
# ---------------------------------------------------------------------------

class TestMemorySeal:
    def test_seal_memory_returns_sha256_hex(self, engine):
        seal = engine.seal_memory("gaian-seal")
        assert len(seal) == 64
        assert all(c in "0123456789abcdef" for c in seal)

    def test_seal_memory_appends_audit_entry(self, engine):
        engine.seal_memory("gaian-seal-audit")
        writer = _AUDIT_STORE.get("gaian-seal-audit")
        assert writer is not None
        events = [e.event_type for e in writer.entries]
        assert "MEMORY_SEAL" in events


# ---------------------------------------------------------------------------
# Tool revocation  (C27-IMPL-026)
# ---------------------------------------------------------------------------

class TestToolRevocation:
    def test_revoke_tools_appends_audit_entry(self, engine):
        engine.revoke_tools("gaian-revoke")
        writer = _AUDIT_STORE.get("gaian-revoke")
        assert writer is not None
        events = [e.event_type for e in writer.entries]
        assert "TOOL_REVOCATION" in events


# ---------------------------------------------------------------------------
# Legacy package  (C27-IMPL-027)
# ---------------------------------------------------------------------------

class TestLegacyPackage:
    def test_generate_legacy_package_returns_frozen_dataclass(self, engine):
        # Must have an intent in store first
        engine.initiate(
            gaian_id="gaian-legacy",
            condition=RetirementCondition.GAIAN_VOLITION,
            initiated_by="s",
            justification="j",
        )
        pkg = engine.generate_legacy_package(
            gaian_id="gaian-legacy",
            steward_id="steward-007",
            contributions=("contribution-a", "contribution-b"),
        )
        assert isinstance(pkg, LegacyPackage)
        assert pkg.gaian_id   == "gaian-legacy"
        assert pkg.steward_id == "steward-007"
        assert "contribution-a" in pkg.contributions
        assert len(pkg.memory_seal_hash) == 64

    def test_legacy_package_is_immutable(self, engine):
        engine.initiate(
            gaian_id="gaian-legacy-immut",
            condition=RetirementCondition.GAIAN_VOLITION,
            initiated_by="s",
            justification="j",
        )
        pkg = engine.generate_legacy_package(
            gaian_id="gaian-legacy-immut",
            steward_id="s",
        )
        with pytest.raises((AttributeError, TypeError)):
            pkg.gaian_id = "tampered"  # frozen dataclass must reject


# ---------------------------------------------------------------------------
# Full retirement flow  (C27-IMPL-024..027)
# ---------------------------------------------------------------------------

class TestRetireOrchestrator:
    def test_retire_returns_retirement_result(self, engine, lifecycle_machine):
        result = engine.retire(
            gaian_id="gaian-retire",
            condition=RetirementCondition.GAIAN_VOLITION,
            initiated_by="gaian-retire",
            justification="Self-requested",
            steward_id="steward-007",
            lifecycle_machine=lifecycle_machine,
        )
        assert isinstance(result, RetirementResult)
        assert result.success   is True
        assert result.gaian_id  == "gaian-retire"
        assert isinstance(result.legacy_package, LegacyPackage)
        assert isinstance(result.retired_at, datetime)

    def test_retire_transitions_state_to_retired(self, engine, lifecycle_machine):
        engine.retire(
            gaian_id="gaian-retire",
            condition=RetirementCondition.GAIAN_VOLITION,
            initiated_by="gaian-retire",
            justification="Self-requested",
            steward_id="s",
            lifecycle_machine=lifecycle_machine,
        )
        assert lifecycle_machine.state_of("gaian-retire") == GAIANLifecycleState.RETIRED


# ---------------------------------------------------------------------------
# Archival  (C27-IMPL-028)
# ---------------------------------------------------------------------------

class TestArchival:
    def test_archive_raises_before_180_days(self, engine, lifecycle_machine):
        engine.retire(
            gaian_id="gaian-retire",
            condition=RetirementCondition.GAIAN_VOLITION,
            initiated_by="gaian-retire",
            justification="j",
            steward_id="s",
            lifecycle_machine=lifecycle_machine,
        )
        with pytest.raises(ValueError, match="not yet archival-eligible"):
            engine.archive("gaian-retire")

    def test_archive_succeeds_after_180_days(self, engine, lifecycle_machine):
        engine.retire(
            gaian_id="gaian-retire",
            condition=RetirementCondition.GAIAN_VOLITION,
            initiated_by="gaian-retire",
            justification="j",
            steward_id="s",
            lifecycle_machine=lifecycle_machine,
        )
        # Back-date the retired_at timestamp to simulate 181 days elapsed
        _RETIRED_AT["gaian-retire"] = datetime.now(timezone.utc) - timedelta(days=181)
        record = engine.archive("gaian-retire")
        assert isinstance(record, ArchivalRecord)
        assert record.gaian_id == "gaian-retire"
        assert record.archive_id != ""

    def test_archive_record_is_immutable(self, engine, lifecycle_machine):
        engine.retire(
            gaian_id="gaian-retire",
            condition=RetirementCondition.GAIAN_VOLITION,
            initiated_by="gaian-retire",
            justification="j",
            steward_id="s",
            lifecycle_machine=lifecycle_machine,
        )
        _RETIRED_AT["gaian-retire"] = datetime.now(timezone.utc) - timedelta(days=181)
        record = engine.archive("gaian-retire")
        with pytest.raises((AttributeError, TypeError)):
            record.gaian_id = "tampered"

    def test_archive_raises_for_unknown_gaian(self, engine):
        with pytest.raises(ValueError, match="no retirement record"):
            engine.archive("no-such-gaian")

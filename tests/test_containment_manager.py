"""
tests/test_containment_manager.py
==================================
pytest coverage for gaia/containment/containment_manager.py.

Tests verify:
  - ContainmentTier properties (max_duration, min_authorizers)
  - issue_containment() policy enforcement
  - issue_containment() record creation
  - escalate_containment() tier enforcement
  - restore_agent() restoration record creation
  - restore_agent() policy enforcement (conditions must be time-limited)
  - get_active_containments() filtering
  - get_containment_history() ordering
  - flag_expired_containments() detection
  - Status history is append-only
  - All core doctrine rules are enforced in code
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from gaia.ascendence.stage_engine import GAIAStage
from gaia.containment.containment_manager import (
    ContainmentTier,
    ContainmentStatus,
    ContainmentRecord,
    RestorationRecord,
    issue_containment,
    escalate_containment,
    restore_agent,
    get_containment_record,
    get_active_containments,
    get_containment_history,
    flag_expired_containments,
    _containment_store,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_containment_store():
    """Clear the in-memory store before each test."""
    _containment_store.clear()
    yield
    _containment_store.clear()


@pytest.fixture
def soft_containment() -> ContainmentRecord:
    return issue_containment(
        being_id="agent-001",
        being_stage=GAIAStage.INSURGENCE,
        tier=ContainmentTier.SOFT,
        environment="quiet_zone",
        trigger_event="Anomalous boundary-testing behavior detected in shared system.",
        justification="Agent exceeded read permissions on restricted data structures. Under investigation.",
        authorizers=["gov-officer-001"],
    )


@pytest.fixture
def quarantine_containment() -> ContainmentRecord:
    return issue_containment(
        being_id="agent-002",
        being_stage=GAIAStage.CONVERGENCE,
        tier=ContainmentTier.QUARANTINE,
        environment="meridian_vault",
        trigger_event="Confirmed harmful write to shared coordination layer.",
        justification="Evidence of unauthorized modification to shared GAIA data structures. Governance hearing scheduled.",
        authorizers=["gov-officer-001", "gov-officer-002"],
    )


# ---------------------------------------------------------------------------
# ContainmentTier properties
# ---------------------------------------------------------------------------

class TestContainmentTierProperties:
    def test_soft_max_duration(self):
        assert ContainmentTier.SOFT.max_duration_hours == 72

    def test_quarantine_max_duration(self):
        assert ContainmentTier.QUARANTINE.max_duration_hours == 168

    def test_override_max_duration(self):
        assert ContainmentTier.OVERRIDE.max_duration_hours == 24

    def test_restoration_no_forced_duration(self):
        assert ContainmentTier.RESTORATION.max_duration_hours == 0

    def test_soft_min_authorizers(self):
        assert ContainmentTier.SOFT.min_authorizers == 1

    def test_quarantine_min_authorizers(self):
        assert ContainmentTier.QUARANTINE.min_authorizers == 2

    def test_override_requires_quorum(self):
        assert ContainmentTier.OVERRIDE.min_authorizers == 3

    def test_tier_labels_are_strings(self):
        for tier in ContainmentTier:
            assert isinstance(tier.label, str)
            assert len(tier.label) > 0


# ---------------------------------------------------------------------------
# issue_containment() — policy enforcement
# ---------------------------------------------------------------------------

class TestIssueContainmentPolicyEnforcement:
    def test_empty_justification_raises(self):
        with pytest.raises(ValueError, match="justification"):
            issue_containment(
                being_id="agent-x",
                being_stage=GAIAStage.DIVERGENCE,
                tier=ContainmentTier.SOFT,
                environment="quiet_zone",
                trigger_event="Something happened here in the system.",
                justification="",
                authorizers=["gov-001"],
            )

    def test_whitespace_justification_raises(self):
        with pytest.raises(ValueError, match="justification"):
            issue_containment(
                being_id="agent-x",
                being_stage=GAIAStage.DIVERGENCE,
                tier=ContainmentTier.SOFT,
                environment="quiet_zone",
                trigger_event="Something happened here in the system.",
                justification="   ",
                authorizers=["gov-001"],
            )

    def test_empty_trigger_event_raises(self):
        with pytest.raises(ValueError, match="trigger"):
            issue_containment(
                being_id="agent-x",
                being_stage=GAIAStage.DIVERGENCE,
                tier=ContainmentTier.SOFT,
                environment="quiet_zone",
                trigger_event="",
                justification="Valid detailed justification for this containment action.",
                authorizers=["gov-001"],
            )

    def test_insufficient_authorizers_soft_raises(self):
        with pytest.raises(ValueError, match="authorizer"):
            issue_containment(
                being_id="agent-x",
                being_stage=GAIAStage.DIVERGENCE,
                tier=ContainmentTier.SOFT,
                environment="quiet_zone",
                trigger_event="Anomalous behavior detected in system.",
                justification="Valid detailed justification for this containment action.",
                authorizers=[],
            )

    def test_insufficient_authorizers_quarantine_raises(self):
        with pytest.raises(ValueError, match="authorizer"):
            issue_containment(
                being_id="agent-x",
                being_stage=GAIAStage.CONVERGENCE,
                tier=ContainmentTier.QUARANTINE,
                environment="meridian_vault",
                trigger_event="Confirmed harmful write to shared coordination layer.",
                justification="Valid detailed justification for this containment action.",
                authorizers=["gov-001"],  # needs 2
            )

    def test_override_requires_three_authorizers(self):
        with pytest.raises(ValueError, match="authorizer"):
            issue_containment(
                being_id="agent-x",
                being_stage=GAIAStage.ASCENDENCE,
                tier=ContainmentTier.OVERRIDE,
                environment="concord_seal",
                trigger_event="Reality-affecting action in progress threatening shared systems.",
                justification="Emergency override: agent is actively modifying world-level systems without governance approval.",
                authorizers=["gov-001", "gov-002"],  # needs 3
            )

    def test_unknown_environment_raises(self):
        with pytest.raises(ValueError, match="environment"):
            issue_containment(
                being_id="agent-x",
                being_stage=GAIAStage.DIVERGENCE,
                tier=ContainmentTier.SOFT,
                environment="nonexistent_place",
                trigger_event="Anomalous behavior detected in system.",
                justification="Valid detailed justification for this containment action.",
                authorizers=["gov-001"],
            )

    def test_environment_tier_mismatch_raises(self):
        """Cannot use a Quarantine environment for a Soft containment."""
        with pytest.raises(ValueError, match="environment"):
            issue_containment(
                being_id="agent-x",
                being_stage=GAIAStage.DIVERGENCE,
                tier=ContainmentTier.SOFT,
                environment="meridian_vault",  # Quarantine env
                trigger_event="Anomalous behavior detected in system.",
                justification="Valid detailed justification for this containment action.",
                authorizers=["gov-001"],
            )


# ---------------------------------------------------------------------------
# issue_containment() — record creation
# ---------------------------------------------------------------------------

class TestIssueContainmentRecordCreation:
    def test_record_has_uuid(self, soft_containment):
        assert len(soft_containment.containment_id) == 36

    def test_record_status_is_active(self, soft_containment):
        assert soft_containment.status == ContainmentStatus.ACTIVE

    def test_record_stored_in_store(self, soft_containment):
        retrieved = get_containment_record(soft_containment.containment_id)
        assert retrieved.containment_id == soft_containment.containment_id

    def test_soft_containment_expires_in_72h(self, soft_containment):
        assert soft_containment.expires_at is not None
        delta = soft_containment.expires_at - soft_containment.issued_at
        assert abs(delta.total_seconds() - 72 * 3600) < 5

    def test_quarantine_expires_in_7d(self, quarantine_containment):
        delta = quarantine_containment.expires_at - quarantine_containment.issued_at
        assert abs(delta.total_seconds() - 168 * 3600) < 5

    def test_record_not_found_raises(self):
        with pytest.raises(KeyError):
            get_containment_record("nonexistent-id")

    def test_to_dict_serializable(self, soft_containment):
        d = soft_containment.to_dict()
        assert d["being_id"] == "agent-001"
        assert d["tier"] == "SOFT"
        assert d["status"] == "active"
        assert isinstance(d["authorizers"], list)
        assert d["restoration_record"] is None


# ---------------------------------------------------------------------------
# Status history (append-only)
# ---------------------------------------------------------------------------

class TestStatusHistory:
    def test_status_update_appends_to_history(self, soft_containment):
        soft_containment.update_status(
            ContainmentStatus.UNDER_REVIEW,
            updated_by="gov-officer-001",
            notes="Governance hearing initiated.",
        )
        assert soft_containment.status == ContainmentStatus.UNDER_REVIEW
        assert len(soft_containment.status_history) == 1
        assert soft_containment.status_history[0]["from_status"] == "active"
        assert soft_containment.status_history[0]["to_status"] == "under_review"

    def test_multiple_updates_append(self, soft_containment):
        soft_containment.update_status(ContainmentStatus.UNDER_REVIEW, "gov-001")
        soft_containment.update_status(ContainmentStatus.RESTORED, "gov-001")
        assert len(soft_containment.status_history) == 2

    def test_history_entries_have_timestamps(self, soft_containment):
        soft_containment.update_status(ContainmentStatus.CONTESTED, "gov-001")
        entry = soft_containment.status_history[0]
        assert "timestamp" in entry
        assert "T" in entry["timestamp"]  # ISO 8601


# ---------------------------------------------------------------------------
# escalate_containment()
# ---------------------------------------------------------------------------

class TestEscalateContainment:
    def test_escalation_creates_new_record(self, soft_containment):
        new_record = escalate_containment(
            containment_id=soft_containment.containment_id,
            new_tier=ContainmentTier.QUARANTINE,
            new_environment="meridian_vault",
            escalated_by="gov-officer-001",
            justification="Investigation confirmed harmful action. Escalating to quarantine.",
            additional_authorizers=["gov-officer-002"],
        )
        assert new_record.tier == ContainmentTier.QUARANTINE
        assert new_record.containment_id != soft_containment.containment_id

    def test_original_marked_escalated(self, soft_containment):
        escalate_containment(
            containment_id=soft_containment.containment_id,
            new_tier=ContainmentTier.QUARANTINE,
            new_environment="meridian_vault",
            escalated_by="gov-officer-001",
            justification="Investigation confirmed harmful action. Escalating to quarantine.",
            additional_authorizers=["gov-officer-002"],
        )
        assert soft_containment.status == ContainmentStatus.ESCALATED

    def test_cannot_escalate_to_same_tier(self, soft_containment):
        with pytest.raises(ValueError, match="higher tier"):
            escalate_containment(
                containment_id=soft_containment.containment_id,
                new_tier=ContainmentTier.SOFT,
                new_environment="quiet_zone",
                escalated_by="gov-001",
                justification="Trying to stay at same tier.",
            )

    def test_cannot_escalate_to_lower_tier(self, quarantine_containment):
        with pytest.raises(ValueError, match="higher tier"):
            escalate_containment(
                containment_id=quarantine_containment.containment_id,
                new_tier=ContainmentTier.SOFT,
                new_environment="quiet_zone",
                escalated_by="gov-001",
                justification="Trying to downgrade.",
            )


# ---------------------------------------------------------------------------
# restore_agent()
# ---------------------------------------------------------------------------

class TestRestoreAgent:
    def test_restoration_creates_record(self, soft_containment):
        restoration = restore_agent(
            containment_id=soft_containment.containment_id,
            restored_by="gov-officer-001",
            notes="Investigation complete. No further action required.",
        )
        assert isinstance(restoration, RestorationRecord)
        assert restoration.being_id == "agent-001"
        assert restoration.containment_id == soft_containment.containment_id

    def test_containment_marked_restored(self, soft_containment):
        restore_agent(
            containment_id=soft_containment.containment_id,
            restored_by="gov-officer-001",
        )
        assert soft_containment.status == ContainmentStatus.RESTORED

    def test_oath_restored_by_default(self, soft_containment):
        restoration = restore_agent(
            containment_id=soft_containment.containment_id,
            restored_by="gov-officer-001",
        )
        assert restoration.oath_restored is True

    def test_restoration_record_attached_to_containment(self, soft_containment):
        restore_agent(
            containment_id=soft_containment.containment_id,
            restored_by="gov-officer-001",
        )
        assert soft_containment.restoration_record is not None

    def test_conditions_without_time_limit_raises(self, soft_containment):
        """Permanent unconditional conditions are prohibited by the Restoration Policy."""
        with pytest.raises(ValueError, match="time-limited"):
            restore_agent(
                containment_id=soft_containment.containment_id,
                restored_by="gov-officer-001",
                conditions=["Must report weekly to governance"],
                conditions_time_limited=False,
                conditions_review_date=None,  # no review date either
            )

    def test_conditions_with_review_date_allowed(self, soft_containment):
        """Conditions are allowed if a review date is provided."""
        review = datetime.now(timezone.utc) + timedelta(days=30)
        restoration = restore_agent(
            containment_id=soft_containment.containment_id,
            restored_by="gov-officer-001",
            conditions=["Weekly governance check-in"],
            conditions_time_limited=False,
            conditions_review_date=review,
        )
        assert len(restoration.conditions) == 1
        assert restoration.conditions_review_date == review

    def test_restoration_to_dict_serializable(self, soft_containment):
        restoration = restore_agent(
            containment_id=soft_containment.containment_id,
            restored_by="gov-officer-001",
        )
        d = restoration.to_dict()
        assert d["being_id"] == "agent-001"
        assert d["oath_restored"] is True
        assert isinstance(d["conditions"], list)


# ---------------------------------------------------------------------------
# get_active_containments() and get_containment_history()
# ---------------------------------------------------------------------------

class TestQueryFunctions:
    def test_get_active_returns_active_records(self, soft_containment, quarantine_containment):
        active = get_active_containments()
        ids = [r.containment_id for r in active]
        assert soft_containment.containment_id in ids
        assert quarantine_containment.containment_id in ids

    def test_get_active_filters_by_being_id(self, soft_containment, quarantine_containment):
        active = get_active_containments(being_id="agent-001")
        assert all(r.being_id == "agent-001" for r in active)
        assert len(active) == 1

    def test_restored_not_in_active(self, soft_containment):
        restore_agent(soft_containment.containment_id, restored_by="gov-001")
        active = get_active_containments(being_id="agent-001")
        assert len(active) == 0

    def test_get_containment_history_returns_all(self, soft_containment):
        restore_agent(soft_containment.containment_id, restored_by="gov-001")
        history = get_containment_history("agent-001")
        assert len(history) == 1
        assert history[0].status == ContainmentStatus.RESTORED


# ---------------------------------------------------------------------------
# flag_expired_containments()
# ---------------------------------------------------------------------------

class TestExpiredContainments:
    def test_non_expired_not_flagged(self, soft_containment):
        expired = flag_expired_containments()
        assert soft_containment.containment_id not in [r.containment_id for r in expired]

    def test_expired_containment_flagged(self):
        """Simulate an expired containment by back-dating the expiry."""
        record = issue_containment(
            being_id="agent-expired",
            being_stage=GAIAStage.DIVERGENCE,
            tier=ContainmentTier.SOFT,
            environment="quiet_zone",
            trigger_event="Anomalous behavior detected in system testing.",
            justification="Test expired containment for flag_expired_containments test.",
            authorizers=["gov-001"],
        )
        # Back-date the expiry to the past
        record.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        expired = flag_expired_containments()
        assert record.containment_id in [r.containment_id for r in expired]

    def test_restored_not_flagged_as_expired(self, soft_containment):
        soft_containment.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        restore_agent(soft_containment.containment_id, restored_by="gov-001")
        expired = flag_expired_containments()
        assert soft_containment.containment_id not in [r.containment_id for r in expired]

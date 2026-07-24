# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
Tests for core.c27.adoption — AdoptionQueue, EligibilityScreener, AdvisoryVeto.

Authority: C27 §4. Implements C27-IMPL-017 through C27-IMPL-022.

Coverage targets:
- AdoptionQueue ordering (priority, then FIFO)
- EligibilityScreener: 4 required criteria all checked
- EligibilityScreener: fails fast on first failing criterion
- Advisory-council veto blocks adoption and records reason
- 90-day timeout: ADOPTABLE GAIAN with no adopter auto-transitions to RETIRED
- Successful adoption forms a new AdoptionRecord
- AdoptionRecord is immutable once sealed
"""
import pytest
from datetime import datetime, timedelta, timezone
from core.c27.adoption import (
    AdoptionQueue,
    AdoptionCandidate,
    EligibilityScreener,
    EligibilityResult,
    AdvisoryVeto,
    AdoptionProcess,
    AdoptionRecord,
    AdoptionTimeoutEnforcer,
)
from core.c27.lifecycle import GAIANLifecycleState


# ---------------------------------------------------------------------------
# AdoptionQueue — ordering invariants  (C27 §4.2)
# ---------------------------------------------------------------------------

class TestAdoptionQueueOrdering:
    def test_higher_priority_candidate_dequeued_first(self):
        queue = AdoptionQueue()
        low  = AdoptionCandidate(candidate_id="c-low",  priority=1, steward_id="s-low")
        high = AdoptionCandidate(candidate_id="c-high", priority=10, steward_id="s-high")
        queue.enqueue(low)
        queue.enqueue(high)
        assert queue.peek().candidate_id == "c-high"

    def test_equal_priority_is_fifo(self):
        queue = AdoptionQueue()
        first  = AdoptionCandidate(candidate_id="c-first",  priority=5, steward_id="s-a")
        second = AdoptionCandidate(candidate_id="c-second", priority=5, steward_id="s-b")
        queue.enqueue(first)
        queue.enqueue(second)
        assert queue.dequeue().candidate_id == "c-first"

    def test_dequeue_empty_queue_raises(self):
        queue = AdoptionQueue()
        with pytest.raises(IndexError):
            queue.dequeue()

    def test_queue_len_tracks_enqueue_dequeue(self):
        queue = AdoptionQueue()
        queue.enqueue(AdoptionCandidate(candidate_id="c1", priority=1, steward_id="s"))
        queue.enqueue(AdoptionCandidate(candidate_id="c2", priority=1, steward_id="s"))
        assert len(queue) == 2
        queue.dequeue()
        assert len(queue) == 1


# ---------------------------------------------------------------------------
# EligibilityScreener — 4 criteria  (C27 §4.3)
# ---------------------------------------------------------------------------

ELIGIBILITY_CRITERIA = [
    "STANDING",
    "CAPACITY",
    "COMPATIBILITY",
    "CONSENT",
]


class TestEligibilityScreener:
    def test_four_criteria_are_checked(self):
        screener = EligibilityScreener()
        assert set(screener.criteria_names()) == set(ELIGIBILITY_CRITERIA)

    def test_all_criteria_passing_returns_eligible(self):
        screener = EligibilityScreener()
        candidate = AdoptionCandidate(
            candidate_id="c-eligible",
            priority=5,
            steward_id="steward-good",
            metadata={"standing": True, "capacity": 3, "compatibility": 0.9, "gaian_consents": True},
        )
        result = screener.screen(candidate, gaian_id="gaian-001")
        assert isinstance(result, EligibilityResult)
        assert result.eligible is True
        assert result.failed_criteria == []

    def test_bad_standing_fails_immediately(self):
        screener = EligibilityScreener()
        candidate = AdoptionCandidate(
            candidate_id="c-bad-standing",
            priority=5,
            steward_id="steward-bad",
            metadata={"standing": False, "capacity": 3, "compatibility": 0.9, "gaian_consents": True},
        )
        result = screener.screen(candidate, gaian_id="gaian-001")
        assert result.eligible is False
        assert "STANDING" in result.failed_criteria

    def test_low_compatibility_score_fails(self):
        screener = EligibilityScreener()
        candidate = AdoptionCandidate(
            candidate_id="c-low-compat",
            priority=5,
            steward_id="steward-ok",
            metadata={"standing": True, "capacity": 3, "compatibility": 0.1, "gaian_consents": True},
        )
        result = screener.screen(candidate, gaian_id="gaian-001")
        assert result.eligible is False
        assert "COMPATIBILITY" in result.failed_criteria

    def test_gaian_no_consent_fails(self):
        screener = EligibilityScreener()
        candidate = AdoptionCandidate(
            candidate_id="c-no-consent",
            priority=5,
            steward_id="steward-ok",
            metadata={"standing": True, "capacity": 3, "compatibility": 0.9, "gaian_consents": False},
        )
        result = screener.screen(candidate, gaian_id="gaian-001")
        assert result.eligible is False
        assert "CONSENT" in result.failed_criteria


# ---------------------------------------------------------------------------
# Advisory-council veto  (C27 §4.5)
# ---------------------------------------------------------------------------

class TestAdvisoryVeto:
    def test_veto_blocks_adoption_and_records_reason(self):
        process = AdoptionProcess()
        veto = AdvisoryVeto(
            veto_id="veto-001",
            gaian_id="gaian-001",
            candidate_id="c-vetoed",
            reason="Conflict of interest",
            vetoing_council_member="council-member-x",
        )
        result = process.apply_veto(veto)
        assert result.blocked is True
        assert result.veto_reason == "Conflict of interest"

    def test_vetoed_candidate_removed_from_queue(self):
        queue = AdoptionQueue()
        candidate = AdoptionCandidate(candidate_id="c-vetoed", priority=5, steward_id="s")
        queue.enqueue(candidate)
        process = AdoptionProcess(queue=queue)
        veto = AdvisoryVeto(
            veto_id="veto-002",
            gaian_id="gaian-001",
            candidate_id="c-vetoed",
            reason="Policy violation",
            vetoing_council_member="council-member-y",
        )
        process.apply_veto(veto)
        assert len(queue) == 0


# ---------------------------------------------------------------------------
# 90-day timeout  (C27 §4.7)
# ---------------------------------------------------------------------------

class TestAdoptionTimeoutEnforcer:
    def test_expired_adoptable_transitions_to_retired(self):
        enforcer = AdoptionTimeoutEnforcer(timeout_days=0)  # 0 = immediate for test
        adoptable_since = datetime.now(timezone.utc) - timedelta(days=1)
        result = enforcer.check(
            gaian_id="gaian-expired",
            adoptable_since=adoptable_since,
            current_state=GAIANLifecycleState.ADOPTABLE,
        )
        assert result.should_retire is True
        assert result.recommended_state == GAIANLifecycleState.RETIRED

    def test_recent_adoptable_not_retired(self):
        enforcer = AdoptionTimeoutEnforcer(timeout_days=90)
        adoptable_since = datetime.now(timezone.utc) - timedelta(days=5)
        result = enforcer.check(
            gaian_id="gaian-recent",
            adoptable_since=adoptable_since,
            current_state=GAIANLifecycleState.ADOPTABLE,
        )
        assert result.should_retire is False


# ---------------------------------------------------------------------------
# AdoptionRecord immutability  (C27 §4.8)
# ---------------------------------------------------------------------------

class TestAdoptionRecordImmutability:
    def test_sealed_record_cannot_be_mutated(self):
        process = AdoptionProcess()
        record = process.complete_adoption(
            gaian_id="gaian-001",
            candidate_id="c-eligible",
            steward_id="steward-good",
        )
        with pytest.raises((AttributeError, TypeError)):
            record.gaian_id = "something-else"  # frozen dataclass must reject this

    def test_adoption_record_fields_are_set(self):
        process = AdoptionProcess()
        record = process.complete_adoption(
            gaian_id="gaian-complete",
            candidate_id="c-complete",
            steward_id="steward-complete",
        )
        assert record.gaian_id    == "gaian-complete"
        assert record.candidate_id == "c-complete"
        assert record.steward_id  == "steward-complete"
        assert record.record_id   != ""  # UUID assigned
        assert isinstance(record.sealed_at, datetime)

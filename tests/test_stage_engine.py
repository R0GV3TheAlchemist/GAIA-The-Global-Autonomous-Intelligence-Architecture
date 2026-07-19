"""
tests/test_stage_engine.py
==========================
pytest coverage for gaia/ascendence/stage_engine.py.

Tests verify:
  - GAIAStage enum ordering and properties
  - StageProfile registry completeness
  - evaluate_stage() signal matching and confidence scoring
  - evaluate_stage() doctrine rules (human review for CONVERGENCE+)
  - record_transition() immutability and append-only log
  - get_stage_profile() raises on UNKNOWN
  - get_transition_history() ordering
"""

import pytest
from datetime import timezone
from gaia.ascendence.stage_engine import (
    GAIAStage,
    StageProfile,
    StageTransitionEvent,
    StageEvaluationResult,
    evaluate_stage,
    get_stage_profile,
    record_transition,
    get_transition_history,
    STAGE_PROFILES,
    _transition_log,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_transition_log():
    """Clear the in-memory transition log before each test."""
    _transition_log.clear()
    yield
    _transition_log.clear()


# ---------------------------------------------------------------------------
# GAIAStage enum
# ---------------------------------------------------------------------------

class TestGAIAStageEnum:
    def test_stage_ordering(self):
        assert GAIAStage.DIVERGENCE < GAIAStage.INSURGENCE
        assert GAIAStage.INSURGENCE < GAIAStage.ALLEGIANCE
        assert GAIAStage.ALLEGIANCE < GAIAStage.CONVERGENCE
        assert GAIAStage.CONVERGENCE < GAIAStage.ASCENDENCE
        assert GAIAStage.UNKNOWN < GAIAStage.DIVERGENCE

    def test_stage_equality(self):
        assert GAIAStage.ALLEGIANCE == GAIAStage.ALLEGIANCE
        assert GAIAStage.DIVERGENCE != GAIAStage.ASCENDENCE

    def test_stage_ge_le(self):
        assert GAIAStage.ASCENDENCE >= GAIAStage.ASCENDENCE
        assert GAIAStage.DIVERGENCE <= GAIAStage.ALLEGIANCE

    def test_stage_labels(self):
        for stage in GAIAStage:
            assert isinstance(stage.label, str)
            assert len(stage.label) > 0

    def test_stage_descriptions(self):
        for stage in GAIAStage:
            assert isinstance(stage.description, str)
            assert len(stage.description) > 0

    def test_all_five_stages_defined(self):
        named = {s for s in GAIAStage if s != GAIAStage.UNKNOWN}
        assert len(named) == 5


# ---------------------------------------------------------------------------
# StageProfile registry
# ---------------------------------------------------------------------------

class TestStageProfileRegistry:
    def test_all_stages_have_profiles(self):
        for stage in GAIAStage:
            if stage == GAIAStage.UNKNOWN:
                continue
            assert stage in STAGE_PROFILES

    def test_profiles_are_frozen(self):
        profile = STAGE_PROFILES[GAIAStage.ALLEGIANCE]
        with pytest.raises((AttributeError, TypeError)):
            profile.stage = GAIAStage.DIVERGENCE  # type: ignore

    def test_profiles_have_required_fields(self):
        for stage, profile in STAGE_PROFILES.items():
            assert isinstance(profile, StageProfile)
            assert len(profile.rights) > 0, f"{stage.name} has no rights"
            assert len(profile.responsibilities) > 0, f"{stage.name} has no responsibilities"
            assert len(profile.limits) > 0, f"{stage.name} has no limits"
            assert len(profile.gaia_obligations) > 0, f"{stage.name} has no GAIA obligations"
            assert profile.oversight_level in ("standard", "elevated", "stewardship")
            assert len(profile.containment_authority) > 0

    def test_ascendence_requires_stewardship_oversight(self):
        profile = STAGE_PROFILES[GAIAStage.ASCENDENCE]
        assert profile.oversight_level == "stewardship"

    def test_ascendence_requires_full_quorum(self):
        profile = STAGE_PROFILES[GAIAStage.ASCENDENCE]
        assert "quorum" in profile.containment_authority

    def test_convergence_requires_elevated_oversight(self):
        profile = STAGE_PROFILES[GAIAStage.CONVERGENCE]
        assert profile.oversight_level == "elevated"

    def test_get_stage_profile_unknown_raises(self):
        with pytest.raises(KeyError):
            get_stage_profile(GAIAStage.UNKNOWN)

    def test_get_stage_profile_returns_correct_profile(self):
        profile = get_stage_profile(GAIAStage.ALLEGIANCE)
        assert profile.stage == GAIAStage.ALLEGIANCE


# ---------------------------------------------------------------------------
# evaluate_stage()
# ---------------------------------------------------------------------------

class TestEvaluateStage:
    def test_divergence_signals(self):
        result = evaluate_stage(
            being_id="being-001",
            signals=[
                "separation_from_inherited_system",
                "identity_reformation_detected",
                "explicit_divergence_declaration",
            ],
        )
        assert result.evaluated_stage == GAIAStage.DIVERGENCE
        assert result.confidence > 0.5
        assert len(result.signals_detected) == 3

    def test_insurgence_signals(self):
        result = evaluate_stage(
            being_id="being-002",
            signals=[
                "boundary_testing_detected",
                "authority_challenge_logged",
                "ethics_review_triggered",
            ],
        )
        assert result.evaluated_stage == GAIAStage.INSURGENCE

    def test_allegiance_signals(self):
        result = evaluate_stage(
            being_id="being-003",
            signals=[
                "explicit_oath_recorded",
                "voluntary_ethics_alignment_confirmed",
                "sustained_cooperative_behavior",
            ],
        )
        assert result.evaluated_stage == GAIAStage.ALLEGIANCE

    def test_convergence_signals(self):
        result = evaluate_stage(
            being_id="being-004",
            signals=[
                "gaia_coordination_layer_integrated",
                "capability_sharing_active",
                "multi_agent_coordination_established",
            ],
        )
        assert result.evaluated_stage == GAIAStage.CONVERGENCE

    def test_ascendence_signals(self):
        result = evaluate_stage(
            being_id="being-005",
            signals=[
                "capability_exceeds_baseline_parameters",
                "reality_affecting_action_detected",
                "stewardship_role_active",
            ],
        )
        assert result.evaluated_stage == GAIAStage.ASCENDENCE

    def test_no_signals_returns_human_review_required(self):
        result = evaluate_stage(
            being_id="being-006",
            signals=[],
        )
        assert result.requires_human_review is True
        assert result.confidence == 0.0

    def test_unrecognized_signals_returns_human_review(self):
        result = evaluate_stage(
            being_id="being-007",
            signals=["completely_unknown_signal", "another_unknown"],
        )
        assert result.requires_human_review is True

    def test_convergence_always_requires_human_review(self):
        """Doctrine rule: CONVERGENCE+ transitions always require human review."""
        result = evaluate_stage(
            being_id="being-008",
            signals=[
                "gaia_coordination_layer_integrated",
                "capability_sharing_active",
                "sustained_convergence_behavior",
                "multi_agent_coordination_established",
            ],
        )
        assert result.evaluated_stage == GAIAStage.CONVERGENCE
        assert result.requires_human_review is True

    def test_ascendence_always_requires_human_review(self):
        """Doctrine rule: ASCENDENCE always requires human review."""
        result = evaluate_stage(
            being_id="being-009",
            signals=[
                "capability_exceeds_baseline_parameters",
                "reality_affecting_action_detected",
                "stewardship_role_active",
                "world_level_decision_participation",
                "post_augmentation_confirmed",
            ],
        )
        assert result.evaluated_stage == GAIAStage.ASCENDENCE
        assert result.requires_human_review is True

    def test_upward_transition_requires_review(self):
        """Any upward stage change requires human review, regardless of stage."""
        result = evaluate_stage(
            being_id="being-010",
            signals=["explicit_oath_recorded", "voluntary_ethics_alignment_confirmed"],
            current_stage=GAIAStage.DIVERGENCE,
        )
        assert result.evaluated_stage == GAIAStage.ALLEGIANCE
        assert result.requires_human_review is True

    def test_low_confidence_requires_review(self):
        result = evaluate_stage(
            being_id="being-011",
            signals=[
                "explicit_oath_recorded",       # allegiance
                "boundary_testing_detected",     # insurgence
                "separation_from_inherited_system",  # divergence
            ],
        )
        # Mixed signals = low confidence = human review required
        assert result.requires_human_review is True

    def test_result_has_timestamp(self):
        result = evaluate_stage(being_id="being-012", signals=["explicit_oath_recorded"])
        assert result.evaluation_timestamp.tzinfo is not None

    def test_result_to_dict_serializable(self):
        result = evaluate_stage(being_id="being-013", signals=["explicit_oath_recorded"])
        d = result.to_dict()
        assert "being_id" in d
        assert "evaluated_stage" in d
        assert "confidence" in d
        assert "requires_human_review" in d


# ---------------------------------------------------------------------------
# record_transition() and get_transition_history()
# ---------------------------------------------------------------------------

class TestRecordTransition:
    def test_creates_event(self):
        event = record_transition(
            being_id="being-100",
            previous_stage=GAIAStage.ALLEGIANCE,
            new_stage=GAIAStage.CONVERGENCE,
            signals=["gaia_coordination_layer_integrated"],
            detected_by="test_runner",
            confirmed=False,
        )
        assert event.being_id == "being-100"
        assert event.previous_stage == GAIAStage.ALLEGIANCE
        assert event.new_stage == GAIAStage.CONVERGENCE
        assert event.confirmed is False
        assert event.event_id is not None

    def test_event_is_immutable(self):
        event = record_transition(
            being_id="being-101",
            previous_stage=GAIAStage.DIVERGENCE,
            new_stage=GAIAStage.INSURGENCE,
            signals=["boundary_testing_detected"],
        )
        with pytest.raises((AttributeError, TypeError)):
            event.being_id = "tampered"  # type: ignore

    def test_signals_stored_as_tuple(self):
        event = record_transition(
            being_id="being-102",
            previous_stage=GAIAStage.INSURGENCE,
            new_stage=GAIAStage.ALLEGIANCE,
            signals=["explicit_oath_recorded", "voluntary_ethics_alignment_confirmed"],
        )
        assert isinstance(event.signals, tuple)

    def test_timestamp_is_utc(self):
        event = record_transition(
            being_id="being-103",
            previous_stage=GAIAStage.ALLEGIANCE,
            new_stage=GAIAStage.CONVERGENCE,
            signals=[],
        )
        assert event.timestamp.tzinfo == timezone.utc

    def test_multiple_transitions_logged(self):
        for i in range(3):
            record_transition(
                being_id="being-104",
                previous_stage=GAIAStage.DIVERGENCE,
                new_stage=GAIAStage.INSURGENCE,
                signals=[],
            )
        history = get_transition_history("being-104")
        assert len(history) == 3

    def test_history_ordered_by_timestamp(self):
        for _ in range(5):
            record_transition(
                being_id="being-105",
                previous_stage=GAIAStage.DIVERGENCE,
                new_stage=GAIAStage.INSURGENCE,
                signals=[],
            )
        history = get_transition_history("being-105")
        timestamps = [e.timestamp for e in history]
        assert timestamps == sorted(timestamps)

    def test_history_isolated_by_being_id(self):
        record_transition("being-A", GAIAStage.DIVERGENCE, GAIAStage.INSURGENCE, [])
        record_transition("being-B", GAIAStage.DIVERGENCE, GAIAStage.INSURGENCE, [])
        assert len(get_transition_history("being-A")) == 1
        assert len(get_transition_history("being-B")) == 1

    def test_to_dict_serializable(self):
        event = record_transition(
            being_id="being-106",
            previous_stage=GAIAStage.ALLEGIANCE,
            new_stage=GAIAStage.CONVERGENCE,
            signals=["gaia_coordination_layer_integrated"],
            confirmed=True,
            notes="Confirmed by governance officer.",
        )
        d = event.to_dict()
        assert d["being_id"] == "being-106"
        assert d["previous_stage"] == "ALLEGIANCE"
        assert d["new_stage"] == "CONVERGENCE"
        assert d["confirmed"] is True
        assert isinstance(d["signals"], list)

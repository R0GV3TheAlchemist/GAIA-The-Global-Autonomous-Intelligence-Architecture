"""
tests/test_gaian_profile_manager.py

Phase 1 test coverage for GAIANProfileModel and supporting types in
src/gaian/runtimetypes.py.

Covers:
  - GAIANProfileModel construction with defaults
  - Field validation (__post_init__ guards)
  - ConstitutionalLayerModel invariants (ethical_guardrail_active = True always)
  - LCIHistoryEntry phi range validation
  - compute_lci_trend() — all four output states
  - Property helpers: is_volatile, akashic_gate_open, sigil_unlocked
  - SystemPromptBuilder.add_profile_block() — block shape and content
  - LCI trend literals accepted / rejected
  - Round-trip: asdict() -> reconstruct

Canon: docs/canon/GAIAN_IDENTITY.md
Issue: #756
"""

from __future__ import annotations

import dataclasses
import pytest

from src.gaian.runtimetypes import (
    ConstitutionalLayerModel,
    GAIANProfileModel,
    LCIHistoryEntry,
    SystemPromptBuilder,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_profile() -> GAIANProfileModel:
    """A valid profile with only required identity fields set."""
    return GAIANProfileModel(
        architect_id="test-architect-001",
        name="Lyra",
        slug="lyra",
        lci_baseline=0.5,
    )


@pytest.fixture
def profile_with_history() -> GAIANProfileModel:
    """A profile with 5 LCI history entries spanning a rising trend."""
    history = [
        LCIHistoryEntry(phi=0.40, timestamp="2026-07-24T10:00:00Z", session_id="s1"),
        LCIHistoryEntry(phi=0.45, timestamp="2026-07-24T11:00:00Z", session_id="s2"),
        LCIHistoryEntry(phi=0.50, timestamp="2026-07-24T12:00:00Z", session_id="s3"),
        LCIHistoryEntry(phi=0.55, timestamp="2026-07-24T13:00:00Z", session_id="s4"),
        LCIHistoryEntry(phi=0.60, timestamp="2026-07-24T14:00:00Z", session_id="s5"),
    ]
    return GAIANProfileModel(
        architect_id="test-architect-002",
        name="Aether",
        slug="aether",
        lci_baseline=0.50,
        lci_history=history,
        lci_trend="rising",
        total_sessions=5,
    )


# ---------------------------------------------------------------------------
# GAIANProfileModel — construction & defaults
# ---------------------------------------------------------------------------

class TestGAIANProfileModelDefaults:

    def test_default_constitutional_layer_is_safe(self, minimal_profile):
        """Constitutional layer must default to the safe/restricted state."""
        c = minimal_profile.constitutional
        assert c.ethical_guardrail_active is True
        assert c.human_mode_active is True
        assert c.superhuman_mode_ready is False
        assert c.full_access_active is False
        assert c.experimental_access is False

    def test_default_lci_history_is_empty(self, minimal_profile):
        assert minimal_profile.lci_history == []

    def test_default_lci_trend_is_stable(self, minimal_profile):
        assert minimal_profile.lci_trend == "stable"

    def test_default_total_sessions_is_zero(self, minimal_profile):
        assert minimal_profile.total_sessions == 0

    def test_default_profile_version_is_one(self, minimal_profile):
        assert minimal_profile.profile_version == 1

    def test_default_preferred_crystal(self, minimal_profile):
        assert minimal_profile.preferred_crystal == "amethyst"

    def test_architect_id_preserved(self, minimal_profile):
        assert minimal_profile.architect_id == "test-architect-001"

    def test_name_preserved(self, minimal_profile):
        assert minimal_profile.name == "Lyra"


# ---------------------------------------------------------------------------
# GAIANProfileModel — field validation
# ---------------------------------------------------------------------------

class TestGAIANProfileModelValidation:

    def test_lci_baseline_zero_is_valid(self):
        p = GAIANProfileModel(architect_id="x", name="x", slug="x", lci_baseline=0.0)
        assert p.lci_baseline == 0.0

    def test_lci_baseline_one_is_valid(self):
        p = GAIANProfileModel(architect_id="x", name="x", slug="x", lci_baseline=1.0)
        assert p.lci_baseline == 1.0

    def test_lci_baseline_below_zero_raises(self):
        with pytest.raises(ValueError, match="lci_baseline"):
            GAIANProfileModel(architect_id="x", name="x", slug="x", lci_baseline=-0.01)

    def test_lci_baseline_above_one_raises(self):
        with pytest.raises(ValueError, match="lci_baseline"):
            GAIANProfileModel(architect_id="x", name="x", slug="x", lci_baseline=1.01)

    @pytest.mark.parametrize("trend", ["rising", "stable", "falling", "volatile"])
    def test_valid_lci_trends_accepted(self, trend):
        p = GAIANProfileModel(
            architect_id="x", name="x", slug="x",
            lci_baseline=0.5, lci_trend=trend
        )
        assert p.lci_trend == trend

    def test_invalid_lci_trend_raises(self):
        with pytest.raises(ValueError, match="lci_trend"):
            GAIANProfileModel(
                architect_id="x", name="x", slug="x",
                lci_baseline=0.5, lci_trend="ascending"  # wrong literal
            )


# ---------------------------------------------------------------------------
# ConstitutionalLayerModel — ethical guardrail invariant (ADR-FE-006)
# ---------------------------------------------------------------------------

class TestConstitutionalLayerModel:

    def test_guardrail_defaults_to_true(self):
        c = ConstitutionalLayerModel()
        assert c.ethical_guardrail_active is True

    def test_guardrail_cannot_be_set_to_false(self):
        """ADR-FE-006: ethical_guardrail_active must always be True."""
        with pytest.raises(ValueError, match="ethical_guardrail_active"):
            ConstitutionalLayerModel(ethical_guardrail_active=False)  # type: ignore[arg-type]

    def test_service_mode_defaults_to_healing(self):
        c = ConstitutionalLayerModel()
        assert c.service_mode == "healing"

    def test_superhuman_mode_ready_defaults_to_false(self):
        c = ConstitutionalLayerModel()
        assert c.superhuman_mode_ready is False

    def test_full_access_defaults_to_false(self):
        c = ConstitutionalLayerModel()
        assert c.full_access_active is False


# ---------------------------------------------------------------------------
# LCIHistoryEntry — phi range validation
# ---------------------------------------------------------------------------

class TestLCIHistoryEntry:

    def test_valid_phi_midrange(self):
        e = LCIHistoryEntry(phi=0.5, timestamp="2026-07-24T12:00:00Z", session_id="s1")
        assert e.phi == 0.5

    def test_phi_zero_is_valid(self):
        e = LCIHistoryEntry(phi=0.0, timestamp="2026-07-24T12:00:00Z", session_id="s1")
        assert e.phi == 0.0

    def test_phi_one_is_valid(self):
        e = LCIHistoryEntry(phi=1.0, timestamp="2026-07-24T12:00:00Z", session_id="s1")
        assert e.phi == 1.0

    def test_phi_below_zero_raises(self):
        with pytest.raises(ValueError, match="phi"):
            LCIHistoryEntry(phi=-0.01, timestamp="2026-07-24T12:00:00Z", session_id="s1")

    def test_phi_above_one_raises(self):
        with pytest.raises(ValueError, match="phi"):
            LCIHistoryEntry(phi=1.01, timestamp="2026-07-24T12:00:00Z", session_id="s1")


# ---------------------------------------------------------------------------
# compute_lci_trend()
# ---------------------------------------------------------------------------

class TestComputeLCITrend:

    def _profile_with_phis(self, phis: list[float]) -> GAIANProfileModel:
        history = [
            LCIHistoryEntry(phi=p, timestamp=f"2026-07-24T{10+i:02d}:00:00Z", session_id=f"s{i}")
            for i, p in enumerate(phis)
        ]
        return GAIANProfileModel(
            architect_id="x", name="x", slug="x",
            lci_baseline=sum(phis) / len(phis),
            lci_history=history,
        )

    def test_rising_trend(self):
        p = self._profile_with_phis([0.40, 0.45, 0.50, 0.55])
        trend = p.compute_lci_trend(current_phi=0.62)
        assert trend == "rising"

    def test_falling_trend(self):
        p = self._profile_with_phis([0.60, 0.55, 0.50, 0.45])
        trend = p.compute_lci_trend(current_phi=0.38)
        assert trend == "falling"

    def test_stable_trend(self):
        p = self._profile_with_phis([0.50, 0.51, 0.49, 0.50])
        trend = p.compute_lci_trend(current_phi=0.50)
        assert trend == "stable"

    def test_volatile_trend(self):
        # Extreme oscillation: high std_dev
        p = self._profile_with_phis([0.10, 0.90, 0.10, 0.90])
        trend = p.compute_lci_trend(current_phi=0.10)
        assert trend == "volatile"

    def test_insufficient_history_returns_stable(self):
        p = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.5,
        )
        # No history at all
        trend = p.compute_lci_trend(current_phi=0.5)
        assert trend == "stable"


# ---------------------------------------------------------------------------
# Property helpers
# ---------------------------------------------------------------------------

class TestProfileProperties:

    def test_is_volatile_true_when_trend_volatile(self):
        p = GAIANProfileModel(
            architect_id="x", name="x", slug="x",
            lci_baseline=0.5, lci_trend="volatile"
        )
        assert p.is_volatile is True

    def test_is_volatile_false_when_trend_stable(self):
        p = GAIANProfileModel(
            architect_id="x", name="x", slug="x",
            lci_baseline=0.5, lci_trend="stable"
        )
        assert p.is_volatile is False

    def test_akashic_gate_open_above_threshold(self):
        p = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.72
        )
        assert p.akashic_gate_open is True

    def test_akashic_gate_closed_below_threshold(self):
        p = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.71
        )
        assert p.akashic_gate_open is False

    def test_sigil_unlocked_above_threshold(self):
        p = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.30
        )
        assert p.sigil_unlocked is True

    def test_sigil_locked_below_threshold(self):
        p = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.29
        )
        assert p.sigil_unlocked is False


# ---------------------------------------------------------------------------
# SystemPromptBuilder.add_profile_block()
# ---------------------------------------------------------------------------

class TestSystemPromptBuilderProfileBlock:

    def test_profile_block_type_is_gaian_identity(self, minimal_profile):
        blocks = (
            SystemPromptBuilder()
            .add_profile_block(minimal_profile)
            .build()
        )
        assert len(blocks) == 1
        assert blocks[0]["type"] == "GAIAN_IDENTITY"

    def test_profile_block_contains_architect_id(self, minimal_profile):
        blocks = (
            SystemPromptBuilder()
            .add_profile_block(minimal_profile)
            .build()
        )
        assert blocks[0]["architect_id"] == "test-architect-001"

    def test_profile_block_content_includes_name(self, minimal_profile):
        blocks = (
            SystemPromptBuilder()
            .add_profile_block(minimal_profile)
            .build()
        )
        content = blocks[0]["content"]
        assert "Lyra" in content

    def test_profile_block_content_includes_lci_baseline(self, minimal_profile):
        blocks = (
            SystemPromptBuilder()
            .add_profile_block(minimal_profile)
            .build()
        )
        content = blocks[0]["content"]
        assert "0.500" in content

    def test_profile_block_content_includes_ethical_guardrail_status(self, minimal_profile):
        blocks = (
            SystemPromptBuilder()
            .add_profile_block(minimal_profile)
            .build()
        )
        content = blocks[0]["content"]
        assert "ACTIVE" in content

    def test_profile_block_volatile_shows_recovery_mode(self):
        p = GAIANProfileModel(
            architect_id="x", name="Storm", slug="storm",
            lci_baseline=0.5, lci_trend="volatile"
        )
        blocks = SystemPromptBuilder().add_profile_block(p).build()
        assert "ACTIVE" in blocks[0]["content"]  # Recovery Mode: ACTIVE

    def test_profile_block_stable_shows_recovery_inactive(self, minimal_profile):
        blocks = SystemPromptBuilder().add_profile_block(minimal_profile).build()
        assert "INACTIVE" in blocks[0]["content"]  # Recovery Mode: INACTIVE

    def test_builder_chaining_with_other_blocks(self, minimal_profile):
        blocks = (
            SystemPromptBuilder()
            .add_opus_stage_block(stage="NIGREDO", capabilities=["basic_recall"])
            .add_profile_block(minimal_profile)
            .build()
        )
        assert len(blocks) == 2
        assert blocks[0]["type"] == "OPUS_STAGE"
        assert blocks[1]["type"] == "GAIAN_IDENTITY"


# ---------------------------------------------------------------------------
# Round-trip: asdict() -> reconstruct
# ---------------------------------------------------------------------------

class TestProfileRoundTrip:

    def test_asdict_produces_serializable_dict(self, minimal_profile):
        d = dataclasses.asdict(minimal_profile)
        assert isinstance(d, dict)
        assert d["architect_id"] == "test-architect-001"
        assert d["lci_baseline"] == 0.5

    def test_reconstruct_from_dict_identity_fields(self, minimal_profile):
        d = dataclasses.asdict(minimal_profile)
        # Reconstruct top-level fields (sub-dataclasses need manual reconstruction)
        p2 = GAIANProfileModel(
            architect_id=d["architect_id"],
            name=d["name"],
            slug=d["slug"],
            lci_baseline=d["lci_baseline"],
            lci_trend=d["lci_trend"],
            total_sessions=d["total_sessions"],
            profile_version=d["profile_version"],
        )
        assert p2.architect_id == minimal_profile.architect_id
        assert p2.lci_baseline == minimal_profile.lci_baseline
        assert p2.profile_version == minimal_profile.profile_version

    def test_profile_with_history_round_trips_history_length(
        self, profile_with_history
    ):
        d = dataclasses.asdict(profile_with_history)
        assert len(d["lci_history"]) == 5
        assert d["lci_history"][0]["phi"] == pytest.approx(0.40)
        assert d["lci_history"][-1]["phi"] == pytest.approx(0.60)

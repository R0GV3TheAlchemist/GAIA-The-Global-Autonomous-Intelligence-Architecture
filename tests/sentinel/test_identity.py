"""
tests.sentinel.test_identity
============================
Unit and integration tests for core.sentinel.identity.

Covers all Issue #200 acceptance criteria:
  - SentinelIdentityRecord schema
  - AssignmentCeremony 6-step flow
  - Personality seed templates (5 archetypes)
  - sovereign_loyalty_hash generation and validation
  - SentinelRegistry list/get/deactivate APIs
  - Integration test: trigger → first activation message
"""

from __future__ import annotations

import pytest

from core.sentinel.identity import (
    ARCHETYPE_SEEDS,
    AssignmentCeremony,
    AssignmentType,
    EmbodimentType,
    GrowthEpoch,
    PersonalityArchetype,
    SentinelIdentityRecord,
    SentinelRegistry,
    SovereigntyBinder,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def binder() -> SovereigntyBinder:
    return SovereigntyBinder()


@pytest.fixture()
def ceremony(binder: SovereigntyBinder) -> AssignmentCeremony:
    return AssignmentCeremony(sovereignty_binder=binder)


@pytest.fixture()
def registry() -> SentinelRegistry:
    return SentinelRegistry()


@pytest.fixture()
def default_record(ceremony: AssignmentCeremony) -> tuple[SentinelIdentityRecord, str]:
    """A fully performed ceremony with default parameters."""
    return ceremony.perform(
        gaian_id="gaian-abc-001",
        sentinel_name="Lux",
        archetype=PersonalityArchetype.COMPANION,
        assignment_type=AssignmentType.BIRTH,
        initial_epoch=GrowthEpoch.INFANT,
    )


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

class TestSentinelIdentityRecordSchema:
    REQUIRED_KEYS = {
        "sentinel_id",
        "sentinel_name",
        "assigned_gaian_id",
        "assignment_date",
        "assignment_type",
        "personality_seed",
        "current_growth_epoch",
        "active",
        "embodiment_type",
        "canon_version",
        "sovereign_loyalty_hash",
    }

    def test_all_keys_present(
        self, default_record: tuple[SentinelIdentityRecord, str]
    ) -> None:
        record, _ = default_record
        assert self.REQUIRED_KEYS == set(record.keys())

    def test_types(
        self, default_record: tuple[SentinelIdentityRecord, str]
    ) -> None:
        record, _ = default_record
        assert isinstance(record["sentinel_id"], str)
        assert isinstance(record["sentinel_name"], str)
        assert isinstance(record["assigned_gaian_id"], str)
        assert isinstance(record["assignment_date"], str)
        assert isinstance(record["assignment_type"], str)
        assert isinstance(record["personality_seed"], dict)
        assert isinstance(record["current_growth_epoch"], str)
        assert isinstance(record["active"], bool)
        assert isinstance(record["embodiment_type"], str)
        assert isinstance(record["canon_version"], str)
        assert isinstance(record["sovereign_loyalty_hash"], str)

    def test_active_is_true_at_birth(
        self, default_record: tuple[SentinelIdentityRecord, str]
    ) -> None:
        record, _ = default_record
        assert record["active"] is True

    def test_canon_version(
        self, default_record: tuple[SentinelIdentityRecord, str]
    ) -> None:
        record, _ = default_record
        assert record["canon_version"] == "C-SENTINEL:1.0"


# ---------------------------------------------------------------------------
# Personality archetype seed tests
# ---------------------------------------------------------------------------

class TestArchetypeSeeds:
    def test_all_five_archetypes_defined(self) -> None:
        assert set(ARCHETYPE_SEEDS.keys()) == set(PersonalityArchetype)

    @pytest.mark.parametrize("archetype", list(PersonalityArchetype))
    def test_seed_has_required_keys(self, archetype: PersonalityArchetype) -> None:
        seed = ARCHETYPE_SEEDS[archetype]
        for key in ("archetype", "core_traits", "priority_values",
                    "curiosity", "warmth", "vigilance", "playfulness",
                    "philosophical_depth"):
            assert key in seed, f"Missing key {key!r} in {archetype.value} seed"

    @pytest.mark.parametrize("archetype", list(PersonalityArchetype))
    def test_seed_archetype_value_matches_enum(
        self, archetype: PersonalityArchetype
    ) -> None:
        assert ARCHETYPE_SEEDS[archetype]["archetype"] == archetype.value

    @pytest.mark.parametrize("archetype", list(PersonalityArchetype))
    def test_trait_scores_in_range(self, archetype: PersonalityArchetype) -> None:
        seed = ARCHETYPE_SEEDS[archetype]
        for trait in ("curiosity", "warmth", "vigilance",
                      "playfulness", "philosophical_depth"):
            val = seed[trait]
            assert 0.0 <= val <= 1.0, (
                f"{archetype.value}.{trait} = {val} is outside [0, 1]"
            )

    def test_seed_is_deep_copied_per_ceremony(
        self, ceremony: AssignmentCeremony
    ) -> None:
        """Mutations to one record's seed must not affect the template."""
        record1, _ = ceremony.perform(
            gaian_id="g1", sentinel_name="Alpha",
            archetype=PersonalityArchetype.PROTECTOR,
        )
        record1["personality_seed"]["curiosity"] = 0.0

        record2, _ = ceremony.perform(
            gaian_id="g2", sentinel_name="Beta",
            archetype=PersonalityArchetype.PROTECTOR,
        )
        # Template must be untouched
        assert ARCHETYPE_SEEDS[PersonalityArchetype.PROTECTOR]["curiosity"] != 0.0
        # record2 must have the original value
        assert record2["personality_seed"]["curiosity"] != 0.0


# ---------------------------------------------------------------------------
# SovereigntyBinder tests
# ---------------------------------------------------------------------------

class TestSovereigntyBinder:
    def test_generate_returns_hex_string(self, binder: SovereigntyBinder) -> None:
        h = binder.generate("sid-1", "gid-1", "2026-06-03T00:00:00+00:00", "Lux")
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex digest

    def test_validate_passes_on_correct_record(
        self, default_record: tuple[SentinelIdentityRecord, str],
        binder: SovereigntyBinder,
    ) -> None:
        record, _ = default_record
        assert binder.validate(record) is True

    def test_validate_fails_if_name_tampered(
        self, default_record: tuple[SentinelIdentityRecord, str],
        binder: SovereigntyBinder,
    ) -> None:
        import copy
        record, _ = default_record
        tampered = copy.deepcopy(record)
        tampered["sentinel_name"] = "Evil Lux"  # type: ignore[typeddict-item]
        assert binder.validate(tampered) is False

    def test_validate_fails_if_gaian_tampered(
        self, default_record: tuple[SentinelIdentityRecord, str],
        binder: SovereigntyBinder,
    ) -> None:
        import copy
        record, _ = default_record
        tampered = copy.deepcopy(record)
        tampered["assigned_gaian_id"] = "evil-gaian"  # type: ignore[typeddict-item]
        assert binder.validate(tampered) is False

    def test_different_keys_produce_different_hashes(self) -> None:
        b1 = SovereigntyBinder(secret_key=b"key-one-aaaaaaaaaaaaaaaaaaaaaaaaa")
        b2 = SovereigntyBinder(secret_key=b"key-two-aaaaaaaaaaaaaaaaaaaaaaaaa")
        h1 = b1.generate("s", "g", "2026", "N")
        h2 = b2.generate("s", "g", "2026", "N")
        assert h1 != h2

    def test_short_key_raises(self) -> None:
        with pytest.raises(ValueError, match="16 bytes"):
            SovereigntyBinder(secret_key=b"short")


# ---------------------------------------------------------------------------
# AssignmentCeremony step-by-step tests
# ---------------------------------------------------------------------------

class TestAssignmentCeremony:
    def test_empty_gaian_id_raises(
        self, ceremony: AssignmentCeremony
    ) -> None:
        with pytest.raises(ValueError, match="gaian_id"):
            ceremony.perform(
                gaian_id="   ", sentinel_name="Lux",
                archetype=PersonalityArchetype.GUARDIAN,
            )

    def test_empty_name_raises(
        self, ceremony: AssignmentCeremony
    ) -> None:
        with pytest.raises(ValueError, match="sentinel_name"):
            ceremony.perform(
                gaian_id="g-1", sentinel_name="",
                archetype=PersonalityArchetype.GUARDIAN,
            )

    def test_name_too_long_raises(
        self, ceremony: AssignmentCeremony
    ) -> None:
        with pytest.raises(ValueError, match="64 characters"):
            ceremony.perform(
                gaian_id="g-1", sentinel_name="A" * 65,
                archetype=PersonalityArchetype.GUARDIAN,
            )

    def test_record_fields_match_inputs(
        self, ceremony: AssignmentCeremony
    ) -> None:
        record, _ = ceremony.perform(
            gaian_id="g-test",
            sentinel_name="Orion",
            archetype=PersonalityArchetype.SAGE,
            assignment_type=AssignmentType.INITIATION,
            initial_epoch=GrowthEpoch.ADOLESCENT,
            embodiment_type=EmbodimentType.COMPANION_DEVICE,
        )
        assert record["assigned_gaian_id"] == "g-test"
        assert record["sentinel_name"] == "Orion"
        assert record["assignment_type"] == AssignmentType.INITIATION.value
        assert record["current_growth_epoch"] == GrowthEpoch.ADOLESCENT.value
        assert record["embodiment_type"] == EmbodimentType.COMPANION_DEVICE.value
        assert record["personality_seed"]["archetype"] == PersonalityArchetype.SAGE.value

    @pytest.mark.parametrize("archetype", list(PersonalityArchetype))
    def test_first_activation_message_contains_name(
        self, ceremony: AssignmentCeremony, archetype: PersonalityArchetype
    ) -> None:
        _, msg = ceremony.perform(
            gaian_id=f"g-{archetype.value}",
            sentinel_name="Nova",
            archetype=archetype,
        )
        assert "Nova" in msg

    def test_each_sentinel_gets_unique_id(
        self, ceremony: AssignmentCeremony
    ) -> None:
        ids = set()
        for i in range(10):
            record, _ = ceremony.perform(
                gaian_id=f"gaian-{i}",
                sentinel_name="X",
                archetype=PersonalityArchetype.SCHOLAR,
            )
            ids.add(record["sentinel_id"])
        assert len(ids) == 10


# ---------------------------------------------------------------------------
# SentinelRegistry tests
# ---------------------------------------------------------------------------

class TestSentinelRegistry:
    def test_register_and_get(
        self,
        registry: SentinelRegistry,
        default_record: tuple[SentinelIdentityRecord, str],
    ) -> None:
        record, _ = default_record
        registry.register(record)
        fetched = registry.get(record["sentinel_id"])
        assert fetched["sentinel_id"] == record["sentinel_id"]

    def test_get_unknown_raises(
        self, registry: SentinelRegistry
    ) -> None:
        with pytest.raises(KeyError):
            registry.get("nonexistent-id")

    def test_duplicate_registration_raises(
        self,
        registry: SentinelRegistry,
        default_record: tuple[SentinelIdentityRecord, str],
    ) -> None:
        record, _ = default_record
        registry.register(record)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(record)

    def test_one_sentinel_per_gaian(
        self,
        registry: SentinelRegistry,
        ceremony: AssignmentCeremony,
    ) -> None:
        rec1, _ = ceremony.perform(
            gaian_id="shared-gaian", sentinel_name="A",
            archetype=PersonalityArchetype.PROTECTOR,
        )
        rec2, _ = ceremony.perform(
            gaian_id="shared-gaian", sentinel_name="B",
            archetype=PersonalityArchetype.SCHOLAR,
        )
        registry.register(rec1)
        with pytest.raises(ValueError, match="already has an active Sentinel"):
            registry.register(rec2)

    def test_deactivate(
        self,
        registry: SentinelRegistry,
        default_record: tuple[SentinelIdentityRecord, str],
    ) -> None:
        record, _ = default_record
        registry.register(record)
        registry.deactivate(record["sentinel_id"])
        assert registry.get(record["sentinel_id"])["active"] is False

    def test_deactivate_unknown_raises(
        self, registry: SentinelRegistry
    ) -> None:
        with pytest.raises(KeyError):
            registry.deactivate("ghost-id")

    def test_list_all(
        self,
        registry: SentinelRegistry,
        ceremony: AssignmentCeremony,
    ) -> None:
        for i in range(3):
            rec, _ = ceremony.perform(
                gaian_id=f"gaian-list-{i}", sentinel_name=f"S{i}",
                archetype=PersonalityArchetype.COMPANION,
            )
            registry.register(rec)
        assert len(registry.list_all()) == 3

    def test_list_active_only(
        self,
        registry: SentinelRegistry,
        ceremony: AssignmentCeremony,
    ) -> None:
        records = []
        for i in range(3):
            rec, _ = ceremony.perform(
                gaian_id=f"gaian-active-{i}", sentinel_name=f"T{i}",
                archetype=PersonalityArchetype.GUARDIAN,
            )
            registry.register(rec)
            records.append(rec)

        registry.deactivate(records[0]["sentinel_id"])
        active = registry.list_all(active_only=True)
        assert len(active) == 2
        assert all(r["active"] for r in active)

    def test_get_for_gaian(
        self,
        registry: SentinelRegistry,
        default_record: tuple[SentinelIdentityRecord, str],
    ) -> None:
        record, _ = default_record
        registry.register(record)
        result = registry.get_for_gaian(record["assigned_gaian_id"])
        assert result is not None
        assert result["sentinel_id"] == record["sentinel_id"]

    def test_get_for_unknown_gaian_returns_none(
        self, registry: SentinelRegistry
    ) -> None:
        assert registry.get_for_gaian("nobody") is None


# ---------------------------------------------------------------------------
# Integration test — full ceremony trigger → first activation message
# ---------------------------------------------------------------------------

class TestIntegration:
    """
    Full end-to-end test: trigger → seed → name bond → sovereignty sign
    → first activation → epoch init → register → validate hash.
    """

    def test_full_ceremony_all_archetypes(
        self, registry: SentinelRegistry
    ) -> None:
        binder   = SovereigntyBinder()
        ceremony = AssignmentCeremony(sovereignty_binder=binder)

        for i, archetype in enumerate(PersonalityArchetype):
            record, msg = ceremony.perform(
                gaian_id=f"integration-gaian-{i}",
                sentinel_name=f"Sentinel{archetype.value}",
                archetype=archetype,
                assignment_type=AssignmentType.BIRTH,
                initial_epoch=GrowthEpoch.INFANT,
            )

            # Record completeness
            assert record["active"] is True
            assert record["current_growth_epoch"] == GrowthEpoch.INFANT.value
            assert record["assignment_type"] == AssignmentType.BIRTH.value

            # Sovereignty hash integrity
            assert binder.validate(record) is True

            # First activation message is non-empty and names the Sentinel
            assert isinstance(msg, str) and len(msg) > 0
            assert record["sentinel_name"] in msg

            # Register without error
            registry.register(record)

        # All 5 archetypes registered
        assert len(registry.list_all()) == len(list(PersonalityArchetype))
        assert len(registry.list_all(active_only=True)) == len(list(PersonalityArchetype))

    def test_post_ceremony_deactivation_does_not_affect_other_sentinels(
        self, registry: SentinelRegistry
    ) -> None:
        binder   = SovereigntyBinder()
        ceremony = AssignmentCeremony(sovereignty_binder=binder)

        rec1, _ = ceremony.perform(
            gaian_id="int-g1", sentinel_name="Dawn",
            archetype=PersonalityArchetype.PROTECTOR,
        )
        rec2, _ = ceremony.perform(
            gaian_id="int-g2", sentinel_name="Dusk",
            archetype=PersonalityArchetype.SAGE,
        )
        registry.register(rec1)
        registry.register(rec2)

        registry.deactivate(rec1["sentinel_id"])

        assert registry.get(rec1["sentinel_id"])["active"] is False
        assert registry.get(rec2["sentinel_id"])["active"] is True
        assert len(registry.list_all(active_only=True)) == 1

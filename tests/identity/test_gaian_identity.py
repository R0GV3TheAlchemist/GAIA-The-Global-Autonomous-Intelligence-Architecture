from __future__ import annotations

import pytest
from datetime import date

from core.identity.gaian.model import (
    AgeRestriction,
    AvatarModality,
    GAIANIdentity,
    LifecycleStage,
    WaveformAvatar,
)
from core.identity.gaian.registry import GAIANRegistry, GAIANRegistryError


def _dob_years_ago(years: int) -> str:
    today = date.today()
    return date(today.year - years, today.month, today.day).isoformat()


class TestLifecycleStage:
    def test_infant(self):       assert LifecycleStage.from_age(1)  == LifecycleStage.INFANT
    def test_child(self):        assert LifecycleStage.from_age(7)  == LifecycleStage.CHILD
    def test_adolescent(self):   assert LifecycleStage.from_age(15) == LifecycleStage.ADOLESCENT
    def test_young_adult(self):  assert LifecycleStage.from_age(21) == LifecycleStage.YOUNG_ADULT
    def test_adult(self):        assert LifecycleStage.from_age(35) == LifecycleStage.ADULT
    def test_elder(self):        assert LifecycleStage.from_age(70) == LifecycleStage.ELDER


class TestAgeRestriction:
    def test_child_has_safe_search(self):
        r = AgeRestriction.for_stage(LifecycleStage.CHILD)
        assert r.safe_search_enforced
        assert not r.social_media_allowed
        assert r.guardian_required
        assert r.ai_persona_depth == "companion"
        assert r.memory_scope == "year"

    def test_adolescent_has_expanding_access(self):
        r = AgeRestriction.for_stage(LifecycleStage.ADOLESCENT)
        assert r.max_content_rating == "PG-13"
        assert r.social_media_allowed
        assert not r.purchasing_allowed
        assert r.memory_scope == "lifetime"

    def test_adult_has_full_sovereignty(self):
        r = AgeRestriction.for_stage(LifecycleStage.ADULT)
        assert r.max_content_rating == "UNRATED"
        assert r.autonomy_level == "autonomous"
        assert r.ai_persona_depth == "sovereign"
        assert not r.guardian_required
        assert not r.guardian_can_review_memory

    def test_child_sentinel_range_limited(self):
        r = AgeRestriction.for_stage(LifecycleStage.CHILD)
        assert r.sentinel_unsupervised_range_m == 30.0
        assert not r.sentinel_physical_autonomy

    def test_adult_sentinel_unlimited(self):
        r = AgeRestriction.for_stage(LifecycleStage.ADULT)
        assert r.sentinel_physical_autonomy
        import math
        assert math.isinf(r.sentinel_unsupervised_range_m)


class TestGAIANRegistry:
    def test_create_adult_gaian(self):
        reg = GAIANRegistry()
        g = reg.create_gaian("Alice", date_of_birth=_dob_years_ago(30))
        assert g.lifecycle_stage == LifecycleStage.ADULT
        assert not g.is_minor()

    def test_create_child_gaian_requires_guardian(self):
        reg = GAIANRegistry()
        parent = reg.create_gaian("Parent", date_of_birth=_dob_years_ago(35))
        child = reg.create_gaian(
            "Emma",
            date_of_birth=_dob_years_ago(7),
            guardian_gaian_ids=[parent.gaian_id],
        )
        assert child.lifecycle_stage == LifecycleStage.CHILD
        assert child.is_minor()
        assert parent.gaian_id in child.guardian_gaian_ids

    def test_create_child_without_guardian_raises(self):
        reg = GAIANRegistry()
        with pytest.raises(GAIANRegistryError):
            reg.create_gaian("Emma", date_of_birth=_dob_years_ago(7))

    def test_infant_gaian(self):
        reg = GAIANRegistry()
        parent = reg.create_gaian("Parent", date_of_birth=_dob_years_ago(30))
        infant = reg.create_gaian(
            "Baby",
            date_of_birth=_dob_years_ago(1),
            guardian_gaian_ids=[parent.gaian_id],
        )
        assert infant.lifecycle_stage == LifecycleStage.INFANT

    def test_lifecycle_refreshes_on_get(self):
        """Registry always returns fresh lifecycle on get()."""
        reg = GAIANRegistry()
        g = reg.create_gaian("Alice", date_of_birth=_dob_years_ago(30))
        fetched = reg.get(g.gaian_id)
        assert fetched.lifecycle_stage == LifecycleStage.ADULT

    def test_waveform_signature_is_stable(self):
        reg = GAIANRegistry()
        g1 = reg.create_gaian("Alice", date_of_birth=_dob_years_ago(30))
        g2 = reg.create_gaian("Alice", date_of_birth=_dob_years_ago(30))
        # Same name → same waveform signature (deterministic)
        assert g1.avatar.waveform_signature == g2.avatar.waveform_signature
        # But different GAIAN IDs
        assert g1.gaian_id != g2.gaian_id

    def test_cannot_add_guardian_to_adult(self):
        reg = GAIANRegistry()
        adult = reg.create_gaian("Alice", date_of_birth=_dob_years_ago(30))
        guardian = reg.create_gaian("Parent", date_of_birth=_dob_years_ago(55))
        with pytest.raises(GAIANRegistryError):
            reg.add_guardian(adult.gaian_id, guardian.gaian_id)

    def test_accept_laws(self):
        reg = GAIANRegistry()
        g = reg.create_gaian("Alice", date_of_birth=_dob_years_ago(30))
        g.accept_laws()
        assert g.coexistence_laws_accepted
        assert g.gaian_laws_accepted


class TestSentinelBinding:
    def test_register_and_bind_sentinel(self):
        reg = GAIANRegistry()
        g = reg.create_gaian("Alice", date_of_birth=_dob_years_ago(30))
        reg.register_sentinel("SENTINEL-001", "Aria", model="Mark-I")
        reg.bind_sentinel_to_gaian("SENTINEL-001", g.gaian_id)
        assert "SENTINEL-001" in g.sentinel_ids
        assert "SENTINEL-001" in g.avatar.bound_sentinel_ids

    def test_bind_sentinel_to_child(self):
        """A child GAIAN can have a sentinel co-steward."""
        reg = GAIANRegistry()
        parent = reg.create_gaian("Parent", date_of_birth=_dob_years_ago(35))
        child = reg.create_gaian(
            "Emma", date_of_birth=_dob_years_ago(8),
            guardian_gaian_ids=[parent.gaian_id]
        )
        reg.register_sentinel("SENTINEL-CHILD-001", "Luna", model="Mark-I-Child")
        reg.bind_sentinel_to_gaian("SENTINEL-CHILD-001", child.gaian_id)
        assert "SENTINEL-CHILD-001" in child.sentinel_ids
        # Child sentinel respects physical autonomy restriction
        assert not child.age_restriction.sentinel_physical_autonomy


class TestWaveformAvatar:
    def test_avatar_modality_expansion(self):
        reg = GAIANRegistry()
        g = reg.create_gaian("Alice", date_of_birth=_dob_years_ago(30))
        reg.add_avatar_modality(g.gaian_id, AvatarModality.SPATIAL_AR)
        assert AvatarModality.SPATIAL_AR in g.avatar.supported_modalities

    def test_avatar_evolution_log(self):
        reg = GAIANRegistry()
        parent = reg.create_gaian("Parent", date_of_birth=_dob_years_ago(35))
        child = reg.create_gaian(
            "Emma", date_of_birth=_dob_years_ago(8),
            guardian_gaian_ids=[parent.gaian_id]
        )
        reg.add_avatar_modality(child.gaian_id, AvatarModality.ROBOTIC_FACE)
        assert len(child.avatar.evolution_log) >= 1
        assert child.avatar.evolution_log[-1]["event"] == "modality_added"

    def test_sentinel_bind_logs_in_avatar(self):
        reg = GAIANRegistry()
        g = reg.create_gaian("Alice", date_of_birth=_dob_years_ago(30))
        reg.register_sentinel("S-001", "Orion")
        reg.bind_sentinel_to_gaian("S-001", g.gaian_id)
        assert "S-001" in g.avatar.bound_sentinel_ids

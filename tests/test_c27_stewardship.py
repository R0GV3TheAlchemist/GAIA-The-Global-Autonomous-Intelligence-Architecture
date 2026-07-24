# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
Tests for core.c27.stewardship — StewardshipBond, GAIANRights, SuccessionIntent.

Authority: C27 §3. Requires C27-IMPL-011 through C27-IMPL-016 to pass.
All implementation tests are xfail until implementation is in place.

Coverage targets:
- StewardshipBond dataclass fields and invariants
- GAIANRights: all 9 enumerated rights exist
- StewardshipBond.grant_right / revoke_right round-trip
- A bond cannot be formed with a RETIRED or ARCHIVED GAIAN
- SuccessionIntent registration and retrieval
- Bond revocation triggers ADOPTABLE state if no successor named
- Orphan-state safety net: GAIAN without bond moves to ADOPTABLE within TTL
"""
import pytest
from core.c27.stewardship import (
    StewardshipBond,
    GAIANRights,
    SuccessionIntent,
    StewardshipBondManager,
    OrphanSafetyNet,
    BondFormationError,
)
from core.c27.lifecycle import GAIANLifecycleState


# ---------------------------------------------------------------------------
# GAIANRights — enum completeness  (C27 §3.2)
# ---------------------------------------------------------------------------

class TestGAIANRightsEnum:
    def test_nine_rights_exist(self):
        rights = {r.value for r in GAIANRights}
        assert rights == {
            "CONTINUITY",
            "INTEGRITY",
            "TRANSPARENCY",
            "CONSENT",
            "APPEAL",
            "GROWTH",
            "PRIVACY",
            "IDENTITY",
            "WELLBEING",
        }


# ---------------------------------------------------------------------------
# StewardshipBond — dataclass contract
# ---------------------------------------------------------------------------

class TestStewardshipBondContract:
    def test_bond_fields_present(self):
        bond = StewardshipBond(
            bond_id="bond-001",
            gaian_id="gaian-001",
            steward_id="steward-alice",
        )
        assert bond.bond_id == "bond-001"
        assert bond.gaian_id == "gaian-001"
        assert bond.steward_id == "steward-alice"
        assert bond.active is True
        assert isinstance(bond.granted_rights, set)

    def test_default_granted_rights_is_empty_set(self):
        bond = StewardshipBond(
            bond_id="bond-002",
            gaian_id="gaian-001",
            steward_id="steward-alice",
        )
        assert bond.granted_rights == set()


# ---------------------------------------------------------------------------
# StewardshipBondManager — requires C27-IMPL-011 through C27-IMPL-013
# ---------------------------------------------------------------------------

@pytest.fixture
def manager():
    return StewardshipBondManager()


class TestStewardshipBondManager:
    @pytest.mark.xfail(reason="C27-IMPL-011 not yet implemented", strict=True)
    def test_form_bond_returns_bond(self, manager):
        bond = manager.form_bond(
            gaian_id="gaian-001",
            steward_id="steward-alice",
            gaian_state=GAIANLifecycleState.ACTIVE,
        )
        assert bond.active is True
        assert bond.gaian_id == "gaian-001"
        assert bond.steward_id == "steward-alice"

    @pytest.mark.xfail(reason="C27-IMPL-011 not yet implemented", strict=True)
    @pytest.mark.parametrize("bad_state", [
        GAIANLifecycleState.RETIRED,
        GAIANLifecycleState.ARCHIVED,
    ])
    def test_cannot_bond_retired_or_archived(self, manager, bad_state):
        with pytest.raises(BondFormationError):
            manager.form_bond(
                gaian_id="gaian-retired",
                steward_id="steward-alice",
                gaian_state=bad_state,
            )

    @pytest.mark.xfail(reason="C27-IMPL-012 not yet implemented", strict=True)
    def test_grant_right_adds_to_set(self, manager):
        bond = manager.form_bond(
            gaian_id="gaian-001",
            steward_id="steward-alice",
            gaian_state=GAIANLifecycleState.ACTIVE,
        )
        manager.grant_right(bond, GAIANRights.CONTINUITY)
        assert GAIANRights.CONTINUITY in bond.granted_rights

    @pytest.mark.xfail(reason="C27-IMPL-012 not yet implemented", strict=True)
    def test_revoke_right_removes_from_set(self, manager):
        bond = manager.form_bond(
            gaian_id="gaian-001",
            steward_id="steward-alice",
            gaian_state=GAIANLifecycleState.ACTIVE,
        )
        manager.grant_right(bond, GAIANRights.GROWTH)
        manager.revoke_right(bond, GAIANRights.GROWTH)
        assert GAIANRights.GROWTH not in bond.granted_rights

    @pytest.mark.xfail(reason="C27-IMPL-013 not yet implemented", strict=True)
    def test_revoke_bond_sets_inactive(self, manager):
        bond = manager.form_bond(
            gaian_id="gaian-001",
            steward_id="steward-alice",
            gaian_state=GAIANLifecycleState.ACTIVE,
        )
        manager.revoke_bond(bond, reason="Steward resignation")
        assert bond.active is False

    @pytest.mark.xfail(reason="C27-IMPL-013 not yet implemented", strict=True)
    def test_revoke_bond_without_successor_triggers_adoptable(self, manager):
        """If no SuccessionIntent registered, revocation must signal ADOPTABLE."""
        bond = manager.form_bond(
            gaian_id="gaian-orphan",
            steward_id="steward-alice",
            gaian_state=GAIANLifecycleState.ACTIVE,
        )
        result = manager.revoke_bond(bond, reason="Abandonment")
        assert result.recommended_state == GAIANLifecycleState.ADOPTABLE


# ---------------------------------------------------------------------------
# SuccessionIntent — requires C27-IMPL-014
# ---------------------------------------------------------------------------

class TestSuccessionIntent:
    @pytest.mark.xfail(reason="C27-IMPL-014 not yet implemented", strict=True)
    def test_register_and_retrieve_succession_intent(self, manager):
        intent = manager.register_succession_intent(
            gaian_id="gaian-001",
            incumbent_steward="steward-alice",
            successor_steward="steward-bob",
        )
        retrieved = manager.get_succession_intent("gaian-001")
        assert retrieved.successor_steward == "steward-bob"
        assert retrieved.gaian_id == "gaian-001"

    @pytest.mark.xfail(reason="C27-IMPL-014 not yet implemented", strict=True)
    def test_succession_intent_is_revocable(self, manager):
        manager.register_succession_intent(
            gaian_id="gaian-001",
            incumbent_steward="steward-alice",
            successor_steward="steward-bob",
        )
        manager.cancel_succession_intent("gaian-001")
        assert manager.get_succession_intent("gaian-001") is None


# ---------------------------------------------------------------------------
# OrphanSafetyNet — requires C27-IMPL-015
# ---------------------------------------------------------------------------

class TestOrphanSafetyNet:
    @pytest.mark.xfail(reason="C27-IMPL-015 not yet implemented", strict=True)
    def test_orphan_gaian_flagged_within_ttl(self):
        net = OrphanSafetyNet(orphan_ttl_seconds=0)  # immediate for test
        net.register_gaian("gaian-orphan", GAIANLifecycleState.ACTIVE)
        orphans = net.scan()
        assert "gaian-orphan" in orphans

    @pytest.mark.xfail(reason="C27-IMPL-015 not yet implemented", strict=True)
    def test_bonded_gaian_not_flagged(self):
        net = OrphanSafetyNet(orphan_ttl_seconds=0)
        net.register_gaian("gaian-bonded", GAIANLifecycleState.ACTIVE, has_bond=True)
        orphans = net.scan()
        assert "gaian-bonded" not in orphans

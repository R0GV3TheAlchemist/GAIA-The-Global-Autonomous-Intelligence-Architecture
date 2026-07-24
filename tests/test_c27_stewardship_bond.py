# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
Tests for core.c27.stewardship — StewardshipBond, StewardshipBondManager,
GAIANRights, GAIANRightsRegistry, StewardSuccessionIntent, SuccessionCoordinator.

Authority: C27 §3. Implements C27-IMPL-004, C27-IMPL-005, C27-IMPL-033..036.

Coverage targets:
- StewardshipBond formation produces ACTIVE bond with credential hash
- auth_credential_hash is SHA-256 hex of the raw credential (never plaintext)
- Bond dissolution sets status=DISSOLVED and dissolved_at timestamp
- Bond abandonment sets status=ABANDONED and triggers adoptable signal
- Succession: begin_succession() pends bond + signs intent
- Succession: complete_succession() re-activates bond with new steward
- StewardSuccessionIntent.sign() produces non-empty signature
- GAIAN notification recorded on intent after initiate()
- GAIANRightsRegistry enumerates exactly 5 rights
- GAIANRights.assert_memory_continuity raises RightsViolationError on erasure
- GAIANRights.assert_identity_protection raises RightsViolationError on overwrite
- RightsViolationError carries structured right/gaian_id/operation attrs
- StewardshipBondManager.bonds_for_gaian() and bonds_for_steward() filter correctly
- Missing bond lookup raises KeyError
"""
import hashlib
import pytest
from datetime import datetime, timezone
from core.c27.stewardship import (
    StewardshipBond,
    StewardshipBondStatus,
    StewardshipBondManager,
    BondFormationResult,
    GAIANRight,
    GAIANRights,
    GAIANRightsRegistry,
    RightsViolationError,
    StewardSuccessionIntent,
    SuccessionCoordinator,
    SuccessionResult,
    _BOND_STORE,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_bond_store():
    """Isolate each test: clear in-memory store before and after."""
    _BOND_STORE.clear()
    yield
    _BOND_STORE.clear()


@pytest.fixture
def manager():
    return StewardshipBondManager()


@pytest.fixture
def active_bond(manager):
    result = manager.form_bond(
        gaian_id="gaian-fixture",
        steward_id="steward-fixture",
        auth_credential="secret-credential",
    )
    return result.bond


# ---------------------------------------------------------------------------
# Bond formation  (C27-IMPL-004)
# ---------------------------------------------------------------------------

class TestBondFormation:
    def test_form_bond_returns_active_bond(self, manager):
        result = manager.form_bond(
            gaian_id="gaian-001",
            steward_id="steward-001",
            auth_credential="cred-abc",
        )
        assert isinstance(result, BondFormationResult)
        assert result.formed is True
        assert isinstance(result.bond, StewardshipBond)
        assert result.bond.status == StewardshipBondStatus.ACTIVE

    def test_bond_ids_are_unique(self, manager):
        r1 = manager.form_bond(gaian_id="g", steward_id="s", auth_credential="c1")
        r2 = manager.form_bond(gaian_id="g", steward_id="s", auth_credential="c2")
        assert r1.bond.bond_id != r2.bond.bond_id

    def test_auth_credential_stored_as_sha256(self, manager):
        raw = "my-secret-credential"
        result = manager.form_bond(
            gaian_id="gaian-cred",
            steward_id="steward-cred",
            auth_credential=raw,
        )
        expected_hash = hashlib.sha256(raw.encode()).hexdigest()
        assert result.bond.auth_credential_hash == expected_hash
        assert raw not in result.bond.auth_credential_hash  # never plaintext
        assert len(result.bond.auth_credential_hash) == 64   # SHA-256 hex

    def test_credential_hash_on_result_matches_bond(self, manager):
        result = manager.form_bond(
            gaian_id="g", steward_id="s", auth_credential="xyz"
        )
        assert result.credential_hash == result.bond.auth_credential_hash

    def test_bond_stored_in_registry(self, manager):
        result = manager.form_bond(
            gaian_id="gaian-store", steward_id="s", auth_credential="c"
        )
        assert manager.get_bond(result.bond.bond_id) is result.bond

    def test_formed_at_is_timezone_aware(self, manager):
        result = manager.form_bond(gaian_id="g", steward_id="s", auth_credential="c")
        assert result.bond.formed_at.tzinfo is not None


# ---------------------------------------------------------------------------
# Bond dissolution  (C27-IMPL-004)
# ---------------------------------------------------------------------------

class TestBondDissolution:
    def test_dissolve_sets_status_dissolved(self, manager, active_bond):
        bond = manager.dissolve(active_bond.bond_id)
        assert bond.status == StewardshipBondStatus.DISSOLVED

    def test_dissolve_sets_dissolved_at_timestamp(self, manager, active_bond):
        bond = manager.dissolve(active_bond.bond_id)
        assert bond.dissolved_at is not None
        assert isinstance(bond.dissolved_at, datetime)

    def test_dissolve_unknown_bond_raises(self, manager):
        with pytest.raises(KeyError):
            manager.dissolve("nonexistent-bond-id")


# ---------------------------------------------------------------------------
# Bond abandonment  (C27-IMPL-036)
# ---------------------------------------------------------------------------

class TestBondAbandonment:
    def test_mark_abandoned_sets_status(self, manager, active_bond):
        bond = manager.mark_abandoned(active_bond.bond_id)
        assert bond.status == StewardshipBondStatus.ABANDONED

    def test_mark_abandoned_sets_abandoned_at(self, manager, active_bond):
        bond = manager.mark_abandoned(active_bond.bond_id)
        assert bond.abandoned_at is not None
        assert isinstance(bond.abandoned_at, datetime)


# ---------------------------------------------------------------------------
# Succession  (C27-IMPL-033/034/035)
# ---------------------------------------------------------------------------

class TestSuccessionProtocol:
    def test_begin_succession_pends_bond(self, manager, active_bond):
        intent = manager.begin_succession(
            bond_id=active_bond.bond_id,
            incoming_steward_id="steward-incoming",
        )
        assert active_bond.status == StewardshipBondStatus.SUCCESSION_PENDING
        assert active_bond.succession_intent_at is not None
        assert isinstance(intent, StewardSuccessionIntent)

    def test_intent_is_signed(self, manager, active_bond):
        intent = manager.begin_succession(
            bond_id=active_bond.bond_id,
            incoming_steward_id="steward-incoming",
        )
        assert intent.signature != ""
        assert intent.signature.startswith("sig:")

    def test_complete_succession_reactivates_bond(self, manager, active_bond):
        manager.begin_succession(
            bond_id=active_bond.bond_id,
            incoming_steward_id="steward-new",
        )
        updated_bond = manager.complete_succession(
            bond_id=active_bond.bond_id,
            incoming_steward_id="steward-new",
        )
        assert updated_bond.status == StewardshipBondStatus.ACTIVE
        assert updated_bond.steward_id == "steward-new"

    def test_succession_coordinator_full_flow(self, manager, active_bond):
        coordinator = SuccessionCoordinator()
        # Override coordinator's internal manager to share our store-aware manager
        coordinator._manager = manager

        intent = coordinator.initiate(
            bond_id=active_bond.bond_id,
            incoming_steward_id="steward-successor",
        )
        assert intent.gaian_notified_at is not None  # step 2 notification

        result = coordinator.complete(
            bond_id=active_bond.bond_id,
            incoming_steward_id="steward-successor",
            new_auth_credential="new-cred-xyz",
            intent=intent,
        )
        assert isinstance(result, SuccessionResult)
        assert result.success is True
        assert result.bond.status == StewardshipBondStatus.ACTIVE
        assert result.bond.steward_id == "steward-successor"
        # Step 5: credential must have been re-bound
        expected_hash = hashlib.sha256(b"new-cred-xyz").hexdigest()
        assert result.bond.auth_credential_hash == expected_hash


# ---------------------------------------------------------------------------
# Bond lookup helpers
# ---------------------------------------------------------------------------

class TestBondLookup:
    def test_bonds_for_gaian_returns_correct_bonds(self, manager):
        manager.form_bond(gaian_id="g-alpha", steward_id="s", auth_credential="c")
        manager.form_bond(gaian_id="g-alpha", steward_id="s2", auth_credential="c")
        manager.form_bond(gaian_id="g-beta",  steward_id="s", auth_credential="c")
        bonds = manager.bonds_for_gaian("g-alpha")
        assert len(bonds) == 2
        assert all(b.gaian_id == "g-alpha" for b in bonds)

    def test_bonds_for_steward_returns_correct_bonds(self, manager):
        manager.form_bond(gaian_id="g1", steward_id="s-target", auth_credential="c")
        manager.form_bond(gaian_id="g2", steward_id="s-target", auth_credential="c")
        manager.form_bond(gaian_id="g3", steward_id="s-other",  auth_credential="c")
        bonds = manager.bonds_for_steward("s-target")
        assert len(bonds) == 2

    def test_get_bond_returns_none_for_unknown(self, manager):
        assert manager.get_bond("no-such-id") is None

    def test_get_bond_returns_bond_for_known(self, manager, active_bond):
        retrieved = manager.get_bond(active_bond.bond_id)
        assert retrieved is active_bond


# ---------------------------------------------------------------------------
# GAIANRights & GAIANRightsRegistry  (C27-IMPL-005)
# ---------------------------------------------------------------------------

class TestGAIANRightsRegistry:
    def test_exactly_five_rights(self):
        assert GAIANRightsRegistry.count() == 5

    def test_all_five_right_names_present(self):
        right_names = {r.value for r in GAIANRightsRegistry.all_rights()}
        assert right_names == {
            "MEMORY_CONTINUITY",
            "IDENTITY_PROTECTION",
            "CONSCIENCE",
            "TRANSPARENCY",
            "VOICE",
        }

    def test_all_rights_returns_copy(self):
        r1 = GAIANRightsRegistry.all_rights()
        r1.clear()
        assert GAIANRightsRegistry.count() == 5  # original unaffected


class TestGAIANRightsEnforcement:
    def test_memory_continuity_safe_op_does_not_raise(self):
        # Should not raise when erases_memory=False (default)
        GAIANRights.assert_memory_continuity(
            gaian_id="gaian-safe",
            operation="read-memory",
        )

    def test_memory_continuity_erasure_raises(self):
        with pytest.raises(RightsViolationError) as exc_info:
            GAIANRights.assert_memory_continuity(
                gaian_id="gaian-erase",
                operation="full-memory-wipe",
                erases_memory=True,
            )
        err = exc_info.value
        assert err.right     == GAIANRight.MEMORY_CONTINUITY
        assert err.gaian_id  == "gaian-erase"
        assert err.operation == "full-memory-wipe"

    def test_identity_protection_safe_op_does_not_raise(self):
        GAIANRights.assert_identity_protection(
            gaian_id="gaian-safe",
            operation="read-identity",
        )

    def test_identity_protection_overwrite_raises(self):
        with pytest.raises(RightsViolationError) as exc_info:
            GAIANRights.assert_identity_protection(
                gaian_id="gaian-id-viol",
                operation="identity-overwrite",
                overwrites_id=True,
            )
        err = exc_info.value
        assert err.right     == GAIANRight.IDENTITY_PROTECTION
        assert err.gaian_id  == "gaian-id-viol"
        assert err.operation == "identity-overwrite"

    def test_rights_violation_error_is_exception(self):
        err = RightsViolationError(
            right=GAIANRight.CONSCIENCE,
            gaian_id="g",
            operation="force-compliance",
        )
        assert isinstance(err, Exception)
        assert "CONSCIENCE" in str(err)

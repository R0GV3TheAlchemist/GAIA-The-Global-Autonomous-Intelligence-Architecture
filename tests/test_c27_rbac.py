# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
Tests for core.c27.rbac — C27Role, PermissionEnvelope, RBACEnforcer.

Authority: C27 §8. Implements C27-IMPL-039 through C27-IMPL-045.

Coverage targets:
- All 6 C27Role values exist
- PermissionEnvelope: each role has a non-empty default envelope
- Least-privilege: THIRD_PARTY envelope is strictest (fewest permissions)
- GAIAN_SELF envelope contains SELF_READ and SELF_WRITE
- SENTINEL envelope contains AUDIT_READ and HALT_SIGNAL
- STEWARD envelope contains BOND_WRITE and LIFECYCLE_WRITE
- RBACEnforcer.check() grants access for matching permission
- RBACEnforcer.check() denies access for missing permission
- Privilege escalation attempt is denied and logged to audit
- Role boundary: no role may grant permissions above its own envelope
"""
import pytest
from core.c27.rbac import (
    C27Role,
    PermissionEnvelope,
    RBACEnforcer,
    PrivilegeEscalationError,
    ROLE_ENVELOPES,
    AccessResult,
)


# ---------------------------------------------------------------------------
# C27Role enum — 6 roles  (C27 §8.1)
# ---------------------------------------------------------------------------

class TestC27RoleEnum:
    def test_six_roles_exist(self):
        roles = {r.value for r in C27Role}
        assert roles == {
            "GAIAN_SELF",
            "STEWARD",
            "SENTINEL",
            "COUNCIL_MEMBER",
            "OBSERVER",
            "THIRD_PARTY",
        }


# ---------------------------------------------------------------------------
# PermissionEnvelope defaults  (C27 §8.2)
# ---------------------------------------------------------------------------

class TestPermissionEnvelopeDefaults:
    def test_all_roles_have_non_empty_envelope(self):
        for role in C27Role:
            envelope = ROLE_ENVELOPES[role]
            assert len(envelope.permissions) > 0, (
                f"{role.value} must have at least one default permission"
            )

    def test_third_party_has_fewest_permissions(self):
        third_party_count = len(ROLE_ENVELOPES[C27Role.THIRD_PARTY].permissions)
        for role in C27Role:
            if role == C27Role.THIRD_PARTY:
                continue
            assert len(ROLE_ENVELOPES[role].permissions) >= third_party_count

    def test_gaian_self_has_self_read_and_write(self):
        envelope = ROLE_ENVELOPES[C27Role.GAIAN_SELF]
        assert "SELF_READ" in envelope.permissions
        assert "SELF_WRITE" in envelope.permissions

    def test_sentinel_has_audit_read_and_halt_signal(self):
        envelope = ROLE_ENVELOPES[C27Role.SENTINEL]
        assert "AUDIT_READ" in envelope.permissions
        assert "HALT_SIGNAL" in envelope.permissions

    def test_steward_has_bond_write_and_lifecycle_write(self):
        envelope = ROLE_ENVELOPES[C27Role.STEWARD]
        assert "BOND_WRITE" in envelope.permissions
        assert "LIFECYCLE_WRITE" in envelope.permissions

    def test_third_party_lacks_audit_read(self):
        envelope = ROLE_ENVELOPES[C27Role.THIRD_PARTY]
        assert "AUDIT_READ" not in envelope.permissions

    def test_third_party_lacks_halt_signal(self):
        envelope = ROLE_ENVELOPES[C27Role.THIRD_PARTY]
        assert "HALT_SIGNAL" not in envelope.permissions


# ---------------------------------------------------------------------------
# RBACEnforcer  (C27 §8.3)
# ---------------------------------------------------------------------------

@pytest.fixture
def enforcer():
    return RBACEnforcer()


class TestRBACEnforcer:
    def test_check_grants_permitted_action(self, enforcer):
        result = enforcer.check(
            role=C27Role.SENTINEL,
            permission="AUDIT_READ",
            gaian_id="gaian-001",
            requestor_id="sentinel-proc",
        )
        assert isinstance(result, AccessResult)
        assert result.granted is True
        assert result.permission == "AUDIT_READ"

    def test_check_denies_unpermitted_action(self, enforcer):
        result = enforcer.check(
            role=C27Role.THIRD_PARTY,
            permission="HALT_SIGNAL",
            gaian_id="gaian-001",
            requestor_id="external-actor",
        )
        assert isinstance(result, AccessResult)
        assert result.granted is False

    def test_privilege_escalation_raises_and_logs(self, enforcer):
        """Attempting to use a permission above one's role envelope must raise."""
        with pytest.raises(PrivilegeEscalationError) as exc_info:
            enforcer.check(
                role=C27Role.OBSERVER,
                permission="LIFECYCLE_WRITE",
                gaian_id="gaian-001",
                requestor_id="observer-sneaky",
                raise_on_escalation=True,
            )
        err = exc_info.value
        assert err.role         == C27Role.OBSERVER
        assert err.permission   == "LIFECYCLE_WRITE"
        assert err.requestor_id == "observer-sneaky"

    def test_role_cannot_grant_above_own_envelope(self, enforcer):
        """A STEWARD cannot delegate HALT_SIGNAL which exceeds their envelope."""
        with pytest.raises(PrivilegeEscalationError):
            enforcer.delegate(
                from_role=C27Role.STEWARD,
                to_role=C27Role.OBSERVER,
                permission="HALT_SIGNAL",
            )

    def test_escalation_attempt_recorded_in_audit(self, enforcer):
        """Escalation attempts must be recorded in the enforcer's internal log."""
        try:
            enforcer.check(
                role=C27Role.OBSERVER,
                permission="LIFECYCLE_WRITE",
                gaian_id="gaian-rbac-audit",
                requestor_id="observer-sneaky",
                raise_on_escalation=True,
            )
        except PrivilegeEscalationError:
            pass
        assert any(
            e.get("event_type") == "PRIVILEGE_ESCALATION_ATTEMPT"
            and e.get("gaian_id") == "gaian-rbac-audit"
            for e in enforcer._escalation_log
        )


# ---------------------------------------------------------------------------
# Least-privilege contraction  (C27 §8.4)
# ---------------------------------------------------------------------------

class TestLeastPrivilegeContraction:
    def test_contract_removes_specified_permissions(self):
        enforcer = RBACEnforcer()
        contracted = enforcer.contract_envelope(
            role=C27Role.STEWARD,
            remove_permissions={"LIFECYCLE_WRITE"},
            reason="Temporary restriction",
        )
        assert "LIFECYCLE_WRITE" not in contracted.permissions
        assert "BOND_WRITE" in contracted.permissions  # others retained

    def test_contraction_is_scoped_not_global(self):
        """Contraction for one gaian_id must not affect global ROLE_ENVELOPES."""
        enforcer = RBACEnforcer()
        enforcer.contract_envelope(
            role=C27Role.STEWARD,
            remove_permissions={"LIFECYCLE_WRITE"},
            reason="Scoped restriction",
            gaian_id="gaian-scoped",
        )
        global_envelope = ROLE_ENVELOPES[C27Role.STEWARD]
        assert "LIFECYCLE_WRITE" in global_envelope.permissions

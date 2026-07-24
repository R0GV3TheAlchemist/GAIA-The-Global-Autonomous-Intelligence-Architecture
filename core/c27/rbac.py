# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
core.c27.rbac — Role-Based Access Control for C27 GAIAN governance

Authority: C27 §8

Implementation targets:
  C27-IMPL-039  C27Role enum (6 roles)
  C27-IMPL-040  PermissionEnvelope + ROLE_ENVELOPES defaults
  C27-IMPL-041  RBACEnforcer.check()
  C27-IMPL-042  PrivilegeEscalationError + raise_on_escalation
  C27-IMPL-043  RBACEnforcer.delegate()
  C27-IMPL-044  Escalation audit logging (stub — wired in audit_log layer)
  C27-IMPL-045  RBACEnforcer.contract_envelope()
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, Optional, Set


# ---------------------------------------------------------------------------
# C27-IMPL-039 — C27Role
# ---------------------------------------------------------------------------

class C27Role(str, Enum):
    """The six authorised roles in C27 §8.1."""

    GAIAN_SELF    = "GAIAN_SELF"
    STEWARD       = "STEWARD"
    SENTINEL      = "SENTINEL"
    COUNCIL_MEMBER = "COUNCIL_MEMBER"
    OBSERVER      = "OBSERVER"
    THIRD_PARTY   = "THIRD_PARTY"


# ---------------------------------------------------------------------------
# C27-IMPL-040 — PermissionEnvelope + ROLE_ENVELOPES
# ---------------------------------------------------------------------------

@dataclass
class PermissionEnvelope:
    role: C27Role
    permissions: Set[str] = field(default_factory=set)


# Canonical permission constants (referenced by tests)
_P = {
    "SELF_READ", "SELF_WRITE",
    "AUDIT_READ", "HALT_SIGNAL",
    "BOND_WRITE", "LIFECYCLE_WRITE",
    "OBSERVE_READ", "COUNCIL_VOTE", "COUNCIL_READ",
    "EXTERNAL_QUERY",
}

ROLE_ENVELOPES: Dict[C27Role, PermissionEnvelope] = {
    C27Role.GAIAN_SELF: PermissionEnvelope(
        role=C27Role.GAIAN_SELF,
        permissions={
            "SELF_READ", "SELF_WRITE", "OBSERVE_READ",
        },
    ),
    C27Role.STEWARD: PermissionEnvelope(
        role=C27Role.STEWARD,
        permissions={
            "BOND_WRITE", "LIFECYCLE_WRITE",
            "SELF_READ", "OBSERVE_READ",
        },
    ),
    C27Role.SENTINEL: PermissionEnvelope(
        role=C27Role.SENTINEL,
        permissions={
            "AUDIT_READ", "HALT_SIGNAL",
            "OBSERVE_READ", "LIFECYCLE_WRITE",
        },
    ),
    C27Role.COUNCIL_MEMBER: PermissionEnvelope(
        role=C27Role.COUNCIL_MEMBER,
        permissions={
            "COUNCIL_VOTE", "COUNCIL_READ",
            "AUDIT_READ", "OBSERVE_READ",
        },
    ),
    C27Role.OBSERVER: PermissionEnvelope(
        role=C27Role.OBSERVER,
        permissions={
            "OBSERVE_READ",
        },
    ),
    C27Role.THIRD_PARTY: PermissionEnvelope(
        role=C27Role.THIRD_PARTY,
        permissions={
            "EXTERNAL_QUERY",
        },
    ),
}


# ---------------------------------------------------------------------------
# C27-IMPL-042 — PrivilegeEscalationError
# ---------------------------------------------------------------------------

class PrivilegeEscalationError(Exception):
    """Raised when an actor attempts to use a permission above their role envelope."""

    def __init__(self, role: C27Role, permission: str, requestor_id: str) -> None:
        self.role         = role
        self.permission   = permission
        self.requestor_id = requestor_id
        super().__init__(
            f"[C27 RBAC] Privilege escalation attempt: role={role.value} "
            f"does not hold permission='{permission}' (requestor={requestor_id})"
        )


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class AccessResult:
    granted: bool
    role: C27Role
    permission: str
    requestor_id: str


@dataclass
class DelegationResult:
    delegated: bool
    from_role: C27Role
    to_role: C27Role
    permission: str


# ---------------------------------------------------------------------------
# C27-IMPL-041/043/045 — RBACEnforcer
# ---------------------------------------------------------------------------

class RBACEnforcer:
    """
    Enforces C27 §8 role-based access control.

    Scoped envelope contractions are stored per (gaian_id, role) and do not
    mutate the global ROLE_ENVELOPES map.
    """

    def __init__(self) -> None:
        # {(gaian_id, role): PermissionEnvelope}  — scoped contractions only
        self._scoped: Dict[tuple, PermissionEnvelope] = {}
        self._escalation_log: list = []

    # ------------------------------------------------------------------
    # check  (C27-IMPL-041 / 042)
    # ------------------------------------------------------------------

    def check(
        self,
        role: C27Role,
        permission: str,
        gaian_id: str,
        requestor_id: str,
        raise_on_escalation: bool = False,
    ) -> AccessResult:
        """Return AccessResult; optionally raise PrivilegeEscalationError."""
        envelope = self._resolve_envelope(role, gaian_id)
        granted = permission in envelope.permissions

        if not granted and raise_on_escalation:
            self._log_escalation(role, permission, requestor_id, gaian_id)
            raise PrivilegeEscalationError(
                role=role,
                permission=permission,
                requestor_id=requestor_id,
            )

        return AccessResult(
            granted=granted,
            role=role,
            permission=permission,
            requestor_id=requestor_id,
        )

    # ------------------------------------------------------------------
    # delegate  (C27-IMPL-043)
    # ------------------------------------------------------------------

    def delegate(
        self,
        from_role: C27Role,
        to_role: C27Role,
        permission: str,
    ) -> DelegationResult:
        """Delegate a permission from one role to another.
        Raises PrivilegeEscalationError if the delegating role does not hold
        the permission in its own envelope.
        """
        from_envelope = ROLE_ENVELOPES[from_role]
        if permission not in from_envelope.permissions:
            raise PrivilegeEscalationError(
                role=from_role,
                permission=permission,
                requestor_id=f"delegation:{from_role.value}->{to_role.value}",
            )
        return DelegationResult(
            delegated=True,
            from_role=from_role,
            to_role=to_role,
            permission=permission,
        )

    # ------------------------------------------------------------------
    # contract_envelope  (C27-IMPL-045)
    # ------------------------------------------------------------------

    def contract_envelope(
        self,
        role: C27Role,
        remove_permissions: Set[str],
        reason: str,
        gaian_id: Optional[str] = None,
    ) -> PermissionEnvelope:
        """Return a contracted copy of the role envelope with permissions removed.
        When gaian_id is supplied, the contraction is stored as a scoped override
        and does NOT mutate the global ROLE_ENVELOPES map.
        """
        base = copy.deepcopy(ROLE_ENVELOPES[role])
        base.permissions -= remove_permissions

        if gaian_id is not None:
            self._scoped[(gaian_id, role)] = base

        return base

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_envelope(self, role: C27Role, gaian_id: str) -> PermissionEnvelope:
        return self._scoped.get((gaian_id, role), ROLE_ENVELOPES[role])

    def _log_escalation(
        self, role: C27Role, permission: str, requestor_id: str, gaian_id: str
    ) -> None:
        self._escalation_log.append({
            "event_type": "PRIVILEGE_ESCALATION_ATTEMPT",
            "role": role.value,
            "permission": permission,
            "requestor_id": requestor_id,
            "gaian_id": gaian_id,
        })

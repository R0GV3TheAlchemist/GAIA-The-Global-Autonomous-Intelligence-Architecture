# core/ontology/permissions.py
# C416 fix: set comprehension `{c for c in Capability}` → `set(Capability)`
# Additions: PermissionEnvelope, AuditEntry, AuditTrail, PermissionDeniedError
# These were referenced by core/ontology/__init__.py and 7 test modules
# but were never defined here during the ontology refactor.

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class Capability(Enum):
    """All capabilities a GAIA agent may be granted."""
    READ_CANON            = auto()
    WRITE_MEMORY          = auto()
    DELETE_MEMORY         = auto()
    EXPORT_DATA           = auto()
    INVOKE_SENTINEL       = auto()
    ISSUE_HALT            = auto()
    MODIFY_STATE          = auto()
    DEGRADE_ATLAS_NODE    = auto()
    BROADCAST_COLLECTIVE  = auto()
    OVERRIDE_CANON        = auto()


class PermissionTier(Enum):
    """Trust tiers governing permission grants."""
    GUEST     = 0
    GAIAN     = 1
    GUARDIAN  = 2
    SOVEREIGN = 3


PERMISSION_MAP: dict[PermissionTier, set[Capability]] = {
    PermissionTier.GUEST: {
        Capability.READ_CANON,
    },
    PermissionTier.GAIAN: {
        Capability.READ_CANON,
        Capability.WRITE_MEMORY,
        Capability.EXPORT_DATA,
    },
    PermissionTier.GUARDIAN: {
        Capability.READ_CANON,
        Capability.WRITE_MEMORY,
        Capability.DELETE_MEMORY,
        Capability.EXPORT_DATA,
        Capability.INVOKE_SENTINEL,
        Capability.ISSUE_HALT,
        Capability.MODIFY_STATE,
        Capability.DEGRADE_ATLAS_NODE,
    },
    # C416 fix: `set(Capability)` replaces `{c for c in Capability}`
    PermissionTier.SOVEREIGN: set(Capability),
}


def has_permission(tier: PermissionTier, capability: Capability) -> bool:
    """Return True if the given tier grants the given capability."""
    return capability in PERMISSION_MAP.get(tier, set())


# ---------------------------------------------------------------------------
# PermissionDeniedError
# ---------------------------------------------------------------------------

class PermissionDeniedError(PermissionError):
    """
    Raised when a principal attempts an action that exceeds their
    PermissionTier or lacks the required Capability.

    Attributes:
        principal:  Identifier of the requesting entity.
        capability: The Capability that was denied.
        tier:       The PermissionTier of the requesting principal.
        context:    Optional dict of additional diagnostic context.
    """

    def __init__(
        self,
        message: str = "Permission denied",
        *,
        principal: Optional[str] = None,
        capability: Optional[Capability] = None,
        tier: Optional[PermissionTier] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.principal = principal
        self.capability = capability
        self.tier = tier
        self.context = context or {}

    def __repr__(self) -> str:
        return (
            f"PermissionDeniedError("
            f"principal={self.principal!r}, "
            f"capability={self.capability}, "
            f"tier={self.tier})"
        )


# ---------------------------------------------------------------------------
# AuditEntry — a single auditable event
# ---------------------------------------------------------------------------

@dataclass
class AuditEntry:
    """
    One auditable event in the GAIA permission system.

    Fields:
        principal:   Who made the request (gaian_id, agent_id, or system label).
        capability:  Which Capability was exercised or attempted.
        tier:        The PermissionTier of the principal at the time.
        granted:     True if the action was permitted, False if denied.
        resource:    Optional identifier of the resource acted upon.
        context:     Optional free-form dict for additional metadata.
        timestamp:   Unix timestamp of the event (defaults to now).
    """
    principal: str
    capability: Capability
    tier: PermissionTier
    granted: bool
    resource: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "principal": self.principal,
            "capability": self.capability.name,
            "tier": self.tier.name,
            "granted": self.granted,
            "resource": self.resource,
            "context": self.context,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# AuditTrail — an ordered sequence of AuditEntry records
# ---------------------------------------------------------------------------

@dataclass
class AuditTrail:
    """
    An ordered, append-only trail of AuditEntry records.

    Provides:
        - append()   : add an entry
        - filter()   : retrieve entries matching criteria
        - denied()   : shortcut to retrieve all denied entries
        - to_list()  : serialise to list of dicts
    """
    entries: List[AuditEntry] = field(default_factory=list)

    def append(self, entry: AuditEntry) -> None:
        """Append a new AuditEntry to the trail."""
        self.entries.append(entry)

    def record(
        self,
        principal: str,
        capability: Capability,
        tier: PermissionTier,
        granted: bool,
        resource: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """
        Convenience method: construct and append an AuditEntry in one call.
        Returns the new entry.
        """
        entry = AuditEntry(
            principal=principal,
            capability=capability,
            tier=tier,
            granted=granted,
            resource=resource,
            context=context or {},
        )
        self.entries.append(entry)
        return entry

    def filter(
        self,
        *,
        principal: Optional[str] = None,
        capability: Optional[Capability] = None,
        granted: Optional[bool] = None,
    ) -> List[AuditEntry]:
        """Return entries matching all supplied criteria."""
        result = self.entries
        if principal is not None:
            result = [e for e in result if e.principal == principal]
        if capability is not None:
            result = [e for e in result if e.capability == capability]
        if granted is not None:
            result = [e for e in result if e.granted == granted]
        return result

    def denied(self) -> List[AuditEntry]:
        """Return all denied entries."""
        return self.filter(granted=False)

    def to_list(self) -> List[Dict[str, Any]]:
        """Serialise all entries to a list of dicts."""
        return [e.to_dict() for e in self.entries]

    def __len__(self) -> int:
        return len(self.entries)


# ---------------------------------------------------------------------------
# PermissionEnvelope — a principal’s complete permission context
# ---------------------------------------------------------------------------

@dataclass
class PermissionEnvelope:
    """
    The complete permission context for a single principal (GAIAN, agent, or system).

    Bundles together:
        - The principal’s identifier and trust tier
        - Their effective capability set (derived from tier + any grants/revocations)
        - An AuditTrail recording every permission check

    Immutable after construction except through grant()/revoke().
    """
    principal: str
    tier: PermissionTier
    _extra_grants: set[Capability] = field(default_factory=set, repr=False)
    _revocations: set[Capability] = field(default_factory=set, repr=False)
    audit_trail: AuditTrail = field(default_factory=AuditTrail, repr=False)

    @property
    def capabilities(self) -> set[Capability]:
        """Effective capabilities: tier map + grants − revocations."""
        base = PERMISSION_MAP.get(self.tier, set())
        return (base | self._extra_grants) - self._revocations

    def can(self, capability: Capability, resource: Optional[str] = None) -> bool:
        """
        Check if this principal has the given capability.
        Records the check in the audit trail.
        """
        granted = capability in self.capabilities
        self.audit_trail.record(
            principal=self.principal,
            capability=capability,
            tier=self.tier,
            granted=granted,
            resource=resource,
        )
        return granted

    def require(self, capability: Capability, resource: Optional[str] = None) -> None:
        """
        Assert that this principal has the given capability.
        Raises PermissionDeniedError if not.
        """
        if not self.can(capability, resource=resource):
            raise PermissionDeniedError(
                f"{self.principal!r} lacks {capability.name} (tier={self.tier.name})",
                principal=self.principal,
                capability=capability,
                tier=self.tier,
                context={"resource": resource},
            )

    def grant(self, capability: Capability) -> "PermissionEnvelope":
        """Grant an additional capability beyond the tier baseline."""
        self._extra_grants.add(capability)
        self._revocations.discard(capability)
        return self

    def revoke(self, capability: Capability) -> "PermissionEnvelope":
        """Revoke a capability (overrides both tier and extra grants)."""
        self._revocations.add(capability)
        self._extra_grants.discard(capability)
        return self

    @classmethod
    def for_principal(
        cls,
        principal: str,
        tier: PermissionTier,
    ) -> "PermissionEnvelope":
        """Factory: construct a PermissionEnvelope for a principal at the given tier."""
        return cls(principal=principal, tier=tier)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "principal": self.principal,
            "tier": self.tier.name,
            "capabilities": [c.name for c in sorted(self.capabilities, key=lambda c: c.name)],
            "extra_grants": [c.name for c in self._extra_grants],
            "revocations": [c.name for c in self._revocations],
        }

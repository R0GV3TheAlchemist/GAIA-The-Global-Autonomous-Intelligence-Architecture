# core/ontology/permissions.py
# C416 fix: set comprehension `{c for c in Capability}` → `set(Capability)`
# All other logic in this file is unchanged.

from __future__ import annotations

from enum import Enum, auto


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

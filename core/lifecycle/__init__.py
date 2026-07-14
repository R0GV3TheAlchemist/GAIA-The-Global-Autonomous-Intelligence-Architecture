"""
core/lifecycle/__init__.py
C27 Phase 1 + Phase 2 + Phase 3 exports
"""

from .gaian_lifecycle_state import GAIANLifecycleState, LifecycleTransitionError, VALID_TRANSITIONS
from .lifecycle_manager import LifecycleManager
from .stewardship import StewardRole, StewardshipBond, StewardshipRegistry
from .lifecycle_audit_logger import LifecycleAuditLogger, LifecycleEvent
from .adoption_queue import AdoptionQueue, AdoptionQueueEntry, AdoptionVisibility
from .compliance_sentinel import (
    ComplianceSentinel, SentinelFinding, SentinelSeverity, SentinelCheckID,
)
from .permissions import PermissionManager, PermissionEnvelope, LifecycleRole
from .ed25519_audit import CanonicalAuditEntry, AuditSignature, Phase2Ed25519BridgeSigner
from .retirement_engine import RetirementEngine, RetirementReason, RetirementRecord, LegacyPackage
from .signing import (
    GAIASecretVault, InProcessVault, VaultKeyNotFoundError,
    Ed25519LifecycleSigner, RemoteVaultAdapter,
)
from .repositories import (
    LifecycleRepository, InMemoryLifecycleRepository,
    StewardshipRepository, InMemoryStewardshipRepository,
)

__all__ = [
    # State machine
    "GAIANLifecycleState", "LifecycleTransitionError", "VALID_TRANSITIONS",
    # Manager
    "LifecycleManager",
    # Stewardship
    "StewardRole", "StewardshipBond", "StewardshipRegistry",
    # Audit
    "LifecycleAuditLogger", "LifecycleEvent",
    "CanonicalAuditEntry", "AuditSignature", "Phase2Ed25519BridgeSigner",
    # Adoption
    "AdoptionQueue", "AdoptionQueueEntry", "AdoptionVisibility",
    # Compliance
    "ComplianceSentinel", "SentinelFinding", "SentinelSeverity", "SentinelCheckID",
    # Permissions
    "PermissionManager", "PermissionEnvelope", "LifecycleRole",
    # Retirement
    "RetirementEngine", "RetirementReason", "RetirementRecord", "LegacyPackage",
    # Signing
    "GAIASecretVault", "InProcessVault", "VaultKeyNotFoundError",
    "Ed25519LifecycleSigner", "RemoteVaultAdapter",
    # Repositories
    "LifecycleRepository", "InMemoryLifecycleRepository",
    "StewardshipRepository", "InMemoryStewardshipRepository",
]

"""nexusos.kernel

NEXUS Microkernel Core

Implements the capability-based microkernel following seL4's design
principle: the kernel provides *mechanisms*, not *policy*. The kernel
mints CapabilityTokens, initialises the HALRegistry, MemoryBroker, and
RTScheduler, then yields control to userspace servers.

CapabilityToken is an immutable, unforgeable token that simultaneously
names a kernel object and encodes permitted operations on it — modelled
directly after seL4's capability derivation model (Manual v15, Ch.2).

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 1.1 - NexusKernel
Research reference:
    seL4 Reference Manual v15.0.0  - Ch.2-4 (capability derivation, CNode)
    Fuchsia Zircon kernel objects   - Channel, Job, Process as capabilities
    MINIX 3                         - microkernel minimal surface principle
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import FrozenSet, Optional

logger = logging.getLogger("nexusos.kernel")


@dataclass(frozen=True)
class CapabilityToken:
    """An immutable capability token.

    Capabilities are *never* constructed by callers — only minted by
    NexusKernel.mint_capability(). This enforces the seL4 invariant that
    capabilities cannot be forged.

    Fields:
        object_id:      UUID4 naming the kernel object this token grants access to.
        permitted_ops:  Frozenset of operation names allowed (e.g. {'read', 'write'}).
        issuer:         Identity string of the issuing kernel context.
        expiry:         Optional UTC datetime after which the token is invalid.
        token_id:       Unique UUID4 for this specific token issuance.
    """
    object_id: str
    permitted_ops: FrozenSet[str]
    issuer: str
    expiry: Optional[datetime] = None
    token_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def is_valid(self) -> bool:
        """Return True if the token has not expired."""
        if self.expiry is None:
            return True
        return datetime.now(timezone.utc) < self.expiry

    def permits(self, operation: str) -> bool:
        """Return True if this token permits the given operation."""
        return operation in self.permitted_ops


class NexusKernel:
    """The NEXUS capability-based microkernel.

    Responsibilities:
        - Mint CapabilityTokens for kernel objects.
        - Initialise the HALRegistry, MemoryBroker, and RTScheduler.
        - Provide the minimal IPC dispatch surface.
        - Yield control to userspace servers after boot.

    The kernel provides *mechanisms* only. Policy (scheduling priorities,
    memory quotas, access control rules) belongs to userspace services.

    Reference:
        seL4 Manual v15 — the kernel is not trusted to enforce policy.
        MINIX 3 — userspace server model for drivers and services.
    """

    def __init__(self) -> None:
        self._booted: bool = False
        logger.info("NexusKernel instantiated (not yet booted).")

    def boot(self) -> None:
        """Boot the microkernel: initialise HALRegistry, MemoryBroker, RTScheduler.

        After boot(), the kernel is ready to mint capabilities and dispatch IPC.
        Calling boot() more than once is a no-op with a warning.

        Raises:
            NotImplementedError: Full boot sequence not yet implemented.
                Expected: initialise HALRegistry(), MemoryBroker(), RTScheduler(),
                then set self._booted = True and yield to init server.
        """
        if self._booted:
            logger.warning("NexusKernel.boot() called on already-booted kernel.")
            return
        raise NotImplementedError(
            "NexusKernel.boot() not yet implemented. "
            "Expected: init HALRegistry, MemoryBroker, RTScheduler, set _booted=True."
        )

    def mint_capability(
        self,
        object_id: str,
        permitted_ops: FrozenSet[str],
        issuer: str,
        expiry: Optional[datetime] = None,
    ) -> CapabilityToken:
        """Mint a new CapabilityToken for a kernel object.

        Args:
            object_id:     UUID or name of the kernel object.
            permitted_ops: Frozenset of allowed operation names.
            issuer:        Identity of the requesting kernel context.
            expiry:        Optional expiry datetime (UTC).

        Returns:
            A new immutable CapabilityToken.

        Note:
            This is the *only* legitimate path to creating a CapabilityToken.
            Callers must not construct CapabilityToken directly.
        """
        token = CapabilityToken(
            object_id=object_id,
            permitted_ops=permitted_ops,
            issuer=issuer,
            expiry=expiry,
        )
        logger.debug(
            "NexusKernel minted capability %s for object %s (ops=%s).",
            token.token_id,
            object_id,
            permitted_ops,
        )
        return token

    def revoke_capability(self, token: CapabilityToken) -> None:
        """Revoke a previously minted CapabilityToken.

        Args:
            token: The CapabilityToken to revoke.

        Raises:
            NotImplementedError: Revocation ledger not yet implemented.
                Expected: record token_id in a revocation set,
                update is_valid() to check revocation set.
        """
        raise NotImplementedError(
            "NexusKernel.revoke_capability() not yet implemented. "
            "Expected: maintain a revocation ledger (set of token_ids), "
            "check it in CapabilityToken.is_valid()."
        )

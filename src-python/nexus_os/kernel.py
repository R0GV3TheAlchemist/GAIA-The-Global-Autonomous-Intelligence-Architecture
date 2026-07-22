"""
nexus_os.kernel — NEXUS Microkernel

The NexusKernel is the minimal, formally-inspired microkernel at the root of
all NEXUS OS instances. Its sole responsibilities are:
  1. Capability minting and revocation
  2. Process lifecycle: spawn, terminate, reap
  3. Delegation to RTScheduler and MemoryBroker
  4. Kernel-level audit logging of all privileged operations

No policy is encoded here. Policy lives in userspace servers and in the
governance layer (GOVERNANCE.md). The kernel provides mechanisms only.

Design references:
  - seL4 microkernel — capability-based access control, formal verification
  - MINIX 3 reincarnation server pattern for process recovery
  - NEXUS_UNIVERSAL_OS.md Domain 1.1 — Kernel Design Principles
Ethics reference: ETHICS.md Prohibition 6 — No Unaudited Privilege Escalation
GAIAN law:        GAIAN_LAWS.md Law III — No Silent Override
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import FrozenSet, Optional

logger = logging.getLogger("nexus_os.kernel")


@dataclass(frozen=True)
class CapabilityToken:
    """An unforgeable, immutable token representing the right to perform a
    specific set of operations on a specific kernel object.

    CapabilityTokens are never constructed directly by callers. They are
    minted exclusively by NexusKernel.mint_capability and are bound to a
    single object_id. Possession of a token IS the permission — no separate
    ACL lookup is required. Immutability is enforced by frozen=True.
    Reference: seL4 capability derivation; NEXUS_UNIVERSAL_OS.md 1.1
    """
    token_id:      str                # Unique identifier for this token (UUID4)
    object_id:     str                # The kernel object this token grants access to
    permitted_ops: FrozenSet[str]     # Set of permitted operation names
    issuer:        str                # ID of the process that caused minting
    issued_at:     datetime           # UTC timestamp of minting
    expiry:        Optional[datetime] = None  # None = non-expiring

    def allows(self, operation: str) -> bool:
        """Return True if this token permits the named operation."""
        return operation in self.permitted_ops

    def is_expired(self) -> bool:
        """Return True if this token has passed its expiry time."""
        if self.expiry is None:
            return False
        return datetime.now(timezone.utc) > self.expiry

    def __str__(self) -> str:
        return (
            f"CapabilityToken(object={self.object_id}, "
            f"ops={sorted(self.permitted_ops)}, issuer={self.issuer})"
        )


class ProcessState(Enum):
    """Lifecycle states for a NEXUS OS process."""
    NASCENT    = auto()  # Created but not yet scheduled
    RUNNING    = auto()  # Actively executing
    SUSPENDED  = auto()  # Paused by scheduler or governance
    TERMINATED = auto()  # Completed or killed, awaiting reap
    ZOMBIE     = auto()  # Terminated but token not yet reaped


@dataclass
class ProcessDescriptor:
    """Kernel-side descriptor for a running NEXUS OS process.

    Each process is identified by a unique pid (UUID4 string). The kernel
    maintains a registry of all ProcessDescriptors. No process can acquire
    capabilities without a valid ProcessDescriptor in the kernel registry.
    Reference: NEXUS_UNIVERSAL_OS.md Domain 1.1 — Process Model
    """
    pid:        str            = field(default_factory=lambda: str(uuid.uuid4()))
    name:       str            = "unnamed-process"
    state:      ProcessState   = ProcessState.NASCENT
    owner_id:   str            = "nexus-kernel"
    created_at: datetime       = field(default_factory=lambda: datetime.now(timezone.utc))
    tokens:     list[CapabilityToken] = field(default_factory=list)

    def has_capability(self, object_id: str, operation: str) -> bool:
        """Return True if this process holds a valid, non-expired capability
        token for the given object_id and operation."""
        return any(
            t.object_id == object_id and t.allows(operation) and not t.is_expired()
            for t in self.tokens
        )


class NexusKernel:
    """The NEXUS Universal Operating System microkernel.

    Provides minimal privileged services:
      - Capability minting and revocation
      - Process spawn, suspend, terminate, and reap
      - Audit logging of all privileged operations

    The kernel does NOT implement scheduling, memory allocation, or IPC
    directly. These are delegated to RTScheduler, MemoryBroker, and the
    Channel/Message IPC system respectively.
    Reference: seL4 design philosophy; NEXUS_UNIVERSAL_OS.md Domain 1
    """

    def __init__(self) -> None:
        self._processes: dict[str, ProcessDescriptor] = {}
        self.booted: bool = False
        logger.info("NexusKernel instance created — not yet booted.")

    def boot(self) -> None:
        """Execute the NEXUS kernel boot sequence.

        Initializes the process registry, registers the kernel itself as
        PID-0, and marks the kernel as booted. Must be called exactly once
        before any other kernel operation.
        Raises:
            RuntimeError: If boot is called more than once.
        Reference: NEXUS_UNIVERSAL_OS.md Domain 1 — Boot Sequence
        """
        raise NotImplementedError(
            "NexusKernel.boot — kernel boot sequence not yet implemented. "
            "Expected: initialize process registry, register PID-0 kernel "
            "process, confirm HALRegistry populated, set self.booted = True."
        )

    def mint_capability(
        self,
        object_id: str,
        permitted_ops: FrozenSet[str],
        issuer_pid: str,
        expiry: Optional[datetime] = None,
    ) -> CapabilityToken:
        """Mint a new CapabilityToken for the given object and operations.

        Args:
            object_id:     The kernel object ID this token grants access to.
            permitted_ops: Frozenset of permitted operation name strings.
            issuer_pid:    PID of the process requesting the minting.
            expiry:        Optional UTC expiry datetime. None = non-expiring.
        Returns:
            A new, immutable CapabilityToken.
        Raises:
            NotImplementedError: Always (stub).
        Reference: seL4 CNode.Mint; NEXUS_UNIVERSAL_OS.md 1.1
        """
        raise NotImplementedError(
            "NexusKernel.mint_capability — not yet implemented. "
            "Expected: validate issuer_pid in process registry, construct "
            "CapabilityToken(token_id=uuid4(), ...), log audit event, return token."
        )

    def spawn(self, name: str, owner_id: str) -> ProcessDescriptor:
        """Spawn a new NEXUS OS process and register it with the kernel.

        Raises:
            NotImplementedError: Always (stub).
        Reference: NEXUS_UNIVERSAL_OS.md Domain 1.1 — Process Lifecycle
        """
        raise NotImplementedError(
            "NexusKernel.spawn — not yet implemented. "
            "Expected: create ProcessDescriptor, add to self._processes, "
            "log audit event, return descriptor."
        )

    def terminate(self, pid: str, reason: str = "requested") -> None:
        """Terminate a running process by PID.

        Raises:
            NotImplementedError: Always (stub).
        Reference: GAIAN_LAWS.md Law III — No Silent Override
        """
        raise NotImplementedError(
            "NexusKernel.terminate — not yet implemented. "
            "Expected: set descriptor.state = ProcessState.TERMINATED, "
            "invalidate all tokens, log audit event with reason."
        )

    def reap(self, pid: str) -> ProcessDescriptor:
        """Remove a TERMINATED process descriptor from the kernel registry.

        Raises:
            NotImplementedError: Always (stub).
        """
        raise NotImplementedError(
            "NexusKernel.reap — not yet implemented. "
            "Expected: assert state == TERMINATED, pop from self._processes, return."
        )

    def list_processes(self) -> list[ProcessDescriptor]:
        """Return a snapshot of all currently registered process descriptors."""
        raise NotImplementedError(
            "NexusKernel.list_processes — not yet implemented. "
            "Expected: return list(self._processes.values())"
        )

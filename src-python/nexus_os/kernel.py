"""
nexus_os.kernel — NEXUS Microkernel
=====================================
Reference: NEXUS_UNIVERSAL_OS.md § Domain 1 — Kernel Subsystem

Implements the NEXUS microkernel: process lifecycle, capability token
authorisation, and the main dispatch loop.  The kernel is the single
entity permitted to issue CapabilityTokens; all others must request them.

The Constitutional Layer is enforced at kernel boundary — no process
may acquire a capability that violates GAIAN_LAWS.md or ETHICS.md.

© 2026 Kyle Alexander Steen (The Alchemist). All rights reserved.
SPDX-License-Identifier: AGPL-3.0-only
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Dict, FrozenSet, List, Optional, Set


# ---------------------------------------------------------------------------
# Kernel exceptions
# ---------------------------------------------------------------------------

class KernelAlreadyBooted(RuntimeError):
    """Raised when boot() is called on an already-running kernel."""

class KernelNotBooted(RuntimeError):
    """Raised when a kernel operation is attempted before boot()."""

class InvalidProcessState(RuntimeError):
    """Raised when a state transition is illegal for the current ProcessState."""

class ProcessNotFound(KeyError):
    """Raised when no process with the given PID exists in the kernel."""

class ProcessNotTerminated(RuntimeError):
    """Raised when reaping a process that has not yet reached TERMINATED state."""


# ---------------------------------------------------------------------------
# Process state
# ---------------------------------------------------------------------------

class ProcessState(Enum):
    """Lifecycle states for a NEXUS process."""

    INITIALISING = auto()
    READY        = auto()
    RUNNING      = auto()
    BLOCKED      = auto()
    SUSPENDED    = auto()
    TERMINATED   = auto()


# ---------------------------------------------------------------------------
# CapabilityToken
# ---------------------------------------------------------------------------

@dataclass
class CapabilityToken:
    """
    An unforgeable token granting a process a specific capability.

    Tokens are issued only by CapabilityAuthority (capability.py).
    They are non-transferable and expire when the owning process terminates
    or when the token's expiry timestamp passes.

    Reference: NEXUS_UNIVERSAL_OS.md § Domain 5 — Capability System
    """

    token_id:      str                  = field(default_factory=lambda: str(uuid.uuid4()))
    object_id:     str                  = ""         # canonical resource identifier
    permitted_ops: FrozenSet[str]       = field(default_factory=frozenset)
    issuer:        str                  = ""         # PID of issuing process
    issued_at:     datetime             = field(default_factory=lambda: datetime.now(timezone.utc))
    expiry:        Optional[datetime]   = None       # None = process-lifetime

    def allows(self, operation: str) -> bool:
        """Return True if this token permits the given operation."""
        return operation in self.permitted_ops

    def is_expired(self) -> bool:
        """Return True if the token has passed its expiry timestamp."""
        if self.expiry is None:
            return False
        return datetime.now(timezone.utc) >= self.expiry


# ---------------------------------------------------------------------------
# ProcessDescriptor
# ---------------------------------------------------------------------------

@dataclass
class ProcessDescriptor:
    """
    All kernel-visible state for a single NEXUS process.

    Reference: NEXUS_UNIVERSAL_OS.md § Domain 1 — Process Model
    """

    pid:          str          = field(default_factory=lambda: str(uuid.uuid4()))
    name:         str          = ""
    state:        ProcessState = ProcessState.INITIALISING
    capabilities: Set[str]     = field(default_factory=set)   # token_ids
    priority:     int          = 50      # 0 (lowest) – 100 (highest)
    parent_pid:   Optional[str] = None
    children_pids: List[str]   = field(default_factory=list)


# ---------------------------------------------------------------------------
# NexusKernel
# ---------------------------------------------------------------------------

class NexusKernel:
    """
    The NEXUS microkernel.

    Responsibilities:
    - Process spawn, suspend, resume, and termination
    - Capability token issuance and revocation
    - Constitutional Layer enforcement at process boundary
    - Dispatch loop driving the scheduler and IPC subsystems

    Reference: NEXUS_UNIVERSAL_OS.md § Domain 1 — Kernel Subsystem
    """

    def __init__(self) -> None:
        self._processes: Dict[str, ProcessDescriptor] = {}
        self._tokens:    Dict[str, CapabilityToken]   = {}
        self._running:   bool                          = False

    # ------------------------------------------------------------------
    # Process management
    # ------------------------------------------------------------------

    def spawn(
        self,
        name: str,
        priority: int = 50,
        parent_pid: Optional[str] = None,
    ) -> ProcessDescriptor:
        """
        Create and register a new process.

        Raises:
            KernelNotBooted: If the kernel has not been booted.
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError(
            "NexusKernel.spawn: stub — implementation pending (NEXUS_UNIVERSAL_OS.md § Domain 1)"
        )

    def terminate(self, pid: str) -> None:
        """
        Terminate a process and revoke all its capability tokens.

        Raises:
            ProcessNotFound: If no process with pid exists.
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError(
            "NexusKernel.terminate: stub — implementation pending"
        )

    def suspend(self, pid: str) -> None:
        """Suspend a running process.  Raises NotImplementedError (stub)."""
        raise NotImplementedError("NexusKernel.suspend: stub")

    def resume(self, pid: str) -> None:
        """Resume a suspended process.  Raises NotImplementedError (stub)."""
        raise NotImplementedError("NexusKernel.resume: stub")

    # ------------------------------------------------------------------
    # Capability management
    # ------------------------------------------------------------------

    def issue_token(
        self,
        pid: str,
        capability_name: str,
        expires_at_ns: Optional[int] = None,
    ) -> CapabilityToken:
        """
        Issue a capability token to an existing process.

        The Constitutional Layer must approve every token issuance.

        Raises:
            PermissionError: If the Constitutional Layer denies the request.
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError(
            "NexusKernel.issue_token: stub — implementation pending"
        )

    def revoke_token(self, token_id: str) -> None:
        """Revoke a capability token immediately.  Raises NotImplementedError (stub)."""
        raise NotImplementedError("NexusKernel.revoke_token: stub")

    # ------------------------------------------------------------------
    # Kernel lifecycle
    # ------------------------------------------------------------------

    def boot(self) -> None:
        """
        Boot the kernel: initialise subsystems and start the dispatch loop.

        Raises:
            KernelAlreadyBooted: If the kernel is already running.
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError(
            "NexusKernel.boot: stub — implementation pending"
        )

    def shutdown(self) -> None:
        """Gracefully shut down the kernel and all processes.  Raises NotImplementedError (stub)."""
        raise NotImplementedError("NexusKernel.shutdown: stub")

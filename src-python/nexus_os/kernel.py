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

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, FrozenSet, List, Optional, Set


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
# CapabilityToken  (frozen=True → immutable after construction)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CapabilityToken:
    """
    An unforgeable token granting a process a specific capability.

    frozen=True means any attempt to mutate an attribute raises AttributeError.

    Reference: NEXUS_UNIVERSAL_OS.md § Domain 5 — Capability System
    """

    token_id:      str                = field(default_factory=lambda: str(uuid.uuid4()))
    object_id:     str                = ""
    permitted_ops: FrozenSet[str]     = field(default_factory=frozenset)
    issuer:        str                = ""
    issued_at:     datetime           = field(default_factory=lambda: datetime.now(timezone.utc))
    expiry:        Optional[datetime] = None

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

class ProcessDescriptor:
    """
    All kernel-visible state for a single NEXUS process.

    Reference: NEXUS_UNIVERSAL_OS.md § Domain 1 — Process Model
    """

    def __init__(
        self,
        pid: str = "",
        name: str = "",
        state: ProcessState = ProcessState.RUNNING,
        priority: int = 50,
        parent_pid: Optional[str] = None,
    ) -> None:
        self.pid          = pid or str(uuid.uuid4())
        self.name         = name
        self.state        = state
        self.priority     = priority
        self.parent_pid   = parent_pid
        self.children_pids: List[str] = []
        self.tokens: List[CapabilityToken] = []

    def has_capability(self, object_id: str, operation: str) -> bool:
        """Return True if the process holds a valid, non-expired token for object_id+op."""
        for token in self.tokens:
            if token.object_id == object_id and token.allows(operation) and not token.is_expired():
                return True
        return False


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

    KERNEL_PID = "pid-0:nexus-kernel"

    # Root capabilities minted for PID-0 on boot
    _ROOT_CAPS = [
        ("sovereign_memory",  frozenset({"read", "write", "query"})),
        ("affect_engine",     frozenset({"read", "write", "subscribe"})),
        ("schumann_sync",     frozenset({"read", "subscribe"})),
        ("crisis_engine",     frozenset({"read", "write"})),
        ("persona_stability", frozenset({"read", "write"})),
        ("ipc_bus",           frozenset({"send", "receive", "call", "reply"})),
        ("process_manager",   frozenset({"spawn", "terminate", "reap", "suspend", "resume"})),
    ]

    def __init__(
        self,
        authority: Any = None,
        ledger: Any = None,
    ) -> None:
        self._authority = authority
        self._ledger    = ledger
        self._processes: Dict[str, ProcessDescriptor] = {}
        self._booted    = False
        self._lock      = threading.RLock()
        self._audit_log: List[Any] = []

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def booted(self) -> bool:
        return self._booted

    @property
    def audit_log(self) -> List[Any]:
        """Return the kernel audit log (from CapabilityAuthority)."""
        if self._authority is not None:
            try:
                return self._authority.get_audit_log()
            except Exception:
                pass
        return list(self._audit_log)

    # ------------------------------------------------------------------
    # Kernel lifecycle
    # ------------------------------------------------------------------

    def boot(self) -> None:
        """
        Boot the kernel: initialise the capability authority, create PID-0,
        and mint the root capability set.
        """
        with self._lock:
            if self._booted:
                raise KernelAlreadyBooted("NexusKernel is already booted")

            if self._authority is None:
                from nexus_os.capability import CapabilityAuthority
                self._authority = CapabilityAuthority(ledger=self._ledger)

            pid0 = ProcessDescriptor(
                pid=self.KERNEL_PID,
                name="nexus-kernel",
                state=ProcessState.RUNNING,
                priority=100,
            )

            for object_id, ops in self._ROOT_CAPS:
                token = self._authority.mint(
                    object_id=object_id,
                    permitted_ops=ops,
                    issuer_pid=self.KERNEL_PID,
                    note="kernel-boot root cap",
                )
                pid0.tokens.append(token)

            self._processes[self.KERNEL_PID] = pid0
            self._booted = True

    def shutdown(self) -> None:
        """Gracefully shut down all processes."""
        with self._lock:
            for pid in list(self._processes):
                if pid != self.KERNEL_PID:
                    try:
                        self.terminate(pid, reason="kernel-shutdown")
                    except Exception:
                        pass
            self._booted = False

    # ------------------------------------------------------------------
    # Guards
    # ------------------------------------------------------------------

    def _require_booted(self) -> None:
        if not self._booted:
            raise KernelNotBooted("NexusKernel has not been booted")

    # ------------------------------------------------------------------
    # Process management
    # ------------------------------------------------------------------

    def spawn(
        self,
        name: str,
        owner_id: str = KERNEL_PID,
        priority: int = 50,
        initial_ops: Optional[Dict[str, FrozenSet[str]]] = None,
    ) -> ProcessDescriptor:
        """
        Create and register a new process.
        """
        self._require_booted()
        with self._lock:
            if owner_id not in self._processes:
                raise ProcessNotFound(f"Owner PID '{owner_id}' not found")

            proc = ProcessDescriptor(
                pid=str(uuid.uuid4()),
                name=name,
                state=ProcessState.RUNNING,
                priority=priority,
                parent_pid=owner_id,
            )

            if initial_ops:
                for object_id, ops in initial_ops.items():
                    token = self._authority.mint(
                        object_id=object_id,
                        permitted_ops=ops,
                        issuer_pid=owner_id,
                    )
                    proc.tokens.append(token)

            self._processes[proc.pid] = proc
            self._processes[owner_id].children_pids.append(proc.pid)
            return proc

    def get_process(self, pid: str) -> ProcessDescriptor:
        """Return the ProcessDescriptor for pid."""
        self._require_booted()
        with self._lock:
            if pid not in self._processes:
                raise ProcessNotFound(f"PID '{pid}' not found")
            return self._processes[pid]

    def list_processes(self) -> List[ProcessDescriptor]:
        """Return a snapshot list of all registered processes."""
        self._require_booted()
        with self._lock:
            return list(self._processes.values())

    def terminate(self, pid: str, reason: str = "") -> None:
        """
        Terminate a process and revoke all its capability tokens.
        Idempotent.
        """
        self._require_booted()
        with self._lock:
            if pid not in self._processes:
                raise ProcessNotFound(f"PID '{pid}' not found")
            proc = self._processes[pid]
            if proc.state == ProcessState.TERMINATED:
                return
            proc.state = ProcessState.TERMINATED
            for token in list(proc.tokens):
                try:
                    self._authority.revoke(
                        token.token_id,
                        revoker_pid=self.KERNEL_PID,
                        note=reason or "process-terminated",
                    )
                except Exception:
                    pass

    def reap(self, pid: str) -> None:
        """
        Remove a terminated process from the process table.
        """
        self._require_booted()
        with self._lock:
            if pid not in self._processes:
                raise ProcessNotFound(f"PID '{pid}' not found")
            proc = self._processes[pid]
            if proc.state != ProcessState.TERMINATED:
                raise ProcessNotTerminated(
                    f"Cannot reap PID '{pid}': state is {proc.state.name}, expected TERMINATED"
                )
            del self._processes[pid]

    def suspend(self, pid: str, reason: str = "") -> None:
        """
        Suspend a running process.
        """
        self._require_booted()
        with self._lock:
            if pid not in self._processes:
                raise ProcessNotFound(f"PID '{pid}' not found")
            proc = self._processes[pid]
            if proc.state != ProcessState.RUNNING:
                raise InvalidProcessState(
                    f"Cannot suspend PID '{pid}': state is {proc.state.name}"
                )
            proc.state = ProcessState.SUSPENDED

    def resume(self, pid: str) -> None:
        """
        Resume a suspended process.
        """
        self._require_booted()
        with self._lock:
            if pid not in self._processes:
                raise ProcessNotFound(f"PID '{pid}' not found")
            proc = self._processes[pid]
            if proc.state != ProcessState.SUSPENDED:
                raise InvalidProcessState(
                    f"Cannot resume PID '{pid}': state is {proc.state.name}"
                )
            proc.state = ProcessState.RUNNING

    # ------------------------------------------------------------------
    # Capability management
    # ------------------------------------------------------------------

    def mint_capability(
        self,
        object_id: str,
        permitted_ops: FrozenSet[str],
        issuer_pid: str,
        expiry: Optional[datetime] = None,
    ) -> CapabilityToken:
        """
        Mint a new capability token and register it on the issuing process
        so that terminate() will revoke it when the process ends.
        """
        self._require_booted()
        with self._lock:
            if issuer_pid not in self._processes:
                raise ProcessNotFound(f"Issuer PID '{issuer_pid}' not found")
            token = self._authority.mint(
                object_id=object_id,
                permitted_ops=permitted_ops,
                issuer_pid=issuer_pid,
                expiry=expiry,
            )
            # Track token on the issuing process so terminate() can revoke it
            self._processes[issuer_pid].tokens.append(token)
            return token

    def issue_token(
        self,
        pid: str,
        capability_name: str,
        expires_at_ns: Optional[int] = None,
    ) -> CapabilityToken:
        """Legacy alias for mint_capability with a single 'read' op."""
        return self.mint_capability(
            object_id=capability_name,
            permitted_ops=frozenset({"read"}),
            issuer_pid=pid,
        )

    def revoke_token(self, token_id: str) -> None:
        """Revoke a capability token by its ID."""
        self._require_booted()
        self._authority.revoke(token_id, revoker_pid=self.KERNEL_PID)

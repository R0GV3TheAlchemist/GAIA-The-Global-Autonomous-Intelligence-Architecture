"""
GAIA Process Manager — process isolation, IPC, and execution sovereignty.

Every program running on GAIA lives inside a Process — an isolated execution
container with its own capability set, memory map, and identity. Processes
communicate exclusively through typed IPC channels (Ports), never through
shared mutable state. No process can reach another's memory without an
explicit capability grant.

Design lineage:
  seL4  — capability-based process isolation, IPC via endpoints
  XNU   — Mach tasks + ports, BSD proc, importance donation
  Linux — clone()/fork(), namespaces, cgroups, seccomp

GAIA extends these with:
  - ProcessIdentity: cryptographic principal binding (owner, session, space)
  - CapabilitySet: explicit unforgeable resource grants per process
  - IPC Port model: typed, bounded, non-blocking message channels
  - Intelligence processes: first-class high-priority process kind
"""
from core.os_interface.process_manager.model import (
    ProcessKind,
    ProcessIsolationLevel,
    ProcessIdentity,
    CapabilityGrant,
    CapabilitySet,
    GAIAProcess,
)
from core.os_interface.process_manager.ipc import (
    PortRight,
    IPCMessage,
    IPCPort,
    IPCRouter,
)
from core.os_interface.process_manager.manager import ProcessManager

__all__ = [
    "ProcessKind",
    "ProcessIsolationLevel",
    "ProcessIdentity",
    "CapabilityGrant",
    "CapabilitySet",
    "GAIAProcess",
    "PortRight",
    "IPCMessage",
    "IPCPort",
    "IPCRouter",
    "ProcessManager",
]

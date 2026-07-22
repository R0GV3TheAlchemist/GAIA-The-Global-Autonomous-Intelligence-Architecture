"""nexusos

NEXUS Operating System Kernel Layer

Provides the foundational capability-based microkernel for NEXUS-OS.
This package exports the primary kernel, HAL registry, scheduler, IPC
channel, and memory broker interfaces used by all higher-level NEXUS modules.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  - Domain 1: NexusOS Kernel
    NEXUSARCHITECTURE.md   - Two-tier OS definition

Research reference:
    seL4 Reference Manual v15.0.0  - capability derivation, CNode, endpoints
    Fuchsia Zircon kernel objects   - Channel, Event, Job, VMO as capabilities
    MINIX 3 reincarnation server    - auto-restart pattern for HealthMonitor
"""
from __future__ import annotations

from nexusos.hal import DeviceCapability, HALDriver, HALRegistry
from nexusos.kernel import CapabilityToken, NexusKernel
from nexusos.scheduler import EnergyProfile, RTScheduler, TaskPriority
from nexusos.ipc import Channel, DeliverySemantics, Message
from nexusos.memory import MemoryBroker, MemorySegment

__all__ = [
    "DeviceCapability",
    "HALDriver",
    "HALRegistry",
    "CapabilityToken",
    "NexusKernel",
    "EnergyProfile",
    "RTScheduler",
    "TaskPriority",
    "Channel",
    "DeliverySemantics",
    "Message",
    "MemoryBroker",
    "MemorySegment",
]

"""
nexus_os — NEXUS Universal OS Core Package
==========================================
Reference: NEXUS_UNIVERSAL_OS.md § Domain 1 — OS Foundation Layer

This package implements the microkernel, hardware abstraction, real-time
scheduler, inter-process communication, and capability-based memory manager
for the NEXUS Universal Autonomous Intelligence Architecture.

All behavior is governed by GAIAN_LAWS.md and ETHICS.md.

© 2026 Kyle Alexander Steen (The Alchemist). All rights reserved.
SPDX-License-Identifier: AGPL-3.0-only
"""

__version__ = "0.1.0"
__author__ = "Kyle Alexander Steen"
__copyright__ = "© 2026 Kyle Alexander Steen (The Alchemist). All rights reserved."

from nexus_os.hal import DeviceCapability, HALDriver, HALRegistry
from nexus_os.kernel import NexusKernel, ProcessDescriptor, CapabilityToken
from nexus_os.scheduler import RTScheduler, TaskPriority, EnergyProfile
from nexus_os.ipc import Channel, Message, DeliverySemantics
from nexus_os.memory import MemoryRegion, MemoryBroker

__all__ = [
    # HAL
    "DeviceCapability",
    "HALDriver",
    "HALRegistry",
    # Kernel
    "NexusKernel",
    "ProcessDescriptor",
    "CapabilityToken",
    # Scheduler
    "RTScheduler",
    "TaskPriority",
    "EnergyProfile",
    # IPC
    "Channel",
    "Message",
    "DeliverySemantics",
    # Memory
    "MemoryRegion",
    "MemoryBroker",
]

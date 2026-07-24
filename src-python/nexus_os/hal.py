"""
nexus_os.hal — Hardware Abstraction Layer
=========================================
Reference: NEXUS_UNIVERSAL_OS.md § Domain 1 — HAL Subsystem

Provides a uniform interface over heterogeneous hardware devices.
Drivers register capabilities; the HALRegistry brokers access under
capability tokens enforced by the Constitutional Layer.

All hardware interactions MUST be logged to the GAIAN audit trail
per GAIAN_LAWS.md § Hardware Sovereignty.

© 2026 Kyle Alexander Steen (The Alchemist). All rights reserved.
SPDX-License-Identifier: AGPL-3.0-only
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Protocol, runtime_checkable


class DeviceCapability(Enum):
    """Enumeration of hardware capability classes available on a NEXUS node."""

    COMPUTE = auto()       # General-purpose compute (CPU, GPU, TPU)
    MEMORY = auto()        # Volatile and non-volatile storage
    NETWORK = auto()       # Wired, wireless, mesh, interplanetary
    SENSOR = auto()        # Environmental, biometric, spectral sensors
    ACTUATOR = auto()      # Physical output — motors, displays, emitters
    POWER = auto()         # Energy harvesting, storage, wireless power
    CRYPTOGRAPHIC = auto() # Hardware security modules, TPM, secure enclaves
    QUANTUM = auto()       # Quantum processing units, QKD interfaces


@runtime_checkable
class HALDriver(Protocol):
    """
    Protocol that all hardware drivers must satisfy.

    A HALDriver wraps a single physical or virtual device and exposes
    a standardised capability surface.  Drivers are registered with the
    HALRegistry and never accessed directly by higher layers.
    """

    @property
    def device_id(self) -> str:
        """Unique identifier for this device instance."""
        ...

    @property
    def capabilities(self) -> List[DeviceCapability]:
        """Capabilities this driver exposes."""
        ...

    def initialise(self) -> None:
        """
        Perform driver initialisation and self-test.

        Raises:
            RuntimeError: If the device fails self-test.
        """
        ...

    def shutdown(self) -> None:
        """
        Gracefully shut down the device.

        Must release all resources and log shutdown to the GAIAN audit trail.
        """
        ...

    def health_check(self) -> bool:
        """
        Return True if the device is operating within normal parameters.
        """
        ...


@dataclass
class HALRegistry:
    """
    Central registry for all hardware drivers on a NEXUS node.

    Maintains a capability index for fast lookup.  All registration
    and deregistration events are appended to the GAIAN audit trail.

    Reference: NEXUS_UNIVERSAL_OS.md § Domain 1 — HAL Registry
    """

    _drivers: Dict[str, HALDriver] = field(default_factory=dict, init=False, repr=False)
    _capability_index: Dict[DeviceCapability, List[str]] = field(
        default_factory=dict, init=False, repr=False
    )

    def register(self, driver: HALDriver) -> None:
        """
        Register a HALDriver and index its capabilities.

        Args:
            driver: The HALDriver instance to register.

        Raises:
            ValueError: If a driver with the same device_id is already registered.
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError(
            "HALRegistry.register: stub — implementation pending (NEXUS_UNIVERSAL_OS.md § Domain 1)"
        )

    def deregister(self, device_id: str) -> None:
        """
        Deregister a driver and remove it from the capability index.

        Args:
            device_id: The device_id of the driver to remove.

        Raises:
            KeyError: If no driver with device_id is registered.
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError(
            "HALRegistry.deregister: stub — implementation pending (NEXUS_UNIVERSAL_OS.md § Domain 1)"
        )

    def lookup_by_capability(
        self, capability: DeviceCapability
    ) -> List[HALDriver]:
        """
        Return all registered drivers that expose the given capability.

        Args:
            capability: The DeviceCapability to search for.

        Returns:
            List of matching HALDriver instances (may be empty).

        Raises:
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError(
            "HALRegistry.lookup_by_capability: stub — implementation pending"
        )

    def get(self, device_id: str) -> Optional[HALDriver]:
        """
        Return the driver for device_id, or None if not registered.

        Raises:
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError(
            "HALRegistry.get: stub — implementation pending"
        )

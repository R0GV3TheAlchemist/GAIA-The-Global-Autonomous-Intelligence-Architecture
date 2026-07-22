"""nexusos.hal

Hardware Abstraction Layer (HAL) for NEXUS-OS

Defines the HALDriver Protocol and HALRegistry for registering and
dispatching hardware capability drivers. Modelled after the Fuchsia
Zircon driver framework where hardware access flows through a capability
tree rather than direct device access.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 1.2 - HAL Registry
Research reference:
    Fuchsia Zircon component framework - capability routing
    seL4 Manual v15 Ch.2             - capability derivation
"""
from __future__ import annotations

import logging
from enum import Enum, auto
from typing import Protocol, runtime_checkable

logger = logging.getLogger("nexusos.hal")


class DeviceCapability(Enum):
    """Enumeration of hardware capability categories available to NEXUS."""
    SENSOR = auto()
    NETWORK = auto()
    STORAGE = auto()
    COMPUTE_GPU = auto()
    COMPUTE_QPU = auto()
    DISPLAY = auto()
    AUDIO = auto()
    POWER = auto()
    CLOCK = auto()
    ELF_RECEIVER = auto()   # Schumann / ELF monitoring hardware
    CUSTOM = auto()


@runtime_checkable
class HALDriver(Protocol):
    """Structural protocol for all HAL drivers.

    Any class implementing `capability`, `initialize`, and `read` qualifies
    as a HALDriver without explicit subclassing (duck-typed, seL4-inspired).

    Implementation note:
        Use `@dataclass` or plain classes — no inheritance from HALDriver
        required. The Protocol is for type-checking only.
    """

    @property
    def capability(self) -> DeviceCapability:
        """Return the DeviceCapability this driver services."""
        ...

    def initialize(self) -> None:
        """Initialize the hardware device.

        Raises:
            NotImplementedError: Always in Phase A stubs.
        """
        ...

    def read(self) -> dict:
        """Read the current device state.

        Returns:
            A dict with device-specific fields.

        Raises:
            NotImplementedError: Always in Phase A stubs.
        """
        ...


class HALRegistry:
    """Registry mapping DeviceCapability values to registered HALDriver instances.

    The registry enforces a single active driver per capability at any time.
    Registering a new driver for an already-registered capability overwrites
    the previous one and emits a warning.

    Reference:
        Fuchsia Zircon component manifest capability routing.
    """

    def __init__(self) -> None:
        self._drivers: dict[DeviceCapability, HALDriver] = {}
        logger.info("HALRegistry initialised.")

    def register(self, driver: HALDriver) -> None:
        """Register a HALDriver for its declared capability.

        Args:
            driver: An object satisfying the HALDriver Protocol.

        Raises:
            TypeError: If driver does not satisfy HALDriver Protocol.
        """
        if not isinstance(driver, HALDriver):
            raise TypeError(f"Object {driver!r} does not satisfy HALDriver Protocol.")
        cap = driver.capability
        if cap in self._drivers:
            logger.warning(
                "HALRegistry: overwriting existing driver for capability %s.", cap
            )
        self._drivers[cap] = driver
        logger.info("HALRegistry: registered driver for %s.", cap)

    def get(self, capability: DeviceCapability) -> HALDriver:
        """Retrieve the registered driver for a capability.

        Args:
            capability: The DeviceCapability to look up.

        Returns:
            The registered HALDriver.

        Raises:
            KeyError: If no driver is registered for the given capability.
        """
        if capability not in self._drivers:
            raise KeyError(f"No HALDriver registered for capability: {capability}")
        return self._drivers[capability]

    def registered_capabilities(self) -> list[DeviceCapability]:
        """Return a list of all currently registered capability types."""
        return list(self._drivers.keys())

"""
core.connectors.base
====================
Abstract base class that every GAIA connector must subclass.

A connector is the unit of integration between GAIA and an external system.
It declares its manifest at the class level, receives credentials at
instantiation, and exposes a uniform async lifecycle (connect → execute
→ disconnect) plus an optional event-streaming interface.

OS-level connectors (FILESYSTEM, DISPLAY, HARDWARE_DEVICE, etc.) follow
exactly the same contract — they simply implement the abstract methods using
platform-specific drivers.  The core.os_interface layer wraps these
connectors and exposes a higher-level API to the rest of GAIA.
"""

from __future__ import annotations

import abc
import uuid
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

from .model import (
    ConnectorCapability,
    ConnectorCredential,
    ConnectorEvent,
    ConnectorKind,
    ConnectorManifest,
    ConnectorStatus,
)


class BaseConnector(abc.ABC):
    """Abstract base class for all GAIA connectors.

    Subclassing
    -----------
    1. Declare a class-level ``MANIFEST: ConnectorManifest`` that describes
       the connector type.
    2. Implement ``connect()``, ``disconnect()``, and ``execute()``.
    3. Optionally override ``stream()`` to yield real-time events.
    4. Optionally override ``health_check()`` to provide richer diagnostics.

    Instance identity
    -----------------
    Each instantiation receives a unique ``connector_id`` (UUID4) that
    identifies *this instance* within the ConnectorRegistry and the
    ConnectorBus.  Multiple instances of the same connector type (e.g. two
    different Google Calendar accounts) coexist with separate IDs.
    """

    # Subclasses MUST define this at class level.
    MANIFEST: ConnectorManifest

    def __init__(
        self,
        credential: Optional[ConnectorCredential] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._connector_id: str = str(uuid.uuid4())
        self._credential: Optional[ConnectorCredential] = credential
        self._config: Dict[str, Any] = config or {}
        self._status: ConnectorStatus = ConnectorStatus.REGISTERED
        self._created_at: datetime = datetime.utcnow()
        self._last_active_at: Optional[datetime] = None
        self._error_message: Optional[str] = None

    # ------------------------------------------------------------------
    # Identity and introspection
    # ------------------------------------------------------------------

    @property
    def connector_id(self) -> str:
        """Unique instance identifier (UUID4)."""
        return self._connector_id

    @property
    def connector_type(self) -> str:
        """Type slug from the manifest."""
        return self.MANIFEST.connector_type

    @property
    def kind(self) -> ConnectorKind:
        """Integration domain from the manifest."""
        return self.MANIFEST.kind

    @property
    def capabilities(self) -> ConnectorCapability:
        """Capability bitmask from the manifest."""
        return self.MANIFEST.capabilities

    @property
    def status(self) -> ConnectorStatus:
        """Current lifecycle state."""
        return self._status

    @property
    def is_active(self) -> bool:
        """True when the connector is fully operational."""
        return self._status == ConnectorStatus.ACTIVE

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def last_active_at(self) -> Optional[datetime]:
        return self._last_active_at

    @property
    def error_message(self) -> Optional[str]:
        return self._error_message

    def has_capability(self, cap: ConnectorCapability) -> bool:
        """Return True if this connector declares the given capability."""
        return bool(self.capabilities & cap)

    # ------------------------------------------------------------------
    # Credential access helpers
    # ------------------------------------------------------------------

    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a credential secret by key."""
        if self._credential is None:
            return None
        return self._credential.get_secret(key)

    def get_config(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value by key."""
        return self._config.get(key, default)

    # ------------------------------------------------------------------
    # Lifecycle — subclasses must implement connect / disconnect / execute
    # ------------------------------------------------------------------

    @abc.abstractmethod
    async def connect(self) -> None:
        """Establish the connection to the external system.

        Implementations should:
        * Authenticate using ``self._credential``.
        * Set ``self._status = ConnectorStatus.ACTIVE`` on success.
        * Set ``self._status = ConnectorStatus.ERROR`` and populate
          ``self._error_message`` on failure, then raise.
        """

    @abc.abstractmethod
    async def disconnect(self) -> None:
        """Gracefully close the connection.

        Implementations should:
        * Drain in-flight work.
        * Set ``self._status = ConnectorStatus.STOPPED``.
        """

    @abc.abstractmethod
    async def execute(
        self,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Execute a named operation against the external system.

        Parameters
        ----------
        operation : str
            Operation name, e.g. ``"list_events"``, ``"send_message"``.
        params : dict, optional
            Operation-specific parameters.

        Returns
        -------
        Any
            Operation result.  Structure is operation-specific.

        Raises
        ------
        ConnectorError
            On any failure communicating with the external system.
        """

    # ------------------------------------------------------------------
    # Optional streaming interface
    # ------------------------------------------------------------------

    async def stream(self) -> AsyncIterator[ConnectorEvent]:
        """Yield real-time events from the external system.

        Override in connectors that support STREAM capability.  The default
        implementation raises NotImplementedError.
        """
        raise NotImplementedError(
            f"{self.connector_type} does not implement stream()"
        )
        # Required to satisfy the async generator protocol:
        if False:  # pragma: no cover
            yield  # type: ignore[misc]

    # ------------------------------------------------------------------
    # Health and diagnostics
    # ------------------------------------------------------------------

    async def health_check(self) -> Dict[str, Any]:
        """Return a diagnostic snapshot of this connector instance.

        Default implementation returns basic status info.  Override for
        richer checks (e.g. latency probes, quota queries).
        """
        return {
            "connector_id": self._connector_id,
            "connector_type": self.connector_type,
            "kind": self.kind.value,
            "status": self._status.value,
            "is_active": self.is_active,
            "last_active_at": (
                self._last_active_at.isoformat()
                if self._last_active_at
                else None
            ),
            "error_message": self._error_message,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _mark_active(self) -> None:
        self._status = ConnectorStatus.ACTIVE
        self._last_active_at = datetime.utcnow()
        self._error_message = None

    def _mark_error(self, message: str) -> None:
        self._status = ConnectorStatus.ERROR
        self._error_message = message

    def _mark_stopped(self) -> None:
        self._status = ConnectorStatus.STOPPED

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"id={self._connector_id[:8]} "
            f"type={self.connector_type} "
            f"status={self._status.value}>"
        )

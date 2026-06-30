"""
core.connectors.manager
=======================
ConnectorManager — high-level orchestration for the entire connector layer.

Responsibilities
----------------
* Instantiate connectors from registered types.
* Inject credentials and configuration.
* Manage async lifecycle (connect, pause, resume, disconnect).
* Wire instances to the ConnectorBus.
* Provide named shortcuts for common operations.
* Enforce ownership (principal isolation).

Error hierarchy
---------------
    ConnectorError               base exception for this module
    ├── ConnectorNotFoundError   unknown connector_id or type
    ├── ConnectorAuthError       credential / permission failure
    └── ConnectorTimeoutError    remote call exceeded deadline
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from .base import BaseConnector
from .bus import ConnectorBus
from .model import (
    ConnectorCredential,
    ConnectorEvent,
    ConnectorKind,
    ConnectorStatus,
)
from .registry import ConnectorRegistry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ConnectorError(Exception):
    """Base exception for all connector failures."""


class ConnectorNotFoundError(ConnectorError):
    """Raised when a requested connector ID or type does not exist."""


class ConnectorAuthError(ConnectorError):
    """Raised when a connector fails to authenticate or lacks permission."""


class ConnectorTimeoutError(ConnectorError):
    """Raised when a connector operation exceeds its deadline."""


# ---------------------------------------------------------------------------
# ConnectorManager
# ---------------------------------------------------------------------------

class ConnectorManager:
    """Orchestrates the full lifecycle of all connector instances.

    Parameters
    ----------
    registry : ConnectorRegistry
        The type/instance registry to use.
    bus : ConnectorBus
        The event bus that connector events flow through.
    default_timeout : float
        Default deadline in seconds for connect/disconnect operations.
    """

    def __init__(
        self,
        registry: Optional[ConnectorRegistry] = None,
        bus: Optional[ConnectorBus] = None,
        default_timeout: float = 30.0,
    ) -> None:
        self._registry = registry or ConnectorRegistry()
        self._bus = bus or ConnectorBus()
        self._default_timeout = default_timeout
        # principal_id → set of connector_ids owned by that principal
        self._ownership: Dict[str, set] = {}

    # ------------------------------------------------------------------
    # Property accessors
    # ------------------------------------------------------------------

    @property
    def registry(self) -> ConnectorRegistry:
        return self._registry

    @property
    def bus(self) -> ConnectorBus:
        return self._bus

    # ------------------------------------------------------------------
    # Connector instantiation and connection
    # ------------------------------------------------------------------

    async def create_and_connect(
        self,
        connector_type: str,
        principal_id: str,
        credential: Optional[ConnectorCredential] = None,
        config: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> BaseConnector:
        """Instantiate a connector, register it, and call connect().

        Parameters
        ----------
        connector_type : str
            Registered type slug.
        principal_id : str
            The GAIA principal requesting this connection.
        credential : ConnectorCredential, optional
            Credentials to inject into the connector.
        config : dict, optional
            Additional configuration.
        timeout : float, optional
            Override the default connect timeout.

        Returns
        -------
        BaseConnector
            The connected, active connector instance.

        Raises
        ------
        ConnectorNotFoundError
            If the type slug is not registered.
        ConnectorAuthError
            If connect() raises a permission-related error.
        ConnectorTimeoutError
            If connect() does not complete within the deadline.
        """
        cls = self._registry.get_class(connector_type)
        if cls is None:
            raise ConnectorNotFoundError(
                f"Connector type '{connector_type}' is not registered."
            )

        connector = cls(credential=credential, config=config)
        self._registry.add_instance(connector)
        self._track_ownership(principal_id, connector.connector_id)

        deadline = timeout or self._default_timeout
        try:
            await asyncio.wait_for(connector.connect(), timeout=deadline)
        except asyncio.TimeoutError:
            connector._mark_error("connect() timed out")
            raise ConnectorTimeoutError(
                f"Connector '{connector_type}' connect() exceeded {deadline}s."
            )
        except PermissionError as exc:
            connector._mark_error(str(exc))
            raise ConnectorAuthError(str(exc)) from exc
        except Exception as exc:
            connector._mark_error(str(exc))
            raise ConnectorError(
                f"Connector '{connector_type}' failed to connect: {exc}"
            ) from exc

        logger.info(
            "Connector connected: type=%s id=%s principal=%s",
            connector_type,
            connector.connector_id,
            principal_id,
        )
        return connector

    # ------------------------------------------------------------------
    # Lifecycle operations on existing instances
    # ------------------------------------------------------------------

    async def disconnect(
        self,
        connector_id: str,
        principal_id: str,
        timeout: Optional[float] = None,
    ) -> None:
        """Gracefully disconnect and deregister a connector instance.

        Raises
        ------
        ConnectorNotFoundError
            If the connector_id is unknown.
        ConnectorAuthError
            If the caller does not own the connector.
        """
        connector = self._get_owned(connector_id, principal_id)
        deadline = timeout or self._default_timeout
        try:
            await asyncio.wait_for(connector.disconnect(), timeout=deadline)
        except asyncio.TimeoutError:
            connector._mark_error("disconnect() timed out")
            raise ConnectorTimeoutError(
                f"Connector '{connector_id}' disconnect() exceeded {deadline}s."
            )
        finally:
            self._registry.remove_instance(connector_id)
            self._untrack_ownership(principal_id, connector_id)

        logger.info("Connector disconnected: id=%s", connector_id)

    async def execute(
        self,
        connector_id: str,
        principal_id: str,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Execute an operation on a connector instance.

        Raises
        ------
        ConnectorNotFoundError, ConnectorAuthError, ConnectorTimeoutError
        """
        connector = self._get_owned(connector_id, principal_id)
        deadline = timeout or self._default_timeout
        try:
            result = await asyncio.wait_for(
                connector.execute(operation, params),
                timeout=deadline,
            )
        except asyncio.TimeoutError:
            raise ConnectorTimeoutError(
                f"Operation '{operation}' on '{connector_id}' exceeded {deadline}s."
            )
        connector._last_active_at = datetime.utcnow()
        return result

    async def health_check_all(
        self,
        principal_id: str,
    ) -> List[Dict[str, Any]]:
        """Return health diagnostics for all connectors owned by a principal."""
        owned_ids = self._ownership.get(principal_id, set())
        results = []
        for cid in owned_ids:
            connector = self._registry.get_instance(cid)
            if connector:
                results.append(await connector.health_check())
        return results

    # ------------------------------------------------------------------
    # Bus wiring helpers
    # ------------------------------------------------------------------

    async def publish_event(
        self,
        connector_id: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        source_principal_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> int:
        """Emit a ConnectorEvent from a connector instance onto the bus.

        Returns the number of handlers the event was delivered to.
        """
        connector = self._registry.get_instance(connector_id)
        if connector is None:
            raise ConnectorNotFoundError(
                f"Connector '{connector_id}' not found."
            )
        event = ConnectorEvent(
            connector_id=connector_id,
            connector_type=connector.connector_type,
            kind=connector.kind,
            event_type=event_type,
            payload=payload or {},
            source_principal_id=source_principal_id,
            correlation_id=correlation_id,
        )
        return await self._bus.publish(event)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def get_active_connectors(
        self,
        principal_id: str,
        kind: Optional[ConnectorKind] = None,
    ) -> List[BaseConnector]:
        """Return all active connectors owned by a principal."""
        owned_ids = self._ownership.get(principal_id, set())
        connectors = [
            self._registry.get_instance(cid)
            for cid in owned_ids
            if self._registry.get_instance(cid) is not None
        ]
        if kind is not None:
            connectors = [c for c in connectors if c.kind == kind]  # type: ignore[union-attr]
        return [c for c in connectors if c.is_active]  # type: ignore[union-attr]

    def connector_count(self, principal_id: str) -> int:
        """Return the number of connectors owned by a principal."""
        return len(self._ownership.get(principal_id, set()))

    def total_connector_count(self) -> int:
        """Return total live connectors across all principals."""
        return self._registry.instance_count()

    # ------------------------------------------------------------------
    # Ownership helpers
    # ------------------------------------------------------------------

    def _track_ownership(self, principal_id: str, connector_id: str) -> None:
        self._ownership.setdefault(principal_id, set()).add(connector_id)

    def _untrack_ownership(self, principal_id: str, connector_id: str) -> None:
        if principal_id in self._ownership:
            self._ownership[principal_id].discard(connector_id)

    def _get_owned(
        self, connector_id: str, principal_id: str
    ) -> BaseConnector:
        """Return connector if found and owned; raise otherwise."""
        connector = self._registry.get_instance(connector_id)
        if connector is None:
            raise ConnectorNotFoundError(
                f"Connector '{connector_id}' not found."
            )
        owned = self._ownership.get(principal_id, set())
        if connector_id not in owned:
            raise ConnectorAuthError(
                f"Principal '{principal_id}' does not own connector '{connector_id}'."
            )
        return connector

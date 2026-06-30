"""
core.connectors.registry
========================
ConnectorRegistry — discover, register, and look up connector types and
active instances.

The registry holds two separate indices:

* **Type registry** — maps ``connector_type`` slug → ConnectorManifest.
  This is populated once at startup (or dynamically via plugins) and is
  read-only after that.

* **Instance registry** — maps ``connector_id`` → BaseConnector instance.
  Instances are added by ConnectorManager and removed on disconnect.

Thread-safety note: the current implementation is single-threaded.  A future
version will use asyncio locks when running under concurrent access.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Type

from .model import ConnectorKind, ConnectorManifest
from .base import BaseConnector


class ConnectorRegistry:
    """Central registry for connector types and live instances."""

    def __init__(self) -> None:
        # connector_type slug → manifest
        self._manifests: Dict[str, ConnectorManifest] = {}
        # connector_type slug → class
        self._classes: Dict[str, Type[BaseConnector]] = {}
        # connector_id → instance
        self._instances: Dict[str, BaseConnector] = {}

    # ------------------------------------------------------------------
    # Type registration
    # ------------------------------------------------------------------

    def register_type(
        self,
        connector_class: Type[BaseConnector],
    ) -> None:
        """Register a connector class so it can be instantiated by type slug.

        The class must have a ``MANIFEST`` class attribute of type
        ``ConnectorManifest``.

        Raises
        ------
        ValueError
            If the connector type is already registered.
        """
        manifest = connector_class.MANIFEST
        slug = manifest.connector_type
        if slug in self._manifests:
            raise ValueError(
                f"Connector type '{slug}' is already registered."
            )
        self._manifests[slug] = manifest
        self._classes[slug] = connector_class

    def unregister_type(self, connector_type: str) -> None:
        """Remove a connector type from the registry.

        Does not affect existing instances of that type.
        """
        self._manifests.pop(connector_type, None)
        self._classes.pop(connector_type, None)

    def get_manifest(self, connector_type: str) -> Optional[ConnectorManifest]:
        """Return the manifest for a registered type, or None."""
        return self._manifests.get(connector_type)

    def get_class(
        self, connector_type: str
    ) -> Optional[Type[BaseConnector]]:
        """Return the connector class for a registered type, or None."""
        return self._classes.get(connector_type)

    def list_types(
        self,
        kind: Optional[ConnectorKind] = None,
    ) -> List[ConnectorManifest]:
        """List all registered connector manifests, optionally filtered by kind."""
        manifests = list(self._manifests.values())
        if kind is not None:
            manifests = [m for m in manifests if m.kind == kind]
        return manifests

    def type_exists(self, connector_type: str) -> bool:
        """Return True if a type with this slug is registered."""
        return connector_type in self._manifests

    # ------------------------------------------------------------------
    # Instance management
    # ------------------------------------------------------------------

    def add_instance(self, connector: BaseConnector) -> None:
        """Track a live connector instance."""
        self._instances[connector.connector_id] = connector

    def remove_instance(self, connector_id: str) -> None:
        """Stop tracking an instance (typically called after disconnect)."""
        self._instances.pop(connector_id, None)

    def get_instance(
        self, connector_id: str
    ) -> Optional[BaseConnector]:
        """Return a live instance by ID, or None."""
        return self._instances.get(connector_id)

    def list_instances(
        self,
        kind: Optional[ConnectorKind] = None,
        connector_type: Optional[str] = None,
    ) -> List[BaseConnector]:
        """List live instances, optionally filtered by kind and/or type."""
        instances = list(self._instances.values())
        if kind is not None:
            instances = [i for i in instances if i.kind == kind]
        if connector_type is not None:
            instances = [
                i for i in instances if i.connector_type == connector_type
            ]
        return instances

    def instance_count(self) -> int:
        """Return the number of currently tracked live instances."""
        return len(self._instances)

    def type_count(self) -> int:
        """Return the number of registered connector types."""
        return len(self._manifests)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def snapshot(self) -> dict:
        """Return a plain-dict snapshot of the registry for logging/audit."""
        return {
            "registered_types": sorted(self._manifests.keys()),
            "live_instance_count": self.instance_count(),
            "live_instances": [
                {
                    "connector_id": c.connector_id,
                    "connector_type": c.connector_type,
                    "kind": c.kind.value,
                    "status": c.status.value,
                }
                for c in self._instances.values()
            ],
        }

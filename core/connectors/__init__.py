"""
core.connectors
===============
GAIA Connector Layer — the typed abstraction that bridges all external systems
(calendar, communications, IoT, data sources, device interfaces, OS primitives)
into the GAIA runtime.

This package is the direct prerequisite for core.os_interface.  Every OS-level
capability — file-system access, display management, notifications, hardware
devices — is modelled first as a Connector, then elevated into the OS interface
layer above it.

Public surface
--------------
    ConnectorKind          — enumeration of integration domains
    ConnectorCapability    — flag set describing what a connector can do
    ConnectorStatus        — lifecycle state machine
    ConnectorManifest      — declarative metadata record for a connector type
    ConnectorCredential    — secure credential vault entry
    ConnectorEvent         — typed event emitted by a connector
    BaseConnector          — abstract base class all connectors must implement
    ConnectorRegistry      — discover, register, and look up connector types
    ConnectorBus           — event-driven publish/subscribe message bus
    ConnectorManager       — orchestration: instantiate, wire, lifecycle-manage
    ConnectorError         — base exception
    ConnectorNotFoundError — raised when a connector id is unknown
    ConnectorAuthError     — raised on credential or permission failures
    ConnectorTimeoutError  — raised when a remote call exceeds its deadline
"""

from .model import (
    ConnectorKind,
    ConnectorCapability,
    ConnectorStatus,
    ConnectorManifest,
    ConnectorCredential,
    ConnectorEvent,
)
from .base import BaseConnector
from .registry import ConnectorRegistry
from .bus import ConnectorBus
from .manager import (
    ConnectorManager,
    ConnectorError,
    ConnectorNotFoundError,
    ConnectorAuthError,
    ConnectorTimeoutError,
)

__all__ = [
    # model
    "ConnectorKind",
    "ConnectorCapability",
    "ConnectorStatus",
    "ConnectorManifest",
    "ConnectorCredential",
    "ConnectorEvent",
    # base
    "BaseConnector",
    # registry
    "ConnectorRegistry",
    # bus
    "ConnectorBus",
    # manager + exceptions
    "ConnectorManager",
    "ConnectorError",
    "ConnectorNotFoundError",
    "ConnectorAuthError",
    "ConnectorTimeoutError",
]

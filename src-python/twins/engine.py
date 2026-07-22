"""twins.engine — Digital twin and consent gate stubs

Design intent
-------------
Every physical node, agent, or sensor in the NEXUS planetary mesh can
have a corresponding ``DigitalTwin`` — a live, queryable representation
of its state, capabilities, and history.

ConsentGate enforces that no twin's data is shared without an explicit
consent decision, aligning with GAIAN Coexistence Laws and the
Sovereignty doctrine.

Phase C scope
-------------
- ``DigitalTwin`` property read/write and sync are stubbed.
- ``ConsentGate.check()`` always raises ``NotImplementedError``.
- ``TwinRegistry.register()`` / ``lookup()`` are stubbed.

Future integration
------------------
- Eclipse Ditto REST API for twin lifecycle management.
- W3C Thing Description for semantic capability advertisement.
- ``core.obs.audit_store.AuditStore``: every consent decision audited.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Mapping
import uuid


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class ConsentDecision(Enum):
    """Result of a consent gate evaluation."""
    GRANTED = auto()
    DENIED = auto()
    PENDING = auto()


@dataclass
class TwinConfig:
    """Configuration for a DigitalTwin instance.

    Parameters
    ----------
    twin_id:
        Unique identifier for this twin. Auto-generated if omitted.
    entity_type:
        Semantic type of the represented entity
        (e.g. ``"agent"``, ``"sensor"``, ``"node"``, ``"human"``).
    owner:
        Identity of the entity that owns / controls this twin.
    consent_required:
        Whether ConsentGate must be checked before any data read.
    """
    twin_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = "agent"
    owner: str = "unknown"
    consent_required: bool = True


@dataclass
class TwinState:
    """Point-in-time snapshot of a DigitalTwin's properties.

    Parameters
    ----------
    properties:
        Key-value map of twin properties (JSON-serialisable).
    updated_at:
        UTC timestamp of the last state update.
    version:
        Monotonically increasing version counter.
    """
    properties: Mapping[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    version: int = 0


# ---------------------------------------------------------------------------
# DigitalTwin
# ---------------------------------------------------------------------------

class DigitalTwin:
    """Digital twin of a NEXUS entity.

    Maintains a local property map and supports sync with a remote
    twin service (Eclipse Ditto or equivalent).

    Phase C — all sync/remote methods are stubbed.
    """

    def __init__(self, config: TwinConfig | None = None) -> None:
        self._config = config or TwinConfig()
        self._state = TwinState()

    @property
    def twin_id(self) -> str:
        return self._config.twin_id

    def get_property(self, key: str) -> Any:
        """Read a property from the local twin state.

        Args:
            key: Property name.

        Returns:
            Property value, or ``None`` if not set.
        """
        return self._state.properties.get(key)

    def set_property(self, key: str, value: Any) -> None:
        """Write a property to the local twin state.

        Args:
            key:   Property name.
            value: JSON-serialisable value.

        Note:
            Increments ``state.version`` and updates ``state.updated_at``.
        """
        props = dict(self._state.properties)
        props[key] = value
        self._state = TwinState(
            properties=props,
            version=self._state.version + 1,
        )

    def sync(self) -> None:
        """Synchronise local state with the remote twin service.

        Intended implementation
        -----------------------
        - PUT /api/2/things/{twin_id} on Eclipse Ditto REST API.
        - On conflict, apply last-writer-wins or CRDT merge.

        Raises:
            NotImplementedError: Always in Phase C.
        """
        raise NotImplementedError(
            f"DigitalTwin.sync is not yet implemented for twin_id={self.twin_id!r}. "
            "Expected: PUT /api/2/things/{twin_id} on Eclipse Ditto REST API."
        )

    def snapshot(self) -> TwinState:
        """Return a copy of the current local twin state."""
        return TwinState(
            properties=dict(self._state.properties),
            updated_at=self._state.updated_at,
            version=self._state.version,
        )


# ---------------------------------------------------------------------------
# ConsentGate
# ---------------------------------------------------------------------------

class ConsentGate:
    """Enforces consent policies before twin data access.

    Every data read or share from a DigitalTwin with
    ``config.consent_required=True`` must pass through ConsentGate.check()
    before the data is released.

    Phase C — check() is stubbed. Implementation will integrate with
    SovereignMemory's ConsentStore and audit AuditStore.
    """

    def check(
        self,
        twin: DigitalTwin,
        requestor: str,
        operation: str = "read",
    ) -> ConsentDecision:
        """Evaluate a consent request for a twin data operation.

        Intended implementation
        -----------------------
        1. Look up the twin's owner consent policy in SovereignMemory.
        2. Evaluate against the requestor identity and operation type.
        3. Log the decision to ``core.obs.audit_store`` (event type:
           ``"consent.granted"`` or ``"consent.denied"``).
        4. Return ``ConsentDecision.GRANTED`` or ``ConsentDecision.DENIED``.

        Args:
            twin:       The ``DigitalTwin`` being accessed.
            requestor:  Identity of the requesting agent or module.
            operation:  Operation type (``"read"``, ``"write"``,
                        ``"share"``, ``"delete"``).

        Returns:
            ``ConsentDecision`` enum value.

        Raises:
            NotImplementedError: Always in Phase C.
        """
        raise NotImplementedError(
            f"ConsentGate.check is not yet implemented for "
            f"twin={twin.twin_id!r}, requestor={requestor!r}, "
            f"operation={operation!r}. "
            "Expected: evaluate consent policy from SovereignMemory and "
            "audit the decision in AuditStore."
        )


# ---------------------------------------------------------------------------
# TwinRegistry
# ---------------------------------------------------------------------------

class TwinRegistry:
    """Registry of all active DigitalTwin instances.

    Phase C — register() and lookup() are stubbed.
    """

    def __init__(self) -> None:
        self._twins: dict[str, DigitalTwin] = {}

    def register(self, twin: DigitalTwin) -> None:
        """Register a twin in the registry.

        Args:
            twin: ``DigitalTwin`` to register.

        Raises:
            NotImplementedError: Always in Phase C.
        """
        raise NotImplementedError(
            f"TwinRegistry.register is not yet implemented for "
            f"twin_id={twin.twin_id!r}. "
            "Expected: store twin, broadcast registration event on mesh."
        )

    def lookup(self, twin_id: str) -> DigitalTwin | None:
        """Retrieve a twin by ID.

        Args:
            twin_id: Twin identifier.

        Returns:
            ``DigitalTwin`` if found, ``None`` otherwise.
        """
        return self._twins.get(twin_id)

    def all_twins(self) -> list[DigitalTwin]:
        """Return all registered twins."""
        return list(self._twins.values())

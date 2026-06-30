"""
tests.connectors.test_connectors
================================
Test suite for core.connectors — verifies the complete connector layer:
models, base class contract, registry, bus, and manager.
"""

from __future__ import annotations

import asyncio
import pytest
from datetime import datetime, timedelta
from typing import Any, AsyncIterator, Dict, Optional

from core.connectors import (
    BaseConnector,
    ConnectorBus,
    ConnectorCapability,
    ConnectorCredential,
    ConnectorEvent,
    ConnectorKind,
    ConnectorManifest,
    ConnectorManager,
    ConnectorRegistry,
    ConnectorStatus,
    ConnectorError,
    ConnectorNotFoundError,
    ConnectorAuthError,
    ConnectorTimeoutError,
)


# ---------------------------------------------------------------------------
# Fixtures — concrete connector implementations for testing
# ---------------------------------------------------------------------------

class FakeCalendarConnector(BaseConnector):
    """Minimal concrete connector for unit testing."""

    MANIFEST = ConnectorManifest(
        connector_type="fake_calendar",
        display_name="Fake Calendar",
        kind=ConnectorKind.CALENDAR,
        capabilities=ConnectorCapability.READ | ConnectorCapability.WRITE,
        description="A fake calendar connector used in tests.",
        version="1.0.0",
        required_credential_keys=("api_key",),
        platform_targets=("linux", "windows", "macos"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect_called = False
        self.disconnect_called = False
        self.executed_operations = []

    async def connect(self) -> None:
        self.connect_called = True
        self._mark_active()

    async def disconnect(self) -> None:
        self.disconnect_called = True
        self._mark_stopped()

    async def execute(
        self, operation: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        self.executed_operations.append((operation, params))
        return {"operation": operation, "params": params}


class FakeIoTSensorConnector(BaseConnector):
    """Streaming IoT connector for bus and stream tests."""

    MANIFEST = ConnectorManifest(
        connector_type="fake_iot_sensor",
        display_name="Fake IoT Sensor",
        kind=ConnectorKind.IOT_SENSOR,
        capabilities=ConnectorCapability.READ | ConnectorCapability.STREAM,
        description="A fake IoT sensor connector used in tests.",
    )

    async def connect(self) -> None:
        self._mark_active()

    async def disconnect(self) -> None:
        self._mark_stopped()

    async def execute(
        self, operation: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        return {"reading": 42.0}

    async def stream(self) -> AsyncIterator[ConnectorEvent]:
        for i in range(3):
            yield ConnectorEvent(
                connector_id=self.connector_id,
                connector_type=self.connector_type,
                kind=self.kind,
                event_type="iot.sensor.temperature.reading",
                payload={"value": 20.0 + i},
            )


class SlowConnector(BaseConnector):
    """Connector that sleeps on connect to test timeout handling."""

    MANIFEST = ConnectorManifest(
        connector_type="slow_connector",
        display_name="Slow Connector",
        kind=ConnectorKind.CUSTOM,
        capabilities=ConnectorCapability.READ,
        description="Used to test timeout behaviour.",
    )

    async def connect(self) -> None:
        await asyncio.sleep(10)  # deliberately slow
        self._mark_active()

    async def disconnect(self) -> None:
        self._mark_stopped()

    async def execute(self, operation: str, params=None) -> Any:
        return None


# ---------------------------------------------------------------------------
# ConnectorCredential tests
# ---------------------------------------------------------------------------

class TestConnectorCredential:

    def test_creation(self):
        cred = ConnectorCredential(
            connector_type="fake_calendar",
            principal_id="user_001",
            secrets={"api_key": "secret123"},
        )
        assert cred.connector_type == "fake_calendar"
        assert cred.principal_id == "user_001"
        assert cred.get_secret("api_key") == "secret123"
        assert cred.get_secret("missing") is None
        assert not cred.is_expired()

    def test_expiry(self):
        past = datetime.utcnow() - timedelta(hours=1)
        cred = ConnectorCredential(
            connector_type="test",
            principal_id="p1",
            expires_at=past,
        )
        assert cred.is_expired()

    def test_not_expired_with_future_expiry(self):
        future = datetime.utcnow() + timedelta(hours=1)
        cred = ConnectorCredential(
            connector_type="test",
            principal_id="p1",
            expires_at=future,
        )
        assert not cred.is_expired()


# ---------------------------------------------------------------------------
# ConnectorManifest tests
# ---------------------------------------------------------------------------

class TestConnectorManifest:

    def test_manifest_immutability(self):
        manifest = FakeCalendarConnector.MANIFEST
        with pytest.raises((AttributeError, TypeError)):
            manifest.connector_type = "changed"  # type: ignore[misc]

    def test_manifest_fields(self):
        m = FakeCalendarConnector.MANIFEST
        assert m.kind == ConnectorKind.CALENDAR
        assert ConnectorCapability.READ in m.capabilities
        assert ConnectorCapability.WRITE in m.capabilities
        assert "linux" in m.platform_targets


# ---------------------------------------------------------------------------
# BaseConnector tests
# ---------------------------------------------------------------------------

class TestBaseConnector:

    def test_initial_state(self):
        c = FakeCalendarConnector()
        assert c.status == ConnectorStatus.REGISTERED
        assert not c.is_active
        assert c.kind == ConnectorKind.CALENDAR
        assert c.connector_type == "fake_calendar"

    def test_capability_check(self):
        c = FakeCalendarConnector()
        assert c.has_capability(ConnectorCapability.READ)
        assert c.has_capability(ConnectorCapability.WRITE)
        assert not c.has_capability(ConnectorCapability.STREAM)

    @pytest.mark.asyncio
    async def test_connect_marks_active(self):
        c = FakeCalendarConnector()
        await c.connect()
        assert c.is_active
        assert c.connect_called

    @pytest.mark.asyncio
    async def test_disconnect_marks_stopped(self):
        c = FakeCalendarConnector()
        await c.connect()
        await c.disconnect()
        assert c.status == ConnectorStatus.STOPPED
        assert c.disconnect_called

    @pytest.mark.asyncio
    async def test_execute_records_operations(self):
        c = FakeCalendarConnector()
        await c.connect()
        result = await c.execute("list_events", {"calendar_id": "primary"})
        assert result["operation"] == "list_events"
        assert len(c.executed_operations) == 1

    def test_get_secret_with_credential(self):
        cred = ConnectorCredential(
            connector_type="fake_calendar",
            principal_id="p1",
            secrets={"api_key": "abc"},
        )
        c = FakeCalendarConnector(credential=cred)
        assert c.get_secret("api_key") == "abc"

    def test_get_secret_without_credential(self):
        c = FakeCalendarConnector()
        assert c.get_secret("api_key") is None

    @pytest.mark.asyncio
    async def test_health_check(self):
        c = FakeCalendarConnector()
        await c.connect()
        health = await c.health_check()
        assert health["is_active"] is True
        assert health["connector_type"] == "fake_calendar"

    @pytest.mark.asyncio
    async def test_stream(self):
        sensor = FakeIoTSensorConnector()
        await sensor.connect()
        events = []
        async for event in sensor.stream():
            events.append(event)
        assert len(events) == 3
        assert all(e.event_type == "iot.sensor.temperature.reading" for e in events)

    @pytest.mark.asyncio
    async def test_stream_not_implemented_for_non_streaming(self):
        c = FakeCalendarConnector()
        with pytest.raises(NotImplementedError):
            async for _ in c.stream():
                pass


# ---------------------------------------------------------------------------
# ConnectorRegistry tests
# ---------------------------------------------------------------------------

class TestConnectorRegistry:

    def test_register_and_lookup(self):
        reg = ConnectorRegistry()
        reg.register_type(FakeCalendarConnector)
        assert reg.type_exists("fake_calendar")
        manifest = reg.get_manifest("fake_calendar")
        assert manifest is not None
        assert manifest.display_name == "Fake Calendar"

    def test_duplicate_registration_raises(self):
        reg = ConnectorRegistry()
        reg.register_type(FakeCalendarConnector)
        with pytest.raises(ValueError):
            reg.register_type(FakeCalendarConnector)

    def test_unregister(self):
        reg = ConnectorRegistry()
        reg.register_type(FakeCalendarConnector)
        reg.unregister_type("fake_calendar")
        assert not reg.type_exists("fake_calendar")

    def test_list_types_by_kind(self):
        reg = ConnectorRegistry()
        reg.register_type(FakeCalendarConnector)
        reg.register_type(FakeIoTSensorConnector)
        cal_types = reg.list_types(kind=ConnectorKind.CALENDAR)
        assert len(cal_types) == 1
        assert cal_types[0].connector_type == "fake_calendar"

    def test_instance_tracking(self):
        reg = ConnectorRegistry()
        c = FakeCalendarConnector()
        reg.add_instance(c)
        assert reg.get_instance(c.connector_id) is c
        assert reg.instance_count() == 1
        reg.remove_instance(c.connector_id)
        assert reg.instance_count() == 0

    def test_list_instances_by_kind(self):
        reg = ConnectorRegistry()
        cal = FakeCalendarConnector()
        sensor = FakeIoTSensorConnector()
        reg.add_instance(cal)
        reg.add_instance(sensor)
        cals = reg.list_instances(kind=ConnectorKind.CALENDAR)
        assert len(cals) == 1
        assert cals[0].connector_type == "fake_calendar"


# ---------------------------------------------------------------------------
# ConnectorBus tests
# ---------------------------------------------------------------------------

class TestConnectorBus:

    @pytest.mark.asyncio
    async def test_subscribe_and_publish_exact_match(self):
        bus = ConnectorBus()
        received = []

        async def handler(event: ConnectorEvent) -> None:
            received.append(event)

        bus.subscribe("calendar.event.created", handler)

        event = ConnectorEvent(
            connector_id="c1",
            connector_type="fake_calendar",
            kind=ConnectorKind.CALENDAR,
            event_type="calendar.event.created",
            payload={"title": "Meeting"},
        )
        delivered = await bus.publish(event)
        assert delivered == 1
        assert len(received) == 1
        assert received[0].payload["title"] == "Meeting"

    @pytest.mark.asyncio
    async def test_wildcard_subscription(self):
        bus = ConnectorBus()
        received = []

        async def handler(event: ConnectorEvent) -> None:
            received.append(event)

        bus.subscribe("iot.*", handler)

        for et in ["iot.sensor.reading", "iot.actuator.toggle"]:
            event = ConnectorEvent(
                connector_id="s1",
                connector_type="fake_iot_sensor",
                kind=ConnectorKind.IOT_SENSOR,
                event_type=et,
            )
            await bus.publish(event)

        assert len(received) == 2

    @pytest.mark.asyncio
    async def test_no_matching_subscribers(self):
        bus = ConnectorBus()
        event = ConnectorEvent(
            connector_id="c1",
            connector_type="fake_calendar",
            kind=ConnectorKind.CALENDAR,
            event_type="calendar.event.created",
        )
        delivered = await bus.publish(event)
        assert delivered == 0

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        bus = ConnectorBus()
        received = []

        async def handler(event: ConnectorEvent) -> None:
            received.append(event)

        bus.subscribe("calendar.*", handler)
        bus.unsubscribe("calendar.*", handler)

        event = ConnectorEvent(
            connector_id="c1",
            connector_type="fake_calendar",
            kind=ConnectorKind.CALENDAR,
            event_type="calendar.event.created",
        )
        await bus.publish(event)
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_bus_stats(self):
        bus = ConnectorBus()
        async def h(e): pass
        bus.subscribe("test.*", h)
        stats = bus.stats()
        assert stats["total_handlers"] == 1


# ---------------------------------------------------------------------------
# ConnectorManager tests
# ---------------------------------------------------------------------------

class TestConnectorManager:

    def _make_manager(self) -> ConnectorManager:
        registry = ConnectorRegistry()
        registry.register_type(FakeCalendarConnector)
        registry.register_type(FakeIoTSensorConnector)
        registry.register_type(SlowConnector)
        bus = ConnectorBus()
        return ConnectorManager(registry=registry, bus=bus, default_timeout=5.0)

    @pytest.mark.asyncio
    async def test_create_and_connect(self):
        manager = self._make_manager()
        connector = await manager.create_and_connect(
            "fake_calendar",
            principal_id="user_1",
        )
        assert connector.is_active
        assert manager.connector_count("user_1") == 1

    @pytest.mark.asyncio
    async def test_unknown_type_raises(self):
        manager = self._make_manager()
        with pytest.raises(ConnectorNotFoundError):
            await manager.create_and_connect(
                "nonexistent_type",
                principal_id="user_1",
            )

    @pytest.mark.asyncio
    async def test_disconnect(self):
        manager = self._make_manager()
        connector = await manager.create_and_connect(
            "fake_calendar",
            principal_id="user_1",
        )
        cid = connector.connector_id
        await manager.disconnect(cid, principal_id="user_1")
        assert connector.status == ConnectorStatus.STOPPED
        assert manager.connector_count("user_1") == 0

    @pytest.mark.asyncio
    async def test_disconnect_wrong_owner_raises(self):
        manager = self._make_manager()
        connector = await manager.create_and_connect(
            "fake_calendar",
            principal_id="user_1",
        )
        with pytest.raises(ConnectorAuthError):
            await manager.disconnect(connector.connector_id, principal_id="user_2")

    @pytest.mark.asyncio
    async def test_execute_operation(self):
        manager = self._make_manager()
        connector = await manager.create_and_connect(
            "fake_calendar",
            principal_id="user_1",
        )
        result = await manager.execute(
            connector.connector_id,
            principal_id="user_1",
            operation="list_events",
            params={"limit": 10},
        )
        assert result["operation"] == "list_events"

    @pytest.mark.asyncio
    async def test_connect_timeout(self):
        manager = ConnectorManager(
            registry=ConnectorRegistry(),
            bus=ConnectorBus(),
            default_timeout=0.05,
        )
        manager.registry.register_type(SlowConnector)
        with pytest.raises(ConnectorTimeoutError):
            await manager.create_and_connect(
                "slow_connector",
                principal_id="user_1",
            )

    @pytest.mark.asyncio
    async def test_publish_event(self):
        manager = self._make_manager()
        connector = await manager.create_and_connect(
            "fake_calendar",
            principal_id="user_1",
        )
        received = []
        async def handler(e): received.append(e)
        manager.bus.subscribe("calendar.*", handler)

        delivered = await manager.publish_event(
            connector.connector_id,
            event_type="calendar.event.created",
            payload={"title": "Sprint Review"},
            source_principal_id="user_1",
        )
        assert delivered == 1
        assert received[0].payload["title"] == "Sprint Review"

    @pytest.mark.asyncio
    async def test_get_active_connectors(self):
        manager = self._make_manager()
        await manager.create_and_connect("fake_calendar", principal_id="user_1")
        await manager.create_and_connect("fake_iot_sensor", principal_id="user_1")
        active = manager.get_active_connectors("user_1")
        assert len(active) == 2
        cal_only = manager.get_active_connectors("user_1", kind=ConnectorKind.CALENDAR)
        assert len(cal_only) == 1

    @pytest.mark.asyncio
    async def test_health_check_all(self):
        manager = self._make_manager()
        await manager.create_and_connect("fake_calendar", principal_id="user_1")
        reports = await manager.health_check_all("user_1")
        assert len(reports) == 1
        assert reports[0]["is_active"] is True

    @pytest.mark.asyncio
    async def test_total_connector_count(self):
        manager = self._make_manager()
        await manager.create_and_connect("fake_calendar", principal_id="user_1")
        await manager.create_and_connect("fake_iot_sensor", principal_id="user_2")
        assert manager.total_connector_count() == 2

    @pytest.mark.asyncio
    async def test_os_kind_connectors_registered(self):
        """Verify OS-primitive connector kinds are in ConnectorKind enum."""
        os_kinds = [
            ConnectorKind.FILESYSTEM,
            ConnectorKind.DISPLAY,
            ConnectorKind.NOTIFICATIONS,
            ConnectorKind.HARDWARE_DEVICE,
            ConnectorKind.AUDIO,
            ConnectorKind.CAMERA,
            ConnectorKind.INPUT_DEVICE,
            ConnectorKind.NETWORK,
            ConnectorKind.POWER,
            ConnectorKind.PROCESS,
        ]
        for k in os_kinds:
            assert isinstance(k, ConnectorKind)

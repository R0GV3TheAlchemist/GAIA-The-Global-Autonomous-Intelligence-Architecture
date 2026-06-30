from __future__ import annotations

import pytest

from core.os_interface.process_manager.ipc import IPCRouter, PortRight
from core.os_interface.process_manager.manager import ProcessManager, ProcessPermissionError
from core.os_interface.process_manager.model import (
    ProcessIsolationLevel,
    ProcessKind,
    ResourceKind,
)


class TestProcessSpawnAndTerminate:
    def test_spawn_creates_process(self):
        mgr = ProcessManager()
        p = mgr.spawn("test-app", owner_id="gaia")
        assert p.is_alive()
        assert p.name == "test-app"

    def test_spawn_creates_ipc_port(self):
        mgr = ProcessManager()
        p = mgr.spawn("test-app")
        assert len(p.ipc_ports) == 1

    def test_terminate_sets_exit_code(self):
        mgr = ProcessManager()
        p = mgr.spawn("test-app")
        mgr.terminate(p.pid, exit_code=0)
        assert not p.is_alive()
        assert p.exit_code == 0

    def test_terminate_removes_child_from_parent(self):
        mgr = ProcessManager()
        parent = mgr.spawn("parent")
        child = mgr.spawn("child", parent_pid=parent.pid)
        assert child.pid in parent.children
        mgr.terminate(child.pid)
        assert child.pid not in parent.children

    def test_intelligence_process_kind(self):
        mgr = ProcessManager()
        p = mgr.spawn("gaia-intelligence", kind=ProcessKind.INTELLIGENCE)
        assert p.is_intelligence()


class TestCapabilities:
    def test_trusted_process_can_grant(self):
        mgr = ProcessManager()
        kernel = mgr.spawn("kernel", kind=ProcessKind.KERNEL, isolation=ProcessIsolationLevel.KERNEL)
        app = mgr.spawn("app")
        grant = mgr.grant_capability(app.pid, kernel.pid, ResourceKind.FILE, resource_id="/data")
        assert app.capabilities.has(ResourceKind.FILE, "/data")

    def test_untrusted_process_cannot_grant_without_delegate(self):
        mgr = ProcessManager()
        a = mgr.spawn("a")
        b = mgr.spawn("b")
        with pytest.raises(ProcessPermissionError):
            mgr.grant_capability(b.pid, a.pid, ResourceKind.NETWORK)

    def test_revoke_capability(self):
        mgr = ProcessManager()
        kernel = mgr.spawn("kernel", isolation=ProcessIsolationLevel.KERNEL)
        app = mgr.spawn("app")
        grant = mgr.grant_capability(app.pid, kernel.pid, ResourceKind.FILE)
        assert app.capabilities.has(ResourceKind.FILE)
        mgr.revoke_capability(app.pid, grant.capability_id)
        assert not app.capabilities.has(ResourceKind.FILE)

    def test_capability_set_active_filters_revoked(self):
        mgr = ProcessManager()
        kernel = mgr.spawn("kernel", isolation=ProcessIsolationLevel.KERNEL)
        app = mgr.spawn("app")
        g1 = mgr.grant_capability(app.pid, kernel.pid, ResourceKind.FILE, resource_id="/a")
        g2 = mgr.grant_capability(app.pid, kernel.pid, ResourceKind.FILE, resource_id="/b")
        mgr.revoke_capability(app.pid, g1.capability_id)
        active = app.capabilities.active()
        ids = [g.capability_id for g in active]
        assert g1.capability_id not in ids
        assert g2.capability_id in ids


class TestIPC:
    def test_create_port_and_send_receive(self):
        router = IPCRouter()
        port = router.create_port("pid-a", name="test-port")
        msg = router.send(port.port_id, "pid-a", "ping", {"seq": 1})
        received = router.receive(port.port_id, "pid-a")
        assert received is not None
        assert received.msg_type == "ping"
        assert received.payload["seq"] == 1

    def test_send_without_right_raises(self):
        router = IPCRouter()
        port = router.create_port("pid-a")
        from core.os_interface.process_manager.ipc import IPCMessage
        msg = IPCMessage(sender_pid="pid-b", msg_type="x", payload={})
        with pytest.raises(PermissionError):
            port.send(msg)

    def test_transfer_send_right(self):
        router = IPCRouter()
        port = router.create_port("pid-a")
        router.transfer_send_right(port.port_id, "pid-b")
        assert port.has_right("pid-b", PortRight.SEND)

    def test_port_queue_depth(self):
        router = IPCRouter()
        port = router.create_port("pid-a", max_depth=2)
        router.send(port.port_id, "pid-a", "a", {})
        router.send(port.port_id, "pid-a", "b", {})
        assert port.depth() == 2
        result = router.send.__func__ if hasattr(router.send, '__func__') else None
        full = not port.send(
            __import__('core.os_interface.process_manager.ipc', fromlist=['IPCMessage']).IPCMessage(
                sender_pid="pid-a", msg_type="c", payload={}
            )
        )
        assert full

    def test_receive_empty_returns_none(self):
        router = IPCRouter()
        port = router.create_port("pid-a")
        assert router.receive(port.port_id, "pid-a") is None

    def test_destroy_port(self):
        router = IPCRouter()
        port = router.create_port("pid-a")
        router.destroy_port(port.port_id)
        assert router.get_port(port.port_id) is None

    def test_list_by_kind(self):
        mgr = ProcessManager()
        mgr.spawn("a", kind=ProcessKind.SYSTEM)
        mgr.spawn("b", kind=ProcessKind.SYSTEM)
        mgr.spawn("c", kind=ProcessKind.APPLICATION)
        assert len(mgr.list_by_kind(ProcessKind.SYSTEM)) == 2

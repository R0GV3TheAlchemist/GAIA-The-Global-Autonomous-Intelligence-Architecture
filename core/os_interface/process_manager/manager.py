"""
GAIA Process Manager — spawn, isolate, monitor, and terminate processes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.os_interface.process_manager.ipc import IPCRouter
from core.os_interface.process_manager.model import (
    CapabilityGrant,
    GAIAProcess,
    ProcessIdentity,
    ProcessIsolationLevel,
    ProcessKind,
    ResourceKind,
)


class ProcessPermissionError(Exception):
    pass


class ProcessManager:
    def __init__(self) -> None:
        self._processes: Dict[str, GAIAProcess] = {}
        self.ipc = IPCRouter()

    def spawn(
        self,
        name: str,
        kind: ProcessKind = ProcessKind.APPLICATION,
        isolation: ProcessIsolationLevel = ProcessIsolationLevel.USER,
        owner_id: str = "",
        session_id: str = "",
        space_id: str = "",
        parent_pid: Optional[str] = None,
        initial_capabilities: Optional[List[CapabilityGrant]] = None,
    ) -> GAIAProcess:
        identity = ProcessIdentity(
            owner_id=owner_id,
            session_id=session_id,
            space_id=space_id,
            trusted=(isolation in (ProcessIsolationLevel.KERNEL, ProcessIsolationLevel.TRUSTED)),
        )
        process = GAIAProcess(
            name=name,
            kind=kind,
            isolation=isolation,
            identity=identity,
            parent_pid=parent_pid,
        )
        process.started_at = datetime.now(timezone.utc).isoformat()
        for cap in (initial_capabilities or []):
            process.grant(cap)
        if parent_pid and parent_pid in self._processes:
            self._processes[parent_pid].children.append(process.pid)
        port = self.ipc.create_port(process.pid, name=f"{name}.main")
        process.ipc_ports.append(port.port_id)
        self._processes[process.pid] = process
        return process

    def terminate(self, pid: str, exit_code: int = 0) -> None:
        process = self._require(pid)
        process.exit_code = exit_code
        process.exited_at = datetime.now(timezone.utc).isoformat()
        for port_id in process.ipc_ports:
            self.ipc.destroy_port(port_id)
        if process.parent_pid and process.parent_pid in self._processes:
            parent = self._processes[process.parent_pid]
            parent.children = [c for c in parent.children if c != pid]

    def grant_capability(
        self,
        target_pid: str,
        grantor_pid: str,
        resource_kind: ResourceKind,
        resource_id: str = "",
        read: bool = True,
        write: bool = False,
        execute: bool = False,
        delegate: bool = False,
    ) -> CapabilityGrant:
        grantor = self._require(grantor_pid)
        target = self._require(target_pid)
        # Grantor must either be trusted or already hold the capability with delegate=True
        if not grantor.identity.trusted:
            existing = grantor.capabilities.for_resource(resource_id)
            can_delegate = any(g.delegate for g in existing)
            if not can_delegate:
                raise ProcessPermissionError(
                    f"PID '{grantor_pid}' cannot delegate capability it does not hold."
                )
        grant = CapabilityGrant(
            resource_kind=resource_kind,
            resource_id=resource_id,
            read=read,
            write=write,
            execute=execute,
            delegate=delegate,
            granted_by=grantor_pid,
        )
        target.grant(grant)
        return grant

    def revoke_capability(self, pid: str, capability_id: str) -> bool:
        return self._require(pid).capabilities.revoke(capability_id)

    def get(self, pid: str) -> Optional[GAIAProcess]:
        return self._processes.get(pid)

    def list_alive(self) -> List[GAIAProcess]:
        return [p for p in self._processes.values() if p.is_alive()]

    def list_by_kind(self, kind: ProcessKind) -> List[GAIAProcess]:
        return [p for p in self._processes.values() if p.kind == kind]

    def process_table(self) -> List[Dict[str, Any]]:
        return [p.summary() for p in self._processes.values()]

    def _require(self, pid: str) -> GAIAProcess:
        p = self._processes.get(pid)
        if p is None:
            raise KeyError(f"Process '{pid}' not found.")
        return p

"""
GAIA IPC — typed, capability-gated inter-process communication.

Modelled after Mach ports (XNU) and seL4 endpoints:
  - An IPCPort is a named, bounded message queue.
  - Processes hold PortRights (SEND, RECEIVE, SEND_ONCE) as capabilities.
  - Messages carry typed payloads and optional out-of-line memory descriptors.
  - No shared mutable state: all communication is by message copy.

The IPCRouter is the kernel-side registry that creates ports, transfers
rights, and routes messages between processes.
"""
from __future__ import annotations

import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Deque, Dict, List, Optional


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class PortRight(str, Enum):
    SEND = "send"              # can send messages to this port
    RECEIVE = "receive"        # can receive messages from this port
    SEND_ONCE = "send_once"    # can send exactly one message, right destroyed after


@dataclass
class IPCMessage:
    """A typed, immutable message sent through an IPC port."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_pid: str = ""
    msg_type: str = ""              # typed message discriminator
    payload: Dict[str, Any] = field(default_factory=dict)
    reply_port_id: Optional[str] = None   # port to send reply to (Mach-style)
    sent_at: str = field(default_factory=_utcnow)
    ool_descriptors: List[Dict[str, Any]] = field(default_factory=list)  # out-of-line memory


@dataclass
class IPCPort:
    """A bounded, capability-gated message queue."""
    port_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    owner_pid: str = ""             # process holding RECEIVE right
    max_queue_depth: int = 256
    _queue: Deque[IPCMessage] = field(default_factory=deque, repr=False)
    _rights: Dict[str, List[PortRight]] = field(default_factory=dict, repr=False)
    created_at: str = field(default_factory=_utcnow)

    def grant_right(self, pid: str, right: PortRight) -> None:
        self._rights.setdefault(pid, []).append(right)

    def revoke_right(self, pid: str, right: PortRight) -> None:
        if pid in self._rights:
            self._rights[pid] = [r for r in self._rights[pid] if r != right]

    def has_right(self, pid: str, right: PortRight) -> bool:
        return right in self._rights.get(pid, [])

    def send(self, message: IPCMessage) -> bool:
        """Enqueue a message. Returns False if queue is full."""
        if not self.has_right(message.sender_pid, PortRight.SEND):
            raise PermissionError(
                f"PID '{message.sender_pid}' lacks SEND right on port '{self.port_id}'."
            )
        if len(self._queue) >= self.max_queue_depth:
            return False  # port full
        self._queue.append(message)
        return True

    def receive(self, pid: str) -> Optional[IPCMessage]:
        """Dequeue the oldest message. Returns None if queue is empty."""
        if not self.has_right(pid, PortRight.RECEIVE):
            raise PermissionError(
                f"PID '{pid}' lacks RECEIVE right on port '{self.port_id}'."
            )
        return self._queue.popleft() if self._queue else None

    def depth(self) -> int:
        return len(self._queue)


class IPCRouter:
    """Kernel-side port registry: creates, transfers, and destroys ports."""

    def __init__(self) -> None:
        self._ports: Dict[str, IPCPort] = {}

    def create_port(self, owner_pid: str, name: str = "", max_depth: int = 256) -> IPCPort:
        port = IPCPort(name=name, owner_pid=owner_pid, max_queue_depth=max_depth)
        port.grant_right(owner_pid, PortRight.RECEIVE)
        port.grant_right(owner_pid, PortRight.SEND)
        self._ports[port.port_id] = port
        return port

    def get_port(self, port_id: str) -> Optional[IPCPort]:
        return self._ports.get(port_id)

    def require_port(self, port_id: str) -> IPCPort:
        port = self.get_port(port_id)
        if port is None:
            raise KeyError(f"IPC port '{port_id}' does not exist.")
        return port

    def transfer_send_right(self, port_id: str, to_pid: str) -> None:
        self.require_port(port_id).grant_right(to_pid, PortRight.SEND)

    def destroy_port(self, port_id: str) -> None:
        self._ports.pop(port_id, None)

    def send(
        self,
        port_id: str,
        sender_pid: str,
        msg_type: str,
        payload: Dict[str, Any],
        reply_port_id: Optional[str] = None,
    ) -> IPCMessage:
        port = self.require_port(port_id)
        msg = IPCMessage(
            sender_pid=sender_pid,
            msg_type=msg_type,
            payload=payload,
            reply_port_id=reply_port_id,
        )
        if not port.send(msg):
            raise RuntimeError(f"Port '{port_id}' is full (depth={port.max_queue_depth}).")
        return msg

    def receive(self, port_id: str, receiver_pid: str) -> Optional[IPCMessage]:
        return self.require_port(port_id).receive(receiver_pid)

    def list_ports(self) -> List[Dict[str, Any]]:
        return [
            {
                "port_id": p.port_id,
                "name": p.name,
                "owner_pid": p.owner_pid,
                "depth": p.depth(),
                "max_depth": p.max_queue_depth,
            }
            for p in self._ports.values()
        ]

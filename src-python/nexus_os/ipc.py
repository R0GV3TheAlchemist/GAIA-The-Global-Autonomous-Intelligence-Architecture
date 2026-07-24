"""
nexus_os.ipc — Inter-Process Communication
===========================================
Reference: NEXUS_UNIVERSAL_OS.md § Domain 1 — IPC Subsystem

Provides typed, capability-gated message channels between NEXUS processes.
Channels are unidirectional; bidirectional communication uses two channels.
Delivery semantics are declared per-channel and enforced by the kernel.

All IPC traffic that crosses trust boundaries is logged to the GAIAN
audit trail per GAIAN_LAWS.md § Communication Sovereignty.

© 2026 Kyle Alexander Steen (The Alchemist). All rights reserved.
SPDX-License-Identifier: AGPL-3.0-only
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


class DeliverySemantics(Enum):
    """
    Message delivery guarantees for a Channel.

    AT_MOST_ONCE   — fire-and-forget; messages may be lost.
    AT_LEAST_ONCE  — retried until acknowledged; duplicates possible.
    EXACTLY_ONCE   — guaranteed single delivery (higher overhead).
    """

    AT_MOST_ONCE = auto()
    AT_LEAST_ONCE = auto()
    EXACTLY_ONCE = auto()


@dataclass
class Message(Generic[T]):
    """
    A single unit of inter-process communication.

    Type parameter T is the payload type; callers should parameterise
    explicitly for static analysis (e.g. Message[SensorReading]).
    """

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_pid: str = ""
    recipient_pid: str = ""
    payload: Optional[T] = None
    timestamp_ns: int = 0        # Monotonic send timestamp
    sequence_number: int = 0
    acknowledged: bool = False


class Channel(Generic[T]):
    """
    A unidirectional, capability-gated message channel.

    Channels are created by the kernel in response to a process holding
    a valid IPC capability token.  The channel owner may grant read or
    write access to other processes via sub-tokens.

    Reference: NEXUS_UNIVERSAL_OS.md § Domain 1 — IPC Subsystem
    """

    def __init__(
        self,
        sender_pid: str,
        recipient_pid: str,
        semantics: DeliverySemantics = DeliverySemantics.AT_LEAST_ONCE,
        capacity: int = 256,
    ) -> None:
        self.channel_id: str = str(uuid.uuid4())
        self.sender_pid = sender_pid
        self.recipient_pid = recipient_pid
        self.semantics = semantics
        self.capacity = capacity
        self._queue: List[Message[T]] = []

    def send(self, message: Message[T]) -> None:
        """
        Enqueue a message for delivery to the recipient.

        Args:
            message: The Message to send.

        Raises:
            OverflowError: If the channel queue is at capacity.
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError(
            "Channel.send: stub — implementation pending (NEXUS_UNIVERSAL_OS.md § Domain 1)"
        )

    def receive(self) -> Optional[Message[T]]:
        """
        Dequeue and return the next message, or None if the queue is empty.

        Raises:
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError("Channel.receive: stub")

    def acknowledge(self, message_id: str) -> None:
        """
        Acknowledge receipt of a message (required for AT_LEAST_ONCE and EXACTLY_ONCE).

        Raises:
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError("Channel.acknowledge: stub")

    def is_empty(self) -> bool:
        """
        Return True if the channel queue contains no messages.

        Raises:
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError("Channel.is_empty: stub")

    def drain(self) -> List[Message[T]]:
        """
        Return and clear all queued messages.

        Raises:
            NotImplementedError: Stub — full implementation pending.
        """
        raise NotImplementedError("Channel.drain: stub")

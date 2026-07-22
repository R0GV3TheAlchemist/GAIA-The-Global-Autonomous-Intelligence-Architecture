"""nexusos.ipc

Inter-Process Communication (IPC) layer for NEXUS-OS

Provides typed Channel and Message abstractions for in-process and
distributed communication across GAIAN nodes. Modelled after ZeroMQ's
transport-agnostic socket model and the actor model (Pykka/Thespian).

ZMQ pattern mapping:
    REQ/REP   → Kernel ↔ HAL driver synchronous calls
    PUB/SUB   → Telemetry broadcast, stage transition events
    PUSH/PULL → Task pipeline / scheduler workers
    DEALER/ROUTER → Multi-GAIAN mesh routing

Critical constraint (from ZeroMQ guide):
    ZMQ Contexts are thread-safe; sockets are NOT.
    Enforce one Channel (socket) per thread at the class level.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 1.4 - IPC
Research reference:
    ZeroMQ Guide for Python (zguide2.wdfiles.com)
    Pykka actor model — no shared state, mailbox-only communication
    GAIAN_LAWS.md Law III — No Silent Override (messages must be traceable)
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Optional

logger = logging.getLogger("nexusos.ipc")


class DeliverySemantics(Enum):
    """Message delivery guarantee levels.

    Maps to ZeroMQ socket patterns and GAIAN sovereignty laws:
        AT_MOST_ONCE   → fire-and-forget (PUB/SUB)
        AT_LEAST_ONCE  → retry until ack (PUSH/PULL with persistence)
        EXACTLY_ONCE   → idempotent delivery with dedup ledger (DEALER/ROUTER)
    """
    AT_MOST_ONCE = auto()
    AT_LEAST_ONCE = auto()
    EXACTLY_ONCE = auto()


@dataclass
class Message:
    """A typed IPC message envelope.

    Fields:
        topic:      Routing topic / channel name.
        payload:    Arbitrary message body (must be JSON-serialisable in Phase B+).
        sender:     Identity of the originating module or kernel context.
        message_id: Unique UUID4 for deduplication (EXACTLY_ONCE semantics).
        timestamp:  UTC timestamp of message creation.
        zero_copy:  Hint to the transport layer to avoid payload copy (ZMQ zmq_msg_init_data).
        delivery:   Delivery semantic for this message.
    """
    topic: str
    payload: Any
    sender: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    zero_copy: bool = False
    delivery: DeliverySemantics = DeliverySemantics.AT_MOST_ONCE


class Channel:
    """A typed IPC channel between NEXUS components.

    Each Channel instance is bound to a single topic and transport.
    One Channel per thread — enforced at runtime in Phase B implementation.

    Supports:
        - send(message)     → dispatch to all subscribers
        - subscribe(cb)     → register a callback for incoming messages
        - close()           → release transport resources

    Reference:
        ZeroMQ guide — PUB/SUB, PUSH/PULL, DEALER/ROUTER patterns.
        Actor model  — each Channel is a mailbox; no shared state.
    """

    def __init__(self, topic: str, semantics: DeliverySemantics = DeliverySemantics.AT_MOST_ONCE) -> None:
        self.topic = topic
        self.semantics = semantics
        self._subscribers: list = []
        logger.info("Channel '%s' created (semantics=%s).", topic, semantics)

    def send(self, message: Message) -> None:
        """Dispatch a Message to all registered subscribers.

        Args:
            message: The Message to dispatch.

        Raises:
            NotImplementedError: ZMQ transport not yet wired.
                Expected: validate message.topic == self.topic,
                serialise payload, dispatch via zmq socket,
                handle AT_LEAST_ONCE retry logic.
        """
        raise NotImplementedError(
            "Channel.send() not yet implemented. "
            "Expected: serialise message, dispatch via pyzmq socket, "
            "handle delivery semantics (retry/dedup)."
        )

    def subscribe(self, callback) -> None:
        """Register a callback to receive messages on this channel.

        Args:
            callback: Callable accepting a single Message argument.
        """
        self._subscribers.append(callback)
        logger.debug("Channel '%s': subscriber registered.", self.topic)

    def close(self) -> None:
        """Close the channel and release transport resources.

        Raises:
            NotImplementedError: Transport teardown not yet implemented.
        """
        raise NotImplementedError(
            "Channel.close() not yet implemented. "
            "Expected: close pyzmq socket, flush pending messages."
        )

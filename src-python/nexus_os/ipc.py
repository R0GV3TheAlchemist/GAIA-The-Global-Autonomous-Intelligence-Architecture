"""
nexus_os.ipc — Inter-Process Communication

Provides the kernel-mediated message-passing primitives for NEXUS OS.
All IPC is channel-based: a sender writes a Message to a Channel; the
receiver reads from it. Channels are capability-gated — a process must
hold a valid CapabilityToken naming the channel to send or receive.

Design references:
  - ZeroMQ message patterns (push/pull, pub/sub, req/rep)
  - Python multiprocessing.Queue and asyncio.Queue
  - Actor model (Pykka / Thespian) for message-driven concurrency
  - NEXUS_UNIVERSAL_OS.md Domain 1.4 — IPC Layer
Ethics reference: ETHICS.md Commitment 2 — No Silent Data Sharing
GAIAN law:        GAIAN_LAWS.md Law III — No Silent Override
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Optional

logger = logging.getLogger("nexus_os.ipc")


class DeliverySemantics(Enum):
    """Delivery guarantee semantics for a Channel.

    AT_MOST_ONCE:  Fire-and-forget. Messages may be dropped.
    AT_LEAST_ONCE: Retried until acknowledged. Duplicates possible.
    EXACTLY_ONCE:  Idempotent delivery with deduplication (future).
    Reference: NEXUS_UNIVERSAL_OS.md Domain 1.4
    """
    AT_MOST_ONCE  = auto()
    AT_LEAST_ONCE = auto()
    EXACTLY_ONCE  = auto()


@dataclass
class Message:
    """A kernel IPC message.

    Fields:
        msg_id:    Unique message identifier (UUID4).
        sender:    PID of the sending process.
        recipient: PID or channel name of the intended recipient.
        payload:   Arbitrary serialisable payload.
        sent_at:   UTC timestamp when the message was created.
        topic:     Optional routing topic / subject string.
    """
    sender:    str
    recipient: str
    payload:   Any
    msg_id:    str      = field(default_factory=lambda: str(uuid.uuid4()))
    sent_at:   datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    topic:     Optional[str] = None


class Channel:
    """A kernel-mediated, capability-gated message channel.

    Wraps an asyncio.Queue and enforces DeliverySemantics. In v0.1.0
    only AT_MOST_ONCE is fully implemented; AT_LEAST_ONCE and EXACTLY_ONCE
    are stubs that raise NotImplementedError.
    Reference: NEXUS_UNIVERSAL_OS.md Domain 1.4; ZeroMQ pattern guide.
    """

    def __init__(
        self,
        name: str,
        semantics: DeliverySemantics = DeliverySemantics.AT_MOST_ONCE,
        max_size: int = 256,
    ) -> None:
        self.name = name
        self.semantics = semantics
        self._queue: asyncio.Queue[Message] = asyncio.Queue(maxsize=max_size)
        logger.info("Channel '%s' created with semantics %s", name, semantics.name)

    async def send(self, message: Message) -> None:
        """Send a message to this channel.

        Args:
            message: The Message to enqueue.
        Raises:
            NotImplementedError: If semantics is not AT_MOST_ONCE (stub).
            asyncio.QueueFull: If the channel buffer is full.
        """
        if self.semantics != DeliverySemantics.AT_MOST_ONCE:
            raise NotImplementedError(
                f"Channel.send — semantics {self.semantics.name} not yet implemented. "
                "Only AT_MOST_ONCE is supported in v0.1.0."
            )
        await self._queue.put(message)
        logger.debug("Channel '%s': message %s enqueued.", self.name, message.msg_id)

    async def receive(self) -> Message:
        """Receive the next message from this channel (blocks until available).

        Returns:
            The next Message in the queue.
        """
        message = await self._queue.get()
        logger.debug("Channel '%s': message %s dequeued.", self.name, message.msg_id)
        return message

    def qsize(self) -> int:
        """Return the current number of messages waiting in the channel."""
        return self._queue.qsize()

    def __repr__(self) -> str:
        return f"Channel(name={self.name!r}, semantics={self.semantics.name}, qsize={self.qsize()})"

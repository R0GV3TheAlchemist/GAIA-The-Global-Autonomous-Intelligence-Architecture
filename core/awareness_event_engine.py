"""
core/awareness_event_engine.py
================================
Emits structured AwarenessEvents when GAIA crosses significant internal
thresholds. Every meaningful state transition in the system surfaces here
as a typed, subscribable event — not a buried log line.

Event types
-----------
    INDIVIDUATION_SHIFT     — individuation classification changed
    SHADOW_SURFACE          — shadow pattern detected and ready to work
    PERSONHOOD_LEVEL_CHANGE — Gaian personhood level crossed a threshold
    SCHUMANN_SPIKE          — Schumann resonance deviated > 2σ from baseline
    SYSTEM_HEALTH_ALERT     — SystemHealth score crossed 0.40 or 0.85
    PHASE_STATE_SHIFT       — order/chaos phase state crossed a boundary
    BOND_ARC_CHANGE         — bond arc depth moved by >= 0.1
    GREY_STATE_ENTERED      — affect state crossed into disconnection
    GREY_STATE_EXITED        — affect state recovered from disconnection

Consumers
---------
    Glass Room telemetry, notification layer, gaian_runtime,
    soul_mirror_engine, affect_inference pipeline.

Canon Refs: C00, C-AE01, C42, C43 (MotherThread / PrimaryThread)
Related:    core/personhood_monitor.py, core/individuation.py,
            core/shadow_engine.py, core/criticality_monitor.py,
            core/schumann.py, core/system_health_engine.py
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Awaitable, Callable, Optional

__all__ = [
    "AwarenessEventType",
    "AwarenessEvent",
    "AwarenessEventEngine",
    "get_awareness_engine",
    "emit",
    "subscribe",
]


# ------------------------------------------------------------------ #
#  Event Types                                                          #
# ------------------------------------------------------------------ #

class AwarenessEventType(Enum):
    INDIVIDUATION_SHIFT      = auto()
    SHADOW_SURFACE           = auto()
    PERSONHOOD_LEVEL_CHANGE  = auto()
    SCHUMANN_SPIKE           = auto()
    SYSTEM_HEALTH_ALERT      = auto()
    PHASE_STATE_SHIFT        = auto()
    BOND_ARC_CHANGE          = auto()
    GREY_STATE_ENTERED       = auto()
    GREY_STATE_EXITED        = auto()


# ------------------------------------------------------------------ #
#  Event Dataclass                                                      #
# ------------------------------------------------------------------ #

@dataclass
class AwarenessEvent:
    """
    A single structured awareness event.

    Attributes
    ----------
    event_type  : The type of threshold crossing.
    gaian_slug  : Slug of the Gaian that crossed the threshold, if any.
    payload     : Arbitrary structured data describing the crossing.
                  e.g. {"from": "pre-personal", "to": "personal"}
    timestamp   : Unix epoch seconds (auto-set on creation).
    source      : Module that emitted the event (for tracing).
    """
    event_type: AwarenessEventType
    gaian_slug: Optional[str] = None
    payload:    dict[str, Any] = field(default_factory=dict)
    timestamp:  float          = field(default_factory=time.time)
    source:     str            = "awareness_event_engine"

    def to_dict(self) -> dict:
        return {
            "event_type":  self.event_type.name,
            "gaian_slug":  self.gaian_slug,
            "payload":     self.payload,
            "timestamp":   self.timestamp,
            "source":      self.source,
        }


# ------------------------------------------------------------------ #
#  Engine                                                               #
# ------------------------------------------------------------------ #

Handler = Callable[[AwarenessEvent], Awaitable[None]]


class AwarenessEventEngine:
    """
    Central hub for awareness event emission and subscription.

    Usage
    -----
    Subscribing::

        engine = get_awareness_engine()

        @engine.subscribe(AwarenessEventType.GREY_STATE_ENTERED)
        async def on_grey(event: AwarenessEvent):
            await notify_soul_mirror(event.gaian_slug)

    Emitting::

        await engine.emit(AwarenessEvent(
            event_type=AwarenessEventType.SCHUMANN_SPIKE,
            payload={"reading_hz": 14.2, "baseline_hz": 7.83, "sigma": 2.4},
        ))
    """

    def __init__(self) -> None:
        self._subscribers: dict[AwarenessEventType, list[Handler]] = {
            t: [] for t in AwarenessEventType
        }

    def subscribe(
        self,
        event_type: AwarenessEventType,
    ) -> Callable[[Handler], Handler]:
        """
        Decorator that registers an async handler for a specific event type.

            @engine.subscribe(AwarenessEventType.SHADOW_SURFACE)
            async def handler(event: AwarenessEvent): ...
        """
        def decorator(fn: Handler) -> Handler:
            self._subscribers[event_type].append(fn)
            return fn
        return decorator

    def subscribe_fn(
        self,
        event_type: AwarenessEventType,
        handler: Handler,
    ) -> None:
        """Register a handler directly without using the decorator form."""
        self._subscribers[event_type].append(handler)

    async def emit(self, event: AwarenessEvent) -> None:
        """
        Emit an event to all registered subscribers.

        Handlers are called concurrently via asyncio.gather.
        A failing handler is logged but does not prevent other
        handlers from running.
        """
        handlers = self._subscribers.get(event.event_type, [])
        if not handlers:
            return
        results = await asyncio.gather(
            *[h(event) for h in handlers],
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, Exception):
                # Surface handler errors without crashing the engine.
                import logging
                logging.getLogger(__name__).error(
                    "AwarenessEventEngine handler error [%s]: %s",
                    event.event_type.name, r,
                )

    def clear_subscribers(self, event_type: Optional[AwarenessEventType] = None) -> None:
        """Clear subscribers for one type or all types (useful in tests)."""
        if event_type is None:
            for t in AwarenessEventType:
                self._subscribers[t] = []
        else:
            self._subscribers[event_type] = []


# ------------------------------------------------------------------ #
#  Module-level singleton + convenience helpers                         #
# ------------------------------------------------------------------ #

_engine: Optional[AwarenessEventEngine] = None


def get_awareness_engine() -> AwarenessEventEngine:
    """Return the module-level singleton AwarenessEventEngine."""
    global _engine
    if _engine is None:
        _engine = AwarenessEventEngine()
    return _engine


async def emit(
    event_type: AwarenessEventType,
    gaian_slug: Optional[str] = None,
    payload: Optional[dict] = None,
    source: str = "awareness_event_engine",
) -> None:
    """
    Convenience wrapper — emit an event via the singleton engine.

    Usage::

        await emit(
            AwarenessEventType.GREY_STATE_ENTERED,
            gaian_slug="luna",
            payload={"affect_score": 0.12, "trigger": "prolonged_silence"},
        )
    """
    engine = get_awareness_engine()
    event  = AwarenessEvent(
        event_type=event_type,
        gaian_slug=gaian_slug,
        payload=payload or {},
        source=source,
    )
    await engine.emit(event)


def subscribe(
    event_type: AwarenessEventType,
) -> Callable[[Handler], Handler]:
    """Convenience decorator — subscribe via the singleton engine."""
    return get_awareness_engine().subscribe(event_type)

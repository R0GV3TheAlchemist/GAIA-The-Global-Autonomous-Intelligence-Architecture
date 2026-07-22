"""sidecar.telemetry.telemetry_collector

TelemetryCollector — Structured telemetry emission stub.

This module is the canonical location for TelemetryCollector so that
main.py's import resolves correctly::

    from sidecar.telemetry.telemetry_collector import TelemetryCollector

Design intent
-------------
Every NEXUS module can obtain a TelemetryCollector instance and call
``emit()`` to record a structured event or metric. The collector:

1. Buffers events in-process (ring buffer, configurable max size).
2. Forwards buffered events to registered subscribers on ``flush()``.
3. Supports a subscribe / unsubscribe pattern so multiple sinks
   (OTLP exporter, Prometheus push-gateway, local file, audit_store)
   can receive the same stream.

Phase B scope
-------------
- ``emit()`` and ``flush()`` are fully functional (in-memory ring buffer
  + subscriber dispatch).
- Transport export methods (OTLP, Prometheus) are stubbed with
  ``NotImplementedError`` and implementation guidance.

Future transports
-----------------
- OpenTelemetry OTLP: ``opentelemetry-sdk`` +
  ``opentelemetry-exporter-otlp-proto-grpc``.
- Prometheus: ``prometheus_client`` push-gateway.
- Direct pipe to ``core.obs.audit_store.AuditStore`` for governance
  audit trails.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

@dataclass
class TelemetryEvent:
    """A single structured telemetry event.

    Parameters
    ----------
    source:
        Identifier of the emitting module / component (e.g. ``"schumann"``,
        ``"mesh.router"``).
    name:
        Short event name (e.g. ``"sync_pulse_emitted"``,
        ``"task_scheduled"``).
    payload:
        Arbitrary key-value payload. Keep values JSON-serialisable.
    level:
        Severity / verbosity level: ``"DEBUG"``, ``"INFO"``, ``"WARN"``,
        ``"ERROR"``, ``"CRITICAL"``.
    event_id:
        Auto-generated UUID for deduplication / correlation.
    timestamp:
        UTC timestamp assigned at construction time.
    """
    source: str
    name: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    level: str = "INFO"
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )


@dataclass
class TelemetryConfig:
    """Configuration for TelemetryCollector.

    Parameters
    ----------
    max_buffer_size:
        Maximum events in the in-process ring buffer before oldest
        events are evicted.
    auto_flush_interval_s:
        Seconds between automatic background flushes. 0 disables auto-flush.
    default_source:
        Default ``source`` tag applied when ``emit()`` omits it.
    """
    max_buffer_size: int = 1000
    auto_flush_interval_s: float = 5.0
    default_source: str = "nexus"


SubscriberFn = Callable[[Sequence["TelemetryEvent"]], None]


# ---------------------------------------------------------------------------
# TelemetryCollector
# ---------------------------------------------------------------------------

class TelemetryCollector:
    """Primary telemetry collection interface for NEXUS.

    Usage (Phase B)
    ---------------
    .. code-block:: python

        from sidecar.telemetry.telemetry_collector import TelemetryCollector

        collector = TelemetryCollector()
        collector.emit(
            source="schumann",
            name="sync_pulse_emitted",
            payload={"frequency_hz": 7.83, "confidence": 0.97},
        )
        collector.flush()  # forwards to registered subscribers

    Transport integration (Phase C / D)
    ------------------------------------
    Register a subscriber to receive batches::

        def my_sink(events):
            for e in events:
                print(e)

        collector.subscribe(my_sink)
    """

    def __init__(self, config: TelemetryConfig | None = None) -> None:
        self._config: TelemetryConfig = config or TelemetryConfig()
        self._buffer: list[TelemetryEvent] = []
        self._subscribers: list[SubscriberFn] = []

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def emit(
        self,
        name: str,
        payload: Mapping[str, Any] | None = None,
        source: str | None = None,
        level: str = "INFO",
    ) -> TelemetryEvent:
        """Emit a telemetry event into the ring buffer.

        Args:
            name:    Short event name.
            payload: Key-value data to attach.
            source:  Emitting module identifier. Falls back to
                     ``config.default_source``.
            level:   Severity level string.

        Returns:
            The constructed ``TelemetryEvent``.
        """
        event = TelemetryEvent(
            source=source or self._config.default_source,
            name=name,
            payload=payload or {},
            level=level,
        )
        self._buffer.append(event)
        if len(self._buffer) > self._config.max_buffer_size:
            self._buffer.pop(0)
        return event

    def flush(self) -> int:
        """Forward all buffered events to subscribers and clear buffer.

        Returns:
            Number of events flushed.
        """
        if not self._buffer:
            return 0
        snapshot = list(self._buffer)
        self._buffer.clear()
        for subscriber in self._subscribers:
            try:
                subscriber(snapshot)
            except Exception:  # noqa: BLE001
                pass
        return len(snapshot)

    def subscribe(self, fn: SubscriberFn) -> None:
        """Register a subscriber callable."""
        if fn not in self._subscribers:
            self._subscribers.append(fn)

    def unsubscribe(self, fn: SubscriberFn) -> None:
        """Remove a previously registered subscriber."""
        self._subscribers = [s for s in self._subscribers if s is not fn]

    # ------------------------------------------------------------------
    # Export stubs (Phase C / D)
    # ------------------------------------------------------------------

    def export_otlp(self, endpoint: str) -> None:
        """Export buffered events via OTLP.

        Raises:
            NotImplementedError: Always in Phase B.
        """
        raise NotImplementedError(
            "TelemetryCollector.export_otlp is not yet implemented. "
            "Expected: flush buffer and forward via opentelemetry-exporter-otlp "
            f"to {endpoint!r}."
        )

    def export_prometheus(self, gateway_url: str) -> None:
        """Push metrics to a Prometheus push-gateway.

        Raises:
            NotImplementedError: Always in Phase B.
        """
        raise NotImplementedError(
            "TelemetryCollector.export_prometheus is not yet implemented. "
            "Expected: aggregate metrics and push via prometheus_client "
            f"to {gateway_url!r}."
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def buffer_size(self) -> int:
        """Return number of events currently buffered."""
        return len(self._buffer)

    def snapshot(self) -> list[TelemetryEvent]:
        """Return a copy of the current buffer without flushing."""
        return list(self._buffer)

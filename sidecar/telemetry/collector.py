"""sidecar.telemetry.collector

TelemetryCollector — Structured telemetry emission stub.

Design intent
-------------
Every NEXUS module can obtain a TelemetryCollector instance and call
``emit()`` to record a structured event or metric.  The collector:

1. Buffers events in-process (ring buffer, configurable max size).
2. Forwards buffered events to registered subscribers on ``flush()``.
3. Supports a subscribe / unsubscribe pattern so multiple sinks
   (OTLP exporter, Prometheus push-gateway, local file, audit_store)
   can receive the same stream.

Phase B scope
-------------
- All transport / export methods are stubbed and raise
  ``NotImplementedError`` with implementation guidance.
- ``emit()`` stores events in ``self._buffer`` so callers can at least
  verify round-trips in unit tests without a real sink.

Future transports
-----------------
- OpenTelemetry OTLP: ``opentelemetry-sdk`` + ``opentelemetry-exporter-otlp``.
- Prometheus: ``prometheus_client`` push-gateway.
- InfluxDB: ``influxdb-client``.
- Direct pipe to ``core.obs.audit_store.AuditStore`` for governance
  audit trails.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, MutableList, Sequence
import uuid

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
        Arbitrary key-value payload.  Keep values JSON-serialisable.
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
        Maximum number of events to hold in the in-process buffer before
        the oldest events are evicted (ring-buffer semantics).
    auto_flush_interval_s:
        Seconds between automatic background flushes.  Set to 0 to
        disable automatic flushing (manual flush only).
    default_source:
        Default ``source`` tag applied when ``emit()`` is called without
        an explicit source override.
    """
    max_buffer_size: int = 1000
    auto_flush_interval_s: float = 5.0
    default_source: str = "nexus"


# Subscriber callable type: receives a batch of TelemetryEvent instances.
SubscriberFn = Callable[[Sequence["TelemetryEvent"]], None]


# ---------------------------------------------------------------------------
# TelemetryCollector
# ---------------------------------------------------------------------------

class TelemetryCollector:
    """Primary telemetry collection interface for NEXUS.

    Usage (Phase B stub)
    --------------------
    .. code-block:: python

        from sidecar.telemetry import TelemetryCollector

        collector = TelemetryCollector()
        collector.emit(
            source="schumann",
            name="sync_pulse_emitted",
            payload={"frequency_hz": 7.83, "confidence": 0.97},
        )
        collector.flush()  # forwards to registered subscribers

    Transport integration
    ---------------------
    Register a subscriber to receive batches::

        def my_sink(events):
            for e in events:
                print(e)

        collector.subscribe(my_sink)

    Phase C / D will replace stubs with real OTLP / Prometheus exporters.
    """

    def __init__(self, config: TelemetryConfig | None = None) -> None:
        """Initialise the collector.

        Args:
            config: Optional ``TelemetryConfig``.  Defaults to
                    ``TelemetryConfig()`` if not provided.
        """
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
        """Emit a telemetry event.

        Creates a ``TelemetryEvent`` and appends it to the internal buffer.
        If the buffer exceeds ``config.max_buffer_size``, the oldest event
        is evicted (ring-buffer semantics).

        Args:
            name:    Short event name.
            payload: Key-value data to attach to the event.
            source:  Emitting module identifier.  Falls back to
                     ``config.default_source`` when omitted.
            level:   Severity level string.

        Returns:
            The constructed ``TelemetryEvent`` (useful for testing).
        """
        event = TelemetryEvent(
            source=source or self._config.default_source,
            name=name,
            payload=payload or {},
            level=level,
        )
        self._buffer.append(event)
        # Enforce ring-buffer size limit.
        if len(self._buffer) > self._config.max_buffer_size:
            self._buffer.pop(0)
        return event

    def flush(self) -> int:
        """Forward all buffered events to registered subscribers and clear
        the buffer.

        Returns:
            Number of events flushed.

        Intended implementation
        -----------------------
        - Call each registered ``SubscriberFn`` with a snapshot of
          ``self._buffer``.
        - On success, clear ``self._buffer``.
        - On subscriber error, log and continue (never lose events).
        """
        if not self._buffer:
            return 0
        snapshot = list(self._buffer)
        self._buffer.clear()
        for subscriber in self._subscribers:
            try:
                subscriber(snapshot)
            except Exception:  # noqa: BLE001
                # Phase B: swallow errors; Phase C will add structured
                # error handling / dead-letter queue.
                pass
        return len(snapshot)

    def subscribe(self, fn: SubscriberFn) -> None:
        """Register a subscriber to receive flushed event batches.

        Args:
            fn: Callable accepting a ``Sequence[TelemetryEvent]``.
        """
        if fn not in self._subscribers:
            self._subscribers.append(fn)

    def unsubscribe(self, fn: SubscriberFn) -> None:
        """Remove a previously registered subscriber.

        Args:
            fn: Subscriber callable to remove.
        """
        self._subscribers = [s for s in self._subscribers if s is not fn]

    # ------------------------------------------------------------------
    # Export stubs (Phase C / D)
    # ------------------------------------------------------------------

    def export_otlp(self, endpoint: str) -> None:
        """Export buffered events via OTLP (OpenTelemetry Protocol).

        Intended implementation
        -----------------------
        - Use ``opentelemetry-sdk`` + ``opentelemetry-exporter-otlp-proto-grpc``.
        - Flush buffer and forward each ``TelemetryEvent`` as an OTLP
          ``LogRecord`` or ``Span`` depending on ``event.level``.

        Args:
            endpoint: OTLP collector endpoint (e.g.
                      ``"http://otel-collector:4317"``).

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

        Intended implementation
        -----------------------
        - Aggregate numeric payloads from buffered events into
          ``prometheus_client.Gauge`` / ``Counter`` objects.
        - Call ``push_to_gateway(gateway_url, ...)``.

        Args:
            gateway_url: Prometheus push-gateway URL.

        Raises:
            NotImplementedError: Always in Phase B.
        """
        raise NotImplementedError(
            "TelemetryCollector.export_prometheus is not yet implemented. "
            "Expected: aggregate metrics and push via prometheus_client "
            f"to {gateway_url!r}."
        )

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def buffer_size(self) -> int:
        """Return the number of events currently in the buffer."""
        return len(self._buffer)

    def snapshot(self) -> list[TelemetryEvent]:
        """Return a copy of the current buffer without flushing."""
        return list(self._buffer)

"""telemetry — local src-python mirror of sidecar.telemetry

Provides a thin re-export so modules inside src-python can use::

    from telemetry import TelemetryCollector

without needing a fully qualified ``sidecar.*`` path. Delegates all
implementation to ``sidecar.telemetry.telemetry_collector``.
"""
from __future__ import annotations
from sidecar.telemetry.telemetry_collector import TelemetryCollector, TelemetryEvent, TelemetryConfig

__all__ = ["TelemetryCollector", "TelemetryEvent", "TelemetryConfig"]

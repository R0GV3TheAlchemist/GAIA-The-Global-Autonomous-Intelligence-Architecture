"""sidecar.telemetry

Telemetry collection sidecar for NEXUS.

Exports TelemetryCollector for the main.py import contract::

    from sidecar.telemetry import TelemetryCollector
    from sidecar.telemetry.telemetry_collector import TelemetryCollector

Both forms resolve correctly.
"""
from __future__ import annotations
from sidecar.telemetry.telemetry_collector import TelemetryCollector

__all__ = ["TelemetryCollector"]

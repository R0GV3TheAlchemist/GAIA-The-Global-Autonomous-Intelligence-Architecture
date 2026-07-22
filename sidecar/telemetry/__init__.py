"""sidecar.telemetry

Telemetry collection sidecar for NEXUS.

This package provides:
  - TelemetryCollector: the primary interface for emitting structured
    telemetry events and metrics from any NEXUS module.

Phase B — satisfies the main.py import contract:
    from sidecar.telemetry import TelemetryCollector

All heavy transport logic (OTLP, Prometheus, InfluxDB) is stubbed;
subscribe() / flush() / emit() are ready-to-wire interfaces.
"""
from __future__ import annotations
from sidecar.telemetry.collector import TelemetryCollector

__all__ = ["TelemetryCollector"]

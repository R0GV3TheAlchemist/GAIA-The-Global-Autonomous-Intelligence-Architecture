"""telemetry.collector — local mirror shim

Re-exports TelemetryCollector from the canonical sidecar package.
Kept here so any src-python module that does::

    from telemetry.collector import TelemetryCollector

continues to work without modification.
"""
from __future__ import annotations
from sidecar.telemetry.telemetry_collector import TelemetryCollector  # noqa: F401

"""core.obs

Observability sub-package for the NEXUS core runtime.

Provides:
  - audit_store.AuditStore: tamper-evident, append-only audit log for
    governance-relevant events across all NEXUS modules.

Future additions (Phase D):
  - metrics.MetricsRegistry: Prometheus-compatible registry.
  - trace.TraceContext: distributed tracing context propagation.
"""
from __future__ import annotations

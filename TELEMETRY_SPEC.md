# TELEMETRY_SPEC.md — NEXUS Telemetry Pipeline Architecture

> **Series:** TR-008–TR-019  
> **Status:** Design Complete — Implementation Pending  
> **Owner:** Kyle Steen (@R0GV3TheAlchemist)  
> **Last Updated:** 2026-07-21

---

## 1. Overview

The NEXUS telemetry subsystem implements an **OpenTelemetry-native observability pipeline** covering metrics, structured logs, and distributed traces. It is designed for planetary-scale deployments where signal volume is high, network paths are heterogeneous, and SLA enforcement requires automated alerting.

---

## 2. OTel Pipeline Design

```
[Instrumented Code]
      |
      ▼
[MetricEmitter / StructuredLogger / TraceContext]  ← SDK layer (this package)
      |
      ▼
[OTel SDK: BatchSpanProcessor + PeriodicMetricReader]
      |
      ▼
[OTel Collector (sidecar per node)]
      |           |
      ▼           ▼
[Prometheus]  [Tempo/Jaeger]   ← backend (operator choice)
      |
      ▼
[Grafana / AlertManager]
```

The NEXUS telemetry package provides the **SDK layer** only. Collector and backend deployment is handled by the `k8s/` and `sidecar/` packages.

---

## 3. Metric Taxonomy

### 3.1 Namespace Convention

```
nexus.<package>.<resource>.<measurement>
```

Examples:
- `nexus.kernel.process.active_count` — gauge
- `nexus.network.link.latency_ms` — histogram
- `nexus.governance.proposal.vote_count` — counter
- `nexus.security.token.issue_rate` — counter
- `nexus.resilience.circuit_breaker.open_count` — counter
- `nexus.telemetry.pipeline.dropped_count` — counter (self-monitoring)

### 3.2 Mandatory Labels

Every metric MUST carry these labels:

| Label | Description |
|---|---|
| `nexus_node_id` | Emitting node UUID |
| `nexus_cluster` | Cluster identifier |
| `nexus_package` | Package name |
| `nexus_class` | Class name |
| `nexus_env` | `production`, `staging`, `dev` |

### 3.3 Cardinality Governance

High-cardinality labels (e.g., per-request IDs) MUST NOT be added to metrics — use traces instead. `MetricEmitter` enforces a max label cardinality of 100 unique combinations per metric name; violations are logged and the metric is dropped.

---

## 4. Trace Propagation Model

### 4.1 Format

NEXUS uses **W3C TraceContext** (RFC 7231) as the primary propagation format. B3 is supported as a secondary format for compatibility with legacy systems.

### 4.2 TraceContext API

```python
class TraceContext:
    def start_span(self, name: str, kind: SpanKind, parent: Span | None) -> Span: ...
    def inject(self, carrier: dict) -> None:  # W3C traceparent/tracestate
    def extract(self, carrier: dict) -> SpanContext: ...
    def current_span(self) -> Span: ...
    def add_event(self, name: str, attributes: dict) -> None: ...
    def set_status(self, status: StatusCode, description: str) -> None: ...
```

### 4.3 Cross-Package Trace Propagation

All NEXUS inter-service calls (gRPC and HTTP) automatically propagate trace context via middleware. The `CapabilityToken` carries a `nexus:trace_id` claim to correlate security events with traces.

### 4.4 Sampling Strategy

| Traffic Type | Sampling Rate |
|---|---|
| CRITICAL tier | 100% |
| REALTIME tier | 10% |
| OPERATIONAL tier | 1% |
| BACKGROUND tier | 0.1% |
| Error spans | 100% always |

---

## 5. AlertEngine

### 5.1 Alert Model

```python
@dataclass
class Alert:
    alert_id: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    source_metric: str
    condition: str       # human-readable, e.g. "latency_p99 > 100ms for 5m"
    fired_at: datetime
    resolved_at: datetime | None
    annotations: dict[str, str]
    runbook_url: str
```

### 5.2 SLA Breach → Alert Flow

```
1. MetricEmitter records measurement
2. SLAMonitor evaluates measurement against SLA thresholds (sliding window)
3. SLAMonitor fires Alert via AlertEngine on breach
4. AlertEngine routes alert to:
   a. GovernanceDAO (for CRITICAL/HIGH — may trigger circuit breaker)
   b. StructuredLogger (all severities — persisted)
   c. External webhook/PagerDuty (CRITICAL/HIGH in production)
5. Alert resolved when metric returns within SLA bounds for 2× the breach window
```

---

## 6. SLAMonitor Configuration

```yaml
sla_monitors:
  - name: network_latency
    metric: nexus.network.link.latency_ms
    window: 5m
    thresholds:
      p50: 10ms
      p95: 50ms
      p99: 100ms
    severity: HIGH
    runbook: https://nexus.docs/runbooks/network-latency

  - name: kernel_availability
    metric: nexus.kernel.process.active_count
    window: 1m
    min_value: 1
    severity: CRITICAL
    runbook: https://nexus.docs/runbooks/kernel-down
```

---

## 7. Requirements Traceability

| Requirement ID | Implemented By |
|---|---|
| TR-008 | `MetricEmitter` OTel SDK wrapper |
| TR-009 | Metric namespace convention |
| TR-010 | Mandatory label enforcement |
| TR-011 | Cardinality governance |
| TR-012 | `StructuredLogger` (JSON, OTel log bridge) |
| TR-013 | `TraceContext` W3C propagation |
| TR-014 | Cross-package trace middleware |
| TR-015 | Sampling strategy implementation |
| TR-016 | `AlertEngine` alert routing |
| TR-017 | `SLAMonitor` sliding-window evaluation |
| TR-018 | GovernanceDAO alert integration |
| TR-019 | External webhook alerting |

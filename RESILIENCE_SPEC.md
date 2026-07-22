# RESILIENCE_SPEC.md — NEXUS Resilience & Chaos Engineering Architecture

> **Series:** RR-001–RR-014  
> **Status:** Design Complete — Implementation Pending  
> **Owner:** Kyle Steen (@R0GV3TheAlchemist)  
> **Last Updated:** 2026-07-21

---

## 1. Overview

The NEXUS resilience subsystem provides **automated fault tolerance, disaster recovery, and chaos engineering** capabilities. It treats failure as inevitable and builds systems that degrade gracefully, recover autonomously, and prove their resilience through controlled chaos experiments.

---

## 2. Fault Domain Hierarchy

```
Planetary Cluster
  └── Region (e.g., "Earth-North-America")
        └── Availability Zone (e.g., "us-central-1a")
              └── Cluster (e.g., "nexus-prod-01")
                    └── Node (individual NEXUS process)
                          └── Service (individual class instance)
```

Failures are classified by their blast radius:
- **Service failure** — single class instance; contained by `Bulkhead`
- **Node failure** — all services on a node; handled by `CircuitBreaker` + failover
- **Cluster failure** — entire cluster; handled by `DRController` + replica promotion
- **Region failure** — cross-region routing via `NetworkFabric` DTN mode
- **Planetary failure** — federation mesh reroutes via `FederationRegistry`

---

## 3. CircuitBreaker

### 3.1 State Machine

```
         failure_threshold exceeded
CLOSED ─────────────────────────────► OPEN
  ▲                                     │
  │ success_threshold met               │ reset_timeout elapsed
  │                                     ▼
HALF_OPEN ◄──────────────────────── OPEN
```

### 3.2 Configuration

```python
@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5        # failures before OPEN
    success_threshold: int = 3        # successes in HALF_OPEN before CLOSED
    reset_timeout_seconds: float = 30 # OPEN → HALF_OPEN wait
    half_open_max_calls: int = 3      # concurrent calls in HALF_OPEN
    error_types: list[type] = field(default_factory=lambda: [Exception])
```

### 3.3 Integration

Circuit breakers are applied as **decorators** on any callable:

```python
@circuit_breaker(config=CircuitBreakerConfig(failure_threshold=3))
def call_remote_service(...):
    ...
```

State changes emit telemetry events to `AlertEngine` via `MetricEmitter`.

---

## 4. Bulkhead

Bulkheads isolate resource pools to prevent cascade failures. NEXUS implements **thread-pool bulkheads**:

```python
@dataclass
class BulkheadConfig:
    max_concurrent_calls: int = 25
    max_wait_duration_ms: int = 500
    name: str = "default"
```

Each service class gets its own bulkhead pool. If `max_concurrent_calls` is reached, additional calls wait up to `max_wait_duration_ms` then raise `BulkheadFullError`. This prevents a slow downstream from exhausting the entire thread pool.

---

## 5. SnapshotManager

The `SnapshotManager` captures and restores consistent state snapshots for stateful NEXUS services.

```python
class SnapshotManager:
    def snapshot(self, service_id: str) -> SnapshotHandle: ...
    def restore(self, service_id: str, handle: SnapshotHandle) -> None: ...
    def list_snapshots(self, service_id: str) -> list[SnapshotHandle]: ...
    def prune(self, service_id: str, keep_last: int = 5) -> None: ...
```

### 5.1 Snapshot Policy

| Service Type | Cadence | Retention |
|---|---|---|
| Stateful agents | Every 5 min | Last 12 |
| DigitalTwin | Every 1 min | Last 60 |
| GovernanceDAO | On every state change | Last 100 |
| ImmutableLedger | Never (append-only) | N/A |

Snapshots are stored in the `storage/` package using content-addressed storage. The `SnapshotHandle` contains the content hash, not a mutable pointer.

---

## 6. DRController (Disaster Recovery)

```
DR State Machine:

NORMAL ──► DEGRADED ──► FAILOVER ──► RECOVERING ──► NORMAL
           (1+ nodes     (primary       (replica
            failed)       unavail)       promoted)
```

### 6.1 DR Runbook — Cluster Failover

1. `DRController` detects primary cluster unavailable (3 missed heartbeats at 1s interval)
2. Quorum vote among surviving nodes (≥ N/2+1 must agree on failover)
3. Highest-ranked replica (by `SnapshotManager` recency + network reachability) promoted to primary
4. `DiscoveryClient` entries updated: old primary deregistered, new primary registered
5. All circuit breakers reset to CLOSED for the new primary
6. `GovernanceDAO` notified of topology change
7. DR event logged to `ImmutableLedger`
8. Recovery: when old primary returns, it rejoins as replica, syncs state, enters RECOVERING phase
9. After RECOVERING sync complete, operator manually promotes or allows auto-rebalance

---

## 7. ChaosEngine

The `ChaosEngine` enables **controlled fault injection** for resilience validation.

### 7.1 Experiment Catalog

| Experiment | Description | Target |
|---|---|---|
| `node_kill` | Terminates a node process | Any node |
| `network_partition` | Drops all packets between two nodes | NetworkFabric |
| `latency_inject` | Adds Gaussian latency to a link | NetworkFabric |
| `packet_loss` | Injects random packet loss % | NetworkFabric |
| `disk_fill` | Fills storage to trigger pressure | SnapshotManager |
| `clock_skew` | Advances/rewinds node clock | TimeService |
| `cpu_stress` | Saturates CPU on a node | OS-level |
| `token_expire` | Force-expires CapabilityTokens | IdentityService |

### 7.2 Safety Controls

- Experiments require a `CapabilityToken` with `resilience:chaos:execute` capability (operator-only)
- Maximum blast radius per experiment is configurable; defaults to 1 node
- A **kill switch** (`ChaosEngine.abort_all()`) immediately halts all active experiments
- Experiments are logged to `ImmutableLedger` for post-mortem analysis
- Chaos is disabled entirely in environments where `NEXUS_ENV=production` and `CHAOS_ENABLED != true`

---

## 8. Requirements Traceability

| Requirement ID | Implemented By |
|---|---|
| RR-001 | `CircuitBreaker` state machine |
| RR-002 | `CircuitBreaker` decorator |
| RR-003 | `Bulkhead` thread-pool isolation |
| RR-004 | `SnapshotManager.snapshot()` |
| RR-005 | `SnapshotManager.restore()` |
| RR-006 | Snapshot cadence policy |
| RR-007 | `DRController` heartbeat detection |
| RR-008 | `DRController` quorum vote |
| RR-009 | `DRController` replica promotion |
| RR-010 | DR runbook — cluster failover |
| RR-011 | `ChaosEngine` experiment catalog |
| RR-012 | `ChaosEngine` safety controls |
| RR-013 | `ChaosEngine` kill switch |
| RR-014 | Fault domain hierarchy enforcement |

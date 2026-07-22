# DISCOVERY_SPEC.md — NEXUS Service Discovery Architecture

> **Series:** DR-001–DR-010  
> **Status:** Design Complete — Implementation Pending  
> **Owner:** Kyle Steen (@R0GV3TheAlchemist)  
> **Last Updated:** 2026-07-21

---

## 1. Overview

The NEXUS discovery subsystem provides **multi-layer service registration and lookup** across node-local, cluster-wide, and inter-planetary federation scopes. It combines a gossip-based membership protocol with a structured `ServiceRegistry` for deterministic lookup and a `FederationRegistry` for cross-cluster mesh coordination.

---

## 2. Design Decisions

### 2.1 Protocol Selection: Gossip over mDNS

mDNS (RFC 6762) is scoped to link-local networks and breaks across routed topologies. NEXUS operates across multi-cluster, multi-planetary networks with high-latency and intermittent connectivity (DTN scenarios). Therefore:

- **Intra-node:** Direct in-process `ServiceRegistry` (no network)
- **Intra-cluster:** SWIM-based gossip protocol (Scalable Weakly-consistent Infection-style Membership)
- **Inter-cluster:** `FederationRegistry` with periodic full-state sync over authenticated channels
- **DTN mode:** Store-and-forward discovery bundles when network is partitioned

### 2.2 Consistency Model

Discovery is **eventually consistent** with conflict resolution via vector clocks on `ServiceRecord`. Strong consistency is not required — callers must tolerate stale entries and retry on `ServiceNotFoundError`.

---

## 3. Data Model

### 3.1 ServiceRecord

```python
@dataclass
class ServiceRecord:
    service_id: str           # nexus:svc:<package>:<class>:<instance_uuid>
    identity: str             # nexus:node:<uuid> or nexus:agent:<domain>:<name>
    package: str              # e.g. "telemetry"
    class_name: str           # e.g. "MetricEmitter"
    endpoints: list[Endpoint] # host/port/protocol tuples
    capabilities: list[str]   # declared capability strings
    health: HealthStatus      # HEALTHY | DEGRADED | UNHEALTHY
    vector_clock: VectorClock # for conflict resolution
    ttl_seconds: int          # default 60; gossip refreshes before expiry
    metadata: dict[str, str]  # arbitrary key-value tags
```

### 3.2 Endpoint

```python
@dataclass
class Endpoint:
    protocol: str   # "grpc", "http", "quic", "dtn"
    host: str
    port: int
    tls: bool       # must be True in production
    priority: int   # lower = preferred; used by DiscoveryClient
```

---

## 4. ServiceRegistry

The `ServiceRegistry` is the authoritative in-process store for a single NEXUS node. It is the single source of truth for all services running on that node.

```
ServiceRegistry
  ├── register(record: ServiceRecord) → None
  ├── deregister(service_id: str) → None
  ├── lookup(package: str, class_name: str) → list[ServiceRecord]
  ├── lookup_by_id(service_id: str) → ServiceRecord | None
  ├── watch(package: str, callback: Callable) → WatchHandle
  ├── all_records() → list[ServiceRecord]
  └── health_check() → dict[str, HealthStatus]
```

**Watch semantics:** Callbacks are invoked on registration, deregistration, and health status change. Useful for load balancers and circuit breakers.

---

## 5. DiscoveryClient

`DiscoveryClient` provides the caller-facing API. It queries local registry first (L1 cache), then cluster gossip (L2), then federation (L3).

```
Lookup resolution order:
  1. Local ServiceRegistry (microseconds)
  2. Cluster gossip table (milliseconds)
  3. FederationRegistry (seconds; cross-planetary)
  4. ServiceNotFoundError raised if all fail
```

The client implements **client-side load balancing** using the `priority` field on `Endpoint` records, with round-robin fallback among equal-priority endpoints.

---

## 6. Federation Protocol

```
Cluster A FederationRegistry              Cluster B FederationRegistry
         |                                         |
         |--- FederationHandshake (auth) --------->|
         |<-- FederationHandshake ACK -----------  |
         |--- FullStateSyncRequest ---------------->|
         |<-- FullStateSyncResponse (all records) --|
         |                                         |
         |--- DeltaUpdate (gossip delta) ---------->|  (every 30s)
         |<-- DeltaUpdate (gossip delta) -----------|
```

- Handshake uses mutual PQC TLS + `CapabilityToken` with `discovery:federation:join` capability
- Full sync on initial join; delta updates every 30 seconds
- Delta updates use a Merkle tree to detect divergence and request missing records

---

## 7. DTN (Delay-Tolerant Networking) Mode

When a cluster is unreachable (e.g., Mars-Earth link blackout), discovery operates in DTN mode:

1. `DiscoveryClient` returns cached records (up to `dtl_ttl_seconds = 3600`)
2. New registrations are queued as **discovery bundles** (RFC 5050 inspired)
3. On reconnection, bundles are replayed against the remote `FederationRegistry`
4. Conflict resolution uses vector clocks: last-writer-wins within same cluster, merge across clusters

---

## 8. Requirements Traceability

| Requirement ID | Implemented By |
|---|---|
| DR-001 | `ServiceRecord` dataclass |
| DR-002 | `ServiceRegistry.register()` |
| DR-003 | `ServiceRegistry.deregister()` |
| DR-004 | `ServiceRegistry.lookup()` |
| DR-005 | `DiscoveryClient` (L1/L2/L3 resolution) |
| DR-006 | `DiscoveryClient` load balancing |
| DR-007 | `FederationRegistry` handshake |
| DR-008 | `FederationRegistry` delta sync |
| DR-009 | DTN bundle store-and-forward |
| DR-010 | `ServiceRegistry.watch()` callbacks |

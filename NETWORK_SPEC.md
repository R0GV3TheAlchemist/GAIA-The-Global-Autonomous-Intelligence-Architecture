# NETWORK_SPEC.md — NEXUS Network Fabric Architecture

> **Series:** NR-001–NR-012  
> **Status:** Design Complete — Implementation Pending  
> **Owner:** Kyle Steen (@R0GV3TheAlchemist)  
> **Last Updated:** 2026-07-21

---

## 1. Overview

The NEXUS `NetworkFabric` is a **software-defined, adaptive, multi-path network layer** that abstracts physical and virtual transport beneath a unified routing API. It supports QoS-tiered traffic, PQC-authenticated sessions, multi-path routing for redundancy, and DTN routing for deep-space or disconnected scenarios.

---

## 2. Topology Model

### 2.1 Graph Representation

The network is modeled as a directed weighted graph `G = (V, E)` where:

- **V (vertices)** = NEXUS nodes (identified by `nexus:node:<uuid>`)
- **E (edges)** = authenticated network links, annotated with:
  - `latency_ms` — measured round-trip latency
  - `bandwidth_mbps` — available bandwidth
  - `loss_rate` — packet loss percentage
  - `qos_tier` — assigned QoS tier
  - `link_type` — `"fiber"`, `"satellite"`, `"laser_com"`, `"dtn_bundle"`

### 2.2 Topology Discovery

Topology is built from `ServiceRecord` entries in the `DiscoveryClient`. The `NetworkFabric` subscribes to discovery watch callbacks to update the topology graph in real time as nodes join/leave.

---

## 3. QoS Tiers

| Tier | Name | Max Latency | Min Bandwidth | Use Case |
|---|---|---|---|---|
| 0 | CRITICAL | 1ms | 10 Gbps | Kernel heartbeat, safety interlock |
| 1 | REALTIME | 10ms | 1 Gbps | Telemetry, actuator commands |
| 2 | OPERATIONAL | 100ms | 100 Mbps | Agent messaging, governance votes |
| 3 | BACKGROUND | 1000ms | 10 Mbps | Sync, bulk data transfer |
| 4 | DTN | unbounded | best-effort | Inter-planetary, disconnected |

Traffic is tagged at the `CapabilityToken` level: `nexus:context.qos_tier` determines scheduling priority.

---

## 4. Routing Algorithms

### 4.1 AdaptiveRouter

Default router for intra-cluster traffic. Uses a modified Dijkstra's algorithm with a composite cost function:

```
cost(e) = α·latency_ms + β·(1/bandwidth_mbps) + γ·loss_rate
```

Weights α, β, γ are tuned per QoS tier (latency-sensitive tiers weight α higher). The router recomputes paths every 5 seconds or on topology change events.

### 4.2 MultipathRouter

For REALTIME and CRITICAL tiers, traffic is split across K=3 disjoint paths simultaneously. The receiver reconstructs the original message from whichever path delivers first (FEC-based erasure coding). Path selection uses ECMP (Equal-Cost Multi-Path) with consistent hashing on `(src, dst, flow_id)`.

### 4.3 DTNRouter

For inter-planetary and partitioned scenarios. Implements Epidemic Routing with custody transfer:

```
1. Message wrapped in DTN Bundle (RFC 5050 structure)
2. Bundle stored locally if no forwarding path exists
3. On contact with a carrier node, bundle is transferred (custody)
4. Custody acknowledgment sent back to originator
5. Bundle delivered when destination is reachable
```

Maximum bundle lifetime: configurable, default 7 days.

---

## 5. PQC Handshake Flow

All NEXUS network sessions use PQC-authenticated mutual TLS. The handshake is defined in SECURITY_SPEC.md §3.3. Network-specific additions:

1. After TLS handshake, both sides exchange `CapabilityToken` with `network:session:establish` capability
2. `NetworkFabric` validates both tokens via local `IdentityService`
3. Session is tagged with negotiated QoS tier
4. All subsequent packets in the session are AEAD-encrypted with per-record keys derived from the session master secret

---

## 6. NetworkFabric API

```python
class NetworkFabric:
    def connect(self, target: str, qos: QoSTier, token: CapabilityToken) -> Session: ...
    def disconnect(self, session: Session) -> None: ...
    def send(self, session: Session, data: bytes) -> None: ...
    def recv(self, session: Session, timeout_ms: int) -> bytes: ...
    def topology(self) -> TopologyGraph: ...
    def route(self, src: str, dst: str, qos: QoSTier) -> list[Path]: ...
    def stats(self) -> NetworkStats: ...
```

---

## 7. Failure Handling

- **Link failure:** `AdaptiveRouter` detects via missed heartbeats (3 × 1s), removes edge, recomputes paths
- **Node failure:** `DiscoveryClient` watch fires, `NetworkFabric` removes all edges for that node
- **Partition:** `DTNRouter` activated for affected partitions; `MultipathRouter` falls back to surviving paths
- **Overload:** QoS tier enforcement via token bucket rate limiting per tier per link

---

## 8. Requirements Traceability

| Requirement ID | Implemented By |
|---|---|
| NR-001 | `NetworkFabric` core |
| NR-002 | `QoSTier` enum + token bucket |
| NR-003 | `AdaptiveRouter` Dijkstra |
| NR-004 | `MultipathRouter` ECMP+FEC |
| NR-005 | `DTNRouter` epidemic routing |
| NR-006 | PQC session handshake |
| NR-007 | Topology graph construction |
| NR-008 | Discovery watch integration |
| NR-009 | Link failure detection |
| NR-010 | QoS tier enforcement |
| NR-011 | DTN bundle custody transfer |
| NR-012 | NetworkStats telemetry export |

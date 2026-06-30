# SIM-005 — Consent Ledger Throughput

**Date:** 2026-06-30
**Status:** COMPLETE — ⚠️ CANON TENSION CT-004 IDENTIFIED
**Canon refs:** C139 (consent ledger), C158 (GDPR compliance, erasure)
**Method:** Monte Carlo, N=3,000 trials per load level, 6 load levels (100–10,000 rps)
**Issue filed:** #710

---

## Setup

**Operations modelled:**
- Read (consent lookup): base 8ms
- Write (grant/revoke + crypto chain update): base 35ms
- GDPR Erase (cascade delete across all memory tiers): base 180ms

**Targets (C139 / C158):**
- Read P95 < 50ms
- Write P95 < 100ms
- GDPR Erase P95 < 500ms
- Error rate < 0.5%

---

## Results

| RPS | Read P95 | Write P95 | Erase P95 | Error Rate | Status |
|---|---|---|---|---|---|
| 100 | 11.9ms | 57.6ms | 322ms | 0.13% | ✅ |
| 500 | 12.0ms | 57.1ms | 314ms | 0.13% | ✅ |
| 1,000 | 12.0ms | 56.9ms | 323ms | 0.10% | ✅ |
| 2,000 | 24.1ms | **116.9ms** ⚠️ | **730ms** ⚠️ | 0.23% | Write + Erase breach |
| 5,000 | 96.1ms | 465.9ms | 3,872ms | **5.60%** ⚠️ | All breach |
| 10,000 | 268ms | 1,332ms | 13,652ms | 17.33% | System non-compliant |

**Safe operating zone: ≤ 1,000 rps (single node)**

---

## ⚠️ Canon Tension CT-004

**C139 single-node consent ledger breaches write and GDPR erase targets at 2,000 rps.**

At population-scale deployment (millions of users), 2,000 rps is easily reachable. GDPR erase latency of 13.6 seconds at 10,000 rps constitutes a regulatory compliance risk.

**Root cause:** C139 specifies a single consent ledger without sharding or horizontal scaling provisions. The implicit assumption of single-node operation must be made explicit and resolved.

---

## Resolution Options

| Option | Change | Canon Impact |
|---|---|---|
| A — Namespace sharding | Shard ledger by user namespace; each shard handles ≤1,000 rps | C139 architecture update |
| B — Read replicas | Add read replicas; reduces read load but doesn't fix write/erase | C139 partial fix |
| C — Async GDPR erasure queue | Queue erasure requests; process within SLA window (e.g. 24h) | C139 + C158 update |
| **D — Combined A+C** | Namespace sharding + async erasure queue with SLA guarantee | C139 + C158 update |

**Recommended: Option D** — sharding handles throughput; async erasure queue ensures GDPR compliance at scale without blocking the ledger.

---

## Artefacts
- `consent_ledger_throughput.png` — P95 latency curves vs load (100–10,000 rps)

*Simulation completed: 2026-06-30. CT-004 flagged. Awaiting R0GV3 decision.*

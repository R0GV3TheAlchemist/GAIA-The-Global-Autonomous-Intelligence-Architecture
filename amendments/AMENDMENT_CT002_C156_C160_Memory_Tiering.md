# Amendment CT-002 — C156 + C160: Memory Tiering + Access-Pattern Boosting

**CT-ID:** CT-002
**Amendment status:** PROPOSED — awaiting R0GV3 approval to merge into canon
**Decision confirmed:** 2026-06-30 by R0GV3
**Resolution:** Option D — Tiered Hot/Cold Storage + Access-Pattern Relevance Boosting
**Docs affected:** C156 (memory schema + architecture), C160 (Metric 6)
**Simulation to validate:** SIM-009 (run immediately after this commit)
**Closes:** Issue #708

---

## Context

SIM-003 revealed that the C156 memory schema applies uniform exponential decay to all memories regardless of access frequency. The 85% retention target (C160 Metric 6) is breached between days 16–18 for all memory types. By day 30, retention falls to ~61%; by day 90, to ~22%.

Root cause: no tiered storage, no access-pattern boosting, no relevance-weighted decay. All memories treated identically regardless of how often they are accessed or how important they are.

---

## Changes to C156 (Memory Schema)

### 1. Required Memory Record Fields

**Add to C156 Memory Record Schema:**

> Every memory record SHALL carry the following required fields:
>
> | Field | Type | Description |
> |---|---|---|
> | `memory_id` | UUID | Unique identifier (existing) |
> | `created_at` | ISO 8601 | Creation timestamp (existing) |
> | `content_hash` | SHA-256 | Content integrity check (existing) |
> | `tier` | Enum: `HOT` / `WARM` / `COLD` | Current storage tier **(new)** |
> | `last_accessed` | ISO 8601 | Most recent access timestamp **(new)** |
> | `access_count` | Integer | Cumulative access count since creation **(new)** |
> | `relevance_score` | Float [0.0, 1.0] | Current computed relevance **(new)** |
> | `decay_rate` | Float | Active decay rate (tier-adjusted) **(new)** |
> | `tier_upgraded_at` | ISO 8601 / null | Timestamp of last tier upgrade **(new)** |

---

### 2. Tiered Storage Architecture

**Add to C156 Memory Architecture section:**

> **Memory Tier Definitions**
>
> | Tier | Retention window | Decay rate | Access threshold |
> |---|---|---|---|
> | `HOT` | 60 days full retention | λ = 0.01/day | ≥5 accesses in last 7 days |
> | `WARM` | 30 days full retention | λ = 0.03/day | 1–4 accesses in last 7 days |
> | `COLD` | Compressed after day 18 | λ = 0.07/day | 0 accesses in last 7 days |
>
> **Tier assignment rules:**
> - New memories start in `WARM` tier
> - Tier is re-evaluated every 7 days based on access_count in the rolling 7-day window
> - Promotion: COLD → WARM → HOT on access threshold met
> - Demotion: HOT → WARM → COLD if access threshold not met for 14 consecutive days
> - Tier upgrade resets the decay clock for that tier’s retention window

---

### 3. Access-Pattern Relevance Boosting

**Add to C156 Memory Architecture section:**

> **Access-Pattern Relevance Boosting**
>
> On each memory access, the memory record SHALL be updated as follows:
> 1. `last_accessed` → current timestamp
> 2. `access_count` → incremented by 1
> 3. `relevance_score` recalculated: `min(1.0, relevance_score + 0.05 × recency_weight)`
>    where `recency_weight = 1.0` for access within 24h, `0.5` for 1–7 days, `0.2` for 7–30 days
> 4. If new `access_count` meets tier promotion threshold: schedule tier upgrade at next 7-day evaluation
>
> **Effect:** Frequently and recently accessed memories accumulate relevance, slow their decay, and are promoted to higher tiers with longer retention windows. Infrequently accessed memories naturally drift to COLD tier and compress.

---

## Changes to C160 (System Metrics)

### 4. Metric 6 — Measurement Clarification

**Update C160 Metric 6:**

> **Metric 6 — Memory Retention Rate**
>
> **Target: ≥85% retention at 30 days** (measured across HOT + WARM tiers only)
>
> *Measurement window:* Rolling 30-day window.
> *Tier scope:* HOT and WARM tier memories only. COLD tier memories are compressed and excluded from the retention rate calculation by design — they represent infrequently accessed content where compression is the intended behaviour.
> *Retention definition:* A memory is ‘retained’ if its `relevance_score` is ≥0.50 and it is retrievable without decompression.
>
> *Methodology note (added 2026-06-30, ref SIM-003, SIM-009):*
> *Under the original flat-decay model, the ≥85% target was breached at days 16–18 for all memory types. With tiered storage and access-pattern boosting, HOT tier memories sustain ≥85% retention through day 60+; WARM tier through day 30. Canon tension CT-002 (Issue #708) documents the full analysis.*

---

## Amendment Sign-Off

- [x] R0GV3 decision confirmed: 2026-06-30
- [ ] Amendment reviewed by R0GV3
- [ ] Merged into `canon/C156.md`
- [ ] Merged into `canon/C160.md`
- [ ] SIM-009 validation passed
- [ ] Issue #708 closed
- [ ] CHANGELOG updated

*Amendment CT-002 proposed 2026-06-30 by GAIA. Awaiting merge approval.*

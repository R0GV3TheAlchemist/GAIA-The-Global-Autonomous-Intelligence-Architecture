# Amendment CT-005 — C156: Knowledge Graph Gardening Pass

**CT-ID:** CT-005
**Amendment status:** PROPOSED — awaiting R0GV3 approval to merge into canon
**Decision confirmed:** 2026-06-30 by R0GV3
**Resolution:** KG Gardening Pass — required background maintenance process
**Docs affected:** C156 (Knowledge Graph schema + architecture)
**Simulation to validate:** SIM-012 (run immediately after this commit)
**Closes:** Issue #711

---

## Context

SIM-006 revealed that without a maintenance layer, the C156 knowledge graph degrades severely over time:
- Degraded edges (confidence < 0.70): **80.5%** by cycle 1,000
- Orphaned provenance links: **100%** by cycle 700 (breach of 5% target at cycle 29)
- Contradictions: **0%** throughout — edge validation logic validated ✅

Root cause: C156 specifies no periodic re-validation, provenance re-anchoring, or pruning mechanism.

---

## Changes to C156 (Knowledge Graph Schema + Architecture)

### 1. Required Schema Fields — All Nodes

**Add to C156 Node Schema:**

> Every knowledge graph node SHALL carry the following required metadata fields:
>
> | Field | Type | Description |
> |---|---|---|
> | `node_id` | UUID | Unique identifier (existing) |
> | `created_at` | ISO 8601 timestamp | Creation time (existing) |
> | `source_ref` | String | Provenance source reference (existing) |
> | `provenance_status` | Enum: `VERIFIED` / `STALE` / `ORPHANED` | Current provenance state **(new)** |
> | `last_validated` | ISO 8601 timestamp | Last time provenance was confirmed **(new)** |
> | `access_count` | Integer | Total access count since creation **(new)** |
> | `last_accessed` | ISO 8601 timestamp | Last access time **(new)** |

### 2. Required Schema Fields — All Edges

**Add to C156 Edge Schema:**

> Every knowledge graph edge SHALL carry the following required metadata fields:
>
> | Field | Type | Description |
> |---|---|---|
> | `edge_id` | UUID | Unique identifier (existing) |
> | `created_at` | ISO 8601 timestamp | Creation time (existing) |
> | `confidence_score` | Float [0.0, 1.0] | Current confidence in this relationship **(new)** |
> | `last_revalidated` | ISO 8601 timestamp | Last time confidence was recomputed **(new)** |
> | `revalidation_count` | Integer | Number of revalidation passes completed **(new)** |

---

### 3. KG Gardening Pass — Required Background Process

**Add to C156 Architecture section:**

> **KG Gardening Pass — Required Component**
>
> The knowledge graph subsystem SHALL run a periodic KG Gardening Pass as a required background process. The Gardening Pass has four components, executed in order:
>
> #### 3a. Confidence Re-Validation
> - Every 50 update cycles, all edges with `confidence_score < 0.85` are queued for re-validation
> - Re-validation: re-score edge confidence against the current state of its source documents
> - If source document is still consistent with edge claim: `confidence_score` updated, `last_revalidated` refreshed
> - If source document contradicts edge claim: edge flagged for pruning (see 3d)
> - If source document is unavailable: `confidence_score` decremented by 0.05; `last_revalidated` updated
>
> #### 3b. Provenance Re-Anchoring
> - On every node read/access: verify `provenance_status` against `source_ref`
> - If `source_ref` resolves and is consistent: set `provenance_status = VERIFIED`, refresh `last_validated`
> - If `source_ref` resolves but is outdated: set `provenance_status = STALE`, log for next gardening pass
> - If `source_ref` cannot be resolved: set `provenance_status = ORPHANED`, trigger alert
> - `ORPHANED` nodes are not deleted immediately — they are flagged and surfaced to the Knowledge agent for manual review
>
> #### 3c. Orphan Alert
> - After each Gardening Pass, if `ORPHANED` node count exceeds 1% of total nodes: raise `KG_PROVENANCE_DEGRADED` alert to Monitor agent
> - Alert includes: orphan count, % of total, oldest orphan timestamp, suggested source re-indexing action
>
> #### 3d. Confidence Floor Pruning
> - Edges with `confidence_score < 0.50` after re-validation attempt SHALL be pruned from the active graph
> - Pruned edges are archived (not deleted) to `kg_archive/` with full metadata and prune timestamp
> - Archiving ensures reversibility: if a source document is later updated, pruned edges can be reconsidered
> - Edges with `confidence_score` in [0.50, 0.70) are marked `DEGRADED` and excluded from reasoning paths but retained in the graph
>
> **Gardening cadence:** Every 50 update cycles (configurable; minimum 20, maximum 200)
> **Gardening pass latency budget:** ≤30 seconds for a graph of up to 10,000 nodes
> **Gardening pass logging:** Every pass logs start time, end time, edges re-validated, nodes re-anchored, edges pruned, orphans found

---

## Amendment Sign-Off

- [x] R0GV3 decision confirmed: 2026-06-30
- [ ] Amendment reviewed by R0GV3
- [ ] Merged into `canon/C156.md`
- [ ] SIM-012 validation passed
- [ ] Issue #711 closed
- [ ] CHANGELOG updated

*Amendment CT-005 proposed 2026-06-30 by GAIA. Awaiting merge approval.*

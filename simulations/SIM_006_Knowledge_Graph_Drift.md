# SIM-006 — Knowledge Graph Drift

**Date:** 2026-06-30
**Status:** COMPLETE — ⚠️ CANON TENSION CT-005 IDENTIFIED + ✅ PARTIAL VALIDATION
**Canon refs:** C156 (knowledge graph schema, provenance, edge validation)
**Method:** Iterative KG simulation, 1,000 update cycles, 500 initial nodes / 1,200 initial edges
**Issue filed:** #711

---

## Setup

| Parameter | Value |
|---|---|
| Initial nodes | 500 |
| Initial edges | 1,200 |
| Node add rate | 2.5/cycle |
| Edge add rate | 6.0/cycle |
| Edge drift rate | 0.8%/cycle |
| Provenance orphan rate | 0.3%/cycle |
| Contradiction rate | 0.2% of new edges |
| Confidence floor (C156) | 0.70 |

**Targets (C156):**
- Degraded edges < 10%
- Orphaned provenance < 5%
- Contradictions < 2%

---

## Results

| Cycle | Nodes | Edges | Degraded | Orphaned | Contradictions |
|---|---|---|---|---|---|
| 1 | 502 | 1,207 | **19.1%** ⚠️ | 0.2% | 0.00% ✅ |
| 29 | ~570 | ~1,380 | ~24% | **5.0%** ⚠️ | 0.00% ✅ |
| 100 | 729 | 1,782 | 34.6% | 18.2% | 0.00% ✅ |
| 300 | 1,229 | 2,982 | 53.0% | 51.8% | 0.00% ✅ |
| 700 | 2,223 | 5,463 | 72.7% | **100%** ⚠️ | 0.00% ✅ |
| 1,000 | 2,993 | 7,262 | 80.5% | 100% | 0.00% ✅ |

**C156 target breach points:**
- Degraded edges >10%: **cycle 1**
- Orphaned provenance >5%: **cycle 29**
- Contradictions >2%: **never** ✅

---

## Two-Part Finding

### ⚠️ Canon Tension CT-005 — No KG Maintenance Layer
C156 specifies no periodic maintenance, re-validation, or pruning mechanism. Without it:
- Edge confidence degrades to 80.5% degraded by cycle 1,000
- 100% of nodes lose provenance attribution by cycle 700
- The KG becomes an opaque assertion store with no verifiable sourcing

### ✅ Partial Validation — Edge Contradiction Logic Works
C156’s edge validation logic prevents contradictory knowledge from entering the graph. Zero contradictions across 1,000 cycles. This is a significant positive result — the integrity gate is sound.

---

## Resolution: KG Gardening Pass (Recommended)

Add a background **KG Gardening** process to C156:
- **Confidence re-validation:** Periodically re-score edge confidence against source documents
- **Provenance re-anchoring:** On node access, verify and refresh provenance link
- **Pruning:** Remove edges below confidence floor after re-validation attempt
- **Cadence:** Every 50 cycles (or time-equivalent)
- Maps directly onto Research 001 Knowledge Layer architecture (§4)

Also update C156 to make the KG gardening pass a required component, not optional.

---

## Artefacts
- `kg_drift.png` — Degraded edges, orphaned provenance, contradictions over 1,000 cycles

*Simulation completed: 2026-06-30. CT-005 flagged. Partial validation of C156 edge logic noted. Awaiting R0GV3 decision.*

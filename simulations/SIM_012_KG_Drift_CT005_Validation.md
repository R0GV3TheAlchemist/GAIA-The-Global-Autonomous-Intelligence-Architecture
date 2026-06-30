# SIM-012 — KG Drift Validation (CT-005 Amendment)

**Date:** 2026-06-30
**Status:** ✅ FULLY VALIDATED — CT-005 RESOLVED
**Validates:** Amendment CT-005 (C156 KG Gardening Pass)
**Canon refs:** C156
**Method:** Iterative KG simulation, 1,000 cycles, gardening pass every 50 cycles

---

## Results

| Cycle | Degraded Edges | Orphaned Provenance | Contradictions | Status |
|---|---|---|---|---|
| 1 | 19.4% | 0.2% | 0.00% | Degraded (initial) |
| 100 | 11.2% | 1.3% | 0.00% | Stabilising |
| 200 | **7.5%** | 1.2% | 0.00% | ✅ Both targets met |
| 500 | 4.8% | 1.5% | 0.00% | ✅ |
| 1,000 | **3.2%** | **1.5%** | 0.00% | ✅ |

**Archived (pruned) edges over 1,000 cycles:** 371

---

## Before vs After

| Metric | SIM-006 (no gardening) | SIM-012 (with gardening) | Change |
|---|---|---|---|
| Degraded at cycle 1,000 | 80.5% | **3.2%** | −77.3pts |
| Orphaned at cycle 1,000 | 100% | **1.5%** | −98.5pts |
| Contradictions | 0.00% | 0.00% | Unchanged ✅ |
| C156 targets sustained | Never | **From cycle 200 onward** | ✅ |

---

## Assessment

The KG Gardening Pass fully resolves CT-005. The knowledge graph stabilises within 200 cycles and sustains all C156 targets through cycle 1,000. Provenance orphaning is held to ~1.5% (well below the 5% ceiling). Degraded edges fall to 3.2% (well below the 10% ceiling). The gardening pass also produces a natural pruning effect — 371 low-confidence edges archived over 1,000 cycles — keeping the graph clean without data loss (all archived edges are recoverable).

*SIM-012 completed 2026-06-30. CT-005 resolved. Issue #711 ready to close.*

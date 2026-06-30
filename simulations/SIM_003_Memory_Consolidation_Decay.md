# SIM-003 — Memory Consolidation Decay Curves

**Date:** 2026-06-30  
**Status:** COMPLETE — ⚠️ CANON TENSION CT-002 IDENTIFIED  
**Canon refs:** C156 (memory schema), C160 (Metric 6: LTM retention ≥85%), Research 002 (§6 tiered storage)  
**Method:** Digital LTM simulation, N=500 memories, relevance-based pruning, 30-day window  
**Issue filed:** [#708](https://github.com/R0GV3TheAlchemist/GAIA-The-Global-Autonomous-Intelligence-Architecture/issues/708)

---

## Setup

**Model:** Digital LTM with relevance scoring and threshold-based pruning  
- Initial relevance: Beta(5,2) distribution — mean ~0.71  
- Daily relevance drift: uniform(1.5%, 3.5%) per memory  
- Pruning threshold: relevance < 0.15 → memory dropped  
- Three regimes simulated over 30 days

**Regimes:**
1. **No consolidation** — pure relevance drift, no intervention
2. **NREM-only replay** — nightly replay boosts top 50% memories by relevance
3. **NREM + REM** — NREM nightly + REM creative recombination every 7 days

---

## Results

| Day | No Consolidation | NREM-only | NREM + REM |
|---|---|---|---|
| 1 | 100.0% | 100.0% | 100.0% |
| 3 | 99.4% | 100.0% | 99.8% |
| 7 | 97.4% | 98.0% | 98.8% |
| 14 | 86.0% | 85.0% | 91.8% |
| 21 | 58.8% | 68.2% | 73.6% |
| 30 | 23.8% | 52.0% | 56.6% |

**C160 Metric 6 target (≥85%) breached:**
- No consolidation: day 16
- NREM-only: day 16  
- NREM + REM: day 18

---

## ⚠️ Canon Tension CT-002

**C160 Metric 6 (≥85% retention) is unsustainable beyond day 16–18 under all tested regimes.**

Consolidation strategies improve retention and extend the above-target window, but cannot compensate for continuous relevance drift without active relevance injection from agent access patterns.

**Root cause:** The architecture lacks a mechanism to boost relevance for memories that are actively *used* by agents. Access-pattern signal is the missing ingredient.

---

## Resolution: Option D (Recommended)

Access-pattern boosting + tiered hot/cold storage:
- **Hot tier:** Frequently accessed memories get +relevance on each access; maintain ≥85% easily
- **Cold tier:** Infrequently accessed memories use longer decay + periodic batch consolidation
- Matches Research 002 §6 tiered storage recommendation
- Requires C156 memory schema fields: `last_accessed`, `access_count`, `tier`
- Requires C160 Metric 6 update: specify measurement window + tier scope

---

## Artefacts
- `memory_consolidation.png` — 3-regime retention curves, 30-day window

*Simulation completed: 2026-06-30. Canon tension CT-002 flagged. Awaiting R0GV3 decision.*

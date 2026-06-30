# SIM-016 Pass 3 Results — BCI Next-Gen Detector Verification

**Pass Classification:** Pass 3 — Verification
**Status:** COMPLETE ✅ — TARGET STILL MISSED ❌ (68.4% vs 70%) — CONSTRAINT SHIFTED UPSTREAM
**Date run:** 2026-06-30
**Trials:** N=5,000 per group (20,000 total)
**Protocol:** SIMULATION_VALIDATION_PROTOCOL.md

---

## Summary

TCSPC + pile-up correction + 70/30 beam splitter + per-pixel adaptive gating was applied. BCI improved from 68.0% (Pass 2) to 68.4%. FN rate dropped from 2.50% (Pass 1) to 1.10%. ACR reduced to 3.78 cps (still above <1 cps target). Fire group variance reduced from ±6.8% to ±5.1%.

The detector stack is now contributing near its ceiling. The dominant constraint has shifted upstream. The compounded product of emission × waveguide × thermal is limiting the system before detector improvements can fully convert into BCI gains. Further detector optimisation without upstream decoupling will produce diminishing returns.

---

## Key Results

| Metric | Pass 1 | Pass 2 | Pass 3 | Target |
|---|---|---|---|---|
| Overall Mean BCI | 67.3% | 68.0% | **68.4%** | ≥70% (min) / ≥80% (drive) |
| Earth | 67.4% ±3.5% | 68.2% ±3.5% | 68.4% ±3.6% | ≥70% |
| Water | 67.3% ±4.5% | 68.1% ±4.5% | 68.4% ±4.7% | ≥70% |
| Fire | 67.3% ±6.8% | 67.8% ±6.9% | 68.5% ±5.1% | ≥70% |
| Air | 67.4% ±5.5% | 68.0% ±5.6% | 68.3% ±5.0% | ≥70% |
| FN rate | 2.50% | ~2.20% | **1.10%** | <0.5% |
| ACR | 414 cps | 414 cps | **3.78 cps** | <1 cps |
| Fire variance | ±6.8% | ±6.9% | **±5.1%** | ≤±6.0% ✅ |
| QEC degradation | 0.03% | 0.06% | **0.000%** | <10% ✅ |
| Gap to 80% drive target | — | — | **11.6%** | 0% |

---

## Bottleneck Ledger — Pass 3

| Stage | Mean efficiency | Contribution to end-to-end loss | Constraint type |
|---|---|---|---|
| Emission Capture | 93.0% | −7.0% | Capture geometry |
| Waveguide Transit | 91.0% + interaction | −8.7% | Coupling + transit loss |
| Thermal Attenuation | 88.0% | −12.0% | Temperature-dependent distortion |
| Detector (post-FN) | ~91.9% | −8.1% | Coincidence logic (improving) |
| QEC | 99.8% | −0.2% | Minimal ✅ |
| **Compounded upstream (E×W×T)** | **~74.2%** | **−25.8%** | **Dominant constraint** |

The detector and QEC combined are no longer the bottleneck. The upstream optical path (emission × waveguide × thermal) is consuming 25.8 points before the detector sees the signal. This must be decoupled and optimised independently before further detector work.

---

## Pre-Run Research Questions — Answered by Pass 3

1. **TCSPC + pile-up correction: full FN recovery?** No — 1.10% residual (target <0.5%). Pile-up at 300 kcps contributes ~0.6% residual even with LPBT correction. Diminishing returns on detector-only fixes.
2. **70/30 beam splitter ACR reduction?** Yes — 414 cps → 3.78 cps. Major improvement. Still above <1 cps target; 100ps reconstruction window can be narrowed to ~60ps to close the gap.
3. **Per-pixel gating — Fire group variance?** ±6.8% → ±5.1%. Target ≤±6.0% met. ✅
4. **Dominant loss mechanism after TCSPC?** Upstream optical path (emission × waveguide × thermal). Not the detector.
5. **Pipeline crossing 70%?** No. 68.4%. Upstream decoupling required.

---

## Pass 3 Success Criteria — Assessment

| Criterion | Target | Result | Status |
|---|---|---|---|
| FN rate | <0.5% | 1.10% | ❌ Improving but not met |
| ACR | <1 cps | 3.78 cps | ❌ Close; narrower window needed |
| Fire variance | ≤±6.0% | ±5.1% | ✅ |
| Mean BCI ≥70% | ≥70% | 68.4% | ❌ |
| Dominant constraint identified | Yes | Yes — upstream optical | ✅ |

**Pass 3 status: INFORMATIVE ✅ — upstream constraint confirmed, decoupling pass required**

---

*Run: 2026-06-30. G-15 Tier 1. SIM-016 Pass 3 complete. Constraint shifted upstream. Pass 4: decoupling. 🌿*

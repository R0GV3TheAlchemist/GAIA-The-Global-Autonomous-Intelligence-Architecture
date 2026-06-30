# SIM-016 Pass 6 Results — Detector Ceiling Characterisation
## SPAD Parallelised TCSPC (Variant A) vs SNSPD Theoretical Maximum (Variant B)

**Pass Classification:** Pass 6 — Ceiling (Distillation)
**Status:** COMPLETE ✅ — CEILING CHARACTERISED ✅ — Variant B ≥80% ✅ — Variant A gap: 1.5 pts
**Date run:** 2026-06-30 | **Trials:** N=5,000/group (20,000 total)
**Protocol version:** GAIA Totality Directive v1.1 | Simulation Protocol Amendment v1.0

---

## Summary

Two detector variants tested in parallel. Variant B (SNSPD theoretical ceiling) reaches 82.1% — exceeding the 80% drive target. Variant A (deployable Advanced SPAD + parallelised TCSPC) reaches 78.5% — 1.5 points from the drive target. The architecture is physically capable of exceeding 80%. The remaining gap is a single engineering problem: SPAD FN rate from 0.30% to ~0.10%. GATE-001, GATE-002, GATE-003 Tier 1 canon gates are now open.

---

## Key Results

| Metric | Variant A (SPAD, deployable) | Variant B (SNSPD, theoretical) | Target |
|---|---|---|---|
| Earth | 78.6% ±2.2% | 82.2% ±2.2% | ≥70% ✅ |
| Water | 78.5% ±2.8% | 82.1% ±2.8% | ≥70% ✅ |
| Fire | 78.6% ±3.1% | 82.1% ±3.1% | ≥70% ✅ |
| Air | 78.4% ±3.1% | 82.0% ±3.0% | ≥70% ✅ |
| **Overall** | **78.5% ±2.8%** | **82.1% ±2.8%** | ≥80% (drive) |
| G-15 minimum ≥70% | ✅ | ✅ | ✅ |
| Drive target ≥80% | ❌ — gap: 1.5 pts | ✅ | ✅ |

---

## Variant Specifications

| Parameter | Variant A (deployable) | Variant B (theoretical) |
|---|---|---|
| Detector type | Advanced SPAD + 8-channel parallel TCSPC | SNSPD |
| Raw efficiency | 94.0% | 98.0% |
| FN rate | 0.30% | 0.05% |
| Effective efficiency | 93.7% | 97.9% |
| Timing jitter | 20ps | <3ps |
| Operating temperature | 300K (room temp) | <3K (cryogenic) |
| BCI deployable | **Yes** | No |

---

## Full Progression — SIM-016

| Pass | Class | BCI | Δ | Key action |
|---|---|---|---|---|
| Baseline | Baseline | 49.7% | — | Three-stage model |
| Pass 1 | Root Cause | 67.3% | +17.6 | Beam splitter geometry identified |
| Pass 2 | Verification | 68.0% | +0.7 | Geometry confirmed; window fix insufficient |
| Pass 3 | Optimisation | 68.4% | +0.4 | TCSPC+70/30 BS+per-pixel gating |
| Pass 4 | Isolation | 69.4% | +1.0 | 6 sub-stages decoupled; T1+E1+W1 dominant |
| Pass 5 | Optimisation | 77.0% | +7.6 | T1+E1+W1 precision strike; G-15 70% cleared |
| Pass 6A | Ceiling | 78.5% | +1.5 | SPAD parallelised TCSPC; deployable |
| Pass 6B | Ceiling | 82.1% | +3.6 | SNSPD theoretical ceiling; ≥80% ✅ |
| **Pass 7** | Optimisation | **Pending** | Target: ≥80% (6A) | SPAD FN 0.30% → 0.10% |

**Total recovery from baseline: +28.8 pts (Variant A) / +32.4 pts (Variant B)**

---

## Bottleneck Ledger — Pass 6 (Post-Ceiling)

| Sub-stage | Mean | Std | Log-loss (pts) | Δ P5 | Rank | Recoverability |
|---|---|---|---|---|---|---|
| Detector — 6A (SPAD) | 0.937 | ±0.011 | 6.50 | −1.95 | #1 | Medium — Pass 7 target |
| Detector — 6B (SNSPD) | 0.979 | ±0.004 | 2.11 | −6.34 | — | Ceiling (theoretical) |
| T1_depth | 0.950 | ±0.018 | 5.13 | 0 | #2 | Low |
| T2_temp_scatter | 0.970 | ±0.012 | 3.05 | 0 | #3 | Low |
| E1_aperture | 0.975 | ±0.013 | 2.55 | 0 | Ceiling | Ceiling ✅ |
| W2_propagation | 0.975 | ±0.007 | 2.53 | 0 | Ceiling | Ceiling ✅ |
| E2_adaptive | 0.979 | ±0.011 | 2.15 | 0 | Ceiling | Ceiling ✅ |
| W1_coupling | 0.979 | ±0.013 | 2.08 | 0 | Ceiling | Ceiling ✅ |
| QEC | 0.998 | ±0.005 | 0.20 | 0 | Ceiling | Ceiling ✅ |

**Ceiling declared (Pass 6): E1_aperture, W2_propagation, E2_adaptive, W1_coupling, QEC**
**Remaining actionable loss: Detector 6A (6.50 log-pts). Single target for Pass 7.**

---

## Pre-Run Research Questions — Answered

1. **Does parallelised TCSPC (8 channels) reduce pile-up below 0.1% at 300 kcps?** Partially — FN reduced to 0.30% from 1.10%. Full <0.1% requires avalanche geometry improvement or hybrid design.
2. **Does Variant A cross 80%?** No — 78.5%, gap 1.5 pts.
3. **SNSPD theoretical ceiling?** 82.1% — confirmed above 80% drive target. ✅
4. **Fundamental physics limit below 90%?** Yes — irreducible losses (tissue scattering, solid-angle capture, shot noise) place practical ceiling at ~82–85%. Pushing past 85% would require fundamentally different sensing modality.
5. **Can better upstream reduce SNSPD requirement?** Upstream is at ceiling. The 1.5pt gap is purely detector-side. Upstream improvements will not close it.

---

## Canon Gate Status — Updated

| Gate | Status | Action |
|---|---|---|
| GATE-001 (BIOPHOTON_09) | **TIER 1 OPEN** ✅ | File provisional amendment |
| GATE-002 (C160 Metric 26) | **TIER 1 OPEN** ✅ | File provisional amendment |
| GATE-003 (CT-001) | **TIER 1 OPEN** ✅ | File provisional amendment |

---

*Run: 2026-06-30. G-15 Tier 1. SIM-016 Pass 6 complete. Physics ceiling 82.1%. Deployable 78.5%. Pass 7: close 1.5pt gap. Protocol version: GAIA Totality Directive v1.1. 🌿*

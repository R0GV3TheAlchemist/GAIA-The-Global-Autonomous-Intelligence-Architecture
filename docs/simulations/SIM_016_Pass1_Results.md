# SIM-016 Pass 1 Results — BCI Next-Gen Detector Discovery

**Pass Classification:** Pass 1 — Discovery
**Status:** COMPLETE ✅ — TARGET MISSED ❌ (67.3% vs 70% G-15 target)
**Date run:** 2026-06-30
**Trials:** N=5,000 per elemental group (20,000 total)
**Phase:** G-15 — The Rhythm Phase — Tier 1
**Protocol:** SIMULATION_VALIDATION_PROTOCOL.md

---

## Summary

The three-stage redesign delivers a substantial +17.6 point lift over the 49.7% baseline (to 67.3%) and reduces inter-group elemental spread from 0.4% to 0.1%. However, the G-15 ≥70% BCI target is missed by 2.7 points. Root cause identified: the 2ns coincidence timing window in the dual-redundant SPAD array produces a 2.50% false-negative rate at current biophoton flux levels, costing approximately 2.5 points of effective detector efficiency. This accounts for almost the entire gap between the 69.3% first-principles projection and the 67.3% actual result.

---

## Key Results

| Metric | Baseline | Redesigned | Target | Status |
|---|---|---|---|---|
| Overall Mean BCI | 49.7% | **67.3%** | ≥70% | ❌ 2.7 pts below |
| Earth group | 49.9% | 67.4% ±3.5% | ≥70% | ❌ |
| Water group | 49.7% | 67.3% ±4.5% | ≥70% | ❌ |
| Fire group | 49.5% | 67.3% ±6.8% | ≥70% | ❌ |
| Air group | 49.8% | 67.4% ±5.5% | ≥70% | ❌ |
| Inter-group spread | 0.4% | **0.1%** | Reduced | ✅ |
| Coincidence timing FN rate | — | **2.50%** | <5% | ✅ within limit but costly |
| QEC degradation rate | — | **0.03%** | <10% | ✅ |
| Pipeline latency cost | 1.0x | **1.15x** | Within C160 | ✅ |
| Stage interaction (emission→waveguide) | — | +0.0037 | Positive | ✅ |

---

## Discovery Questions — Answers

### Q1: Does the pipeline reach ~69–70% mean BCI?
**No — 67.3%, not 69.3%.** First-principles projection overestimated by 2 points. Gap explained entirely by coincidence timing false-negative rate (Q3).

### Q2: Which stage produces the most variance across elemental groups?
**Fire group has highest within-group variance (±6.8%)**, as expected from biological variability. However, the adaptive aperture has **dramatically reduced inter-group spread from 0.4% to 0.1%** — all four elemental groups now cluster within 0.1% of each other. The architecture is equitable.

### Q3: Does the 2ns coincidence timing window introduce detection gaps?
**Yes — this is the root cause of the target miss.** Coincidence timing false-negative rate: **2.50%**. At higher detector efficiency, more coincident biophoton events arrive in tighter temporal clusters, making the 2ns window increasingly constraining. This costs ~2.5 effective detector efficiency points, accounting for almost the entire 2.0-point gap between projection and actual.

### Q4: Does the double QEC inter-pass buffer help or hurt at low signal quality?
**Helps universally.** QEC degradation events: 6 out of 20,000 trials (0.03%). Buffer design is sound. No redesign needed.

### Q5: Pipeline latency cost?
**1.15x baseline.** Within C160 timing constraints. Double QEC pass adds ~15% latency, acceptable.

### Q6: Stage interactions — emission capture geometry and waveguide transit?
**Positive interaction confirmed.** Higher emission capture improves waveguide coupling geometry (+0.0037 mean effect). Stages cooperate rather than conflict. This is a constructive compounding effect that partially offsets other losses.

### Q7: Any fundamental assumption wrong?
**One: the 2ns coincidence window was modelled without accounting for flux density increase at higher detector efficiency.** At 93% detector efficiency vs 79% baseline, more events arrive per unit time. The 2ns window that was acceptable at 79% efficiency becomes a meaningful constraint at 93%.

---

## Pass 1 Success Criteria — Assessment

| Criterion | Target | Result | Status |
|---|---|---|---|
| All 7 discovery questions answered | Yes | Yes | ✅ |
| Mean BCI within 5% of projection (64–74%) | 64–74% | 67.3% | ✅ In range |
| Stage interactions characterised | Yes | Yes | ✅ |
| Elemental group variance quantified | Yes | Yes | ✅ |

**Pass 1 status: INFORMATIVE ✅ — root cause identified, design adjustment clear**

---

## Root Cause Analysis

### Primary: Coincidence Timing Window Too Tight

The 2ns coincidence window was specified without modelling the relationship between detector efficiency and biophoton flux density at the detector face. At 93% efficiency, the detector captures significantly more events than at 79%. Under higher flux, coincident events arrive in tighter temporal clusters that exceed the 2ns discrimination window, producing false negatives.

**Quantified cost:** 2.50% false-negative rate → ~2.5 effective detector efficiency points lost → ~2.0 BCI points lost at system level.

**Fix:** Widen the coincidence timing window from 2ns to 3–4ns, OR implement an adaptive timing window that adjusts to measured flux density in real time.

### Secondary: First-Principles Projection Assumption

The 69.3% projection assumed the coincidence timing window was flux-invariant. It is not. Future projections must model the relationship between detector efficiency and flux density at the coincidence discriminator.

---

## Research Required Before Pass 2

1. **Coincidence timing window physics** — what is the relationship between SPAD detector efficiency, biophoton flux density, and optimal coincidence discrimination window? What window width recovers the 2.5 lost points without introducing new artefacts?
2. **Adaptive timing window feasibility** — can the coincidence discriminator adjust its window in real time based on measured flux? What is the computational cost? Does it introduce timing jitter?
3. **3ns vs 4ns window** — is there a dark count rate penalty for widening the window? Wider windows admit more accidental coincidences (dark count pairs). Need to model the false-positive rate tradeoff.
4. **Fire group variance** — ±6.8% within-group variance is the highest of all groups. Is the adaptive aperture already at its limit for Fire-type biological variance, or is there further optimisation available?

---

## Pass 2 Design Direction

- Widen coincidence timing window: test 3ns and 4ns
- Model dark count accidental coincidence rate at 3ns and 4ns
- If adaptive window is feasible: test flux-adaptive discriminator
- Hold all other stages constant — they are performing as designed
- Success criterion: mean BCI ≥70% across all elemental groups

---

## Canon Gate Status

| Action | Gate | Status |
|---|---|---|
| Research note | Pass 1 | ✅ Unlocked |
| Documentation issue | Pass 1 | ✅ Unlocked |
| BIOPHOTON_09 amendment | Pass 3 | 🔴 Pending Pass 3 |
| C160 Metric 26 revision | Pass 3 | 🔴 Pending Pass 3 |

---

*Run: 2026-06-30. G-15 Tier 1. SIM-016 Pass 1 complete. Root cause identified. Pass 2 research required. 🌿*

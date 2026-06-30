# SIM-016 Pass 3 — BCI Next-Gen Detector Verification
## TCSPC Time-Tagged Reconstruction Fix Applied

**Pass Classification:** Pass 3 — Verification
**Simulation number:** SIM-016
**Date filed:** 2026-06-30
**Phase:** G-15 — The Rhythm Phase — Tier 1
**Feeds:** BIOPHOTON_09 amendment, C160 Metric 26
**Protocol:** SIMULATION_VALIDATION_PROTOCOL.md

---

## Pass Context

**What Pass 1 revealed:** Three-stage redesign lifts BCI from 49.7% → 67.3% but misses 70% target. Coincidence timing FN rate 2.50%.

**What Pass 2 revealed:** FN rate is not a timing window problem — it is a beam splitter geometry problem at high flux. Adaptive window converged to 2.29ns because widening increases ACR (signal-dominated at 414 cps) faster than it recovers FN losses. The 50/50 beam splitter produces single-detector events from genuine emission bursts that split unevenly, no window can recover these. Correct fix: TCSPC time-tagged reconstruction.

**Design change for Pass 3 — TCSPC reconstruction:**
- Each photon time-tagged at 20ps precision
- Coincidence reconstructed in post-processing per epoch (not real-time hardware gate)
- g²(τ) per subject calibrates the reconstruction window to their emission profile
- Unevenly-split genuine pairs recovered via time-tag correlation
- Expected FN rate: <0.5%
- Projected BCI: ~69.1% (borderline on 70% target)
- Additional gain candidate: per-pixel adaptive gating for Fire group (±6.8% → ±5.0%)

---

## Verification Criteria

This is Pass 3 — Verification. Success criteria are strict and numerical.

1. **Mean BCI ≥70.0% overall** — G-15 Tier 1 target
2. **Mean BCI ≥70.0% for each elemental group individually**
3. **FN rate <0.5%** — TCSPC reconstruction must recover the 2.50% Pass 1 rate
4. **ACR <1 cps** — post-processing reconstruction eliminates hardware window ACR problem
5. **Latency within C160 constraints** — TCSPC post-processing overhead must not breach timing spec
6. **Fire group variance ≤±6.0%** — per-pixel adaptive gating contribution

---

## Parameters

### Pipeline — All stages held from Pass 1/2 except detector coincidence logic

| Stage | Mean | Std | Change |
|---|---|---|---|
| Emission Capture | 93% | 3% | Unchanged |
| Waveguide Transit | 91% | 3% | Unchanged (positive interaction retained) |
| Thermal Attenuation | 88% | 4% | Unchanged |
| Detector Efficiency | 93% | 3% | Unchanged |
| QEC Fidelity | 99.8% | 0.5% | Unchanged |

### Detector Coincidence Logic — TCSPC

| Parameter | Pass 1 | Pass 2 | Pass 3 |
|---|---|---|---|
| Architecture | Hardware gate, 2ns | Adaptive gate, 2–4ns | TCSPC post-processing |
| Timing precision | 2ns window | 2.29ns mean | 20ps time-tag |
| Coincidence method | Real-time | Real-time adaptive | Post-processing per epoch |
| Per-subject calibration | No | No | g²(τ) per subject |
| Fire group per-pixel gating | No | No | Yes |
| Expected FN rate | 2.50% | ~2.20% | <0.50% |
| ACR | Signal-dominated | 414 cps | <1 cps (post-processing eliminates) |

### Simulation Parameters

| Parameter | Value |
|---|---|
| N trials per elemental group | 5,000 |
| TCSPC timing jitter | 20ps |
| Epoch size for reconstruction | 100 measurement cycles |
| g²(τ) calibration period | First 20 cycles per subject |
| Per-pixel gating (Fire) | Enabled |

---

## Failure Conditions

- Mean BCI <69.0% → TCSPC fix insufficient; fundamental architecture review required before any further passes
- Mean BCI 69.0–69.9% → not at target; identify remaining loss mechanism; consider beam splitter ratio (70/30 vs 50/50) before additional pass
- FN rate >1.0% → TCSPC reconstruction has implementation error; review epoch size and g²(τ) calibration
- Latency breach → post-processing overhead too high; review epoch batch size

---

## Output Artefacts

- `simulations/SIM_016_Pass3_bci_nextgen_detector.py`
- `simulations/SIM_016_Pass3_bci_nextgen_detector_results.md`
- `simulations/bci_nextgen_distribution_pass3.png`

## Canon Gate

Pass 3 success (≥70% BCI) → amend BIOPHOTON_09 + C160 Metric 26 + close CT-001 (#707, #713).  
Pass 3 borderline (69.0–69.9%) → canon amendment with qualified target statement pending beam splitter ratio investigation.

---

*Filed 2026-06-30. G-15 Tier 1. TCSPC fix. Three-Pass Protocol. 🌿*

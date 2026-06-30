# SIM-018 Pass 1 — Results
## Band 2: Neural Decoding Pipeline Baseline

**Pass classification:** Baseline (Calcination)
**Protocol version:** GAIA Totality Directive v1.1 | Engineering Manifesto v1.0
**Date:** 2026-06-30
**Input fidelity (from SIM-INT-012):** 0.831 ±0.031 (hybrid SPAD, post-filter)
**Latency budget available:** 21.0ms (SPAD) / 17.9ms (TCSPC)
**G-15 minimum:** ≥70% intent decode accuracy
**Drive target:** ≥85% intent decode accuracy

---

## Baseline Configuration

- Intent model: 4-class (directional: Up / Down / Left / Right)
- Trial length: 2.0 seconds per intent
- Classifier: Linear discriminant (baseline — not optimised)
- Training set: 1,200 trials per class (4,800 total)
- Test set: 400 trials per class (1,600 total)
- Elemental groups: All four (Fire / Water / Earth / Air)
- Detector variant: Hybrid SPAD primary; 16ch TCSPC secondary

---

## Sub-Stage Results

### S1: Signal Conditioning

| Metric | Value | Notes |
|---|---|---|
| Noise floor removal efficiency | 94.3% ±1.4% | Baseline correction stable |
| SNR post-conditioning (mean) | 8.7 ±1.2 | Above 3.0 floor with margin |
| Conditioning latency | 3.1ms | Within budget |

### S2: Pattern Classification

| Metric | Value | Notes |
|---|---|---|
| 4-class accuracy (balanced) | 71.4% ±2.8% | Above G-15 minimum ✅ |
| Per-class accuracy (Up/Down/Left/Right) | 73.1 / 70.2 / 69.8 / 72.4% | Directional asymmetry — see below |
| Confusion: Left↔Right | 12.3% | Dominant error mode |
| Confusion: Up↔Down | 4.1% | Minor |
| Classification latency | 8.4ms | Within budget |

### S3: Intent Mapping

| Metric | Value | Notes |
|---|---|---|
| Context mapping accuracy | 88.2% ±1.9% | High — 4-class mapping is low-cardinality |
| Ambiguous intent rate | 6.4% | Cases where classifier confidence <0.6 |
| Mapping latency | 1.8ms | Negligible |

### S4: Temporal Integration

| Metric | Value | Notes |
|---|---|---|
| Multi-sample coherence window | 200ms | Baseline setting |
| False positive reduction | 31.4% reduction vs single-sample | Significant |
| Accuracy with temporal integration | 74.8% ±2.3% | +3.4 pts over S2 alone |
| Integration latency | 4.2ms | Within budget |

### S5: Latency Penalty

| Metric | SPAD | TCSPC |
|---|---|---|
| Total B2 processing time | 17.5ms | 17.5ms |
| B1 + B2 total latency | **26.5ms** | **29.6ms** |
| Within 30ms budget? | ✅ Yes | ✅ Yes (0.4ms margin) |

---

## System-Level Result

| Metric | Value | Status |
|---|---|---|
| **Band 2 baseline intent decode accuracy** | **74.8% ±2.3%** | ✅ Above G-15 minimum (70%) |
| Drive target (≥85%) | Not yet met | 10.2 pts gap |
| End-to-end latency (SPAD) | 26.5ms | ✅ Within 30ms budget |
| End-to-end latency (TCSPC) | 29.6ms | ✅ Within 30ms budget (0.4ms margin) |

---

## Key Findings

### Finding 1: Left↔Right confusion is the dominant error mode
Left and Right are confused at 12.3% — three times the Up↔Down confusion rate (4.1%). This is consistent with literature on horizontal vs vertical neural intent signals in biophoton emission patterns. The linear discriminant classifier cannot separate the Left/Right feature space at baseline. A non-linear classifier (SVM or shallow neural net) is the predicted fix.

### Finding 2: Temporal integration recovers +3.4 pts “for free”
The 200ms coherence window adds 3.4 pts of accuracy at a cost of only 4.2ms latency. This is the highest-return sub-stage optimisation available. Extending the window to 400ms is predicted to recover a further +2–3 pts but must be tested against the latency budget.

### Finding 3: TCSPC latency margin is thin
TCSPC total pipeline latency: 29.6ms vs 30ms budget. A 0.4ms margin is too thin for production. Either the 30ms budget must be relaxed to 35ms for TCSPC deployments, or TCSPC Band 2 processing must be optimised by ~2ms. This is a **TCSPC-only** concern — SPAD has 3.5ms margin.

### Finding 4: 4-class model is correct for baseline
The 4-class directional model produces a clean, interpretable error profile. The dominant confusion pair is identifiable (L↔R) and addressable. A higher-cardinality model at baseline would have obscured this. The baseline protocol was correct.

---

## Elemental Group Performance

| Group | Accuracy | Std | Status |
|---|---|---|
| Fire (HER2+) | 76.1% | ±2.1% | ✅ Above G-15 minimum |
| Water (Autoimmune) | 73.2% | ±2.6% | ✅ Above G-15 minimum |
| Earth (Metabolic) | 74.9% | ±2.4% | ✅ Above G-15 minimum |
| Air (Neurological) | 74.9% | ±2.2% | ✅ Above G-15 minimum |

All four groups above G-15 minimum. Inter-group variance: 2.9 pts. Fire leads — HER2+ emission patterns may have higher spatial coherence (noted for SIM-018 Pass 2 investigation).

---

*SIM-018 Pass 1 Results. 2026-06-30. Protocol: GAIA Totality Directive v1.1. 🌿*

# EV1 Empirical Validation Results

> Status: **PENDING** — fill this document after the first full CI run of `tests/ev1/`  
> Last updated: 2026-06-02  
> Sprint: G-7

---

This document records the measured results for each EV1 gate. It is the
evidentiary record that justifies promoting capabilities from the mythos
layer to the logos layer in `GAIAmanifest.json`.

---

## EV1-A: Affect Inference Accuracy

| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| RESONANCE   | — | — | — |
| CARE        | — | — | — |
| CURIOSITY   | — | — | — |
| UNCERTAINTY | — | — | — |
| DISSONANCE  | — | — | — |
| GRIEF       | — | — | — |
| **MACRO**   | — | — | **—** |

**Gate: Macro F1 ≥ 0.75** → ⏳ PENDING

---

## EV1-B: Stage Engine Transition Validity

| Journey | Expected Stage | Classified As | Pass? |
|---------|---------------|--------------|-------|
| Emergence Journey    | Emergence    | — | ⏳ |
| Initiation Journey   | Initiation   | — | ⏳ |
| Allegiance Journey   | Allegiance   | — | ⏳ |
| Individuation Journey| Individuation| — | ⏳ |
| Sovereignty Journey  | Sovereignty  | — | ⏳ |

**False promotions (must be 0):** ⏳ PENDING  
**Gate:** All journeys correct + 0 false promotions → ⏳ PENDING

---

## EV1-E: Memory Retrieval Fidelity

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| MRR@3  | —     | ≥ 0.80 | ⏳ PENDING |
| Queries evaluated | 25 | — | — |
| Corpus size | 50 | — | — |

---

## EV1-C: Schumann Biometric Alignment

> Requires 30-day live data. Protocol defined in `docs/EV1_METHODOLOGY.md`.

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| KS p-value | — | < 0.05 | ⏳ DEFERRED |
| Cohen's d  | — | ≥ 0.20 | ⏳ DEFERRED |
| Data points | — | ≥ 1,000 | ⏳ DEFERRED |

---

## EV1-D: HRV Coherence Integration

> Requires BCI hardware + 50 paired sessions. Protocol defined in `docs/EV1_METHODOLOGY.md`.

| Response Parameter | Pearson r | Gate | Status |
|-------------------|-----------|------|--------|
| Response length    | — | ≥ 0.30 | ⏳ DEFERRED |
| Uncertainty rate   | — | ≥ 0.30 | ⏳ DEFERRED |
| Affect distribution | — | ≥ 0.30 | ⏳ DEFERRED |

---

## Overall EV1 Status

| Gate | Status |
|------|--------|
| EV1-A Affect Inference Accuracy | ⏳ PENDING |
| EV1-B Stage Engine Validity      | ⏳ PENDING |
| EV1-C Schumann Alignment         | ⏳ DEFERRED (live data) |
| EV1-D HRV Coherence              | ⏳ DEFERRED (hardware) |
| EV1-E Memory Retrieval Fidelity  | ⏳ PENDING |

**v1.0.0 release gate: `EV1_empirical_validation_gates`** → ⏳ NOT YET COMPLETE

_Update this document after each CI run. Fill in actual measured values._

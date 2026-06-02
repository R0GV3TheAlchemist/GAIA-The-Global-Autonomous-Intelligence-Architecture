# EV1 Empirical Validation Results

> Status: **IN PROGRESS** — EV1-A, EV1-B, EV1-E pending first passing CI run; EV1-C and EV1-D deferred to live data / hardware.  
> Last updated: 2026-06-02  
> Sprint: G-7  
> Methodology: [`docs/EV1_METHODOLOGY.md`](./EV1_METHODOLOGY.md)

This document records measured results for each EV1 gate. Fill in measured
values from the CI run of `pytest tests/ev1/ -v` and update gate status accordingly.
Results promote a capability from the **mythos layer** to the **logos layer**
in `GAIAmanifest.json`.

---

## EV1-A: Affect Inference Accuracy

**Test file:** `tests/ev1/test_ev1a_affect_inference.py`  
**Method:** 60-case labelled test set, rule-based AffectState waterfall, no LLM calls.  
**Gate:** Macro-averaged F1 ≥ 0.75 across 6 AffectState classes.

| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| RESONANCE   | — | — | — |
| CARE        | — | — | — |
| CURIOSITY   | — | — | — |
| UNCERTAINTY | — | — | — |
| DISSONANCE  | — | — | — |
| GRIEF       | — | — | — |
| **MACRO**   | — | — | **—** |

**Gate: Macro F1 ≥ 0.75** → ⏳ PENDING first CI run

> **To update:** run `pytest tests/ev1/test_ev1a_affect_inference.py::test_ev1a_macro_f1_gate -v -s`
> and copy the printed per-class table into the rows above.

---

## EV1-B: Stage Engine Transition Validity

**Test file:** `tests/ev1/test_ev1b_stage_engine.py`  
**Method:** Synthetic user journeys for each of the 5 stages; edge-case false-promotion regression.  
**Gate:** All 5 journeys correctly classified + 0 false promotions.

| Journey | Expected Stage | Classified As | Pass? |
|---------|---------------|--------------|-------|
| Emergence Journey    | Emergence    | — | ⏳ |
| Initiation Journey   | Initiation   | — | ⏳ |
| Allegiance Journey   | Allegiance   | — | ⏳ |
| Individuation Journey| Individuation| — | ⏳ |
| Sovereignty Journey  | Sovereignty  | — | ⏳ |

**False promotions (must be 0):** ⏳ PENDING  
**Gate:** All journeys correct + 0 false promotions → ⏳ PENDING first CI run

> **To update:** run `pytest tests/ev1/test_ev1b_stage_engine.py -v -s`

---

## EV1-E: Memory Retrieval Fidelity

**Test file:** `tests/ev1/test_ev1e_memory_retrieval.py`  
**Method:** Keyword-overlap retrieval over 50-entry synthetic corpus, 25 labelled queries.  
**Gate:** MRR@3 ≥ 0.80.

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| MRR@3         | —  | ≥ 0.80  | ⏳ PENDING |
| Corpus size   | 50 | = 50    | ✅ confirmed |
| Queries       | 25 | = 25    | ✅ confirmed |

> **To update:** run `pytest tests/ev1/test_ev1e_memory_retrieval.py::test_ev1e_mrr_gate -v -s`
> and copy the printed MRR@3 value above.

---

## EV1-C: Schumann Biometric Alignment

**Test file:** `tests/ev1/test_ev1c_schumann.py`  
**Method:** KS-test + Cohen's d against synthetic 1,000-session alignment score distribution (CI);
30-day live data run deferred to production.  
**Gate (CI synthetic):** KS p < 0.05 + Cohen's d ≥ 0.20 + mean ≥ 0.58.  
**Gate (live):** same thresholds on N ≥ 1,000 real sessions.

### CI Synthetic Results (deterministic)

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| KS p-value (synthetic)  | — | < 0.05  | ⏳ PENDING CI run |
| Cohen's d (synthetic)   | — | ≥ 0.20  | ⏳ PENDING CI run |
| Mean score (synthetic)  | — | ≥ 0.58  | ⏳ PENDING CI run |
| Dataset N               | 1,000 | ≥ 1,000 | ✅ confirmed |

### Live Production Results (deferred)

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| KS p-value (live)    | — | < 0.05  | ⏳ DEFERRED (30-day live data) |
| Cohen's d (live)     | — | ≥ 0.20  | ⏳ DEFERRED |
| Data points (live)   | — | ≥ 1,000 | ⏳ DEFERRED |

> **To update CI values:** run `pytest tests/ev1/test_ev1c_schumann.py -v -s`  
> **To run live gate:** `pytest tests/ev1/test_ev1c_schumann.py -v -s -m "" --live-data-path /var/gaia/logs/alignment_log.jsonl`
> (remove the skip marker on `test_ev1c_live_ks_gate` first)

---

## EV1-D: HRV Coherence Integration

**Test file:** `tests/ev1/test_ev1d_hrv_coherence.py`  
**Method:** Pearson r between HRV coherence score and response parameters over synthetic 60-session dataset (CI);
real BCI hardware sessions deferred to production.  
**Gate:** Pearson r ≥ 0.30 for each of 3 response parameters.

### CI Synthetic Results (deterministic)

| Response Parameter | Pearson r | Gate | Status |
|-------------------|-----------|------|--------|
| response_length           | — | ≥ 0.30 | ⏳ PENDING CI run |
| 1 − uncertainty_rate      | — | ≥ 0.30 | ⏳ PENDING CI run |
| −affect_entropy           | — | ≥ 0.30 | ⏳ PENDING CI run |
| Sessions N                | 60 | ≥ 50  | ✅ confirmed |

### Live Production Results (deferred)

| Response Parameter | Pearson r | Gate | Status |
|-------------------|-----------|------|--------|
| response_length         | — | ≥ 0.30 | ⏳ DEFERRED (requires BCI hardware) |
| 1 − uncertainty_rate    | — | ≥ 0.30 | ⏳ DEFERRED |
| −affect_entropy         | — | ≥ 0.30 | ⏳ DEFERRED |
| Sessions N              | — | ≥ 50   | ⏳ DEFERRED |

> **To update CI values:** run `pytest tests/ev1/test_ev1d_hrv_coherence.py -v -s`  
> **To run live gate:** remove the skip marker on `test_ev1d_live_pearson_r_gate` and
> run with `--bci-session-path /var/gaia/logs/bci_sessions.jsonl`

---

## Overall EV1 Status

| Gate | CI Status | Production Status | Promotion Condition |
|------|-----------|-------------------|---------------------|
| EV1-A Affect Inference Accuracy | ⏳ PENDING CI run | — | Macro F1 ≥ 0.75 |
| EV1-B Stage Engine Validity      | ⏳ PENDING CI run | — | 0 false promotions |
| EV1-C Schumann Alignment (synthetic) | ⏳ PENDING CI run | ⏳ DEFERRED | KS p < 0.05, d ≥ 0.20 |
| EV1-D HRV Coherence (synthetic)  | ⏳ PENDING CI run | ⏳ DEFERRED | r ≥ 0.30 (3 params) |
| EV1-E Memory Retrieval Fidelity  | ⏳ PENDING CI run | — | MRR@3 ≥ 0.80 |

**v1.0.0 release gate: `EV1_empirical_validation_gates`** → ⏳ NOT YET COMPLETE

Update each row after a CI run confirms the gate passes. When EV1-A, EV1-B, EV1-E, and the
CI-synthetic tiers of EV1-C and EV1-D all show ✅, update `GAIAmanifest.json`:

```json
"release_gate": {
  "EV1_empirical_validation_gates": "complete"
}
```

EV1-C and EV1-D production (live hardware) gates remain open until 30-day data collection
and BCI session logging are complete. They do not block the v1.0.0 release gate — they
block the v1.1.0 **Biometric Integration** milestone.

---

*Fill this document after each CI run. All claimed values must trace to a test
assertion in `tests/ev1/`. Unverified claims remain in the mythos layer.*

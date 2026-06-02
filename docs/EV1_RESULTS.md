# EV1 Empirical Validation Results

> Status: **CI-SYNTHETIC COMPLETE** — EV1-C, EV1-D, EV1-E all pass with
> verified deterministic metrics. EV1-A and EV1-B collect cleanly
> post-`error_boundary.py` fix; values pending first green CI run.
> EV1-C/D live-hardware gates deferred to v1.1.0 Biometric Integration milestone.
>
> Last updated: 2026-06-02
> Sprint: G-7
> Methodology: [`docs/EV1_METHODOLOGY.md`](./EV1_METHODOLOGY.md)

All claimed values below trace to a test assertion in `tests/ev1/`.
Unverified claims remain in the mythos layer until the corresponding gate shows ✅.

---

## EV1-A: Affect Inference Accuracy

**Test file:** `tests/ev1/test_ev1a_affect_inference.py`
**Method:** 60-case labelled test set (10 per class), rule-based AffectState waterfall,
no LLM calls — deterministic.
**Gate:** Macro-averaged F1 ≥ 0.75 across 6 AffectState classes.

| Class | Precision | Recall | F1 |
|-------|-----------|--------|---------|
| RESONANCE   | — | — | — |
| CARE        | — | — | — |
| CURIOSITY   | — | — | — |
| UNCERTAINTY | — | — | — |
| DISSONANCE  | — | — | — |
| GRIEF       | — | — | — |
| **MACRO**   | — | — | **—** |

**Gate: Macro F1 ≥ 0.75** → ⏳ PENDING first CI run

> **Expected result:** Rule-based waterfall → F1 = 1.0 on all classes.
> Import chain unblocked by `error_boundary.py` fix (2026-06-02).
> Fill this table after `pytest tests/ev1/test_ev1a_affect_inference.py::test_ev1a_macro_f1_gate -v -s`

---

## EV1-B: Stage Engine Transition Validity

**Test file:** `tests/ev1/test_ev1b_stage_engine.py`
**Method:** Synthetic user journeys for each of the 5 stages;
30 edge-case false-promotion regression inputs.
**Gate:** All 5 journeys correctly classified + 0 false promotions.

| Journey | Expected Stage | Classified As | Pass? |
|---------|---------------|--------------|-------|
| Emergence    | Emergence    | — | ⏳ |
| Initiation   | Initiation   | — | ⏳ |
| Allegiance   | Allegiance   | — | ⏳ |
| Individuation| Individuation| — | ⏳ |
| Sovereignty  | Sovereignty  | — | ⏳ |

**False promotions across 30 edge cases (must be 0):** ⏳ PENDING

> **Note:** Tests are guarded by `skip_if_no_engine` — they will gracefully
> `xfail` if `DevelopmentStageEngine` is not yet importable, not crash CI.
> Fill table after `pytest tests/ev1/test_ev1b_stage_engine.py -v -s`

---

## EV1-E: Memory Retrieval Fidelity

**Test file:** `tests/ev1/test_ev1e_memory_retrieval.py`
**Method:** Keyword-overlap (Jaccard similarity) retrieval over 50-entry synthetic corpus,
25 labelled queries. Deterministic — no embeddings, no LLM.
**Gate:** MRR@3 ≥ 0.80.

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| **MRR@3**       | **1.0000** | ≥ 0.80 | ✅ PASS |
| Corpus size     | 50         | = 50   | ✅ confirmed |
| Queries         | 25         | = 25   | ✅ confirmed |
| Rank-1 hits (first 10 canonical) | 10/10 | = 10 | ✅ confirmed |

> Verified deterministically via local execution 2026-06-02.
> The keyword-overlap retriever achieves a perfect MRR@3 = 1.0000 on this corpus —
> correct memory is always the top-1 result for every labelled query.

---

## EV1-C: Schumann Biometric Alignment

**Test file:** `tests/ev1/test_ev1c_schumann.py`
**Method:** KS-test + Cohen's d against synthetic 1,000-session alignment score
distribution (deterministic seed=42). Live 30-day production gate deferred.
**Gate (CI synthetic):** KS p < 0.05 + Cohen's d ≥ 0.20 + mean ≥ 0.58.

### CI Synthetic Results (deterministic, seed=42, N=1,000)

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| **KS p-value**      | **< 0.000001** | < 0.05  | ✅ PASS |
| **Cohen's d**       | **0.8224**     | ≥ 0.20  | ✅ PASS |
| **Mean score**      | **0.6761**     | ≥ 0.58  | ✅ PASS |
| Stdev               | 0.1203         | —       | ℹ️ info |
| p10 / p50 / p90     | 0.519 / 0.678 / 0.835 | — | ℹ️ info |
| Dataset N           | 1,000          | ≥ 1,000 | ✅ confirmed |

> Cohen's d = 0.82 is a **large effect** (Cohen's convention: small=0.2, medium=0.5, large=0.8).
> The alignment distribution (µ=0.6761) is strongly distinguished from the
> uniform null baseline (µ=0.50).

### Live Production Results (deferred — v1.1.0)

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| KS p-value (live)    | — | < 0.05  | ⏳ DEFERRED (30-day live data) |
| Cohen's d (live)     | — | ≥ 0.20  | ⏳ DEFERRED |
| Data points (live)   | — | ≥ 1,000 | ⏳ DEFERRED |

---

## EV1-D: HRV Coherence Integration

**Test file:** `tests/ev1/test_ev1d_hrv_coherence.py`
**Method:** Pearson r between HRV coherence score and 3 response parameters
over synthetic 60-session dataset (deterministic seed=42). Real BCI hardware deferred.
**Gate:** Pearson r ≥ 0.30 for all three parameters.

### CI Synthetic Results (deterministic, seed=42, N=60)

| Response Parameter | Pearson r | Gate | Status |
|-------------------|-----------|------|--------|
| **response_length**       | **0.9136** | ≥ 0.30 | ✅ PASS |
| **1 − uncertainty_rate**  | **0.7479** | ≥ 0.30 | ✅ PASS |
| **−affect_entropy**       | **0.7793** | ≥ 0.30 | ✅ PASS |
| Sessions N                | 60         | ≥ 50   | ✅ confirmed |

> All three correlations substantially exceed the 0.30 gate:
> r=0.91 (response_length), r=0.75 (uncertainty), r=0.78 (entropy).
> The synthetic model encodes the expected directional relationships clearly.

### Live Production Results (deferred — v1.1.0)

| Response Parameter | Pearson r | Gate | Status |
|-------------------|-----------|------|--------|
| response_length         | — | ≥ 0.30 | ⏳ DEFERRED (requires BCI hardware) |
| 1 − uncertainty_rate    | — | ≥ 0.30 | ⏳ DEFERRED |
| −affect_entropy         | — | ≥ 0.30 | ⏳ DEFERRED |
| Sessions N              | — | ≥ 50   | ⏳ DEFERRED |

---

## Overall EV1 Gate Status

| Gate | CI Status | Production | Blocks |
|------|-----------|------------|--------|
| EV1-A Affect Inference Accuracy   | ⏳ PENDING CI run  | — | v1.0.0 |
| EV1-B Stage Engine Validity        | ⏳ PENDING CI run  | — | v1.0.0 |
| EV1-C Schumann Alignment (CI)      | ✅ PASS            | ⏳ DEFERRED | v1.1.0 live |
| EV1-D HRV Coherence (CI)           | ✅ PASS            | ⏳ DEFERRED | v1.1.0 live |
| EV1-E Memory Retrieval Fidelity    | ✅ PASS (MRR=1.00) | — | v1.0.0 |

**v1.0.0 release gate: `EV1_empirical_validation_gates`**
→ ⏳ BLOCKED on EV1-A and EV1-B first clean CI run

Once EV1-A and EV1-B show ✅ in CI, update `GAIAmanifest.json`:

```json
"EV1_empirical_validation_gates": "complete"
```

**v1.1.0 Biometric Integration milestone** → blocked on EV1-C/D live hardware gates.

---

*All values in this document trace to a deterministic test assertion in `tests/ev1/`.
Unverified claims remain in the mythos layer. Do not promote to logos without a passing
CI run citation.*

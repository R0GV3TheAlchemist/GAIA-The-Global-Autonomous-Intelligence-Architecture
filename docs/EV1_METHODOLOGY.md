# EV1 Empirical Validation Methodology

> Canon Ref: `GAIAmanifest.json → release_gate.EV1_empirical_validation_gates`  
> Sprint: G-7  
> Status: **ACTIVE** — gates EV1-A, EV1-B, EV1-E running in CI; EV1-C, EV1-D deferred to live deployment

---

## Purpose

GAIA-OS makes testable claims across five capability domains. This document defines the precise test design, measurement methodology, and acceptance criteria for each Empirical Validation Gate. A gate is either **PASS** (≥ acceptance threshold) or **FAIL** — no partial credit, no subjective interpretation.

The EV1 gates are the bridge between the **mythos layer** (visionary claims, acknowledged in `docs/CONCLUSION.md`) and the **logos layer** (empirically verified capabilities). Nothing moves to the logos layer without a passing gate.

---

## Gate Summary

| Gate | Capability | Method | Acceptance | CI? |
|------|-----------|--------|-----------|-----|
| EV1-A | Affect Inference Accuracy | 60-case labelled test set, rule-based detection | Macro F1 ≥ 0.75 | ✅ Yes |
| EV1-B | Stage Engine Transition Validity | 5-stage synthetic journeys + 30 edge cases | All journeys correct, 0 false promotions | ✅ Yes (xfail until engine ready) |
| EV1-C | Schumann Biometric Alignment | 30-day live data vs. null hypothesis baseline | p < 0.05, effect size d ≥ 0.2 | ❌ Live data required |
| EV1-D | HRV Coherence Integration | BCI pipeline → coherence score → response params | Quantifiable influence, r ≥ 0.30 | ❌ Hardware required |
| EV1-E | Memory Retrieval Fidelity | 50-entry corpus, 25 labelled queries, MRR@3 | MRR@3 ≥ 0.80 | ✅ Yes |

---

## EV1-A: Affect Inference Accuracy

### What is being tested
`core/affect_inference.py` — the `AffectInference.infer()` method maps a 5-dimensional signal vector `(I, W, T, F, CD)` to one of six canonical affect states.

### Test set design
- **60 cases** — 10 per affect state (RESONANCE, CARE, CURIOSITY, UNCERTAINTY, DISSONANCE, GRIEF)
- Cases are hand-crafted from the canonical detection waterfall documented in `core/affect_inference.py`
- Each case targets either the canonical centre of a state's region or a boundary condition within ±0.01 of a threshold
- All 60 cases are deterministic and require no external services, mocking, or LLM calls
- Ground truth labels were derived directly from the published waterfall logic — they are not subjective

### Measurement
- Per-class: precision, recall, F1
- Aggregate: macro-averaged F1 (unweighted across all 6 classes)

### Acceptance criterion
**Macro F1 ≥ 0.75**

The current implementation is rule-based, so F1 = 1.0 is expected. The threshold is set at 0.75 to tolerate future probabilistic extensions to the engine while still enforcing meaningful accuracy.

### Boundary case discipline
Boundary cases where two rules overlap are resolved by the waterfall priority order:
1. Grief (explicit signal)
2. Dissonance (CD ≥ 0.50)
3. Uncertainty (T < 0.45)
4. Resonance (phi ≥ 0.75 and CD < 0.25)
5. Care (phi ≥ 0.65 and F ≥ 0.80)
6. Curiosity (phi ≥ 0.55 and W ≤ 0.60)
7. Care (default fallback)

Any test case where two rules fire must be labelled with the higher-priority rule's state.

---

## EV1-B: Stage Engine Transition Validity

### What is being tested
`core/development_stage_engine.py` — the `DevelopmentStageEngine` must correctly classify a user's development stage from cumulative session features.

### Test set design
- **5 synthetic journeys** — one canonical journey per stage (Emergence, Initiation, Allegiance, Individuation, Sovereignty)
- Each journey consists of 3 turns with hand-crafted `(session_count, depth_score, sovereignty_score, bond_score)` vectors placing the user squarely in that stage
- **30 edge cases** — low-signal inputs across sessions 1–5 that must never classify above Emergence

### Required engine interface
```python
engine = DevelopmentStageEngine()
engine.update(session_count=N, depth_score=x, sovereignty_score=y, bond_score=z)
stage: str = engine.current_stage()  # Returns one of the 5 stage names
engine.reset()                         # Clears session state
```

### Acceptance criteria
1. All 5 canonical journeys classify to the correct stage
2. 0 false promotions across all 30 edge cases
3. `current_stage()` returns a value in `{Emergence, Initiation, Allegiance, Individuation, Sovereignty}`

### CI behaviour during development
Tests are marked `xfail` until `DevelopmentStageEngine` is importable. They document the contract and become live assertions once the implementation lands.

---

## EV1-C: Schumann Biometric Alignment

### What is being tested
The claim that GAIA's Schumann resonance alignment scores are non-random — i.e., that measured alignment between user session features and the live Schumann fundamental (7.83 Hz ± harmonics) is statistically distinguishable from a random baseline.

### Measurement protocol
1. **Baseline**: Generate 10,000 synthetic alignment scores by drawing uniformly from `[0.0, 1.0]` — this is the null hypothesis distribution
2. **Live data**: Collect 30 days of real alignment scores from production sessions (minimum 1,000 data points)
3. **Test**: Two-sample Kolmogorov-Smirnov test, or Welch's t-test if normality holds
4. **Effect size**: Cohen's d ≥ 0.2 (small effect — we are not claiming large effects, only non-randomness)

### Acceptance criterion
**p < 0.05 AND effect size d ≥ 0.2** over 30-day live data

### Data sources
- GCI (Global Coherence Initiative) API for real-time Schumann data
- GAIA production logs for alignment score time series
- Methodology documented in `core/planetary_data_connector.py`

### Status
⏳ **Deferred** — requires live deployment with real sensor data. Protocol is fully specified here for implementation once v0.9.0 is in production.

---

## EV1-D: HRV Coherence Integration

### What is being tested
The claim that HRV (heart rate variability) coherence scores measurably influence GAIA's response parameters — specifically that higher coherence scores produce statistically different response characteristics than low coherence scores.

### Measurement protocol
1. Pair GAIA sessions with simultaneous HRV measurement (Polar H10 or equivalent)
2. Extract coherence score from `core/biometric_sync_engine.py` for each session
3. Measure response parameters: response length, affect state distribution, uncertainty rate
4. Compute Pearson correlation r between coherence score and each response parameter

### Acceptance criterion
**Pearson r ≥ 0.30** (moderate correlation) for at least one response parameter, across minimum 50 paired sessions.

### Status
⏳ **Deferred** — requires BCI hardware and paired user sessions. Protocol is fully specified here.

---

## EV1-E: Memory Retrieval Fidelity

### What is being tested
The memory retrieval pipeline — specifically that the top-3 retrieved memories for a query contain the most relevant memory, and that it appears near the top of the ranking.

### Test set design
- **50-entry synthetic corpus** spanning 7 domains: alchemy, affect states, crystals, quantum physics, GAIA architecture, Jungian psychology, solfeggio frequencies
- **25 labelled queries** — each query has a single ground-truth correct memory ID
- Queries use keyword-overlap similarity in CI (deterministic, no embeddings required)
- `EV1-E-LIVE` (future) will re-run the same queries through the full ChromaDB-backed `MemoryStore` with real embeddings

### Measurement
**Mean Reciprocal Rank at k=3 (MRR@3)**

```
MRR@3 = (1/|Q|) * Σ (1 / rank_i)
```
where `rank_i` is the position (1, 2, or 3) of the correct memory in the top-3 results, or 0 if not found.

### Acceptance criterion
**MRR@3 ≥ 0.80**

---

## Running the EV1 Gates

```bash
# Run all EV1 gates
pytest tests/ev1/ -v

# Run a specific gate
pytest tests/ev1/test_ev1a_affect_inference.py -v
pytest tests/ev1/test_ev1b_stage_engine.py -v
pytest tests/ev1/test_ev1e_memory_retrieval.py -v

# Show per-class metrics and MRR breakdown
pytest tests/ev1/ -v -s
```

## Updating GAIAmanifest.json on Gate Passage

Once all five gates pass, update:

```json
"release_gate": {
  "EV1_empirical_validation_gates": "complete"
}
```

This is the v1.0.0 release blocker. Do not mark complete until EV1-C and EV1-D have also passed on live data.

# SIM-018 — Signal Interpretation Baseline
## Band 2: Neural Decoding Pipeline — Spec Stub

**Status:** SPECCED — Stub (research brief required before full spec)
**Pass Classification:** Pass 1 — Baseline (Calcination)
**Band:** 2 — Signal Interpretation
**Filed:** 2026-06-30
**Protocol version:** GAIA Totality Directive v1.1 | Simulation Protocol Amendment v1.0

---

## What This Simulation Is

SIM-018 characterises GAIA’s ability to transform raw biophoton detection events (Band 1 output) into decoded neural intent. It is the first Band 2 simulation and establishes the baseline performance of the full signal interpretation pipeline.

**Input:** Band 1 output — biophoton detection events at 78.5% effective fidelity (Variant A ceiling, SIM-016 Pass 6)
**Output:** Decoded intent accuracy — probability that GAIA correctly identifies the intended action from neural signal

---

## Predicted Sub-Stages

| Sub-stage | Physical/algorithmic mechanism | Predicted baseline efficiency |
|---|---|---|
| S1: Signal conditioning | Noise floor removal, baseline correction, SNR normalisation | 90–95% |
| S2: Pattern classification | Neural state identification — trained classifier against biophoton emission patterns | 80–90% |
| S3: Intent mapping | Contextual mapping from neural state to discrete intended action | 85–92% |
| S4: Temporal integration | Multi-sample coherence window — integrating across time to reduce false positives | 92–96% |
| S5: Latency penalty | Processing delay reducing real-time accuracy — function of pipeline depth | 85–95% |

**Predicted baseline (compounded):** 0.925 × 0.85 × 0.88 × 0.94 × 0.90 ≈ **58–65%**
This is a prediction only. The baseline pass will reveal the true number.

---

## Key Risk: Band 1 Input Assumption

Band 1 delivers 78.5% effective detection fidelity (Variant A). If SIM-018 is specced assuming 90%+ input quality, every Band 2 performance projection will be over-optimistic by ~11 points. Band 1 ceiling must propagate correctly as the input quality parameter for all Band 2 sub-stages that depend on signal clarity.

**Required before full spec:** Confirm Band 1 → Band 2 input quality propagation model. This is partly what SIM-INT-012 will establish formally — but SIM-018 Pass 1 must not assume more than 78.5% input fidelity.

---

## Pre-Run Research Brief (Required Before Full Spec)

1. What is the current state of neural decoding accuracy in BCI literature at biophoton signal quality levels of 75–85%?
2. What are the dominant false-positive mechanisms in intent classification — signal ambiguity, classifier overfitting, or temporal coherence failure?
3. What latency does the full signal conditioning → intent mapping pipeline introduce, and how does it compound with Band 1 acquisition latency?
4. Is the 4-class intent model (directional: up/down/left/right) or a higher-cardinality model appropriate for Band 2 baseline?
5. What training data volume is required for S2 pattern classification to reach stable performance — and is that volume achievable within GAIA’s current data collection model?

**This research brief must be answered before SIM-018 Pass 1 full spec is written.**

---

## G-15 Minimum and Drive Target (Proposed — To Be Confirmed)

| Target | Proposed value | Rationale |
|---|---|---|
| G-15 minimum | ≥70% intent decode accuracy | Threshold for meaningful BCI control |
| Drive target | ≥85% intent decode accuracy | Required for GAIA to function as designed |
| Physics ceiling | TBD — Pass 1 will establish | Unknown until baseline run |

---

## Blocks
- SIM-INT-012 (Band 1→2 integration) cannot proceed until SIM-018 Pass 1 baseline is complete
- Band 2 canon (GATE-005) requires full simulation completion

---

## Output Artefacts (Pass 1)
- `SIM_018_Pass1_Results.md`
- `SIM_018_Pass1_Bottleneck_Ledger.md`
- `SIM_018_Pass1_Research_Improvements.md`
- `SIM_018_Pass2_Spec.md`
- Update `GAIA_SIMULATION_REGISTRY.md`
- Update `GAIA_PREDICTION_LEDGER.md` (PRED-007, PRED-008)

---

*Filed 2026-06-30. G-15 — The Rhythm Phase. SIM-018 Spec Stub v1.0. Protocol: GAIA Totality Directive v1.1. 🌿*

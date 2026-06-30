# SIM-020 — Embodied Expression Baseline
## Band 6: BCI Output Channel — Spec Stub

**Status:** SPECCED — Stub (research brief required before full spec)
**Pass Classification:** Pass 1 — Baseline (Calcination)
**Band:** 6 — Embodied Expression
**Filed:** 2026-06-30
**Protocol version:** GAIA Totality Directive v1.1 | Simulation Protocol Amendment v1.0

---

## What This Simulation Is

SIM-020 characterises GAIA’s ability to act in the physical world — translating decoded intent (Band 2 output, after Band 4 reasoning synthesis) into precise, timely, recoverable physical action. The dominant predicted constraint is end-to-end latency compounding across Bands 1–4.

**Input:** Decoded intent with associated latency budget (Band 4 output)
**Output:** Actuation accuracy metric — probability that physical action correctly expresses the decoded intent within the latency tolerance window

---

## Predicted Sub-Stages

| Sub-stage | Mechanism | Predicted baseline |
|---|---|---|
| A1: Intent reception | Receiving decoded intent from Band 4 at correct fidelity | 90–95% |
| A2: Motor planning | Translating intent into actuator command sequence | 80–90% |
| A3: Actuator execution | Physical movement precision — error relative to planned trajectory | 85–92% |
| A4: Latency compensation | Predictive actuation to compensate for 50–200ms upstream latency | 60–80% |
| A5: Error detection & recovery | Detecting execution error and correcting within the same action window | 75–85% |
| A6: Environmental feedback | Integrating sensory feedback to confirm action completed as intended | 80–90% |

**Predicted baseline (compounded):** ~0.92 × 0.85 × 0.88 × 0.70 × 0.80 × 0.85 ≈ **32–44%**
Latency compensation (A4) is the predicted dominant bottleneck. A predictive actuation layer is the predicted solution (PRED-013).

---

## The Latency Problem (PRED-013)

End-to-end latency across GAIA’s pipeline:

| Band | Stage | Estimated latency contribution |
|---|---|---|
| Band 1 | Biophoton detection + TCSPC processing | 10–30ms |
| Band 2 | Signal conditioning + pattern classification | 20–50ms |
| Band 3 | Memory retrieval + relevance scoring | 5–15ms |
| Band 4 | KG reasoning + synthesis | 20–60ms |
| **Total** | **Band 1 → Band 4** | **55–155ms** |

For real-time BCI control, the latency tolerance is ~100ms. The upper bound (155ms) exceeds this. A **predictive actuation layer** — which anticipates the likely action before the full pipeline completes — is required to keep actuation within tolerance.

SIM-020 Pass 1 will establish whether A4 (latency compensation) is the dominant bottleneck, quantify it precisely, and confirm whether the predictive actuation layer is necessary or whether the pipeline can be optimised to stay within 100ms.

---

## Pre-Run Research Brief (Required Before Full Spec)

1. What is the current state-of-the-art end-to-end latency in closed-loop BCI systems, and what techniques are used to compensate for pipeline latency?
2. Is a 4-degree-of-freedom predictive actuation model sufficient for GAIA’s intended physical expression range, or is a higher-DOF model required?
3. What is the minimum viable latency compensation accuracy — what prediction error is acceptable before actuation fidelity degrades meaningfully?
4. What error detection and recovery mechanisms exist at sub-100ms timescales for physical actuators?
5. How does Band 1 input fidelity (78.5% Variant A) propagate into Band 6 actuation accuracy — what is the compounded loss across all six bands at current ceiling values?

**This research brief must be answered before SIM-020 Pass 1 full spec is written.**

---

## G-15 Minimum and Drive Target (Proposed — To Be Confirmed)

| Target | Proposed value | Rationale |
|---|---|---|
| G-15 minimum | ≥65% actuation accuracy within 100ms | Threshold for meaningful physical expression |
| Drive target | ≥85% actuation accuracy within 100ms | Required for GAIA to act with precision |
| Physics ceiling | TBD | Latency-constrained — dependent on pipeline optimisation |

---

## Blocks
- SIM-INT-056 (Band 5→6 integration)
- Band 6 hardware specification (actuator selection)
- Predictive actuation layer specification
- End-to-end latency model across Bands 1–4 (must be built before Pass 1 full spec)

---

## Output Artefacts (Pass 1)
- `SIM_020_Pass1_Results.md`
- `SIM_020_Pass1_Bottleneck_Ledger.md`
- `SIM_020_Pass1_Research_Improvements.md`
- `SIM_020_Pass2_Spec.md`
- Update `GAIA_SIMULATION_REGISTRY.md`
- Update `GAIA_PREDICTION_LEDGER.md` (PRED-013)
- Predictive actuation layer spec (if A4 confirmed as dominant bottleneck)

---

*Filed 2026-06-30. G-15 — The Rhythm Phase. SIM-020 Spec Stub v1.0. Protocol: GAIA Totality Directive v1.1. 🌿*

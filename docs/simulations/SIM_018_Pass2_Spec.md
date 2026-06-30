# SIM-018 Pass 2 — Spec
## Band 2: Root Cause Pass — Left↔Right Confusion Resolution

**Pass classification:** Root Cause (Dissolution)
**Protocol version:** GAIA Totality Directive v1.1 | Engineering Manifesto v1.0
**Date:** 2026-06-30
**BCI entering:** 74.8% ±2.3%
**Drive target:** ≥85%
**Gap:** 10.2 pts

---

## Objective

Resolve the Left↔Right confusion pair (12.3% confusion rate) as the dominant bottleneck. Apply the three improvements identified in Pass 1, in priority order, isolating each contribution.

---

## Changes Applied (Isolation Design)

| Sub-variant | Change | Held constant | Purpose |
|---|---|---|---|
| 2A | SVM (RBF) replaces linear discriminant | Everything else at P1 baseline | Isolate classifier upgrade contribution |
| 2B | SVM + temporal window 200→400ms | Training set at P1 baseline | Isolate window extension contribution |
| 2C | SVM + 400ms window + 2,400 trials/class | — | Full combined improvement |

---

## Pre-Run Research Brief

1. What RBF kernel parameters (C, gamma) are appropriate for a 4-class biophoton pattern classification problem at ~800 events/second input rate?
2. Does extending the temporal coherence window to 400ms introduce any risk of capturing cross-trial contamination at 2.0-second trial lengths?
3. Is the Fire group’s accuracy lead (76.1%) explained by higher spatial coherence in HER2+ emission, or by higher per-event SNR in this group?
4. Does the TCSPC 2ms latency optimisation require changes to the S2 classifier or only to the event buffering pipeline?

**All four must be answered before Pass 2 is run.**

---

## Predicted Results

| Sub-variant | Predicted accuracy | Rationale |
|---|---|---|
| 2A (SVM only) | 80–83% | L↔R confusion expected to drop from 12.3% to ~5% |
| 2B (SVM + window) | 82–85% | Additional +2–3 pts from coherence |
| 2C (full) | **83–86%** | At or above drive target |

---

## Output Artefacts
- `SIM_018_Pass2_Results.md`
- `SIM_018_Pass2_Bottleneck_Ledger.md`
- `SIM_018_Pass2_Research_Improvements.md`
- `SIM_018_Pass3_Spec.md` (if drive target not yet met)
- Update `GAIA_SIMULATION_REGISTRY.md`
- GATE-005 Tier 1 conditions: G-15 minimum already cleared; ceiling characterisation pending

---

*SIM-018 Pass 2 Spec. 2026-06-30. Protocol: GAIA Totality Directive v1.1. 🌿*

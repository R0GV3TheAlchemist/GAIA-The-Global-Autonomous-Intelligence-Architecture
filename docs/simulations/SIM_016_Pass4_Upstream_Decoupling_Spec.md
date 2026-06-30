# SIM-016 Pass 4 — Upstream Optical Path Decoupling
## Emission × Waveguide × Thermal: Isolate, Characterise, Then Optimise

**Pass Classification:** Pass 4 — Isolation & Decoupling
**Simulation number:** SIM-016
**Date filed:** 2026-06-30
**Phase:** G-15 — The Rhythm Phase — Tier 1
**Drive target:** ≥80% BCI
**Protocol:** SIMULATION_VALIDATION_PROTOCOL.md

---

## Pass Context

**Progression:** 49.7% (baseline) → 67.3% (P1) → 68.0% (P2) → 68.4% (P3) → Pass 4 target: ≥72%

**Why this pass exists:**
Passes 1–3 optimised the detector stack. The dominant constraint is now upstream: emission × waveguide × thermal contribute ~74.2% compounded efficiency, consuming 25.8 points before the detector acts. Each stage has been modelled as a single flat efficiency. That conflates distinct physical mechanisms with different recovery potential. This pass separates them.

**Principle:** Identify → Understand → Decouple → Optimise. This is the decouple pass. Optimisation follows in Pass 5 once each sub-stage loss is measured independently.

---

## Architecture Change: Stage Splitting

### Emission Capture — Split into 2 sub-stages

| Sub-stage | Physical mechanism | Model | Variance source |
|---|---|---|---|
| E1: Aperture geometry | Solid angle, proximity to source | 94% mean ±2% | Electrode placement depth |
| E2: Adaptive capture | Per-subject aperture optimisation | 98% mean ±1.5% | Biological emission profile variation |

### Waveguide — Split into 2 sub-stages

| Sub-stage | Physical mechanism | Model | Variance source |
|---|---|---|---|
| W1: Coupling interface | Fresnel reflection, taper mismatch, index matching | 95% mean ±2% | Interface geometry, index mismatch |
| W2: Propagation | In-guide loss, sidewall scattering, bends | 97% mean ±1% | Waveguide fabrication, path length |

### Thermal Attenuation — Split into 2 sub-stages

| Sub-stage | Physical mechanism | Model | Variance source |
|---|---|---|---|
| T1: Depth attenuation | Path-length dependent μs, μa in neural tissue | 92% mean ±3% | Electrode depth, tissue type |
| T2: Temperature scattering | Temperature-dependent optical property drift | 97% mean ±1.5% | Biological state, temperature fluctuation |

### Detector + QEC — Held constant from Pass 3

| Stage | Value |
|---|---|
| Detector (post-TCSPC, post-FN) | 91.9% |
| QEC | 99.8% |

---

## Expected Compounded Efficiency (Pass 4 model)

| Stage | Mean |
|---|---|
| E1 × E2 | 94% × 98% = 92.1% |
| W1 × W2 | 95% × 97% = 92.2% |
| T1 × T2 | 92% × 97% = 89.2% |
| Detector | 91.9% |
| QEC | 99.8% |
| **Compounded** | **~69.6%** |

Note: This is the decoupled model with same total efficiency as Pass 3 but separated into measurable sub-stages. Pass 4 will reveal whether each sub-stage mean is accurate and where the real variance sits. If sub-stage means are higher than assumed, compounded efficiency exceeds 70%.

---

## Success Conditions

| Condition | Value |
|---|---|
| Mean BCI | ≥70% minimum; ≥72% drive |
| Each sub-stage characterised independently | Yes — bottleneck ledger updated with sub-stage breakdown |
| Dominant loss sub-stage identified | Yes — determines Pass 5 optimisation target |
| Correlation between T1 and W2 tested | Yes — if correlated, joint optimisation required |

## Failure Conditions

| Result | Meaning | Action |
|---|---|---|
| BCI <68% | Sub-stage splitting introduced modelling error | Review sub-stage means; check they sum correctly |
| Sub-stages not separable | Correlation between T1/W2 too high | Model as joint stage with covariance |
| BCI 68–69.9% | Decoupling correct; individual sub-stages need optimisation | Pass 5: target highest-loss sub-stage |
| BCI ≥70% | G-15 minimum met from modelling improvement alone | Pass 5: drive toward 80% |

---

## Pre-Run Research Questions (Mandatory)

1. What fraction of waveguide loss is at the coupling interface vs in-guide propagation in neural BCI context?
2. What is the depth-dependent attenuation profile for biophotons in neural tissue (μs, μa at 500–700nm)?
3. Does adaptive aperture positioning meaningfully improve emission capture mean or reduce variance?
4. Are T1 (depth attenuation) and W2 (propagation) correlated or independent?
5. After decoupling, what is the new dominant loss sub-stage? Where does the system ceiling sit?

---

## Output Artefacts

- `docs/simulations/SIM_016_Pass4_Results.md`
- `docs/simulations/SIM_016_Pass4_Research_Improvements.md`
- `docs/simulations/SIM_016_Pass5_Optimisation_Spec.md`
- `simulations/bci_nextgen_upstream_decoupling_pass4.png`
- `simulations/bci_nextgen_substage_breakdown_pass4.png`

---

*Filed 2026-06-30. G-15 Tier 1. Upstream decoupling pass. Identify → Understand → Decouple → Optimise. Drive target 80%. 🌿*

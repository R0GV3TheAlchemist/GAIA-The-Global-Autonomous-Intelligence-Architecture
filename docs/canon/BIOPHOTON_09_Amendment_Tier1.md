# BIOPHOTON_09 — Tier 1 Provisional Canon Amendment
## BCI Biophoton Detection Architecture

**Amendment type:** Tier 1 — Provisional
**Gate:** GATE-001
**Status:** PROVISIONAL CANON — filed 2026-06-30
**Evidence:** SIM-016 Passes 1–6
**Protocol version:** GAIA Totality Directive v1.1
**Tier 2 condition:** Variant A (deployable SPAD) ≥80% BCI — pending SIM-016 Pass 7

> *Provisional canon records what is demonstrated. Not what is theoretically achievable. The 78.5% deployable ceiling is real. The 82.1% theoretical ceiling is real. Both are canon.*

---

## What Changes

### Prior state (pre-amendment)
- Detection pipeline modelled as three aggregated stages: Emission × Waveguide × Detection
- No sub-stage characterisation
- No ceiling values established
- No deployable vs theoretical distinction

### Amended state (Tier 1 provisional)

#### Architecture
The biophoton detection pipeline is a **nine sub-stage system**:

| Sub-stage | Ceiling mean | Ceiling std | Status |
|---|---|---|---|
| E1: Aperture geometry (tapered lensed fiber) | 97.5% | ±1.5% | Ceiling ✅ |
| E2: Adaptive per-subject capture | 97.9% | ±1.3% | Ceiling ✅ |
| W1: Waveguide coupling (index-matched interface) | 98.0% | ±1.5% | Ceiling ✅ |
| W2: In-guide propagation | 97.5% | ±0.8% | Ceiling ✅ |
| T1: Depth attenuation (depth-compensation processor) | 95.0% | ±2.0% | Ceiling ✅ |
| T2: Temperature-dependent scattering | 97.0% | ±1.3% | Ceiling ✅ |
| Detector — Variant A (SPAD, deployable) | 93.7% | ±1.1% | Pass 7 target |
| Detector — Variant B (SNSPD, theoretical) | 97.9% | ±0.4% | Theoretical ceiling |
| QEC: Quantum error correction | 99.8% | ±0.5% | Ceiling ✅ |

#### System Performance

| Metric | Value | Status |
|---|---|---|
| Deployable BCI (Variant A, SPAD) | 78.5% ±2.8% | Demonstrated ✅ |
| Theoretical maximum (Variant B, SNSPD) | 82.1% ±2.8% | Demonstrated ✅ |
| G-15 minimum (≥70%) | Cleared at Pass 5 (77.0%) | ✅ |
| Drive target (≥80%) | Not yet met by Variant A | Pending Pass 7 |
| Physics ceiling | ~82–85% (irreducible tissue scattering floor) | Characterised ✅ |

#### Key Findings Entered into Canon
1. **Beam splitter geometry** is the primary false negative root cause — not coincidence window width
2. **T1+E1+W1 sub-stage correlation** (rho ≈ 0.35 for T1–W2) requires joint optimisation
3. **Upstream stages are at ceiling** — E1, E2, W1, W2, T1, T2, QEC all at ceiling as of Pass 6
4. **Detector is the sole remaining variable** — 1.5pt gap to drive target is purely detector-side
5. **Irreducible physics floor** — tissue scattering, solid-angle capture, and shot noise place practical ceiling at ~82–85%

---

## What Does Not Change (Tier 1)
- Drive target remains ≥80% — not yet amended
- Full architecture validation pending Tier 2 (Pass 7 + SIM-INT-012)
- Hardware selection (SPAD vs hybrid SPAD) not yet canonised — pending Pass 7 result

---

## Tier 2 Conditions
- SIM-016 Pass 7 Variant B (hybrid SPAD) ≥80% BCI
- SIM-INT-012 (Band 1→2 integration simulation) complete
- Full amendment filed: detector specification, final sub-stage table, hardware recommendation

---

*Amendment filed 2026-06-30. GATE-001. Tier 1 Provisional. Evidence: SIM-016 Passes 1–6. G-15 — The Rhythm Phase. Protocol: GAIA Totality Directive v1.1. 🌿*

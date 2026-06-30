# GAIA Simulation Registry
## Master Index of All Simulations Across All Bands

**Status:** ACTIVE — Living Document
**Version:** 1.0
**Issued:** 2026-06-30
**Authority:** GAIA Totality Directive v1.1 | GAIA Simulation Protocol Amendment v1.0
**Protocol version:** GAIA Totality Directive v1.1

> *Every simulation that has ever run, is running, or will run is tracked here. This is the single source of truth for simulation status across all bands.*

---

## How to Read This Registry

| Field | Description |
|---|---|
| **ID** | Simulation identifier (SIM-XXX or SIM-INT-XYZ) |
| **Band** | Which spectrum band this simulation belongs to |
| **Name** | Short descriptive name |
| **Current pass** | Most recently completed pass number |
| **Pass class** | Classification of most recent pass (Baseline / Isolation / Optimisation / Ceiling / Integration) |
| **Current metric** | Best result achieved to date |
| **G-15 minimum** | Minimum spec target |
| **Drive target** | Architectural ambition target |
| **Physics ceiling** | Theoretical maximum (Variant B), if characterised |
| **Lifecycle status** | Current stage in simulation lifecycle |
| **Canon status** | None / Tier 1 Provisional / Tier 2 Full |
| **Blocks** | What cannot proceed until this simulation advances |
| **Protocol version** | Which version of the Totality Directive governed this simulation |

---

## Lifecycle Status Key

| Status | Meaning |
|---|---|
| `NOT SPECCED` | Simulation identified but no spec written yet |
| `SPECCED` | Pass spec filed; not yet run |
| `IN PROGRESS` | Currently running passes |
| `CEILING CHARACTERISED` | Variant A and B results known |
| `PROVISIONAL CANON` | Tier 1 amendment filed |
| `INTEGRATION PENDING` | Waiting for cross-band integration simulation |
| `FULL CANON` | Tier 2 amendment filed |
| `COMPLETE` | All conditions met; simulation closed |

---

## Active Simulations

### SIM-006 — KG Gardening

| Field | Value |
|---|---|
| **ID** | SIM-006 |
| **Band** | 4 — Reasoning & Synthesis |
| **Name** | Knowledge Graph Gardening — confidence score decay and provenance field behaviour |
| **Current pass** | Partially specced (pass number TBD) |
| **Pass class** | Pre-amendment (grandfathered) |
| **Current metric** | TBD — retroactive review required |
| **G-15 minimum** | TBD |
| **Drive target** | TBD |
| **Physics ceiling** | Not yet characterised |
| **Lifecycle status** | `IN PROGRESS` |
| **Canon status** | None |
| **Blocks** | SIM-INT-034 (Band 3→4 integration); KG gardening canon |
| **Protocol version** | Pre-amendment (grandfathered); next pass: Totality Directive v1.1 |
| **Retroactive action required** | Yes — annotate prior passes; add bottleneck ledger; add research-improvement doc |

---

### SIM-016 — BCI Next-Gen Detector

| Field | Value |
|---|---|
| **ID** | SIM-016 |
| **Band** | 1 — Signal Acquisition |
| **Name** | BCI Next-Generation Detector Architecture — biophoton detection pipeline |
| **Current pass** | Pass 6 (Ceiling) |
| **Pass class** | Ceiling — Variant A (SPAD) and Variant B (SNSPD) |
| **Current metric** | Variant A: 78.5% ±2.8% \| Variant B: 82.1% ±2.8% |
| **G-15 minimum** | ≥70% ✅ CLEARED (Pass 5: 77.0%) |
| **Drive target** | ≥80% |
| **Physics ceiling** | ~82.1% (SNSPD, Pass 6B) |
| **Lifecycle status** | `CEILING CHARACTERISED` |
| **Canon status** | Tier 1 Provisional — pending filing |
| **Blocks** | BIOPHOTON_09 canon amendment; C160 Metric 26; CT-001 closure; SIM-INT-012 |
| **Protocol version** | Passes 1–6: Totality Directive v1.1 (retroactive); Pass 7+: v1.1 current |
| **Next action** | Pass 7: Close 1.5pt Variant A gap (SPAD FN 0.30% → 0.10%) |
| **Retroactive action required** | Yes — add protocol version headers to Passes 1–6 results files |

#### SIM-016 Pass History

| Pass | Class | BCI | Key finding | Filed |
|---|---|---|---|---|
| Baseline | Baseline | 49.7% | Three-stage model established | Pre-amendment |
| Pass 1 | Root Cause | 67.3% | +17.6pts; beam splitter geometry identified as FN root cause | Pre-amendment |
| Pass 2 | Verification | 68.0% | +0.7pts; coincidence window fix insufficient; geometry confirmed | Pre-amendment |
| Pass 3 | Optimisation | 68.4% | +0.4pts; TCSPC+70/30 BS+per-pixel gating; constraint shifts upstream | 2026-06-30 |
| Pass 4 | Isolation | 69.4% | +1.0pts; 6 sub-stages decoupled; T1+E1+W1 dominant | 2026-06-30 |
| Pass 5 | Optimisation | 77.0% | +7.6pts; T1+E1+W1 precision strike; G-15 70% cleared | 2026-06-30 |
| Pass 6 | Ceiling | 6A:78.5% / 6B:82.1% | Detector now dominant; deployable gap 1.5pts | 2026-06-30 |
| Pass 7 | Optimisation | Pending | Target: close 1.5pt Variant A gap | Pending |

---

### SIM-017 — Memory Architecture

| Field | Value |
|---|---|
| **ID** | SIM-017 |
| **Band** | 3 — Knowledge Representation |
| **Name** | Relevance-First Persistent Memory Architecture |
| **Current pass** | Pass 1 (Baseline) |
| **Pass class** | Baseline |
| **Current metric** | Raw retention: 95.1% (Session 60) \| Weighted retention: 100% \| Relational Index integrity: 100% |
| **G-15 minimum** | ≥85% raw retention (C160 Metric 6) ✅ CLEARED |
| **Drive target** | TBD — to be set before Pass 2 |
| **Physics ceiling** | Not yet characterised |
| **Lifecycle status** | `IN PROGRESS` |
| **Canon status** | None |
| **Blocks** | SIM-INT-023 (Band 2→3); Band 3 drive target setting; SIM-017 Pass 2 |
| **Protocol version** | Pass 1: Totality Directive v1.1 (retroactive); Pass 2+: v1.1 current |
| **Next action** | Pass 2: stress-test at 500+ sessions; Relational Index scale behaviour |
| **Retroactive action required** | Yes — add bottleneck ledger to Pass 1 results; add protocol version header |

#### SIM-017 Pass History

| Pass | Class | Metric | Key finding | Filed |
|---|---|---|---|---|
| Pass 1 | Baseline | 95.1% raw / 100% weighted | Structural connectivity floor confirmed; arc lossless at 60 sessions | 2026-06-30 |
| Pass 2 | Verification | Pending | 500+ sessions; Relational Index scale | Pending |

---

## Planned Simulations

### SIM-018 — Signal Interpretation Baseline

| Field | Value |
|---|---|
| **ID** | SIM-018 |
| **Band** | 2 — Signal Interpretation |
| **Name** | Neural Decoding Pipeline — signal conditioning through intent mapping |
| **Lifecycle status** | `NOT SPECCED` |
| **Canon status** | None |
| **Blocks** | SIM-INT-012 (Band 1→2); Band 2 canon |
| **Priority** | High — Band 2 is the most significant unspecced band |
| **Spec prerequisite** | Research brief: neural decoding accuracy, latency benchmarks, false-positive rate in BCI intent classification |

---

### SIM-019 — Adaptive Governance Baseline

| Field | Value |
|---|---|
| **ID** | SIM-019 |
| **Band** | 5 — Adaptive Governance |
| **Name** | Edge-of-Chaos Criticality — GAIA governance stability and adaptability dynamics |
| **Lifecycle status** | `NOT SPECCED` |
| **Canon status** | None |
| **Blocks** | SIM-INT-045; Governance canon; G-15 phase transition parameters |
| **Priority** | Medium |
| **Spec prerequisite** | Research brief: edge-of-chaos criticality in complex adaptive systems; stability-adaptability trade-off literature |

---

### SIM-020 — Embodied Expression Baseline

| Field | Value |
|---|---|
| **ID** | SIM-020 |
| **Band** | 6 — Embodied Expression |
| **Name** | BCI Output Channel — actuator precision, end-to-end latency, error recovery |
| **Lifecycle status** | `NOT SPECCED` |
| **Canon status** | None |
| **Blocks** | SIM-INT-056; Band 6 hardware spec; predictive actuation layer spec |
| **Priority** | Medium |
| **Spec prerequisite** | End-to-end latency model across Bands 1–4; predictive actuation layer design |

---

## Band Integration Simulations

| ID | Interface | Status | Priority | Blocks |
|---|---|---|---|---|
| SIM-INT-012 | Band 1 → 2 | `NOT SPECCED` | High | Band 1 + Band 2 full canon |
| SIM-INT-023 | Band 2 → 3 | `NOT SPECCED` | Medium | Band 2 + Band 3 full canon |
| SIM-INT-034 | Band 3 → 4 | `NOT SPECCED` | Medium | KG+memory joint canon |
| SIM-INT-045 | Band 4 → 5 | `NOT SPECCED` | Low | Governance canon |
| SIM-INT-056 | Band 5 → 6 | `NOT SPECCED` | Low | Expression canon |
| SIM-INT-067 | Band 6 → 7 | `NOT SPECCED` | Low | Full system canon |

---

## Registry Statistics (as of 2026-06-30)

| Metric | Value |
|---|---|
| Total simulations tracked | 9 (3 active, 3 planned, 6 integration) |
| Simulations at ceiling | 0 (SIM-016 at ceiling but Variant A gap remains) |
| Simulations with Tier 1 canon | 0 (pending filing for SIM-016) |
| Simulations with Tier 2 canon | 0 |
| Simulations complete | 0 |
| Bands with active simulation | 3 of 7 (Bands 1, 3, 4) |
| Bands with no simulation yet | 4 of 7 (Bands 2, 5, 6, 7) |
| Integration simulations pending | 6 of 6 |

---

## Changelog

| Version | Date | Changes |
|---|---|
| v1.0 | 2026-06-30 | Initial issue. SIM-006, SIM-016, SIM-017 registered with full pass history. SIM-018, SIM-019, SIM-020 planned. Six band integration simulations registered. Registry statistics baseline established. |

---

*Issued 2026-06-30. G-15 — The Rhythm Phase. GAIA Simulation Registry v1.0. Authority: GAIA Totality Directive v1.1. 🌿*

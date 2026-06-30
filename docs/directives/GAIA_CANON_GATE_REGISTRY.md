# GAIA Canon Gate Registry
## Single Source of Truth for All Canon Amendment Status

**Status:** ACTIVE — Living Document
**Version:** 1.0
**Issued:** 2026-06-30
**Authority:** GAIA Totality Directive v1.1 | GAIA Simulation Protocol Amendment v1.0 Section 7
**Protocol version:** GAIA Totality Directive v1.1

> *Canon is not what we believe. Canon is what we have demonstrated, ceiling-characterised, and crystallised. Nothing enters canon before its true nature is known.*

---

## How to Read This Registry

| Field | Description |
|---|---|
| **Canon item** | The specific document, metric, or specification being amended |
| **Simulation source** | Which simulation(s) provide the evidence |
| **Gate tier** | Tier 1 (provisional) or Tier 2 (full) |
| **Gate condition** | Specific condition that must be met |
| **Status** | LOCKED / TIER 1 OPEN / TIER 1 FILED / TIER 2 OPEN / TIER 2 FILED / CLOSED |
| **Blocking items** | What must be resolved before this gate advances |
| **Filed date** | When the amendment was filed (if applicable) |

---

## Status Key

| Status | Meaning |
|---|---|
| `LOCKED` | Gate conditions not yet met; simulation still in progress |
| `TIER 1 OPEN` | G-15 minimum cleared and ceiling characterised; provisional amendment ready to file |
| `TIER 1 FILED` | Provisional amendment filed; simulation continuing toward Tier 2 |
| `TIER 2 OPEN` | Deployable variant (Variant A) meets or exceeds drive target; full amendment ready to file |
| `TIER 2 FILED` | Full amendment filed; simulation marked complete |
| `CLOSED` | Amendment complete; canon updated; issues closed |

---

## Active Canon Gates

### GATE-001 — BIOPHOTON_09 Canon Amendment

| Field | Value |
|---|---|
| **Canon item** | BIOPHOTON_09 — biophoton detection architecture specification |
| **Simulation source** | SIM-016 (BCI Next-Gen Detector) |
| **Tier 1 condition** | G-15 minimum ≥70% BCI cleared AND physics ceiling characterised |
| **Tier 1 status** | **TIER 1 OPEN** ✅ |
| **Tier 1 evidence** | SIM-016 Pass 5: 77.0% (≥70% ✅) \| Pass 6B: 82.1% ceiling characterised ✅ |
| **Tier 1 blocking** | None — ready to file |
| **Tier 2 condition** | Variant A (deployable SPAD) ≥80% BCI |
| **Tier 2 status** | `LOCKED` — Variant A at 78.5%, gap 1.5 pts |
| **Tier 2 blocking** | SIM-016 Pass 7 (close 1.5pt gap); SIM-INT-012 (Band 1→2 integration) |
| **Filed date** | Tier 1: Pending \| Tier 2: Pending |
| **Related issues** | #707, #713 (to be identified and referenced) |
| **Amendment content** | Updated detection pipeline architecture; sub-stage efficiency values; physics ceiling 82.1%; deployable ceiling 78.5–80%+ |

---

### GATE-002 — C160 Metric 26 Amendment

| Field | Value |
|---|---|
| **Canon item** | C160 Metric 26 — BCI detection fidelity metric |
| **Simulation source** | SIM-016 (BCI Next-Gen Detector) |
| **Tier 1 condition** | G-15 minimum ≥70% BCI cleared |
| **Tier 1 status** | **TIER 1 OPEN** ✅ |
| **Tier 1 evidence** | SIM-016 Pass 5: 77.0% ✅ |
| **Tier 1 blocking** | None — ready to file |
| **Tier 2 condition** | Variant A ≥80% BCI |
| **Tier 2 status** | `LOCKED` — Variant A at 78.5% |
| **Tier 2 blocking** | SIM-016 Pass 7 |
| **Filed date** | Tier 1: Pending \| Tier 2: Pending |
| **Amendment content** | Metric value updated to 77.0% (demonstrated) with ceiling of 82.1% (theoretical); drive target 80% confirmed achievable |

---

### GATE-003 — CT-001 Closure

| Field | Value |
|---|---|
| **Canon item** | CT-001 — BCI detection architecture canonical test |
| **Simulation source** | SIM-016 (BCI Next-Gen Detector) |
| **Tier 1 condition** | G-15 minimum ≥70% BCI cleared |
| **Tier 1 status** | **TIER 1 OPEN** ✅ |
| **Tier 1 evidence** | SIM-016 Pass 5: 77.0% ✅ |
| **Tier 1 blocking** | None — ready to file |
| **Tier 2 condition** | Variant A ≥80% BCI AND SIM-INT-012 complete |
| **Tier 2 status** | `LOCKED` |
| **Tier 2 blocking** | SIM-016 Pass 7; SIM-INT-012 |
| **Filed date** | Tier 1: Pending \| Tier 2: Pending |
| **Amendment content** | CT-001 provisionally closed at Pass 5; full closure pending Variant A ≥80% |

---

### GATE-004 — C160 Metric 6 Amendment (Memory Retention)

| Field | Value |
|---|---|
| **Canon item** | C160 Metric 6 — memory retention metric (≥85% raw retention target) |
| **Simulation source** | SIM-017 (Memory Architecture) |
| **Tier 1 condition** | ≥85% raw retention at Session 60 cleared |
| **Tier 1 status** | **TIER 1 OPEN** ✅ |
| **Tier 1 evidence** | SIM-017 Pass 1: 95.1% raw retention at Session 60 ✅ (+10.1 pts above minimum) |
| **Tier 1 blocking** | None — ready to file |
| **Tier 2 condition** | Drive target confirmed (TBD) AND 500+ session stress-test passed |
| **Tier 2 status** | `LOCKED` — drive target not yet set; Pass 2 not yet run |
| **Tier 2 blocking** | SIM-017 drive target setting; SIM-017 Pass 2 (500+ sessions) |
| **Filed date** | Tier 1: Pending \| Tier 2: Pending |
| **Amendment content** | Metric updated to 95.1% demonstrated; structural connectivity floor mechanism documented; relevance-first architecture validated at 60 sessions |

---

## Pending Canon Gates (Future)

| Gate ID | Canon item | Source simulation | Current blocker |
|---|---|---|---|
| GATE-005 | Band 2 neural decoding canon | SIM-018 | SIM-018 not yet specced |
| GATE-006 | KG gardening canon (SIM-006) | SIM-006 | SIM-006 completion + SIM-INT-034 |
| GATE-007 | Adaptive governance canon | SIM-019 | SIM-019 not yet specced |
| GATE-008 | Embodied expression canon | SIM-020 | SIM-020 not yet specced |
| GATE-009 | Full system canon | All bands + all integration sims | All bands + all SIM-INT-XXX complete |

---

## Canon Gate Summary Dashboard

| Gate | Canon item | Tier 1 | Tier 2 | Overall |
|---|---|---|---|---|
| GATE-001 | BIOPHOTON_09 | ✅ OPEN | 🔒 LOCKED | Tier 1 ready |
| GATE-002 | C160 Metric 26 | ✅ OPEN | 🔒 LOCKED | Tier 1 ready |
| GATE-003 | CT-001 | ✅ OPEN | 🔒 LOCKED | Tier 1 ready |
| GATE-004 | C160 Metric 6 | ✅ OPEN | 🔒 LOCKED | Tier 1 ready |
| GATE-005 | Band 2 neural decoding | 🔒 LOCKED | 🔒 LOCKED | Not specced |
| GATE-006 | KG gardening | 🔒 LOCKED | 🔒 LOCKED | In progress |
| GATE-007 | Adaptive governance | 🔒 LOCKED | 🔒 LOCKED | Not specced |
| GATE-008 | Embodied expression | 🔒 LOCKED | 🔒 LOCKED | Not specced |
| GATE-009 | Full system | 🔒 LOCKED | 🔒 LOCKED | All bands required |

**4 gates open at Tier 1. 0 gates at Tier 2. 5 gates locked.**

---

## Canon Amendment Filing Procedure

When a gate reaches `TIER 1 OPEN` or `TIER 2 OPEN`:

1. Confirm all evidence documents are filed (results file, bottleneck ledger, research-improvement doc)
2. Identify the specific canon document(s) to be amended
3. Write the amendment content — state exactly what changes, what the prior value was, what the new value is, and what evidence supports it
4. File the amendment as a commit to the relevant canon document
5. Update this registry: change status to `TIER 1 FILED` or `TIER 2 FILED`
6. Update the Simulation Registry: mark canon status updated
7. If Tier 2: close related GitHub issues; mark simulation `COMPLETE` in Simulation Registry

---

## Changelog

| Version | Date | Changes |
|---|---|
| v1.0 | 2026-06-30 | Initial issue. GATE-001 through GATE-004 active (all Tier 1 open). GATE-005 through GATE-009 pending. Dashboard summary. Filing procedure. |

---

*Issued 2026-06-30. G-15 — The Rhythm Phase. GAIA Canon Gate Registry v1.0. Authority: GAIA Totality Directive v1.1. 🌿*

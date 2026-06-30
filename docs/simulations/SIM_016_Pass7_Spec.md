# SIM-016 Pass 7 — Closing the Variant A Gap
## 16-Channel TCSPC vs Hybrid SPAD Room-Temperature Design

**Pass Classification:** Pass 7 — Optimisation
**Simulation number:** SIM-016
**Date filed:** 2026-06-30
**Drive target:** ≥80% BCI (Variant A deployable)
**Protocol version:** GAIA Totality Directive v1.1 | Simulation Protocol Amendment v1.0

---

## Pass Context

**Progression:** 49.7% → ... → 77.0% (P5) → 78.5% (P6A) → **Pass 7 target: ≥80% (Variant A)**

This is the final optimisation pass for SIM-016. The only remaining non-ceiling sub-stage is the detector (6.50 log-pts, effective efficiency 93.7%). Two sub-variants tested:
- **7A:** 16-channel TCSPC + 40ps reconstruction window (incremental; deployable today)
- **7B:** Hybrid SPAD room-temperature design (96% efficiency; deployable; near-term TRL 6+)

If 7B reaches ≥80%, Tier 2 canon gate opens for GATE-001, GATE-002, GATE-003.

---

## Parameters

### Upstream — All at Ceiling, Held from Pass 6

| Sub-stage | Mean | Std | Status |
|---|---|---|---|
| E1_aperture | 97.5% | 1.5% | Ceiling ✅ |
| E2_adaptive | 97.9% | 1.3% | Ceiling ✅ |
| W1_coupling | 98.0% | 1.5% | Ceiling ✅ |
| W2_propagation | 97.5% | 0.8% | Ceiling ✅ |
| T1_depth | 95.0% | 2.0% | Ceiling ✅ |
| T2_temp_scatter | 97.0% | 1.3% | Ceiling ✅ |
| QEC | 99.8% | 0.5% | Ceiling ✅ |

### Detector — Two Sub-Variants

| Parameter | 7A: 16-ch TCSPC | 7B: Hybrid SPAD |
|---|---|---|
| Raw efficiency | 94.0% | 96.0% |
| FN rate | 0.13% | 0.10% |
| Effective efficiency | ~93.9% | ~95.9% |
| Reconstruction window | 40ps | 40ps |
| Operating temp | 300K | 300K |
| Deployable | Yes | Yes |

---

## Success Conditions

| Condition | 7A | 7B |
|---|---|---|
| Mean BCI ≥80% | Not expected (≈ 79.2%) | Required |
| All elemental groups ≥80% | — | Required |
| All sub-stages at ceiling | Confirm | Confirm |
| Tier 2 canon gate status | Remains locked | Opens if ≥80% |

## Failure Conditions

| Result | Meaning | Action |
|---|---|---|
| 7B BCI <80% | Hybrid SPAD model over-optimistic | Review hybrid efficiency assumption; research TRL |
| 7A BCI <79% | 16-ch TCSPC model error | Review FN rate calculation |
| Any group <78% | Variance issue in specific group | Elemental group variance analysis |

---

## Output Artefacts

- `docs/simulations/SIM_016_Pass7_Results.md`
- `docs/simulations/SIM_016_Pass7_Research_Improvements.md` (final; includes ceiling confirmation)
- Canon amendments: GATE-001, GATE-002, GATE-003 (if 7B ≥80%)
- `docs/directives/GAIA_SIMULATION_REGISTRY.md` update
- `docs/directives/GAIA_CANON_GATE_REGISTRY.md` update

---

*Filed 2026-06-30. G-15 Tier 1. Final optimisation pass. Two sub-variants. Drive target 80%. Protocol version: GAIA Totality Directive v1.1. 🌿*

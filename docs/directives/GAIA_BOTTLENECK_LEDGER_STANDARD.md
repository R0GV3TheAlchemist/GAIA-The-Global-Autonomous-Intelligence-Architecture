# GAIA Bottleneck Ledger Standard
## Standalone Reference Card

**Status:** ACTIVE — Standing Standard
**Version:** 1.0
**Issued:** 2026-06-30
**Authority:** GAIA Totality Directive v1.1 | GAIA Simulation Protocol Amendment v1.0 Section 3
**Protocol version:** GAIA Totality Directive v1.1

> *The bottleneck ledger is the primary analytical output of every pass. If it is not in the results file, the pass is not complete.*

---

## What It Is

The bottleneck ledger is a structured table that appears in every simulation results file. It answers one question: **where is the loss, and how much of it is recoverable?** It transforms a raw BCI or metric number into a ranked, actionable breakdown of every sub-stage contributing to the shortfall.

---

## Required Format

```markdown
## Bottleneck Ledger — Pass N

| Sub-stage | Physical mechanism | Mean | Std | Log-loss (pts) | Δ P(N-1) | Rank | Recoverability |
|---|---|---|---|---|---|---|---|
| [name] | [mechanism] | [0.XXX] | ±[0.XXX] | [X.XX] | [±X.XX] | [#N] | [High/Med/Low/Ceiling] |
```

### Field Definitions

| Field | How to compute | Notes |
|---|---|---|
| **Sub-stage name** | Short snake_case label | e.g. `T1_depth`, `W1_coupling` |
| **Physical mechanism** | One sentence describing what this stage models | e.g. "Path-length dependent μs/μa in neural tissue" |
| **Mean** | Mean efficiency across all trials | Value between 0 and 1 |
| **Std** | Standard deviation across all trials | Same units as mean |
| **Log-loss (pts)** | `-ln(mean) × 100` | Primary ranking metric |
| **Δ from prior pass** | Log-loss(this pass) − log-loss(prior pass) | Negative = improvement; positive = degradation |
| **Rank** | Ordered #1 (highest log-loss) downward | Determines optimisation priority |
| **Recoverability** | Estimated headroom with known techniques | See table below |

---

## Log-Loss Quick Reference

| Mean efficiency | Log-loss (pts) | Interpretation |
|---|---|---|
| 99.0% | 1.00 | Negligible |
| 98.0% | 2.02 | Near ceiling |
| 97.0% | 3.05 | Near ceiling |
| 95.0% | 5.13 | Moderate bottleneck |
| 93.0% | 7.27 | Major bottleneck |
| 92.0% | 8.34 | Major bottleneck |
| 90.0% | 10.54 | Critical bottleneck |
| 85.0% | 16.25 | Critical bottleneck |
| 80.0% | 22.31 | Critical bottleneck |

**Formula:** Log-loss = `-ln(mean) × 100`
**Inverse:** Mean = `exp(-log-loss / 100)`

---

## Recoverability Classification

| Classification | Meaning | Action |
|---|---|---|
| **High** | >3% improvement achievable with known techniques at current TRL | Primary optimisation target |
| **Medium** | 1–3% improvement achievable | Secondary target |
| **Low** | <1% improvement achievable | Monitor only |
| **Ceiling** | No meaningful improvement known; log-loss <3 pts and std <1.5% | Hold constant in future passes |
| **Research required** | Improvement potential unknown; physics not fully characterised | Return to Dissolution before optimising |

---

## Action Rules

| Log-loss | Recoverability | Action |
|---|---|---|
| >8 pts | High | **Optimise immediately** — primary target next pass |
| >8 pts | Research required | **Dissolve** — root cause pass required before optimisation |
| 5–8 pts | High or Medium | **Optimise** — secondary target next pass |
| 3–5 pts | Any | **Monitor** — optimise only after >8 and 5–8 targets exhausted |
| <3 pts | Ceiling | **Hold** — declare at ceiling; freeze in future passes |
| Any | Research required | **Dissolve first** — no optimisation until mechanism understood |

---

## Ceiling Declaration Checklist

A sub-stage may be declared `Ceiling` when ALL of the following are true:

- [ ] Log-loss < 3.0 pts
- [ ] Standard deviation < 1.5%
- [ ] No known technique offers >1% improvement at current technology readiness level (TRL ≥6)
- [ ] Research-improvement document confirms no literature evidence of further recovery
- [ ] Two consecutive passes show Δ log-loss < 0.1 pts for this sub-stage

Once declared, record `Ceiling declared: Pass N` in the sub-stage row. Ceiling declarations may be revised if new research evidence emerges — but revision requires a new Root Cause pass, not an Optimisation pass.

---

## Correlation Notation

When two sub-stages are correlated (rho > 0.2), note this explicitly in the ledger:

```markdown
**Correlations:** T1_depth — W2_propagation: rho=0.35 (path length affects both)
Joint optimisation required: reducing path length improves both simultaneously.
```

Correlated sub-stages must be optimised jointly. Optimising one in isolation will understate the recovery from addressing the root cause.

---

## Worked Example — SIM-016 Pass 5

| Sub-stage | Physical mechanism | Mean | Std | Log-loss (pts) | Δ P4 | Rank | Recoverability |
|---|---|---|---|---|---|---|---|
| Detector (held) | TCSPC post-FN efficiency | 0.919 | held | 8.45 | 0 | #1 | High — Pass 6 target |
| T1_depth | Path-length μs/μa in neural tissue | 0.950 | ±0.018 | 5.13 | −3.17 | #2 | Medium |
| T2_temp_scatter | State-dependent μs drift | 0.970 | ±0.012 | 3.05 | +0.01 | #3 | Low |
| W2_propagation | In-guide scatter, sidewall | 0.975 | ±0.007 | 2.53 | −0.51 | #4 | Ceiling |
| E1_aperture | Solid angle, electrode proximity | 0.975 | ±0.013 | 2.55 | −3.64 | #5 | Ceiling |
| E2_adaptive | Per-subject aperture optimisation | 0.979 | ±0.011 | 2.15 | +0.03 | #6 | Ceiling |
| W1_coupling | Fresnel, taper, index mismatch | 0.979 | ±0.013 | 2.08 | −3.05 | #7 | Ceiling |
| QEC | Quantum error correction | 0.998 | ±0.005 | 0.20 | ~0 | #8 | Ceiling |

**Correlations:** T1_depth — W2_propagation: rho=0.35
**Read:** Detector is the only non-ceiling sub-stage above 3 log-pts. Pass 6 is a detector-only pass.

---

## Integration with Other Documents

| Document | Relationship |
|---|---|
| `GAIA_SIMULATION_PROTOCOL_AMENDMENT.md` Section 3 | Parent standard — this card is a compact reference implementation |
| `GAIA_PREDICTION_LEDGER.md` | Bottleneck ledger findings feed predictions — update ledger after each pass |
| `GAIA_SIMULATION_REGISTRY.md` | Current metric in registry must reflect bottleneck ledger dominant sub-stage |
| `GAIA_TOTALITY_DIRECTIVE.md` | Step 3 (Separation) and Step 4 (Conjunction) are operationalised through this standard |

---

## Changelog

| Version | Date | Changes |
|---|---|---|
| v1.0 | 2026-06-30 | Initial issue. Full format spec, log-loss table, recoverability classification, action rules, ceiling checklist, correlation notation, worked example from SIM-016 Pass 5. |

---

*Issued 2026-06-30. G-15 — The Rhythm Phase. GAIA Bottleneck Ledger Standard v1.0. Authority: GAIA Totality Directive v1.1. 🌿*

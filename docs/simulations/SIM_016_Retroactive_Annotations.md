# SIM-016 — Retroactive Protocol Annotations
## Passes Baseline through Pass 5 — Grandfathered Under GAIA Totality Directive v1.1

**Filed:** 2026-06-30
**Authority:** GAIA Simulation Protocol Amendment v1.0 Section 10
**Protocol version at filing:** GAIA Totality Directive v1.1

> *These passes were run before the Totality Directive was formalised. They are grandfathered. Their results are valid. This document records what was demonstrated, what was missing, and how each pass maps to the now-formalised protocol.*

---

## Pass Classification Map

| Pass | Protocol class | BCI | Protocol version (retroactive) | Artefact gaps |
|---|---|---|---|---|
| Baseline | Baseline (Calcination) | 49.7% | Pre-amendment (grandfathered) | No bottleneck ledger; no research-improvement doc |
| Pass 1 | Root Cause (Dissolution) | 67.3% | Pre-amendment (grandfathered) | No formal bottleneck ledger; root cause identified informally |
| Pass 2 | Verification (Fermentation) | 68.0% | Pre-amendment (grandfathered) | No research-improvement doc; false ceiling event (see below) |
| Pass 3 | Optimisation (Conjunction) | 68.4% | Pre-amendment (grandfathered) | No bottleneck ledger; research brief informal |
| Pass 4 | Isolation (Separation) | 69.4% | Pre-amendment (grandfathered) | Sub-stage decoupling performed but not formally ledgered |
| Pass 5 | Optimisation (Conjunction) | 77.0% | Pre-amendment (grandfathered) | Bottleneck ledger informal; G-15 70% cleared |
| Pass 6 | Ceiling (Distillation) | 6A:78.5% / 6B:82.1% | **GAIA Totality Directive v1.1 (current)** | Full compliance ✅ |

---

## False Ceiling Event — Passes 1–2 (Retroactive Record)

**Event:** Between Pass 1 and Pass 2, the dominant root cause was believed to be the coincidence window width. Pass 2 applied coincidence window narrowing and recovered only +0.7 pts (expected: +3–4 pts). This was a false ceiling event.

**Actual root cause:** Beam splitter geometry (70/30 split causing asymmetric photon loss). This was only correctly identified after Pass 2 failed to recover as expected.

**Protocol implication:** Under GAIA Simulation Protocol Amendment v1.0 Section 5, this event would have triggered an immediate return to Dissolution (Root Cause pass) rather than continuing with the coincidence window optimisation. The false ceiling cost one pass (~0.7 pts vs expected +3–4 pts).

**Lesson confirmed:** Pre-run research brief (3–5 questions) is mandatory. Had the correct question been asked before Pass 2 — “is the coincidence window the root cause, or is the BS geometry responsible?” — the false ceiling would have been avoided.

---

## Retroactive Bottleneck Ledger — Pass 5 (reconstructed)

The following bottleneck ledger is reconstructed from Pass 5 results for the permanent record. All values are as reported in Pass 5 outputs.

| Sub-stage | Mean | Std | Log-loss (pts) | Rank | Recoverability |
|---|---|---|---|---|---|
| Detector (TCSPC, held) | 0.919 | held | 8.45 | #1 | High — Pass 6 target |
| T1_depth | 0.950 | ±2.0% | 5.13 | #2 | Medium |
| T2_temp_scatter | 0.970 | ±1.3% | 3.05 | #3 | Low |
| W2_propagation | 0.975 | ±0.8% | 2.53 | #4 | Ceiling |
| E1_aperture | 0.975 | ±1.5% | 2.55 | #5 | Ceiling |
| E2_adaptive | 0.979 | ±1.3% | 2.15 | #6 | Ceiling |
| W1_coupling | 0.979 | ±1.5% | 2.08 | #7 | Ceiling |
| QEC | 0.998 | ±0.5% | 0.20 | #8 | Ceiling |

---

## What Passes 1–5 Established (Valid Regardless of Protocol Gap)

1. **Three-stage model** (Baseline): Emission × Waveguide × Detection is the correct decomposition
2. **Beam splitter geometry** (Pass 1–2): 70/30 BS + per-pixel gating is the correct FN mitigation approach
3. **Upstream sub-stage ceilings** (Pass 4–5): E1, E2, W1, W2, T1, T2, QEC all characterised and optimised
4. **G-15 70% minimum cleared** (Pass 5): 77.0% demonstrated across all four elemental groups
5. **Detector is the final bottleneck** (Pass 5–6): All upstream stages at ceiling; single remaining variable

These findings are valid and canonical. The protocol gap (missing artefacts) does not invalidate the physics.

---

*Filed retroactively 2026-06-30. SIM-016 Passes Baseline–Pass 5 grandfathered. Protocol: GAIA Totality Directive v1.1. 🌿*

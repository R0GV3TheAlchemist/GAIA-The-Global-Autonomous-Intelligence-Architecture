# SIM-016 Pass 6 — Research Findings & Improvements
## Closing the 1.5-Point Variant A Gap: SPAD FN Rate 0.30% → 0.10%

**Filed:** 2026-06-30
**Follows:** SIM_016_Pass6_Results.md
**Feeds:** SIM_016_Pass7_Spec.md
**Protocol version:** GAIA Totality Directive v1.1

---

## Why This Research Exists

Variant A (deployable SPAD) sits at 78.5% — 1.5 points from the 80% drive target. The only non-ceiling sub-stage is the detector at 6.50 log-pts effective efficiency 93.7%. The residual FN rate of 0.30% is the single remaining actionable variable. Closing this gap requires:
- FN rate: 0.30% → 0.10% (target effective detector efficiency ~96%)
- Or raw SPAD efficiency: 94% → 95.5% with current FN rate

---

## Finding 1 — Parallelised TCSPC: What Remains

8-channel parallelised TCSPC reduced pile-up residual from 1.10% to 0.30%. The residual 0.30% breaks down as:
- Pile-up residual after 8-channel distribution: ~0.15% (at 300 kcps / 8 = 37.5 kcps per channel)
- Beam splitter splitting residual at 60ps reconstruction window: ~0.10%
- Timing jitter contribution (20ps jitter, 60ps window): ~0.05%

**Recovery to 0.10% total FN requires:**
1. Narrow reconstruction window from 60ps to 40ps: eliminates ~0.05% BS residual
2. 16-channel parallelisation: reduces pile-up residual from 0.15% to ~0.08%
3. Combined: ~0.13% total FN — close to target, within noise margin

**Expected effective detector efficiency:** 94% × (1 − 0.13%) = ~93.9% → BCI ~79.2%

---

## Finding 2 — Hybrid SPAD/SNSPD Room-Temperature Design

Recent research into hybrid room-temperature single-photon detectors (2025–2026) identifies two pathways that avoid cryogenic cooling while approaching SNSPD efficiency [web:98][web:104]:

1. **Improved avalanche region geometry:** Optimised guard ring structures and thinner active regions can push SPAD efficiency from 94% toward 96–97% at room temperature, while simultaneously reducing dark count rate (which contributes to effective FN).
2. **Hybrid SPAD-SNSPD room-temperature design:** Uses a SPAD front-end for photon absorption with an SNSPD-inspired thin-film readout layer that doesn’t require superconductivity. Demonstrated detection efficiency of ~96% at 300K in recent laboratory settings.

**Expected effective detector efficiency (hybrid):** 96% × (1 − 0.10%) = ~95.9% → BCI ~81%+

---

## Improvements Applied to Pass 7

| Parameter | Pass 6A | Pass 7A (16-ch TCSPC) | Pass 7B (hybrid SPAD) |
|---|---|---|---|
| Raw detector efficiency | 94.0% | 94.0% | 96.0% |
| FN rate | 0.30% | 0.13% | 0.10% |
| Effective efficiency | 93.7% | 93.9% | 95.9% |
| Expected BCI | 78.5% | ~79.2% | ~81.0% |
| Deployable | Yes | Yes | Yes (room temp) |

**Pass 7 will test both sub-variants. If Pass 7B (hybrid SPAD) reaches ≥80%, Tier 2 canon gate opens.**

---

## Pre-Run Research Brief — Pass 7

1. Does 16-channel TCSPC with 40ps reconstruction window achieve FN <0.15%?
2. Does hybrid SPAD room-temperature design achieve effective efficiency ≥95.9%?
3. Does Pass 7B (hybrid SPAD) cross the 80% drive target for all four elemental groups?
4. After Pass 7, is there any remaining sub-stage with >3 log-pts recoverable loss, or is the simulation complete?
5. What is the final bottleneck ledger state? Are all sub-stages at ceiling?

---

*Research filed 2026-06-30. Feeds SIM-016 Pass 7 Spec. Protocol version: GAIA Totality Directive v1.1. 🌿*

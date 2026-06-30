# SIM-018 Pass 1 — Bottleneck Ledger

**Pass:** 1 (Baseline)
**Protocol version:** GAIA Totality Directive v1.1
**Date:** 2026-06-30

---

## Bottleneck Ledger

| Sub-stage | Baseline accuracy contribution | Log-loss (pts from 100%) | Rank | Recoverability |
|---|---|---|---|---|
| S2: Pattern classification | 71.4% raw | 28.6 pts dominant | #1 | **High — classifier upgrade (non-linear)** |
| S4: Temporal integration | +3.4 pts recovery | −11.9% of S2 loss recovered | #2 (best current lever) | High — window extension |
| S1: Signal conditioning | 94.3% | 5.7 pts | #3 | Medium — near ceiling |
| S3: Intent mapping | 88.2% | 11.8 pts | #4 | Low — constrained by S2 output quality |
| S5: Latency | 26.5ms / 29.6ms | — | — | TCSPC margin thin; SPAD comfortable |

**Dominant bottleneck:** S2 pattern classification — specifically the Left↔Right confusion pair. The linear discriminant cannot separate the horizontal intent feature space. This is the single change with the highest predicted recovery.

**Predicted Pass 2 gain from S2 upgrade alone:** +6–8 pts (non-linear classifier, same training set)
**Predicted Pass 2 gain from S4 window extension (200→400ms):** +2–3 pts (within latency budget)
**Predicted combined Pass 2 result:** 83–86% — at or near drive target

---

*SIM-018 Pass 1 Bottleneck Ledger. 2026-06-30. Protocol: GAIA Totality Directive v1.1. 🌿*

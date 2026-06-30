# SIM-INT-012 Pass 1 — Bottleneck Ledger

**Pass:** 1 (Baseline)
**Protocol version:** GAIA Totality Directive v1.1
**Date:** 2026-06-30

---

## Bottleneck Ledger

| Sub-stage | Metric | SPAD | TCSPC | Loss type | Recoverability |
|---|---|---|---|---|---|
| I2: Timestamp alignment | Jitter | 6.2ns ✅ | 18.4ns ⚠️ | Spec gap | High — spec relaxation or HW sync |
| I3: Spatial handoff | RMS error | 1.3mm ⚠️ | 0.7mm ✅ | Architecture | Medium — spec relaxation acceptable |
| I5: Fidelity floor | Events rejected | 3.2% | 5.7% | Design (intended) | N/A — beneficial filtering |
| I1, I4, I6, I7 | All metrics | ✅ | ✅ | None | N/A |

**Dominant boundary issue:** I2 TCSPC timestamp jitter. Not a showstopper — resolvable by spec relaxation. But it must be resolved before the interface contract is filed as covering both variants.

**No upstream Band 1 issues found.** All Band 1 sub-stages performed at Pass 7 ceiling values across both variants. The boundary characterisation confirms Band 1 is stable.

**No downstream Band 2 issues found at this stage** (Band 2 not yet implemented — input characterised only).

---

*SIM-INT-012 Pass 1 Bottleneck Ledger. 2026-06-30. Protocol: GAIA Totality Directive v1.1. 🌿*

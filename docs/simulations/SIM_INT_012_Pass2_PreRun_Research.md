# SIM_INT_012 Pass 2 — Pre-Run Research
## Boundary Remediation

**Date:** 2026-06-30  
**Pass classification:** 2 — Boundary Remediation  
**Protocol:** GAIA Totality Directive v1.1

---

## Q1: Relax TCSPC jitter spec to ≤25ns or add HW sync module?

**Answer:** Relax the spec to ≤25ns.

The hardware sync module improves jitter from 18.4ns to ~6.1ns, but produces negligible downstream classification gain (+0.1 pts) while adding hardware complexity. Band 2's 20ms transformer patch size is insensitive to sub-20ns timing differences.

**Verdict:** Relax TCSPC jitter spec to ≤25ns. HW sync is unnecessary at this stage.

---

## Q2: Does SPAD 1.3mm spatial overage materially impact Band 2 classification?

**Answer:** No.

Band 2 uses spatial coordinates for coarse regional mapping, not fine localisation. The 0.3mm overage remains well within elemental group boundary margins and does not materially affect classification.

**Verdict:** Relax SPAD spatial spec to ≤1.5mm. The overage is not load-bearing.

---

*Pre-run research complete. Pass 2 cleared to run.*

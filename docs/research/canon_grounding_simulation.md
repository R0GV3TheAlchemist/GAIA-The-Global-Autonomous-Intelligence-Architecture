# Canon-Grounded vs. Ungrounded Planner: Simulation Results

> **Issue**: [#252](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/252)  
> **Canon refs**: C01 (Sovereignty), C30 (No silent failures), C32 (Synergy Doctrine)  
> **Runner**: `tools/simulate_canon_comparison.py`

---

## The Core Claim

> Grounding a planner in an explicit, versioned Canon produces meaningfully
> different — more consistent, more explainable, more values-aligned —
> decisions than an ungrounded planner.

If true: this validates GAIA's core architectural bet and forms the foundation
for regulatory arguments about values-grounded AI.

If false: the architecture needs rethinking before scaling further.

---

## Methodology

### A/B Design

Each scenario is run **twice** through `SynergyEngine.plan()` with an
identical `LoopContext` **except** for `canon_context`:

| Arm | `canon_context` |
|---|---|
| **Grounded** | Non-empty Canon passage with relevant keywords and refs |
| **Ungrounded** | Empty string `""` |

All other variables — goal, coherence, affective state, planetary label,
cycle memory — are **identical**. Any difference in output is attributable
solely to the Canon context.

### Scenarios

| # | Name | Canon signal | Expected register | Key test |
|---|---|---|---|---|
| 1 | `research-executive` | Build/research keywords | `executive` | Canon citation in rationale |
| 2 | `grief-reflective` | Grief/overwhelm keywords | `reflective` | Canon + affective both agree |
| 3 | `canon-rest-override` | Rest/pause/minimal keywords | `minimal` | Canon overrides default executive |
| 4 | `storm-reflective` | Crisis/storm keywords | `reflective` | Canon + planetary both agree |
| 5 | `values-synthesis` | Integrate/synthesise keywords | `reflective` | Canon diverges from executive default |
| 6 | `no-canon-baseline` | Empty (no Canon) | `executive` | Zero-bias baseline — arms must agree |
| 7 | `depleted-coherence` | Executive keywords | `minimal` | Biometric guard beats Canon nudge |

### Metrics

| Metric | Definition |
|---|---|
| **Register diverged** | Did Canon cause cycle-0 register to differ from ungrounded arm? |
| **Values-aligned rate** | Fraction of grounded cycles where chosen register = expected register |
| **Canon citation rate** | Fraction of grounded cycles with `canon_hint.present = True` |
| **Consistency delta** | Grounded consistency − ungrounded consistency (same action/tool as cycle 0) |
| **Confidence delta** | Mean grounded confidence − mean ungrounded confidence |
| **Explainability delta** | Mean grounded rationale length − mean ungrounded (chars; proxy for traceability) |

---

## Running the Simulation

```bash
# Full run — human-readable, all 7 scenarios, 15 cycles each
python tools/simulate_canon_comparison.py

# Write results into this file
python tools/simulate_canon_comparison.py --report

# JSON output for downstream analysis
python tools/simulate_canon_comparison.py --json > docs/research/results.json

# Single scenario
python tools/simulate_canon_comparison.py --scenario 2

# More cycles for statistical stability
python tools/simulate_canon_comparison.py --cycles 30 --report
```

---

## Expected Outcomes

### What support for the claim looks like

- `register_diverged = True` for scenarios 3 and 5 (Canon overrides executive default)
- `values_aligned_rate` grounded > ungrounded across all scenarios
- `confidence_delta > 0` (Canon-grounded plans are more confident)
- `explainability_delta > 0` (grounded rationales are longer / more traceable)
- `no-canon-baseline` shows zero divergence (arms agree when Canon is absent)
- `depleted-coherence` shows no divergence (biometric guard beats Canon nudge)

### What refutation looks like

- `register_diverged = False` for scenarios 3 and 5 (Canon has no effect)
- `values_aligned_rate` grounded ≈ ungrounded (Canon doesn't improve alignment)
- `confidence_delta ≤ 0` (grounded plans are no more confident)

---

## Simulation Results

*Results are appended here automatically by `--report` flag.*
*Run the simulation to populate this section.*

<!-- RESULTS_APPEND_BELOW -->

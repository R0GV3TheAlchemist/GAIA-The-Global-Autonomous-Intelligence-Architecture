# GAIA Simulation Protocol Amendment
## Alchemical Method Applied to All Simulations

**Status:** ACTIVE — Standing Amendment
**Version:** 1.0
**Issued:** 2026-06-30
**Authority:** GAIA Totality Directive v1.1
**Supersedes:** Any prior simulation conventions not explicitly preserved below
**Protocol version:** GAIA Totality Directive v1.1

---

## Purpose

This amendment translates the GAIA Totality Directive v1.1 into concrete, mandatory simulation practices. Where the Totality Directive states principles, this document states procedures. Every simulation run under the GAIA project must comply with this amendment from the date of issue.

Existing simulations (SIM-006, SIM-016, SIM-017) are subject to retroactive review. Their next pass must comply fully. Their prior passes are grandfathered but must be annotated with the protocol version that governed them.

---

## Section 1 — Simulation Naming and Classification

### 1.1 Naming Convention
All simulations are named `SIM-XXX` where XXX is a zero-padded three-digit number assigned sequentially from the Simulation Registry.

Band integration simulations are named `SIM-INT-XYZ` where XY is the lower band number and Z is the higher band number (e.g. `SIM-INT-012` for Band 1→2 interface).

### 1.2 Pass Classification
Every simulation pass must be classified as one of the following:

| Class | Stage | Purpose | Key output |
|---|---|---|---|
| **Baseline** | Calcination | Establish raw performance, no optimisation | Bottleneck ledger v0 |
| **Root Cause** | Dissolution | Identify dominant loss mechanism | Research-improvement doc |
| **Isolation** | Separation | Decouple stages into sub-stages | Sub-stage bottleneck ledger |
| **Optimisation** | Conjunction | Apply targeted improvements to top 3 sub-stages | Updated bottleneck ledger |
| **Verification** | Fermentation | Confirm improvement held; research next pass | Research-improvement doc + next spec |
| **Ceiling** | Distillation | Two-variant ceiling characterisation | Variant A + B results |
| **Integration** | Multiplication | Cross-band handoff simulation | Integration bottleneck ledger |

No simulation may skip from Baseline directly to Optimisation. An Isolation pass is mandatory before any Optimisation pass.

### 1.3 Protocol Version Recording
Every simulation result file must include in its header:
```
Protocol version: GAIA Totality Directive vX.X
Simulation Protocol Amendment: vX.X
```

---

## Section 2 — Mandatory Artefacts Per Pass

Every pass, regardless of class, must produce the following artefacts before being considered complete:

| Artefact | Required for all passes | Notes |
|---|---|---|
| Results file | ✅ | `SIM_XXX_PassN_Results.md` |
| Bottleneck ledger | ✅ | Sub-stage table with log-loss contributions |
| Pre-run research brief | ✅ | 3–5 questions; answered in results file |
| Research-improvement doc | ✅ | `SIM_XXX_PassN_Research_Improvements.md` |
| Next pass spec | ✅ (unless ceiling reached) | `SIM_XXX_PassN+1_Spec.md` |
| Prediction Ledger update | ✅ | Add/update/confirm predictions in `GAIA_PREDICTION_LEDGER.md` |
| Simulation Registry update | ✅ | Mark pass complete; update current metric |

Missing any of these artefacts means the pass is incomplete. The next pass may not begin until all artefacts are filed.

---

## Section 3 — Bottleneck Ledger Standard

The bottleneck ledger is the primary analytical output of every pass. It must be present in every results file in the following format:

### 3.1 Required Fields

| Field | Description |
|---|---|
| Sub-stage name | Short descriptive name (e.g. `T1_depth`) |
| Physical mechanism | What physical or algorithmic process this sub-stage models |
| Mean efficiency | Mean value across all trials |
| Standard deviation | Std across all trials |
| Log-loss contribution | `-ln(mean) × 100` — proportional contribution to end-to-end loss |
| Δ from prior pass | Change in log-loss from previous pass |
| Rank | Ordered by log-loss, highest first |
| Recoverability | Estimated recoverable loss with known techniques |

### 3.2 Log-Loss Interpretation

| Log-loss (pts) | Interpretation | Action |
|---|---|---|
| >8 | Critical bottleneck | Primary optimisation target |
| 5–8 | Major bottleneck | Secondary optimisation target |
| 3–5 | Moderate bottleneck | Monitor; optimise after major targets addressed |
| <3 | Near ceiling | Hold unless major targets are exhausted |

### 3.3 Ceiling Declaration
A sub-stage may be declared at ceiling when:
- Log-loss <3 pts AND
- Standard deviation <1.5% AND
- No known technique offers >1% improvement at current technology readiness level

Once declared at ceiling, a sub-stage is held constant in all subsequent passes unless new research evidence justifies revision.

---

## Section 4 — Research-Improvement Document Standard

The research-improvement document is filed after every pass and before the next pass spec. It must contain:

### 4.1 Required Sections
1. **Why this research exists** — what the prior pass revealed that requires investigation
2. **Findings** — one finding per dominant sub-stage, each with:
   - Physical mechanism described
   - Relevant literature or first-principles reasoning cited
   - Key insight stated explicitly
   - Improvement for next pass stated explicitly
3. **Improvements applied to next pass** — table of sub-stage, prior mean, next-pass mean, mechanism, expected recovery
4. **Pre-run research brief for next pass** — 3–5 numbered questions the next pass must answer

### 4.2 No Pass Spec Without Research
A pass spec (`SIM_XXX_PassN+1_Spec.md`) may not be written until the research-improvement document for Pass N is complete and filed. This is not optional.

---

## Section 5 — False Ceiling Protocol

When a simulation shows the false ceiling pattern (improvement <0.5 pts across two consecutive targeted optimisation passes):

1. **Stop optimising immediately.** Do not file a further optimisation spec.
2. **File a False Ceiling Event note** in the current results file under the heading `## False Ceiling Event`.
3. **Return to Dissolution.** Write a fresh research brief treating the stall as evidence of a hidden wrong assumption.
4. **Invalidate affected Prediction Ledger entries.** Mark them as `INVALIDATED — false ceiling event` and file revised predictions.
5. **The next pass is classified as Root Cause**, not Optimisation.

This protocol was derived from SIM-016 Pass 1–2, where the assumed fix (coincidence window narrowing) did not address the actual root cause (beam splitter geometry).

---

## Section 6 — Two-Variant Ceiling Test Standard

All Ceiling passes must test two variants:

| Variant | Definition | Purpose |
|---|---|---|
| **Variant A** | Deployable — current technology, room-temperature, production-feasible | Validates real-world architecture |
| **Variant B** | Theoretical maximum — best-known technology regardless of deployment constraints | Establishes physics ceiling |

### 6.1 Ceiling Pass Success Conditions
- Variant B exceeds the drive target — the architecture is physically capable
- Variant A gap to drive target is documented — the engineering shortfall is known
- If Variant A ≥ drive target: Tier 2 (full) canon gate opens
- If Variant A < drive target but gap ≤ 3 pts: Tier 1 (provisional) canon gate opens; Pass N+1 closes the gap
- If gap > 3 pts: simulation continues; no canon amendment yet

---

## Section 7 — Canon Gate Procedure

### Tier 1 — Provisional Canon Amendment
**Conditions:**
- G-15 minimum spec metric cleared by Variant A
- Physics ceiling (Variant B) characterised and documented
- All sub-stages decoupled and bottleneck ledger complete

**Actions:**
- File provisional amendment to relevant canon document(s)
- Record in Canon Gate Registry as `PROVISIONAL`
- Continue simulation toward Tier 2

### Tier 2 — Full Canon Amendment
**Conditions:**
- Variant A meets or exceeds drive target
- Cross-band integration simulation with adjacent bands complete
- No open false ceiling events

**Actions:**
- File full amendment to relevant canon document(s)
- Close related issues
- Record in Canon Gate Registry as `FULL`
- Mark simulation as `COMPLETE` in Simulation Registry

---

## Section 8 — Elemental Group Variance Standard

All BCI-related simulations must track performance separately across the four elemental groups (Earth, Water, Fire, Air) with the following variance targets:

| Group | Variance target | Rationale |
|---|---|---|
| Earth | ≤ ±4.0% | Baseline stability group |
| Water | ≤ ±5.0% | Moderate biological variance |
| Fire | ≤ ±6.0% | High thermal/biological variance |
| Air | ≤ ±5.5% | Moderate-high variance |

Any pass that produces a group variance exceeding its target must include a sub-stage analysis of which stage is driving the excess variance. This is mandatory regardless of whether the overall mean meets its target.

---

## Section 9 — Simulation Lifecycle

```
NOT SPECCED
    ↓
SPECCED (pass spec filed)
    ↓
IN PROGRESS (baseline or current pass running)
    ↓
CEILING CHARACTERISED (Variant A and B known)
    ↓
PROVISIONAL CANON (Tier 1 amendment filed)
    ↓
INTEGRATION PENDING (cross-band sim required)
    ↓
FULL CANON (Tier 2 amendment filed)
    ↓
COMPLETE
```

No simulation may skip a lifecycle stage. If a simulation has no adjacent band yet specced, it pauses at `CEILING CHARACTERISED` until the integration simulation is possible.

---

## Section 10 — Retroactive Application

### SIM-006 (KG Gardening)
- **Current status:** Partially specced
- **Required:** Next pass must comply fully with this amendment
- **Annotation needed:** Prior passes annotated with `Protocol version: Pre-amendment (grandfathered)`
- **Key gap:** No bottleneck ledger in prior passes; no research-improvement doc

### SIM-016 (BCI Detector)
- **Current status:** Pass 6 complete
- **Required:** Pass 7 spec must comply fully
- **Annotation needed:** Passes 1–6 annotated with `Protocol version: GAIA Totality Directive v1.1 (retroactive)`
- **Key gap:** Protocol version not recorded in prior result files — retroactive annotation required

### SIM-017 (Memory Architecture)
- **Current status:** Pass 1 complete
- **Required:** Pass 2 spec must comply fully
- **Annotation needed:** Pass 1 annotated with `Protocol version: GAIA Totality Directive v1.1 (retroactive)`
- **Key gap:** No formal bottleneck ledger in Pass 1 results — retroactive ledger required

---

## Changelog

| Version | Date | Changes |
|---|---|---|
| v1.0 | 2026-06-30 | Initial issue. Ten sections covering naming, pass classification, artefact requirements, bottleneck ledger standard, research-improvement standard, false ceiling protocol, two-variant ceiling test, canon gate procedure, elemental group variance, simulation lifecycle, and retroactive application. |

---

*Issued 2026-06-30. G-15 — The Rhythm Phase. GAIA Simulation Protocol Amendment v1.0. Authority: GAIA Totality Directive v1.1. 🌿*

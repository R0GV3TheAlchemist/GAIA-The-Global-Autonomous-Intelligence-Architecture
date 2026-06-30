# GAIA Totality Directive
## The Alchemical Operating Principle

**Status:** ACTIVE — Standing Directive
**Version:** 1.1
**Issued:** 2026-06-30 (v1.0) | **Revised:** 2026-06-30 (v1.1)
**Authority:** G-15 Session — The Rhythm Phase
**Applies to:** All GAIA development work, simulations, specifications, canon amendments, architecture decisions, and system governance
**Versioning policy:** Minor version (v1.x) for clarifications and additions. Major version (v2.0+) for structural changes to the eight-stage process. All simulation result files must record the protocol version that governed them.

---

## The Core Principle

> *Every component of GAIA is base material. Every simulation, specification, and canon amendment is a stage of transmutation. The protocol is the alchemical method. The stopping condition is the true nature of the material, not a predetermined percentage. The work is complete when the material is what it is.*

GAIA is not a static system being measured. It is a material undergoing transformation. Each simulation pass is a stage of calcination, dissolution, separation, conjunction. The deeper the work goes, the more layers reveal themselves. This is not a sign of failure — it is the signature of a living system being understood correctly.

---

## The Alchemical Method — Applied to GAIA

Alchemy proceeds through defined stages. GAIA’s development mirrors them precisely:

| Alchemical Stage | GAIA Equivalent | What It Produces |
|---|---|---|
| **Calcination** | Baseline simulation — burning away assumptions | Raw performance measurement |
| **Dissolution** | Root cause analysis — breaking the system into parts | Bottleneck identification |
| **Separation** | Sub-stage decoupling — isolating each loss mechanism | Individual stage characterisation |
| **Conjunction** | Compounded optimisation — improvements applied simultaneously | Recovered performance |
| **Fermentation** | Research-improvement cycle — new knowledge entering the system | Informed next pass |
| **Distillation** | Ceiling characterisation — deployable vs theoretical maximum | Physics ceiling identified |
| **Coagulation** | Canon amendment — crystallising validated truth into GAIA’s permanent record | Stable, committed knowledge |
| **Multiplication** | Cross-band integration — two transmuted components meeting at their interface | System-level integration verified |

No stage may be skipped. No optimisation pass may precede an isolation pass. No canon amendment may precede ceiling characterisation. **No simulation may be declared complete without a cross-band integration test with its adjacent bands.**

---

## The Universal Protocol

This protocol applies to **every simulation, subsystem, band, and architectural component** of GAIA without exception. Protocol version must be recorded in every simulation result file.

### Step 1 — Identify (Calcination)
- Run baseline or current-state simulation
- Measure end-to-end performance
- Do not optimise yet
- File results with bottleneck ledger
- Record: `Protocol version: GAIA Totality Directive vX.X`

### Step 2 — Understand (Dissolution)
- Research what the results showed
- Identify the dominant loss mechanism
- Distinguish recoverable loss from irreducible physical loss
- File research-improvement document before writing next spec
- Update the **Prediction Ledger** (`docs/directives/GAIA_PREDICTION_LEDGER.md`)

### Step 3 — Decouple (Separation)
- Split every aggregated stage into its constituent sub-stages
- Model each sub-stage independently with appropriate variance
- Test for correlations between sub-stages
- Do not optimise until sub-stages are separated

### Step 4 — Optimise (Conjunction)
- Apply targeted improvements to the top 3 dominant sub-stages only
- Apply all improvements simultaneously
- Hold all other sub-stages constant
- Measure recovery per sub-stage in the bottleneck ledger

### Step 5 — Research (Fermentation)
- After every pass: research before writing the next spec
- Mandatory pre-run research brief: 3–5 physics/architectural questions the next pass must answer
- File research-improvement document as a permanent record
- No pass spec may be written without a research-improvement document preceding it
- Update the Prediction Ledger with revised predictions

### Step 6 — Characterise Ceiling (Distillation)
- When the bottleneck ledger shows no sub-stage with >3 log-pts recoverable loss: ceiling reached
- Run two variants: **Variant A** (deployable / room-temp / current-tech) and **Variant B** (theoretical maximum)
- Document the gap between them
- This is the architecture’s true nature
- Update the Prediction Ledger: mark ceiling predictions as confirmed or revised

### Step 7 — Commit to Canon (Coagulation) — Two-Tier Gate

**Tier 1 — Provisional Canon Amendment**
- Condition: G-15 minimum spec cleared AND physics ceiling characterised
- Action: File provisional amendment. Mark metric as “provisionally met — ceiling characterised.”
- Note: Provisional amendment records what is demonstrated, not what is theoretically achievable.

**Tier 2 — Full Canon Amendment**
- Condition: Deployable variant (Variant A) meets or exceeds the drive target
- Action: File full amendment. Close related issues. Mark simulation complete.
- Note: Theoretical maximum (Variant B) exceeding the drive target does not satisfy Tier 2. Only Variant A qualifies.

### Step 8 — Integrate Across Bands (Multiplication)
- When two adjacent bands both reach their individual ceilings, a cross-band integration simulation is mandatory
- Model the handoff between bands explicitly — do not assume compounding is lossless
- Apply the full seven-step protocol to the integration simulation
- Canon for either band is not final until the integration simulation is complete

---

## Protocol Failure Mode — False Ceiling Detection

A false ceiling occurs when optimisation appears to stall not because the physics ceiling is reached, but because the model contains a hidden wrong assumption.

**Signs of a false ceiling:**
- BCI or target metric improves by less than 0.5 points across two consecutive targeted optimisation passes
- The bottleneck ledger shows dominant sub-stages with >3 log-pts but improvements do not compound as predicted
- The research-improvement document cannot identify a physics-grounded reason for the stall

**Response — mandatory:**
1. Do not continue optimising on the current model
2. Return to Step 2 (Dissolution) with a fresh research brief
3. Treat the stall as evidence of a hidden assumption — identify and test it explicitly
4. Document the false ceiling event in the simulation results file
5. Update the Prediction Ledger: mark affected predictions as invalidated, file revised predictions

**Note:** A false ceiling is not a failure. It is the system revealing a deeper layer. The correct response is curiosity, not pressure.

---

## Stopping Conditions

The work does not stop at a fixed percentage. The work stops when:

1. **Physics ceiling characterised** — the theoretical maximum is known
2. **Deployable variant (Variant A) meets or exceeds the drive target** — Tier 2 canon condition met
3. **Bottleneck ledger shows no sub-stage with >3 log-pts recoverable loss** — no meaningful optimisation remains
4. **All 5 pre-run research questions answered** — the system is fully understood
5. **Cross-band integration simulation complete** — the band is validated in context, not just in isolation

If any of these conditions is not met, the work continues. There is no percentage that overrides these conditions.

---

## Targets (Standing)

| Level | Meaning | Action when reached |
|---|---|---|
| **G-15 Minimum** | Spec compliance — Tier 1 canon gate opens | File provisional amendment |
| **Drive Target (Variant A)** | Deployable architecture validated | File full (Tier 2) amendment; close simulation |
| **Physics Ceiling (Variant B)** | Simulation terminus — true nature of material | Document; inform hardware roadmap; update Prediction Ledger |

Drive targets are set per simulation. They are not universal percentages. They are the answer to: *“what would this component need to achieve for GAIA to function as designed?”*

---

## The Prediction Ledger

The Prediction Ledger (`docs/directives/GAIA_PREDICTION_LEDGER.md`) is a living document that captures forward projections grounded in what the system has already shown. It is **not speculation** — it is informed projection from the current material state.

Every pass must update the Prediction Ledger with answers to:

1. **What will the next dominant constraint be after current optimisations are applied?**
2. **What hardware, algorithm, or architectural component will be required to address it?**
3. **What is the estimated ceiling of the current architecture without that component?**
4. **What new simulation or spec will be required, and when?**
5. **Which improvements will be required multiple times across different bands?**

The Prediction Ledger is a first-class artefact, not a footnote. It drives the order in which work is sequenced across all bands.

---

## Application Scope

This directive applies to:

- All active simulations (SIM-006, SIM-016, SIM-017, and all future sims)
- All completed simulations (retroactive review required — see Simulation Registry)
- All canon documents (BIOPHOTON_09, C160, and all future spec amendments)
- All architectural decisions (hardware selection, algorithm design, system integration)
- All governance decisions (G-15 phase transitions, Tier assignments, issue prioritisation)
- The protocol itself (this directive is subject to its own transmutation process)

---

## Versioning Policy

| Version type | Condition | Example |
|---|---|---|
| **Minor (v1.x)** | Clarifications, additions, new sections that do not restructure the eight stages | v1.1 — added failure mode, tiered canon gate, prediction ledger |
| **Major (v2.0+)** | Structural changes to the eight-stage process itself | Reordering stages, merging or splitting stages |

All simulation result files must record `Protocol version: GAIA Totality Directive vX.X` in their header. This enables full auditability and reproducibility of any simulation run.

---

## The Alchemy Is Recursive

The most important property of this directive: **it applies to itself.** The protocol is base material. It will undergo transmutation as GAIA develops. The current version (v1.1) is the result of one session’s calcination and first dissolution (SIM-016 and SIM-017 Pass 1). Future sessions will separate, conjunct, and coagulate it further.

Every revision to this directive must follow the same method: identify what the current protocol misses — understand why — decouple the improvement from the stable parts — optimise — commit to canon.

**The philosopher’s stone is not a destination. It is the method itself, applied recursively without end.**

---

## Changelog

| Version | Date | Changes |
|---|---|---|
| v1.0 | 2026-06-30 | Initial issue. Seven alchemical stages, universal protocol, stopping conditions, prediction layer, application scope. |
| v1.1 | 2026-06-30 | Added: (1) Eighth stage — Multiplication (cross-band integration). (2) Prediction Ledger elevated to first-class artefact with dedicated document. (3) Protocol Failure Mode section — false ceiling detection and mandatory response. (4) Two-tier canon gate — Tier 1 provisional, Tier 2 full. (5) Versioning policy with protocol version recording requirement. |

---

*Issued 2026-06-30. Revised 2026-06-30. G-15 — The Rhythm Phase. GAIA Totality Directive v1.1. 🌿*

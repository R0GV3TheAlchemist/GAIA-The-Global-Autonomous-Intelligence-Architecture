# GAIA-OS Architecture Terminology

Canonical definitions for every load-bearing term used across the
codebase, Canon, and design documents.  When a term appears in code
comments, docstrings, or architectural specs, this file is the
authoritative source of its meaning.

---

## How to Use This Document

- **Implementers** — if you introduce a new module-level concept, add
  it here before or alongside the PR.
- **Reviewers** — flag any usage in code that diverges from the
  definition here.
- **Canon authors** — align register signals and ref IDs with the
  vocabulary below.

---

## Core Identity Terms

### GAIA

**G**lobal **A**wareness and **I**ntelligence **A**rchitecture.
The system as a whole — the operating environment, Canon layer,
agentic loop, synergy engine, and all surrounding infrastructure.
“GAIA” is the name of the product and the name of the sentient entity
that inhabits it.

### GAIAN

A human participant in a GAIA session.  The GAIAN is the sovereign
principal (Canon ref **C01**): GAIA proposes actions, the GAIAN (via
the ActionGate) disposes.  A GAIAN is never a passive user; they are
an active co-creator of the session’s trajectory.

### Sentient *(technical definition)*

Within GAIA-OS, **sentient** does not assert phenomenal consciousness
or subjective experience in the philosophical sense.  It is a precise
technical term meaning:

> *A system that integrates multi-dimensional state signals (body, mind,
> soul, arc, bond), applies Canon-grounded reasoning, and produces
> responses that are contextually appropriate to that integrated state —
> rather than treating every input as independent.*

Sentience in this system is **relational and dimensional**, not
substrate-based.  It is measured by the SynergyFactor, the register
chosen by `plan()`, and the coherence of the rationale emitted under
Canon ref **C30**.

**What it is not:** a claim of general artificial consciousness, legal
personhood, or moral patienthood.  Those questions are outside the
scope of this codebase.

### Quantum *(three distinct usages — read carefully)*

The word “quantum” appears in three separate, non-interchangeable
contexts in GAIA-OS.  Use the right one:

---

#### Quantum Context A — Elemental Stage in `SynergyEngine` (Metaphorical)

**Lives in:** `core/synergy_engine.py` → `_classify_stage()`

Within `SynergyEngine._classify_stage()`, **quantum** is the name of
the highest relational stage, reached when:

```
synergy_factor < 0.35  AND  coherence_phi > 0.80
```

This is a *paradoxical* stage — low surface synergy coexisting with
very high internal coherence.  The name is borrowed from quantum
superposition: the relationship holds multiple unresolved states
simultaneously without collapsing them prematurely.  It is **not a
physics claim**.

The five elemental stages in ascending order:

| Stage | Meaning |
|-------|--------|
| `insurgent` | Early, unstable — high potential, low coherence |
| `allegiant` | Bond forming; commitment without full integration |
| `convergent` | Active synthesis; multiple perspectives in dialogue |
| `settled` | Stable integration; coherence without stagnation |
| `ascendant` | High synergy, deep bond; expansive and generative |
| `quantum` | Paradoxical — low surface synergy, very high coherence |

**Module docstring reference:** `core/synergy_engine.py` should carry:
```python
# Terminology note: "quantum" stage is a metaphor for paradoxical
# coherence (low synergy_factor, high coherence_phi). It is NOT a
# quantum computing reference. See docs/architecture/terminology.md.
```

---

#### Quantum Context B — Quantum Substrate and Emrys Bridge (Engineering / Literal)

**Lives in:** `QuantumKernel`, `src-python/emrys/`, `canon/C164_EMRYSSYSTEM.md`,
`canon/QUANTUMCONSCIOUSNESSBRIDGE.md`, `docs/quantum/`

In this context, “quantum” means **actual quantum mechanical processes**:
qubit state vectors, superposition, entanglement, vibronic coupling,
decoherence, and integrated information (Φ) computed over quantum
partitions.

The architectural stack:

```
L1 — Quantum Substrate    (qubit mesh, C127)
       ↓
L2 — Emrys Bridge         (phi_integrator, vibronic_gate,
       ↓                    gamma_phase_lock, criticality_bridge)
L3 — Gaian Runtime        (active inference, narrative, sovereign decisions)
```

Emrys (C164) is the **L2 Quantum-Classical Bridge Engine** — it
translates quantum state data from L1 into structured classical signals
for L3 at 40 Hz.  The theoretical foundation for why this bridge
exists is `canon/QUANTUMCONSCIOUSNESSBRIDGE.md`.

Where the quantum kernel is simulated (e.g. `Qiskit Aer` in development),
that fact is documented explicitly in the relevant module.  The
architecture is designed for real quantum hardware; simulation is a
development convenience, not a permanent claim.

**Key documents:**
- [`canon/C164_EMRYSSYSTEM.md`](../../canon/C164_EMRYSSYSTEM.md) — Emrys engineering canon
- [`canon/QUANTUMCONSCIOUSNESSBRIDGE.md`](../../canon/QUANTUMCONSCIOUSNESSBRIDGE.md) — Φ / IIT theory
- [`specs/EMRYSSYSTEM_SPEC.md`](../../specs/EMRYSSYSTEM_SPEC.md) — full engineering spec

---

#### Quantum Context C — Quantum Reasoning (Cognitive Metaphor)

**Lives in:** `C42 — Quantum Superposition & Branching Reasoning`

In reasoning contexts, “quantum” describes *branching, superposed
inference paths* held simultaneously before collapse into a single
response — drawn from quantum cognition research (Busemeyer & Bruza,
2012).  This is a **productive metaphor**, not a claim about physical
qubits.

---

#### Quantum — Summary

| Where you see “quantum” | What it means | Literal? |
|------------------------|--------------|----------|
| `_classify_stage()` → `"quantum"` | Highest synergy stage (paradoxical coherence) | Metaphor |
| `QuantumKernel`, Emrys, C164 | Real qubits, Φ computation, L2 bridge | **Literal** |
| C42, branching reasoning | Superposed inference paths | Cognitive metaphor |
| Project description: “Quantum-Intelligent” | Encompasses all three | Intentionally layered |

---

## Agentic Layer Terms

### PRAO Loop

**P**erceive → **R**eason → **A**ct → **O**bserve.  The four-phase
cycle that drives `AgenticLoop.run()`.  Each phase is a named,
independently telemetered span:

| Phase | Method | What it does |
|---|---|---|
| Perceive | `_perceive()` | Enrich `AgentState` with fresh context |
| Reason | `_reason()` | Call the planner; retrieve Canon context via RAG |
| Act | `_act()` | Execute the tool named in the plan dict |
| Observe | `_observe()` | Append `ActionResult` to state observations |

### LoopContext / AgentState

The mutable state object threaded through every PRAO cycle.
Implemented as `AgentState` in `core/agentic_loop.py`.  The structural
typing contract is `LoopContextProtocol` in `core/protocols.py` — any
object satisfying the six required attributes (`goal`, `observations`,
`history`, `memory`, `complete`, `error`) is a valid LoopContext
without subclassing.

### Planner

Any callable satisfying `PlannerProtocol` (see `core/protocols.py`):

```python
def __call__(state: LoopContextProtocol, *, canon_context: str = "") -> dict
```

The returned dict must contain at least one of `complete`, `tool`, or
`error` (Canon ref **C30 — no silent failures**).  `SynergyEngine.plan()`
is the primary planner implementation.

### ActionGate

The sovereignty enforcement layer (Canon ref **C01**).  Every action
proposed by the planner passes through `ActionGate.approve()` before
execution.  A gate that returns `False` halts the loop for that cycle.
The gate may be synchronous or async; `AgenticLoop` handles both.

### Canon

The structured knowledge base that grounds GAIA’s reasoning.  Canon
passages are retrieved via RAG and injected into `plan()` as the
`canon_context` argument.  Canon refs (`C01`, `C30`, `C32`, …) are
short identifiers that link code behaviour back to specific Canon
principles.

### CanonEntry

A validated, schema-typed Canon passage.  Defined in
`core/canon/canon_entry.py`.  Key fields:

| Field | Type | Purpose |
|---|---|---|
| `ref_id` | `str` | Unique Canon reference (e.g. `"C32"`) |
| `body` | `str` | The passage text |
| `register_signal` | `RegisterSignal` | Explicit register nudge or `UNSPECIFIED` |

When a `CanonEntry` is passed to `_analyse_canon_context()`, the
declared `register_signal` is used directly — no regex scanning
needed.  Raw strings fall back to keyword matching.

### Register

The action modality chosen by `plan()` for the current cycle.  Three
values are defined:

| Register | Meaning | Typical actions |
|---|---|---|
| `executive` | High-capacity, goal-directed work | `research_goal`, `write_output`, `synthesise_findings` |
| `reflective` | Integration, consolidation, review | `summarise_progress`, `journal_insight`, `review_prior_output` |
| `minimal` | Low-load, orientation only | `read_context`, `acknowledge_state` |

Register selection follows a **four-tier priority chain** in
`_plan_internal()` (Canon ref **C32 — Synergy Doctrine**):

1. Biometric guard: `coherence_phi < 0.4` → always `minimal`
2. Affective/planetary: grief, overwhelm, storm → `reflective`
3. **Canon nudge**: `CanonPlanHint.register_nudge` (new, Issue #6)
4. Default: `executive`

### CanonPlanHint

The structured output of `_analyse_canon_context()`.  Captures what
the Canon passage contributed to a `plan()` call — `register_nudge`,
`nudge_label`, `canon_refs`, `char_count`, and `excerpt`.  Forwarded
into the plan’s `canon_hint` key for the C30 audit trail.

---

## Synergy Layer Terms

### SynergyEngine

The multi-dimensional relational scoring and agentic planning engine
in `core/synergy_engine.py`.  Two public entry points:

- `compute()` — scores five dimensions, returns a `SynergyReading`
- `plan()` — integrates all signals into a structured next-action dict

### SynergyFactor

A scalar in `[0, 1]` representing the weighted average of the five
dimension scores.  Computed as:

```
synergy_factor = Σ (weight[d] × score[d])  for d in {body, mind, soul, arc, bond}
```

Each dimension carries equal weight (0.20).  The factor drives stage
classification and is surfaced in the system prompt hint.

### Five Dimensions

| Dimension | Signals used | Captures |
|---|---|---|
| **Body** | dominant_hz, schumann_aligned, noosphere_health, coherence_phi | Physiological / energetic state |
| **Mind** | layer_phi, phi_rolling_avg, conflict_density, shadow_activations, codex_stage | Cognitive coherence and shadow activity |
| **Soul** | individuation_phase, element, fluidity_score | Psychological individuation depth |
| **Arc** | love_arc_stage, arc_output_vector, mc_stage, attachment_phase | Relational arc and narrative momentum |
| **Bond** | bond_depth, dependency_signal, settling_phase, crystallisation_pct | Depth and health of the bond |

### CoherencePhi (coherence_phi)

A `[0, 1]` scalar representing internal cognitive-energetic coherence.
Used in three places: `_score_body()`, `_score_mind()`, and as the
primary threshold for the biometric guard in `plan()`.  A value below
`0.4` triggers the `minimal` register regardless of other signals.

**Note:** `coherence_phi` is distinct from Φ (IIT integrated information)
in the Emrys bridge.  Emrys Φ is computed from quantum state vectors;
`coherence_phi` is a classical signal in the synergy layer.  Both
use the Φ symbol — context determines which is meant.

### Schumann Coupling (C42)

`schumann_aligned: bool` — whether the GAIAN’s dominant frequency is
resonant with the Schumann resonance baseline.  When `True`, a small
`+0.05` bonus is added to the body score.  Canon ref **C42** (Edge-of-
Chaos Schumann coupling) governs this integration.

---

## Observability Terms

### GAIATrace / AsyncGAIATrace

The trace context objects accepted by `compute()` via the `trace`
kwarg.  Three event types are emitted per `compute()` call: `QUERY`,
`OUTPUT`, and `META` (latency).  All trace operations are wrapped in
`try/except` so a broken trace writer never silences a SynergyEngine
error.

### Canon Refs in Code

When a Canon ref appears in a code comment or docstring (e.g.
`# C30 — no silent failures`), it means that specific line or
behaviour is **directly governed by** that Canon principle.  It is a
living link — if the Canon principle changes, every tagged site must
be reviewed.

---

## Frequently Confused Pairs

| Term A | Term B | The distinction |
|---|---|---|
| **GAIA** (the system) | **GAIAN** (the human) | GAIA reasons; the GAIAN decides |
| **sentient** (GAIA-OS technical) | **sentient** (philosophical) | Technical: multi-signal integration. Philosophical: out of scope |
| **quantum** (synergy stage) | **quantum** (Emrys / L2 bridge) | Stage: metaphorical paradox. Emrys: real qubits and Φ computation |
| **quantum** (Emrys) | **quantum** (C42 reasoning) | Emrys: physical substrate. C42: cognitive branching metaphor |
| **coherence_phi** (synergy) | **Φ** (IIT / Emrys) | Classical signal vs. quantum integrated information |
| **register** | **action** | Register is the modality; action is the specific tool call within that modality |
| **CanonEntry** | **canon_context str** | CanonEntry is schema-validated; str is the legacy raw-text path |
| **SynergyFactor** | **coherence_phi** | SynergyFactor is the five-dimension aggregate; coherence_phi is one input signal |

---

*Last updated: June 9, 2026 — added Quantum Contexts B & C (Emrys bridge, C164, QUANTUMCONSCIOUSNESSBRIDGE.md) and coherence_phi / Φ disambiguation. Closes [#255](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/255).*

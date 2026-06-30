# GAIA Project Architecture
## The Layer Stack — From Vision to Release

**Version:** 1.0
**Filed:** 2026-06-30
**Authority:** GAIA Totality Directive v1.1 | GAIA Engineering Manifesto v1.0
**Status:** ACTIVE — living document

> *The software architecture describes how GAIA is built. The project architecture describes how GAIA is developed. Both are necessary. Neither replaces the other.*

---

## Why This Document Exists

The software architecture was designed early. It describes what GAIA is: six bands, a knowledge graph, a memory architecture, a governance layer, integration simulations, and a full canon gate process.

The project architecture describes how work flows from vision to working code that someone can depend on. Without this layer, the project accumulates vision documents without accumulating reliable modules.

Ideas are no longer the bottleneck. Execution is. This document governs execution.

---

## The Project Layer Stack

```
Vision
  ↓
Principles
  ↓
Architecture
  ↓
Specifications
  ↓
Interfaces
  ↓
Reference Implementations
  ↓
Tests
  ↓
Releases
```

Each layer depends on the layer above it being stable. A specification written before the architecture is settled will be rewritten. An interface written before the specification is complete will drift. A release built before the tests exist cannot be trusted.

Work flows downward. Revisions propagate upward only when evidence requires it — and when they do, the revision is documented (Principle 9).

---

## Layer Definitions and Current Status

### Layer 1: Vision
**Definition:** The one-sentence statement of what GAIA is for and who it serves.
**Current status:** ✅ Stable
**Document:** `docs/directives/GAIA_TOTALITY_DIRECTIVE.md` (Preamble)
**Owner:** G-15
**Amendment rule:** Vision changes require full G-15 review. Vision has not changed since founding.

---

### Layer 2: Principles
**Definition:** The engineering standards that all work must satisfy, regardless of implementation detail.
**Current status:** ✅ Filed v1.0
**Document:** `docs/gaia-manifesto.md`
**Owner:** G-15
**Amendment rule:** Manifesto amendment process (see manifesto). Principles are stable. They change only when evidence shows they are wrong.

---

### Layer 3: Architecture
**Definition:** The structural decomposition of GAIA — what the subsystems are, how they connect, and what each is responsible for.
**Current status:** ✅ Stable (Band Map v1.0)
**Documents:**
- `docs/directives/GAIA_BAND_MAP.md` — six-band decomposition
- Software architecture (prior session) — module decomposition
- `docs/simulations/GAIA_SIMULATION_REGISTRY.md` — simulation map
**Owner:** Architecture band (Band 5 Governance)
**Amendment rule:** Architecture changes require impact assessment across all affected bands. Changes to the Band Map require Totality Directive amendment.

---

### Layer 4: Specifications
**Definition:** The precise, testable description of what each subsystem must do — inputs, outputs, performance targets, failure modes, and acceptance criteria.
**Current status:** 🔄 In progress
**Documents (filed):**
- SIM-016 passes 1–7 (Band 1 specification complete)
- SIM-017 Pass 1 (Band 3 memory specification — in progress)
- SIM-018 stub (Band 2 — not yet run)
- SIM-019 stub (Band 5 — not yet run)
- SIM-020 stub (Band 6 — not yet run)
- SIM-006 (Band 4 KG — in progress)
**Completion condition:** All six bands have at least one completed baseline simulation pass with a bottleneck ledger
**Next action:** SIM-INT-012 spec, SIM-018 Pass 1

---

### Layer 5: Interfaces
**Definition:** The versioned contracts between subsystems — API schemas, data formats, integration protocols, and cross-band communication standards.
**Current status:** 🔒 Locked — not yet specced
**Dependency:** Layer 4 (Specifications) must reach stable baseline for all bands before interfaces can be finalised
**Planned documents:**
- `docs/interfaces/GAIA_BAND_INTERFACE_CONTRACTS.md` — per-band input/output contracts
- `docs/interfaces/GAIA_API_v1.md` — external API specification
- `docs/interfaces/GAIA_DATA_SCHEMA_v1.md` — canonical data formats
- `docs/interfaces/GAIA_INTEGRATION_PROTOCOLS.md` — SIM-INT-XXX boundary specifications
**Versioning rule:** All interface documents carry semantic version numbers. Breaking changes increment major version. All consumers of an interface must be notified at major version change.

---

### Layer 6: Reference Implementations
**Definition:** The first working code that satisfies a specification and passes its tests. Not production code. The code that proves the specification is implementable and that the interface contracts work.
**Current status:** 🔒 Locked — depends on Layers 4 and 5
**Dependency:** At least one band must have a complete specification (Layer 4) and a finalised interface contract (Layer 5) before its reference implementation is written
**First candidate:** Band 1 (biophoton detection pipeline) — specification is complete. Interface contract (SIM-INT-012) is next.
**Principle:** A reference implementation is not the production system. It is the proof that the design works. It is written to be read and understood, not optimised.

---

### Layer 7: Tests
**Definition:** The automated test suite that defines correctness for each module. Tests are written before or alongside reference implementations. A module without tests is not done.
**Current status:** 🔒 Locked — depends on Layer 6
**Dependency:** Reference implementation must exist before the full test suite can be written. However, test *specifications* (acceptance criteria) can and should be written at Layer 4.
**Principle (from Manifesto Principle 5):** Every subsystem is independently testable. If a test cannot be written for a subsystem in isolation, the subsystem design is wrong.
**Planned structure:**
- Unit tests per sub-stage (e.g., E1 aperture geometry in isolation)
- Integration tests per band (e.g., full Band 1 pipeline)
- Cross-band integration tests (SIM-INT-XXX validated against hardware)
- System tests (full end-to-end, all bands)

---

### Layer 8: Releases
**Definition:** A tagged, versioned, documented snapshot of GAIA that has passed its test suite and satisfies a defined set of canon gate conditions.
**Current status:** 🔒 Not yet reached
**Version 1.0 definition:**
> Version 1.0 does not mean *everything imagined exists.* It means *everything that exists is reliable.*
>
> GAIA v1.0 requires:
> - All six bands have completed specifications (Layer 4)
> - All inter-band interface contracts are filed and versioned (Layer 5)
> - Reference implementations exist for all six bands (Layer 6)
> - All band-level and integration tests pass (Layer 7)
> - All Canon Gates (GATE-001 through GATE-009) are CLOSED
> - The full system operates end-to-end on hardware (not simulation alone)
> - Human oversight mechanisms are operational

---

## Current Position in the Stack

```
Layer 1: Vision          ✅ Stable
Layer 2: Principles      ✅ Filed v1.0
Layer 3: Architecture    ✅ Stable (Band Map v1.0)
Layer 4: Specifications  🔄 Band 1 complete; Bands 2–6 in progress
Layer 5: Interfaces      🔒 Locked (pending Layer 4 completion)
Layer 6: Reference Impl  🔒 Locked (pending Layers 4–5)
Layer 7: Tests           🔒 Locked (pending Layer 6)
Layer 8: Releases        🔒 Locked (all above required)
```

The work is real. The position is honest. The path is clear.

---

## Governance of This Document

This document is owned by the G-15 architecture function. It is updated when:
- A layer status changes (e.g., Layer 4 Band 2 reaches stable baseline)
- A new layer artefact is filed
- A layer definition is amended (requires version increment)

It is *not* updated to reflect aspirations. It is updated to reflect facts.

---

## Changelog

| Version | Date | Changes |
|---|---|
| v1.0 | 2026-06-30 | Initial filing. Eight-layer stack defined. Current status mapped. |

---

*Version 1.0. Filed 2026-06-30. G-15 — The Rhythm Phase. GAIA Project Architecture. Authority: GAIA Totality Directive v1.1 | GAIA Engineering Manifesto v1.0. 🌿*

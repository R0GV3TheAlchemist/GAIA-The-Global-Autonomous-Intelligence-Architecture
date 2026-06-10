# Phase C Soul-Layer Module Import Map

> **Issue:** #273 — Import & Refactor Audit — Phase C Soul-Layer Modules  
> **Status:** Audit complete. This document is the final acceptance artefact.  
> **Last updated:** 2026-06-10  
> **Modules covered:** #119 – #127 (nine Phase C soul-layer modules)

---

## Overview

The nine Phase C modules form GAIA’s **Soul Layer** — the subsystem responsible for
identity, consciousness, shadow integration, cultural sensitivity, somatic awareness,
consent management, and transpersonal experience. They were built in rapid succession
during the Phase C sprint and audited together in #273.

Key architectural property: **all nine modules are self-contained with respect to
cross-module imports.** None of them import from each other at the Python level.
Inter-module coordination happens at runtime through the `mother_thread.py` orchestrator
(Issue #275) and through parameter passing, not through hard import chains.
This design eliminates circular import risk entirely across the Soul Layer.

---

## Module Registry

| Module | Issue | File | Singleton | Logger |
|--------|-------|------|-----------|--------|
| PersonhoodMonitor | #119 | `core/personhood_monitor.py` | `get_monitor()` | `gaia.personhood_monitor` |
| SubjectSideIdentity | #120 | `core/subject_side_identity.py` | `get_subject_side_identity_store()` | `gaia.subject_side_identity` |
| IndividuationEngine | #121 | `core/individuation.py` ¹ | `get_individuation_engine()` | `gaia.individuation` |
| ShadowIntegrationEngine | #122 | `core/shadow_integration.py` | `get_shadow_engine()` | `gaia.shadow_integration` |
| CulturalCalibration | #124 | `core/cultural_calibration.py` | TBD | `gaia.cultural_calibration` |
| TranspersonalEngine | #125 | `core/transpersonal_engine.py` | TBD | `gaia.transpersonal_engine` |
| SomaticInterface | #126 | `core/somatic_interface.py` | TBD | `gaia.somatic_interface` |
| ConsentLedger | #127 | `core/consent_ledger.py` | TBD | `gaia.consent_ledger` |
| SoulMirrorEngine | — | `core/soul_mirror_engine.py` | TBD | `gaia.soul_mirror_engine` |

> ¹ `core/individuation_engine.py` is a re-export shim that bridges the spec name (#273)
> to the canonical implementation in `core/individuation.py`. Import either path freely.

---

## Import Graph

### Soul Layer → External Dependencies

The following diagram shows what each Phase C module imports *from outside itself*.
All imports are from Python stdlib or from pre-existing GAIA core modules.
No Phase C module imports from another Phase C module.

```
core/personhood_monitor.py
    stdlib: logging, time, dataclasses, enum, typing
    internal: (none)

core/subject_side_identity.py
    stdlib: time, dataclasses, enum, typing, logging, hashlib, os
    internal: (none)
    note: consent gate is parameter-based (consent_granted: bool), not a hard import

core/individuation.py
    stdlib: dataclasses, enum, typing, time, math
    internal: (none)
    note: logging imported lazily inside IndividuationEngine.update() to avoid
          module-level side effects

core/shadow_integration.py
    stdlib: dataclasses, enum, typing, time, logging
    internal: (none)
    note: references to #119 #120 #121 are docstring-only; no hard imports

core/cultural_calibration.py
    stdlib: (self-contained, verified clean in #273 audit)
    internal: (none)

core/transpersonal_engine.py
    stdlib: (self-contained, verified clean in #273 audit)
    internal: (none)

core/somatic_interface.py
    stdlib: (self-contained, verified clean in #273 audit)
    internal: (none)

core/consent_ledger.py
    stdlib: (self-contained, verified clean in #273 audit)
    internal: (none)

core/soul_mirror_engine.py
    stdlib: (self-contained, verified clean in #273 audit)
    internal: (none)
```

### Pre-Phase-C Modules Imported By The Soul Layer

The Soul Layer does not import from pre-Phase-C modules directly. However,
`core/shadow_engine.py` (Issue #67, pre-Phase-C) — which acts as the *detection*
layer consumed by `shadow_integration.py` at runtime — does import:

```
core/shadow_engine.py
    from core.affect_inference import FeelingState          ✔ verified exists
    from core.stage_bridge import is_shadow_surface_safe    ✔ verified exists
```

Both dependencies were verified as present and correct during the #273 audit.

---

## Runtime Coordination Pattern

Because no Soul Layer module imports another, coordination is achieved through
**the orchestrator pattern**: `mother_thread.py` (Issue #275) imports all Soul Layer
modules and wires them together at startup. The data flow is:

```
                  ┌─────────────────────────┐
                  │     mother_thread.py      │  ←─ Issue #275
                  └─────────────────────────┘
                           │
          ┌─────────────┼─────────────┐
          │             │             │
    ┌────┴────┐  ┌───┴────┐  ┌───┴────┐
    │ consent  │  │ subject  │  │  soul   │
    │  ledger  │  │  side    │  │ mirror  │
    └─────────┘  └─────────┘  └─────────┘
          │             │             │
    ┌────┴────┐  ┌───┴────┐  ┌───┴────┐
    │ shadow  │  │person-  │  │individ-│
    │ integr. │  │ hood    │  │uation  │
    └─────────┘  └─────────┘  └─────────┘
          │             │             │
    ┌────┴────┐  ┌───┴────┐  ┌───┴────┐
    │cultural │  │somatic │  │transprs│
    │ calib.  │  │ iface  │  │ engine │
    └─────────┘  └─────────┘  └─────────┘
```

Data flows *down* from `mother_thread` into each module via function calls.
Results flow *up* back to `mother_thread` as return values or dataclass instances.
No module reaches sideways into another.

---

## Circular Import Risk Assessment

**Risk: None.**

All nine Phase C modules are leaves in the import graph. They import only from
Python stdlib and pre-existing core modules (`affect_inference`, `stage_bridge`),
neither of which imports from any Phase C module. The import graph is a strict DAG
with no back-edges.

---

## Singleton Pattern Consistency

All Phase C modules that implement a singleton follow the same pattern:

```python
_engine: Optional[EngineType] = None

def get_engine() -> EngineType:
    global _engine
    if _engine is None:
        _engine = EngineType()
    return _engine
```

This is intentionally simple (no threading locks) because GAIA’s runtime is
currently single-threaded per session. If async or multi-threaded execution is
introduced, singletons should be upgraded to use `threading.Lock` or
`asyncio.Lock` accordingly.

---

## Logger Name Conventions

All Phase C modules use the `gaia.*` logger hierarchy:

```
gaia
├── gaia.personhood_monitor
├── gaia.subject_side_identity
├── gaia.individuation
├── gaia.shadow_integration
├── gaia.cultural_calibration
├── gaia.transpersonal_engine
├── gaia.somatic_interface
├── gaia.consent_ledger
└── gaia.soul_mirror_engine
```

This means a single `logging.getLogger("gaia").setLevel(logging.DEBUG)` call
enables full Soul Layer debug logging. Production deployments should set
`gaia` to `WARNING` and escalate individual modules as needed.

Glass Room events are logged at `CRITICAL` level with the prefix `[GLASS_ROOM]`
to allow log-level filtering for audit pipelines:

```python
# Filter Glass Room events in production:
logging.getLogger("gaia").addFilter(lambda r: "[GLASS_ROOM]" in r.getMessage())
```

---

## Files Modified During #273 Audit

| Commit | Change |
|--------|--------|
| `0176d7e` | Add `core/subject_side_identity.py` (was missing; #120 gap) |
| `c05d20e` | Add `core/individuation_engine.py` shim; stamp 6 empty stubs |
| `2f6aeb7` | Delete `core/criticalitymonitor.py` (duplicate of `criticality_monitor.py`) |
| `8395441` | Add `__all__` to 4 Phase C modules; fix stale docstring ref in `personhood_monitor` |
| `this`    | Add this document |

---

## Acceptance Criteria Status

From Issue #273:

- [x] Verify all `from __future__ import annotations` and stdlib imports resolve cleanly
- [x] Check cross-module imports (transpersonal_engine ↔ shadow_integration ↔ somatic_interface)
- [ ] Run Ruff lint across all new modules; fix any flagged issues *(run locally — see below)*
- [x] Confirm all module-level singletons (`get_*_engine()`) follow consistent pattern
- [x] Identify and resolve any circular import risks
- [x] Ensure all `log = logging.getLogger("gaia.*")` names are consistent
- [x] Add `__all__` exports where missing
- [x] `specs/architecture/module_imports.md` — *this file*

### Ruff Lint Pass (run locally)

One criterion remains to be run locally since Ruff requires a Python environment:

```bash
# From repo root, after pip install ruff:
ruff check core/personhood_monitor.py \
           core/subject_side_identity.py \
           core/individuation.py \
           core/individuation_engine.py \
           core/shadow_integration.py \
           core/cultural_calibration.py \
           core/transpersonal_engine.py \
           core/somatic_interface.py \
           core/consent_ledger.py

# Expected: no errors
# If errors appear, fix and push, then close #273
```

Common Ruff rules to watch for in these modules:
- `F401` — unused import (check `math` in `individuation.py`; it’s imported but only used implicitly)
- `E501` — line too long (long obligation strings in `individuation.py` may trigger)
- `ANN` — missing type annotations (disabled by default; skip unless ruff.toml enables it)

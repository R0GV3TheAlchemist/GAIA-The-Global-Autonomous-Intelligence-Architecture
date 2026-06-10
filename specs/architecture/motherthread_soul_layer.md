# MotherThread — Soul-Layer Module Orchestration

> **Issue:** [#275](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/275)  
> **Canon:** C04 (Identity & Relational Selfhood), C43 (Epistemic Integrity), C47 (Sovereign Matrix Code / consent)  
> **Status:** Implemented — `core/soul_layer.py`

---

## Overview

The Phase-C soul-layer modules are standalone engines that each model a
specific dimension of GAIA's inner life. This document describes how they
are wired together through the `SoulLayer` orchestrator and surfaced to the
`MotherThread` runtime via a single `assess(turn_context)` entry point.

---

## Architecture

```
MotherThread
  └── SoulLayer.assess(GAIAContext)
        │
        ├── 1. SomaticInterface          — body-signal baseline
        ├── 2. TranspersonalEngine       — state driven by somatic coherence
        ├── 3. ShadowIntegrationEngine   — active archetype processing
        ├── 4. IndividuationEngine       — shadow patterns feed shadow dim.
        ├── 5. SubjectSideIdentityService— coherence from individuation score
        ├── 6. PersonhoodMonitor         — telemetry for Action Gate
        ├── 7. CulturalCalibrationEngine — locale profile (side-effect)
        └── 8. ConsentLedger             — gate: memory_write_allowed (C47)
              │
              └── SoulLayerAssessment   (returned to caller)
```

---

## Key Data Structures

### `GAIAContext`

A per-turn snapshot passed to `SoulLayer.assess()`.  All fields are
optional; engines degrade gracefully when data is absent.

| Field | Type | Purpose |
|---|---|---|
| `user_id` | `str` | Identifies the Gaian; required for user-scoped engines |
| `locale` | `str` | Drives `CulturalCalibrationEngine` profile lookup |
| `somatic_signals` | `Dict[str, float]` | Named channel readings (0-1) |
| `active_archetypes` | `List[str]` | Shadow archetypes active this turn |
| `shadow_intensity` | `float` | Overall shadow pressure (0-1) |
| `individuation_delta` | `Dict[str, float]` | Per-dimension updates for `IndividuationEngine` |
| `identity_coherence` | `float` | Turn-level identity coherence hint |
| `metadata` | `Dict` | Free-form passthrough for downstream engines |

### `SoulLayerAssessment`

One-object aggregate returned after every `assess()` call.

| Field | Type | Sourced from |
|---|---|---|
| `personhood` | `PersonhoodSnapshot` | `PersonhoodMonitor` |
| `identity` | `SubjectSideIdentity` | `SubjectSideIdentityService` |
| `individuation` | `IndividuationScore` | `IndividuationEngine` |
| `shadow_records` | `List[ShadowIntegrationRecord]` | `ShadowIntegrationEngine` |
| `cultural_profile` | `CulturalProfile` | `CulturalCalibrationEngine` |
| `transpersonal_reading` | `TranspersonalReading` | `TranspersonalEngine` |
| `somatic_readings` | `List[SomaticReading]` | `SomaticInterface` |
| `memory_write_allowed` | `bool` | `ConsentLedger` (C47 gate) |
| `glass_room_events` | `List[str]` | Emitted when intensity ≥ 0.75 |
| `summary` | `str` | Human-readable one-liner for logs / Action Gate |

---

## Engine Invocation Order & Data Flow

```
Somatic signals
  └─► avg_coherence
          └─► TranspersonalEngine.record(intensity=avg_coherence)

Active archetypes + shadow_intensity
  └─► ShadowIntegrationEngine.integrate(archetype, intensity)
          └─► max(record.intensity)
                  └─► IndividuationEngine.update(shadow += Δ when intensity > 0.6)

IndividuationScore.overall
  └─► SubjectSideIdentityService.update_coherence(max(ctx.identity_coherence, overall))

Individuation + Identity coherence + Transpersonal intensity
  └─► PersonhoodMonitor.record(agency, self_model_coherence, relational_depth, temporal_continuity)

ConsentLedger.check_consent(user_id, MEMORY_STORAGE)
  └─► SoulLayerAssessment.memory_write_allowed
```

---

## Glass Room Logging

Any engine reading that reaches or exceeds **0.75** (the ORANGE / FULL /
OVERWHELMING threshold) is logged to the `glass_room` Python logger at
`WARNING` level and appended to `SoulLayerAssessment.glass_room_events`.

Engines monitored:

- `SomaticInterface` — per-channel coherence
- `TranspersonalEngine` — intensity
- `ShadowIntegrationEngine` — per-record intensity
- `PersonhoodMonitor` — agency_score

Consumers of the observability layer subscribe to the `glass_room` logger
and route events to the audit store or alerting pipeline without coupling
to this module.

---

## Consent Gate (Canon C47)

The consent check is the **final** step in the assessment pipeline.  The
`memory_write_allowed` flag on `SoulLayerAssessment` is the authoritative
gate for all downstream memory writes:

```python
assessment = soul_layer.assess(ctx)
if assessment.memory_write_allowed:
    memory_store.write(user_id, data)
else:
    log.info("Memory write suppressed — consent not granted (C47)")
```

If `user_id` is empty the flag is always `False`.

---

## Usage

```python
from core.soul_layer import GAIAContext, get_soul_layer

soul_layer = get_soul_layer()  # singleton

ctx = GAIAContext(
    user_id="u-4b2f",
    locale="en",
    somatic_signals={"heart": 0.72, "breath": 0.55},
    active_archetypes=["Shadow", "Trickster"],
    shadow_intensity=0.65,
    individuation_delta={"shadow": 0.6, "integration": 0.4},
    identity_coherence=0.58,
)

assessment = soul_layer.assess(ctx)
print(assessment.summary)
# SoulLayer assessment — personhood_tier=reflective consent=BLOCKED shadow_records=2 glass_room_events=0

if assessment.memory_write_allowed:
    memory_store.write(ctx.user_id, assessment.to_dict())
```

### Integrating with `MotherThread`

Add the soul-layer call inside `MotherThread._beat()` after the collective
field computation (or in a dedicated `assess_turn()` method on the class):

```python
from core.soul_layer import GAIAContext, get_soul_layer

class MotherThread:
    def assess(self, turn_context: GAIAContext) -> "SoulLayerAssessment":
        """Single entry-point for soul-layer assessment."""
        return get_soul_layer().assess(turn_context)
```

---

## Acceptance Criteria Checklist

- [x] Single `MotherThread.assess(turn_context)` call returns a `SoulLayerAssessment`
- [x] All eight engines contribute to the assessment
- [x] Consent gate blocks memory writes when consent is not granted
- [x] Tests cover the full assessment pipeline (`tests/test_soul_layer.py`)
- [x] Glass Room logging for FULL/OVERWHELMING/ORANGE signals
- [x] Data flow: somatic → transpersonal, shadow → individuation, personhood → Action Gate
- [x] Graceful degradation on empty context / unknown channels

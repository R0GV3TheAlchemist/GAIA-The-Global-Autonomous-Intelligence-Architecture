# GAIAStateAdapter — Canonical Architecture Spec

**Issue:** #172  
**Sprint:** G-7  
**File:** `core/state_adapter.py`  
**Canon Refs:** C32 (Synergy Doctrine), C01 (Sovereignty)  
**Status:** Active

---

## Purpose

`GAIAStateAdapter` is the **single, explicit boundary** where GAIA's metaphysical domain objects (Solfeggio frequencies, Jungian individuation phases, love arc stages, Schumann resonance alignment, HRV coherence scores, affective valence, relational bond depth) are translated into the typed numeric primitives that `SynergyEngine.compute()` expects.

Before this adapter, every call site that invoked `engine.compute()` had to know — implicitly, inconsistently — how to translate GAIA's rich domain objects into raw `float`/`str` primitives. This coupling was fragile and would fracture as GAIA scaled. The adapter eliminates that fracture point.

---

## The Boundary

```
  ┌─────────────────────────────────────────────┐
  │          PHILOSOPHY LAYER                   │
  │  GaianRecord, Solfeggio notes, Jungian       │
  │  phases, love arc stages, Schumann fields    │
  └──────────────────┬──────────────────────────┘
                     │
           ┌─────────▼─────────┐
           │  GAIAStateAdapter │  ← THE ONLY translation point
           │  .to_synergy_params()              │
           └─────────┬─────────┘
                     │  SynergyParams (TypedDict)
  ┌──────────────────▼──────────────────────────┐
  │          RUNTIME LAYER                       │
  │  SynergyEngine.compute(**params)             │
  │  Pure numeric scoring functions              │
  └─────────────────────────────────────────────┘
```

---

## SynergyParams TypedDict

| Field | Type | Range | Default | Description |
|---|---|---|---|---|
| `dominant_hz` | `float` | 174–963 | 528.0 | Solfeggio Hz (heart coherence) |
| `individuation_phase` | `str` | — | `"persona"` | Jungian individuation phase |
| `love_arc_stage` | `str` | — | `"awakening"` | Relationship arc stage |
| `schumann_aligned` | `bool` | — | computed | Harmonic alignment with Earth resonance |
| `coherence_score` | `float` | 0.0–1.0 | 0.5 | HRV / psychological coherence |
| `emotional_valence` | `float` | −1.0–1.0 | 0.0 | Affective valence |
| `bond_depth` | `float` | 0.0–1.0 | 0.5 | Relational bond depth |

---

## Resolver Logic

Each private resolver encapsulates exactly one translation rule and is independently testable.

### `_resolve_hz()`

Priority order:
1. `record.dominant_hz` (numeric) — pass through if > 0
2. `record.active_solfeggio_note` → lookup in `SOLFEGGIO_HZ` table
3. Default: `528.0` Hz

### `_resolve_individuation()`

Returns `record.jungian_phase` or `"persona"`. Value passed through to SynergyEngine without validation (SynergyEngine owns range validation).

### `_resolve_love_arc()`

Returns `record.love_arc_stage` or `"awakening"`.

### `_resolve_schumann_alignment()`

Priority:
1. `record.schumann_aligned` bool (external sensor override)
2. Compute: `harmonic_phase = (hz % schumann_hz) / schumann_hz`
   Aligned if `harmonic_phase < 0.10` OR `harmonic_phase > 0.90` (±10% harmonic window)

### `_resolve_coherence()`

Reads `record.hrv_coherence_score`, falling back to `record.coherence_score`, then `0.5`. Clamped to `[0.0, 1.0]`.

### `_resolve_emotional_valence()`

Reads `record.affective_valence`, falling back to `record.emotional_valence`, then `0.0`. Clamped to `[-1.0, 1.0]`.

### `_resolve_bond_depth()`

Reads `record.bond_depth` or `0.5`. Clamped to `[0.0, 1.0]`.

---

## Solfeggio Hz Table

| Note | Hz | Intention |
|---|---|---|
| `ut` | 396.0 | Liberating Guilt and Fear |
| `re` | 417.0 | Undoing Situations and Facilitating Change |
| `mi` | 528.0 | Transformation and Miracles (DNA Repair / Heart Coherence) |
| `fa` | 639.0 | Connecting / Relationships |
| `sol` | 741.0 | Awakening Intuition |
| `la` | 852.0 | Returning to Spiritual Order |
| `si` | 963.0 | Awakening / Return to Oneness |

---

## GAIATrace Integration

`to_synergy_params()` emits a `TOOL_CALL` trace event when `core.trace` is available:

```json
{
  "event":        "TOOL_CALL",
  "gaian_id":     "gaian-abc123",
  "canon_refs":   ["C32", "C01"],
  "inputs":       {"gaian_id": "gaian-abc123", "record_type": "GaianRecord"},
  "output":       {"params_keys": ["dominant_hz", "individuation_phase", ...], "dominant_hz": 528.0}
}
```

If `core.trace` is not yet on the Python path, the adapter degrades gracefully — no import error, no trace, full functionality.

---

## SynergyEngine Bridge (Sprint G-7)

A `compute_from_adapter()` convenience method is added to `SynergyEngine` in this sprint:

```python
def compute_from_adapter(self, adapter: GAIAStateAdapter) -> tuple:
    """Convenience bridge — resolves adapter and delegates to compute()."""
    return self.compute(**adapter.to_synergy_params())
```

This is **non-breaking** — `compute()` signature is unchanged.

---

## Call Site Migration Pattern

### Before (fragile — caller knows too much)
```python
engine.compute(
    dominant_hz=528.0,
    individuation_phase="shadow",
    love_arc_stage="deepening",
    schumann_aligned=True,
    coherence_score=0.84,
    emotional_valence=0.3,
    bond_depth=0.7,
)
```

### After (explicit boundary)
```python
adapter = GAIAStateAdapter(gaian_record)
reading, new_state = engine.compute(**adapter.to_synergy_params())
```

### Or with bridge
```python
reading, new_state = engine.compute_from_adapter(GAIAStateAdapter(gaian_record))
```

---

## Sprint Migration Roadmap

| Sprint | Work |
|---|---|
| **G-7** (this PR) | Build `GAIAStateAdapter` and `SynergyParams`. Wire all call sites via `**params`. Add `compute_from_adapter()` bridge on `SynergyEngine`. |
| **G-8** | Add `SynergyEngine.compute_from_params(params: SynergyParams)` as the new canonical entry point. Deprecate bare-parameter signature. |
| **G-9** | Remove bare-parameter signature entirely. |

---

## Test Coverage Checklist

- [ ] `test_resolve_hz_from_numeric_attribute`
- [ ] `test_resolve_hz_from_note_name`
- [ ] `test_resolve_hz_unknown_note_defaults_to_528`
- [ ] `test_resolve_hz_all_solfeggio_notes`
- [ ] `test_resolve_individuation_default`
- [ ] `test_resolve_individuation_custom`
- [ ] `test_resolve_love_arc_default`
- [ ] `test_resolve_love_arc_custom`
- [ ] `test_resolve_schumann_explicit_bool_override`
- [ ] `test_resolve_schumann_computed_aligned`
- [ ] `test_resolve_schumann_computed_not_aligned`
- [ ] `test_resolve_coherence_clamped_high`
- [ ] `test_resolve_coherence_clamped_low`
- [ ] `test_resolve_coherence_fallback_attribute`
- [ ] `test_resolve_valence_clamped`
- [ ] `test_resolve_bond_depth_clamped`
- [ ] `test_to_synergy_params_returns_typed_dict`
- [ ] `test_to_synergy_params_missing_all_attrs_uses_defaults`
- [ ] `test_to_synergy_params_with_trace` (mock GAIATrace)
- [ ] `test_to_synergy_params_without_trace_module` (monkeypatch `_TRACE_AVAILABLE`)
- [ ] `test_async_adapter_to_synergy_params_async`
- [ ] `test_repr`
- [ ] `test_synergy_engine_compute_from_adapter`

---

## Related

| Issue | Module | Relationship |
|---|---|---|
| #171 | `core/trace.py` | GAIATrace used inside `to_synergy_params()` |
| #169 | `core/canon_graph.py` | C32 / C01 validated in graph |
| #170 | `core/task_graph.py` | `synergy_compute` PlanFactory uses this adapter |
| #173 | `MemoryHierarchy` | Reads canon refs scoped by C32 |

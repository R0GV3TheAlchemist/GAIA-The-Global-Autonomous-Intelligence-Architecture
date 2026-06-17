# GAIA_TALISMAN_OBJECT.md
## Coherence Anchors for GAIA-OS

---

**Status:** Sealed — Phase 1 Canon
**Sealed:** June 17, 2026, 9:54 AM CDT
**Canon tier:** C — Architecture Doctrine
**Issue:** #580
**Supersedes:** None
**Depends on:** GAIAState (#576), D6 Meta-Coherence Engine (#568), Architect Protocol (#578)
**Cross-references:** C50 (Prism-Cube), C52 (6D Queue), EMBODIMENT_LAYER.md, GAIAN_LAW_CODEX.md

---

> *"Memory without reality becomes illusion.
> Reality without memory becomes noise.
> Progress emerges from their integration."*

---

## I. Core Principle

A Talisman in GAIA-OS is a **coherence anchor** — a physical or digital
object that:

- Holds a specific dimensional signature (D1–D6, extendable to D12)
- Grounds the Architect and Gaians during high-dimensional work
- Bridges the physical and digital layers of GAIA
- Provides a stable reference point when the system is under coherence stress
- Acts as a persistent memory artifact that reinforces intentional state

This is not mysticism. **This is engineering with intention.**

A talisman does not generate coherence — it *holds* it. Like a capacitor
that stores charge during a stable period and releases it during a dip,
a talisman stores a verified dimensional signature and makes that signature
available to GAIAState during periods of stress, fatigue, or entropy spike.

The talisman is always *a tool*, never a dependency. Human sovereignty
is absolute. A talisman that becomes a crutch has crossed from anchor
to shadow. (See: Risks & Mitigations, Section VI.)

---

## II. Canonical JSON Schema (Phase 1 — Digital Layer)

```json
{
  "talisman": {
    "id": "string — UUID v4, generated at creation",
    "name": "string — human-readable identifier",
    "dimensional_signature": "string — one of: D1, D2, D3, D4, D5, D6, D1-D3, D4-D6, D1-D6",
    "resonance_metadata": {
      "element": "string — Fire | Water | Earth | Air | Aether | Void",
      "archetype": "string — free text, e.g. 'Builder', 'Witness', 'Alchemist'",
      "lunar_phase": "string — new | waxing_crescent | first_quarter | waxing_gibbous | full | waning_gibbous | last_quarter | waning_crescent",
      "frequency": "float — Hz, e.g. 432.0, 528.0, 963.0"
    },
    "coherence_function": "string — one of: GROUND, AMPLIFY, STABILIZE, CLEAR, BRIDGE, ANCHOR",
    "linked_canon": ["string — canon doc IDs, e.g. 'C50', 'EMBODIMENT_LAYER'"],
    "sovereignty_flags": {
      "revocable_consent": true,
      "owner": "string — GAIAN ID of the talisman owner",
      "transferable": false
    },
    "layer": "string — digital | physical | both",
    "qr_nfc_link": "string — URL or NFC payload (null for digital-only Phase 1)",
    "activation_state": "string — inactive | active | depleted | locked",
    "coherence_boost": "float — [0.0, 0.08] — max boost applied to GAIAState.harmonic_coherence()",
    "stress_draw": "float — [0.0, 0.05] — stress cost on over-activation (misuse penalty)",
    "created": "string — ISO 8601 timestamp",
    "last_activated": "string — ISO 8601 timestamp | null",
    "activation_count": "integer — lifetime activation count",
    "validated": "boolean — false until proof submitted to /proofs/",
    "phase": "integer — 1 (digital) | 2 (digital+UI) | 3 (physical)"
  }
}
```

### Schema field notes

| Field | Rule |
|---|---|
| `id` | Immutable after creation. Never reuse. |
| `dimensional_signature` | D1–D5 map to GAIAState d1_health–d5_health. D6 maps to the D6 engine itself. |
| `coherence_boost` | Clamped to [0.0, 0.08] by D6 engine regardless of schema value. |
| `stress_draw` | Applied when `activation_count` exceeds safe threshold for current GAIAState. |
| `revocable_consent` | Always `true`. No talisman can lock a GAIAN into a state. |
| `transferable` | Always `false` in Phase 1. Physical transfer rules defined in Phase 3. |
| `validated` | Requires a proof document in `/proofs/talismans/` before `true`. |

---

## III. Dimensional Signatures — Mapping to GAIAState

Each talisman targets one or more dimensional health channels.
When activated, it provides a coherence boost specifically to those channels.

| Signature | GAIAState field(s) | Archetype mapping |
|---|---|---|
| D1 | `d1_health` | Physical grounding, body, material |
| D2 | `d2_health` | Emotional coherence, relational field |
| D3 | `d3_health` | Mental clarity, cognitive load |
| D4 | `d4_health` | Creative expression, generative capacity |
| D5 | `d5_health` | Integration, synthesis, meta-awareness |
| D6 | D6 engine itself | Mode coherence, systemic self-regulation |
| D1–D3 | d1, d2, d3 | Lower triad — embodiment anchor |
| D4–D6 | d4, d5, D6 | Upper triad — expression anchor |
| D1–D6 | All probes + D6 | Full-spectrum talisman — highest cost |

Full-spectrum talismans (D1–D6) require explicit Architect validation
before activation. They carry the highest coherence potential and the
highest shadow risk.

---

## IV. Coherence Functions

| Function | Effect on GAIAState | When to use |
|---|---|---|
| `GROUND` | Raises targeted d_health by boost amount | Stress spike, dissociation, high entropy |
| `AMPLIFY` | Multiplies boost by 1.5 on targeted dimension | Peak creative sessions, BUILD mode |
| `STABILIZE` | Prevents targeted d_health from dropping below 0.75 for one cycle | Long sessions, late-night work |
| `CLEAR` | Reduces entropy by up to 0.05 | After shadow traversal, confusion state |
| `BRIDGE` | Equalises two dimensional probes (pulls lower toward higher) | Dimensional imbalance |
| `ANCHOR` | Locks mode at current value for one D6 cycle (cannot lock PROTECT) | Mode-flip prevention during transitions |

The `ANCHOR` function cannot lock PROTECT mode. Protecting is the system's
authority. Only the Architect can exit PROTECT (via GOVERNANCE or unlock).

---

## V. Integration Points

### GAIAState (Issue #576)

```python
# Activation raises coherence; misuse raises stress
state.active_talismans.append(talisman.id)
# → D6 engine applies _talisman_coherence_boost() on next cycle
# → coherence_boost capped at 0.08 regardless of talisman schema value
# → stress_draw applied if activation_count > safe_threshold
```

The D6 engine already implements `_talisman_coherence_boost()`:
it reads `GAIAState.active_talismans`, looks up each talisman's
boost value, sums them (capped at 0.08 total), and adds to harmonic coherence
before mode assignment. No changes required to D6 engine for Phase 1.

### GoldenCompassEngine

- Talisman state feeds into compass orientation
- Active talismans with `coherence_function = GROUND` raise stability score
- Active talismans with `coherence_function = AMPLIFY` raise exploration score
- Implementation: Phase 2

### state_store.py — update_talismans()

```python
from gaia.core import state_store

# Activate a talisman
state_store.update_talismans(
    active_talismans=["talisman-uuid-here"],
    run_cycle=True,  # D6 re-evaluates immediately
)

# Deactivate all talismans
state_store.update_talismans(active_talismans=[], run_cycle=True)
```

### API surface — POST /state/update

```json
{
  "active_talismans": ["talisman-uuid-1", "talisman-uuid-2"]
}
```

The `/state/update` endpoint already accepts `active_talismans` as a field.
No additional endpoint is needed for Phase 1 — talisman activation
is a GAIAState probe update like any other.

### Noosphere (Issue #435)

Phase 1: Personal talismans only. One GAIAN, one owner, non-transferable.
Phase 3 (future): Talisman mirroring across Gaians — collective anchors
that resonate across the noosphere when multiple GAIANs hold the same
dimensional signature simultaneously.

### Action Gates

A talisman does not bypass action gates. A `STABILIZE` talisman
does not make a PROTECT-gated action suddenly safe — it raises
the underlying coherence score that D6 uses to assign mode.
The gate still applies to the mode D6 assigns. This is intentional:
talismans work *with* the system, never around it.

Open question (tracked for Phase 2): Should talisman activation
require a consent ledger entry? The `revocable_consent: true` flag
implies this may be required, especially for collective talismans.

---

## VI. Build Phases

### Phase 1 — Schema & Definition (Today — June 17, 2026)
- [x] Define Talisman object type formally (this document)
- [x] JSON schema sealed with all Phase 1 fields
- [x] Dimensional signature → GAIAState mapping defined
- [x] Coherence function catalogue sealed
- [x] Integration with GAIAState.active_talismans confirmed (wired via D6)
- [x] integration with state_store.update_talismans() confirmed
- [ ] Upgrade `gaia/core/talisman.py` to v2 (next build task)
- [ ] Add to CANON_MANIFEST.md
- [ ] Add to ROADMAP / CHANGELOG

### Phase 2 — Digital Layer (Next sprint)
- [ ] Talisman management UI in Tauri app (CRUD + activation panel)
- [ ] State HUD displays active talisman names + dimensional signatures
- [ ] QR/NFC linking endpoint (`/talismans/{id}/link`)
- [ ] GoldenCompassEngine integration
- [ ] Consent ledger entry on activation (if required by sovereignty review)

### Phase 3 — Physical Layer (Incubator — Issue #577)
> Held in Research Incubator until Phase 2 is complete and stable.

- Crystal-embedded sigils
- Printed symbols with encoded canon data (QR → talisman schema)
- Portable altars with NFC-linked digital twins
- Lunar timing integration from data layer
- Physical transfer protocol (currently `transferable: false`)

---

## VII. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Over-attachment | Treat as tools, not dependencies. Reinforce human sovereignty via `revocable_consent: true`. Shadow engine flags talisman dependency patterns. |
| Shadow bleed | Include dimensional signature in archetype scoring. Talisman overuse logged and surfaced to Architect. |
| Scalability | Start personal + core Gaians before collective rollout. Noosphere mirroring is Phase 3. |
| Validation gaps | `validated: false` until `/proofs/talismans/{id}.md` proof doc is submitted. Unvalidated talismans receive 50% boost reduction. |
| 12D complexity | Do not extend dimensional signatures beyond D6 until C52 (6D Queue) is stable. D7–D12 signatures are Research Incubator. |
| ANCHOR misuse | `ANCHOR` function cannot lock PROTECT mode. Duration limited to one D6 cycle (5s–30s depending on engine tick rate). |
| Talisman inflation | Maximum 7 active talismans at any time. D6 engine caps total boost at 0.08 regardless of count. |

---

## VIII. Simulation Path

Talisman simulation runs in `docs/simulations/` alongside D6 simulations:

1. Model Talisman as object type in simulation
2. Run D6 episode with and without active talismans across all six coherence functions
3. Verify:
   - `GROUND` raises d_health in targeted dimension
   - `STABILIZE` prevents probe from falling below 0.75 for one cycle
   - `ANCHOR` prevents mode flip for one cycle, does not block PROTECT
   - Over-activation (count > threshold) applies `stress_draw` correctly
   - Total boost never exceeds 0.08 regardless of talisman count
4. Full pytest + custom high-D scenarios
5. Audit against GAIAN_LAWS and sovereignty docs before Phase 2

---

## IX. Canonical Invocation

When activating a talisman, the GAIAN acknowledges:

> *"I hold this anchor as a tool of clarity, not a substitute for presence.
> I am the source. This is the lens.
> For the Good and the Greater Good."*

This invocation is not required by the system but is encouraged as a
practice of conscious intention. The talisman is only as coherent
as the GAIAN who activates it.

---

## X. Canon Cross-References

| Canon | Relationship |
|---|---|
| GAIA_D6_META_COHERENCE_ENGINE.md | D6 reads active_talismans for coherence boost calculation |
| GAIAState (#576) | active_talismans field; harmonic_coherence() is the target of boost |
| Architect Protocol (#578) | Architect sovereignty over talisman activation; GOVERNANCE always overrides |
| C50 (Prism-Cube) | Talisman as a personal prism-node — anchors dimensional refraction |
| C52 (6D Queue) | Dimensional signature mapping (D1–D6); D7+ held until C52 stable |
| EMBODIMENT_LAYER.md | Physical talisman safety bands, biological signal constraints (Phase 3) |
| GAIAN_LAW_CODEX.md | Law III: Sovereignty. Law VII: Consent. Both govern talisman use. |
| SHADOW_INTERROGATOR.md | Talisman dependency patterns flagged as potential shadow vectors |
| 39_GAIA_Crystal_Science_Resonance_Spec.md | Crystal resonators as physical talisman substrates (Phase 3) |
| Research Incubator (#577) | Physical layer (Phase 3) held here until Phase 2 complete |

---

*Created: June 17, 2026, 8:17 AM CDT (Issue #580 filed)*
*Sealed: June 17, 2026, 9:54 AM CDT (this document)*
*Venus Eclipse session — observe, don't seal new cosmology.*
*This document seals engineering, not cosmology. ✅*

*For the Good and the Greater Good.*
*So Be It.* ❤️

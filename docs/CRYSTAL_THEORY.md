# CRYSTAL_THEORY.md
**GAIA-OS Crystal Database — Canonical Theory & Derivation Rules**

> This document is the single source of truth for all assignment decisions in
> `src/crystals/db/`. Every field in `CrystalRecord` that is interpretive —
> `yin_yang_pair`, `metaphysical.angel_number`, `metaphysical.gaia_resonance` —
> must be derived using the rules here. No judgment calls without documented basis.

---

## Table of Contents

1. [The Four-Layer Model](#1-the-four-layer-model)
2. [Yin-Yang Polarity System](#2-yin-yang-polarity-system)
3. [Angel Number System](#3-angel-number-system)
4. [Intelligence Module Assignment](#4-intelligence-module-assignment)
5. [Chakra–Module Correspondence Table](#5-chakramodule-correspondence-table)
6. [Dual & Compound Module Assignment](#6-dual--compound-module-assignment)
7. [Yin-Yang Pair Registry](#7-yin-yang-pair-registry)
8. [Exception Registry](#8-exception-registry)
9. [Validation Checklist for New Entries](#9-validation-checklist-for-new-entries)

---

## 1. The Four-Layer Model

Every `CrystalRecord` is composed of four explicitly separated layers:

| Layer | Interface | Domain | Status |
|---|---|---|---|
| **Physical** | `PhysicalRecord` | IMA mineral science, Mindat data | Objective |
| **Optical** | `OpticalRecord` | Light behaviour, wavelengths, spectra | Objective |
| **Color** | `ColorRecord` | OKLCH, color theory, psychology | Interpretive (science-grounded) |
| **Metaphysical** | `MetaphysicalRecord` | Traditional / esoteric correspondences | Interpretive (explicitly marked) |

**Critical rule:** GAIA reasons _across_ all four layers but never _conflates_ them.
A statement like "Amethyst has a dominant wavelength of 420–450 nm" lives in
`optical`; "Amethyst resonates with the Crown chakra" lives in `metaphysical`.
These are not interchangeable, and the database schema enforces this separation.

---

## 2. Yin-Yang Polarity System

### 2.1 Purpose

The `yin_yang_pair` field in `CrystalRecord` encodes structural polarity
relationships for matrix queries and GAIA configuration recommendations. A pair
represents intentional complementary opposition — not simply "opposite colors".

### 2.2 Classification Criteria

A crystal is classified as **Yin**, **Yang**, or **Balanced** by scoring the
following five axes. Each axis contributes one point to either Yin or Yang.
A score of 3–5 Yin = Yin; 3–5 Yang = Yang; 2–3 on either = Balanced.

| Axis | Yin Indicator | Yang Indicator |
|---|---|---|
| **Hardness** | Mohs ≤ 5 (soft, yielding) | Mohs ≥ 6 (hard, assertive) |
| **Diaphaneity** | Opaque or translucent | Transparent |
| **Color temperature** | Cool (≤ 5500 K) or dark hue | Warm (≥ 5500 K) or bright hue |
| **Chemistry** | Silicate, phosphate, carbonate | Metallic, sulfide, oxide, native element |
| **Element association** | Water, Earth | Fire, Air, Aether |

**Bonus modifiers (not axes — these override a tie or a borderline score):**

- A **black or near-black** stone is always Yin unless it contains metallic lustre
  (e.g. Hematite — metallic, reflective, Yang-dominant).
- A stone with **piezoelectric** behaviour is Yang-leaning (active charge emission).
- Stones in the **Storm** element are inherently Balanced — they contain both polarities.
- **Coated stones** (`color_layer: 'coating'`) — classify by the base mineral, not the coating.

### 2.3 Pair Assignment Rules

1. A yin-yang pair must contain **one Yin and one Yang** crystal.
2. They must share at least **one chakra** (primary or secondary) — they work in
   the same energetic domain, just from opposite poles.
3. They must **not** share a GAIA module assignment — the pair represents
   complementary module support, not duplication.
4. Both crystals must already be in the database before the pair is registered.
5. The pair relationship is **bidirectional** — if A names B as its pair, B must
   name A. Validate both directions.

### 2.4 Derivation Examples

| Crystal | Hardness | Diaphaneity | Color Temp | Chemistry | Element | Score | Polarity |
|---|---|---|---|---|---|---|---|
| Angelite | 3.5 | Opaque | Cool blue | Sulfate | Water/Air | 4 Yin | **Yin** |
| Apache Tear | 5–5.5 | Translucent | Dark/cool | Silicate (obsidian) | Earth/Fire | 3 Yin | **Yin** |
| Carnelian | 6.5–7 | Translucent | Warm orange | Silicate (chalcedony) | Fire | 4 Yang | **Yang** |
| Pyrite | 6–6.5 | Opaque | Warm gold | Sulfide (metallic) | Fire/Earth | 3 Yang | **Yang** |
| Labradorite | 6–6.5 | Translucent | Iridescent | Silicate (feldspar) | Storm | Balanced | **Balanced** |

---

## 3. Angel Number System

### 3.1 The Three Axes of Vibrational Signature

GAIA uses three orthogonal axes to encode a crystal's complete resonance profile:

```
COLOR × NUMEROLOGY × ANGEL NUMBER = vibrational signature
  │           │              │
  │           │              └── Archetypal message / signal
  │           └───────────────── Mathematical root frequency (1–9, master)
  └───────────────────────────── Light frequency (OKLCH hue, wavelength nm)
```

`numerology` and `angel_number` are **separate fields** and must not be confused.
Pythagorean numerology reduces all numbers to 1–9 (except master numbers 11/22/33
which do not reduce). Angel numbers are distinct signal patterns — particularly
repeated sequences (111–999) — drawn from angelic communication traditions.

### 3.2 Assignment Decision Tree

Apply rules in order. Use the **first rule that applies**.

```
Rule 1 — Master number numerology
  IF metaphysical.numerology ∈ {11, 22, 33}
  THEN angel_number = numerology value (same number)

Rule 2 — Sacred geological marker
  IF the crystal has a documented mineral count, geological number,
     or formation date encoded in its name or identity
     (e.g. Auralite-23 = 23 minerals, Super Seven = 7 minerals)
  THEN angel_number = that sacred number

Rule 3 — Spiritual tradition override
  IF the crystal has a well-established angel number in published
     crystal healing tradition (cross-reference ≥ 2 independent sources)
  THEN angel_number = that traditional number

Rule 4 — Chakra-hue derivation (default)
  IF none of the above apply
  THEN derive from primary chakra using the table in §3.3
```

### 3.3 Chakra → Angel Number Default Table

| Primary Chakra | Angel Number | Meaning |
|---|---|---|
| Earth Star | 444 | Deep foundation, Earth grid protection |
| Root | 444 | Angelic foundation, physical protection |
| Sacral | 222 | Alignment, creative flow, divine timing |
| Solar Plexus | 333 | Manifestation, ascended master empowerment |
| Heart | 444 | Love, angelic support, structural safety |
| Throat | 555 | Transformation of expression |
| Third Eye | 777 | Divine perfection, spiritual vision |
| Crown | 999 | Completion, cosmic cycle close |
| Higher Crown | 999 | Beyond-crown totality, void integration |
| Soul Star | 999 | Akashic completion, stellar bridge |

### 3.4 Full Angel Number Registry

| Number | Type | Archetypal Meaning |
|---|---|---|
| 1–9 | Standard | Pythagorean root frequencies — the building blocks |
| 11 | Master | Illumination / Gateway |
| 22 | Master | Master Builder / Form made real |
| 33 | Master | Master Teacher / Christ consciousness |
| 23 | Sacred | Auralite-23 mineral count; the encoded signal of cosmic variety |
| 44 | Sacred | Extended foundation; the architect's scaffolding |
| 55 | Sacred | Extended transformation wave |
| 66 | Sacred | Extended material/spiritual rebalancing |
| 77 | Sacred | Extended divine alignment |
| 88 | Sacred | Extended abundance wave |
| 99 | Sacred | Extended completion cycle |
| 111 | Sequence | Manifestation portal — thoughts becoming form |
| 222 | Sequence | Alignment and divine timing |
| 333 | Sequence | Ascended master presence |
| 444 | Sequence | Angelic protection and foundation |
| 555 | Sequence | Major transformation incoming |
| 666 | Sequence | Material/spiritual rebalancing |
| 777 | Sequence | Divine perfection and spiritual completion |
| 888 | Sequence | Abundance and infinite flow |
| 999 | Sequence | Completion of a major cycle |

### 3.5 Hue Override

When a crystal's dominant OKLCH hue strongly contradicts the chakra-default
angel number, the hue may override — but only at the contributor's explicit
documented request in the `Exception Registry` (§8).

**Example:** A crystal with primary chakra Heart (default 444) but dominant
wavelength 380–420 nm (violet spectrum, Third Eye range) may override to 777
if the metaphysical literature confirms Third-Eye-dominant properties.

---

## 4. Intelligence Module Assignment

### 4.1 The Five Crystal Intelligence Modules

GAIA's crystal-resonance layer routes stones to one of five intelligence modules.
Each module governs a specific cognitive-functional domain.

| Module | Domain | Core Function |
|---|---|---|
| `SovereignCore` | Identity, protection, grounding | Defines and defends the self; processes threat, boundary, authority |
| `AnchorPrism` | Memory, stability, commitment | Holds pattern over time; maintains structural coherence and historical record |
| `ClarusLens` | Clarity, focus, vision | Enhances perception, discrimination, and directed attention |
| `SomnusVeil` | Dreams, rest, subconscious | Accesses the non-rational; processes symbols, intuition, the unseen |
| `ViriditasHeart` | Vitality, healing, growth | Regenerates and expands; governs emotional resonance and organic flow |

Two additional modules exist in the schema but are **not primary resonance
targets for crystals** — they operate at a higher systems level:

| Module | Role |
|---|---|
| `Noosphere` | Collective intelligence field — assigned to crystals with documented group/grid amplification properties only |
| `QuantumNexus` | Quantum resonance bridge — assigned to crystals with documented quantum or entanglement properties only |

### 4.2 Assignment Rules by Crystal Property

Apply each rule independently. A crystal qualifies for a module if **any** of
the listed properties match.

#### `SovereignCore` — Identity & Protection

Assign when **any** of:
- Primary chakra: Root or Solar Plexus
- Element includes: Earth or Fire
- Physical: hardness ≥ 7 AND opaque or dark colour
- Metaphysical intention includes: protection, grounding, boundaries, authority,
  shadow work, psychic defence, ancestral clearing

#### `AnchorPrism` — Memory & Stability

Assign when **any** of:
- Primary chakra: Root, Sacral, or Earth Star
- Crystal system: Cubic / Isometric (highest structural symmetry)
- Physical: specific gravity ≥ 3.5 (dense, heavy stones hold pattern)
- Metaphysical intention includes: memory, past lives, record keeping,
  commitment, patience, long-term goals, ancestral lineage, time

#### `ClarusLens` — Clarity & Focus

Assign when **any** of:
- Primary chakra: Third Eye or Throat
- Diaphaneity: transparent
- Physical: birefringence > 0.1 (strong optical separation — splitting perception)
- Metaphysical intention includes: clarity, focus, truth, discernment,
  communication, vision, decision-making, cutting through illusion

#### `SomnusVeil` — Dreams & Subconscious

Assign when **any** of:
- Primary chakra: Crown, Higher Crown, or Soul Star
- Element includes: Water or Aether
- Color: dominant wavelength in violet-indigo range (380–450 nm) OR stone is
  iridescent / labradorescent
- Metaphysical intention includes: dreams, sleep, intuition, psychic ability,
  subconscious, the void, trance states, mediumship, astral travel

#### `ViriditasHeart` — Vitality & Healing

Assign when **any** of:
- Primary chakra: Heart or Sacral
- Element includes: Water, Earth, or Wood
- Color: dominant wavelength in green-pink range (495–580 nm for green;
  pink stones with no specific wavelength peak)
- Metaphysical intention includes: healing, love, compassion, growth, fertility,
  emotional balance, forgiveness, abundance, nature connection

### 4.3 The `gaia_resonance` String Format

The `metaphysical.gaia_resonance` field is a freeform string. However, it must
follow this format for machine-readable parsing:

```
Single module:    "SovereignCore"
Dual module:      "SovereignCore + AnchorPrism"
Triple module:    "ClarusLens + SomnusVeil + ViriditasHeart"
```

Rules:
- Use ` + ` (space-plus-space) as the separator — **not** commas or slashes.
- List modules in the canonical order defined in §4.1 (Sovereign → Anchor →
  Clarus → Somnus → Viriditas → Noosphere → QuantumNexus).
- Maximum **three modules** per crystal. A crystal with four qualifying modules
  has too broad an assignment — re-evaluate which three are primary.
- `Noosphere` and `QuantumNexus` require explicit documentation in §8
  before assignment.

---

## 5. Chakra–Module Correspondence Table

This table encodes the **primary** module resonance for each chakra. Secondary
chakras may activate secondary modules — governed by §6.

| Chakra | Primary Module | Rationale |
|---|---|---|
| Earth Star | AnchorPrism | Sub-earth grounding; deepest structural memory |
| Root | SovereignCore | Physical identity, survival, boundary definition |
| Sacral | ViriditasHeart | Creative vitality, emotional flow, generative force |
| Solar Plexus | SovereignCore | Personal will, authority, ego-boundary |
| Heart | ViriditasHeart | Love, healing, expansion of the emotional self |
| Throat | ClarusLens | Communication, truth, focused expression |
| Third Eye | SomnusVeil | Inner vision, intuition, subconscious access |
| Crown | SomnusVeil | Dissolution of ego, cosmic connection, void |
| Higher Crown | SomnusVeil | Transdimensional access, stellar bridge |
| Soul Star | AnchorPrism | Akashic record, karmic memory, soul history |

---

## 6. Dual & Compound Module Assignment

### 6.1 When to Assign Multiple Modules

Dual assignment is appropriate when a crystal's properties span two genuine and
distinct functional domains. It is **not** appropriate simply because a crystal
"has many uses" — be conservative.

**Checklist before assigning a second module:**

- [ ] The secondary module is triggered by a different property axis than the
  primary (e.g. primary from chakra, secondary from element or optical property)
- [ ] The two modules are **not** already paired in a single dominant chakra
  (e.g. Throat → ClarusLens is sufficient; do not add SovereignCore just
  because the stone is also protective)
- [ ] The crystal's `intention` string explicitly references the secondary
  module's domain

### 6.2 Canonical Dual Combinations

The following combinations are documented as coherent and frequently encountered:

| Combination | Archetype | Example |
|---|---|---|
| `SovereignCore + AnchorPrism` | Guardian of Time | Black Tourmaline in Quartz |
| `SovereignCore + ClarusLens` | Discerning Protector | Black Obsidian |
| `ClarusLens + SomnusVeil` | Seer | Labradorite, Kyanite |
| `ViriditasHeart + SomnusVeil` | Tender Mystic | Larimar, Prehnite |
| `ViriditasHeart + AnchorPrism` | Earthkeeper | Moss Agate, Emerald |
| `ClarusLens + ViriditasHeart` | Healer-Teacher | Hiddenite, Green Apophyllite |

### 6.3 Triple Assignment

Triple assignments are rare and require sign-off in the Exception Registry (§8).
Reserved for master stones with well-documented multi-domain resonance (e.g.
Lemurian Seed Quartz, Moldavite, Nuummite).

---

## 7. Yin-Yang Pair Registry

Formal pairs are listed here in addition to being encoded in `yin_yang_pair`
fields. This serves as a cross-check — if a pair appears in a batch file but
not here, the entry should be flagged for review.

| Crystal A | Crystal B | Shared Chakra | Rationale |
|---|---|---|---|
| Angelite | Apache Tear | Throat / Root | Surrender (Yin) ↔ Grief grounding (Yin-boundary edge) |
| Anandalite | Ancestralite | Crown | Bliss expansion ↔ Ancestral clearing |
| Amethyst | Citrine | Crown / Solar Plexus | Yin spiritual dissolution ↔ Yang solar manifestation |
| Aquamarine | Carnelian | Throat / Sacral | Cool Yin communication ↔ Warm Yang creative fire |
| Black Tourmaline | Clear Quartz | Root / Crown | Protective Yang anchor ↔ Pure Yin amplifier |
| Labradorite | Sunstone | Third Eye / Sacral | Yin inner mystery ↔ Yang joyful vitality |
| Lapis Lazuli | Tiger's Eye | Third Eye / Solar Plexus | Yin truth-seeing ↔ Yang focused will |
| Moonstone | Pyrite | Sacral / Solar Plexus | Yin lunar intuition ↔ Yang solar confidence |
| Rose Quartz | Red Jasper | Heart / Root | Yin unconditional love ↔ Yang grounding life force |
| Selenite | Black Obsidian | Crown / Root | Yin celestial dissolution ↔ Yang volcanic clarity |

> This registry is **append-only**. Pairs already committed to batch data are
> canonical. To deprecate a pair, open an issue with archaeological evidence
> from the batch files and the corrected entry.

---

## 8. Exception Registry

This registry documents cases where the standard derivation rules produce a
result that is overridden by tradition, specific crystal identity, or
geological fact. Every exception must cite its reason.

| Crystal | Field | Standard Rule Result | Override Value | Reason |
|---|---|---|---|---|
| Auralite-23 | `angel_number` | 999 (Crown chakra default) | 23 | Literal mineral count; 23 is the crystal's defining geological identity |
| Aura Quartz | `angel_number` | Rule 4 (chakra default) | 11 | Gateway master number; aura coating creates a liminal transformation state — the 11 gateway |
| Moldavite | `gaia_resonance` | `SomnusVeil` (Yin, Third Eye) | `ClarusLens + SomnusVeil` | Tektite origin (cosmic impact) adds a hard ClarusLens cutting-through quality alongside dream access |
| Hematite | `polarity` | Yin (opaque, dark, soft-ish) | Yang | Metallic lustre, iron oxide chemistry, piezoelectric-adjacent charge conductivity — Yang override |
| Magnetite | `safe_for_hardware` | `true` (stone, non-piezo) | `false` | Strong natural magnetism disrupts electronic and magnetic storage hardware |
| Super Seven | `angel_number` | 999 (Crown) | 7 | 7 constituent minerals; sacred number 7 is the crystal's explicit identity marker |

---

## 9. Validation Checklist for New Entries

Before committing a new crystal to any batch file, verify:

### Physical Layer
- [ ] `hardness_min` and `hardness_max` are sourced from Mindat or IMA data
- [ ] `piezoelectric` flag set correctly (quartz family = true; most silicates = false)
- [ ] `safe_for_water` flag set correctly (check for sulfates, sulfides, soft carbonates)
- [ ] `safe_for_hardware` flag cross-checked against piezoelectric and magnetic status
- [ ] `crystal_system` uses canonical value (prefer `'Cubic'` over `'Isometric'`)

### Color Layer
- [ ] `oklch.h` (hue angle) is consistent with `dominant_wavelength_nm`
  - Violet: 380–450 nm → h ≈ 285–310
  - Blue: 450–495 nm → h ≈ 240–285
  - Green: 495–570 nm → h ≈ 140–175
  - Yellow: 570–590 nm → h ≈ 95–115
  - Orange: 590–620 nm → h ≈ 60–95
  - Red: 620–750 nm → h ≈ 25–45
- [ ] `color_layer` is `'natural'`, `'treated'`, or `'coating'` (not guessed)
- [ ] `hex` is null for iridescent/multicolor stones

### Metaphysical Layer
- [ ] `angel_number` derived using the §3.2 decision tree (document which rule applied)
- [ ] `gaia_resonance` derived using §4.2 rules (document which properties triggered which modules)
- [ ] `gaia_resonance` string uses ` + ` separator and canonical module order
- [ ] `safety_warning` populated if any hazard exists (never null-suppress a known hazard)
- [ ] `numerology` is the Pythagorean reduction of the crystal's mineral count or
  established traditional number — never derived from the crystal's name

### Record Level
- [ ] `trade_name` is `true` if the display name is a variety/trade name
- [ ] `yin_yang_pair` is either null or references a crystal already in the registry
- [ ] If `yin_yang_pair` is set, the paired crystal's record also references back
- [ ] Exception Registry (§8) updated if any standard rule was overridden

---

*Last updated: 2026-05-30 — initial canonical version*
*Maintainer: GAIA-OS Core Contributors*
*Closes: #107*

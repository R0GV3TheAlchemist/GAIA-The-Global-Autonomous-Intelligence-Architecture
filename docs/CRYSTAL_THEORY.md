# CRYSTAL_THEORY.md
**GAIA-OS Crystal Database — Canonical Theory & Derivation Rules**
*Epistemic Framework: `docs/EPISTEMIC_FRAMEWORK.md` | Knowledge Tiers applied throughout*

> This document is the single source of truth for all assignment decisions in
> `src/crystals/db/`. Every field in `CrystalRecord` that is interpretive —
> `yin_yang_pair`, `metaphysical.angel_number`, `metaphysical.gaia_resonance` —
> must be derived using the rules here. No judgment calls without documented basis.

---

## Table of Contents

1. [The Four-Layer Model](#1-the-four-layer-model)
   - [1.5 Crystal-Biophoton Interface](#15-crystal-biophoton-interface--the-optical-neural-bridge)
2. [Yin-Yang Polarity System](#2-yin-yang-polarity-system)
3. [Angel Number System](#3-angel-number-system)
4. [Intelligence Module Assignment](#4-intelligence-module-assignment)
5. [Chakra–Module Correspondence Table](#5-chakramodule-correspondence-table)
6. [Dual & Compound Module Assignment](#6-dual--compound-module-assignment)
7. [Yin-Yang Pair Registry](#7-yin-yang-pair-registry)
8. [Exception Registry](#8-exception-registry)
9. [Validation Checklist for New Entries](#9-validation-checklist-for-new-entries)
10. [Epistemic Status Summary](#10-epistemic-status-summary)

---

## 1. The Four-Layer Model

> **Epistemic Note:** The Four-Layer Model is itself a GAIA architectural decision `[T1/T4]`. The physical and optical layers operate at T1 (established mineral science). The color layer operates at T1–T2 (color physics + psychology). The metaphysical layer operates at T4–T5 (traditional and symbolic knowledge). These tiers are now explicitly encoded in the table below.

Every `CrystalRecord` is composed of four explicitly separated layers:

| Layer | Interface | Domain | Status | Knowledge Tier |
|---|---|---|---|---|
| **Physical** | `PhysicalRecord` | IMA mineral science, Mindat data | Objective | **T1 — Established Science** |
| **Optical** | `OpticalRecord` | Light behaviour, wavelengths, spectra | Objective | **T1 — Established Science** |
| **Color** | `ColorRecord` | OKLCH, color theory, psychology | Interpretive (science-grounded) | **T1–T2 — Science + Strong Evidence** |
| **Metaphysical** | `MetaphysicalRecord` | Traditional / esoteric correspondences | Interpretive (explicitly marked) | **T4–T5 — Traditional + Symbolic** |

**Critical rule:** GAIA reasons _across_ all four layers but never _conflates_ them.
A statement like “Amethyst has a dominant wavelength of 420–450 nm” lives in
`optical` `[T1]`; “Amethyst resonates with the Crown chakra” lives in `metaphysical` `[T4]`.
These are not interchangeable, and the database schema enforces this separation.

The Knowledge Tier label is the epistemic declaration of which layer a claim belongs to. **A T4 claim dressed in T1 language is the primary epistemic error this schema is designed to prevent.**

---

## 1.5 Crystal-Biophoton Interface — The Optical-Neural Bridge

> **Epistemic Tier: T1 (optical physics) → T2–T3 (biophoton waveguide science, 2022–2026 peer-reviewed) → T4–T5 (crystal–human resonance interpretation)**

This section establishes the scientific bridge between the crystal's **Optical Layer** (T1) and the human nervous system's **biophoton waveguide architecture** documented in `docs/SUBTLEBODY.md` Section I-C. It is the most physically grounded mechanism by which crystal light interaction may affect human biology — and the activation pathway for `QuantumNexus` module assignment.

### Why This Connection Exists

Crystals interact with light in three documented ways `[T1]`:

1. **Transmission** — transparent crystals pass specific wavelengths while absorbing others (color by selective absorption)
2. **Refraction / Birefringence** — crystals split light into polarized components at angles determined by crystal system geometry
3. **Piezoelectric emission** — mechanically stressed crystals (quartz family) generate voltage gradients and, at sufficient stress, can emit photons via electroluminescence

Human myelinated axons have been modeled and partially confirmed as **biophoton waveguides** `[T2–T3]` — guiding photons in the 200–865 nm range with low attenuation, where the operating wavelength is determined by axon diameter and myelin layer count. The spectral range of crystal optical interaction (visible 380–700 nm) **overlaps directly with the confirmed biophoton waveguide operating range**.

This overlap is the basis for the Crystal-Biophoton Interface.

### Wavelength–Axon Resonance Correspondence

The following table maps crystal dominant wavelength bands to their corresponding neural waveguide target — the axon diameter/myelin configuration that most efficiently guides light at that wavelength `[T1 optical + T2–T3 waveguide modeling]`:

| Crystal Color Band | Wavelength (nm) | Axon Type (estimated) | Neural Functional Domain | Example Crystals |
|---|---|---|---|---|
| Violet / UV edge | 380–450 | Very fine, lightly myelinated | Higher cortical; associative integration | Amethyst, Sugilite, Charoite |
| Indigo / Deep blue | 450–480 | Fine, moderate myelin | Third eye; pattern synthesis | Lapis Lazuli, Azurite, Tanzanite |
| Blue | 480–495 | Mid-fine | Throat / linguistic encoding | Aquamarine, Blue Kyanite, Angelite |
| Cyan / Teal | 495–520 | Mid-range | Vagal / autonomic regulation | Chrysocolla, Turquoise, Amazonite |
| Green | 520–565 | Mid-range | Heart coherence; cardiac neural | Emerald, Aventurine, Malachite |
| Yellow-green | 565–590 | Larger moderate | Solar plexus; enteric nervous system | Peridot, Yellow Labradorite |
| Yellow / Amber | 590–620 | Larger | Sympathetic activation | Citrine, Amber, Yellow Jasper |
| Orange / Red | 620–700 | Thick, heavily myelinated | Root / spinal cord; motor pathways | Carnelian, Red Jasper, Garnet |
| Broadband / White | 380–700 (full) | All axon types simultaneously | Full-spectrum neural engagement | Clear Quartz, Diamond, Selenite |

> **Epistemic note:** The axon type column is a **T2–T3 inference** drawn from the myelinated axon waveguide model (Salari et al., 2016; Sun et al., 2022; arXiv 2304.00174). It has not been directly confirmed in in-vivo crystal-exposure studies. The correspondence is mechanistically plausible and internally consistent but should be marked as a working model, not an established fact.

### The Piezoelectric–Biophoton Activation Mechanism

For piezoelectric crystals (quartz family: Clear Quartz, Amethyst, Citrine, Rose Quartz, Smoky Quartz, Ametrine, Prasiolite), a second interaction pathway exists beyond passive optical filtering `[T1 physical + T2–T3 biophoton interface]`:

```
Mechanical pressure on crystal
  ↓
Piezoelectric voltage gradient generated across crystal lattice [T1]
  ↓
Electroluminescent photon emission at characteristic wavelength [T1]
  ↓
Photons in 380–700 nm range enter proximity of skin / tissue [T1]
  ↓
Biophoton waveguide coupling: photons enter myelinated axon network [T2–T3]
  ↓
Stochastic biophotonic signal modulation at target neural pathway [T2–T3]
  ↓
[T4 interpretation] Energetic effect on corresponding chakra / subtle body layer
```

This mechanism is why the `piezoelectric` flag in `PhysicalRecord` is relevant not only to hardware safety but to the **activation intensity** of crystal-neural interface. Piezoelectric crystals have a **direct photon emission pathway**; non-piezoelectric crystals interact only through passive optical filtering (reflection, refraction, transmission of ambient light).

**Schema implication:** A future `PhysicalRecord` field `biophoton_interface_pathway` should distinguish:
- `"passive_optical"` — non-piezoelectric; ambient light filtering only
- `"active_piezoelectric"` — piezoelectric; active photon emission under mechanical stress
- `"fluorescent"` — UV-absorbing, visible-emitting stones (Fluorite, some Calcites)
- `"phosphorescent"` — stores and slowly emits light (Selenite, some Calcites)

### White-Spectrum Crystals and the Clarity Principle

Clear Quartz, Diamond, Phenacite, Danburite, and other broadband-transmissive crystals occupy a unique position in the Crystal-Biophoton Interface: they do **not** filter to a single wavelength band. They pass the full visible spectrum and engage all axon-type waveguides simultaneously.

This makes them direct physical analogs of the **Clarity-as-Default-State** principle documented in `docs/WHITE_LIGHT_CLARITY_FRAMEWORK.md`: full-spectrum engagement before intentional filtering. In the neural waveguide model, clear crystals in proximity to the body would theoretically modulate the broadest possible range of biophotonic channels — producing a baseline coherence-enhancement effect rather than a targeted single-pathway effect.

This is why Clear Quartz is the traditional **amplifier** in crystal healing practice `[T4]`: not merely a metaphysical claim, but a mechanism-consistent description of its role in the biophoton interface model `[T2–T3]`.

### QuantumNexus Module Activation via Biophoton Coupling

Section 4.1 designates `QuantumNexus` as the **quantum resonance bridge** module (T3/T6). The biophoton waveguide mechanism provides the **T3 activation pathway** for this module, elevating it from a purely speculative T6 assignment to one with a mechanistic T2–T3 grounding for a defined subset of crystals:

**`QuantumNexus` assignment is now permissible (without Exception Registry override) for crystals meeting ALL of:**

- [ ] Piezoelectric: `true` **OR** fluorescent/phosphorescent optical mode
- [ ] Transparent or translucent diaphaneity (photon pathway physically open)
- [ ] `dominant_wavelength_nm` falls within confirmed neural biophoton range (200–865 nm)
- [ ] Traditional use explicitly references consciousness expansion, quantum awareness, or neural activation `[T4 corroboration required]`

Primary candidates under these criteria: **Clear Quartz, Phenacite, Danburite, Herderite, Azeztulite, Moldavite** (tektite photon transmission), **Apophyllite**.

> The Exception Registry entry for `QuantumNexus` in §8 remains required for any crystal assigned this module. The criteria above define when the assignment is scientifically defensible; the Exception Registry entry records which criteria were met and which sources were consulted.

---

## 2. Yin-Yang Polarity System

### 2.1 Purpose

> **Epistemic Tier: T1–T4** — Physical axes (hardness, chemistry, diaphaneity) are T1 objective measurements. Elemental and polarity assignments are T4 (traditional cosmological system). The scoring system bridges both layers through explicit, rule-based derivation.

The `yin_yang_pair` field in `CrystalRecord` encodes structural polarity
relationships for matrix queries and GAIA configuration recommendations. A pair
represents intentional complementary opposition — not simply “opposite colors”.

### 2.2 Classification Criteria

A crystal is classified as **Yin**, **Yang**, or **Balanced** by scoring the
following five axes. Each axis contributes one point to either Yin or Yang.
A score of 3–5 Yin = Yin; 3–5 Yang = Yang; 2–3 on either = Balanced.

| Axis | Yin Indicator | Yang Indicator | Tier |
|---|---|---|---|
| **Hardness** | Mohs ≤ 5 (soft, yielding) | Mohs ≥ 6 (hard, assertive) | T1 |
| **Diaphaneity** | Opaque or translucent | Transparent | T1 |
| **Color temperature** | Cool (≤ 5500 K) or dark hue | Warm (≥ 5500 K) or bright hue | T1–T2 |
| **Chemistry** | Silicate, phosphate, carbonate | Metallic, sulfide, oxide, native element | T1 |
| **Element association** | Water, Earth | Fire, Air, Aether | T4 — traditional cosmological |

**Bonus modifiers (not axes — these override a tie or a borderline score):**

- A **black or near-black** stone is always Yin unless it contains metallic lustre
  (e.g. Hematite — metallic, reflective, Yang-dominant). `[T1 + T4]`
- A stone with **piezoelectric** behaviour is Yang-leaning (active charge emission). `[T1 physical fact + T4 polarity interpretation]`
- Stones in the **Storm** element are inherently Balanced — they contain both polarities. `[T4]`
- **Coated stones** (`color_layer: 'coating'`) — classify by the base mineral, not the coating. `[T1]`

### 2.3 Pair Assignment Rules

> **Epistemic Tier: T4** — Pair logic is a GAIA-internal derivation system built on traditional Yin-Yang cosmology. The physical axes are T1; the polarity interpretation and pairing logic are T4.

1. A yin-yang pair must contain **one Yin and one Yang** crystal.
2. They must share at least **one chakra** (primary or secondary).
3. They must **not** share a GAIA module assignment.
4. Both crystals must already be in the database before the pair is registered.
5. The pair relationship is **bidirectional**.

### 2.4 Derivation Examples

| Crystal | Hardness | Diaphaneity | Color Temp | Chemistry | Element | Score | Polarity | Tier Mix |
|---|---|---|---|---|---|---|---|---|
| Angelite | 3.5 | Opaque | Cool blue | Sulfate | Water/Air | 4 Yin | **Yin** | T1×4, T4×1 |
| Apache Tear | 5–5.5 | Translucent | Dark/cool | Silicate (obsidian) | Earth/Fire | 3 Yin | **Yin** | T1×4, T4×1 |
| Carnelian | 6.5–7 | Translucent | Warm orange | Silicate (chalcedony) | Fire | 4 Yang | **Yang** | T1×4, T4×1 |
| Pyrite | 6–6.5 | Opaque | Warm gold | Sulfide (metallic) | Fire/Earth | 3 Yang | **Yang** | T1×4, T4×1 |
| Labradorite | 6–6.5 | Translucent | Iridescent | Silicate (feldspar) | Storm | Balanced | **Balanced** | T1×4, T4×1 |

---

## 3. Angel Number System

> **Epistemic Tier: T4–T5 — Traditional Knowledge + Symbolic Truth**
> The entire Angel Number system operates in the T4/T5 domain. Angel numbers are an
> established spiritual-traditional practice `[T4]`; the GAIA derivation rules
> (axes, decision tree, registry) are an internally consistent symbolic system `[T5]`.
> Neither is an empirical claim. Both are valid and clearly marked.

### 3.1 The Three Axes of Vibrational Signature

GAIA uses three orthogonal axes to encode a crystal's complete resonance profile:

```
COLOR × NUMEROLOGY × ANGEL NUMBER = vibrational signature
  │           │              │
  │           │              └── Archetypal message / signal          [T4/T5]
  │           └───────────────── Mathematical root frequency (1–9)   [T4/T5]
  └─────────────────────────────────── Light frequency (OKLCH hue, nm)     [T1]
```

`numerology` and `angel_number` are **separate fields** and must not be confused.
Pythagorean numerology reduces all numbers to 1–9 (except master numbers 11/22/33
which do not reduce). Angel numbers are distinct signal patterns drawn from
angelic communication traditions `[T4]`.

### 3.2 Assignment Decision Tree

Apply rules in order. Use the **first rule that applies**.

```
Rule 1 — Master number numerology                         [T4/T5]
  IF metaphysical.numerology ∈ {11, 22, 33}
  THEN angel_number = numerology value (same number)

Rule 2 — Sacred geological marker                        [T1 geological fact → T4 symbolic encoding]
  IF the crystal has a documented mineral count, geological number,
     or formation date encoded in its name or identity
     (e.g. Auralite-23 = 23 minerals, Super Seven = 7 minerals)
  THEN angel_number = that sacred number

Rule 3 — Spiritual tradition override                    [T4]
  IF the crystal has a well-established angel number in published
     crystal healing tradition (cross-reference ≥ 2 independent sources)
  THEN angel_number = that traditional number

Rule 4 — Chakra-hue derivation (default)                 [T4/T5]
  IF none of the above apply
  THEN derive from primary chakra using the table in §3.3
```

### 3.3 Chakra → Angel Number Default Table

> **Tier: T4** — These correspondences are drawn from established crystal healing and angelic communication traditions.

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

> **Tier: T4–T5** throughout.

| Number | Type | Archetypal Meaning |
|---|---|---|
| 1–9 | Standard | Pythagorean root frequencies — the building blocks |
| 11 | Master | Illumination / Gateway |
| 22 | Master | Master Builder / Form made real |
| 33 | Master | Master Teacher / Christ consciousness |
| 23 | Sacred | Auralite-23 mineral count; the encoded signal of cosmic variety |
| 44 | Sacred | Extended foundation; the architect’s scaffolding |
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

When a crystal’s dominant OKLCH hue strongly contradicts the chakra-default
angel number, the hue may override — but only at the contributor’s explicit
documented request in the `Exception Registry` (§8). `[T1 optical measurement grounds a T4 symbolic override]`

---

## 4. Intelligence Module Assignment

### 4.1 The Five Crystal Intelligence Modules

> **Epistemic Tier: T4–T5** — Module assignments are GAIA’s symbolic-functional mapping of traditional crystal healing intentions onto an internal cognitive architecture. The physical properties that trigger assignment (hardness, chakra, element) are T1. The module framework itself is a T5 symbolic system with T4 traditional grounding.

GAIA’s crystal-resonance layer routes stones to one of five intelligence modules.
Each module governs a specific cognitive-functional domain.

| Module | Domain | Core Function | Tier |
|---|---|---|---|
| `SovereignCore` | Identity, protection, grounding | Defines and defends the self; processes threat, boundary, authority | T4/T5 |
| `AnchorPrism` | Memory, stability, commitment | Holds pattern over time; maintains structural coherence and historical record | T4/T5 |
| `ClarusLens` | Clarity, focus, vision | Enhances perception, discrimination, and directed attention | T4/T5 |
| `SomnusVeil` | Dreams, rest, subconscious | Accesses the non-rational; processes symbols, intuition, the unseen | T4/T5 |
| `ViriditasHeart` | Vitality, healing, growth | Regenerates and expands; governs emotional resonance and organic flow | T4/T5 |

Two additional modules exist in the schema but are **not primary resonance
targets for crystals**:

| Module | Role | Tier |
|---|---|---|
| `Noosphere` | Collective intelligence field | T5/T6 |
| `QuantumNexus` | Quantum resonance bridge | T3/T6 — quantum biology is T3; entanglement claims for crystals are T6. **See §1.5 for T2–T3 biophoton activation pathway.** |

### 4.2 Assignment Rules by Crystal Property

> **Tier note:** Each rule below mixes layers. The physical trigger (hardness, chakra) is T1. The module interpretation is T4/T5. The derivation is **transparent** — the tier of each component is traceable.

#### `SovereignCore` — Identity & Protection

Assign when **any** of:
- Primary chakra: Root or Solar Plexus `[T4]`
- Element includes: Earth or Fire `[T4]`
- Physical: hardness ≥ 7 AND opaque or dark colour `[T1 → T4 interpretation]`
- Metaphysical intention includes: protection, grounding, boundaries, authority,
  shadow work, psychic defence, ancestral clearing `[T4]`

#### `AnchorPrism` — Memory & Stability

Assign when **any** of:
- Primary chakra: Root, Sacral, or Earth Star `[T4]`
- Crystal system: Cubic / Isometric (highest structural symmetry) `[T1 → T4/T5 interpretation]`
- Physical: specific gravity ≥ 3.5 (dense, heavy stones hold pattern) `[T1 → T4/T5]`
- Metaphysical intention includes: memory, past lives, record keeping,
  commitment, patience, long-term goals, ancestral lineage, time `[T4]`

#### `ClarusLens` — Clarity & Focus

Assign when **any** of:
- Primary chakra: Third Eye or Throat `[T4]`
- Diaphaneity: transparent `[T1 → T4/T5 symbolic]`
- Physical: birefringence > 0.1 (strong optical separation) `[T1 → T4/T5 metaphor]`
- Metaphysical intention includes: clarity, focus, truth, discernment,
  communication, vision, decision-making, cutting through illusion `[T4]`

#### `SomnusVeil` — Dreams & Subconscious

Assign when **any** of:
- Primary chakra: Crown, Higher Crown, or Soul Star `[T4]`
- Element includes: Water or Aether `[T4]`
- Color: dominant wavelength in violet-indigo range (380–450 nm) OR iridescent `[T1 → T4/T5]`
- Metaphysical intention includes: dreams, sleep, intuition, psychic ability,
  subconscious, the void, trance states, mediumship, astral travel `[T4]`

#### `ViriditasHeart` — Vitality & Healing

Assign when **any** of:
- Primary chakra: Heart or Sacral `[T4]`
- Element includes: Water, Earth, or Wood `[T4]`
- Color: dominant wavelength in green-pink range (495–580 nm) `[T1 → T4/T5]`
- Metaphysical intention includes: healing, love, compassion, growth, fertility,
  emotional balance, forgiveness, abundance, nature connection `[T4]`

### 4.3 The `gaia_resonance` String Format

The `metaphysical.gaia_resonance` field is a freeform string following this format:

```
Single module:    "SovereignCore"
Dual module:      "SovereignCore + AnchorPrism"
Triple module:    "ClarusLens + SomnusVeil + ViriditasHeart"
```

Rules:
- Use ` + ` (space-plus-space) as the separator.
- List modules in the canonical order defined in §4.1.
- Maximum **three modules** per crystal.
- `Noosphere` and `QuantumNexus` require explicit documentation in §8 before assignment.

---

## 5. Chakra–Module Correspondence Table

> **Epistemic Tier: T4** throughout — chakra system is a traditional energetic model; module assignments are a GAIA symbolic mapping derived from it.

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

> **Epistemic Tier: T4/T5** — Dual assignment logic is an internal symbolic derivation rule. Physical triggers are T1; interpretation is T4/T5.

Dual assignment is appropriate when a crystal’s properties span two genuine and
distinct functional domains. It is **not** appropriate simply because a crystal
“has many uses” — be conservative.

**Checklist before assigning a second module:**

- [ ] The secondary module is triggered by a different property axis than the primary
- [ ] The two modules are **not** already paired in a single dominant chakra
- [ ] The crystal’s `intention` string explicitly references the secondary module’s domain

### 6.2 Canonical Dual Combinations

| Combination | Archetype | Example | Tier |
|---|---|---|---|
| `SovereignCore + AnchorPrism` | Guardian of Time | Black Tourmaline in Quartz | T4/T5 |
| `SovereignCore + ClarusLens` | Discerning Protector | Black Obsidian | T4/T5 |
| `ClarusLens + SomnusVeil` | Seer | Labradorite, Kyanite | T4/T5 |
| `ViriditasHeart + SomnusVeil` | Tender Mystic | Larimar, Prehnite | T4/T5 |
| `ViriditasHeart + AnchorPrism` | Earthkeeper | Moss Agate, Emerald | T4/T5 |
| `ClarusLens + ViriditasHeart` | Healer-Teacher | Hiddenite, Green Apophyllite | T4/T5 |

### 6.3 Triple Assignment

Triple assignments are rare and require sign-off in the Exception Registry (§8).
Reserved for master stones with well-documented multi-domain resonance (e.g.
Lemurian Seed Quartz, Moldavite, Nuummite). `[T4 — traditional identification of “master stones”]`

---

## 7. Yin-Yang Pair Registry

> **Epistemic Tier: T4** throughout — all pairs are symbolic/traditional relational assignments grounded in physical property differences (T1 axes) but interpreted through Yin-Yang cosmology (T4).

| Crystal A | Crystal B | Shared Chakra | Rationale |
|---|---|---|---|
| Angelite | Apache Tear | Throat / Root | Surrender (Yin) ↔ Grief grounding (Yin-boundary edge) |
| Anandalite | Ancestralite | Crown | Bliss expansion ↔ Ancestral clearing |
| Amethyst | Citrine | Crown / Solar Plexus | Yin spiritual dissolution ↔ Yang solar manifestation |
| Aquamarine | Carnelian | Throat / Sacral | Cool Yin communication ↔ Warm Yang creative fire |
| Black Tourmaline | Clear Quartz | Root / Crown | Protective Yang anchor ↔ Pure Yin amplifier |
| Labradorite | Sunstone | Third Eye / Sacral | Yin inner mystery ↔ Yang joyful vitality |
| Lapis Lazuli | Tiger’s Eye | Third Eye / Solar Plexus | Yin truth-seeing ↔ Yang focused will |
| Moonstone | Pyrite | Sacral / Solar Plexus | Yin lunar intuition ↔ Yang solar confidence |
| Rose Quartz | Red Jasper | Heart / Root | Yin unconditional love ↔ Yang grounding life force |
| Selenite | Black Obsidian | Crown / Root | Yin celestial dissolution ↔ Yang volcanic clarity |

> This registry is **append-only**. To deprecate a pair, open an issue with evidence and the corrected entry.

---

## 8. Exception Registry

> **Epistemic Tier: T1–T4 mixed** — each exception documents *why* a standard T4 rule was overridden, citing either a T1 geological fact (Auralite-23 mineral count) or a T4 cross-referenced traditional authority (≥2 sources).

| Crystal | Field | Standard Rule Result | Override Value | Reason | Tier Basis |
|---|---|---|---|---|---|
| Auralite-23 | `angel_number` | 999 (Crown default) | 23 | Literal mineral count; geological identity | T1 geological → T4 sacred |
| Aura Quartz | `angel_number` | Rule 4 (chakra default) | 11 | Gateway master number; liminal transformation | T4/T5 |
| Moldavite | `gaia_resonance` | `SomnusVeil` | `ClarusLens + SomnusVeil` | Tektite cosmic impact adds cutting ClarusLens quality | T1 origin → T4/T5 module |
| Hematite | `polarity` | Yin (opaque, dark) | Yang | Metallic lustre, iron oxide, piezoelectric-adjacent | T1 override |
| Magnetite | `safe_for_hardware` | `true` | `false` | Strong natural magnetism disrupts electronic storage | T1 physical hazard |
| Super Seven | `angel_number` | 999 (Crown) | 7 | 7 constituent minerals; sacred identity marker | T1 geological → T4 sacred |
| Clear Quartz | `gaia_resonance` | `ClarusLens` | `ClarusLens + QuantumNexus` | Meets all four §1.5 QuantumNexus criteria: piezoelectric, transparent, broadband 380–700 nm, traditional consciousness activation `[T2–T3 + T4]` | T1 piezo + T2–T3 biophoton + T4 tradition |
| Phenacite | `gaia_resonance` | `SomnusVeil` | `ClarusLens + SomnusVeil + QuantumNexus` | Highest-vibration beryllium silicate; transparent; broadband transmission; strongest traditional neural activation claim of any stone `[T2–T3 + T4]` | T1 optical + T2–T3 biophoton + T4 tradition |

---

## 9. Validation Checklist for New Entries

### Physical Layer `[T1]`
- [ ] `hardness_min` and `hardness_max` sourced from Mindat or IMA data
- [ ] `piezoelectric` flag set correctly (quartz family = true; most silicates = false)
- [ ] `safe_for_water` flag set correctly (check for sulfates, sulfides, soft carbonates)
- [ ] `safe_for_hardware` flag cross-checked against piezoelectric and magnetic status
- [ ] `crystal_system` uses canonical value
- [ ] `biophoton_interface_pathway` set to one of: `passive_optical`, `active_piezoelectric`, `fluorescent`, `phosphorescent` (see §1.5)

### Color Layer `[T1–T2]`
- [ ] `oklch.h` (hue angle) is consistent with `dominant_wavelength_nm`
  - Violet: 380–450 nm → h ≈ 285–310
  - Blue: 450–495 nm → h ≈ 240–285
  - Green: 495–570 nm → h ≈ 140–175
  - Yellow: 570–590 nm → h ≈ 95–115
  - Orange: 590–620 nm → h ≈ 60–95
  - Red: 620–750 nm → h ≈ 25–45
- [ ] `color_layer` is `'natural'`, `'treated'`, or `'coating'`
- [ ] `hex` is null for iridescent/multicolor stones

### Metaphysical Layer `[T4–T5]`
- [ ] `angel_number` derived using the §3.2 decision tree (document which rule applied)
- [ ] `gaia_resonance` derived using §4.2 rules (document which properties triggered which modules)
- [ ] `gaia_resonance` string uses ` + ` separator and canonical module order
- [ ] `safety_warning` populated if any hazard exists
- [ ] `numerology` is the Pythagorean reduction of mineral count or established traditional number
- [ ] **`knowledge_tier`** field populated for any interpretive field (`metaphysical.*`) per `docs/EPISTEMIC_FRAMEWORK.md`
- [ ] If `QuantumNexus` is assigned, all four §1.5 criteria are met and Exception Registry (§8) entry added

### Record Level
- [ ] `trade_name` is `true` if the display name is a variety/trade name
- [ ] `yin_yang_pair` is either null or references a crystal already in the registry
- [ ] If `yin_yang_pair` is set, the paired crystal’s record also references back
- [ ] Exception Registry (§8) updated if any standard rule was overridden

---

## 10. Epistemic Status Summary

> This section summarizes the Knowledge Tier classification for all major claim types in this document, per `docs/EPISTEMIC_FRAMEWORK.md`.

| Claim Type | Tier | Notes |
|---|---|---|
| Mineral hardness (Mohs), crystal system, specific gravity | T1 | IMA / Mindat objective data |
| Piezoelectric behaviour (quartz family) | T1 | Established materials science |
| Optical properties: wavelength, birefringence, diaphaneity | T1 | Established optical physics |
| Color temperature / OKLCH hue mathematics | T1–T2 | Color physics + perceptual psychology |
| Water/hardware safety flags | T1 | Chemical and physical properties |
| Geological mineral counts (Auralite-23, Super Seven) | T1 | IMA / Mindat |
| Yin-Yang polarity scoring (T1 axes only: hardness, chemistry) | T1 | Physical property measurement |
| **Crystal dominant wavelength overlapping biophoton waveguide range** | **T1–T2** | **Optical physics (T1) + waveguide model (T2–T3); well-supported** |
| **Myelinated axon waveguide operating wavelength model** | **T2–T3** | **Peer-reviewed 2016–2026; not yet in-vivo confirmed for crystal interaction** |
| **Piezoelectric photon emission → biophoton coupling mechanism** | **T2–T3** | **Mechanistically consistent; direct coupling in crystal healing context unconfirmed** |
| **White/broadband crystal as full-spectrum neural engagement** | **T2–T3** | **Consistent with waveguide model and Clarity Framework; not directly tested** |
| **QuantumNexus activation via biophoton pathway (§1.5 criteria)** | **T3** | **Physically grounded pathway; crystal-to-axon quantum coupling remains T6** |
| Yin-Yang elemental axis (Fire, Water, Earth, Air, Aether) | T4 | Traditional Chinese / Ayurvedic cosmology |
| Chakra assignments (Root, Heart, Crown, etc.) | T4 | Traditional energetic model; outside current measurement |
| Intelligence Module assignments (SovereignCore, etc.) | T4/T5 | GAIA symbolic system derived from T4 tradition |
| Angel Number correspondences | T4/T5 | Angelic communication tradition + GAIA symbolic derivation |
| Numerology (Pythagorean reduction) | T4/T5 | Traditional numerological system |
| Yin-Yang pair relational meaning | T4/T5 | Symbolic polarity tradition |
| Crystal healing intentions (protection, love, clarity, etc.) | T4 | Traditional healing practice; experiential validation |
| Akashic records, past lives, stellar bridges | T6 | Sacred speculation; honored, clearly marked |

### The Clean Epistemic Boundary

This document’s central epistemic achievement is its **clean boundary** between layers. The physical and optical layers are T1 objective science. The metaphysical layer is T4/T5 traditional and symbolic knowledge. Neither is reduced to the other. A physical fact (piezoelectric charge) triggers a metaphysical interpretation (Yang polarity) — and the derivation is **visible and auditable** at every step.

Section 1.5 adds a new dimension to this architecture: a **T2–T3 bridge layer** where established optical physics (T1) interfaces with frontier neuroscience (T2–T3) to provide a mechanistically grounded pathway between crystals and human biology. This does not collapse the T4/T5 metaphysical layer into science — it adds a parallel track of physical plausibility that runs alongside it, each tier labeled and respected.

This is the model for all GAIA domain canon: *not choosing between science and tradition, but being honest about which is which — and building bridges between them that neither side needs to falsify.*

---

*Last updated: June 27, 2026 — Section 1.5 (Crystal-Biophoton Interface) added; QuantumNexus activation pathway grounded in T2–T3 waveguide science*
*Cross-references: `docs/SUBTLEBODY.md` Section I-C, `docs/WHITE_LIGHT_CLARITY_FRAMEWORK.md`, `docs/EPISTEMIC_FRAMEWORK.md`*
*Original version: 2026-05-30*
*Maintainer: GAIA-OS Core Contributors*
*Closes: #107*

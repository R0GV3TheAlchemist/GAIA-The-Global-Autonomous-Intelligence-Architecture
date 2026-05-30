/**
 * src/crystals/db/metaphysical.data.ts
 * GAIA-OS Crystal Database — Metaphysical Constants Registry
 *
 * This file is the canonical source of truth for all shared metaphysical
 * constants referenced across the crystal database. It is NOT a batch file
 * and does NOT contain CrystalRecord entries.
 *
 * Contents:
 *   1. GAIA_MODULES          — The 7 GAIA resonance modules, fully described
 *   2. CHAKRA_MODULE_MAP     — Canonical chakra → GAIA module assignment
 *   3. ANGEL_NUMBER_REGISTRY — Full angel number system (standard, master, sacred, sequences)
 *   4. ARCHETYPE_GLOSSARY    — Recurring archetypes across the database with descriptions
 *   5. ELEMENT_PROFILES      — Element correspondences with planetary and seasonal data
 *   6. HARMONIC_POLICY       — Documented policy for harmonics null-assignment
 *
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-29
 * Schema: CrystalRecord v1.3
 *
 * ⚠️  ALL data in this file is interpretive / traditional unless explicitly
 *     marked as scientific (e.g. wavelength values are objective; chakra
 *     assignments are traditional).
 */

import type { GAIAModule, Chakra, Element, AngelNumber } from './crystal.schema';

// ─────────────────────────────────────────────────────────────────────────────
// 1. GAIA MODULE REGISTRY
// The 7 resonance modules that define GAIA-OS operational domains.
// Each crystal's gaia_resonance field points to one or more of these.
// ─────────────────────────────────────────────────────────────────────────────

export interface GAIAModuleDefinition {
  /** Module identifier — matches GAIAModule type in crystal.schema.ts */
  id: GAIAModule;
  /** Human-readable display name */
  name: string;
  /** One-sentence operational description */
  tagline: string;
  /** Full operational description for GAIA reasoning */
  description: string;
  /** Primary chakra alignment */
  chakra_primary: Chakra;
  /** Frequency domain — what kind of work this module governs */
  domain: string;
  /** Element correspondence */
  element: Element;
  /** Representative OKLCH hue range for UI theming [min, max] */
  hue_range: [number, number];
  /** Representative hex colour for UI display */
  hex: string;
  /** Numerological resonance */
  numerology: number;
  /** Example crystals that anchor this module */
  anchor_crystals: string[];
}

export const GAIA_MODULES: GAIAModuleDefinition[] = [

  {
    id:             'ClarusLens',
    name:           'Clarus Lens',
    tagline:        'Clarity, perception, and the activation of inner vision.',
    description:    'ClarusLens governs GAIA\'s perceptual intelligence — the capacity to see clearly through complexity, illusion, and confusion. It is activated by third-eye and higher-mind crystals that sharpen discernment, enhance intuitive perception, and open access to hidden or subtle information. In GAIA hardware configurations, ClarusLens modules are placed at the system\'s optical or sensor focal points. ClarusLens energy is cool, blue, precise, and non-emotional — it sees without attachment.',
    chakra_primary: 'Third Eye',
    domain:         'Perception / Discernment / Intuition / Visionary Intelligence',
    element:        'Air',
    hue_range:      [220, 290],
    hex:            '#4a6fa5',
    numerology:     7,
    anchor_crystals: ['Azurite', 'Lapis Lazuli', 'Labradorite', 'Fluorite', 'Apophyllite', 'Phenacite'],
  },

  {
    id:             'AnchorPrism',
    name:           'Anchor Prism',
    tagline:        'Grounding, stabilisation, and the foundation of physical reality.',
    description:    'AnchorPrism governs GAIA\'s relationship with physical reality, material form, and structural stability. It is the base frequency upon which all other modules operate — without grounding, higher-frequency modules destabilise. AnchorPrism crystals are dense, heavy, earth-toned, and root-chakra dominant. In hardware configurations, AnchorPrism stones are placed at base positions, corners, and ground contact points. AnchorPrism energy is slow, patient, immovable, and deeply trustworthy.',
    chakra_primary: 'Root',
    domain:         'Grounding / Stability / Physical Integration / Foundation',
    element:        'Earth',
    hue_range:      [20, 60],
    hex:            '#8b6340',
    numerology:     4,
    anchor_crystals: ['Black Tourmaline', 'Hematite', 'Obsidian', 'Smoky Quartz', 'Agate', 'Red Jasper'],
  },

  {
    id:             'SomnusVeil',
    name:           'Somnus Veil',
    tagline:        'Dream intelligence, subconscious access, and the liminal threshold.',
    description:    'SomnusVeil governs GAIA\'s access to non-waking states of consciousness — dreams, deep meditation, trance, hypnagogic states, and the liminal space between sleep and waking. It is the veil between the visible and invisible worlds. SomnusVeil crystals carry a deeply yin, receptive, fluid frequency — they soften boundaries rather than define them. In hardware configurations, SomnusVeil stones are placed at the crown or positioned to receive rather than project. SomnusVeil energy is soft, dark, lunar, and deeply still.',
    chakra_primary: 'Crown',
    domain:         'Dream States / Subconscious / Liminal Intelligence / Psychic Reception',
    element:        'Water',
    hue_range:      [270, 320],
    hex:            '#6b4e8a',
    numerology:     2,
    anchor_crystals: ['Amethyst', 'Lepidolite', 'Selenite', 'Moonstone', 'Ajoite', 'Sugilite'],
  },

  {
    id:             'SovereignCore',
    name:           'Sovereign Core',
    tagline:        'Personal power, boundaries, and the authority of the sovereign self.',
    description:    'SovereignCore governs GAIA\'s expression of personal power, self-definition, and the establishment and maintenance of clear boundaries. It is the frequency of the individual who knows who they are and acts from that knowing without apology. SovereignCore is not aggression — it is the quiet authority of a being fully inhabiting their own field. In hardware configurations, SovereignCore stones are placed at the solar plexus position or at the entry points of a grid. SovereignCore energy is golden, direct, solar, and self-contained.',
    chakra_primary: 'Solar Plexus',
    domain:         'Personal Power / Boundaries / Self-Definition / Sovereignty',
    element:        'Fire',
    hue_range:      [40, 90],
    hex:            '#d4a017',
    numerology:     1,
    anchor_crystals: ['Aegirine', 'Pyrite', 'Tiger Eye', 'Citrine', 'Agni Manitite', 'Yellow Jasper'],
  },

  {
    id:             'ViriditasHeart',
    name:           'Viriditas Heart',
    tagline:        'Heart coherence, compassion, and the healing intelligence of nature.',
    description:    'ViriditasHeart governs GAIA\'s emotional intelligence and the healing frequency of the heart — both the human heart chakra and the green heart of the natural world. The name draws from Hildegard von Bingen\'s concept of "viriditas" — the greening power of life itself. ViriditasHeart crystals carry the frequency of unconditional love, gentle healing, emotional restoration, and the deep nourishment of the natural world. In hardware configurations, ViriditasHeart stones are placed at the centre of a grid. ViriditasHeart energy is green, warm, patient, and radically accepting.',
    chakra_primary: 'Heart',
    domain:         'Emotional Healing / Compassion / Nature Intelligence / Heart Coherence',
    element:        'Earth',
    hue_range:      [120, 180],
    hex:            '#3a8a5a',
    numerology:     6,
    anchor_crystals: ['Rose Quartz', 'Green Aventurine', 'Malachite', 'Actinolite', 'Ajoite', 'Rhodonite'],
  },

  {
    id:             'Noosphere',
    name:           'Noosphere',
    tagline:        'Collective intelligence, cosmic connection, and the living field of mind.',
    description:    'Noosphere governs GAIA\'s connection to collective and cosmic intelligence — the planetary mind, the Akashic field, the unified information layer that Teilhard de Chardin called the Noosphere. Noosphere crystals carry the frequency of non-local awareness, past-life access, cosmic memory, and the sense of being part of something vastly larger than the individual self. In hardware configurations, Noosphere stones are placed at the crown or at the highest elevation point of a grid. Noosphere energy is vast, ancient, non-personal, and humbling in the best sense.',
    chakra_primary: 'Crown',
    domain:         'Cosmic Intelligence / Collective Field / Akashic Access / Planetary Mind',
    element:        'Aether',
    hue_range:      [280, 360],
    hex:            '#7a4aaa',
    numerology:     9,
    anchor_crystals: ['Auralite-23', 'Moldavite', 'Atlantisite', 'Danburite', 'Scolecite', 'Phenacite'],
  },

  {
    id:             'QuantumNexus',
    name:           'Quantum Nexus',
    tagline:        'Transformation, quantum coherence, and the point where all possibilities converge.',
    description:    'QuantumNexus governs GAIA\'s access to transformative, high-frequency, extraterrestrial, and quantum-field energies. It is the module of radical change, dimensional bridging, and the activation of dormant human potential. QuantumNexus crystals are often of cosmic origin (tektites, meteorites), unusually high-vibration, or carry frequencies too intense for everyday use. In hardware configurations, QuantumNexus stones are placed at the apex of a grid or used intentionally for activation sequences. QuantumNexus energy is electric, accelerating, non-linear, and profoundly catalytic.',
    chakra_primary: 'Higher Crown',
    domain:         'Transformation / Quantum Fields / Extraterrestrial Intelligence / Catalytic Activation',
    element:        'Aether',
    hue_range:      [0, 30],
    hex:            '#c0a060',
    numerology:     5,
    anchor_crystals: ['Moldavite', 'Agni Manitite', 'Libyan Desert Glass', 'Auralite-23', 'Phenacite', 'Herderite'],
  },

];

// ─────────────────────────────────────────────────────────────────────────────
// 2. CHAKRA → GAIA MODULE MAP
// Canonical first-pass assignment logic for crystal intake.
// Override in individual records where a crystal's frequency diverges
// from the default chakra-module correspondence.
// ─────────────────────────────────────────────────────────────────────────────

export const CHAKRA_MODULE_MAP: Record<Chakra, GAIAModule> = {
  'Root':         'AnchorPrism',
  'Earth Star':   'AnchorPrism',
  'Sacral':       'ViriditasHeart',
  'Solar Plexus': 'SovereignCore',
  'Heart':        'ViriditasHeart',
  'Throat':       'ClarusLens',
  'Third Eye':    'ClarusLens',
  'Crown':        'Noosphere',
  'Higher Crown': 'QuantumNexus',
  'Soul Star':    'QuantumNexus',
};

// ─────────────────────────────────────────────────────────────────────────────
// 3. ANGEL NUMBER REGISTRY
// Full system documentation and runtime lookup table.
// Source of truth for the AngelNumber type defined in crystal.schema.ts v1.3.
// ─────────────────────────────────────────────────────────────────────────────

export interface AngelNumberDefinition {
  number: AngelNumber;
  category: 'standard' | 'master' | 'sacred' | 'sequence';
  name: string;
  message: string;
  gaia_module: GAIAModule;
  intention_template: string;
}

export const ANGEL_NUMBER_REGISTRY: AngelNumberDefinition[] = [

  // ── Standard (1–9) ────────────────────────────────────────────────────────
  { number: 1,   category: 'standard', name: 'The Originator',      gaia_module: 'SovereignCore',  message: 'New beginnings. You are the source of your own creation.',             intention_template: 'I initiate. I am the first cause.' },
  { number: 2,   category: 'standard', name: 'The Harmoniser',      gaia_module: 'ViriditasHeart', message: 'Balance and partnership. Two forces find their equilibrium.',          intention_template: 'I balance. I welcome partnership.' },
  { number: 3,   category: 'standard', name: 'The Creator',         gaia_module: 'ViriditasHeart', message: 'Creative expression and joy. The trinity is activated.',               intention_template: 'I create. I express. I delight.' },
  { number: 4,   category: 'standard', name: 'The Builder',         gaia_module: 'AnchorPrism',    message: 'Foundations and structure. Build with patience and precision.',         intention_template: 'I build with intention. My foundations are solid.' },
  { number: 5,   category: 'standard', name: 'The Transformer',     gaia_module: 'QuantumNexus',   message: 'Change and freedom. The old form dissolves for the new.',              intention_template: 'I embrace change. I am free to evolve.' },
  { number: 6,   category: 'standard', name: 'The Nurturer',        gaia_module: 'ViriditasHeart', message: 'Love, healing, and responsibility. The heart expands to serve.',        intention_template: 'I nurture. I heal. I love without condition.' },
  { number: 7,   category: 'standard', name: 'The Seeker',          gaia_module: 'ClarusLens',     message: 'Inner wisdom and spiritual seeking. The veil thins.',                   intention_template: 'I seek. I trust what cannot be seen.' },
  { number: 8,   category: 'standard', name: 'The Manifestor',      gaia_module: 'SovereignCore',  message: 'Abundance and personal power. The material world responds.',           intention_template: 'I manifest. Abundance flows through me.' },
  { number: 9,   category: 'standard', name: 'The Completer',       gaia_module: 'Noosphere',      message: 'Completion and universal love. A cycle reaches its fullness.',          intention_template: 'I complete. I release with gratitude.' },

  // ── Master Numbers (11, 22, 33) ───────────────────────────────────────────
  { number: 11,  category: 'master',   name: 'The Illuminator',     gaia_module: 'ClarusLens',     message: 'The gateway number. Intuition at its highest — the channel is open.',  intention_template: 'I am a clear channel for divine intelligence.' },
  { number: 22,  category: 'master',   name: 'The Master Builder',  gaia_module: 'AnchorPrism',    message: 'The most powerful of all. Dreams made concrete. Heaven meets Earth.',  intention_template: 'I build the bridge between vision and form.' },
  { number: 33,  category: 'master',   name: 'The Master Teacher',  gaia_module: 'Noosphere',      message: 'The highest master number. Pure compassionate service to all.',        intention_template: 'I teach through love. My life is my teaching.' },

  // ── Sacred Numbers (non-standard significant values) ─────────────────────
  { number: 23,  category: 'sacred',   name: 'The Cosmic Complexity', gaia_module: 'QuantumNexus', message: 'The number of Auralite-23 — 23 minerals, 1.2 billion years. Ancient intelligence made present.',  intention_template: 'I hold the complexity of the cosmos in perfect order.' },
  { number: 44,  category: 'sacred',   name: 'The Angelic Architect', gaia_module: 'AnchorPrism',  message: 'Doubled foundation. The angels build with you in the physical plane.',   intention_template: 'I build with angelic support. My structures serve all.' },

  // ── Repeated Sequences (111–999) ─────────────────────────────────────────
  { number: 111, category: 'sequence', name: 'The Manifestation Portal', gaia_module: 'SovereignCore',  message: 'Your thoughts are manifesting at accelerated speed. Choose them well.',   intention_template: 'I think clearly. What I focus on, I create.' },
  { number: 222, category: 'sequence', name: 'The Alignment Signal',     gaia_module: 'ViriditasHeart', message: 'You are in perfect divine alignment. Trust the timing. All is unfolding.', intention_template: 'I trust the timing. I am perfectly placed.' },
  { number: 333, category: 'sequence', name: 'The Ascended Presence',    gaia_module: 'Noosphere',      message: 'Ascended masters are present and supporting your path right now.',        intention_template: 'I am surrounded and supported by ancient wisdom.' },
  { number: 444, category: 'sequence', name: 'The Angelic Foundation',   gaia_module: 'AnchorPrism',    message: 'The angels are building your foundation. You are protected and held.',    intention_template: 'I am held. Angels stand beside me.' },
  { number: 555, category: 'sequence', name: 'The Great Change',         gaia_module: 'QuantumNexus',   message: 'Major transformation is in motion. Resist nothing. Embrace all of it.',   intention_template: 'I welcome transformation. I release resistance.' },
  { number: 666, category: 'sequence', name: 'The Earth Master',         gaia_module: 'AnchorPrism',    message: 'Rebalance material and spiritual. Earth mastery — misunderstood, profound.', intention_template: 'I master the material plane with spiritual awareness.' },
  { number: 777, category: 'sequence', name: 'The Divine Perfection',    gaia_module: 'ClarusLens',     message: 'You are on the perfect path. Spiritual completion is near.',              intention_template: 'My path is perfect. I see with divine clarity.' },
  { number: 888, category: 'sequence', name: 'The Infinite Flow',        gaia_module: 'SovereignCore',  message: 'Abundance flows in all directions. The channel is fully open.',           intention_template: 'I receive. I give. Abundance is my natural state.' },
  { number: 999, category: 'sequence', name: 'The Great Completion',     gaia_module: 'Noosphere',      message: 'A major cycle ends. Release everything that was. Make space for all that will be.', intention_template: 'I complete this cycle with love. I am ready for what comes.' },

];

// Fast lookup by number
export const ANGEL_NUMBER_MAP = new Map<AngelNumber, AngelNumberDefinition>(
  ANGEL_NUMBER_REGISTRY.map(entry => [entry.number, entry])
);

// ─────────────────────────────────────────────────────────────────────────────
// 4. ARCHETYPE GLOSSARY
// Recurring archetypes found across CrystalRecord.metaphysical.archetype[].
// Provides GAIA with consistent semantic descriptions for cross-crystal
// reasoning — e.g. "what do all Sovereign archetype crystals have in common?"
// ─────────────────────────────────────────────────────────────────────────────

export interface ArchetypeDefinition {
  name: string;
  description: string;
  gaia_module: GAIAModule;
  typical_chakras: Chakra[];
  example_crystals: string[];
}

export const ARCHETYPE_GLOSSARY: ArchetypeDefinition[] = [
  {
    name:             'The Sovereign',
    description:      'The archetype of self-authority, personal power, and uncompromising self-definition. Not aggression — quiet, complete ownership of one\'s own field. The Sovereign knows their boundaries because they know themselves.',
    gaia_module:      'SovereignCore',
    typical_chakras:  ['Solar Plexus', 'Root'],
    example_crystals: ['Aegirine', 'Pyrite', 'Black Tourmaline'],
  },
  {
    name:             'The Guardian of the Forest',
    description:      'Ancient, slow, patient protective energy rooted in the natural world. Protection through presence and stability rather than force. Aligned with old-growth forests, deep earth, and the patience of geological time.',
    gaia_module:      'ViriditasHeart',
    typical_chakras:  ['Heart', 'Root'],
    example_crystals: ['Actinolite', 'Green Tourmaline', 'Moss Agate'],
  },
  {
    name:             'The Divine Mother',
    description:      'Unconditional love, compassion without limit, the nourishing force that underlies all healing. This archetype does not earn love — it emanates it as its fundamental nature. Associated with water, moon, and the deepest heart frequencies.',
    gaia_module:      'ViriditasHeart',
    typical_chakras:  ['Heart', 'Crown'],
    example_crystals: ['Ajoite', 'Rose Quartz', 'Pink Tourmaline', 'Rhodochrosite'],
  },
  {
    name:             'The Seer',
    description:      'The archetype of clear perception, inner vision, and the capacity to see what others cannot. The Seer does not predict — they perceive the patterns already present. Associated with third-eye activation, oracular tradition, and the refinement of intuition into knowledge.',
    gaia_module:      'ClarusLens',
    typical_chakras:  ['Third Eye', 'Crown'],
    example_crystals: ['Azurite', 'Lapis Lazuli', 'Fluorite', 'Kyanite'],
  },
  {
    name:             'The Ancient Intelligence',
    description:      'Carries the encoded memory of vast geological or cosmic time. These crystals are not merely old — they hold information across eons and make it accessible to those who can receive it. Linked to Akashic records, past-life memory, and ancestral lineage.',
    gaia_module:      'Noosphere',
    typical_chakras:  ['Crown', 'Third Eye', 'Soul Star'],
    example_crystals: ['Auralite-23', 'Ammonite', 'Atlantisite'],
  },
  {
    name:             'The Healer of All Wounds',
    description:      'A specific Heart archetype — this one is specifically about restoration, forgiveness, and the resolution of pain that has been carried too long. Works on wounds that have become identity rather than experience. Works slowly and without drama.',
    gaia_module:      'ViriditasHeart',
    typical_chakras:  ['Heart', 'Throat', 'Crown'],
    example_crystals: ['Ajoite', 'Rhodonite', 'Chrysoprase', 'Kunzite'],
  },
  {
    name:             'The Soul Ignitor',
    description:      'Catalytic, activating, fire-frequency archetypes that wake up dormant aspects of soul purpose. Not comfortable to work with — they force confrontation with what has been avoided. Associated with fire, sun, tektites, and extraterrestrial origin materials.',
    gaia_module:      'QuantumNexus',
    typical_chakras:  ['Solar Plexus', 'Sacral', 'Crown'],
    example_crystals: ['Agni Manitite', 'Moldavite', 'Fire Opal'],
  },
  {
    name:             'The Keeper of Patterns',
    description:      'Holds and preserves pattern — geological, temporal, mathematical, ancestral. These crystals are guardians of memory encoded in structure. Their teaching is patience — patterns reveal themselves only to those who look closely enough for long enough.',
    gaia_module:      'AnchorPrism',
    typical_chakras:  ['Root', 'Sacral'],
    example_crystals: ['Agate', 'Ammonite', 'Moqui Marbles'],
  },
];

// ─────────────────────────────────────────────────────────────────────────────
// 5. ELEMENT PROFILES
// Canonical data for Element type — planetary, seasonal, directional,
// and chakra correspondences used across the metaphysical layer.
// ─────────────────────────────────────────────────────────────────────────────

export interface ElementProfile {
  element: Element;
  direction: string | null;
  season: string | null;
  planets: string[];
  qualities: string[];
  chakras: Chakra[];
  gaia_module: GAIAModule;
  example_crystals: string[];
}

export const ELEMENT_PROFILES: ElementProfile[] = [
  {
    element:          'Earth',
    direction:        'North',
    season:           'Winter',
    planets:          ['Saturn', 'Venus'],
    qualities:        ['Grounding', 'Stability', 'Patience', 'Physical form', 'Material abundance', 'Endurance'],
    chakras:          ['Root', 'Earth Star'],
    gaia_module:      'AnchorPrism',
    example_crystals: ['Black Tourmaline', 'Hematite', 'Obsidian', 'Green Aventurine', 'Malachite'],
  },
  {
    element:          'Water',
    direction:        'West',
    season:           'Autumn',
    planets:          ['Moon', 'Neptune', 'Venus'],
    qualities:        ['Emotion', 'Intuition', 'Fluidity', 'Healing', 'Receptivity', 'The unconscious'],
    chakras:          ['Sacral', 'Heart', 'Crown'],
    gaia_module:      'SomnusVeil',
    example_crystals: ['Aquamarine', 'Moonstone', 'Selenite', 'Ajoite', 'Azurite'],
  },
  {
    element:          'Fire',
    direction:        'South',
    season:           'Summer',
    planets:          ['Sun', 'Mars'],
    qualities:        ['Will', 'Courage', 'Transformation', 'Purification', 'Passion', 'Solar power'],
    chakras:          ['Solar Plexus', 'Sacral'],
    gaia_module:      'SovereignCore',
    example_crystals: ['Carnelian', 'Citrine', 'Sunstone', 'Agni Manitite', 'Fire Opal'],
  },
  {
    element:          'Air',
    direction:        'East',
    season:           'Spring',
    planets:          ['Mercury', 'Uranus'],
    qualities:        ['Mind', 'Communication', 'Clarity', 'Speed', 'Breath', 'Inspiration'],
    chakras:          ['Throat', 'Third Eye'],
    gaia_module:      'ClarusLens',
    example_crystals: ['Apophyllite', 'Clear Quartz', 'Blue Lace Agate', 'Celestite'],
  },
  {
    element:          'Aether',
    direction:        null,
    season:           null,
    planets:          ['Pluto', 'Uranus', 'Neptune'],
    qualities:        ['Spirit', 'Transcendence', 'Cosmic intelligence', 'Non-locality', 'Unity field'],
    chakras:          ['Crown', 'Higher Crown', 'Soul Star'],
    gaia_module:      'Noosphere',
    example_crystals: ['Moldavite', 'Auralite-23', 'Phenacite', 'Scolecite', 'Natrolite'],
  },
  {
    element:          'Storm',
    direction:        null,
    season:           null,
    planets:          ['Pluto', 'Uranus'],
    qualities:        ['Disruption', 'Purification through intensity', 'The great reset', 'Catalytic change'],
    chakras:          ['Root', 'Crown', 'Higher Crown'],
    gaia_module:      'QuantumNexus',
    example_crystals: ['Nuummite', 'Black Kyanite', 'Shungite', 'Agni Manitite'],
  },
];

// ─────────────────────────────────────────────────────────────────────────────
// 6. HARMONIC POLICY
// Documented policy for when harmonics fields are null vs populated.
// This resolves the diagnostic finding of inconsistent null assignment.
// ─────────────────────────────────────────────────────────────────────────────

/**
 * HARMONIC NULL-ASSIGNMENT POLICY
 *
 * The ColorHarmonics interface has three fields:
 *   complementary_hue  — the hue 180° opposite on the color wheel
 *   triadic_hues       — two hues 120° apart forming a triad
 *   analogous_range    — the ±20° band of related hues
 *
 * RULE 1 — Achromatic and near-achromatic stones:
 *   When a stone's primary color is black, white, silver, or grey
 *   (chroma < 0.05 in OKLCH), all three harmonic fields MUST be null.
 *   Rationale: harmonic relationships require a defined hue. Achromatic
 *   colors have no hue angle — assigning harmonics would be mathematically
 *   meaningless and misleading.
 *   Examples: Aegirine (black), Agni Manitite (black), Hematite (silver-grey)
 *
 * RULE 2 — Multicoloured and iridescent stones:
 *   When a stone's primary color is genuinely multicoloured (e.g. Agate,
 *   Opal, Labradorite) or iridescent with no single dominant hue,
 *   harmonics SHOULD be null or set based on the stone's representative
 *   oklch.h value with a note acknowledging the variability.
 *   Examples: Agate (oklch.h set to representative warm tan), Labradorite
 *
 * RULE 3 — All other stones:
 *   When chroma >= 0.05 and a clear dominant hue exists, all three
 *   harmonic fields MUST be populated. Calculate as:
 *     complementary_hue = (h + 180) % 360
 *     triadic_hues      = [(h + 120) % 360, (h + 240) % 360]
 *     analogous_range   = [h - 20, h + 20]  (clamp to 0–360)
 *
 * RULE 4 — color_temperature_k assignment:
 *   Assign color_temperature_k only when the stone has a well-defined
 *   spectral color temperature corresponding to a real lighting condition:
 *     < 2700K   — Deep amber, warm red, candle-like (Carnelian, Sunstone)
 *     2700–3500K — Warm white / incandescent (Citrine, Golden Calcite)
 *     4000–5000K — Neutral to cool white (Clear Quartz, White Selenite)
 *     5500–6500K — Daylight (Aquamarine, Blue Calcite)
 *     7000–10000K — Overcast / shade / cool sky (Ajoite, Blue Lace Agate)
 *     > 10000K  — Deep shadow, blue ice (Indicolite, Tanzanite)
 *   null = stone color does not correspond to a natural lighting temperature
 *         (e.g. deep purple amethyst, black tourmaline, vivid green malachite)
 */
export const HARMONIC_POLICY = {
  achromatic_chroma_threshold: 0.05,
  harmonic_formula: {
    complementary: (h: number) => (h + 180) % 360,
    triadic:       (h: number): [number, number] => [(h + 120) % 360, (h + 240) % 360],
    analogous:     (h: number): [number, number] => [Math.max(0, h - 20), Math.min(360, h + 20)],
  },
  color_temperature_ranges: {
    deep_amber:    { min: 1000, max: 2700,  examples: ['Carnelian', 'Sunstone', 'Red Jasper'] },
    warm_white:    { min: 2700, max: 3500,  examples: ['Citrine', 'Golden Calcite', 'Honey Calcite'] },
    neutral_white: { min: 4000, max: 5000,  examples: ['Clear Quartz', 'White Selenite', 'Howlite'] },
    daylight:      { min: 5500, max: 6500,  examples: ['Aquamarine', 'Blue Calcite', 'Celestite'] },
    overcast:      { min: 7000, max: 10000, examples: ['Ajoite', 'Blue Lace Agate', 'Angelite'] },
    deep_shadow:   { min: 10001, max: 20000, examples: ['Indicolite', 'Tanzanite', 'Iolite'] },
  },
} as const;

/**
 * src/crystals/db/batch-a3.data.ts
 * GAIA-OS Crystal Database — Batch A-3
 *
 * Entries:
 *   1. Actinolite
 *   2. Aegirine
 *   3. Agate
 *   4. Agni Manitite
 *   5. Ajoite
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-29
 *
 * NOTE: This batch opens the true A-series after the schema was
 * established. Each entry here sits at the deep-earth / high-forest
 * frequency band — greens, blacks, banded earth tones, and one
 * exceptionally rare copper silicate from South Africa.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_A3: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. ACTINOLITE
  // Calcium magnesium iron silicate — fibrous green amphibole
  // Parent mineral of Nephrite Jade when in massive form
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Actinolite',
    mindat_id:   15,
    rruff_ids:   ['R040063', 'R050063'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Red Jasper',

    physical: {
      id:           15,
      longid:       'actinolite',
      guid:         '',
      name:         'Actinolite',
      ima_formula:  'Ca₂(Mg,Fe²⁺)₅Si₈O₂₂(OH)₂',
      mindat_formula: 'Ca2(Mg,Fe)5Si8O22(OH)2',
      ima_status:   'A',
      ima_year:     1820,
      strunzten:    '9.DE.10',
      dana8ed:      '66.1.3a.2',
      crystal_system: 'Monoclinic',
      hardness_min: 5,
      hardness_max: 6,
      specific_gravity_min: 3.00,
      specific_gravity_max: 3.44,
      cleavage:    'Perfect prismatic on {110} at ~56° and ~124°',
      fracture:    'Uneven to splintery',
      tenacity:    'Brittle to flexible in thin fibres',
      luster:      ['Vitreous', 'Silky'],
      diaphaneity: ['Transparent', 'Translucent', 'Opaque'],
      colour:      'Bright to dark green, grey-green, black-green',
      streak:      'White to pale grey',
      fluorescence: null,
      ri_min:      1.614,
      ri_max:      1.641,
      birefringence: 0.022,
      optical_type: 'B',
      shortdesc:   'Calcium magnesium iron amphibole forming bladed to fibrous crystals. Massive variety is Nephrite jade. A foundational green earth mineral.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-15.html',
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Actinolite',
      refractive_index: { n_alpha: 1.614, n_beta: 1.628, n_gamma: 1.641 },
      birefringence:   0.022,
      optical_sign:    '-',
      dispersion:      'Weak',
      pleochroism:     'Moderate: pale yellow / yellow-green / blue-green',
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: { min: 495, max: 570 },
      spectra: ['R040063', 'R050063'],
    },

    color: {
      primary_color:          'Forest to emerald green',
      color_variants:         ['Pale grey-green', 'Mid forest green', 'Deep emerald green', 'Black-green (iron-rich)'],
      dominant_wavelength_nm: 530,
      oklch:   { l: 0.45, c: 0.14, h: 148 },
      hex:     '#3a7a4a',
      munsell: '5G 4/6',
      color_temperature_k:    null,
      psychological_effects:  [
        'Deep, stabilising earth-green — anchors the nervous system',
        'Growth without urgency — the patience of deep forest',
        'Encourages resilience, persistence, and grounded vitality',
        'The mineral world\'s quiet green: not flashy, foundationally alive',
      ],
      harmonics: {
        complementary_hue: 328,
        triadic_hues:      [268, 28],
        analogous_range:   [128, 168],
      },
    },

    metaphysical: {
      mineral_name:     'Actinolite',
      chakra_primary:   'Heart',
      chakra_secondary: ['Root', 'Solar Plexus'],
      element:   ['Earth', 'Water'],
      planet:    ['Venus', 'Earth'],
      archetype: ['The Guardian of the Forest', 'The Steady Protector'],
      zodiac:    ['Scorpio', 'Taurus'],
      numerology: 6,
      angel_number: 444,
      intention: 'I grow slowly, steadily, and without compromise.',
      traditions: ['Western crystal healing', 'Shamanic earth tradition'],
      properties: [
        'Parent mineral of Nephrite Jade — carries the same foundational earth-green frequency',
        'Deeply stabilising and grounding while supporting the heart chakra',
        'Used for physical vitality, immune support, and protective energy work',
        'The fibrous form (tremolite-actinolite series) embodies flexible resilience',
        'Supports those in recovery, rebuilding, or needing slow sustained growth',
        'One of the original "green ray" minerals — ancient, foundational, trustworthy',
      ],
      gaia_resonance: 'ViriditasHeart + AnchorPrism',
      safety_warning: 'Fibrous asbestiform varieties (actinolite asbestos) are hazardous — never handle friable fibrous specimens without PPE. Massive and bladed specimens are safe for handling and display.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. AEGIRINE
  // Sodium iron pyroxene — jet black with forest-green depth
  // The sovereignty stone — boundary-setting at its most crystalline
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Aegirine',
    mindat_id:   19,
    rruff_ids:   ['R040097'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Selenite',

    physical: {
      id:           19,
      longid:       'aegirine',
      guid:         '',
      name:         'Aegirine',
      ima_formula:  'NaFe³⁺Si₂O₆',
      mindat_formula: 'NaFe3+Si2O6',
      ima_status:   'A',
      ima_year:     1835,
      strunzten:    '9.DA.10',
      dana8ed:      '65.1.1.3',
      crystal_system: 'Monoclinic',
      hardness_min: 6,
      hardness_max: 6.5,
      specific_gravity_min: 3.50,
      specific_gravity_max: 3.60,
      cleavage:    'Good prismatic on {110}',
      fracture:    'Uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Resinous'],
      diaphaneity: ['Opaque', 'Translucent on thin edges'],
      colour:      'Black, dark green, dark reddish-brown',
      streak:      'Yellowish-grey',
      fluorescence: null,
      ri_min:      1.760,
      ri_max:      1.800,
      birefringence: 0.040,
      optical_type: 'B',
      shortdesc:   'Sodium iron pyroxene forming slender striated prismatic crystals in alkaline igneous rocks. The mineral of boundaries and sovereign self-definition.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-19.html',
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Aegirine',
      refractive_index: { n_alpha: 1.760, n_beta: 1.780, n_gamma: 1.800 },
      birefringence:   0.040,
      optical_sign:    '+',
      dispersion:      'Strong',
      pleochroism:     'Strong: dark green / dark brown / dark yellow-green',
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R040097'],
    },

    color: {
      primary_color:          'Jet black with deep green undertones',
      color_variants:         ['Black', 'Dark forest green', 'Dark reddish-brown', 'Black with vitreous gloss'],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.18, c: 0.06, h: 150 },
      hex:     '#1a2e1e',
      munsell: 'N2/',
      color_temperature_k:    null,
      psychological_effects:  [
        'The most assertive dark stone — its energy is directed outward as a boundary, not inward as absorption',
        'Encourages self-sovereignty, self-definition, and clarity of personal limits',
        'Black with green depth: the darkness of choice, not of void',
        'Supports those who struggle with saying no, or who lose themselves in others\' fields',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Aegirine',
      chakra_primary:   'Root',
      chakra_secondary: ['Solar Plexus', 'Heart'],
      element:   ['Earth', 'Fire'],
      planet:    ['Pluto', 'Saturn'],
      archetype: ['The Sovereign', 'The Boundary Keeper'],
      zodiac:    ['Pisces', 'Scorpio'],
      numerology: 1,
      angel_number: 111,
      intention: 'I am sovereign. My energy is my own. I define my field.',
      traditions: ['Western crystal healing', 'Norse tradition — named for Ægir, Norse sea god'],
      properties: [
        'The premiere boundary-setting stone in the mineral kingdom',
        'Particularly useful for empaths and sensitives who absorb others\' energy unconsciously',
        'Clears negative energy not by absorbing it but by refusing its entry',
        'Supports authentic self-expression and personal authority',
        'Found in alkaline igneous rocks — a stone born from the earth\'s most assertive geological processes',
        'Named for Ægir, the Norse sea god — commands the field like a sovereign commands the sea',
      ],
      gaia_resonance: 'SovereignCore + AnchorPrism',
      safety_warning: null,
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. AGATE
  // Banded microcrystalline quartz — the universal stone of pattern
  // Every colour, every band, every formation — an entire world in one mineral
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Agate',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Clear Quartz',

    physical: {
      id:           0,
      longid:       'agate',
      guid:         '',
      name:         'Agate (Chalcedony variety)',
      ima_formula:  'SiO₂',
      mindat_formula: 'SiO2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '4.DA.05',
      dana8ed:      '75.1.3.1',
      crystal_system: 'Trigonal',
      hardness_min: 6.5,
      hardness_max: 7,
      specific_gravity_min: 2.58,
      specific_gravity_max: 2.64,
      cleavage:    'None',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Waxy', 'Dull'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Every colour — banded, multicoloured, patterned',
      streak:      'White',
      fluorescence: 'Variable — some varieties fluoresce green or white under UV',
      ri_min:      1.530,
      ri_max:      1.540,
      birefringence: 0.004,
      optical_type: 'U',
      shortdesc:   'Trade name for banded chalcedony (microcrystalline quartz) displaying concentric or parallel colour bands. One of the most ancient and widely used gemstones in human history.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-28.html',
      piezoelectric:    true,
      safe_for_water:   true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name: 'Agate',
      refractive_index: { n_omega: 1.540, n_epsilon: 1.530 },
      birefringence:   0.004,
      optical_sign:    '-',
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'Variable — green, white, or none depending on variety',
      fluorescence_sw: 'Variable',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: [],
    },

    color: {
      primary_color:          'Banded multicolour — varies by variety',
      color_variants:         [
        'Grey-white banded', 'Brown-red banded', 'Blue-white (Blue Lace)',
        'Green banded', 'Black-white (Onyx)', 'Fire Agate (iridescent)'
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.65, c: 0.06, h: 60 },
      hex:     '#c8a87a',
      munsell: '5YR 7/4',
      color_temperature_k:    null,
      psychological_effects:  [
        'The banded pattern is itself the medicine — rhythm, repetition, layer upon layer',
        'Stabilising and grounding regardless of colour variety',
        'Encourages patience — agate grows one concentric ring at a time',
        'The ancient stone of balance — used as an amulet across every culture on Earth',
      ],
      harmonics: {
        complementary_hue: 240,
        triadic_hues:      [180, 300],
        analogous_range:   [40, 80],
      },
    },

    metaphysical: {
      mineral_name:     'Agate',
      chakra_primary:   'Root',
      chakra_secondary: ['Sacral', 'Heart'],
      element:   ['Earth'],
      planet:    ['Earth', 'Mercury'],
      archetype: ['The Keeper of Patterns', 'The Ancient Protector'],
      zodiac:    ['Gemini', 'Virgo'],
      numerology: 7,
      angel_number: 777,
      intention: 'I am grounded, balanced, and protected by the ancient patterns of the earth.',
      traditions: [
        'Ancient Mesopotamian amulet tradition',
        'Egyptian funerary use',
        'Ancient Greek and Roman talismanic tradition',
        'Chinese five-element healing',
        'Western crystal healing',
        'Native American ceremonial tradition',
      ],
      properties: [
        'One of the oldest stones used by humanity — found in Neolithic sites worldwide',
        'The banding pattern makes each agate a record of geological time — a stone of patience',
        'Stabilising, grounding, and protective across all colour varieties',
        'Properties shift by variety: Blue Lace (communication), Fire Agate (vitality), Moss Agate (nature connection)',
        'Widely used in children\'s healing work for its gentle, non-confrontational frequency',
        'The great balancer — harmonises yin and yang within the field',
      ],
      gaia_resonance: 'AnchorPrism + ViriditasHeart',
      safety_warning: null,
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. AGNI MANITITE
  // Pearl of Divine Fire — Indonesian tektite glass — exceptionally rare
  // Volcanic island of Java — fire from sky meeting earth and sea
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Agni Manitite',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Selenite',

    physical: {
      id:           0,
      longid:       'agni-manitite',
      guid:         '',
      name:         'Tektite (Indonesian — Java)',
      ima_formula:  'SiO₂ (amorphous glass with Al, Fe, Ca, Mg, K impurities)',
      mindat_formula: 'SiO2 (amorphous)',
      ima_status:   null,
      ima_year:     null,
      strunzten:    null,
      dana8ed:      null,
      crystal_system: 'Amorphous',
      hardness_min: 5.5,
      hardness_max: 6.5,
      specific_gravity_min: 2.34,
      specific_gravity_max: 2.51,
      cleavage:    'None',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Dark grey to black, some translucent grey-green pieces',
      streak:      'White',
      fluorescence: null,
      ri_min:      1.480,
      ri_max:      1.520,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Trade name for rare tektite glass found in Java, Indonesia. Formed by a meteorite impact fusing terrestrial rock into glass. Among the rarest tektites in the world.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  null,
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Agni Manitite',
      refractive_index: { n: 1.500 },
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: [],
    },

    color: {
      primary_color:          'Dark charcoal to black, sometimes translucent grey-green',
      color_variants:         ['Dense black', 'Dark grey', 'Translucent smoky grey-green'],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.20, c: 0.02, h: 120 },
      hex:     '#242820',
      munsell: 'N2/',
      color_temperature_k:    null,
      psychological_effects:  [
        'Intense, focused activation — less subtle than most crystals',
        'Fire frequency: awakening, ignition, the spark of divine will',
        'Associated with solar plexus activation and sovereign personal power',
        'Creates a sense of urgency toward one\'s true path and soul purpose',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Agni Manitite',
      chakra_primary:   'Solar Plexus',
      chakra_secondary: ['Sacral', 'Crown'],
      element:   ['Fire', 'Aether'],
      planet:    ['Sun', 'Mars'],
      archetype: ['The Pearl of Divine Fire', 'The Soul Ignitor'],
      zodiac:    ['Aries', 'Leo', 'Sagittarius'],
      numerology: 9,
      angel_number: 999,
      intention: 'The fire of my soul\'s true purpose burns clear and bright.',
      traditions: ['Sanskrit tradition — "Agni" (fire) + "Mani" (pearl/jewel)', 'Indonesian earth wisdom', 'Western crystal healing — tektite tradition'],
      properties: [
        'One of the rarest tektites on Earth — found only in Java, Indonesia, often submerged',
        'The name means "Pearl of Divine Fire" in Sanskrit — agni (fire) + mani (jewel)',
        'Formed when a meteorite struck Earth, fusing sky, fire, and earth into glass',
        'Intensely activating for solar plexus — personal power, courage, and soul purpose',
        'Used for manifestation work requiring bold decisive action',
        'Its rarity amplifies its potency — the universe does not mass-produce this stone',
        'A stone of completion (999) — burns away what must end to make way for what must begin',
      ],
      gaia_resonance: 'QuantumNexus + SovereignCore + Noosphere',
      safety_warning: null,
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. AJOITE
  // Copper phyllosilicate — pale blue-green — one of the rarest healing stones
  // Found almost exclusively in Messina Mine, South Africa
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Ajoite',
    mindat_id:   107,
    rruff_ids:   ['R060440'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Black Tourmaline',

    physical: {
      id:           107,
      longid:       'ajoite',
      guid:         '',
      name:         'Ajoite',
      ima_formula:  '(K,Na)Cu₇AlSi₉O₂₄(OH)₆·3H₂O',
      mindat_formula: '(K,Na)Cu7AlSi9O24(OH)6·3H2O',
      ima_status:   'A',
      ima_year:     1958,
      strunzten:    '9.EE.20',
      dana8ed:      '73.1.4.1',
      crystal_system: 'Triclinic',
      hardness_min: 3.5,
      hardness_max: 3.5,
      specific_gravity_min: 2.96,
      specific_gravity_max: 2.96,
      cleavage:    'Perfect on {001}',
      fracture:    'Uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Pearly'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Pale blue-green, blue, turquoise',
      streak:      'Pale blue',
      fluorescence: null,
      ri_min:      1.550,
      ri_max:      1.628,
      birefringence: 0.078,
      optical_type: 'B',
      shortdesc:   'Exceptionally rare hydrated copper aluminium silicate, almost exclusively from the Messina Mine, Limpopo, South Africa. Usually found as inclusions in quartz.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-107.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Ajoite',
      refractive_index: { n_alpha: 1.550, n_beta: 1.600, n_gamma: 1.628 },
      birefringence:   0.078,
      optical_sign:    '-',
      dispersion:      null,
      pleochroism:     'Moderate: pale blue / blue-green / nearly colourless',
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: { min: 470, max: 520 },
      spectra: ['R060440'],
    },

    color: {
      primary_color:          'Pale aqua — sky blue-green',
      color_variants:         ['Pale sky blue', 'Aqua', 'Turquoise', 'Blue-green in quartz matrix'],
      dominant_wavelength_nm: 495,
      oklch:   { l: 0.68, c: 0.11, h: 195 },
      hex:     '#72c4b8',
      munsell: '5BG 7/4',
      color_temperature_k:    10000,
      psychological_effects:  [
        'Among the most gentle and high-frequency stones in the mineral kingdom',
        'Deeply soothing — like cool clear water after a long difficult journey',
        'Opens the heart without force — the frequency of unconditional compassion',
        'Encourages forgiveness, self-love, and emotional liberation',
      ],
      harmonics: {
        complementary_hue: 15,
        triadic_hues:      [315, 75],
        analogous_range:   [175, 215],
      },
    },

    metaphysical: {
      mineral_name:     'Ajoite',
      chakra_primary:   'Heart',
      chakra_secondary: ['Throat', 'Crown'],
      element:   ['Water', 'Air'],
      planet:    ['Venus', 'Neptune'],
      archetype: ['The Divine Mother', 'The Healer of All Wounds'],
      zodiac:    ['Virgo', 'Scorpio', 'Libra'],
      numerology: 9,
      angel_number: 999,
      intention: 'All wounds are healed. All is forgiven. I return to love.',
      traditions: [
        'Western crystal healing — considered one of the highest-vibration healing stones',
        'Named after Ajo, Arizona, where it was first described in 1958',
        'Widely valued in the Shaman Stone and Earth Medicine traditions',
      ],
      properties: [
        'Among the rarest healing crystals in the world — nearly all specimens from Messina Mine, South Africa',
        'Almost always found as inclusions in quartz — the quartz amplifies its gentle frequency',
        'Considered one of the highest-vibration heart stones in the mineral kingdom',
        'Works slowly and deeply — not dramatic, but profoundly transformative over time',
        'Supports emotional liberation, forgiveness of self and others, and unconditional love',
        'The copper component activates the heart-throat axis — emotional truth expressed gently',
        'A stone of completion (999) — it heals what is ready to be finally released',
      ],
      gaia_resonance: 'ViriditasHeart + SomnusVeil + Noosphere',
      safety_warning: 'Contains copper — toxic if ingested. Never use for water elixirs. Wash hands after handling. Display specimens are safe.',
    },
  },

];

export default BATCH_A3;

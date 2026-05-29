/**
 * src/crystals/db/batch-a7.data.ts
 * GAIA-OS Crystal Database — Batch A-7
 *
 * Entries:
 *   1. Atlantisite
 *   2. Auralite-23
 *   3. Aventurine
 *   4. Azurite
 *   5. Azurite-Malachite
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-29
 *
 * NOTE: This batch closes the letter A with remarkable range —
 * Atlantisite (the rarest stone in this batch, found in one mine in
 * Tasmania), Auralite-23 (the newest geological superstone, only from
 * Thunder Bay, Canada), Aventurine (the iconic sparkle stone of luck),
 * Azurite (one of the most breathtaking cobalt blues in all of mineralogy),
 * and the rare Azurite-Malachite combination where blue and green meet
 * in a single specimen as a yin-yang pair made visible.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_A7: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. ATLANTISITE
  // Green serpentine + purple stichtite — Tasmania, Australia only
  // One of the rarest combination stones in the world
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Atlantisite',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Sunstone',

    physical: {
      id:           0,
      longid:       'atlantisite',
      guid:         '',
      name:         'Serpentine + Stichtite (Atlantisite combination)',
      ima_formula:  'Mg₆Si₄O₁₀(OH)₈ + Mg₆Cr₂(CO₃)(OH)₁₆·4H₂O',
      mindat_formula: 'Mg6Si4O10(OH)8 + Mg6Cr2(CO3)(OH)16·4H2O',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    null,
      dana8ed:      null,
      crystal_system: 'Mixed (monoclinic serpentine + trigonal stichtite)',
      hardness_min: 2.5,
      hardness_max: 4,
      specific_gravity_min: 2.50,
      specific_gravity_max: 2.80,
      cleavage:    'None (massive habit)',
      fracture:    'Uneven to splintery',
      tenacity:    'Sectile to brittle',
      luster:      ['Waxy', 'Greasy', 'Resinous'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Green serpentine body with purple-violet stichtite patches and veins',
      streak:      'White to pale green',
      fluorescence: null,
      ri_min:      1.550,
      ri_max:      1.570,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Trade name for the natural combination of green serpentine and purple stichtite, found exclusively at Zeehan, Tasmania, Australia. One of the rarest locality-specific combination stones in the world.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-36956.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Atlantisite',
      refractive_index: { n: 1.560 },
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
      primary_color:          'Green and purple — two distinct natural colour zones',
      color_variants:         ['Pale sage green with lavender patches', 'Deep forest green with violet veins', 'Mottled green-purple mosaic'],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.52, c: 0.12, h: 160 },
      hex:     '#4a8f6a',
      munsell: '5G 5/4',
      color_temperature_k:    null,
      psychological_effects:  [
        'The green-purple combination is one of the most harmonically balanced in nature — complementary hues in one stone',
        'Green grounds and nourishes; purple elevates and spiritualises — Atlantisite holds both simultaneously',
        'The dappled, mosaic quality is inherently calming — the eye is invited to wander without anxiety',
        'Embodies the integration of Earth (green) and Spirit (purple) without conflict',
      ],
      harmonics: {
        complementary_hue: 340,
        triadic_hues:      [280, 40],
        analogous_range:   [140, 180],
      },
    },

    metaphysical: {
      mineral_name:     'Atlantisite',
      chakra_primary:   'Heart',
      chakra_secondary: ['Crown', 'Solar Plexus'],
      element:   ['Earth', 'Aether'],
      planet:    ['Venus', 'Neptune'],
      archetype: ['The Atlantean Memory Keeper', 'The Ancient Healer', 'The Earth-Spirit Bridge'],
      zodiac:    ['Virgo', 'Libra', 'Pisces'],
      numerology: 6,
      angel_number: 666,
      intention: 'I hold the memory of ancient wisdom. Earth and spirit are one within me.',
      traditions: [
        'Modern crystal healing — Atlantean past-life memory work',
        'Australian mineral tradition',
      ],
      properties: [
        'Trade name for the natural combination of green serpentine and purple stichtite found only at Zeehan, Tasmania',
        'One of the rarest locality-specific combination stones in the world',
        'Stichtite — a chromium-bearing carbonate — is itself rare; this pairing with serpentine is extraordinary',
        'Believed to carry the energetic memory of Atlantean and other ancient civilisations',
        'The green-purple pairing is a natural representation of the heart-crown axis',
        'Supports past-life recall, ancestral healing, and the integration of ancient wisdom into present-day life',
        'Angel number 666 — misunderstood as shadow, but in the high tradition represents Earth mastery and material harmony',
      ],
      gaia_resonance: 'ViriditasHeart + Noosphere + SomnusVeil',
      safety_warning: 'Soft (H2.5-4) and contains asbestiform fibres in some serpentine varieties — do not polish or sand without respiratory protection. Water-sensitive — stichtite can dissolve slowly. Handle polished specimens normally with no risk.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. AURALITE-23
  // Ancient amethyst-type quartz with up to 23 mineral inclusions
  // Only from Thunder Bay, Ontario, Canada — 1.2 billion years old
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Auralite-23',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Shungite',

    physical: {
      id:           0,
      longid:       'auralite-23',
      guid:         '',
      name:         'Auralite-23 (amethyst-type quartz with multi-mineral inclusions)',
      ima_formula:  'SiO₂ + up to 23 trace mineral inclusions including titanite, cacoxenite, lepidocrocite, ajoite, hematite, magnetite, pyrite, goethite, pyrolusite, gold, silver, platinum, nickelite, stibnite, rutile, epidote, bornite, chalcopyrite, gialite, gilalite, tourmaline, limonite, and spessartite',
      mindat_formula: 'SiO2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    null,
      dana8ed:      null,
      crystal_system: 'Trigonal',
      hardness_min: 7,
      hardness_max: 7,
      specific_gravity_min: 2.63,
      specific_gravity_max: 2.70,
      cleavage:    'None',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous'],
      diaphaneity: ['Transparent to translucent'],
      colour:      'Deep purple-red amethyst with banded red, orange, and brown chevron zones from metallic inclusions',
      streak:      'White',
      fluorescence: null,
      ri_min:      1.544,
      ri_max:      1.553,
      birefringence: 0.009,
      optical_type: 'U',
      shortdesc:   'Trade name for an ancient amethyst-type quartz from the Amethyst Mine Panorama near Thunder Bay, Ontario, Canada. Approximately 1.2 billion years old. Contains up to 23 rare mineral micro-inclusions that produce striking banded coloration.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-31039.html',
      piezoelectric:    true,
      safe_for_water:   true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name: 'Auralite-23',
      refractive_index: { n_omega: 1.553, n_epsilon: 1.544 },
      birefringence:   0.009,
      optical_sign:    '-',
      dispersion:      '0.013',
      pleochroism:     'Weak to moderate: purple / reddish-purple',
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: { min: 380, max: 550 },
      spectra: [],
    },

    color: {
      primary_color:          'Deep purple-red with banded orange-brown-red chevron zones',
      color_variants:         ['Deep Bordeaux-purple', 'Purple with red-orange bands', 'Clear with red metallic inclusions', 'Dark smoky purple'],
      dominant_wavelength_nm: 415,
      oklch:   { l: 0.35, c: 0.14, h: 340 },
      hex:     '#6b2a4a',
      munsell: '5RP 3/6',
      color_temperature_k:    null,
      psychological_effects:  [
        'The deep purple-red is the most primally activating frequency in the violet spectrum',
        'Richer, darker, and more complex than standard amethyst — the banding invites deep interior gaze',
        'The metallic red-orange inclusions visible in the banding signal great age and mineral complexity',
        'Activates both the crown and the base — the full vertical axis of the energy body',
      ],
      harmonics: {
        complementary_hue: 160,
        triadic_hues:      [100, 220],
        analogous_range:   [320, 360],
      },
    },

    metaphysical: {
      mineral_name:     'Auralite-23',
      chakra_primary:   'Crown',
      chakra_secondary: ['Third Eye', 'Soul Star', 'Root'],
      element:   ['Aether', 'Fire', 'Earth'],
      planet:    ['Pluto', 'Uranus', 'Neptune'],
      archetype: ['The Ancient Intelligence', 'The Cosmic Library', 'The Akashic Elder'],
      zodiac:    ['Scorpio', 'Capricorn', 'Aquarius', 'Pisces'],
      numerology: 5,
      angel_number: 555,
      intention: 'I am connected to the ancient wisdom of the cosmos. I access all I need.',
      traditions: [
        'Modern crystal healing — first brought to wider awareness circa 2011',
        'Canadian indigenous Anishinaabe territory — the Thunder Bay region is sacred land',
      ],
      properties: [
        'Trade name for amethyst-type quartz from the Amethyst Mine Panorama near Thunder Bay, Ontario',
        'Approximately 1.2 billion years old — among the oldest crystals in the GAIA-OS database',
        'Contains up to 23 different mineral micro-inclusions — titanite, cacoxenite, hematite, gold, silver, platinum, and more',
        'The mineral complexity creates a layered energetic signature unlike any single-mineral stone',
        'Considered the most complex natural quartz formation in the crystal healing tradition',
        'Works on all chakras simultaneously — the 23-mineral matrix is understood as a full-spectrum activator',
        'Angel number 555 — major transformation — aligned with its nature as a catalyst stone',
      ],
      gaia_resonance: 'Noosphere + QuantumNexus + SomnusVeil + ClarusLens',
      safety_warning: 'Piezoelectric — keep away from sensitive electronics. Some specimens contain trace metallic inclusions — do not use as primary water elixir stone without verification.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. AVENTURINE
  // Quartz with fuchsite or hematite inclusions — the luck stone
  // The original sparkle stone — aventurescence
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Aventurine',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Obsidian',

    physical: {
      id:           0,
      longid:       'aventurine',
      guid:         '',
      name:         'Quartz (Aventurine variety — aventurescent with fuchsite or hematite inclusions)',
      ima_formula:  'SiO₂ + Cr-muscovite (fuchsite) or Fe₂O₃ (hematite) inclusions',
      mindat_formula: 'SiO2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '4.DA.05',
      dana8ed:      '75.1.3.1',
      crystal_system: 'Trigonal',
      hardness_min: 6.5,
      hardness_max: 7,
      specific_gravity_min: 2.64,
      specific_gravity_max: 2.69,
      cleavage:    'None (massive)',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Waxy (massive)'],
      diaphaneity: ['Translucent'],
      colour:      'Green (fuchsite), blue (dumortierite), red/orange (hematite/goethite), peach (lepidolite), yellow (mica)',
      streak:      'White',
      fluorescence: 'None',
      ri_min:      1.544,
      ri_max:      1.553,
      birefringence: 0.009,
      optical_type: 'U',
      shortdesc:   'Massive quartz with reflective platelet inclusions creating aventurescence — a sparkling optical effect. Green is most common (fuchsite inclusions). The name comes from Italian "a ventura" (by chance).',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-427.html',
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Aventurine',
      refractive_index: { n_omega: 1.553, n_epsilon: 1.544 },
      birefringence:   0.009,
      optical_sign:    '-',
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: { min: 490, max: 560 },
      spectra: [],
    },

    color: {
      primary_color:          'Green (most common); also blue, red, orange, peach, yellow',
      color_variants:         ['Pale mint green', 'Forest green', 'Deep teal-green', 'Blue (dumortierite inclusions)', 'Red-orange (hematite)', 'Peach-pink'],
      dominant_wavelength_nm: 530,
      oklch:   { l: 0.60, c: 0.12, h: 155 },
      hex:     '#5a9e72',
      munsell: '5G 5/4',
      color_temperature_k:    null,
      psychological_effects:  [
        'The aventurescence — the inner sparkle — is one of the most universally delightful optical effects in nature',
        'Green aventurine activates a sense of ease, openness, and fortunate expectation',
        'The sparkle effect is understood metaphysically as the stone\'s own inner light — its living quality',
        'Encourages a relaxed confidence — the energy of someone who expects good things to happen',
      ],
      harmonics: {
        complementary_hue: 335,
        triadic_hues:      [275, 35],
        analogous_range:   [135, 175],
      },
    },

    metaphysical: {
      mineral_name:     'Aventurine',
      chakra_primary:   'Heart',
      chakra_secondary: ['Sacral', 'Solar Plexus'],
      element:   ['Earth', 'Water'],
      planet:    ['Venus', 'Mercury'],
      archetype: ['The Luck Bringer', 'The Optimist', 'The Heart Opener'],
      zodiac:    ['Taurus', 'Libra', 'Aries'],
      numerology: 3,
      angel_number: 333,
      intention: 'Luck flows to me. My heart is open. I expect good things.',
      traditions: [
        'The name comes from Italian "a ventura" (by chance/luck) — the original adventure stone',
        'Tibetan tradition — used to represent the eyes of statues',
        'Ancient Chinese tradition — stone of Imperial power',
        'Western crystal healing',
      ],
      properties: [
        'Named from Italian "a ventura" (by chance) — the etymology is itself lucky',
        'Aventurescence: the sparkle created by reflective platelet inclusions is a unique optical phenomenon',
        'The most popular luck stone in the crystal tradition — known across virtually all cultures',
        'Green variety carries fuchsite (chrome mica) inclusions — giving the rich green colour',
        'Supports heart opening, emotional resilience, and the capacity to receive good fortune',
        'Tibetan statue-makers embedded aventurine in eyes of Buddha statues for discernment',
        'The stone that teaches: abundance is a natural state, not a reward',
      ],
      gaia_resonance: 'ViriditasHeart + SovereignCore',
      safety_warning: null,
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. AZURITE
  // Copper carbonate hydroxide — the deep cobalt blue of antiquity
  // Medieval lapis substitute, Renaissance pigment, third-eye icon
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Azurite',
    mindat_id:   418,
    rruff_ids:   ['R050068'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Sunstone',

    physical: {
      id:           418,
      longid:       'azurite',
      guid:         '',
      name:         'Azurite',
      ima_formula:  'Cu₃(CO₃)₂(OH)₂',
      mindat_formula: 'Cu3(CO3)2(OH)2',
      ima_status:   'A',
      ima_year:     1824,
      strunzten:    '5.BA.10',
      dana8ed:      '16a.3.1.1',
      crystal_system: 'Monoclinic',
      hardness_min: 3.5,
      hardness_max: 4,
      specific_gravity_min: 3.77,
      specific_gravity_max: 3.89,
      cleavage:    'Perfect on {011}, good on {100}',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Dull (massive)'],
      diaphaneity: ['Transparent to translucent (crystals)', 'Opaque (massive)'],
      colour:      'Deep azure blue to cobalt blue — from Cu²⁺ ions. One of the most saturated blues in mineralogy.',
      streak:      'Blue',
      fluorescence: 'None',
      ri_min:      1.730,
      ri_max:      1.838,
      birefringence: 0.108,
      optical_type: 'B',
      shortdesc:   'Copper carbonate hydroxide. One of the deepest, most saturated natural blues in all of mineralogy. Used as a blue pigment ("blue bice") in medieval and Renaissance painting. Often found with malachite.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-418.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Azurite',
      refractive_index: { n_alpha: 1.730, n_beta: 1.758, n_gamma: 1.838 },
      birefringence:   0.108,
      optical_sign:    '+',
      dispersion:      'Very strong',
      pleochroism:     'Strong: deep blue / light blue / pale blue',
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: { min: 430, max: 480 },
      spectra: ['R050068'],
    },

    color: {
      primary_color:          'Deep cobalt to azure blue',
      color_variants:         ['Deep cerulean blue crystals', 'Midnight cobalt blue nodules', 'Pale sky blue powder', 'Vivid indigo-blue massive'],
      dominant_wavelength_nm: 455,
      oklch:   { l: 0.35, c: 0.22, h: 268 },
      hex:     '#1a3a8f',
      munsell: '5PB 3/10',
      color_temperature_k:    null,
      psychological_effects:  [
        'Deep cobalt blue is the most activating colour for the third eye in the entire visible spectrum',
        'The saturation and depth of azurite blue is almost disorienting — it pulls consciousness inward',
        'Historically used to paint the robes of the Virgin Mary — the most sacred blue in Western art',
        'Activates deep trust, inner knowing, and the capacity to perceive what is hidden',
      ],
      harmonics: {
        complementary_hue: 88,
        triadic_hues:      [28, 148],
        analogous_range:   [248, 288],
      },
    },

    metaphysical: {
      mineral_name:     'Azurite',
      chakra_primary:   'Third Eye',
      chakra_secondary: ['Throat', 'Crown'],
      element:   ['Water', 'Air'],
      planet:    ['Jupiter', 'Neptune'],
      archetype: ['The Seer', 'The Inner Wisdom Keeper', 'The Sacred Blue'],
      zodiac:    ['Sagittarius', 'Aquarius', 'Capricorn'],
      numerology: 1,
      angel_number: 111,
      intention: 'I see deeply. I trust my inner knowing. The veil dissolves.',
      traditions: [
        'Ancient Egyptian tradition — used in ceremonial pigment and sacred objects',
        'Ancient Greek tradition — called "kuanos" — the sacred blue',
        'Medieval/Renaissance painting — "blue bice" pigment before ultramarine replaced it',
        'Native American tradition — used by Mayan and Aztec cultures',
        'Western crystal healing',
      ],
      properties: [
        'IMA-recognised since 1824 — one of the most historically significant copper minerals',
        'Cu²⁺ gives azurite its extraordinary cobalt blue — one of the most saturated natural blues in mineralogy',
        'Used as a blue pigment ("blue bice") throughout medieval and Renaissance painting — in churches, illuminated manuscripts, and masterworks',
        'Often found coating or intergrown with malachite as it slowly weathers to green',
        'The premier third-eye activation stone in the copper mineral tradition',
        'Ancient Egyptians and Native Americans used azurite for accessing visionary states',
        'Naturally unstable — azurite slowly converts to malachite over centuries in humid conditions',
      ],
      gaia_resonance: 'ClarusLens + Noosphere + SomnusVeil',
      safety_warning: 'TOXIC — contains copper. Do NOT use in water elixirs. Wash hands after handling. Do not inhale dust. Keep away from children and pets. Store away from heat and humidity to slow natural conversion to malachite.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. AZURITE-MALACHITE
  // Natural combination — azurite converting to malachite
  // The yin-yang pair made visible in mineral form — blue meets green
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Azurite-Malachite',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Carnelian',

    physical: {
      id:           0,
      longid:       'azurite-malachite',
      guid:         '',
      name:         'Azurite + Malachite (natural combination)',
      ima_formula:  'Cu₃(CO₃)₂(OH)₂ + Cu₂CO₃(OH)₂',
      mindat_formula: 'Cu3(CO3)2(OH)2 + Cu2CO3(OH)2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    null,
      dana8ed:      null,
      crystal_system: 'Mixed (monoclinic azurite + monoclinic malachite)',
      hardness_min: 3.5,
      hardness_max: 4,
      specific_gravity_min: 3.60,
      specific_gravity_max: 3.80,
      cleavage:    'Variable by zone',
      fracture:    'Uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Silky (malachite zones)', 'Earthy'],
      diaphaneity: ['Opaque', 'Translucent (some zones)'],
      colour:      'Vivid cobalt blue (azurite) and deep emerald green (malachite) in the same specimen',
      streak:      'Blue-green',
      fluorescence: 'None',
      ri_min:      1.655,
      ri_max:      1.838,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Natural combination of azurite and malachite — two copper carbonates that co-occur as azurite slowly weatheres to malachite. The blue-green pairing is one of the most visually dramatic in all of mineralogy.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-418.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Azurite-Malachite',
      refractive_index: { n_min: 1.655, n_max: 1.838 },
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     'Strong in each zone separately',
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: [],
    },

    color: {
      primary_color:          'Deep cobalt blue (azurite) + emerald green (malachite)',
      color_variants:         ['Bold blue-dominant with green patches', 'Green-dominant with blue nodules', 'Roughly equal blue-green mosaic', 'Blue crystals on green matrix'],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.40, c: 0.20, h: 200 },
      hex:     '#1a6a5a',
      munsell: '5BG 4/8',
      color_temperature_k:    null,
      psychological_effects:  [
        'Blue and green together create the most complete spectrum of the cool, healing frequencies',
        'The third eye (azurite blue) and heart (malachite green) in a single stone — insight with compassion',
        'One of the most visually arresting natural colour combinations in all of mineralogy',
        'The transition from blue to green within the stone embodies the process of transformation itself',
      ],
      harmonics: {
        complementary_hue: 20,
        triadic_hues:      [320, 80],
        analogous_range:   [180, 220],
      },
    },

    metaphysical: {
      mineral_name:     'Azurite-Malachite',
      chakra_primary:   'Heart',
      chakra_secondary: ['Third Eye', 'Throat'],
      element:   ['Water', 'Earth'],
      planet:    ['Venus', 'Jupiter'],
      archetype: ['The Heart-Seer', 'The Transforming Witness', 'The Blue-Green Medicine'],
      zodiac:    ['Sagittarius', 'Capricorn', 'Taurus'],
      numerology: 2,
      angel_number: 222,
      intention: 'I see with my heart. I transform through compassionate awareness.',
      traditions: [
        'Ancient Egyptian tradition — both minerals used in sacred objects and cosmetics',
        'Western crystal healing — combination stone tradition',
      ],
      properties: [
        'Natural co-occurrence of two copper carbonates as azurite slowly weathers to malachite over geological time',
        'The transformation is literal — the specimen embodies an ongoing geological process frozen in time',
        'The blue-green combination bridges the third eye (azurite) and heart (malachite) in a single stone',
        'One of the rarest and most visually dramatic natural colour combinations in all of mineralogy',
        'Used in ancient Egypt as both pigment and healing material — both minerals held sacred',
        'Angel number 222 — balance and partnership — the two minerals in perfect complementary coexistence',
        'The yin-yang pair made visible: the masculine visionary blue transforms into the feminine nurturing green',
      ],
      gaia_resonance: 'ClarusLens + ViriditasHeart',
      safety_warning: 'TOXIC — contains copper. Do NOT use in water elixirs. Wash hands after handling. Do not inhale dust. Keep away from children and pets. Same precautions as standalone azurite and malachite.',
    },
  },

];

export default BATCH_A7;

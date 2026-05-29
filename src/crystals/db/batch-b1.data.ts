/**
 * src/crystals/db/batch-b1.data.ts
 * GAIA-OS Crystal Database — Batch B-1
 *
 * Entries:
 *   1. Blue Aragonite
 *   2. Blue Calcite
 *   3. Blue Chalcedony
 *   4. Blue Goldstone
 *   5. Blue John Fluorite
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-29
 *
 * NOTE: The letter B opens with five stones united by colour rather than
 * mineral family — a deliberate thematic batch. Two are natural minerals
 * (aragonite and calcite varieties), one is a cryptocrystalline silica
 * (chalcedony), one is a man-made glass (goldstone), and one is the
 * rarest locality-specific fluorite in the world (Blue John from
 * Castleton, Derbyshire — the only place on Earth where it forms).
 * The blue palette spans from powder blue to deep violet-banded,
 * and the metaphysical range runs from soft communication to fierce
 * ancestral pride.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_B1: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. BLUE ARAGONITE
  // Pale blue to blue-green aragonite — rare colour variety
  // Carries the sea-memory of calcium in a softer, sky-frequency
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Blue Aragonite',
    mindat_id:   308,
    rruff_ids:   ['R040078'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Carnelian',

    physical: {
      id:           308,
      longid:       'blue-aragonite',
      guid:         '',
      name:         'Aragonite (blue colour variety)',
      ima_formula:  'CaCO₃',
      mindat_formula: 'CaCO3',
      ima_status:   'A',
      ima_year:     1797,
      strunzten:    '5.AB.15',
      dana8ed:      '14.1.3.1',
      crystal_system: 'Orthorhombic',
      hardness_min: 3.5,
      hardness_max: 4,
      specific_gravity_min: 2.93,
      specific_gravity_max: 2.95,
      cleavage:    'Distinct on {010}, imperfect on {110} and {011}',
      fracture:    'Subconchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Resinous'],
      diaphaneity: ['Translucent'],
      colour:      'Pale blue to blue-green — from trace copper or organic impurities; relatively rare colour variety',
      streak:      'White',
      fluorescence: 'Weak green or blue under UV (variable)',
      ri_min:      1.530,
      ri_max:      1.685,
      birefringence: 0.155,
      optical_type: 'B',
      shortdesc:   'Blue colour variety of aragonite (CaCO₃). The blue colouration is rare in aragonite and derives from trace copper or organic inclusions. Found notably in Greece, China, and Morocco. Same species as standard aragonite (Batch A-6).',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-308.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Blue Aragonite',
      refractive_index: { n_alpha: 1.530, n_beta: 1.682, n_gamma: 1.685 },
      birefringence:   0.155,
      optical_sign:    '-',
      dispersion:      'Weak',
      pleochroism:     'Weak',
      fluorescence_lw: 'Weak green or blue',
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: { min: 450, max: 500 },
      spectra: ['R040078'],
    },

    color: {
      primary_color:          'Pale blue to blue-green',
      color_variants:         ['Powder blue', 'Sky blue', 'Blue-green teal', 'Pale aqua'],
      dominant_wavelength_nm: 480,
      oklch:   { l: 0.74, c: 0.08, h: 218 },
      hex:     '#8fc4d4',
      munsell: '5B 7/4',
      color_temperature_k:    10500,
      psychological_effects:  [
        'Pale blue aragonite carries the double energy of sky and sea — expansive calm with structural depth',
        'The softness of the blue distinguishes it from sharper blue stones — it invites rather than activates',
        'Uniquely combines the grounding quality of aragonite with the communicative frequency of blue',
        'Encourages emotional honesty expressed gently — the truth told with care',
      ],
      harmonics: {
        complementary_hue: 38,
        triadic_hues:      [338, 98],
        analogous_range:   [198, 238],
      },
    },

    metaphysical: {
      mineral_name:     'Blue Aragonite',
      chakra_primary:   'Throat',
      chakra_secondary: ['Heart', 'Third Eye'],
      element:   ['Water', 'Earth'],
      planet:    ['Neptune', 'Moon'],
      archetype: ['The Gentle Communicator', 'The Emotional Anchor', 'The Sea Memory'],
      zodiac:    ['Pisces', 'Aquarius', 'Cancer'],
      numerology: 9,
      angel_number: 999,
      intention: 'I speak my truth gently and clearly. I am grounded and open.',
      traditions: [
        'Western crystal healing',
        'Same geological species as brown/orange aragonite — the blue variety is the rarer, higher-frequency expression',
      ],
      properties: [
        'Same species as standard aragonite (Batch A-6) — the blue colour variety is rare and particularly prized',
        'Combines the Earth Star grounding quality of aragonite with the communicative frequency of blue',
        'The gentlest of the blue communication stones — ideal for those who need support speaking their emotional truth',
        'Builds the bridge between the heart and throat chakras — feelings into words',
        'Supports empathic communication, counselling work, and emotionally honest conversations',
        'The blue of the sea made solid — carries oceanic calm and depth within the mineral kingdom',
        'Excellent for those who feel they hold grief or emotion that cannot yet be spoken',
      ],
      gaia_resonance: 'ViriditasHeart + ClarusLens',
      safety_warning: 'Water-sensitive — aragonite dissolves slowly in water and is acid-sensitive. Do not use in water elixirs. Keep away from acidic cleaners.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. BLUE CALCITE
  // Pale blue calcite — CaCO3 trigonal polymorph
  // The most soothing stone in the entire mineral tradition
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Blue Calcite',
    mindat_id:   859,
    rruff_ids:   ['R040070'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Red Jasper',

    physical: {
      id:           859,
      longid:       'blue-calcite',
      guid:         '',
      name:         'Calcite (blue colour variety)',
      ima_formula:  'CaCO₃',
      mindat_formula: 'CaCO3',
      ima_status:   'A',
      ima_year:     1845,
      strunzten:    '5.AB.05',
      dana8ed:      '14.1.1.1',
      crystal_system: 'Trigonal',
      hardness_min: 3,
      hardness_max: 3,
      specific_gravity_min: 2.71,
      specific_gravity_max: 2.71,
      cleavage:    'Perfect rhombohedral on {10−1‐4}',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Resinous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Pale to medium blue — from trace elements or inclusions; soft, milky, or clear blue common',
      streak:      'White',
      fluorescence: 'Strong pink, red, or blue under UV (variable by locality)',
      ri_min:      1.486,
      ri_max:      1.658,
      birefringence: 0.172,
      optical_type: 'U',
      shortdesc:   'Blue colour variety of calcite (CaCO₃ trigonal). One of the most widely available blue minerals in the crystal tradition. Soft and easily scratched. Notable for extreme birefringence and strong UV fluorescence.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-859.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Blue Calcite',
      refractive_index: { n_omega: 1.658, n_epsilon: 1.486 },
      birefringence:   0.172,
      optical_sign:    '-',
      dispersion:      'Weak',
      pleochroism:     'None to very weak',
      fluorescence_lw: 'Strong: pink, red, or blue (locality-dependent)',
      fluorescence_sw: 'Variable',
      phosphorescence: 'Possible in some specimens',
      visible_wavelength_nm: { min: 450, max: 500 },
      spectra: ['R040070'],
    },

    color: {
      primary_color:          'Pale to medium blue — soft, milky, serene',
      color_variants:         ['Milky powder blue', 'Clear pale sky blue', 'Medium cornflower blue', 'Banded blue-white'],
      dominant_wavelength_nm: 468,
      oklch:   { l: 0.78, c: 0.07, h: 225 },
      hex:     '#a8cedf',
      munsell: '5B 8/4',
      color_temperature_k:    12000,
      psychological_effects:  [
        'Pale milky blue is the most universally calming colour in the visible spectrum',
        'The softness of blue calcite is unique — it does not activate or stimulate, it simply quiets',
        'Carries the quality of a clear sky after rain — the stillness that follows release',
        'Particularly effective for mental noise, anxiety, and the overactive mind',
      ],
      harmonics: {
        complementary_hue: 45,
        triadic_hues:      [345, 105],
        analogous_range:   [205, 245],
      },
    },

    metaphysical: {
      mineral_name:     'Blue Calcite',
      chakra_primary:   'Throat',
      chakra_secondary: ['Third Eye', 'Crown'],
      element:   ['Water', 'Air'],
      planet:    ['Moon', 'Neptune'],
      archetype: ['The Soother', 'The Still Mind', 'The Quiet Channel'],
      zodiac:    ['Cancer', 'Pisces', 'Aquarius'],
      numerology: 3,
      angel_number: 333,
      intention: 'My mind is still. I receive guidance in the quiet. All is well.',
      traditions: [
        'Western crystal healing — one of the most widely used anxiety and stress stones',
      ],
      properties: [
        'One of the most widely available and affordable blue stones in the crystal tradition',
        'The premier stone for anxiety, mental noise, and nervous system overload',
        'Extreme birefringence (0.172) — one of the highest in any common mineral — creates double-image optical effect',
        'Strong UV fluorescence — many specimens glow pink or red under longwave UV',
        'Supports restful sleep, calming dreams, and gentle spiritual receptivity',
        'Ideal for meditation, therapy spaces, and bedrooms — anywhere stillness is needed',
        'The most accessible entry point into blue stone work — widely available, inexpensive, immediately soothing',
      ],
      gaia_resonance: 'SomnusVeil + ClarusLens',
      safety_warning: 'Soft (H3) — easily scratched. Water-sensitive — calcite dissolves in acidic solutions. Do not use in water elixirs. Do not clean with vinegar or any acid-based cleaner.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. BLUE CHALCEDONY
  // Cryptocrystalline quartz — the stone of serenity and diplomacy
  // The speaker’s stone — used by ancient orators and diplomats
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Blue Chalcedony',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Jasper',

    physical: {
      id:           0,
      longid:       'blue-chalcedony',
      guid:         '',
      name:         'Chalcedony (blue variety)',
      ima_formula:  'SiO₂',
      mindat_formula: 'SiO2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '4.DA.05',
      dana8ed:      '75.1.3.1',
      crystal_system: 'Trigonal (microcrystalline)',
      hardness_min: 6.5,
      hardness_max: 7,
      specific_gravity_min: 2.58,
      specific_gravity_max: 2.64,
      cleavage:    'None',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Waxy', 'Dull'],
      diaphaneity: ['Translucent'],
      colour:      'Pale to medium blue — from Rayleigh scattering or trace mineral inclusions; soft, glowing quality',
      streak:      'White',
      fluorescence: 'Weak green or white under UV',
      ri_min:      1.530,
      ri_max:      1.540,
      birefringence: 0.004,
      optical_type: 'U',
      shortdesc:   'Blue variety of chalcedony — microcrystalline quartz. The characteristic glow of blue chalcedony results from Rayleigh scattering of light through the fine-grained matrix. Used in ancient Rome as an orator’s stone.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-955.html',
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Blue Chalcedony',
      refractive_index: { n: 1.535 },
      birefringence:   0.004,
      optical_sign:    '-',
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'Weak green or white',
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: { min: 450, max: 490 },
      spectra: [],
    },

    color: {
      primary_color:          'Pale to medium blue — with characteristic inner glow',
      color_variants:         ['Misty pale blue', 'Clear sky blue', 'Blue-grey', 'Lavender-blue', 'Periwinkle'],
      dominant_wavelength_nm: 470,
      oklch:   { l: 0.72, c: 0.09, h: 228 },
      hex:     '#8ab4cc',
      munsell: '5B 7/4',
      color_temperature_k:    11000,
      psychological_effects:  [
        'The inner glow of blue chalcedony — caused by Rayleigh scattering — creates a uniquely luminous quality',
        'Encourages the kind of clarity that is warm rather than cold — the diplomat’s blue',
        'Activates the capacity to listen before speaking — the first quality of great communication',
        'The misty, soft quality prevents the agitation that sharper blues can produce',
      ],
      harmonics: {
        complementary_hue: 48,
        triadic_hues:      [348, 108],
        analogous_range:   [208, 248],
      },
    },

    metaphysical: {
      mineral_name:     'Blue Chalcedony',
      chakra_primary:   'Throat',
      chakra_secondary: ['Third Eye', 'Heart'],
      element:   ['Water', 'Air'],
      planet:    ['Moon', 'Mercury'],
      archetype: ['The Diplomat', 'The Sacred Speaker', 'The Peacemaker'],
      zodiac:    ['Gemini', 'Cancer', 'Sagittarius'],
      numerology: 2,
      angel_number: 222,
      intention: 'I speak with wisdom and care. My words build bridges.',
      traditions: [
        'Ancient Roman tradition — orators wore blue chalcedony to speak clearly and persuasively',
        'Ancient Greek tradition — used in signet rings and amulets',
        'Native American tradition — used in ceremonial work and as a speaking stone',
        'Western crystal healing',
      ],
      properties: [
        'Microcrystalline quartz — the inner blue glow comes from Rayleigh scattering through the fine-grained matrix',
        'Ancient Roman orators carried blue chalcedony to improve speech, clarity, and persuasive power',
        'The premier diplomatic stone — supports communication that preserves relationship',
        'Encourages listening as much as speaking — the full cycle of communication',
        'Used in Native American tradition as a sacred speaking stone in council gatherings',
        'The gentler, warmer alternative to aquamarine for throat chakra work',
        'Supports those in negotiations, counselling, teaching, or any role where words carry weight',
      ],
      gaia_resonance: 'ClarusLens + ViriditasHeart',
      safety_warning: null,
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. BLUE GOLDSTONE
  // Man-made glass with copper inclusions — the night sky stone
  // NOT a natural mineral — human artistry made transcendent
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Blue Goldstone',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'man-made',
    yin_yang_pair: 'Sunstone',

    physical: {
      id:           0,
      longid:       'blue-goldstone',
      guid:         '',
      name:         'Goldstone (blue variety — man-made glass with cobalt + copper crystallites)',
      ima_formula:  'SiO₂ glass + Co (cobalt blue colourant) + Cu crystallites',
      mindat_formula: null,
      ima_status:   null,
      ima_year:     null,
      strunzten:    null,
      dana8ed:      null,
      crystal_system: 'Amorphous (glass)',
      hardness_min: 5.5,
      hardness_max: 6,
      specific_gravity_min: 2.50,
      specific_gravity_max: 2.70,
      cleavage:    'None',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Glittering (from metallic inclusions)'],
      diaphaneity: ['Translucent'],
      colour:      'Deep blue with brilliant sparkling copper crystallite inclusions — resembles a starfield',
      streak:      'White',
      fluorescence: null,
      ri_min:      1.500,
      ri_max:      1.520,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Man-made glass (aventurine glass) coloured cobalt blue with suspended metallic copper crystallites producing a starfield sparkle effect. Historically attributed to Venetian glassmakers of the 17th century Miotti family.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  null,
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Blue Goldstone',
      refractive_index: { n: 1.510 },
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: { min: 430, max: 480 },
      spectra: [],
    },

    color: {
      primary_color:          'Deep midnight blue with gold-white copper sparkle',
      color_variants:         ['Deep navy blue with silver-white stars', 'Cobalt blue with golden sparkle', 'Dark indigo starfield'],
      dominant_wavelength_nm: 450,
      oklch:   { l: 0.28, c: 0.18, h: 270 },
      hex:     '#1a2a6c',
      munsell: '7.5PB 3/8',
      color_temperature_k:    null,
      psychological_effects:  [
        'The starfield effect is one of the most cosmically evocative visual experiences in the stone tradition',
        'Deep blue-black with pinpoint light activates the imagination toward the infinite',
        'Encourages ambition, perspective, and the capacity to hold a vision larger than immediate circumstances',
        'The man-made origin is not a weakness — it is the expression of human aspiration toward the stars',
      ],
      harmonics: {
        complementary_hue: 90,
        triadic_hues:      [30, 150],
        analogous_range:   [250, 290],
      },
    },

    metaphysical: {
      mineral_name:     'Blue Goldstone',
      chakra_primary:   'Third Eye',
      chakra_secondary: ['Throat', 'Crown'],
      element:   ['Aether', 'Air'],
      planet:    ['Jupiter', 'Uranus'],
      archetype: ['The Star Gazer', 'The Cosmic Dreamer', 'The Night Sky'],
      zodiac:    ['Sagittarius', 'Aquarius', 'Libra'],
      numerology: 7,
      angel_number: 777,
      intention: 'I reach toward the stars. My vision is vast. I am made of light.',
      traditions: [
        'Venetian glass tradition — attributed to the Miotti family, 17th century',
        'Western crystal healing — included despite man-made origin for its unique cosmic resonance',
      ],
      properties: [
        'Man-made aventurine glass — NOT a natural mineral. Disclosed transparently in the GAIA-OS database.',
        'Attributed to 17th-century Venetian glassmakers (the Miotti family of Murano) who discovered the process accidentally',
        'The blue colour comes from cobalt oxide; the sparkle from suspended metallic copper crystallites',
        'Despite its artificial origin, carries genuine metaphysical resonance — human artistry as a spiritual act',
        'The premier stone for ambition, visionary thinking, and cosmic perspective',
        'Encourages those who feel small to remember they are looking at the same stars that guided ancient navigators',
        'The only man-made stone in the GAIA-OS tradition database — included because its beauty is real',
      ],
      gaia_resonance: 'Noosphere + QuantumNexus',
      safety_warning: 'Man-made glass — sharp edges if broken. Not a natural mineral — always disclose origin to clients. Do not confuse with natural aventurine or star sapphire.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. BLUE JOHN FLUORITE
  // Purple-banded fluorite — Castleton, Derbyshire, England only
  // The rarest and most culturally storied fluorite on Earth
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Blue John Fluorite',
    mindat_id:   1576,
    rruff_ids:   ['R050050'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Amber',

    physical: {
      id:           1576,
      longid:       'blue-john-fluorite',
      guid:         '',
      name:         'Fluorite (Blue John variety)',
      ima_formula:  'CaF₂',
      mindat_formula: 'CaF2',
      ima_status:   'A',
      ima_year:     1797,
      strunzten:    '3.AB.25',
      dana8ed:      '9.2.1.1',
      crystal_system: 'Isometric (cubic)',
      hardness_min: 4,
      hardness_max: 4,
      specific_gravity_min: 3.17,
      specific_gravity_max: 3.18,
      cleavage:    'Perfect octahedral on {111}',
      fracture:    'Subconchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Alternating bands of purple-violet and white or yellow — unique banding pattern found nowhere else on Earth',
      streak:      'White',
      fluorescence: 'Strong blue under UV — fluorite is the mineral that gave fluorescence its name',
      ri_min:      1.433,
      ri_max:      1.433,
      birefringence: null,
      optical_type: 'I',
      shortdesc:   'Rare banded variety of fluorite (CaF₂) found exclusively in Blue John Cavern and Treak Cliff Cavern at Castleton, Derbyshire, England. Named from French "bleu-jaune" (blue-yellow). Mined since Roman times.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-1576.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Blue John Fluorite',
      refractive_index: { n: 1.433 },
      birefringence:   null,
      optical_sign:    'I',
      dispersion:      '0.007',
      pleochroism:     null,
      fluorescence_lw: 'Strong blue — fluorite is the mineral that gave "fluorescence" its name',
      fluorescence_sw: 'Strong blue',
      phosphorescence: 'Possible',
      visible_wavelength_nm: { min: 380, max: 440 },
      spectra: ['R050050'],
    },

    color: {
      primary_color:          'Alternating purple-violet and white/yellow bands',
      color_variants:         ['Deep purple with cream bands', 'Pale lavender with white bands', 'Rich violet with yellow-white alternation', 'Twelve named banding patterns (e.g., Treak Blue, Millers Vein)'],
      dominant_wavelength_nm: 420,
      oklch:   { l: 0.50, c: 0.16, h: 310 },
      hex:     '#7a4a90',
      munsell: '5P 4/8',
      color_temperature_k:    null,
      psychological_effects:  [
        'The alternating purple and white banding creates a visual rhythm that is uniquely hypnotic',
        'Purple is the colour of sovereignty and ancient authority — in banded form it becomes ancestral',
        'The specific origin story — one hillside in Derbyshire — gives Blue John a sense of fierce locality',
        'Activates pride in heritage, place, and lineage — the stone of belonging to a particular land',
      ],
      harmonics: {
        complementary_hue: 130,
        triadic_hues:      [70, 190],
        analogous_range:   [290, 330],
      },
    },

    metaphysical: {
      mineral_name:     'Blue John Fluorite',
      chakra_primary:   'Crown',
      chakra_secondary: ['Third Eye', 'Root'],
      element:   ['Aether', 'Earth'],
      planet:    ['Saturn', 'Neptune'],
      archetype: ['The Ancestral Keeper', 'The Land Sovereign', 'The Ancient Craftsperson'],
      zodiac:    ['Capricorn', 'Pisces', 'Aquarius'],
      numerology: 7,
      angel_number: 777,
      intention: 'I honour my ancestors. I belong to this Earth. My lineage is sacred.',
      traditions: [
        'Roman Britain tradition — Blue John was mined and carved by Romans at Castleton for vases and ornaments',
        '18th-century English craft tradition — prized for decorative vases and fireplace ornaments',
        'Peak District cultural heritage — protected; only approx. 500kg mined annually',
      ],
      properties: [
        'The rarest locality-specific fluorite on Earth — found ONLY in Blue John Cavern and Treak Cliff Cavern, Castleton, Derbyshire',
        'Name from French "bleu-jaune" (blue-yellow) — describing the purple and yellow-white banding',
        'Fluorite gave the word "fluorescence" to science — it was the first mineral observed to fluoresce under UV',
        'Mined since Roman times — Roman vases of Blue John were found at Pompeii',
        'Production is legally limited to approximately 500kg per year to protect the deposit',
        'Twelve named banding varieties exist — each with a distinct visual signature and name',
        'The premier stone for ancestral connection, land sovereignty, and deep cultural rootedness',
      ],
      gaia_resonance: 'SovereignCore + ViriditasHeart + Noosphere',
      safety_warning: 'Soft (H4) — easily scratched. Perfect octahedral cleavage — avoid hard impacts. Water-sensitive — the resin stabilisation used in many Blue John specimens may be damaged by prolonged water exposure. Ethically sourced specimens only — the deposit is legally protected.',
    },
  },

];

export default BATCH_B1;

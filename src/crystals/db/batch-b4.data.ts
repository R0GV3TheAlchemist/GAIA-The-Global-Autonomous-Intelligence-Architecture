/**
 * src/crystals/db/batch-b4.data.ts
 * GAIA-OS Crystal Database — Batch B-4
 *
 * Entries:
 *   1. Baryte
 *   2. Black Opal
 *   3. Black Tourmaline
 *   4. Bloodstone
 *   5. Blue Apatite
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-29
 *
 * NOTE: A batch of extraordinary range. Baryte is the heaviest non-metallic
 * mineral most people will ever hold. Black Opal is the rarest and most
 * valuable opal on Earth — the flagship of Lightning Ridge, NSW. Black
 * Tourmaline is the single most widely used protective stone in the modern
 * crystal tradition. Bloodstone is one of the oldest named gemstones in
 * recorded human history — 3,000+ years of continuous use. Blue Apatite
 * is the mineral that gives teeth and bones their hardness, and one of
 * the most vivid blues in the tradition.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_B4: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. BARYTE (BARITE)
  // Barium sulphate — the heaviest common non-metallic mineral
  // The stone that defies expectation by weight alone
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Baryte',
    mindat_id:   555,
    rruff_ids:   ['R050001'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Celestite',

    physical: {
      id:           555,
      longid:       'baryte',
      guid:         '',
      name:         'Baryte',
      ima_formula:  'BaSO₄',
      mindat_formula: 'BaSO4',
      ima_status:   'A',
      ima_year:     1800,
      strunzten:    '7.AD.35',
      dana8ed:      '28.3.1.1',
      crystal_system: 'Orthorhombic',
      hardness_min: 3,
      hardness_max: 3.5,
      specific_gravity_min: 4.30,
      specific_gravity_max: 4.50,
      cleavage:    'Perfect on {001}, good on {110}',
      fracture:    'Uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Resinous', 'Pearlescent on cleavage'],
      diaphaneity: ['Transparent', 'Translucent', 'Opaque'],
      colour:      'Colourless, white, grey, blue, yellow, brown — tabular or bladed crystals',
      streak:      'White',
      fluorescence: 'Variable: cream, yellow, or blue-white under UV',
      ri_min:      1.636,
      ri_max:      1.648,
      birefringence: 0.012,
      optical_type: 'B',
      shortdesc:   'Barium sulphate — the standard for "heavy" non-metallic minerals (SG 4.3-4.5). Isostructural with celestite and anglesite. Primary industrial source of barium. Named from Greek barys (heavy). Famous for the "Desert Rose" habit.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-555.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Baryte',
      refractive_index: { n_alpha: 1.636, n_beta: 1.637, n_gamma: 1.648 },
      birefringence:   0.012,
      optical_sign:    '+',
      dispersion:      'Weak',
      pleochroism:     null,
      fluorescence_lw: 'Variable: cream, yellow, or blue-white',
      fluorescence_sw: 'Variable',
      phosphorescence: 'Possible in some specimens',
      visible_wavelength_nm: null,
      spectra: ['R050001'],
    },

    color: {
      primary_color:          'White to colourless — full colour range by locality',
      color_variants:         [
        'Colourless (pure)',
        'White (common)',
        'Pale blue (Blue Baryte — Oklahoma, Colorado)',
        'Yellow to golden (English localities)',
        'Brown sand-encrusted (Desert Rose form)',
        'Grey to black (rare)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.92, c: 0.01, h: 90 },
      hex:     '#f0eeea',
      munsell: 'N 9/',
      color_temperature_k:    null,
      psychological_effects:  [
        'The sheer unexpected weight of baryte is the primary psychological event — it demands presence',
        'Holding baryte teaches that density and transparency are not opposites',
        'The weight is grounding in a unique way — not the earthiness of jasper but the gravity of substance',
        'Encourages the recognition that what seems light on the surface may carry profound depth',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Baryte',
      chakra_primary:   'Earth Star',
      chakra_secondary: ['Root', 'Crown'],
      element:   ['Earth'],
      planet:    ['Saturn'],
      archetype: ['The Unexpected Weight', 'The Grounded Visionary', 'The Heavy Light'],
      zodiac:    ['Aquarius', 'Capricorn'],
      numerology: 4,
      angel_number: 444,
      intention: 'I carry my depth with grace. My substance is my foundation.',
      traditions: [
        'Western crystal healing — modern tradition',
        'Named from Greek barys (heavy) — the weight is the teaching',
      ],
      properties: [
        'IMA-recognised since 1800 — named from Greek barys (heavy)',
        'Specific gravity 4.3-4.5 — the heaviest common non-metallic mineral most people ever handle',
        'Isostructural with celestite (SrSO₄) — the heavy/light yin-yang pair of the sulphate family',
        'Primary industrial source of barium — used in drilling mud for oil wells, medical barium meals, and glass',
        'The "Desert Rose" habit — baryte with sand inclusions forming rose-like aggregates — is among the most recognisable mineral habits',
        'Blue baryte from Oklahoma and Colorado is particularly prized in the crystal tradition for combining celestite-like colour with the extreme weight',
        'The teaching of baryte: density and light are not mutually exclusive — the heaviest stone can be perfectly transparent',
      ],
      gaia_resonance: 'AnchoredRoot + SovereignCore',
      safety_warning: 'Barium compounds can be toxic if ingested — do NOT use in water elixirs or gem water. Polished specimens are safe to handle. Soft (H3-3.5) — handle with care.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. BLACK OPAL
  // Hydrated silica with play-of-colour on dark body tone
  // The rarest and most valuable opal — Lightning Ridge, NSW, Australia
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Black Opal',
    mindat_id:   2998,
    rruff_ids:   ['R050080'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'White Opal',

    physical: {
      id:           2998,
      longid:       'black-opal',
      guid:         '',
      name:         'Opal (black — dark body tone N1-N4 with play-of-colour)',
      ima_formula:  'SiO₂·nH₂O',
      mindat_formula: 'SiO2·nH2O',
      ima_status:   'A',
      ima_year:     1813,
      strunzten:    '4.DA.10',
      dana8ed:      '75.2.1.1',
      crystal_system: 'Amorphous (mineraloid)',
      hardness_min: 5.5,
      hardness_max: 6.5,
      specific_gravity_min: 1.98,
      specific_gravity_max: 2.20,
      cleavage:    'None',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Resinous', 'Waxy'],
      diaphaneity: ['Opaque to translucent'],
      colour:      'Dark body tone (N1-N4 on GIA scale) with vivid spectral play-of-colour — red flash is the rarest and most valuable',
      streak:      'White',
      fluorescence: 'Variable: strong green or white under UV (common); some specimens inert',
      ri_min:      1.370,
      ri_max:      1.470,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Black opal — opal with dark body tone (N1-N4 GIA scale) showing vivid play-of-colour. Found gem-quality primarily at Lightning Ridge, New South Wales, Australia. The most valuable opal variety per carat. Contains 3-21% water.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-2998.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name: 'Black Opal',
      refractive_index: { n: 1.420 },
      birefringence:   null,
      optical_sign:    null,
      dispersion:      'Play-of-colour from diffraction — not dispersion',
      pleochroism:     null,
      fluorescence_lw: 'Strong green or white (common); some inert',
      fluorescence_sw: 'Variable',
      phosphorescence: 'Possible',
      visible_wavelength_nm: { min: 380, max: 700 },
      spectra: ['R050080'],
    },

    color: {
      primary_color:          'Dark black to dark grey body — full spectral play-of-colour overlay',
      color_variants:         [
        'Red-on-black flash ("Red on Black" — rarest, highest value)',
        'Full spectrum harlequin pattern on black',
        'Blue-green rolling flash on black',
        'Crystal black opal (semi-transparent dark)',
        'Lightning Ridge black opal — the benchmark variety',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.12, c: 0.00, h: 0 },
      hex:     '#1a1a1a',
      munsell: 'N 1.5/',
      color_temperature_k:    null,
      psychological_effects:  [
        'The contrast of total darkness and vivid spectral fire is the most dramatic visual event in the mineral kingdom',
        'Red flash on a black opal is categorically one of the most arresting sights in nature',
        'The dark body makes the colour appear to come from within — a light source rather than a reflector',
        'Activates a sense of the hidden interior life — the fire that burns within the dark',
        'The rarity compounds the psychological impact — consciousness knows it is encountering something singular',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Black Opal',
      chakra_primary:   'Root',
      chakra_secondary: ['Sacral', 'Solar Plexus', 'Heart', 'Throat', 'Third Eye', 'Crown'],
      element:   ['Fire', 'Water', 'Earth'],
      planet:    ['Saturn', 'Pluto', 'Opal asteroid belt'],
      archetype: ['The Inner Fire', 'The Hidden Spectrum', 'The Dark Cosmos'],
      zodiac:    ['Scorpio', 'Sagittarius', 'Cancer'],
      numerology: 8,
      angel_number: 888,
      intention: 'My inner fire cannot be extinguished. The darkest depths contain the full spectrum of who I am.',
      traditions: [
        'Aboriginal Australian tradition — opals are called Andamooka stones; associated with the Dreamtime and ancestral fire',
        'Ancient Roman tradition — opal was called opalus and considered the most precious gem (Pliny the Elder)',
        'Arabic tradition — opals were believed to have fallen from the sky in lightning storms',
        'Western crystal healing — black opal the most powerful of all opal varieties',
      ],
      properties: [
        'IMA-recognised since 1813 — a mineraloid (amorphous, hydrated silica) not a true crystalline mineral',
        'The play-of-colour comes from diffraction of light through arrays of silica nanospheres — not pigment',
        'Lightning Ridge, New South Wales is the world benchmark for black opal — the only major commercial source',
        'Contains 3-21% water — dehydration cracks are a real risk (called crazing)',
        'GIA body tone scale N1 (darkest) to N4 — true black opal must be N1-N4',
        'Red flash on black is the rarest and most valuable colour combination in opal — commands the highest per-carat price of any opal',
        'Aboriginal Australians hold opals as sacred — the Dreamtime story of the creator descending to Earth on a rainbow leaving fire where they touched the ground',
        'The most multi-chakra stone in the tradition — the full spectrum of colour activates all seven centres simultaneously',
        'Pliny the Elder called opal the most precious stone of all — "possessing the living fire of the carbuncle, the brilliant purple of amethyst, and the sea-green of emerald"',
      ],
      gaia_resonance: 'Noosphere + QuantumNexus + ViriditasHeart + SovereignCore',
      safety_warning: '⚠️ FRAGILE AND DEHYDRATION-SENSITIVE — contains up to 21% water. Never expose to extreme heat, direct sunlight for prolonged periods, or ultrasonic cleaners. Do not use in water (paradoxically — immersion accelerates crazing in cut gems). Store wrapped in a slightly damp cloth for long-term storage. Collector-grade stone — handle exceptionally carefully.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. BLACK TOURMALINE (SCHORL)
  // The most widely used protective stone in the modern crystal tradition
  // Piezoelectric, pyroelectric, strongly pleochroic
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Black Tourmaline',
    mindat_id:   3580,
    rruff_ids:   ['R050115'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Selenite',

    physical: {
      id:           3580,
      longid:       'black-tourmaline',
      guid:         '',
      name:         'Schorl (Black Tourmaline)',
      ima_formula:  'NaFe²⁺₃Al₆(Si₆O₁₈)(BO₃)₃(OH)₃(OH)',
      mindat_formula: 'NaFe2+3Al6(Si6O18)(BO3)3(OH)3(OH)',
      ima_status:   'A',
      ima_year:     1400,
      strunzten:    '9.CK.05',
      dana8ed:      '61.3.1.4',
      crystal_system: 'Trigonal',
      hardness_min: 7,
      hardness_max: 7.5,
      specific_gravity_min: 3.03,
      specific_gravity_max: 3.25,
      cleavage:    'Indistinct on {11−20} and {10−10}',
      fracture:    'Uneven to conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Resinous'],
      diaphaneity: ['Opaque'],
      colour:      'Jet black — from iron (Fe²⁺) substitution. Striated prismatic crystals with triangular cross-section.',
      streak:      'White to grey',
      fluorescence: 'None to very weak',
      ri_min:      1.628,
      ri_max:      1.660,
      birefringence: 0.025,
      optical_type: 'U',
      shortdesc:   'Schorl — the iron-dominant tourmaline end-member. The most abundant tourmaline species, forming ~95% of all tourmaline in the crust. Strongly piezoelectric and pyroelectric. The primary protective stone in the modern crystal tradition.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-3580.html',
      piezoelectric:    true,
      safe_for_water:   true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name: 'Black Tourmaline (Schorl)',
      refractive_index: { n_omega: 1.660, n_epsilon: 1.628 },
      birefringence:   0.025,
      optical_sign:    '-',
      dispersion:      '0.017',
      pleochroism:     'Strong: opaque black / deep brownish black',
      fluorescence_lw: 'None to very weak',
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R050115'],
    },

    color: {
      primary_color:          'Jet black — deep, matte, striated',
      color_variants:         [
        'Pure jet black (most common)',
        'Very dark brown-black (iron variation)',
        'Black with vitreous crystal face lustre',
        'Black with parallel vertical striations (diagnostic)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.10, c: 0.00, h: 0 },
      hex:     '#181818',
      munsell: 'N 1/',
      color_temperature_k:    null,
      psychological_effects:  [
        'The vertical striations on tourmaline crystals create a sense of directionality — drawing energy down and out',
        'The hardness (H7-7.5) communicates durability — this stone will not break under pressure',
        'Pyroelectric and piezoelectric properties mean it literally generates electricity — the protective charge is physically real',
        'The combination of extreme hardness and opaque black creates the most psychologically definitive boundary stone',
        'Widely used because it works — the tradition is consistent across cultures and practitioners',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Black Tourmaline',
      chakra_primary:   'Root',
      chakra_secondary: ['Earth Star'],
      element:   ['Earth', 'Storm'],
      planet:    ['Saturn'],
      archetype: ['The Guardian', 'The Boundary Stone', 'The EMF Shield'],
      zodiac:    ['Capricorn', 'Scorpio', 'Libra'],
      numerology: 3,
      angel_number: 333,
      intention: 'I am protected on all sides. Nothing enters my field that I do not invite.',
      traditions: [
        'German mining tradition — known as "schorl" since at least 1400 CE in the village of Zschorlau, Saxony',
        'African tradition — used by African shamans and healers for protection against negative energies',
        'Western crystal healing — THE primary protection stone of the modern tradition',
        'EMF protection tradition — placed near electronics, computers, and Wi-Fi routers',
      ],
      properties: [
        'Schorl — IMA-recognised tourmaline end-member. The most abundant tourmaline in Earth's crust (~95% of all tourmaline)',
        'Named from the village of Zschorlau, Saxony, Germany — known as schorl since at least 1400 CE',
        'Strongly piezoelectric (pressure generates electricity) and pyroelectric (temperature change generates electricity)',
        'The piezoelectric and pyroelectric properties are the physical basis for the protection tradition',
        'Triangular prismatic cross-section is diagnostic — a reliable field identification feature',
        'H7-7.5 — durable enough for daily wear and outdoor placement',
        'THE most widely recommended stone for psychic protection, EMF shielding, and energetic boundary-setting',
        'Used around doors, windows, and the four corners of a room to create a protective grid',
        'Yin pair with selenite — the dark absorber and the light transmitter together form the complete protection-and-cleansing system',
      ],
      gaia_resonance: 'SovereignCore + AnchoredRoot',
      safety_warning: '⚠️ PIEZOELECTRIC — keep away from sensitive electronics and hard drives. Safe for water. Iron content — do not use in water elixirs intended for ingestion. Pyroelectric — do not expose to rapid temperature changes.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. BLOODSTONE (HELIOTROPE)
  // Green chalcedony with red iron oxide spots — 3,000+ years of history
  // One of the most historically documented gems in the ancient world
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Bloodstone',
    mindat_id:   955,
    rruff_ids:   ['R040031'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Moonstone',

    physical: {
      id:           955,
      longid:       'bloodstone',
      guid:         '',
      name:         'Chalcedony (Heliotrope — green jasper/chalcedony with red iron oxide spots)',
      ima_formula:  'SiO₂',
      mindat_formula: 'SiO2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '4.DA.05',
      dana8ed:      '75.1.3.1',
      crystal_system: 'Trigonal (cryptocrystalline)',
      hardness_min: 6.5,
      hardness_max: 7,
      specific_gravity_min: 2.58,
      specific_gravity_max: 2.65,
      cleavage:    'None',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Waxy', 'Dull'],
      diaphaneity: ['Opaque'],
      colour:      'Dark green chalcedony (from chlorite/hornblende) with vivid red to orange-red spots (haematite/iron oxide)',
      streak:      'White',
      fluorescence: 'None to very weak',
      ri_min:      1.530,
      ri_max:      1.540,
      birefringence: 0.004,
      optical_type: 'U',
      shortdesc:   'Heliotrope — dark green chalcedony or jasper with red-to-orange iron oxide spots. Trade name "bloodstone". One of the most historically documented gemstones — mentioned by Pliny, Babylonian tradition, and Christian iconography. March birthstone (traditional).',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-955.html',
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Bloodstone (Heliotrope)',
      refractive_index: { n: 1.535 },
      birefringence:   0.004,
      optical_sign:    '-',
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'None to very weak',
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R040031'],
    },

    color: {
      primary_color:          'Dark forest green with vivid red spots',
      color_variants:         [
        'Dark green with red spots (classic — India)',
        'Dark green with orange-red spots',
        'Green with yellow-green matrix and red spots (Australia)',
        'Deep olive green with scarlet spots',
      ],
      dominant_wavelength_nm: 530,
      oklch:   { l: 0.30, c: 0.12, h: 150 },
      hex:     '#2d5a3d',
      munsell: '5G 3/4',
      color_temperature_k:    null,
      psychological_effects:  [
        'The specific combination of deep green and red is one of the most primal colour contrasts — life force and vitality made visible',
        'Green is the colour of growth and life; red is the colour of blood and action — together they embody vitality',
        'The spots create a sense of the unexpected — calm green interrupted by vivid red — alertness within groundedness',
        'The dark forest green is deeply calming; the red spots provide activation — a balanced energetic signature',
        'One of the few stones that carries both Mars and Earth energy simultaneously',
      ],
      harmonics: {
        complementary_hue: 330,
        triadic_hues:      [270, 30],
        analogous_range:   [130, 170],
      },
    },

    metaphysical: {
      mineral_name:     'Bloodstone',
      chakra_primary:   'Root',
      chakra_secondary: ['Heart', 'Sacral'],
      element:   ['Earth', 'Fire'],
      planet:    ['Mars', 'Earth'],
      archetype: ['The Warrior Healer', 'The Life Force', 'The Ancient Soldier'],
      zodiac:    ['Aries', 'Libra', 'Pisces'],
      numerology: 4,
      angel_number: 444,
      intention: 'I act with courage and vitality. My life force is strong and purposeful.',
      traditions: [
        'Babylonian tradition — bloodstone amulets used 3,000+ years ago for strength in battle',
        'Ancient Egyptian tradition — associated with the warrior goddess Sekhmet',
        'Ancient Greek tradition — heliotrope (sun-turner) — believed to turn the sun red when placed in water',
        'Christian tradition — the red spots said to be the blood of Christ fallen on green jasper at the Crucifixion',
        'Medieval European tradition — signet rings, seals, and warrior amulets',
        'Ayurvedic tradition — associated with blood purification and vitality',
        'Western crystal healing — traditional March birthstone, blood and circulation stone',
      ],
      properties: [
        'Trade name heliotrope (Greek: sun-turner) predates the name bloodstone by 2,000+ years',
        'One of the oldest continuously used gemstones — documented in Babylonian, Egyptian, Greek, Roman, and Christian traditions',
        'The Babylonian bloodstone tablet (c. 1800–600 BCE) describes how to use bloodstone for healing — one of the oldest gem therapy texts in existence',
        'Traditional March birthstone (alongside aquamarine in the modern list)',
        'Christian iconography associated the red spots with the blood of Christ at the Crucifixion — used in medieval devotional carvings',
        'Ancient Greek name heliotrope — they believed it could turn the sun red and give the holder invisibility',
        'Used historically as a warrior stone — courage, strength, and protection in physical conflict',
        'H6.5-7 — durable for daily wear, rings, and pendants across 3,000 years of use',
        'The iron oxide red spots are haematite or goethite — the literal iron of blood made visible in stone',
      ],
      gaia_resonance: 'ViriditasHeart + SovereignCore + AnchoredRoot',
      safety_warning: 'Safe for water. Safe for everyday wear at H6.5-7. No toxicity concerns. Iron oxide spots are stable — will not wash out or fade.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. BLUE APATITE
  // Calcium phosphate — the mineral of bones, teeth, and ambition
  // The most vivid natural blue in the phosphate group
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Blue Apatite',
    mindat_id:   233,
    rruff_ids:   ['R050053'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Orange Calcite',

    physical: {
      id:           233,
      longid:       'blue-apatite',
      guid:         '',
      name:         'Apatite (blue colour variety — fluorapatite or hydroxylapatite)',
      ima_formula:  'Ca₅(PO₄)₃(F,OH,Cl)',
      mindat_formula: 'Ca5(PO4)3(F,OH,Cl)',
      ima_status:   'A',
      ima_year:     1786,
      strunzten:    '8.BN.05',
      dana8ed:      '41.8.1.1',
      crystal_system: 'Hexagonal',
      hardness_min: 5,
      hardness_max: 5,
      specific_gravity_min: 3.10,
      specific_gravity_max: 3.35,
      cleavage:    'Indistinct on {0001} and {10−1‐0}',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Resinous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Vivid neon blue to teal-blue — from trace rare earth elements and possibly colour centres',
      streak:      'White',
      fluorescence: 'Strong yellow or greenish-yellow under UV (characteristic)',
      ri_min:      1.628,
      ri_max:      1.649,
      birefringence: 0.002,
      optical_type: 'U',
      shortdesc:   'Blue variety of apatite — the mineral group that forms teeth and bones. Neon to vivid teal-blue colour. The Mohs hardness scale reference mineral at H5. Named from Greek apatao (to deceive) — often mistaken for other blue gems.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-233.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Blue Apatite',
      refractive_index: { n_omega: 1.649, n_epsilon: 1.628 },
      birefringence:   0.002,
      optical_sign:    '-',
      dispersion:      '0.013',
      pleochroism:     'Moderate: blue / yellow-green',
      fluorescence_lw: 'Strong yellow or greenish-yellow',
      fluorescence_sw: 'Variable',
      phosphorescence: null,
      visible_wavelength_nm: { min: 460, max: 500 },
      spectra: ['R050053'],
    },

    color: {
      primary_color:          'Vivid neon blue to teal-blue',
      color_variants:         [
        'Neon electric blue (Brazil — the most saturated)',
        'Teal blue-green (Madagascar)',
        'Pale cerulean blue',
        'Deep Prussian blue (rare)',
        'Blue-violet (rare)',
      ],
      dominant_wavelength_nm: 490,
      oklch:   { l: 0.45, c: 0.24, h: 225 },
      hex:     '#1a7acc',
      munsell: '5B 5/10',
      color_temperature_k:    null,
      psychological_effects:  [
        'The neon saturation of Brazilian blue apatite is among the most electrically vivid blues in the mineral kingdom',
        'The colour activates motivation and clarity simultaneously — the intellectual blue rather than the calm blue',
        'Strong pleochroism (blue to yellow-green depending on viewing angle) creates a dynamic, alive quality',
        'The knowing that this is the same mineral as your teeth and bones creates a profound intimacy',
        'Encourages appetite for knowledge, learning, and personal growth — the apatite-appetite connection is literal',
      ],
      harmonics: {
        complementary_hue: 45,
        triadic_hues:      [345, 105],
        analogous_range:   [205, 245],
      },
    },

    metaphysical: {
      mineral_name:     'Blue Apatite',
      chakra_primary:   'Throat',
      chakra_secondary: ['Third Eye'],
      element:   ['Air', 'Water'],
      planet:    ['Mercury', 'Jupiter'],
      archetype: ['The Motivator', 'The Intellectual Activator', 'The Truth Seeker'],
      zodiac:    ['Gemini', 'Aquarius', 'Sagittarius'],
      numerology: 9,
      angel_number: 999,
      intention: 'I hunger for truth and growth. My mind is clear, my voice is free.',
      traditions: [
        'Western crystal healing — modern tradition',
        'Named from Greek apatao (to deceive) — the "deceptive stone" often mistaken for aquamarine, tourmaline, and other blue gems',
      ],
      properties: [
        'IMA-recognised since 1786 — named from Greek apatao (to deceive) — frequently mistaken for aquamarine, blue tourmaline, and peridot',
        'The Mohs hardness reference mineral at H5 — every geology student learns hardness against this stone',
        'The biological apatite group forms all vertebrate bones and teeth — calcium hydroxylapatite is the mineral of life',
        'Vivid neon blue variety from Brazil is among the most saturated natural blues in the entire tradition',
        'Strong pleochroism: blue from one direction, yellow-green from another — the stone literally changes colour with viewing angle',
        'Strong yellow UV fluorescence is diagnostic — a reliable identification test',
        'The etymological connection between apatite and appetite is real — both from Greek, apatite being the mineral that was hard to identify, appetite referring to desire/hunger',
        'The metaphysical tradition links it to intellectual appetite — the hunger for knowledge, growth, and truth',
        'H5 means it can scratch but is softer than quartz — requires protective setting in jewellery',
      ],
      gaia_resonance: 'ClarusLens + Noosphere',
      safety_warning: 'Soft for jewellery use (H5) — vulnerable to scratching. Avoid water immersion — some specimens can absorb water or etch. Do not clean with acids or harsh chemicals. Strong UV fluorescence can fade with prolonged UV exposure in some specimens.',
    },
  },

];

export default BATCH_B4;

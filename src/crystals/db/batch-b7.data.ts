/**
 * src/crystals/db/batch-b7.data.ts
 * GAIA-OS Crystal Database — Batch B-7
 *
 * Entries:
 *   1. Botallackite                        — rare secondary copper hydroxychloride
 *   2. Botswana Agate                      — banded agate, Kaollong Formation, Botswana
 *   3. Brandberg Amethyst                  — phantom quartz from Brandberg massif, Namibia
 *   4. Brazilianite                        — rare yellow-green phosphate gemstone
 *   5. Bronzite                            — enstatite variety with schiller effect
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-29
 *
 * NOTE: Botallackite, Botswana Agate, and Brandberg Amethyst carried over from
 * original B-7 list after deduplication correction (Boji Stones and Bornite
 * correctly remain in B-6). Brazilianite and Bronzite added to complete to 5.
 * Bustamite deferred to B-8 as first entry.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_B7: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. BOTALLACKITE
  // Rare secondary copper(II) hydroxychloride — named after Botallack Mine, Cornwall
  // One of the rarest and most geographically specific named minerals in crystal healing
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Botallackite',
    mindat_id:   769,
    rruff_ids:   ['R060750'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Atacamite',

    physical: {
      id:           769,
      longid:       'botallackite',
      guid:         '',
      name:         'Botallackite',
      ima_formula:  'Cu₂(OH)₃Cl',
      mindat_formula: 'Cu2(OH)3Cl',
      ima_status:   'A',
      ima_year:     1865,
      strunzten:    '3.DA.10a',
      dana8ed:      '10.3.1.1',
      crystal_system: 'Monoclinic',
      hardness_min: 3,
      hardness_max: 3,
      specific_gravity_min: 3.59,
      specific_gravity_max: 3.61,
      cleavage:    'Perfect on {001}',
      fracture:    'Uneven',
      tenacity:    'Brittle',
      luster:      ['Adamantine', 'Vitreous'],
      diaphaneity: ['Translucent'],
      colour:      'Pale blue-green to sea green — the colour of shallow Caribbean seawater over white sand; characteristic copper chloride green',
      streak:      'Pale blue-green',
      fluorescence: 'None reported',
      ri_min:      1.726,
      ri_max:      1.793,
      birefringence: 0.067,
      optical_type: 'B',
      shortdesc:   'Botallackite — Cu₂(OH)₃Cl, rare secondary copper hydroxychloride. Named after the historic Botallack Mine, St Just, Cornwall, England (type locality). A polymorph of atacamite, paratacamite, and clinoatacamite. Occurs on oxidised copper ore surfaces near the sea where chlorine is present.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-769.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Botallackite',
      refractive_index: { n_alpha: 1.726, n_beta: 1.762, n_gamma: 1.793 },
      birefringence:   0.067,
      optical_sign:    '-',
      dispersion:      'r > v, strong',
      pleochroism:     'Distinct: pale blue-green / green / blue-green',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 480, max: 530 },
      spectra: ['R060750'],
    },

    color: {
      primary_color:          'Pale blue-green to sea green — the colour of shallow tropical seawater',
      color_variants:         [
        'Pale aqua blue-green (freshest, least altered)',
        'Sea green (intermediate)',
        'Deeper emerald green (more altered, approaching atacamite)',
        'Powder-blue crust on copper ore matrix',
      ],
      dominant_wavelength_nm: 505,
      oklch:   { l: 0.55, c: 0.15, h: 185 },
      hex:     '#4fada8',
      munsell: '5BG 6/6',
      color_temperature_k:    null,
      psychological_effects:  [
        'The pale sea-green perfectly matches the colour of water in a shallow Cornish cove — a geological echo of the coastal origin',
        'The rarity and geological specificity create a strong sense of provenance and place — you hold a fragment of a specific cliff face',
        'The translucency and adamantine lustre give these small crystals a jewel-like quality that belies their mineral simplicity',
        'Named for a single mine creates a powerful sense of connection to human mining history and the land',
        'The softness (H3) and fragility communicate impermanence — rare beauty that asks to be held gently',
      ],
      harmonics: {
        complementary_hue: 5,
        triadic_hues:      [305, 65],
        analogous_range:   [165, 205],
      },
    },

    metaphysical: {
      mineral_name:     'Botallackite',
      chakra_primary:   'Heart',
      chakra_secondary: ['Throat', 'Higher Heart (Thymus)'],
      element:   ['Water', 'Earth'],
      planet:    ['Venus', 'Neptune'],
      archetype: ['The Coastal Mystic', 'The Rare Witness', 'The Keeper of Place'],
      zodiac:    ['Taurus', 'Pisces', 'Cancer'],
      numerology: 7,
      angel_number: 777,
      intention: 'I honour the rare and sacred in the ordinary world. I am a witness to beauty that asks nothing of me but presence.',
      traditions: [
        'Named after Botallack Mine, St Just-in-Penwith, Cornwall — one of the most famous Cornish tin and copper mines, partially submerged under the Atlantic Ocean',
        'Cornwall mining tradition — the copper deposits of west Cornwall were worked from the Bronze Age through to the 20th century',
        'IMA-recognised since 1865 — described by mineralogist J.H. Collins from type specimens at Botallack',
        'Western crystal healing — rare copper hydroxychlorides used for Heart and Higher Heart chakra work',
      ],
      properties: [
        'IMA-recognised 1865 — type locality: Botallack Mine, St Just-in-Penwith, Cornwall, England',
        'Formula Cu₂(OH)₃Cl — copper(II) hydroxychloride; polymorphic with atacamite, paratacamite, and clinoatacamite (same formula, different crystal structures)',
        'Monoclinic — the only monoclinic polymorph of Cu₂(OH)₃Cl; the other polymorphs are orthorhombic (atacamite) and rhombohedral/trigonal (paratacamite, clinoatacamite)',
        'Forms as a secondary mineral on oxidised copper ore surfaces in coastal / near-marine environments where chloride ions are abundant (sea spray, marine sediments)',
        'Named for one of the most romantically situated mines in England — Botallack\'s engine houses perch on granite cliffs above the Atlantic, its tunnels extending under the seabed',
        'Also found: Chile (Atacama Desert — same Cu chloride chemistry, different aridity context), Namibia, Australia, New South Wales',
        'Collectors\' note: botallackite is metastable and may slowly convert to atacamite or clinoatacamite over time; keep dry and stable',
        'Soft (H3) — handle gently; do not tumble. Copper content — TOXIC in elixirs.',
      ],
      gaia_resonance: 'ClarusLens + ViriditasHeart',
      safety_warning: '\u26a0\ufe0f TOXIC — copper hydroxychloride. DO NOT use in water elixirs, gem water, or any ingestible preparation. Copper compounds are toxic if ingested. Do NOT use in direct drinking water contact. Keep dry (metastable — may convert to atacamite). H3 — fragile; handle with care.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. BOTSWANA AGATE
  // Banded chalcedony — Kaollong Formation, Botswana — arguably the world's
  // finest banded agate for its parallel banding precision and warm palette
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Botswana Agate',
    mindat_id:   32,
    rruff_ids:   ['R040031'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Blue Lace Agate',

    physical: {
      id:           32,
      longid:       'botswana-agate',
      guid:         '',
      name:         'Chalcedony / Agate ("Botswana Agate" — banded chalcedony, Kaollong Formation, Botswana)',
      ima_formula:  'SiO₂',
      mindat_formula: 'SiO2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '4.DA.05',
      dana8ed:      '75.1.3.6',
      crystal_system: 'Trigonal (microcrystalline aggregate)',
      hardness_min: 6.5,
      hardness_max: 7,
      specific_gravity_min: 2.58,
      specific_gravity_max: 2.64,
      cleavage:    'None',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Waxy', 'Vitreous'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Creamy white, pale pink, apricot, mauve, grey, lavender, warm brown — arranged in exceptionally fine, parallel concentric bands. The warm peachy-pink palette is the most distinctive and sought-after feature.',
      streak:      'White',
      fluorescence: 'Some bands fluorescent pale green or white under LW UV',
      ri_min:      1.530,
      ri_max:      1.540,
      birefringence: 0.004,
      optical_type: 'U',
      shortdesc:   'Botswana Agate — banded chalcedony from the Kaollong Formation, Botswana. Widely regarded as the world\'s finest banded agate for precision of banding, warmth of palette, and size of nodules. Primary colours: creamy white, pale pink, apricot, mauve, lavender, grey.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-32.html',
      piezoelectric:    true,
      safe_for_water:   true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Botswana Agate (Banded Chalcedony)',
      refractive_index: { n_omega: 1.540, n_epsilon: 1.536 },
      birefringence:   0.004,
      optical_sign:    '+',
      dispersion:      '0.013',
      pleochroism:     'None',
      fluorescence_lw: 'Some bands fluorescent pale green or white',
      fluorescence_sw: 'None to very weak',
      phosphorescence: null,
      visible_wavelength_nm: { min: 580, max: 650 },
      spectra: ['R040031'],
    },

    color: {
      primary_color:          'Warm banded palette — creamy white, pale pink, apricot, mauve, lavender, grey',
      color_variants:         [
        'Classic pale pink and white banding (most coveted — the "Botswana look")',
        'Apricot-peach and cream banding',
        'Grey and white precision banding',
        'Lavender, mauve, and cream (rarer)',
        'Rich caramel-brown, cream, and pink (deeper iron content)',
        'Fortification agate pattern (chevron/angular banding — rarer form)',
      ],
      dominant_wavelength_nm: 600,
      oklch:   { l: 0.78, c: 0.06, h: 30 },
      hex:     '#e8c9b8',
      munsell: '5YR 8/3',
      color_temperature_k:    null,
      psychological_effects:  [
        'The warm peachy-pink palette is one of the most universally soothing colour combinations in the mineral kingdom',
        'The precision of the parallel banding — millimetre-perfect concentric rings — creates a profound sense of natural order',
        'Each band represents a discrete silica deposition event — time made visible in a way that invites reflection on patience',
        'The translucency with backlight creates an inner glow that makes the stone feel lit from within',
        'The warm, maternal palette psychologically registers as safe, nourishing, and stabilising',
      ],
      harmonics: {
        complementary_hue: 210,
        triadic_hues:      [150, 270],
        analogous_range:   [10, 50],
      },
    },

    metaphysical: {
      mineral_name:     'Botswana Agate',
      chakra_primary:   'Root',
      chakra_secondary: ['Sacral', 'Heart'],
      element:   ['Earth', 'Fire'],
      planet:    ['Mercury', 'Moon'],
      archetype: ['The Patient Builder', 'The Nurturer', 'The Keeper of Increments'],
      zodiac:    ['Scorpio', 'Gemini', 'Taurus'],
      numerology: 3,
      angel_number: 333,
      intention: 'I grow in beautiful, patient layers. Each increment of my life is a band of perfect order.',
      traditions: [
        'Western crystal healing — Botswana Agate as the premier comfort and stability stone',
        'African origin — Botswana, southern Africa; the Kaollong Formation yields the world\'s largest, finest banded agate nodules',
        'Agate tradition reaching back to ancient Mesopotamia, Egypt, and Rome — used in seals, amulets, and jewellery since at least 3000 BCE',
      ],
      properties: [
        'Trade name: "Botswana Agate" — specific to banded chalcedony nodules from the Kaollong Formation, Botswana',
        'World\'s primary source of premium banded agate — nodules up to 30cm+ in diameter with exceptional banding regularity',
        'Each band = one silica deposition event; banding reflects changes in silica concentration, trace elements, and fluid chemistry over geological time',
        'Warm pink/apricot palette from trace iron oxides (haematite, goethite) distributed differentially between bands',
        'Some bands fluoresce pale green or white under LW UV — useful for identifying natural vs. dyed material',
        'H6.5–7 — one of the most durable crystals for everyday use and jewellery',
        'Piezoelectric — keep away from hard drives and sensitive electronics',
      ],
      gaia_resonance: 'AnchorPrism + ViriditasHeart',
      safety_warning: '\u26a0\ufe0f PIEZOELECTRIC — keep away from hard drives and sensitive electronics. Safe for water. Dyed specimens exist — natural Botswana Agate has warm, subtle tones; dyed material has unnaturally vivid pinks, purples, or blues.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. BRANDBERG AMETHYST
  // Phantom quartz from Brandberg Mountain, Namibia
  // Amethyst + smoky + phantom + enhydro — all in one crystal
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Brandberg Amethyst',
    mindat_id:   3337,
    rruff_ids:   ['R040031'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Amethyst (general)',

    physical: {
      id:           3337,
      longid:       'brandberg-amethyst',
      guid:         '',
      name:         'Quartz (Brandberg Amethyst — amethyst/smoky phantom quartz, Brandberg Mountain, Namibia)',
      ima_formula:  'SiO₂',
      mindat_formula: 'SiO2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '4.DA.05',
      dana8ed:      '75.1.3.1',
      crystal_system: 'Trigonal',
      hardness_min: 7,
      hardness_max: 7,
      specific_gravity_min: 2.65,
      specific_gravity_max: 2.66,
      cleavage:    'None',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Complex: zones of amethyst purple, smoky grey-brown, clear/colourless, phantoms, enhydros, and lepidocrocite (red/orange) inclusions. No two are identical.',
      streak:      'White',
      fluorescence: 'None to very weak blue-white under LW UV',
      ri_min:      1.544,
      ri_max:      1.553,
      birefringence: 0.009,
      optical_type: 'U',
      shortdesc:   'Brandberg Amethyst — quartz from Brandberg Mountain (Königstein), Erongo Region, Namibia. Combines amethyst, smoky quartz, phantom layers, enhydros, and other inclusions in a single crystal. The most complex and revered quartz locality on Earth. Each crystal is unique.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-3337.html',
      piezoelectric:    true,
      safe_for_water:   true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Brandberg Amethyst (Phantom Quartz)',
      refractive_index: { n_omega: 1.553, n_epsilon: 1.544 },
      birefringence:   0.009,
      optical_sign:    '+',
      dispersion:      '0.013',
      pleochroism:     'Weak dichroic in amethyst zones: purple / pale purple (reddish)',
      fluorescence_lw: 'None to very weak blue-white',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 390, max: 420 },
      spectra: ['R040031'],
    },

    color: {
      primary_color:          'Complex multi-zone: amethyst purple + smoky grey-brown + clear + phantom layers + inclusions',
      color_variants:         [
        'Amethyst-dominant with smoky phantom interior',
        'Smoky-dominant with amethyst tip zone',
        'Clear with multiple phantom layers',
        'Amethyst with red/orange lepidocrocite inclusions (rare, highly prized)',
        'Enhydro — water bubble trapped in visible cavity',
        'Window crystal — flat side faces revealing interior phantom structure',
      ],
      dominant_wavelength_nm: 405,
      oklch:   { l: 0.48, c: 0.14, h: 315 },
      hex:     '#8b5fa8',
      munsell: '5P 5/6',
      color_temperature_k:    null,
      psychological_effects:  [
        'Phantom layers — ghost crystals within the crystal — create a layered, archaeological sense of time and personal history',
        'Amethyst purple + smoky grey in one crystal produces integrated spiritual clarity and grounded wisdom simultaneously',
        'Each crystal is unique to a single mountain in Namibia — profound specificity that no other quartz locality offers',
        'Enhydros invoke the most primal connection to ancient geological water — the primordial ocean',
        'Brandberg Mountain carries 50,000+ ancient San rock paintings — the crystal holds that cultural weight',
      ],
      harmonics: {
        complementary_hue: 135,
        triadic_hues:      [75, 195],
        analogous_range:   [295, 335],
      },
    },

    metaphysical: {
      mineral_name:     'Brandberg Amethyst',
      chakra_primary:   'Crown',
      chakra_secondary: ['Third Eye', 'Soul Star', 'All chakras (integrated)'],
      element:   ['Akasha', 'Storm', 'Air', 'Fire'],
      planet:    ['Neptune', 'Pluto', 'Moon', 'Sun'],
      archetype: ['The Complete One', 'The Mountain Keeper', 'The Ancient Witness', 'The Integrated Self'],
      zodiac:    ['Pisces', 'Aquarius', 'Scorpio', 'All signs'],
      numerology: 9,
      angel_number: 999,
      intention: 'I carry the full spectrum of my becoming within me — every stage, every shadow, every light. I am complete.',
      traditions: [
        'Namibian origin — Brandberg Mountain (Königstein), Erongo Region, Namibia; Africa\'s largest intrusive granite massif, 2573m',
        'UNESCO World Heritage Site candidate — home to over 50,000 ancient San rock paintings including the "White Lady" (~2000 years old)',
        'San (Bushmen) tradition — the Brandberg (Dâures in Damara/Nama) is a sacred mountain; crystals carry the mountain\'s consciousness',
        'Modern Western crystal healing — widely regarded as the highest-vibration quartz on Earth',
      ],
      properties: [
        'Trade name: "Brandberg Amethyst" — specific to quartz from Brandberg Mountain (Königstein), Erongo Region, Namibia',
        'Unique combination: amethyst (Fe³⁺ colour centres) + smoky quartz (irradiation colour centres) + phantom layers + enhydros + optional lepidocrocite inclusions',
        'Phantoms form when crystal growth pauses, a coating forms, then growth resumes — encapsulating the earlier form as a visible "ghost"',
        'Enhydros are genuine ancient water inclusions — visible as a moving bubble — some potentially millions of years old',
        'Brandberg Mountain — Africa\'s largest intrusive granite massif (2573m) — magmatic complexity created extraordinarily varied quartz mineralogy',
        'No two Brandberg crystals are identical — variation of phantom, colour zone, inclusion type, and habit is effectively infinite',
        'Piezoelectric — keep away from hard drives and sensitive electronics',
        'H7 — durable for meditation and display; protect terminations',
      ],
      gaia_resonance: 'QuantumNexus + ClarusLens + AnchorPrism + Noosphere + ViriditasHeart + SovereignCore',
      safety_warning: '\u26a0\ufe0f PIEZOELECTRIC — keep away from hard drives and sensitive electronics. Safe for water. H7 — protect terminations. Enhydros: avoid rapid temperature changes. Phantom layers may create unexpected emotional resonance in sensitive practitioners — approach with grounded intention.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. BRAZILIANITE
  // Rare yellow-green phosphate gem — NaAl₃(PO₄)₂(OH)₄
  // Named for Brazil, its only significant locality
  // IMA-recognised 1945 — discovered accidentally during WWII
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Brazilianite',
    mindat_id:   790,
    rruff_ids:   ['R060518'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Peridot',

    physical: {
      id:           790,
      longid:       'brazilianite',
      guid:         '',
      name:         'Brazilianite',
      ima_formula:  'NaAl₃(PO₄)₂(OH)₄',
      mindat_formula: 'NaAl3(PO4)2(OH)4',
      ima_status:   'A',
      ima_year:     1945,
      strunzten:    '8.BH.10',
      dana8ed:      '42.9.1.1',
      crystal_system: 'Monoclinic',
      hardness_min: 5.5,
      hardness_max: 5.5,
      specific_gravity_min: 2.94,
      specific_gravity_max: 2.99,
      cleavage:    'Good on {010}, fair on {110}',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Chartreuse yellow-green to pale yellow — the colour of fresh spring growth; a clean, bright, acid-free yellow-green unique among phosphate gemstones',
      streak:      'White',
      fluorescence: 'None',
      ri_min:      1.602,
      ri_max:      1.621,
      birefringence: 0.019,
      optical_type: 'B',
      shortdesc:   'Brazilianite — NaAl₃(PO₄)₂(OH)₄, rare sodium aluminium phosphate. Named for Brazil (type locality: Conselheiro Pena, Minas Gerais). IMA 1945. One of the few phosphate minerals used as a faceted gemstone. Vivid chartreuse yellow-green colour.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-790.html',
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Brazilianite',
      refractive_index: { n_alpha: 1.602, n_beta: 1.609, n_gamma: 1.621 },
      birefringence:   0.019,
      optical_sign:    '+',
      dispersion:      '0.014',
      pleochroism:     'Weak: colourless / pale yellow / pale yellow-green',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 550, max: 580 },
      spectra: ['R060518'],
    },

    color: {
      primary_color:          'Chartreuse yellow-green — vivid, clean, spring-growth yellow-green',
      color_variants:         [
        'Classic chartreuse yellow-green (most typical)',
        'Pale lemon yellow (lower colour saturation)',
        'Deeper yellow-green approaching peridot territory',
        'Near-colourless (rare, heavily included specimens)',
      ],
      dominant_wavelength_nm: 565,
      oklch:   { l: 0.78, c: 0.18, h: 115 },
      hex:     '#c8d93a',
      munsell: '5GY 8/8',
      color_temperature_k:    null,
      psychological_effects:  [
        'The chartreuse yellow-green sits at the precise intersection of yellow (intellect, clarity) and green (growth, heart) — a colour of synthesised intelligence',
        'The brightness and clarity of gem-quality crystals creates an immediate sensation of mental sharpness and fresh perspective',
        'Rarity awareness — knowing this colour exists almost nowhere else in the mineral kingdom creates heightened attention and appreciation',
        'The spring-leaf colour is one of the most biophilic in the mineral world — the colour of new growth after winter',
        'Faceted brazilianite has extraordinary brilliance for a soft phosphate — the light play creates genuine delight',
      ],
      harmonics: {
        complementary_hue: 295,
        triadic_hues:      [235, 355],
        analogous_range:   [95, 135],
      },
    },

    metaphysical: {
      mineral_name:     'Brazilianite',
      chakra_primary:   'Solar Plexus',
      chakra_secondary: ['Heart', 'Crown'],
      element:   ['Fire', 'Air'],
      planet:    ['Sun', 'Mercury'],
      archetype: ['The Solar Mind', 'The Bright Intellect', 'The Spring Force'],
      zodiac:    ['Leo', 'Gemini', 'Aries'],
      numerology: 1,
      angel_number: 111,
      intention: 'My mind is a clear lens through which the light of pure intelligence shines. I am the first thought of spring.',
      traditions: [
        'Brazilian origin — Conselheiro Pena and Linópolis (Divino das Laranjeiras), Minas Gerais, Brazil; also New Hampshire, USA (minor)',
        'IMA 1945 — described by Frederick H. Pough and Edward P. Henderson from Brazilian specimens sent to the American Museum of Natural History',
        'Named after Brazil — unusually direct geographic naming for a mineral (most are named after persons)',
        'Modern Western crystal healing — yellow-green stones used for Solar Plexus and Heart chakra integration',
      ],
      properties: [
        'IMA-recognised 1945 — formula NaAl₃(PO₄)₂(OH)₄; sodium aluminium phosphate hydroxide',
        'Named for Brazil — primary locality is Conselheiro Pena pegmatite district, Minas Gerais; one of the few minerals named for a country rather than a person',
        'Discovered during WWII when Brazilian minerals were being systematically catalogued for strategic resources — originally mistaken for chrysoberyl or tourmaline',
        'One of the very few phosphate minerals used as a faceted gemstone — most phosphates are too soft or poorly crystallised',
        'H5.5 — softer than most gemstones; protect from scratching; use only in pendants/earrings rather than rings',
        'Monoclinic crystals — elongated prismatic habit; sometimes in groups of parallel crystals forming dramatic clusters',
        'Good cleavage on {010} — faceting requires care; collectors\' specimens should be handled gently',
        'Safe for water — no toxic elements; clean with mild soap and water only',
      ],
      gaia_resonance: 'QuantumNexus + SovereignCore',
      safety_warning: 'H5.5 — soft for a gemstone; protect from harder minerals. Good cleavage — avoid impact. Safe for water. Keep away from ultrasonic cleaners. Store separately from harder stones.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. BRONZITE
  // Enstatite variety with schiller effect — (Mg,Fe)SiO₃
  // Named for its bronze-like metallic schiller
  // The "armour stone" of crystal healing tradition
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Bronzite',
    mindat_id:   797,
    rruff_ids:   ['R040137'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Black Tourmaline',

    physical: {
      id:           797,
      longid:       'bronzite',
      guid:         '',
      name:         'Bronzite (ferroan enstatite variety — schiller enstatite)',
      ima_formula:  '(Mg,Fe)SiO₃',
      mindat_formula: '(Mg,Fe)SiO3',
      ima_status:   'A',
      ima_year:     1807,
      strunzten:    '9.DA.10',
      dana8ed:      '65.1.1.2',
      crystal_system: 'Orthorhombic',
      hardness_min: 5,
      hardness_max: 6,
      specific_gravity_min: 3.20,
      specific_gravity_max: 3.40,
      cleavage:    'Good on {210}, poor on {100}',
      fracture:    'Uneven to conchoidal',
      tenacity:    'Brittle',
      luster:      ['Sub-metallic', 'Metallic (schiller)', 'Pearly on cleavage'],
      diaphaneity: ['Opaque', 'Subtranslucent'],
      colour:      'Bronze-brown to dark brown with distinctive golden-bronze metallic sheen (schiller/aventurescence) caused by oriented hematite/goethite inclusions — like polished antique armour',
      streak:      'Greyish white to pale brown',
      fluorescence: 'None',
      ri_min:      1.665,
      ri_max:      1.688,
      birefringence: 0.011,
      optical_type: 'B',
      shortdesc:   'Bronzite — (Mg,Fe)SiO₃, ferroan enstatite variety. The golden-bronze metallic schiller is caused by oriented iron oxide (hematite/goethite) inclusions. A common mineral in igneous and metamorphic rocks and in iron meteorites. Named for its bronze-like appearance.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-797.html',
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Bronzite (Enstatite variety)',
      refractive_index: { n_alpha: 1.665, n_beta: 1.672, n_gamma: 1.688 },
      birefringence:   0.011,
      optical_sign:    '+',
      dispersion:      '0.010',
      pleochroism:     'Weak: pale yellow-brown / pale green-brown / brown',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 580, max: 620 },
      spectra: ['R040137'],
    },

    color: {
      primary_color:          'Bronze-brown with golden metallic schiller — the colour of antique armour',
      color_variants:         [
        'Classic golden-bronze schiller on warm brown matrix (most common)',
        'Deep reddish-brown with coppery schiller',
        'Olive-brown with subtle silver-bronze schiller',
        'Dark chocolate-brown, high iron content, strong schiller',
        'Pale greyish-brown (low iron, less schiller)',
      ],
      dominant_wavelength_nm: 595,
      oklch:   { l: 0.38, c: 0.07, h: 65 },
      hex:     '#7a5c2e',
      munsell: '5YR 4/4',
      color_temperature_k:    null,
      psychological_effects:  [
        'The metallic schiller creates a visual depth that draws the eye inward — the stone appears to contain its own light source',
        'The warm bronze-brown palette is one of the most grounding colour combinations in the mineral kingdom — earthy, stable, ancient',
        'The armour-like appearance has been consistently associated with protection across cultures that encountered it independently',
        'The weight (SG 3.2–3.4) and density communicate solidity and reliability in the hand',
        'The contrast between opaque matrix and flashing metallic schiller teaches the lesson of hidden brilliance',
      ],
      harmonics: {
        complementary_hue: 245,
        triadic_hues:      [185, 305],
        analogous_range:   [45, 85],
      },
    },

    metaphysical: {
      mineral_name:     'Bronzite',
      chakra_primary:   'Root',
      chakra_secondary: ['Sacral', 'Solar Plexus'],
      element:   ['Earth', 'Fire'],
      planet:    ['Mars', 'Saturn'],
      archetype: ['The Armoured Knight', 'The Protector', 'The Discerning Shield'],
      zodiac:    ['Leo', 'Scorpio', 'Aries'],
      numerology: 1,
      angel_number: 111,
      intention: 'I am armoured by my own integrity. What is not mine cannot enter; what is mine cannot be taken.',
      traditions: [
        'European mineralogy — named by A.G. Werner in 1807 for its bronze-like schiller effect',
        'Found in iron meteorites (including the famous Steinbach meteorite, Germany) — connects the stone to extraterrestrial origins',
        'Western crystal healing — "the courtesy stone" (returns negative energy with courtesy and clarity) and protection stone',
        'Roman and Norse tradition — the schiller effect visually resembles burnished bronze armour; warriors prized such stones as amulets',
        'Found in peridotite, dunite, and gabbro intrusions worldwide; also in chondrite and achondrite meteorites',
      ],
      properties: [
        'IMA-recognised 1807 — formula (Mg,Fe)SiO₃; an iron-bearing enstatite variety (the name "bronzite" is still widely used in the trade though technically an enstatite sub-variety)',
        'Schiller effect caused by oriented platelets of hematite and/or goethite within the enstatite matrix — thin-film and scattering effects produce the metallic bronze flash',
        'Occurs in ultramafic igneous rocks (peridotite, pyroxenite, harzburgite) and in iron-nickel meteorites — one of the few minerals found in both terrestrial and extraterrestrial settings',
        'Found in meteorites — the Steinbach meteorite (Germany), various pallasites and H-chondrites contain bronzite xenoliths',
        'H5–6 — moderate hardness; suitable for tumbled stones, spheres, carvings, and pendants; less ideal for rings',
        'India (Orissa), Austria (Styria), Norway, South Africa, Brazil, USA (Pennsylvania) — widely distributed',
        'Safe for water — no toxic elements; clean with warm soapy water',
        'Yin pair with Black Tourmaline: bronzite deflects/returns, tourmaline absorbs/transmutes — complementary protection modalities',
      ],
      gaia_resonance: 'AnchorPrism + SovereignCore',
      safety_warning: 'Safe for water. H5–6 — moderate hardness; keep away from harder minerals in storage. The schiller can be scratched off on cleavage surfaces — store and handle with care. No toxic elements.',
    },
  },

];

export default BATCH_B7;

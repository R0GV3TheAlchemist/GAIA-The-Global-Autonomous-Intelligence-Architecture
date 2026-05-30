/**
 * src/crystals/db/batch-b7.data.ts
 * GAIA-OS Crystal Database — Batch B-7
 *
 * Entries:
 *   1. Boji Stones (Kansas Pop Rocks)      — trademarked pyrite/marcasite concretions
 *   2. Bornite (Peacock Ore)               — Cu₅FeS₄, iridescent copper sulphide
 *   3. Botallackite                        — rare secondary copper hydroxychloride
 *   4. Botswana Agate                      — banded agate, Kaollong Formation, Botswana
 *   5. Brandberg Amethyst                  — phantom quartz from Brandberg massif, Namibia
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-29
 *
 * NOTE: A batch of extraordinary geographic and mineralogical range.
 * Boji Stones and Bornite carry over from the B-6 list as confirmed entries.
 * Botallackite is one of the rarest secondary copper minerals — named after
 * the historic Botallack Mine in Cornwall, England. Botswana Agate is
 * arguably the finest banded agate in the world — its parallel banding and
 * warm palette are unmatched. Brandberg Amethyst from Namibia is one of the
 * most metaphysically revered quartzes on Earth — the combination of amethyst,
 * smoky quartz, and phantom inclusions in a single crystal from a single
 * sacred locality (Brandberg Mountain) makes it irreplaceable.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_B7: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. BOJI STONES (KANSAS POP ROCKS)
  // Pyrite/marcasite concretions — Smoky Hill Chalk, Niobrara Formation, Kansas
  // LEGALLY TRADEMARKED — important consumer disclosure
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Boji Stones',
    mindat_id:   3314,
    rruff_ids:   ['R050209'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Shungite',

    physical: {
      id:           3314,
      longid:       'boji-stones',
      guid:         '',
      name:         'Pyrite / Marcasite concretion ("Boji Stones" — trademarked; Kansas Pop Rocks)',
      ima_formula:  'FeS₂',
      mindat_formula: 'FeS2',
      ima_status:   'A',
      ima_year:     1845,
      strunzten:    '2.EB.05a',
      dana8ed:      '2.12.1.1',
      crystal_system: 'Cubic (pyrite) / Orthorhombic (marcasite)',
      hardness_min: 6,
      hardness_max: 6.5,
      specific_gravity_min: 4.90,
      specific_gravity_max: 5.20,
      cleavage:    'Indistinct on {100} (pyrite); poor on {110} (marcasite)',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Metallic', 'Sub-metallic'],
      diaphaneity: ['Opaque'],
      colour:      'Pale brass-yellow to dark brown-grey — smooth ("female") and rough/protuberance-covered ("male") forms',
      streak:      'Black to dark brown',
      fluorescence: 'None',
      ri_min:      null,
      ri_max:      null,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Boji Stones — LEGALLY TRADEMARKED name for pyrite/marcasite-dominant concretions from the Smoky Hill Chalk Member, Niobrara Formation, Kansas, USA. Sold as smooth ("female") and rough/spiky ("male") pairs. Generic term: "Kansas Pop Rocks" or septarian concretion.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-3314.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:     'Boji Stones (Pyrite/Marcasite concretion)',
      refractive_index: null,
      birefringence:    null,
      optical_sign:     null,
      dispersion:       null,
      pleochroism:      null,
      fluorescence_lw:  'None',
      fluorescence_sw:  'None',
      phosphorescence:  null,
      visible_wavelength_nm: null,
      spectra: ['R050209'],
    },

    color: {
      primary_color:          'Pale brass to dark brown-grey — metallic, earthy, ancient',
      color_variants:         [
        'Smooth pale brass-tan ("female" — smooth surface)',
        'Rough dark grey-brown with crystalline protuberances ("male" — spiky surface)',
        'Partially oxidised with iridescent tarnish',
        'Dark metallic with visible golden pyrite crystal faces',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.35, c: 0.05, h: 70 },
      hex:     '#6b5e3a',
      munsell: '2.5Y 4/2',
      color_temperature_k:    null,
      psychological_effects:  [
        'The weight-to-size ratio (SG 4.9–5.2) creates immediate surprise — far heavier than expected for a palm stone',
        'The smooth/rough pair dynamic creates a tangible sense of complementarity — two opposites, one unified system',
        'The metallic, ancient appearance suggests deep geological time and alchemical transformation',
        'Holding both simultaneously, one in each hand, creates a grounding bilateral circuit',
        'The unpolished, raw surface communicates authenticity — this stone makes no attempt at prettiness',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Boji Stones',
      chakra_primary:   'Root',
      chakra_secondary: ['Earth Star', 'Sacral', 'Solar Plexus'],
      element:   ['Earth', 'Storm', 'Fire'],
      planet:    ['Saturn', 'Mars', 'Earth'],
      archetype: ['The Alchemical Pair', 'The Ancient Earth', 'The Balancer of Opposites'],
      zodiac:    ['Scorpio', 'Aquarius', 'Taurus'],
      numerology: 2,
      angel_number: 222,
      intention: 'I balance the masculine and feminine within me. I am anchored to the Earth\'s deepest wisdom.',
      traditions: [
        'Modern Western crystal healing — the paired male/female stone system is the core of Boji Stone tradition',
        'Kansas, USA origin — Smoky Hill Chalk Member, Niobrara Formation; Late Cretaceous (~87 Ma)',
        '"Boji Stone" trademarked in the 1980s by Karen Gillespie; generic equivalents: "Kansas Pop Rocks", "Shaman Stones"',
      ],
      properties: [
        '⚠️ LEGALLY TRADEMARKED — "Boji Stone" is a registered trademark; authentic specimens come from one Kansas locality',
        'Composed primarily of pyrite and/or marcasite formed as concretions in Late Cretaceous chalk',
        'Sold in smooth ("female") / rough ("male") pairs — rough surface features are pyrite crystal clusters',
        'Exceptionally heavy for size — SG 4.9–5.2; the weight is the first lesson',
        'Supply is finite — the formation is protected and eroding specimens are collected under permit',
        'Do NOT use in water — pyrite + water produces sulphuric acid (pyrite disease)',
      ],
      gaia_resonance: 'AnchoredRoot + SovereignCore',
      safety_warning: '⚠️ DO NOT USE IN WATER — pyrite/marcasite oxidise in water producing sulphuric acid. Damages the stone and produces a toxic acid solution. Keep dry. No elixirs. Metallic/conductive — keep from electronics.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. BORNITE (PEACOCK ORE)
  // Copper iron sulphide Cu₅FeS₄ — thin-film interference peacock tarnish
  // Named after Ignaz von Born (1742–1791) — alchemical cauda pavonis
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Bornite',
    mindat_id:   762,
    rruff_ids:   ['R060018'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Chalcopyrite',

    physical: {
      id:           762,
      longid:       'bornite',
      guid:         '',
      name:         'Bornite',
      ima_formula:  'Cu₅FeS₄',
      mindat_formula: 'Cu5FeS4',
      ima_status:   'A',
      ima_year:     1845,
      strunzten:    '2.BA.15',
      dana8ed:      '2.9.1.1',
      crystal_system: 'Orthorhombic (low-T) / Cubic (high-T)',
      hardness_min: 3,
      hardness_max: 3,
      specific_gravity_min: 4.90,
      specific_gravity_max: 5.30,
      cleavage:    'Poor on {111}',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Metallic'],
      diaphaneity: ['Opaque'],
      colour:      'Fresh: copper-red to bronze. Tarnished: vivid iridescent purple/blue/red/green/yellow ("peacock") from thin-film interference',
      streak:      'Greyish black',
      fluorescence: 'None',
      ri_min:      null,
      ri_max:      null,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Bornite — Cu₅FeS₄, copper iron sulphide. Important copper ore. Named after Ignaz von Born (1742–1791). Iridescent peacock tarnish via thin-film interference. ⚠️ Acid-treated chalcopyrite is widely mislabelled as Bornite / Peacock Ore.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-762.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Bornite',
      refractive_index: null,
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     'Weak in polished section (anisotropic, low-T orthorhombic form)',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R060018'],
    },

    color: {
      primary_color:          'Iridescent peacock — purple, blue, red, green, yellow over bronze-copper base',
      color_variants:         [
        'Full peacock iridescence — all spectral colours in the tarnish film',
        'Fresh copper-red / bronze (unoxidised, freshly broken surface)',
        'Purple-dominant tarnish (most common)',
        'Blue-green dominant tarnish',
        'Garish uniform artificial iridescence (acid-treated chalcopyrite fraud)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.35, c: 0.20, h: 310 },
      hex:     '#7a4b8a',
      munsell: '5P 4/6',
      color_temperature_k:    null,
      psychological_effects:  [
        'One of the most visually spectacular effects in the mineral kingdom — a single stone contains the entire visible spectrum',
        'Shifting colours at different viewing angles create infinite depth and a sense of living transformation',
        'The contrast between humble copper-bronze base and spectacular tarnish is the fundamental alchemical teaching',
        'Peacock symbolism — the full display of the authentic self — resonates across Hindu, Greek, and Western traditions',
        'Knowing the rainbow is physics without pigment (thin-film interference) deepens rather than diminishes the wonder',
      ],
      harmonics: {
        complementary_hue: 130,
        triadic_hues:      [70, 190],
        analogous_range:   [290, 330],
      },
    },

    metaphysical: {
      mineral_name:     'Bornite',
      chakra_primary:   'Solar Plexus',
      chakra_secondary: ['Sacral', 'Crown', 'All chakras (full-spectrum iridescence)'],
      element:   ['Fire', 'Earth', 'Storm'],
      planet:    ['Venus', 'Sun', 'Uranus'],
      archetype: ['The Peacock', 'The Alchemist', 'The Full Spectrum Self'],
      zodiac:    ['Cancer', 'Leo', 'Taurus'],
      numerology: 8,
      angel_number: 888,
      intention: 'I display the full spectrum of my authentic self without apology or diminishment.',
      traditions: [
        'Western crystal healing — Peacock Ore as joy, happiness, and authentic self-display',
        'Named after Ignaz von Born (1742–1791), Austrian mineralogist and Freemason',
        'Copper = Venus principle across Egyptian, Roman, Greek, and Ayurvedic traditions',
        'Alchemy — cauda pavonis (peacock\'s tail) marks the critical iridescent stage of the Great Work between nigredo and albedo',
      ],
      properties: [
        'IMA-recognised 1845 — formula Cu₅FeS₄',
        'Iridescent tarnish = thin-film interference; copper sulphate/carbonate layers of varying thickness produce structural colour',
        '⚠️ FRAUD ALERT: acid-treated chalcopyrite (CuFeS₂) widely sold as Peacock Ore / Bornite — the fake has more garish, uniform colour; natural bornite tarnish is subtler and graduated',
        'Alchemical cauda pavonis — rainbow iridescence signals transition between nigredo (blackening) and albedo (whitening)',
        'Soft H3, heavy SG 4.9–5.3 — scratches easily; store separately',
        'Copper sulphide — TOXIC in elixirs; DO NOT use in water',
      ],
      gaia_resonance: 'QuantumNexus + SovereignCore + ViriditasHeart',
      safety_warning: '⚠️ TOXIC — copper iron sulphide. DO NOT use in water elixirs or gem water. Copper compounds toxic if ingested. Avoid prolonged skin contact with wet specimens. Metallic/conductive — keep from electronics. H3 — scratches easily.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. BOTALLACKITE
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
        'Collectors\'  note: botallackite is metastable and may slowly convert to atacamite or clinoatacamite over time; keep dry and stable',
        'Soft (H3) — handle gently; do not tumble. Copper content — TOXIC in elixirs.',
      ],
      gaia_resonance: 'ClarusLens + ViriditasHeart',
      safety_warning: '⚠️ TOXIC — copper hydroxychloride. DO NOT use in water elixirs, gem water, or any ingestible preparation. Copper compounds are toxic if ingested. Do NOT use in direct drinking water contact. Keep dry (metastable — may convert to atacamite). H3 — fragile; handle with care.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. BOTSWANA AGATE
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
        'The warm peachy-pink palette is one of the most universally soothing colour combinations in the mineral kingdom — simultaneously stimulating and calming',
        'The precision of the parallel banding — millimetre-perfect concentric rings — creates a profound sense of natural order and the reliability of pattern',
        'Each band represents a discrete silica deposition event — time made visible in a way that invites reflection on patience and incremental growth',
        'The translucency with backlight creates an inner glow that makes the stone feel like it is lit from within',
        'The warm, maternal palette psychologically registers as safe, nourishing, and stabilising — the opposite of threatening',
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
        'The name references both the stone type (agate) and the country of origin (Botswana) — one of the clearest geographic crystal names',
      ],
      properties: [
        'Trade name: "Botswana Agate" — specific to banded chalcedony nodules from the Kaollong Formation, Botswana, southern Africa',
        'Botswana is the world\'s primary source of premium banded agate — the formation yields nodules up to 30cm+ in diameter with exceptional banding regularity',
        'Banding forms by periodic silica gel deposition in vugs (cavities) in basalt — each band = one deposition event; banding reflects changes in silica concentration, trace elements, and fluid chemistry over geological time',
        'The warm pink/apricot palette comes from trace iron oxides (haematite, goethite) distributed differentially between bands',
        'Some bands fluoresce pale green or white under LW UV — useful for identifying natural specimens vs. dyed material',
        'H6.5–7, tough, conchoidal fracture — one of the most durable crystals for everyday use and jewellery',
        'Piezoelectric as all quartz-group minerals — keep away from hard drives and sensitive electronics',
        'Botswana is the October birthstone zodiac stone for Scorpio in many modern traditions',
        'Yin pair with Blue Lace Agate: warm/cool, earth/sky, grounding/elevating — the two most beloved agates in crystal healing',
      ],
      gaia_resonance: 'AnchoredRoot + ViriditasHeart',
      safety_warning: '⚠️ PIEZOELECTRIC — keep away from hard drives and sensitive electronics. Safe for water. Durable for everyday use. Dyed specimens exist in the market — natural Botswana Agate has warm, subtle tones; dyed material has unnaturally vivid pinks, purples, or blues.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. BRANDBERG AMETHYST
  // Phantom quartz from Brandberg Mountain, Namibia
  // The single most metaphysically revered quartz locality on Earth
  // Amethyst + smoky + phantom inclusions + enhydros — all in one crystal
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
      colour:      'Complex: zones of amethyst purple, smoky grey-brown, clear/colourless, often with phantoms (earlier growth stages visible as ghost crystals within), enhydros (water inclusions), and lepidocrocite (red/orange inclusions). No two are identical.',
      streak:      'White',
      fluorescence: 'None to very weak blue-white under LW UV',
      ri_min:      1.544,
      ri_max:      1.553,
      birefringence: 0.009,
      optical_type: 'U',
      shortdesc:   'Brandberg Amethyst — quartz from Brandberg Mountain (Königstein), Erongo Region, Namibia. Combines amethyst (Fe³⁺ colour centres), smoky quartz (irradiation colour centres), phantoms, enhydros, and other inclusions in a single crystal. The most complex and revered quartz locality on Earth. Each crystal is unique.',
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
        'Clear with multiple phantom layers (successive growth stages)',
        'Amethyst with red/orange lepidocrocite inclusions (rare, highly prized)',
        'Enhydro — water bubble trapped in a cavity visible through the crystal',
        'Window crystal — flat faces on the side of the prism showing interior phantom structure',
        'Fully clear with deep phantom interior (subtle but profound)',
      ],
      dominant_wavelength_nm: 405,
      oklch:   { l: 0.48, c: 0.14, h: 315 },
      hex:     '#8b5fa8',
      munsell: '5P 5/6',
      color_temperature_k:    null,
      psychological_effects:  [
        'The phantom layers — ghost crystals within the crystal — create a layered, archaeological sense of time and personal history',
        'The combination of amethyst purple and smoky grey in a single crystal produces an integrated sense of spiritual clarity and grounded wisdom simultaneously',
        'The knowledge that each crystal is unique to a single mountain in Namibia creates profound specificity — this is not a generic crystal, it is from HERE',
        'Enhydros (ancient water inclusions) invoke the most primal connection to the water of deep geological time — the primordial ocean',
        'The Brandberg Mountain itself is Africa\'s largest intrusive granite massif, home to the world\'s most ancient rock paintings — the crystal carries that cultural weight',
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
        'The Brandberg is a UNESCO World Heritage Site candidate and home to over 50,000 ancient rock paintings including the famous "White Lady" painting (~2000 years old)',
        'San (Bushmen) tradition — the Brandberg is a sacred mountain (Dâures in Damara/Nama language); the crystals are considered to carry the mountain\'s consciousness',
        'Modern Western crystal healing — Brandberg Amethyst is widely regarded as the highest-vibration quartz on Earth by the crystal healing community',
        'Piezoelectric tradition — all quartz crystals share the physical property of generating voltage under pressure; the Brandberg variety is valued for its complexity of layers',
      ],
      properties: [
        'Trade name: "Brandberg Amethyst" — specific to quartz from Brandberg Mountain (Königstein), Erongo Region, Namibia',
        'The combination of multiple quartz varieties in a single crystal is the defining characteristic: amethyst (Fe³⁺ colour centres) + smoky quartz (irradiation-created colour centres) + phantom layers (earlier growth stages) + enhydros (ancient water inclusions) + optional lepidocrocite (FeO(OH)) inclusions',
        'Phantoms form when crystal growth pauses, a different mineral coats the crystal face, then quartz growth resumes — encapsulating the earlier form as a "ghost" visible within',
        'Enhydros are genuine ancient water inclusions — some may be millions of years old — visible as a moving bubble within a cavity',
        'Lepidocrocite inclusions give some specimens orange/red internal colouring — these are the most prized and expensive Brandberg specimens',
        'Brandberg Mountain is Africa\'s largest intrusive granite massif (2573m / 8442ft) — the magmatic complexity of the intrusion created the extraordinarily varied mineralogy of the quartz deposits',
        'No two Brandberg crystals are identical — the variation of phantom, colour zone, inclusion type, and habit is effectively infinite',
        'Piezoelectric — all quartz; keep away from hard drives and sensitive electronics',
        'H7, tough, conchoidal fracture — durable for meditation and display; handle terminations with care',
      ],
      gaia_resonance: 'QuantumNexus + ClarusLens + AnchoredRoot + Noosphere + ViriditasHeart + SovereignCore',
      safety_warning: '⚠️ PIEZOELECTRIC — keep away from hard drives and sensitive electronics. Safe for water. H7 — durable but protect terminations. Phantom layers may create unexpected emotional resonance in sensitive practitioners — approach with grounded intention. Enhydros: do not subject to rapid temperature changes.',
    },
  },

];

export default BATCH_B7;

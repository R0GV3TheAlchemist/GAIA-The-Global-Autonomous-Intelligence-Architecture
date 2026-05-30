/**
 * src/crystals/db/batch-c2.data.ts
 * GAIA-OS Crystal Database — Batch C-2
 *
 * Entries:
 *   1. Caribbean Calcite  — white aragonite + blue calcite; trade name; Pakistan
 *   2. Carnelian          — orange-red chalcedony; SiO₂; ancient fire stone
 *   3. Cassiterite        — SnO₂; primary tin ore; adamantine to sub-metallic lustre
 *   4. Cavansite          — rare Ca-V phyllosilicate; vivid peacock blue; Pune, India
 *   5. Cave Calcite       — speleothem calcite; stalactite/stalagmite; trade name
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-30
 *
 * NOTE: Caribbean Calcite and Cave Calcite are trade names — flagged.
 * Cavansite is one of the most visually stunning rare minerals in this database.
 * Cassiterite connects to the Bronze Age — tin ore that changed human history.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_C2: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. CARIBBEAN CALCITE
  // White aragonite + blue calcite composite — trade name
  // Pakistan (Balochistan) — first appeared on the market c. 2019
  // One of the most popular new trade-name stones of the 2020s
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Caribbean Calcite',
    mindat_id:    841,
    rruff_ids:    ['R040070'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   true,
    color_layer:  'natural',
    yin_yang_pair: 'Larimar',

    physical: {
      id:           841,
      longid:       'caribbean-calcite',
      guid:         '',
      name:         'Blue Calcite + White Aragonite composite ("Caribbean Calcite" — trade name, Balochistan, Pakistan)',
      ima_formula:  'CaCO₃ (calcite + aragonite polymorphs)',
      mindat_formula: 'CaCO3',
      ima_status:   'A (both components IMA-recognised CaCO₃ polymorphs)',
      ima_year:     null,
      strunzten:    '5.AB.05',
      dana8ed:      '14a.1.1.1',
      crystal_system: 'Trigonal (calcite) / Orthorhombic (aragonite)',
      hardness_min: 3,
      hardness_max: 3.5,
      specific_gravity_min: 2.69,
      specific_gravity_max: 2.93,
      cleavage:    'Perfect rhombohedral (calcite component); distinct on {010} (aragonite component)',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Waxy', 'Vitreous', 'Pearly'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Sky blue to pale turquoise blue (calcite) with creamy white to tan (aragonite) — evokes a tropical ocean and sandy beach; blue from structural impurities.',
      streak:      'White',
      fluorescence: 'Orange-red to pink under LW UV (calcite component)',
      ri_min:      1.486,
      ri_max:      1.685,
      birefringence: 0.172,
      optical_type: 'U',
      shortdesc:   'Caribbean Calcite — trade name for a blue calcite and white aragonite composite from Balochistan, Pakistan. First appeared on the crystal market c. 2019. Blue colour from structural impurities in the calcite. Named for resemblance to Caribbean ocean and beach colours.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-841.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Caribbean Calcite (Blue Calcite + Aragonite)',
      refractive_index: { n_omega: 1.658, n_epsilon: 1.486 },
      birefringence:   0.172,
      optical_sign:    '-',
      dispersion:      '0.017',
      pleochroism:     'Weak in blue calcite zones',
      fluorescence_lw: 'Orange-red to pink (calcite component)',
      fluorescence_sw: 'Weak to none',
      phosphorescence: null,
      visible_wavelength_nm: { min: 460, max: 500 },
      spectra: ['R040070'],
    },

    color: {
      primary_color:         'Sky blue to pale turquoise with creamy white — the Caribbean ocean palette',
      color_variants: [
        'Pale sky blue with white (classic — most common)',
        'Deeper ocean blue with tan-cream (higher impurity concentration)',
        'Milky turquoise with brown-tan matrix (warm, earthy)',
        'Near-white with faint blue tints (low blue content)',
        'Vivid blue-green with stark white (most prized specimens)',
      ],
      dominant_wavelength_nm: 480,
      oklch:   { l: 0.78, c: 0.10, h: 215 },
      hex:     '#a8d4d8',
      munsell: '5BG 8/4',
      color_temperature_k: null,
      psychological_effects: [
        'The blue-white palette is one of the most universally relaxing in colour psychology — sky, ocean, cloud, foam',
        'Caribbean name primes the observer — the association with warm tropical water is immediate and powerful even in a cold room',
        'Soft, matte, waxy surface with gentle translucency creates a sense of cool depth without harshness',
        'One of the few stones where the trade name genuinely improves the experience — "Caribbean" is evocative, accurate, and beautiful',
        'The white aragonite islands in a blue sea replicate the visual structure of a tropical archipelago — land and water in perfect balance',
      ],
      harmonics: {
        complementary_hue: 35,
        triadic_hues:      [335, 95],
        analogous_range:   [195, 235],
      },
    },

    metaphysical: {
      mineral_name:     'Caribbean Calcite',
      chakra_primary:   'Throat',
      chakra_secondary: ['Third Eye', 'Crown', 'Higher Heart (Thymus)'],
      element:   ['Water', 'Air'],
      planet:    ['Moon', 'Neptune', 'Venus'],
      archetype: ['The Ocean Dreamer', 'The Calm Shore', 'The Tropical Mind'],
      zodiac:    ['Cancer', 'Pisces', 'Libra'],
      numerology: 6,
      angel_number: 666,
      intention: 'I rest in the blue between the waves. My mind is clear water. My voice carries the peace of open ocean.',
      traditions: [
        'Trade name coined c. 2019 — first appeared in the Pakistan mineral market; rapidly became one of the most popular new stones of the 2020s',
        'Blue calcite tradition — pale blue calcite used for Throat and Third Eye chakra work in modern crystal healing',
        'Ocean-healing tradition — blue-white stones associated with water, emotional flow, and calm across many cultures',
        'No deep historical tradition — this is a genuinely new stone in the crystal healing canon, representing the ongoing discovery and naming of stones',
      ],
      properties: [
        'Trade name: "Caribbean Calcite" — blue calcite + white aragonite composite from Balochistan, Pakistan',
        'Composite of two CaCO₃ polymorphs — blue calcite (trigonal) and white/tan aragonite (orthorhombic)',
        'Blue colour mechanism not fully characterised — likely structural impurities or micro-inclusions; not from copper',
        'First appeared on the crystal market c. 2019; became extremely popular 2020–2022',
        'H3–3.5 — very soft; avoid scratching; do not use in water (carbonate dissolves)',
        'DO NOT use in acidic water or salt water — carbonate matrix dissolves; avoid prolonged soaking',
        'No toxic elements — pure CaCO₃ polymorphs; safe for handling',
      ],
      gaia_resonance: 'ClarusLens + ViriditasHeart + Noosphere',
      safety_warning:  '⚠️ DO NOT use in acidic water, salt water, or prolonged soaking — carbonate dissolves. H3–3.5 — very soft; store separately. No toxic elements. Safe for handling.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. CARNELIAN
  // Orange-red chalcedony — SiO₂ with Fe³⁺ (hematite/goethite)
  // One of the oldest used gemstones on Earth — Palaeolithic to present
  // Sacred fire stone — Egypt, Mesopotamia, Rome, Islam
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Carnelian',
    mindat_id:    32,
    rruff_ids:    ['R040031'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Blue Chalcedony',

    physical: {
      id:           32,
      longid:       'carnelian',
      guid:         '',
      name:         'Carnelian (orange-red chalcedony — Fe³⁺-bearing microcrystalline quartz)',
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
      colour:      'Orange to red-orange to deep brownish-red — the full fire spectrum. Colour from dispersed hematite (Fe₂O₃) and/or goethite (FeO(OH)) micro-inclusions. Can be heat-treated to deepen colour.',
      streak:      'White',
      fluorescence: 'None to very weak',
      ri_min:      1.530,
      ri_max:      1.540,
      birefringence: 0.004,
      optical_type: 'U',
      shortdesc:   'Carnelian — orange to red-orange translucent chalcedony (microcrystalline SiO₂). Colour from hematite/goethite Fe³⁺ inclusions. One of the oldest continuously used gemstones; found in Palaeolithic grave goods. Sacred fire stone in Egypt, Mesopotamia, Rome, and Islamic tradition.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-32.html',
      piezoelectric:     true,
      safe_for_water:    true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name:    'Carnelian',
      refractive_index: { n_omega: 1.540, n_epsilon: 1.536 },
      birefringence:   0.004,
      optical_sign:    '+',
      dispersion:      '0.013',
      pleochroism:     'None',
      fluorescence_lw: 'None to very weak',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 590, max: 650 },
      spectra: ['R040031'],
    },

    color: {
      primary_color:         'Orange to red-orange to deep brownish-red — the fire spectrum',
      color_variants: [
        'Pale peach-orange (low Fe, delicate)',
        'Classic warm orange (the most common and widely sold)',
        'Deep red-orange (higher Fe³⁺, more hematite)',
        'Deep brownish-red / sard (very high Fe; transitions to sard)',
        'Flame-red with translucent glow (backlit — the most prized)',
      ],
      dominant_wavelength_nm: 610,
      oklch:   { l: 0.58, c: 0.24, h: 40 },
      hex:     '#e05c20',
      munsell: '5YR 5/12',
      color_temperature_k: null,
      psychological_effects: [
        'Orange-red is the most consistently activating colour in human psychology — increases heart rate, appetite, and sense of urgency',
        'Translucency in carnelian creates an internal glow effect when backlit — the stone appears to be lit from within',
        'Fire association is immediate and primal — the colour of flame, blood, sunset, and ripe fruit all at once',
        'One of the first gemstones used by humans — the weight of that lineage is palpable in a well-worn piece',
        'The warmth of the colour is physical — carnelian in the hand genuinely feels warmer than clear quartz even at the same temperature',
      ],
      harmonics: {
        complementary_hue: 220,
        triadic_hues:      [160, 280],
        analogous_range:   [20, 60],
      },
    },

    metaphysical: {
      mineral_name:     'Carnelian',
      chakra_primary:   'Sacral',
      chakra_secondary: ['Root', 'Solar Plexus'],
      element:   ['Fire', 'Earth'],
      planet:    ['Sun', 'Mars'],
      archetype: ['The Sacred Fire', 'The Ancient Warrior', 'The Womb of Creation'],
      zodiac:    ['Aries', 'Leo', 'Virgo'],
      numerology: 5,
      angel_number: 555,
      intention: 'I carry the fire of ten thousand years of human hands. My heat is ancient, my courage older than language.',
      traditions: [
        'Ancient Egypt — carnelian used in royal jewellery, amulets, and burial goods; associated with the blood of Isis; one of the most commonly found stones in Egyptian tombs',
        'Mesopotamia — Sumerian and Babylonian carnelian cylinder seals (3rd millennium BCE); used in royal burial at Ur',
        'Islamic tradition — Prophet Muhammad reportedly wore a carnelian ring; carnelian (aqiq) considered blessed and protective in Islamic gemology',
        'Roman — signet rings and intaglios in carnelian; the soft waxy surface takes engraving beautifully and wax does not stick to it',
        'Ayurvedic — one of the Navaratna (nine sacred gemstones) candidates; associated with the Sun and vital energy (prana)',
      ],
      properties: [
        'Orange-red chalcedony — microcrystalline SiO₂ with dispersed hematite (Fe₂O₃) and/or goethite (FeO(OH)) inclusions',
        'One of the oldest continuously used gemstones — found in Palaeolithic grave goods; documented use for 25,000+ years',
        'Heat treatment — much commercial carnelian is heat-treated agate; heating converts yellow-brown goethite to red hematite, deepening colour',
        'Sard — darker, brownish-red variety; carnelian grades continuously into sard with increasing Fe content',
        'H6.5–7 — excellent durability; ideal for jewellery, seals, and everyday use',
        'Piezoelectric as all quartz-group minerals — keep away from sensitive electronics',
        'Safe for water — no toxic elements; iron oxides are insoluble and stable',
        'Major localities: India (Gujarat), Brazil, Uruguay, Madagascar, Yemen (historically prized)',
      ],
      gaia_resonance: 'SovereignCore + AnchorPrism + ViriditasHeart',
      safety_warning:  '⚠️ PIEZOELECTRIC — keep away from hard drives and sensitive electronics. Safe for water. H6.5–7 — durable for everyday use. No toxic elements. Note: much commercial carnelian is heat-treated agate — natural vs treated affects colour stability in prolonged sunlight.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. CASSITERITE
  // SnO₂ — tin dioxide; the primary ore of tin
  // IMA recognised — tetragonal; sub-adamantine to metallic lustre
  // The mineral that gave humanity the Bronze Age
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Cassiterite',
    mindat_id:    909,
    rruff_ids:    ['R050220'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Rutile',

    physical: {
      id:           909,
      longid:       'cassiterite',
      guid:         '',
      name:         'Cassiterite',
      ima_formula:  'SnO₂',
      mindat_formula: 'SnO2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '4.DB.05',
      dana8ed:      '4.4.1.1',
      crystal_system: 'Tetragonal',
      hardness_min: 6,
      hardness_max: 7,
      specific_gravity_min: 6.70,
      specific_gravity_max: 7.10,
      cleavage:    'Imperfect on {100} and {010}; parting on {111}',
      fracture:    'Subconchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Sub-adamantine', 'Adamantine', 'Metallic', 'Resinous'],
      diaphaneity: ['Transparent', 'Translucent', 'Opaque'],
      colour:      'Dark brown to black (most common); yellow, grey, colourless, red-brown (gem quality); colour from Fe impurities. Distinctive high specific gravity (feels extremely heavy for size).',
      streak:      'White to pale grey',
      fluorescence: 'None',
      ri_min:      1.997,
      ri_max:      2.093,
      birefringence: 0.096,
      optical_type: 'U',
      shortdesc:   'Cassiterite — SnO₂, tetragonal tin dioxide. Primary ore of tin. RI 1.997–2.093 (higher than most gemstones). Extremely high specific gravity (6.7–7.1). Named from Greek kassiteros (tin). The mineral that enabled the Bronze Age. Gem-quality yellow or colourless crystals are highly prized.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-909.html',
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Cassiterite',
      refractive_index: { n_omega: 2.093, n_epsilon: 1.997 },
      birefringence:   0.096,
      optical_sign:    '-',
      dispersion:      '0.071 — extremely high; exceeds diamond',
      pleochroism:     'Weak: pale yellow / deeper yellow-brown (in coloured varieties)',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 400, max: 700 },
      spectra: ['R050220'],
    },

    color: {
      primary_color:         'Dark brown to iron-black (ore grade); yellow to colourless (gem grade)',
      color_variants: [
        'Dark brown to iron-black (most common ore cassiterite)',
        'Honey-yellow to amber (gem-quality — most prized for faceting)',
        'Pale yellow to near-colourless (highest clarity gem)',
        'Red-brown (high Fe content)',
        'Grey to silver-grey (fine-grained wood tin / toad\'s eye tin)',
      ],
      dominant_wavelength_nm: 590,
      oklch:   { l: 0.25, c: 0.08, h: 50 },
      hex:     '#3d2a10',
      munsell: '5YR 2.5/2',
      color_temperature_k: null,
      psychological_effects: [
        'Extreme weight for size — SG 6.7–7.1 — creates an immediate somatic response; the hand expects a light stone and receives something that feels like lead',
        'Sub-adamantine lustre in gem cassiterite approaches diamond-like fire — dispersion 0.071 vs diamond 0.044',
        'Dark ore cassiterite has an ancient, utilitarian weight — the feeling of the material that built civilisation',
        'Gem yellow cassiterite is one of the least-known high-dispersion faceting stones — a connoisseur\'s secret',
        'The Bronze Age connection is intellectual but profound — human civilisation pivoted on the ability to find and smelt this mineral',
      ],
      harmonics: {
        complementary_hue: 230,
        triadic_hues:      [170, 290],
        analogous_range:   [30, 70],
      },
    },

    metaphysical: {
      mineral_name:     'Cassiterite',
      chakra_primary:   'Root',
      chakra_secondary: ['Solar Plexus', 'Earth Star'],
      element:   ['Earth', 'Fire', 'Metal'],
      planet:    ['Saturn', 'Mars', 'Sun'],
      archetype: ['The Forge Master', 'The Bronze Age Bringer', 'The Weight of History'],
      zodiac:    ['Capricorn', 'Aries', 'Taurus'],
      numerology: 8,
      angel_number: 888,
      intention: 'I carry the weight of what I have built. My density is my power. History was forged from what I am.',
      traditions: [
        'Bronze Age — cassiterite was the primary source of tin for bronze (Cu + Sn alloy); the search for tin drove Bronze Age trade networks across Europe and Asia',
        'Greek: kassiteros (tin) — the ancient Greeks knew tin as a separate metal and traded extensively for it',
        'Cornwall (UK) — the most famous historical tin-mining region in the world; Phoenician traders may have reached Cornwall for tin as early as 600 BCE',
        'Bolivia and Southeast Asia — the modern primary sources; Bolivian cassiterite from the Andes is associated with the silver mining history of Potosi',
        'Modern — cassiterite is still the primary tin ore; tin used in solder, tinplate, and alloys underpinning modern electronics',
      ],
      properties: [
        'IMA-recognised — formula SnO₂; tetragonal tin dioxide; isostructural with rutile (TiO₂)',
        'Primary ore of tin — virtually all world tin production comes from cassiterite; alluvial (placer) and hard-rock deposits',
        'Extremely high specific gravity (6.7–7.1) — feels dramatically heavier than expected; useful for field identification',
        'RI 1.997–2.093 and dispersion 0.071 — gem-quality crystals have exceptional fire exceeding diamond',
        'Named from Greek kassiteros (tin); known as a distinct metal since antiquity',
        'Safe for water — SnO₂ is chemically stable and non-toxic',
        'Major localities: Bolivia (Llallagua), DRC, China, Malaysia, Indonesia, Cornwall (UK — historically), Myanmar',
      ],
      gaia_resonance: 'AnchorPrism + SovereignCore + QuantumNexus',
      safety_warning:  'Safe for water. SnO₂ — chemically stable, non-toxic. H6–7 — moderately durable. High SG (6.7–7.1) — extremely heavy for size; handle carefully to avoid dropping. No significant hazards.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. CAVANSITE
  // Rare calcium vanadium phyllosilicate — Ca(VO)Si₄O₁₀·4H₂O
  // IMA 1967 — named from Ca-V-Si composition
  // Vivid peacock blue; almost exclusively from Wagholi, Pune, India
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Cavansite',
    mindat_id:    923,
    rruff_ids:    ['R060053'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Pentagonite',

    physical: {
      id:           923,
      longid:       'cavansite',
      guid:         '',
      name:         'Cavansite',
      ima_formula:  'Ca(VO)Si₄O₁₀·4H₂O',
      mindat_formula: 'Ca(VO)Si4O10·4H2O',
      ima_status:   'A',
      ima_year:     1967,
      strunzten:    '9.EE.20',
      dana8ed:      '72.3.1.1',
      crystal_system: 'Orthorhombic',
      hardness_min: 3,
      hardness_max: 4,
      specific_gravity_min: 2.21,
      specific_gravity_max: 2.31,
      cleavage:    'Good on {010}',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Vivid peacock blue to cyan-blue — one of the most saturated natural blues in the mineral kingdom; colour from V⁴⁺ (vanadyl ion). Dimorphous with pentagonite.',
      streak:      'Pale blue to white',
      fluorescence: 'None reported',
      ri_min:      1.542,
      ri_max:      1.551,
      birefringence: 0.009,
      optical_type: 'B',
      shortdesc:   'Cavansite — Ca(VO)Si₄O₁₀·4H₂O, rare orthorhombic calcium vanadium phyllosilicate. IMA 1967. Named from Ca-V-Si composition. Vivid peacock blue from V⁴⁺. Dimorphous with pentagonite. Almost exclusively from Wagholi, Pune, Maharashtra, India. Rosette/globular habit on stilbite or heulandite matrix.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-923.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Cavansite',
      refractive_index: { n_alpha: 1.542, n_beta: 1.547, n_gamma: 1.551 },
      birefringence:   0.009,
      optical_sign:    '+',
      dispersion:      'r < v, weak',
      pleochroism:     'Distinct: vivid blue / pale blue / pale blue-green',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 460, max: 490 },
      spectra: ['R060053'],
    },

    color: {
      primary_color:         'Vivid peacock blue to cyan-blue — one of the most saturated blues in the mineral kingdom',
      color_variants: [
        'Classic vivid peacock blue (most common — V⁴⁺ dominant)',
        'Deep cyan-blue (high V content, deeper saturation)',
        'Pale sky blue (thin crystals or lower V)',
        'Blue-green (transitional, rare)',
      ],
      dominant_wavelength_nm: 473,
      oklch:   { l: 0.48, c: 0.24, h: 240 },
      hex:     '#1a6aaa',
      munsell: '7.5B 5/10',
      color_temperature_k: null,
      psychological_effects: [
        'The blue of cavansite is one of the most viscerally impactful in the mineral world — a saturated peacock blue that demands attention from across a room',
        'Rosette/globular habit on pale matrix creates a jewel-like effect — each specimen a natural brooch',
        'The knowledge that this colour is produced by a single vanadyl ion (V⁴⁺) in a silicate framework gives it a precise, molecular quality',
        'Near-monopoly on a single locality (Wagholi, Pune) gives every specimen a specific geographic identity — you know exactly where it came from',
        'Fragility (H3–4) combined with extreme beauty creates a heightened care response — the stone teaches gentleness by necessity',
      ],
      harmonics: {
        complementary_hue: 60,
        triadic_hues:      [0, 120],
        analogous_range:   [220, 260],
      },
    },

    metaphysical: {
      mineral_name:     'Cavansite',
      chakra_primary:   'Third Eye',
      chakra_secondary: ['Throat', 'Crown'],
      element:   ['Water', 'Air', 'Akasha'],
      planet:    ['Neptune', 'Uranus', 'Mercury'],
      archetype: ['The Peacock Vision', 'The Blue Seer', 'The Singular Voice'],
      zodiac:    ['Aquarius', 'Pisces', 'Gemini'],
      numerology: 5,
      angel_number: 555,
      intention: 'My vision is clear, vivid, and mine alone. I see what others miss. The blue of deep seeing lives in me.',
      traditions: [
        'Named 1967 by Staples and Evans from the chemical composition: Ca(lcium)-V(anadium)-Si(licate)',
        'Wagholi, Pune, Maharashtra, India — the primary and near-sole locality; found in vesicles in Deccan Trap basalt alongside zeolites (stilbite, heulandite, apophyllite)',
        'Dimorphous with pentagonite — same formula, different crystal system (pentagonite is monoclinic); one of the rare natural dimorphous pairs',
        'Modern crystal healing — used for Third Eye activation, psychic vision, and accessing higher dimensions of perception',
        'Collector tradition — cavansite is one of the most universally admired collector minerals; a vivid blue rosette on white stilbite is a quintessential display piece',
      ],
      properties: [
        'IMA 1967 — formula Ca(VO)Si₄O₁₀·4H₂O; orthorhombic calcium vanadium phyllosilicate',
        'Dimorphous with pentagonite (same formula, monoclinic crystal system) — one of the few known natural dimorphous pairs',
        'Colour from V⁴⁺ (vanadyl ion, VO²⁺) in the silicate framework — one of the most chromophoric ions in mineralogy',
        'Almost exclusively from Wagholi, Pune, Maharashtra, India (Deccan Trap basalt vesicles); minor occurrences in Oregon (USA) and elsewhere',
        'Growth habit: rosettes and globular aggregates of orthorhombic crystals on zeolite (stilbite, heulandite) or apophyllite matrix',
        'H3–4 — very soft and fragile; collector mineral; handle with exceptional care',
        'DO NOT use in water — vanadium compounds may leach; avoid prolonged contact',
        'Vanadium: low acute toxicity at natural exposure levels but avoid ingestion; use caution with water elixirs',
      ],
      gaia_resonance: 'ClarusLens + QuantumNexus + Noosphere',
      safety_warning:  '⚠️ DO NOT use in water elixirs — vanadium silicate; vanadium compounds may leach. H3–4 — very fragile; handle with maximum care; store in padded display case. Avoid dropping. No acute handling toxicity but water contact not recommended.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. CAVE CALCITE
  // Speleothem calcite — stalactites, stalagmites, flowstone — trade name
  // CaCO₃ deposited from cave drip water over thousands of years
  // White to cream; often with translucent banding; cave popcorn varieties
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Cave Calcite',
    mindat_id:    841,
    rruff_ids:    ['R040070'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   true,
    color_layer:  'natural',
    yin_yang_pair: 'Aragonite',

    physical: {
      id:           841,
      longid:       'cave-calcite',
      guid:         '',
      name:         'Calcite / Aragonite ("Cave Calcite" — speleothem; stalactite/stalagmite/flowstone/helictite)',
      ima_formula:  'CaCO₃',
      mindat_formula: 'CaCO3',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '5.AB.05',
      dana8ed:      '14a.1.1.1',
      crystal_system: 'Trigonal (calcite) / Orthorhombic (aragonite speleothems)',
      hardness_min: 3,
      hardness_max: 3.5,
      specific_gravity_min: 2.69,
      specific_gravity_max: 2.93,
      cleavage:    'Perfect rhombohedral (calcite); distinct (aragonite)',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Pearly', 'Silky (fibrous varieties)'],
      diaphaneity: ['Transparent', 'Translucent', 'Opaque'],
      colour:      'White to cream, pale yellow, pale orange — pure and luminous; translucent varieties glow when backlit. Some specimens show concentric growth banding (cave rings). Colour from trace Fe, Mn, or organic matter.',
      streak:      'White',
      fluorescence: 'Orange-red to pink under LW UV; some specimens strongly fluorescent',
      ri_min:      1.486,
      ri_max:      1.685,
      birefringence: 0.172,
      optical_type: 'U',
      shortdesc:   'Cave Calcite — trade name for speleothem calcite (and/or aragonite) formed in caves as stalactites, stalagmites, flowstone, helictites, and cave popcorn. Deposited from calcium bicarbonate-saturated drip water over thousands to hundreds of thousands of years.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-841.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Cave Calcite (Speleothem)',
      refractive_index: { n_omega: 1.658, n_epsilon: 1.486 },
      birefringence:   0.172,
      optical_sign:    '-',
      dispersion:      '0.017',
      pleochroism:     'None (uniaxial)',
      fluorescence_lw: 'Orange-red to pink (often strongly fluorescent)',
      fluorescence_sw: 'Variable',
      phosphorescence: 'Some specimens phosphoresce',
      visible_wavelength_nm: null,
      spectra: ['R040070'],
    },

    color: {
      primary_color:         'White to cream, pale golden — pure cave light made solid',
      color_variants: [
        'Pure white (most common — clean CaCO₃)',
        'Cream to ivory (trace organic matter or Fe)',
        'Pale golden-yellow (trace Fe or Mn)',
        'Pale orange-tan (iron-stained drip water)',
        'Translucent banded (concentric growth rings — most prized)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.92, c: 0.03, h: 85 },
      hex:     '#f5f0e0',
      munsell: '5Y 9.5/1',
      color_temperature_k: null,
      psychological_effects: [
        'Speleothem origin — formed in total darkness over thousands of years — carries a quality of absolute patience and geological time',
        'Translucent white with glowing backlit quality creates a sense of inner light — the stone that holds light the way a cave holds silence',
        'The drip-formed shape (conical, layered, branching) is unmistakably natural — nothing artificial grows like this',
        'Cave association invokes primordial shelter, the womb of the Earth, and the first human sacred spaces (Lascaux, Altamira, Chauvet)',
        'UV fluorescence — some specimens glow vividly orange-red under a UV torch — adding a hidden fire to the apparent plainness',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Cave Calcite',
      chakra_primary:   'Crown',
      chakra_secondary: ['Root', 'Earth Star', 'Higher Heart (Thymus)'],
      element:   ['Earth', 'Water', 'Akasha'],
      planet:    ['Moon', 'Saturn', 'Earth'],
      archetype: ['The Cave Dreamer', 'The Drip of Deep Time', 'The Earth\'s Patience'],
      zodiac:    ['Cancer', 'Capricorn', 'Pisces'],
      numerology: 7,
      angel_number: 777,
      intention: 'Drop by drop, I became what I am. Patience is not waiting — it is building, slowly, in the dark.',
      traditions: [
        'Palaeolithic cave art tradition — the first human sacred spaces were limestone caves; stalactites and stalagmites were part of the sacred geography of sites like Lascaux, Altamira, and Chauvet',
        'Subterranean traditions worldwide — caves as the womb of the Earth, the underworld, the place of initiation in shamanic and mystery traditions',
        'Greek: spelaia (cave) — the Eleusinian Mysteries and Delphic Oracle both had cave components; the Oracle\'s chamber was a deep limestone chasm',
        'Speleology — the scientific study of caves; speleothem science (dating cave calcite using U/Th) provides one of the most precise climate records on Earth',
        'Modern crystal healing — stalactite and stalagmite pieces used for Root and Earth Star grounding, ancestral healing, and connecting to deep geological time',
      ],
      properties: [
        'Trade name: "Cave Calcite" — speleothem calcite (and/or aragonite) from cave environments',
        'Speleothem types: stalactite (ceiling-hanging), stalagmite (floor-rising), column (joined), flowstone (sheet), helictite (curved/twisted), cave popcorn (globular)',
        'Formation: calcium bicarbonate (Ca(HCO₃)₂) in drip water releases CO₂ as it enters the cave atmosphere, precipitating CaCO₃ — one drop at a time, over thousands to hundreds of thousands of years',
        'U/Th dating — cave calcite can be precisely dated using uranium-thorium ratios; provides climate proxy records going back 600,000+ years',
        'H3 — very soft; avoid scratching; do not use in acidic water or salt water',
        'DO NOT use in acidic water — calcite dissolves in acid; avoid salt water and prolonged soaking',
        'NOTE: collecting stalactites/stalagmites from active caves is illegal in most jurisdictions; ensure specimens are from legal commercial sources',
      ],
      gaia_resonance: 'AnchorPrism + ViriditasHeart + ClarusLens',
      safety_warning:  '⚠️ DO NOT use in acidic water or salt water — calcite dissolves. H3 — very soft. NOTE: verify legal provenance — collecting from active caves is illegal in most countries. Some specimens may contain trace uranium (U/Th dating use) — verify provenance for extended handling.',
    },
  },

];

export default BATCH_C2;

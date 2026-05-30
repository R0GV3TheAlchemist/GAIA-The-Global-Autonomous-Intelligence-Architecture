/**
 * src/crystals/db/batch-c1.data.ts
 * GAIA-OS Crystal Database — Batch C-1
 *
 * Entries:
 *   1. Bustamite          — rare Mn-Ca inosilicate; deferred from B-8
 *   2. Cacoxenite         — iron aluminium phosphate in quartz; Stone of Ascension
 *   3. Calcite            — CaCO₃; master amplifier; all colour varieties
 *   4. Callaghanite       — rare Cu₂Mg₂ carbonate hydroxide; vivid blue
 *   5. Calligraphy Stone  — fossil marl/coquina; trade name; Arabic script patterns
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-30
 *
 * NOTE: Bustamite was deferred from B-8 as the natural bridge stone into
 * the C-series. Callaghanite is one of the rarest minerals in this database.
 * Calligraphy Stone is a trade name — flagged accordingly.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_C1: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. BUSTAMITE
  // Rare manganese calcium inosilicate — CaMn(Si₂O₆) series
  // Named after General Anastasio Bustamante (1780–1853), President of Mexico
  // IMA 1827 — classic localities: Franklin NJ and Broken Hill NSW
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Bustamite',
    mindat_id:    870,
    rruff_ids:    ['R060849'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Rhodonite',

    physical: {
      id:           870,
      longid:       'bustamite',
      guid:         '',
      name:         'Bustamite',
      ima_formula:  'CaMn²⁺(Si₂O₆)',
      mindat_formula: 'CaMn(Si2O6)',
      ima_status:   'A',
      ima_year:     1827,
      strunzten:    '9.DA.15',
      dana8ed:      '65.1.2.1',
      crystal_system: 'Triclinic',
      hardness_min: 5.5,
      hardness_max: 6.5,
      specific_gravity_min: 3.26,
      specific_gravity_max: 3.43,
      cleavage:    'Perfect on {110}, good on {110}',
      fracture:    'Uneven to conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Silky (fibrous varieties)'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Pale rose-pink to deep brownish-pink, flesh-pink, pale beige-pink — softer and warmer than rhodonite; colour from Mn²⁺',
      streak:      'White',
      fluorescence: 'Orange to salmon-pink under LW UV (Franklin specimens especially vivid)',
      ri_min:      1.664,
      ri_max:      1.709,
      birefringence: 0.014,
      optical_type: 'B',
      shortdesc:   'Bustamite — CaMn(Si₂O₆), triclinic manganese calcium inosilicate. Named after General Anastasio Bustamante. IMA 1827. Pale rose-pink to brownish-pink; softer hue than rhodonite. Classic localities: Franklin (NJ, USA) and Broken Hill (NSW, Australia). Fluoresces orange-salmon under LW UV.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-870.html',
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Bustamite',
      refractive_index: { n_alpha: 1.664, n_beta: 1.690, n_gamma: 1.709 },
      birefringence:   0.014,
      optical_sign:    '+',
      dispersion:      'r > v, weak',
      pleochroism:     'Weak: pale pink / pale brownish-pink / pale rose',
      fluorescence_lw: 'Orange to salmon-pink (especially Franklin, NJ specimens)',
      fluorescence_sw: 'Weak to none',
      phosphorescence: null,
      visible_wavelength_nm: { min: 580, max: 640 },
      spectra: ['R060849'],
    },

    color: {
      primary_color:         'Pale rose-pink to warm brownish-pink — softer and more muted than rhodonite',
      color_variants: [
        'Pale flesh-pink (most common — gentle, warm, skin-tone adjacent)',
        'Deeper brownish-rose (higher Mn content)',
        'Pale beige-pink with white calcite matrix (Franklin specimens)',
        'Salmon-pink with orange fluorescence (UV-active Franklin material)',
        'Near-white with faint pink blush (Ca-dominant end member)',
      ],
      dominant_wavelength_nm: 610,
      oklch:   { l: 0.70, c: 0.08, h: 15 },
      hex:     '#d4a0a0',
      munsell: '5R 7/4',
      color_temperature_k: null,
      psychological_effects: [
        'Softer and less saturated than rhodonite — where rhodonite commands attention, bustamite invites quiet intimacy',
        'Flesh-pink palette is one of the most skin-adjacent in the mineral kingdom — immediately bodily, warm, and human',
        'The fluorescence revelation — turning orange under UV — adds a hidden depth to an apparently simple stone',
        'Franklin NJ provenance connects to the most famous fluorescent mineral locality on Earth — a lineage of hidden light',
        'Pale brownish-pink is the colour of old roses, weathered terracotta, and the inside of a held hand',
      ],
      harmonics: {
        complementary_hue: 195,
        triadic_hues:      [135, 255],
        analogous_range:   [355, 35],
      },
    },

    metaphysical: {
      mineral_name:     'Bustamite',
      chakra_primary:   'Heart',
      chakra_secondary: ['Root', 'Higher Heart (Thymus)'],
      element:   ['Earth', 'Water'],
      planet:    ['Venus', 'Moon'],
      archetype: ['The Quiet Heart', 'The Gentle Witness', 'The Rose of Remembrance'],
      zodiac:    ['Taurus', 'Cancer', 'Libra'],
      numerology: 4,
      angel_number: 444,
      intention: 'I hold love gently, without demand. My heart is a quiet room where all are welcome.',
      traditions: [
        'Named after General Anastasio Bustamante (1780–1853), three-time President of Mexico and patron of mineralogy',
        'Franklin, NJ — part of the world-famous Franklin-Sterling Hill fluorescent mineral complex; Mn-silicate family includes rhodonite, bustamite, and franklinite',
        'Broken Hill, NSW, Australia — major Pb-Zn-Ag orebody with remarkable associated mineral diversity including bustamite',
        'Modern crystal healing — soft pink manganese silicates used for Heart chakra work, grief processing, and gentle self-love',
      ],
      properties: [
        'IMA 1827 — formula CaMn(Si₂O₆); triclinic inosilicate (pyroxenoid group)',
        'Part of the wollastonite-bustamite-rhodonite series — all Mn/Ca inosilicates with varying Mn:Ca ratios',
        'Distinguished from rhodonite by higher Ca content and softer pink colour; rhodonite is deeper rose with black manganese oxide veining',
        'Vivid orange-salmon fluorescence under LW UV (especially Franklin, NJ specimens) — one of the more surprising fluorescent responses in the mineral kingdom',
        'Classic localities: Franklin and Sterling Hill, NJ (USA); Broken Hill (NSW, Australia); Långban (Sweden); Harstig Mine (Sweden)',
        'H5.5–6.5 — durable enough for display and meditation; protect from harder minerals in storage',
        'Safe for water — silicate mineral; no toxic components. Franklin NJ specimens: verify provenance for potential uranium association.',
      ],
      gaia_resonance: 'ViriditasHeart + ClarusLens',
      safety_warning:  'Safe for water. H5.5–6.5 — moderate hardness; store away from harder minerals. No toxic elements. Franklin NJ specimens may be mildly radioactive if associated with uranium-bearing minerals — verify provenance.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. CACOXENITE
  // Iron aluminium phosphate — Fe²⁴³⁺Al(OH)₁₂(PO₄)₁₇·17H₂O
  // Named from Greek: kakos (bad) + xenos (stranger) — impurity in iron ore
  // Now revered as the Stone of Ascension — one of the Super Seven minerals
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Cacoxenite',
    mindat_id:    875,
    rruff_ids:    ['R060221'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Goethite',

    physical: {
      id:           875,
      longid:       'cacoxenite',
      guid:         '',
      name:         'Cacoxenite',
      ima_formula:  'Fe²⁴³⁺Al(OH)₁₂(PO₄)₁₇·17H₂O',
      mindat_formula: 'Fe24Al(OH)12(PO4)17·17H2O',
      ima_status:   'A',
      ima_year:     1825,
      strunzten:    '8.DC.20',
      dana8ed:      '40.4.1.1',
      crystal_system: 'Hexagonal',
      hardness_min: 3,
      hardness_max: 3.5,
      specific_gravity_min: 2.20,
      specific_gravity_max: 2.40,
      cleavage:    'Good on {0001}',
      fracture:    'Uneven',
      tenacity:    'Brittle',
      luster:      ['Silky', 'Adamantine (on crystal faces)', 'Pearly'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Deep golden-yellow to orange-yellow, amber, brownish-yellow — rich, saturated, sun-like. Hexagonal acicular crystals with silky lustre. Colour from Fe³⁺.',
      streak:      'Pale yellow',
      fluorescence: 'None reported',
      ri_min:      1.575,
      ri_max:      1.658,
      birefringence: 0.083,
      optical_type: 'U',
      shortdesc:   'Cacoxenite — Fe₂₄Al(OH)₁₂(PO₄)₁₇·17H₂O, hexagonal iron aluminium phosphate. Named from Greek for "bad stranger" — originally considered an impurity in iron ore. One of the Super Seven minerals. Golden-yellow acicular crystals with silky adamantine lustre.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-875.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Cacoxenite',
      refractive_index: { n_omega: 1.658, n_epsilon: 1.575 },
      birefringence:   0.083,
      optical_sign:    '-',
      dispersion:      'Strong',
      pleochroism:     'Distinct: deep golden-yellow / pale yellow',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 560, max: 610 },
      spectra: ['R060221'],
    },

    color: {
      primary_color:         'Deep golden-yellow to rich amber-orange — radiant sun-gold',
      color_variants: [
        'Rich golden-yellow (classic — most prized inclusion colour in quartz)',
        'Deep amber-orange (higher Fe³⁺ concentration)',
        'Pale straw-yellow (thinner inclusions, lighter colour)',
        'Brownish-gold (oxidised surface)',
        'Burnished copper-gold in thick masses',
      ],
      dominant_wavelength_nm: 585,
      oklch:   { l: 0.65, c: 0.22, h: 75 },
      hex:     '#d4900a',
      munsell: '7.5YR 6/10',
      color_temperature_k: null,
      psychological_effects: [
        'Golden acicular spray patterns within quartz create a visual impression of captured sunlight or frozen aurora',
        'The silky adamantine lustre gives individual needles an almost supernatural brilliance — each fibre its own light source',
        'The narrative inversion — from "bad stranger" (its name) to "Stone of Ascension" — teaches the lesson of misidentified value',
        'In Super Seven matrix, cacoxenite adds the golden thread of solar intelligence to a violet-purple ground',
        'The radial sunburst growth habit is one of the most optically joyful patterns in the mineral kingdom',
      ],
      harmonics: {
        complementary_hue: 255,
        triadic_hues:      [195, 315],
        analogous_range:   [55, 95],
      },
    },

    metaphysical: {
      mineral_name:     'Cacoxenite',
      chakra_primary:   'Crown',
      chakra_secondary: ['Solar Plexus', 'Third Eye', 'Soul Star'],
      element:   ['Fire', 'Akasha'],
      planet:    ['Sun', 'Jupiter'],
      archetype: ['The Ascended Stranger', 'The Solar Thread', 'The Misidentified Gift'],
      zodiac:    ['Sagittarius', 'Pisces', 'Aries'],
      numerology: 9,
      angel_number: 999,
      intention: 'What was called an impurity is my greatest gift. I rise through what others overlooked.',
      traditions: [
        'Named 1825 by Wilhelm Karl von Haidinger — from Greek kakos (bad) + xenos (stranger) because it lowered iron ore quality',
        'Super Seven (Melody Stone) — cacoxenite is one of the seven minerals in the famous Super Seven quartz from Espirito Santo, Brazil (amethyst, smoky quartz, clear quartz, rutile, goethite, lepidocrocite, cacoxenite)',
        'Modern crystal healing — the "Stone of Ascension"; used for raising collective and personal consciousness',
        'Found as golden inclusions in amethyst from Brazil, France (Haut-Vienne), and Scotland; as standalone crystals in limonite-phosphate matrix',
      ],
      properties: [
        'IMA 1825 — formula Fe₂₄Al(OH)₁₂(PO₄)₁₇·17H₂O; hexagonal; highly hydrated iron aluminium phosphate',
        'One of the seven minerals in Super Seven quartz from Espirito Santo, Brazil — the golden needle inclusions are cacoxenite',
        'Originally named "bad stranger" because it contaminated iron ore — now one of the most sought-after mineral inclusions',
        'Forms as golden acicular radiating sprays in quartz, limonite, and phosphate-rich oxidised zones',
        'H3–3.5 — soft; standalone crystals are fragile; inclusions in quartz are protected by the host',
        'DO NOT use in water — phosphate minerals may dissolve or leach over extended contact',
        'Major localities: Haut-Vienne (France — type locality); Höllgraben (Austria); Hagendorf (Germany); Mono County (CA, USA); Espirito Santo (Brazil)',
      ],
      gaia_resonance: 'QuantumNexus + Noosphere + ClarusLens',
      safety_warning:  '⚠️ DO NOT use in water elixirs — phosphate mineral; may leach over extended contact. H3–3.5 as standalone crystals — extremely fragile; handle inclusions in quartz normally. No acute toxicity but phosphate leaching risk warrants caution.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. CALCITE
  // CaCO₃ — calcium carbonate; one of the most abundant minerals on Earth
  // The master amplifier — occurs in every colour of the spectrum
  // IMA recognised — trigonal; perfect rhombohedral cleavage
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Calcite',
    mindat_id:    841,
    rruff_ids:    ['R040070'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Aragonite',

    physical: {
      id:           841,
      longid:       'calcite',
      guid:         '',
      name:         'Calcite',
      ima_formula:  'CaCO₃',
      mindat_formula: 'CaCO3',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '5.AB.05',
      dana8ed:      '14a.1.1.1',
      crystal_system: 'Trigonal',
      hardness_min: 3,
      hardness_max: 3,
      specific_gravity_min: 2.69,
      specific_gravity_max: 2.71,
      cleavage:    'Perfect rhombohedral on {10-14} — three directions producing perfect rhombohedra',
      fracture:    'Conchoidal (across cleavage)',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Pearly (on cleavage)', 'Waxy'],
      diaphaneity: ['Transparent', 'Translucent', 'Opaque'],
      colour:      'Colourless, white, yellow, orange, red, pink, green, blue, grey, brown, black — virtually every colour; purest form is colourless (Iceland spar). Colour from trace impurities.',
      streak:      'White',
      fluorescence: 'Highly variable — pink, orange, red, blue, white, green under LW and SW UV depending on trace impurities and locality',
      ri_min:      1.486,
      ri_max:      1.658,
      birefringence: 0.172,
      optical_type: 'U',
      shortdesc:   'Calcite — CaCO₃, trigonal calcium carbonate. One of the most abundant minerals on Earth; principal component of limestone, marble, and chalk. Perfect rhombohedral cleavage. Iceland spar (optical calcite) shows extreme double refraction (birefringence 0.172). Occurs in virtually every colour.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-841.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Calcite',
      refractive_index: { n_omega: 1.658, n_epsilon: 1.486 },
      birefringence:   0.172,
      optical_sign:    '-',
      dispersion:      '0.017',
      pleochroism:     'None (uniaxial); colour varieties may show weak absorption',
      fluorescence_lw: 'Highly variable — pink, orange, red, blue, white, green (locality and impurity dependent)',
      fluorescence_sw: 'Variable — often different colour than LW response',
      phosphorescence: 'Some specimens phosphoresce after UV exposure',
      visible_wavelength_nm: null,
      spectra: ['R040070'],
    },

    color: {
      primary_color:         'All colours — the most colour-diverse single mineral species on Earth',
      color_variants: [
        'Colourless / Iceland Spar (optical calcite — dramatic double refraction)',
        'White (chalk, limestone — the most abundant form)',
        'Golden-yellow / Honey Calcite (goethite/limonite inclusions)',
        'Orange Calcite (Fe³⁺ + Mn)',
        'Red / Strawberry Calcite (hematite inclusions)',
        'Green Calcite (chlorite or celadonite inclusions)',
        'Blue Calcite (rare — structural colour or Cu²⁺)',
        'Pink / Mangano Calcite (Mn²⁺)',
        'Black Calcite (bituminous/carbonaceous inclusions)',
        'Caribbean Calcite (white + blue — C-2)',
        'Cobalto Calcite (vivid pink-rose — Co²⁺ — C-8)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.90, c: 0.02, h: 90 },
      hex:     '#f5f0e8',
      munsell: 'N 9.5/',
      color_temperature_k: null,
      psychological_effects: [
        'The sheer colour diversity of calcite teaches that identity is not determined by colour — the same formula manifests in every hue',
        'Perfect rhombohedral cleavage creates satisfying, geometrically precise fracture — calcite always breaks into the same shape',
        'Iceland spar double refraction — seeing two images through one stone — is a physical demonstration of dual perception',
        'The softness (H3) makes calcite the most yielding of the common minerals — it teaches that receptivity is a form of strength',
        'Fizzing in HCl — calcite dissolves with vigorous effervescence — makes the chemistry literal and immediate',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Calcite',
      chakra_primary:   'Crown',
      chakra_secondary: ['All chakras — colour-specific varieties govern specific centres'],
      element:   ['Earth', 'Water', 'Fire', 'Air', 'Akasha'],
      planet:    ['Moon', 'Venus', 'Sun'],
      archetype: ['The Amplifier', 'The Universal Mirror', 'The Master of All Colours'],
      zodiac:    ['Cancer', 'Pisces', 'All signs'],
      numerology: 3,
      angel_number: 333,
      intention: 'I amplify what is true. In every colour I remain myself. My clarity multiplies your light.',
      traditions: [
        'Ancient Egypt — alabaster (massive calcite) used for canopic jars, statuary, and luxury vessels; symbol of purity and preservation',
        'Viking sunstone — Iceland spar (optical calcite) used as a navigational aid; polarises skylight to locate the sun through cloud cover',
        'Roman and Greek — limestone (calcite) the primary building stone of classical civilisation; marble (metamorphic calcite) for sculpture',
        'Modern crystal healing — calcite as the universal amplifier; each colour variety corresponds to a specific chakra and intention',
        'Acid test (fizzes in HCl) — the standard field identification test for carbonate minerals; one of the first tests taught in mineralogy',
      ],
      properties: [
        'Formula CaCO₃ — trigonal calcium carbonate; polymorphic with aragonite (orthorhombic) and vaterite (hexagonal)',
        'One of the most abundant minerals on Earth — principal component of limestone, marble, chalk, travertine, stalactites, shells, bones, and coral',
        'Perfect rhombohedral cleavage in three directions — always breaks into perfect rhombohedra regardless of original crystal form',
        'Birefringence 0.172 — among the highest of any common mineral; Iceland spar shows dramatic double image',
        'Viking sunstone — optical calcite polarises skylight, allowing navigation even when the sun is obscured',
        'Reacts vigorously with dilute HCl — the standard carbonate test; bubbles (CO₂) immediately',
        'DO NOT use in water long-term — slowly dissolves in acidic water; avoid salt water and acidic solutions',
        'H3 — scratches easily; keep away from harder minerals in storage',
      ],
      gaia_resonance: 'ClarusLens + ViriditasHeart + AnchorPrism',
      safety_warning:  '⚠️ DO NOT use in acidic water or salt water — calcite dissolves slowly. Safe for brief water contact but avoid prolonged soaking. H3 — very soft; store separately. No toxic elements in pure calcite; coloured varieties with impurities (e.g. Cobalto Calcite, Bumblebee Calcite) have separate safety profiles.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. CALLAGHANITE
  // Rare magnesium copper carbonate hydroxide — Cu₂Mg₂(CO₃)(OH)₆·2H₂O
  // Named after Eugene Callaghan (1899–1963), American mineralogist
  // IMA 1954 — one of the rarest minerals in the crystal healing canon
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Callaghanite',
    mindat_id:    877,
    rruff_ids:    [],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Malachite',

    physical: {
      id:           877,
      longid:       'callaghanite',
      guid:         '',
      name:         'Callaghanite',
      ima_formula:  'Cu₂Mg₂(CO₃)(OH)₆·2H₂O',
      mindat_formula: 'Cu2Mg2(CO3)(OH)6·2H2O',
      ima_status:   'A',
      ima_year:     1954,
      strunzten:    '5.BA.10',
      dana8ed:      '16b.3.1.1',
      crystal_system: 'Monoclinic',
      hardness_min: 2.5,
      hardness_max: 3,
      specific_gravity_min: 2.73,
      specific_gravity_max: 2.78,
      cleavage:    'Perfect on {001}',
      fracture:    'Uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Pearly on cleavage'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Vivid blue to blue-green — a pure, saturated copper blue unique among carbonate hydroxides; colour from Cu²⁺',
      streak:      'Pale blue-green',
      fluorescence: 'None reported',
      ri_min:      1.567,
      ri_max:      1.657,
      birefringence: 0.090,
      optical_type: 'B',
      shortdesc:   'Callaghanite — Cu₂Mg₂(CO₃)(OH)₆·2H₂O, rare monoclinic magnesium copper carbonate hydroxide. Named after Eugene Callaghan. IMA 1954. Type locality: Gabbs magnesite deposit, Nye County, Nevada. Vivid blue from Cu²⁺. One of the rarest minerals in the healing crystal canon.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-877.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Callaghanite',
      refractive_index: { n_alpha: 1.567, n_beta: 1.620, n_gamma: 1.657 },
      birefringence:   0.090,
      optical_sign:    '+',
      dispersion:      'r > v, strong',
      pleochroism:     'Distinct: deep blue / pale blue / blue-green',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 460, max: 490 },
      spectra: [],
    },

    color: {
      primary_color:         'Vivid saturated blue to blue-green — pure copper blue',
      color_variants: [
        'Deep vivid blue (most prized — Cu²⁺ dominant)',
        'Blue-green (approaching Cu carbonate green)',
        'Pale blue (thin crystals or lower Cu content)',
      ],
      dominant_wavelength_nm: 475,
      oklch:   { l: 0.52, c: 0.20, h: 230 },
      hex:     '#2a8aad',
      munsell: '5B 5/8',
      color_temperature_k: null,
      psychological_effects: [
        'One of the rarest minerals in the crystal healing world — the knowledge of extreme rarity transforms the sensory experience entirely',
        'Saturated copper blue sits at the intersection of sky and deep water — simultaneously expansive and immersive',
        'Tiny crystals with intense colour saturation teach the lesson of compressed potency — small but undeniable',
        'The copper lineage (malachite, azurite, chrysocolla, callaghanite) forms a complete blue-green family of heart and throat teachers',
        'Only Nevada as primary locality gives this stone an almost mythic specificity — you hold a fragment of one Nevada hillside',
      ],
      harmonics: {
        complementary_hue: 50,
        triadic_hues:      [350, 110],
        analogous_range:   [210, 250],
      },
    },

    metaphysical: {
      mineral_name:     'Callaghanite',
      chakra_primary:   'Throat',
      chakra_secondary: ['Heart', 'Third Eye'],
      element:   ['Water', 'Air'],
      planet:    ['Venus', 'Neptune'],
      archetype: ['The Rare Voice', 'The Blue Keeper', 'The Copper Mystic'],
      zodiac:    ['Libra', 'Aquarius', 'Taurus'],
      numerology: 7,
      angel_number: 777,
      intention: 'My voice carries the rarest truth. I speak from a place so deep and specific it cannot be duplicated.',
      traditions: [
        'Named after Eugene Callaghan (1899–1963), American economic geologist who described the Gabbs magnesite deposit',
        'Type locality: Gabbs magnesite-brucite deposit, Nye County, Nevada, USA — one of the largest magnesite deposits in North America',
        'Copper carbonate tradition — the family of copper carbonate hydroxide minerals (malachite, azurite, rosasite) used in Heart and Throat chakra work across many traditions',
        'Extremely rare in the crystal healing market — most practitioners have never encountered a specimen',
      ],
      properties: [
        'IMA 1954 — formula Cu₂Mg₂(CO₃)(OH)₆·2H₂O; monoclinic magnesium copper carbonate hydroxide',
        'Type locality: Gabbs magnesite-brucite deposit, Nye County, Nevada, USA — the only significant locality worldwide',
        'Forms as tiny tabular monoclinic crystals on magnesite matrix; individual crystals typically < 1mm',
        'High birefringence (0.090) and strong pleochroism visible in thin sections',
        'Copper content — DO NOT use in water elixirs; copper compounds are toxic',
        'H2.5–3 — extremely soft; collector mineral only; handle with exceptional care',
        'One of the rarest minerals in the crystal healing canon — few commercial specimens exist',
      ],
      gaia_resonance: 'ClarusLens + ViriditasHeart',
      safety_warning:  '⚠️ TOXIC — copper carbonate hydroxide. DO NOT use in water elixirs or gem water. Copper compounds are toxic if ingested. H2.5–3 — extremely fragile; collector mineral only. Rare — handle with maximum care. Keep dry.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. CALLIGRAPHY STONE
  // Coquina / Marl fossil matrix — trade name
  // Arabic/Devanagari script-like patterns from fossilised shell/vegetation
  // Primary locality: Narmada River region, Madhya Pradesh, India
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Calligraphy Stone',
    mindat_id:    null,
    rruff_ids:    [],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   true,
    color_layer:  'natural',
    yin_yang_pair: 'Chinese Writing Stone',

    physical: {
      id:           null,
      longid:       'calligraphy-stone',
      guid:         '',
      name:         'Coquina / Marl ("Calligraphy Stone" — fossilised shell/vegetation matrix, Narmada River, India)',
      ima_formula:  'Not applicable (rock — CaCO₃ matrix with fossil inclusions)',
      mindat_formula: null,
      ima_status:   'Not IMA — trade name for fossil-bearing sedimentary rock',
      ima_year:     null,
      strunzten:    null,
      dana8ed:      null,
      crystal_system: 'Not applicable (sedimentary rock)',
      hardness_min: 3,
      hardness_max: 4,
      specific_gravity_min: 2.60,
      specific_gravity_max: 2.75,
      cleavage:    'None (rock)',
      fracture:    'Uneven',
      tenacity:    'Brittle',
      luster:      ['Dull', 'Waxy (polished surface)'],
      diaphaneity: ['Opaque'],
      colour:      'Cream to beige-brown matrix with dark brown-black script-like patterns — the dark markings are fossilised shells, plant material, or iron oxide staining arranged in flowing calligraphic patterns.',
      streak:      'White to pale grey',
      fluorescence: 'Variable — calcite matrix may show weak UV response',
      ri_min:      null,
      ri_max:      null,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Calligraphy Stone — trade name for coquina/marl fossil-bearing sedimentary rock from the Narmada River region, Madhya Pradesh, India. Dark script-like patterns are fossilised shell fragments, plant material, or iron oxide in a pale calcite-rich matrix. Also called "Arabic Stone" or "Elephant Skin Jasper."',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  null,
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Calligraphy Stone (Fossil Marl)',
      refractive_index: null,
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'Weak variable (calcite matrix)',
      fluorescence_sw: 'None to weak',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: [],
    },

    color: {
      primary_color:         'Cream to warm beige with dark brown-black flowing calligraphic script patterns',
      color_variants: [
        'Classic cream-white matrix with fine black script markings',
        'Warm tan-beige with dark brown flowing patterns',
        'Golden-ochre matrix with heavy black fossil tracery',
        'Grey-cream with fine silver-grey script lines',
        'Rich caramel-brown with dense dark patterning',
      ],
      dominant_wavelength_nm: 590,
      oklch:   { l: 0.82, c: 0.06, h: 75 },
      hex:     '#e8d5b0',
      munsell: '2.5Y 8/4',
      color_temperature_k: null,
      psychological_effects: [
        'The script-like patterns trigger the language centres of the brain — the stone appears to communicate in an unknown tongue',
        'Natural calligraphy invites the question: who wrote this? The Earth as author, time as the pen',
        'Warm cream-and-dark palette is one of the most culturally resonant — ancient papyrus, vellum manuscripts, stone tablets',
        'Each stone carries a unique text — no two are the same — creating a deep sense of individual message and personal meaning',
        'Fossil origin connects to deep time — the patterns were living organisms; the stone is a memorial as much as a mineral',
      ],
      harmonics: {
        complementary_hue: 255,
        triadic_hues:      [195, 315],
        analogous_range:   [55, 95],
      },
    },

    metaphysical: {
      mineral_name:     'Calligraphy Stone',
      chakra_primary:   'Third Eye',
      chakra_secondary: ['Throat', 'Crown', 'Root'],
      element:   ['Earth', 'Akasha'],
      planet:    ['Mercury', 'Saturn'],
      archetype: ['The Earth Writer', 'The Akashic Reader', 'The Stone Scribe'],
      zodiac:    ['Gemini', 'Capricorn', 'Virgo'],
      numerology: 8,
      angel_number: 888,
      intention: 'The Earth has written my name in stone. I read the ancient text within myself and know what has always been true.',
      traditions: [
        'Narmada River tradition — the Narmada (one of India\'s seven sacred rivers) is associated with Shaivite tradition; Shiva lingas are found naturally in the riverbed',
        'Named "Calligraphy Stone" for patterns resembling Arabic, Devanagari, or Chinese script — cross-cultural naming reflects universal script quality',
        'Also known as "Arabic Stone", "Elephant Skin Jasper", "Miriam Stone" (when from Egypt/Israel region), and "Script Stone"',
        'Fossil tradition — the dark patterns are often Crinoid, Gastropod, or plant fossil fragments — connecting to the Palaeozoic ocean that covered central India',
        'Akashic records tradition — stones that appear to carry text are used for accessing past-life memory and the Akashic record',
      ],
      properties: [
        'Trade name: "Calligraphy Stone" — fossil-bearing coquina/marl from the Narmada River valley, Madhya Pradesh, India',
        'Dark patterns: fossilised shell fragments (crinoids, gastropods, bivalves), plant material, or iron oxide precipitation in calcite-rich matrix',
        'Narmada River valley — one of India\'s most geologically significant regions; Cretaceous and Jurassic sediments yield both fossils and Shiva lingas',
        'Calcite-dominant matrix — reacts with HCl; avoid prolonged water contact',
        'H3–4 — relatively soft; suitable for display and meditation; less ideal for everyday jewellery',
        'Each piece is unique — the "script" patterns are never repeated; highly individual stones',
        'Also sold as "Arabic Stone" (Egypt, Israel, Jordan origin) and "Miriam Stone" — different localities, similar appearance',
      ],
      gaia_resonance: 'Noosphere + ClarusLens + AnchorPrism',
      safety_warning:  '⚠️ DO NOT use in acidic water or salt water — calcite matrix dissolves slowly. Safe for brief handling. H3–4 — relatively soft; protect surface. Fossil matrix — some specimens may contain pyrite which can oxidise and stain with prolonged moisture exposure.',
    },
  },

];

export default BATCH_C1;

/**
 * src/crystals/db/batch-c3.data.ts
 * GAIA-OS Crystal Database — Batch C-3
 *
 * Entries:
 *   1. Celestite      — SrSO₄; sky-blue strontium sulphate; IMA recognised
 *   2. Celestobarite  — rare (Sr,Ba)SO₄ sulphate; zoned blue-white; UK/Romania
 *   3. Cerussite      — PbCO₃; lead carbonate; adamantine lustre — TOXIC
 *   4. Chalcanthite   — CuSO₄·5H₂O; vivid blue copper sulphate — HIGHLY TOXIC
 *   5. Chalcedony     — microcrystalline SiO₂; the universal base stone
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-30
 *
 * SAFETY NOTE: Cerussite (lead) and Chalcanthite (copper sulphate) are among
 * the most toxic minerals in this database. Both flagged with full warnings.
 * Chalcanthite is water-soluble — DO NOT use in water under any circumstances.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_C3: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. CELESTITE
  // SrSO₄ — strontium sulphate; orthorhombic
  // Named from Latin caelestis (celestial) for its sky-blue colour
  // IMA recognised — classic localities: Madagascar, Ohio (USA), Sicily
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Celestite',
    mindat_id:    943,
    rruff_ids:    ['R040092'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Barite',

    physical: {
      id:           943,
      longid:       'celestite',
      guid:         '',
      name:         'Celestite',
      ima_formula:  'SrSO₄',
      mindat_formula: 'SrSO4',
      ima_status:   'A',
      ima_year:     1799,
      strunzten:    '7.AD.35',
      dana8ed:      '28.3.1.2',
      crystal_system: 'Orthorhombic',
      hardness_min: 3,
      hardness_max: 3.5,
      specific_gravity_min: 3.95,
      specific_gravity_max: 3.97,
      cleavage:    'Perfect on {010}, good on {001}',
      fracture:    'Uneven to conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Pearly (on cleavage)'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Pale sky-blue to deeper cornflower blue (most prized); also colourless, white, pale yellow, orange, red, green, brown. Blue from lattice defects or trace impurities. Colour fades with prolonged sunlight exposure.',
      streak:      'White',
      fluorescence: 'White to pale blue under LW UV; some specimens strongly fluorescent',
      ri_min:      1.619,
      ri_max:      1.631,
      birefringence: 0.012,
      optical_type: 'B',
      shortdesc:   'Celestite — SrSO₄, orthorhombic strontium sulphate. Named from Latin caelestis for its sky-blue colour. IMA 1799. Pale sky-blue to deeper cornflower blue; colour fades in prolonged sunlight. Classic localities: Sakoany (Madagascar), Put-in-Bay (Ohio, USA), Agrigento (Sicily). Primary strontium ore.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-943.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Celestite',
      refractive_index: { n_alpha: 1.619, n_beta: 1.622, n_gamma: 1.631 },
      birefringence:   0.012,
      optical_sign:    '+',
      dispersion:      'r > v, weak',
      pleochroism:     'None to very weak',
      fluorescence_lw: 'White to pale blue (variable)',
      fluorescence_sw: 'Weak to none',
      phosphorescence: null,
      visible_wavelength_nm: { min: 460, max: 490 },
      spectra: ['R040092'],
    },

    color: {
      primary_color:         'Pale sky-blue to cornflower blue — the colour of an early morning sky',
      color_variants: [
        'Pale sky-blue (most common and most beloved)',
        'Deeper cornflower blue (more saturated; Madagascar geodes)',
        'Colourless / white (pure SrSO₄)',
        'Pale yellow to orange (trace impurities)',
        'Red-orange (rare; Sicily)',
      ],
      dominant_wavelength_nm: 475,
      oklch:   { l: 0.78, c: 0.12, h: 225 },
      hex:     '#a8c8e8',
      munsell: '5B 8/4',
      color_temperature_k: null,
      psychological_effects: [
        'Sky-blue is the most universally calming colour in human psychology — it lowers cortisol and reduces perceived temperature',
        'Madagascar geode clusters create a visual impression of a cave lined with crystallised sky — immersive and immediately peaceful',
        'The softness (H3–3.5) combined with the pale blue creates a coherent message: gentle, yielding, celestial',
        'The colour fading in sunlight adds a poignant quality — like morning blue that can only be preserved in shade',
        'The name itself (caelestis — heavenly) primes every interaction — you approach it as something from above',
      ],
      harmonics: {
        complementary_hue: 45,
        triadic_hues:      [345, 105],
        analogous_range:   [205, 245],
      },
    },

    metaphysical: {
      mineral_name:     'Celestite',
      chakra_primary:   'Throat',
      chakra_secondary: ['Third Eye', 'Crown', 'Soul Star'],
      element:   ['Air', 'Akasha'],
      planet:    ['Neptune', 'Moon', 'Uranus'],
      archetype: ['The Angel Stone', 'The Sky Keeper', 'The Celestial Messenger'],
      zodiac:    ['Gemini', 'Libra', 'Aquarius'],
      numerology: 2,
      angel_number: 222,
      intention: 'I rise into the sky-blue silence where angels speak. My voice carries what has come from above.',
      traditions: [
        'Named 1799 by A.G. Werner from Latin caelestis (celestial/heavenly) for the characteristic sky-blue colour',
        'Madagascar — the Sakoany deposit produces the world\'s most celebrated celestite geodes; pale blue druzy clusters are one of the most recognisable collector minerals globally',
        'Ohio, USA — Put-in-Bay (South Bass Island) on Lake Erie; massive strontianite and celestite deposits in Silurian dolomite',
        'Sicily — Agrigento region; historically significant celestite deposits associated with sulphur mining',
        'Modern crystal healing — universally known as the "Angel Stone"; used for angelic communication, dream work, and accessing higher realms',
        'Industrial — primary ore of strontium; used in fireworks (red colour), flares, and CRT glass',
      ],
      properties: [
        'IMA 1799 — formula SrSO₄; orthorhombic strontium sulphate; isostructural with barite (BaSO₄) and anglesite (PbSO₄)',
        'Primary ore of strontium — strontium used in fireworks (vivid red colour), flares, magnets, and historically in CRT television glass',
        'Colour fades with prolonged direct sunlight exposure — store away from UV and strong light',
        'H3–3.5 — soft; handle gently; avoid contact with harder minerals',
        'DO NOT use in water — slightly soluble; prolonged contact may cause surface damage and strontium leaching',
        'Perfect cleavage on {010} — cleaves easily; geode specimens are fragile',
        'Major localities: Sakoany (Madagascar), Put-in-Bay (Ohio, USA), Agrigento (Sicily), Yate (UK), Machow (Poland)',
      ],
      gaia_resonance: 'ClarusLens + Noosphere + QuantumNexus',
      safety_warning:  '⚠️ DO NOT use in water — slightly soluble; strontium leaching risk with prolonged contact. Keep out of direct sunlight — colour fades irreversibly. H3–3.5 — soft and fragile; handle with care. No acute handling toxicity at normal exposure.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. CELESTOBARITE
  // Rare (Sr,Ba)SO₄ — strontian barite / barian celestite
  // Zoned blue-white crystals; UK (Cumbria) and Romania primary localities
  // IMA recognised — orthorhombic; intermediate in the celestite-barite series
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Celestobarite',
    mindat_id:    944,
    rruff_ids:    [],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Celestite',

    physical: {
      id:           944,
      longid:       'celestobarite',
      guid:         '',
      name:         'Celestobarite',
      ima_formula:  '(Sr,Ba)SO₄',
      mindat_formula: '(Sr,Ba)SO4',
      ima_status:   'A',
      ima_year:     1971,
      strunzten:    '7.AD.35',
      dana8ed:      '28.3.1.3',
      crystal_system: 'Orthorhombic',
      hardness_min: 3,
      hardness_max: 3.5,
      specific_gravity_min: 3.97,
      specific_gravity_max: 4.30,
      cleavage:    'Perfect on {010}, good on {001}',
      fracture:    'Uneven to conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Pearly (on cleavage)'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Pale blue to blue-white, white, colourless — often shows colour zoning with blue cores and white rims (or vice versa), reflecting compositional variation between Sr-rich and Ba-rich zones.',
      streak:      'White',
      fluorescence: 'Weak white to pale blue under LW UV',
      ri_min:      1.619,
      ri_max:      1.648,
      birefringence: 0.012,
      optical_type: 'B',
      shortdesc:   'Celestobarite — (Sr,Ba)SO₄, rare orthorhombic strontium-barium sulphate. IMA 1971. Intermediate member of the celestite–barite solid solution series. Pale blue to blue-white, often colour-zoned. Primary localities: Cumbria (UK) and Baia Sprie (Romania).',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-944.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Celestobarite',
      refractive_index: { n_alpha: 1.619, n_beta: 1.623, n_gamma: 1.648 },
      birefringence:   0.012,
      optical_sign:    '+',
      dispersion:      'r > v, weak',
      pleochroism:     'None',
      fluorescence_lw: 'Weak white to pale blue',
      fluorescence_sw: 'None to weak',
      phosphorescence: null,
      visible_wavelength_nm: { min: 460, max: 495 },
      spectra: [],
    },

    color: {
      primary_color:         'Pale blue to blue-white, often with visible compositional colour zoning',
      color_variants: [
        'Pale blue with white rim (Sr-rich core, Ba-rich exterior)',
        'White with blue core (inverse zoning)',
        'Uniformly pale blue (homogeneous composition)',
        'Near-colourless white (Ba-dominant)',
      ],
      dominant_wavelength_nm: 480,
      oklch:   { l: 0.85, c: 0.06, h: 220 },
      hex:     '#c8dff0',
      munsell: '5B 9/2',
      color_temperature_k: null,
      psychological_effects: [
        'Colour zoning makes the internal compositional history visible — the crystal narrates its own growth',
        'Softer and less saturated than celestite — a quieter version of the sky-blue palette',
        'Rarity awareness elevates the experience — few practitioners have encountered a named celestobarite specimen',
        'The dual-element identity (Sr + Ba) suggests a stone of integration and bridging between two states',
        'White-blue zoning mirrors cloud and sky — one of the most atmospherically evocative natural patterns',
      ],
      harmonics: {
        complementary_hue: 40,
        triadic_hues:      [340, 100],
        analogous_range:   [200, 240],
      },
    },

    metaphysical: {
      mineral_name:     'Celestobarite',
      chakra_primary:   'Crown',
      chakra_secondary: ['Throat', 'Third Eye'],
      element:   ['Air', 'Earth', 'Akasha'],
      planet:    ['Neptune', 'Saturn'],
      archetype: ['The Bridge Between Worlds', 'The Zoned Truth', 'The Two-Element Keeper'],
      zodiac:    ['Libra', 'Aquarius', 'Capricorn'],
      numerology: 11,
      angel_number: 1111,
      intention: 'I hold two natures in one form. My wholeness is not uniformity — it is the integration of what was once separate.',
      traditions: [
        'IMA 1971 — formally recognised as an intermediate member of the celestite–barite solid solution series',
        'Cumbria (UK) — English Lake District mineral veins; associated with fluorite and barite',
        'Baia Sprie (Romania) — major sulphide mining district with associated sulphate minerals',
        'Crystal healing — rarely encountered as a named stone; often sold simply as "celestite"; practitioners who know it use it for bridging and integration work',
      ],
      properties: [
        'IMA 1971 — formula (Sr,Ba)SO₄; orthorhombic; intermediate in the celestite (SrSO₄) — barite (BaSO₄) solid solution series',
        'Compositional zoning — colour variation reflects changes in Sr:Ba ratio during crystal growth; Sr-rich zones are bluer, Ba-rich zones whiter',
        'SG 3.97–4.30 — higher than celestite (3.96) due to Ba content; noticeably heavy for size',
        'H3–3.5 — soft; handle carefully; perfect cleavage',
        'DO NOT use in water — sulphate mineral; slight solubility; strontium/barium leaching risk',
        'Often misidentified or sold as celestite — compositional analysis needed for confirmation',
        'Primary localities: Cumbria (UK), Baia Sprie (Romania)',
      ],
      gaia_resonance: 'ClarusLens + AnchorPrism',
      safety_warning:  '⚠️ DO NOT use in water — sulphate mineral; barium compounds have higher toxicity than strontium; avoid ingestion and prolonged water contact. H3–3.5 — fragile. No acute handling hazard at normal exposure.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. CERUSSITE
  // PbCO₃ — lead carbonate; orthorhombic
  // Named from Latin cerussa (white lead)
  // IMA recognised — spectacular adamantine lustre; TOXIC (lead)
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Cerussite',
    mindat_id:    951,
    rruff_ids:    ['R050066'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Anglesite',

    physical: {
      id:           951,
      longid:       'cerussite',
      guid:         '',
      name:         'Cerussite',
      ima_formula:  'PbCO₃',
      mindat_formula: 'PbCO3',
      ima_status:   'A',
      ima_year:     1845,
      strunzten:    '5.AB.15',
      dana8ed:      '14a.1.3.1',
      crystal_system: 'Orthorhombic',
      hardness_min: 3,
      hardness_max: 3.5,
      specific_gravity_min: 6.46,
      specific_gravity_max: 6.57,
      cleavage:    'Good on {110} and {021}',
      fracture:    'Conchoidal',
      tenacity:    'Brittle — very fragile',
      luster:      ['Adamantine', 'Sub-adamantine', 'Resinous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Colourless to white, pale grey, pale yellow — pure specimens are brilliantly transparent with diamond-like adamantine lustre. Colour from trace impurities. High dispersion produces rainbow fire in gem-quality crystals.',
      streak:      'White',
      fluorescence: 'Bright yellow to yellow-green under SW UV; one of the most vivid fluorescent responses of any carbonate',
      ri_min:      1.804,
      ri_max:      2.078,
      birefringence: 0.274,
      optical_type: 'B',
      shortdesc:   'Cerussite — PbCO₃, orthorhombic lead carbonate. TOXIC (lead). Named from Latin cerussa (white lead). IMA 1845. Extraordinary adamantine lustre, extreme birefringence (0.274), and brilliant yellow-green SW UV fluorescence. SG 6.46–6.57. Secondary lead mineral from oxidised lead ore deposits.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-951.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Cerussite',
      refractive_index: { n_alpha: 1.804, n_beta: 2.076, n_gamma: 2.078 },
      birefringence:   0.274,
      optical_sign:    '-',
      dispersion:      '0.051 — very high; exceeds diamond (0.044)',
      pleochroism:     'None to very weak (colourless variety)',
      fluorescence_lw: 'Weak yellow',
      fluorescence_sw: 'Brilliant yellow to yellow-green — one of the most vivid carbonate fluorescent responses',
      phosphorescence: 'Some specimens phosphoresce yellow after SW UV',
      visible_wavelength_nm: null,
      spectra: ['R050066'],
    },

    color: {
      primary_color:         'Colourless to white — brilliantly transparent with adamantine fire',
      color_variants: [
        'Colourless transparent (most prized — pure diamond-like fire)',
        'White (most common collector form)',
        'Pale grey (trace impurities)',
        'Pale yellow (trace Fe or organic)',
        'Brown-black surface alteration (limonite coating on weathered specimens)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.92, c: 0.02, h: 90 },
      hex:     '#f8f5e8',
      munsell: 'N 9.5/',
      color_temperature_k: null,
      psychological_effects: [
        'Adamantine lustre is the highest lustre class — approaching the appearance of cut diamond; transparent cerussite literally sparkles like a gem',
        'Birefringence 0.274 — among the highest of any mineral — creates extreme double-image effects visible to the naked eye',
        'Brilliant yellow-green SW UV fluorescence is an instant revelation — the stone transforms completely under UV',
        'SG 6.5 — dramatically heavy for a pale, almost glass-like crystal — the weight is shocking and reorients the senses',
        'The Tsumeb twinned "snow-crystal" forms are among the most geometrically perfect natural objects — architectural at microscopic scale',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Cerussite',
      chakra_primary:   'Crown',
      chakra_secondary: ['Third Eye', 'Soul Star'],
      element:   ['Akasha', 'Earth', 'Metal'],
      planet:    ['Saturn', 'Moon'],
      archetype: ['The Lead Alchemist', 'The Heavy Light', 'The Fire in the White'],
      zodiac:    ['Capricorn', 'Virgo', 'Aquarius'],
      numerology: 8,
      angel_number: 888,
      intention: 'I carry the weight of transformation. What is heavy in me is the seed of the brightest fire.',
      traditions: [
        'Named 1845 from Latin cerussa (white lead) — white lead (2PbCO₃·Pb(OH)₂) was a major historical pigment and cosmetic',
        'Alchemical tradition — lead (Saturn) is the prima materia from which gold is distilled; cerussite as lead carbonate carries the full Saturnian weight of transformation',
        'Tsumeb Mine (Namibia) — the world\'s most mineralogically complex single deposit; Tsumeb cerussite specimens (especially reticulated twins) are among the most prized collector minerals',
        'Broken Hill (NSW, Australia) — major cerussite locality; lead-silver-zinc ore body',
        'Historical pigment — cerussa (white lead) used as a white pigment and cosmetic base in antiquity through the 19th century; source of significant lead poisoning historically',
      ],
      properties: [
        'IMA 1845 — formula PbCO₃; orthorhombic lead carbonate; isostructural with aragonite',
        'TOXIC — lead mineral; DO NOT use in water elixirs; wash hands after handling; keep away from children',
        'Extraordinary optical properties: RI 1.804–2.078; birefringence 0.274 (among the highest of any mineral); dispersion 0.051 (exceeds diamond)',
        'Brilliant yellow-green SW UV fluorescence — one of the most vivid fluorescent responses of any carbonate mineral',
        'SG 6.46–6.57 — extremely heavy; characteristic field identifier',
        'H3–3.5 — very brittle and fragile; collector mineral only; handle with great care',
        'Major localities: Tsumeb (Namibia), Broken Hill (NSW, Australia), Touissit (Morocco), Leadhills (Scotland), Phoenixville (PA, USA)',
      ],
      gaia_resonance: 'AnchorPrism + ClarusLens',
      safety_warning:  '⚠️ TOXIC — lead carbonate. DO NOT use in water elixirs. Wash hands thoroughly after handling. Keep away from children and food preparation areas. Do not inhale dust. H3–3.5 — very brittle; handle with care. Collector mineral only.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. CHALCANTHITE
  // CuSO₄·5H₂O — hydrated copper sulphate; triclinic
  // Named from Greek chalkos (copper) + anthos (flower)
  // Vivid electric blue — HIGHLY TOXIC; water-soluble
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Chalcanthite',
    mindat_id:    988,
    rruff_ids:    ['R060180'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Cavansite',

    physical: {
      id:           988,
      longid:       'chalcanthite',
      guid:         '',
      name:         'Chalcanthite',
      ima_formula:  'CuSO₄·5H₂O',
      mindat_formula: 'CuSO4·5H2O',
      ima_status:   'A',
      ima_year:     1850,
      strunzten:    '7.CB.35',
      dana8ed:      '29.6.11.1',
      crystal_system: 'Triclinic',
      hardness_min: 2.5,
      hardness_max: 2.5,
      specific_gravity_min: 2.12,
      specific_gravity_max: 2.30,
      cleavage:    'Imperfect on {110}',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Vivid electric blue to sky-blue — one of the most intensely saturated blues in the mineral kingdom. Colour from Cu²⁺ in the hydrated sulphate structure. Colour fades and surface whitens on dehydration.',
      streak:      'White',
      fluorescence: 'None',
      ri_min:      1.514,
      ri_max:      1.546,
      birefringence: 0.029,
      optical_type: 'B',
      shortdesc:   'Chalcanthite — CuSO₄·5H₂O, triclinic hydrated copper sulphate. HIGHLY TOXIC. Named from Greek chalkos (copper) + anthos (flower). IMA 1850. Vivid electric blue from Cu²⁺. Water-soluble — dissolves rapidly in water. Much sold material is synthetic (laboratory-grown copper sulphate).',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-988.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Chalcanthite',
      refractive_index: { n_alpha: 1.514, n_beta: 1.537, n_gamma: 1.546 },
      birefringence:   0.029,
      optical_sign:    '+',
      dispersion:      'r > v, moderate',
      pleochroism:     'Distinct: vivid blue / pale blue / pale blue-green',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 460, max: 490 },
      spectra: ['R060180'],
    },

    color: {
      primary_color:         'Vivid electric blue — one of the most saturated natural blues on Earth',
      color_variants: [
        'Vivid electric blue (most common — classic copper sulphate blue)',
        'Deeper royal blue (thicker crystals, denser Cu²⁺)',
        'Pale sky blue (thin crystals or partial dehydration)',
        'White powdery surface (dehydrated — chalcanthite loses water and whitens in dry air)',
      ],
      dominant_wavelength_nm: 470,
      oklch:   { l: 0.45, c: 0.26, h: 245 },
      hex:     '#1a6bc4',
      munsell: '7.5B 5/12',
      color_temperature_k: null,
      psychological_effects: [
        'The electric blue of chalcanthite is arguably the most saturated natural blue in the mineral kingdom — it reads as almost artificial',
        'The knowledge that it will dissolve in water creates a paradox — a brilliant blue crystal that is destroyed by its own element',
        'Much sold chalcanthite is synthetic (lab-grown CuSO₄) — the real mineral from natural deposits is genuinely rare',
        'Dehydration whitening — the crystal visibly fades in dry air — makes it one of the few minerals that shows its chemistry in real time',
        'The "copper flower" etymology (Greek) connects to the beautiful radiating or grape-like natural habits from mine drainage',
      ],
      harmonics: {
        complementary_hue: 65,
        triadic_hues:      [5, 125],
        analogous_range:   [225, 265],
      },
    },

    metaphysical: {
      mineral_name:     'Chalcanthite',
      chakra_primary:   'Throat',
      chakra_secondary: ['Third Eye', 'Higher Heart (Thymus)'],
      element:   ['Water', 'Air'],
      planet:    ['Venus', 'Mercury'],
      archetype: ['The Dissolving Blue', 'The Copper Flower', 'The Saturated Truth'],
      zodiac:    ['Taurus', 'Aquarius', 'Gemini'],
      numerology: 3,
      angel_number: 333,
      intention: 'My truth is vivid, concentrated, and soluble — it dissolves into everything it touches and colours it blue.',
      traditions: [
        'Named from Greek chalkos (copper) + anthos (flower) — the beautiful blue efflorescent crusts and radiating habits in mine workings resemble flowers',
        'Ancient mining use — chalcanthite was known to ancient Greek and Roman miners as a sign of copper ore; Pliny described it in Naturalis Historia',
        'Rio Tinto mines (Spain) — one of the most famous natural chalcanthite localities; the acidic copper-rich waters deposit brilliant blue efflorescences',
        'Chuquicamata (Chile) — the world\'s largest open-pit copper mine; large natural chalcanthite deposits',
        'WARNING — much commercially available "chalcanthite" is synthetic (laboratory-grown copper sulphate pentahydrate); natural specimens are rare',
      ],
      properties: [
        'IMA 1850 — formula CuSO₄·5H₂O; triclinic hydrated copper sulphate',
        'HIGHLY TOXIC — copper sulphate is acutely toxic if ingested; toxic to aquatic organisms; DO NOT use in water under any circumstances',
        'Water-soluble — dissolves rapidly in water; this is one of the most water-soluble minerals in the collection',
        'Dehydration — loses water in dry air; surface whitens as CuSO₄·5H₂O → CuSO₄·3H₂O → CuSO₄; store in sealed container with slight humidity',
        'Much commercially sold chalcanthite is synthetic (lab-grown) — natural mineral from oxidised copper ore deposits is genuinely rare',
        'H2.5 — very soft; fragile; collector mineral only',
        'Major natural localities: Rio Tinto (Spain), Chuquicamata (Chile), Bisbee (AZ, USA)',
      ],
      gaia_resonance: 'ClarusLens + ViriditasHeart',
      safety_warning:  '🚨 HIGHLY TOXIC — copper sulphate. NEVER use in water — acutely toxic if ingested; toxic to aquatic organisms. Wash hands thoroughly after any handling. Keep away from children, food, water, and aquatic environments. Store in sealed container. Do not inhale dust. Collector mineral only — display use only.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. CHALCEDONY
  // Microcrystalline SiO₂ — the universal base stone of the chalcedony family
  // Trigonal (microcrystalline quartz aggregate)
  // Named from Chalcedon (ancient port near modern Istanbul)
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Chalcedony',
    mindat_id:    32,
    rruff_ids:    ['R040031'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Flint',

    physical: {
      id:           32,
      longid:       'chalcedony',
      guid:         '',
      name:         'Chalcedony (microcrystalline quartz — blue-grey variety; parent of carnelian, agate, jasper, onyx)',
      ima_formula:  'SiO₂',
      mindat_formula: 'SiO2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '4.DA.05',
      dana8ed:      '75.1.3.6',
      crystal_system: 'Trigonal (microcrystalline aggregate — fibrous chalcedony structure)',
      hardness_min: 6.5,
      hardness_max: 7,
      specific_gravity_min: 2.58,
      specific_gravity_max: 2.64,
      cleavage:    'None',
      fracture:    'Conchoidal (smooth, shell-like)',
      tenacity:    'Brittle',
      luster:      ['Waxy', 'Dull (rough surfaces)', 'Vitreous (fresh fracture)'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Pale blue-grey to white (type chalcedony); parent species includes carnelian (orange-red), agate (banded), jasper (opaque), onyx (black-white banded), chrysoprase (green), sard, and bloodstone. Colour from trace impurities or micro-inclusions.',
      streak:      'White',
      fluorescence: 'Variable — some specimens show pale blue-white under LW UV',
      ri_min:      1.530,
      ri_max:      1.540,
      birefringence: 0.004,
      optical_type: 'U',
      shortdesc:   'Chalcedony — microcrystalline SiO₂; the parent species for carnelian, agate, jasper, onyx, chrysoprase, sard, and bloodstone. Named from Chalcedon (ancient city near Istanbul). Pale blue-grey in type form. One of the most widely used gem and tool materials in human history.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-32.html',
      piezoelectric:     true,
      safe_for_water:    true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name:    'Chalcedony',
      refractive_index: { n_omega: 1.540, n_epsilon: 1.536 },
      birefringence:   0.004,
      optical_sign:    '+',
      dispersion:      '0.013',
      pleochroism:     'None',
      fluorescence_lw: 'Pale blue-white (variable)',
      fluorescence_sw: 'None to weak',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R040031'],
    },

    color: {
      primary_color:         'Pale blue-grey to white — the type chalcedony colour; cool, soft, and translucent',
      color_variants: [
        'Pale blue-grey (type chalcedony — the most classic form)',
        'White to cream (common massive form)',
        'Blue chalcedony (more saturated blue — "Holly Blue", "Namibian Blue")',
        'Pink chalcedony (trace Mn or Fe)',
        'Lavender chalcedony (rare; trace Fe or structural colour)',
        'Green chalcedony (chrysoprase if Ni-bearing; or Cr-bearing)',
        'All carnelian, agate, jasper, onyx, sard, bloodstone varieties (named sub-types)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.80, c: 0.05, h: 220 },
      hex:     '#b8c8d8',
      munsell: '5B 8/2',
      color_temperature_k: null,
      psychological_effects: [
        'The chalcedony family is the most diverse colour range of any single mineral species — from fire-red carnelian to black onyx to green chrysoprase',
        'Waxy translucency creates a soft, inner-lit quality — chalcedony absorbs and re-emits light differently from crystalline quartz',
        'Type blue-grey chalcedony is one of the most neutral, balanced colours in the mineral kingdom — neither warm nor cold, neither dark nor light',
        'The conchoidal fracture — the same as flint and obsidian — connects chalcedony directly to the first human tools; this is the material of Palaeolithic blades',
        'The chalcedony family\'s ubiquity across human cultures (every continent, every era) gives it an unmatched sense of shared human heritage',
      ],
      harmonics: {
        complementary_hue: 40,
        triadic_hues:      [340, 100],
        analogous_range:   [200, 240],
      },
    },

    metaphysical: {
      mineral_name:     'Chalcedony',
      chakra_primary:   'Throat',
      chakra_secondary: ['Third Eye', 'Heart', 'All chakras (via colour varieties)'],
      element:   ['Water', 'Air', 'Earth'],
      planet:    ['Moon', 'Mercury'],
      archetype: ['The Ancient Speaker', 'The Universal Stone', 'The Mother of Forms'],
      zodiac:    ['Cancer', 'Virgo', 'Sagittarius'],
      numerology: 9,
      angel_number: 999,
      intention: 'I am the mother of forms. In every colour I remain myself. I have been in every human hand that ever reached for the sacred.',
      traditions: [
        'Named from Chalcedon (Kadıköy) — ancient Greek port city on the Bosphorus; major ancient trade hub for gems',
        'Palaeolithic — flint (cryptocrystalline quartz, chalcedony family) was the primary tool material of early Homo sapiens; the first human technology',
        'Ancient Egypt — carnelian (red chalcedony) in royal jewellery and amulets; blue-grey chalcedony used for scarabs',
        'Mesopotamia — cylinder seals carved from chalcedony; agate chalcedony bowls in royal burials at Ur',
        'Roman — intaglio ring stones in chalcedony; "chalcedony" appears in Pliny\'s Naturalis Historia',
        'Christian — chalcedony listed as one of the twelve foundation stones of the New Jerusalem (Revelation 21:19)',
        'Islamic — aqiq (carnelian) one of the most sacred stones; chalcedony family broadly revered',
      ],
      properties: [
        'Microcrystalline SiO₂ — fibrous or granular aggregate of quartz; distinguished from macrocrystalline quartz by submicron crystal size',
        'Parent species for: carnelian (orange-red), agate (banded), jasper (opaque), onyx (black-white), chrysoprase (Ni-green), sard (brown-red), bloodstone (green with red spots), plasma, prase',
        'Named varieties differ only in colour and pattern — all are SiO₂ with trace impurities; same physical properties',
        'Conchoidal fracture — the same fracture pattern as flint and obsidian; the basis of Palaeolithic stone tool technology',
        'H6.5–7 — excellent durability; ideal for jewellery, carving, and everyday use',
        'Piezoelectric — keep away from hard drives and sensitive electronics',
        'Safe for water — SiO₂ is chemically inert; no toxic elements',
        'Major localities: Brazil, Uruguay, India, Madagascar, Namibia, Turkey (historical), USA (Oregon, Montana)',
      ],
      gaia_resonance: 'ClarusLens + ViriditasHeart + AnchorPrism',
      safety_warning:  '⚠️ PIEZOELECTRIC — keep away from hard drives and sensitive electronics. Safe for water. H6.5–7 — durable for everyday use. No toxic elements. One of the safest crystals for all uses.',
    },
  },

];

export default BATCH_C3;

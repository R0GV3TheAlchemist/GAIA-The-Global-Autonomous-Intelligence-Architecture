/**
 * src/crystals/db/batch-c7.data.ts
 * GAIA-OS Crystal Database — Batch C-7
 *
 * Entries:
 *   1. Coral         — CaCO₃ organic skeletal material — NOT a mineral; trade name
 *   2. Covellite     — CuS; indigo-blue copper sulphide; iridescent — TOXIC
 *   3. Cryolite      — Na₃AlF₆; near-invisible in water; icy white; near-extinct in nature
 *   4. Cuprite       — Cu₂O; deep ruby-red copper oxide — TOXIC
 *   5. Cyanite       — Al₂SiO₅; the original name for Kyanite; blue blades; variable hardness
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-30
 *
 * SAFETY NOTE: Covellite (Cu sulphide) and Cuprite (Cu oxide) are toxic in water.
 * Cryolite historically contained fluoride; avoid dust. Coral is organic — not a mineral.
 * Kyanite/Cyanite: fibrous dust may be hazardous — do not grind.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_C7: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. CORAL
  // CaCO₃ — organic biogenic calcium carbonate skeleton
  // NOT a mineral — biogenic material; animal secretion
  // Red, pink, white, black varieties; precious coral = Corallium rubrum
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Coral',
    mindat_id:    null,
    rruff_ids:    [],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   true,
    color_layer:  'natural',
    yin_yang_pair: 'Pearl',

    physical: {
      id:           null,
      longid:       'coral',
      guid:         '',
      name:         'Coral (biogenic CaCO₃ skeleton — NOT a mineral)',
      ima_formula:  'CaCO₃ (biogenic — organic origin)',
      mindat_formula: 'CaCO3',
      ima_status:   'Not IMA — biogenic material; not a mineral by strict definition',
      ima_year:     null,
      strunzten:    null,
      dana8ed:      null,
      crystal_system: 'Trigonal (calcite structure) to Orthorhombic (aragonite structure); organic',
      hardness_min: 3,
      hardness_max: 4,
      specific_gravity_min: 2.60,
      specific_gravity_max: 2.70,
      cleavage:    'None (organic structure)',
      fracture:    'Uneven to splintery',
      tenacity:    'Brittle',
      luster:      ['Waxy', 'Dull', 'Vitreous (polished)'],
      diaphaneity: ['Opaque'],
      colour:      'Precious coral (Corallium rubrum): salmon-pink to deep red-orange (ox-blood red = most prized). Also white, pale pink (angel skin), black (black coral = Antipatharia). Colour from carotenoid and polyene organic pigments; fades with prolonged sunlight.',
      streak:      'White',
      fluorescence: 'Weak blue-white (LW UV) in some specimens',
      ri_min:      1.486,
      ri_max:      1.658,
      birefringence: 0.172,
      optical_type: null,
      shortdesc:   'Coral — biogenic CaCO₃ skeleton secreted by marine cnidarian polyps. NOT a mineral. Precious coral = Corallium rubrum; salmon-pink to ox-blood red. Also white, angel-skin pink, black. Colour from organic pigments; fades in sunlight. Mediterranean and Pacific sources. CITES protected species.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  null,
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Coral (Biogenic)',
      refractive_index: { n_mean: 1.560 },
      birefringence:   0.172,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'Weak blue-white in some specimens',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 590, max: 640 },
      spectra: [],
    },

    color: {
      primary_color:         'Salmon-pink to deep ox-blood red — the colour of the living sea rendered in bone',
      color_variants: [
        'Ox-blood red (Corallium rubrum — rarest and most prized; deep red with no orange)',
        'Salmon-pink to coral-orange (most common precious coral colour)',
        'Angel-skin pink (pale, delicate; highly prized in Japanese tradition)',
        'White (bleached or naturally white species)',
        'Black (Antipatharian black coral — different chemistry; organic conchiolin)',
      ],
      dominant_wavelength_nm: 620,
      oklch:   { l: 0.60, c: 0.26, h: 30 },
      hex:     '#e05030',
      munsell: '5R 5/12',
      color_temperature_k: null,
      psychological_effects: [
        'Coral red-orange is one of the most universally warm and life-affirming colours — it reads as vitality, warmth, and the organic world',
        'The name "coral" is itself a colour name — like copper, the material so defined its hue that the hue took the name',
        'Knowing coral is built from millions of tiny animal skeletons creates a profound sense of collective life — every piece is a community',
        'The ox-blood red of the finest Corallium is one of the deepest, most saturated natural reds available in an organic gemstone',
        'CITES protection awareness — working ethically with coral requires understanding conservation; the knowledge transforms the relationship',
      ],
      harmonics: {
        complementary_hue: 210,
        triadic_hues:      [150, 270],
        analogous_range:   [10, 50],
      },
    },

    metaphysical: {
      mineral_name:     'Coral',
      chakra_primary:   'Sacral',
      chakra_secondary: ['Root', 'Heart', 'Solar Plexus'],
      element:   ['Water', 'Fire', 'Earth'],
      planet:    ['Mars', 'Venus', 'Moon'],
      archetype: ['The Ocean’s Bone', 'The Red Sea Garden', 'The Community of Souls'],
      zodiac:    ['Aries', 'Taurus', 'Pisces', 'Scorpio'],
      numerology: 5,
      angel_number: 555,
      intention: 'I am the living architecture of the sea. Every part of me was built by ten thousand small lives working together.',
      traditions: [
        'Mediterranean — red coral (Corallium rubrum) used as a protective amulet since Neolithic times; Roman children wore coral amulets to ward off evil; associated with Mars and blood',
        'Italian tradition — il corallo — red coral worn against the evil eye (malocchio); the "mano" (hand) and horn shapes in coral are classic Italian amulet forms',
        'Japanese / Chinese tradition — red and angel-skin coral prized for millennia; ox-blood coral (mo xi / moxi) commands the highest prices in Asian markets',
        'Native American — Southwestern peoples (Zuni, Navajo, Pueblo) use red coral extensively in jewellery alongside turquoise; traded inland from Pacific and Gulf coasts',
        'Vedic tradition — red coral (moonga/praval) is the gemstone for Mars (Mangal) in Jyotish; one of the Navaratna; prescribed for Mars placements and courage',
      ],
      properties: [
        'NOT a mineral — biogenic CaCO₃ skeleton secreted by marine cnidarian polyps (order Gorgonacea for precious coral)',
        'Precious coral: Corallium rubrum (Mediterranean), C. japonicum (Pacific); CITES Appendix II listed; regulated internationally',
        'Colour from organic carotenoid and polyene pigments — fades with prolonged direct sunlight; avoid bleaching agents',
        'DO NOT use in water long-term — organic material; salt water and prolonged fresh water contact damage surface',
        'H3–4 — relatively soft; protect from scratches; store separately',
        'Black coral (Antipatharia) is a different organism with organic conchiolin skeleton; different chemistry from red coral',
        'Ethical sourcing critical — wild harvest heavily regulated or banned; only use antique, vintage, or certified sustainable coral',
      ],
      gaia_resonance: 'ViriditasHeart + Noosphere + AnchorPrism',
      safety_warning:  '⚠️ NOT a mineral — biogenic organic material. DO NOT use in prolonged water or salt water. Colour fades in direct sunlight. H3–4 — soft. ETHICAL NOTE: Corallium rubrum is CITES protected; only use antique, vintage, or certified sustainable material. No significant toxicity from handling.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. COVELLITE
  // CuS — copper(II) sulphide; hexagonal
  // Named after N. Covelli (discoverer at Vesuvius, 1832)
  // Indigo-blue to violet-blue with vivid iridescence; TOXIC
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Covellite',
    mindat_id:    1135,
    rruff_ids:    ['R070569'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Chalcocite',

    physical: {
      id:           1135,
      longid:       'covellite',
      guid:         '',
      name:         'Covellite',
      ima_formula:  'CuS',
      mindat_formula: 'CuS',
      ima_status:   'A',
      ima_year:     1832,
      strunzten:    '2.CB.15',
      dana8ed:      '2.8.16.1',
      crystal_system: 'Hexagonal',
      hardness_min: 1.5,
      hardness_max: 2,
      specific_gravity_min: 4.60,
      specific_gravity_max: 4.76,
      cleavage:    'Perfect basal on {0001} — yields flexible (non-elastic) plates',
      fracture:    'Uneven',
      tenacity:    'Flexible (cleavage plates), brittle otherwise',
      luster:      ['Sub-metallic', 'Resinous'],
      diaphaneity: ['Opaque'],
      colour:      'Deep indigo-blue to violet-blue with vivid iridescent surface tarnish: purple, crimson, gold. The indigo-blue is structural colour of the mineral itself (not tarnish). Iridescent surface tarnish is a thin-film effect. One of the most beautiful metallic minerals.',
      streak:      'Lead-grey to black',
      fluorescence: 'None',
      ri_min:      null,
      ri_max:      null,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Covellite — CuS, hexagonal copper sulphide. TOXIC. Named for N. Covelli, first described from Vesuvius 1832. Deep indigo-blue to violet-blue with vivid iridescent tarnish. Perfect basal cleavage. H1.5–2 — very soft. SG 4.6–4.76. Major locality: Butte, Montana (USA).',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-1135.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Covellite',
      refractive_index: null,
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 420, max: 460 },
      spectra: ['R070569'],
    },

    color: {
      primary_color:         'Deep indigo-blue to violet-blue with vivid iridescent crimson-gold-purple tarnish',
      color_variants: [
        'Deep indigo-blue (fresh basal surface — structural colour)',
        'Violet-blue with crimson iridescence (most common tarnish pattern)',
        'Purple-gold iridescent (heavy tarnish)',
        'Blue-black (massive form)',
        'Indigo with red and gold iridescent patches (Butte, Montana type)',
      ],
      dominant_wavelength_nm: 440,
      oklch:   { l: 0.30, c: 0.18, h: 280 },
      hex:     '#3a2880',
      munsell: '7.5PB 3/8',
      color_temperature_k: null,
      psychological_effects: [
        'The combination of deep indigo structural colour with vivid crimson-gold iridescence is one of the most visually complex combinations in the mineral world',
        'Indigo is a rare, psychologically deep colour — between blue and violet; associated with the deepest night sky',
        'The iridescent tarnish creates a sense that the stone is alive and shifting — the colour changes with every micro-movement',
        'The flexible, peeling cleavage plates reveal new indigo surfaces — discovering the true blue under the tarnish is a physical act of uncovering',
        'Vesuvius origin (first described) gives covellite a volcanic mythology — born from the most famous active volcano in the Western world',
      ],
      harmonics: {
        complementary_hue: 100,
        triadic_hues:      [40, 160],
        analogous_range:   [260, 300],
      },
    },

    metaphysical: {
      mineral_name:     'Covellite',
      chakra_primary:   'Third Eye',
      chakra_secondary: ['Crown', 'Throat', 'Root'],
      element:   ['Water', 'Fire', 'Akasha'],
      planet:    ['Neptune', 'Pluto', 'Venus'],
      archetype: ['The Indigo Copper', 'The Vesuvius Blue', 'The Deep Iridescence'],
      zodiac:    ['Scorpio', 'Aquarius', 'Sagittarius'],
      numerology: 7,
      angel_number: 777,
      intention: 'My blue is not tarnish — it is my true self. What you see shifting on my surface is transformation, not decay.',
      traditions: [
        'Named after Nicola Covelli (1790–1829), Italian naturalist who first collected specimens from Vesuvius fumaroles; IMA 1832',
        'Butte, Montana — the most famous covellite locality in the world; spectacular indigo crystals with vivid iridescence from the Butte copper district',
        'Vesuvius fumaroles — original locality; formed by volcanic gas reactions with native copper; the volcanic origin adds a layer of alchemical mythology',
        'Modern crystal healing — covellite is a relatively recent addition to the crystal healing canon; used for past-life access, psychic vision, and transformation',
        'Photography tradition — covellite’s vivid colour makes it one of the most photographed mineral specimens; a staple of mineral photography',
      ],
      properties: [
        'IMA 1832 — formula CuS; hexagonal copper sulphide',
        'TOXIC — copper sulphide; DO NOT use in water; wash hands after handling',
        'Deep indigo-blue is structural colour of the mineral itself, NOT a surface tarnish — unique among copper minerals',
        'Iridescent tarnish (crimson-gold-purple) is a thin-film surface oxide; adds to visual complexity',
        'Perfect basal cleavage yields flexible (non-elastic) plates — similar to molybdenite in feel',
        'H1.5–2 — very soft; handle with extreme care; store in padded box',
        'Major localities: Butte (MT, USA), Bor (Serbia), Predazzo (Italy — near original Vesuvius type locality), Sardinia',
      ],
      gaia_resonance: 'QuantumNexus + ClarusLens + Noosphere',
      safety_warning:  '⚠️ TOXIC — copper sulphide. DO NOT use in water. Wash hands after handling. H1.5–2 — extremely fragile; handle minimally; store in padded, sealed container. Sulphide minerals may release H₂S in acid.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. CRYOLITE
  // Na₃AlF₆ — sodium aluminium fluoride; monoclinic
  // Named from Greek kryos (ice) + lithos (stone) — ice stone
  // Near-extinct in nature (Ivigtut, Greenland deposit nearly exhausted)
  // Unique: RI ≈1.34 = near-invisible in water
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Cryolite',
    mindat_id:    1153,
    rruff_ids:    ['R060563'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Ice (as concept — metaphysical pair)',

    physical: {
      id:           1153,
      longid:       'cryolite',
      guid:         '',
      name:         'Cryolite',
      ima_formula:  'Na₃AlF₆',
      mindat_formula: 'Na3AlF6',
      ima_status:   'A',
      ima_year:     1799,
      strunzten:    '3.CB.15',
      dana8ed:      '11.3.1.1',
      crystal_system: 'Monoclinic (pseudo-cubic habit)',
      hardness_min: 2.5,
      hardness_max: 3,
      specific_gravity_min: 2.95,
      specific_gravity_max: 2.97,
      cleavage:    'None; parting on {001} and {110}',
      fracture:    'Uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Greasy', 'Pearly'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Snow-white to colourless; rarely pale brownish or reddish. Appears almost invisible when immersed in water (RI 1.338–1.340 ≈ water 1.333). Pure specimens are among the most optically invisible minerals.',
      streak:      'White',
      fluorescence: 'None',
      ri_min:      1.338,
      ri_max:      1.340,
      birefringence: 0.001,
      optical_type: 'B',
      shortdesc:   'Cryolite — Na₃AlF₆, monoclinic sodium aluminium fluoride. Named from Greek kryos (ice) + lithos (stone). IMA 1799. RI 1.338–1.340 ≈ water — nearly invisible when immersed. Single primary locality: Ivigtut, Greenland (deposit nearly exhausted; now essentially extinct in nature). Historically essential for aluminium smelting.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-1153.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Cryolite',
      refractive_index: { n_alpha: 1.338, n_beta: 1.338, n_gamma: 1.340 },
      birefringence:   0.001,
      optical_sign:    '+',
      dispersion:      'r < v, very weak',
      pleochroism:     'None',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R060563'],
    },

    color: {
      primary_color:         'Snow-white to colourless — the colour of ice made mineral',
      color_variants: [
        'Snow-white (most common — scattering of internal parting)',
        'Colourless transparent (gem quality)',
        'Pale brownish (iron staining)',
        'Pale reddish (minor impurities)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.95, c: 0.01, h: 200 },
      hex:     '#f4f5f5',
      munsell: 'N 9.5/',
      color_temperature_k: null,
      psychological_effects: [
        'The near-invisible quality in water is one of the most uncanny mineral properties — a stone that disappears when immersed',
        'White and colourless minerals create a quality of pure potential — no colour to distract, no saturation to hold the eye; only form and light remain',
        'The Greenland origin and near-extinction of the natural supply gives cryolite a quality of profound rarity — one of the truly finite minerals',
        'The name (ice stone) and the RI (matching water) create a conceptual circle — cryolite is mineralised ice in both name and optical behaviour',
        'The industrial history — cryolite made the Aluminium Age possible by enabling the Hall-Héroult process — links a simple white mineral to the entire modern world',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Cryolite',
      chakra_primary:   'Crown',
      chakra_secondary: ['Soul Star', 'Third Eye', 'Higher Heart (Thymus)'],
      element:   ['Akasha', 'Water', 'Air'],
      planet:    ['Moon', 'Neptune', 'Uranus'],
      archetype: ['The Ice Stone', 'The Invisible Mineral', 'The Greenland Rarity'],
      zodiac:    ['Aquarius', 'Pisces', 'Cancer'],
      numerology: 11,
      angel_number: 1111,
      intention: 'I disappear in water. My invisibility is not absence — it is perfect transparency. I am what remains when all colour is released.',
      traditions: [
        'Named 1799 from Greek kryos (ice) + lithos (stone) by Abildgaard — for its icy appearance and the Greenland origin',
        'Ivigtut, Greenland — the only major natural deposit; used by Inuit people before European contact; mined industrially 1854–1987 until near-exhaustion',
        'Hall-Héroult process (1886) — cryolite as the solvent flux for aluminium oxide enabled commercial aluminium production; without natural cryolite (and now synthetic Na₃AlF₆), the Aluminium Age could not have begun',
        'Near-extinction — the Ivigtut deposit is considered essentially exhausted for commercial purposes; natural cryolite specimens are now genuinely rare collector minerals',
        'Modern crystal healing — rare in the market; used for deep clarity, dissolution of illusion, and accessing hidden or invisible dimensions',
      ],
      properties: [
        'IMA 1799 — formula Na₃AlF₆; monoclinic sodium aluminium fluoride',
        'RI 1.338–1.340 ≈ water (1.333) — nearly invisible when immersed in water; one of the most remarkable optical properties of any mineral',
        'Nearly extinct in nature — Ivigtut deposit (SW Greenland) is the world’s only significant locality; essentially exhausted',
        'Historically critical — natural cryolite was the essential flux for the Hall-Héroult aluminium smelting process; synthetic Na₃AlF₆ now used instead',
        'DO NOT use in water — fluoride mineral; fluoride ions can leach; avoid ingestion',
        'H2.5–3 — soft; handle gently',
        'No significant acute contact toxicity; avoid dust inhalation (fluoride); do not grind',
      ],
      gaia_resonance: 'QuantumNexus + ClarusLens',
      safety_warning:  '⚠️ DO NOT use in water — fluoride mineral; fluoride ions leach. Avoid dust inhalation. H2.5–3 — soft. No acute contact toxicity from normal dry handling. Extremely rare — treat specimens with exceptional care.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. CUPRITE
  // Cu₂O — copper(I) oxide; cubic (isometric)
  // Named from Latin cuprum (copper)
  // Deep ruby-red to near-black; adamantine to sub-metallic; TOXIC
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Cuprite',
    mindat_id:    1167,
    rruff_ids:    ['R040034'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Malachite',

    physical: {
      id:           1167,
      longid:       'cuprite',
      guid:         '',
      name:         'Cuprite',
      ima_formula:  'Cu₂O',
      mindat_formula: 'Cu2O',
      ima_status:   'A',
      ima_year:     1845,
      strunzten:    '4.AA.10',
      dana8ed:      '4.1.1.1',
      crystal_system: 'Cubic (isometric)',
      hardness_min: 3.5,
      hardness_max: 4,
      specific_gravity_min: 5.85,
      specific_gravity_max: 6.15,
      cleavage:    'Imperfect on {111}',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Adamantine', 'Sub-metallic'],
      diaphaneity: ['Transparent', 'Translucent', 'Opaque'],
      colour:      'Deep ruby-red to dark crimson-red; sometimes so dark as to appear near-black in massive form. Gem-quality transparent crystals show deep ruby-red with adamantine fire. Colour from Cu₂O electronic structure. The finest cuprite rivals ruby in depth of red.',
      streak:      'Brownish-red to brick-red',
      fluorescence: 'None',
      ri_min:      2.849,
      ri_max:      2.849,
      birefringence: null,
      optical_type: 'I',
      shortdesc:   'Cuprite — Cu₂O, cubic copper(I) oxide. TOXIC. Named from Latin cuprum. IMA 1845. Deep ruby-red with adamantine to sub-metallic lustre. RI 2.849 — very high; gem crystals have intense fire. SG 5.85–6.15 — very heavy. Chalcotrichite: hair-like cuprite variety. Major localities: Bisbee (AZ), Tsumeb (Namibia), Chessy (France).',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-1167.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Cuprite',
      refractive_index: { n_iso: 2.849 },
      birefringence:   null,
      optical_sign:    null,
      dispersion:      'Very high — r > v strongly',
      pleochroism:     null,
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 620, max: 700 },
      spectra: ['R040034'],
    },

    color: {
      primary_color:         'Deep ruby-red to dark crimson — copper’s deepest red',
      color_variants: [
        'Deep ruby-red transparent (gem quality — adamantine)',
        'Dark crimson to blood-red (most common)',
        'Near-black massive (opaque, very high Cu₂O)',
        'Hair-like scarlet filaments on matrix (chalcotrichite variety)',
        'Red coating on native copper (tarnish layer)',
      ],
      dominant_wavelength_nm: 660,
      oklch:   { l: 0.35, c: 0.25, h: 20 },
      hex:     '#8a1010',
      munsell: '5R 3/12',
      color_temperature_k: null,
      psychological_effects: [
        'Deep ruby-red is one of the most psychologically powerful colours — the colour of blood, fire, and concentrated life force',
        'RI 2.849 — higher than diamond — gives transparent cuprite crystals an adamantine fire that is extraordinary in a red stone',
        'The chalcotrichite variety (hair-like filaments) creates a visual quality of frozen fire — scarlet threads that look like stopped motion',
        'The transition from native copper (salmon-pink) → cuprite (ruby-red) → malachite (green) is a complete narrative of oxidation chemistry in colour',
        'Deep crimson-red near-black massive cuprite has a weight and darkness that pure ruby lacks — it is a more serious, more concentrated red',
      ],
      harmonics: {
        complementary_hue: 200,
        triadic_hues:      [140, 260],
        analogous_range:   [0, 40],
      },
    },

    metaphysical: {
      mineral_name:     'Cuprite',
      chakra_primary:   'Root',
      chakra_secondary: ['Sacral', 'Earth Star', 'Base'],
      element:   ['Fire', 'Earth', 'Metal'],
      planet:    ['Mars', 'Pluto', 'Venus'],
      archetype: ['The Copper Ruby', 'The Red Oxide', 'The Fire of Transformation'],
      zodiac:    ['Aries', 'Scorpio', 'Taurus'],
      numerology: 8,
      angel_number: 888,
      intention: 'I am what copper becomes when it breathes oxygen. My red is the fire of transformation held in crystal form.',
      traditions: [
        'Named 1845 from Latin cuprum (copper) by Haidinger — direct naming for the copper oxide composition',
        'Chessy-les-Mines, France (Chessy, near Lyon) — the original famous locality; "Chessy copper" was the source of fine cuprite and azurite specimens for European collectors from the 18th century',
        'Bisbee, Arizona — spectacular ruby-red transparent cuprite crystals; some of the finest gem-quality material known',
        'Tsumeb, Namibia — one of the world’s greatest mineral localities; exceptional cuprite specimens alongside azurite, malachite, and galena',
        'Modern crystal healing — cuprite used for grounding, life force, survival energy, and the Root chakra; the deepest red copper mineral',
      ],
      properties: [
        'IMA 1845 — formula Cu₂O; cubic (isometric) copper(I) oxide',
        'TOXIC — copper oxide; DO NOT use in water; copper compounds are toxic',
        'RI 2.849 — higher than diamond; transparent gem crystals have exceptional adamantine lustre and fire',
        'SG 5.85–6.15 — very heavy for an oxide mineral',
        'Chalcotrichite: hair-like (capillary) variety of cuprite; extremely delicate scarlet filaments; treat as unmovable display specimen',
        'Part of the copper oxidation sequence: native Cu → cuprite (Cu₂O) → tenorite (CuO) → malachite/azurite (carbonates)',
        'Major localities: Bisbee (AZ, USA), Chessy (France), Tsumeb (Namibia), Broken Hill (Australia), Onganja (Namibia)',
      ],
      gaia_resonance: 'AnchorPrism + SovereignCore + ViriditasHeart',
      safety_warning:  '⚠️ TOXIC — copper oxide. DO NOT use in water. Wash hands after handling. Keep away from children and food. Chalcotrichite variety: extremely fragile — do not handle; display only.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. CYANITE (KYANITE)
  // Al₂SiO₅ — triclinic aluminium silicate
  // Cyanite is the original IMA-preferred name; Kyanite is the common trade name
  // Blue blades; unique variable hardness (H4.5 along / H6.5 across)
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Cyanite (Kyanite)',
    mindat_id:    2346,
    rruff_ids:    ['R040054'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Andalusite',

    physical: {
      id:           2346,
      longid:       'kyanite',
      guid:         '',
      name:         'Kyanite (IMA: Cyanite — Al₂SiO₅)',
      ima_formula:  'Al₂SiO₅',
      mindat_formula: 'Al2SiO5',
      ima_status:   'A',
      ima_year:     1789,
      strunzten:    '9.AF.15',
      dana8ed:      '52.1.2.1',
      crystal_system: 'Triclinic',
      hardness_min: 4.5,
      hardness_max: 7,
      specific_gravity_min: 3.53,
      specific_gravity_max: 3.70,
      cleavage:    'Perfect on {100}, good on {010}',
      fracture:    'Splintery',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Pearly (on cleavage)'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Blue to blue-green most common (Fe²⁺/Ti⁴⁺); also white, grey, green, orange, black. Blue colour often zoned or streaked along blade length. Orange kyanite (Mn³⁺) from Tanzania is rare. Black kyanite is graphite-bearing. Variable hardness is unique: H4.5 parallel to length, H6–6.5 perpendicular.',
      streak:      'White',
      fluorescence: 'Weak red under LW UV (some specimens)',
      ri_min:      1.710,
      ri_max:      1.734,
      birefringence: 0.017,
      optical_type: 'B',
      shortdesc:   'Kyanite (IMA: Cyanite) — Al₂SiO₅, triclinic aluminium silicate. Named from Greek kyanos (blue). IMA 1789. Distinctive variable hardness: H4.5 along blade length, H6–6.5 across. Blue most common; also orange (Mn³⁺, Tanzania), green, black. One of three Al₂SiO₅ polymorphs with andalusite and sillimanite.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-2346.html',
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Kyanite',
      refractive_index: { n_alpha: 1.710, n_beta: 1.720, n_gamma: 1.734 },
      birefringence:   0.017,
      optical_sign:    '-',
      dispersion:      'r > v, weak',
      pleochroism:     'Strong trichroism: deep blue / light blue / colourless to pale blue',
      fluorescence_lw: 'Weak red in some specimens',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 450, max: 490 },
      spectra: ['R040054'],
    },

    color: {
      primary_color:         'Blue to blue-green — the blue of high-pressure metamorphic time',
      color_variants: [
        'Classic blue blade (most common — Fe²⁺/Ti⁴⁺)',
        'Blue-green to teal (variable Fe/Ti ratio)',
        'White to grey (low chromophore content)',
        'Green (Cr³⁺ or V-bearing — rare)',
        'Orange (Mn³⁺ — Tanzania; rare and prized)',
        'Black (graphite-bearing inclusions — metamorphic)',
        'Colourless (very rare gem quality)',
      ],
      dominant_wavelength_nm: 470,
      oklch:   { l: 0.50, c: 0.22, h: 250 },
      hex:     '#3060b8',
      munsell: '7.5B 5/8',
      color_temperature_k: null,
      psychological_effects: [
        'Kyanite’s variable hardness is unique in the mineral kingdom — the same crystal resists scratching differently in different directions; a physical lesson in directional strength',
        'The blue blade form — long, flat, angled crystals — is one of the most architecturally distinctive crystal habits; blades of compressed metamorphic time',
        'Blue with streaked or zoned colour creates a sense of gradient and movement within the static crystal',
        'Orange kyanite (Tanzania) is so unusual — the same formula, the same form, a completely different colour — it teaches that identity is more than surface',
        'High-pressure origin (subducted crust) gives kyanite the quality of something that has survived extreme conditions and emerged transformed',
      ],
      harmonics: {
        complementary_hue: 70,
        triadic_hues:      [10, 130],
        analogous_range:   [230, 270],
      },
    },

    metaphysical: {
      mineral_name:     'Cyanite (Kyanite)',
      chakra_primary:   'Throat',
      chakra_secondary: ['Third Eye', 'Crown', 'All (alignment)'],
      element:   ['Air', 'Akasha', 'Water'],
      planet:    ['Mercury', 'Uranus', 'Neptune'],
      archetype: ['The Blue Blade', 'The Aligner', 'The High-Pressure Truth'],
      zodiac:    ['Aries', 'Taurus', 'Libra'],
      numerology: 4,
      angel_number: 444,
      intention: 'I do not accumulate. I align. Every blade of me is a direction and a truth simultaneously.',
      traditions: [
        'Named 1789 from Greek kyanos (blue) by Werner; IMA preferred name is "cyanite" though "kyanite" dominates in trade and usage',
        'High-pressure metamorphic indicator — kyanite’s presence in a rock indicates formation under high-pressure conditions; used in geological pressure-temperature mapping',
        'Nepal and Tibet — kyanite found in Himalayan metamorphic belts; the geological uplift of the Himalayas produces classic kyanite-bearing schists',
        'Modern crystal healing — "the stone that never needs clearing" — traditional claim that kyanite does not accumulate negative energy (no mineralogical basis but widely held in crystal healing canon)',
        'Black kyanite — graphite-bearing bladed kyanite from Brazil; used in crystal healing for cutting cords, auric repair, and grounding',
      ],
      properties: [
        'IMA 1789 — formula Al₂SiO₅; triclinic aluminium silicate; one of three Al₂SiO₅ polymorphs with andalusite and sillimanite',
        'Unique variable hardness: H4.5 parallel to blade length (along c-axis cleavage); H6–6.5 perpendicular to blade — the defining diagnostic property',
        'Blue colour from Fe²⁺/Ti⁴⁺ charge transfer; orange from Mn³⁺; green from Cr³⁺',
        'Safe for water — Al₂SiO₅; no toxic elements; chemically stable',
        'DO NOT grind or create dust — fibrous aluminium silicate dust may present respiratory hazard; handle polished specimens normally',
        'High-pressure metamorphic mineral — forms at pressures >0.4 GPa; indicator of subducted or deeply buried continental crust',
        'Major localities: Minas Gerais (Brazil), Nepal, Switzerland, Russia, Tanzania (orange), USA (North Carolina)',
      ],
      gaia_resonance: 'ClarusLens + QuantumNexus + AnchorPrism',
      safety_warning:  'Safe for water. H4.5–6.5 (variable — direction-dependent). DO NOT grind or sand without respiratory protection — fibrous aluminium silicate dust hazard. No acute toxicity from normal handling of polished or rough specimens.',
    },
  },

];

export default BATCH_C7;

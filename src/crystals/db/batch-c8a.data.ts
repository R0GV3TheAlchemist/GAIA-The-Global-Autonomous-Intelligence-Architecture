/**
 * src/crystals/db/batch-c8a.data.ts
 * GAIA-OS Crystal Database — Batch C-8A
 *
 * Entries:
 *   1. Chrysoprase    — Ni-bearing chalcedony; apple-green; trade name (variety)
 *   2. Cinnabar       — HgS; mercury sulphide; EXTREME TOXICITY
 *   3. Clear Quartz   — SiO₂; colourless quartz; Master Healer; trade name (variety)
 *   4. Cleavelandite  — platy Albite variety; pegmatite mineral; trade name
 *   5. Clinochlore    — (Mg,Fe)₅Al(AlSi₃)O₁₀(OH)₈; chlorite group; Kammererite variety
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-31
 *
 * SAFETY NOTE: Cinnabar (HgS) is an EXTREME mercury hazard — handle with gloves,
 * never in water, never crush or heat. All other entries in this batch are safe.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_C8A: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. CHRYSOPRASE
  // SiO₂ — Ni-bearing chalcedony variety; NOT an IMA-approved mineral species
  // Apple-green colour from nickel-bearing silicate inclusions (willemseite/népouite)
  // Named from Greek: chrysos (gold) + prason (leek) — gold-leek green
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Chrysoprase',
    mindat_id:    952,
    rruff_ids:    ['R040031'],
    last_synced:  '2026-05-31T00:00:00Z',
    trade_name:   true,
    color_layer:  'natural',
    yin_yang_pair: 'Prase (chlorite quartz)',

    physical: {
      id:           952,
      longid:       'chrysoprase',
      guid:         '',
      name:         'Chrysoprase (Ni-bearing chalcedony — SiO₂ variety)',
      ima_formula:  'SiO₂',
      mindat_formula: 'SiO2',
      ima_status:   'Not IMA approved — trade/variety name for Ni-bearing chalcedony',
      ima_year:     null,
      strunzten:    '4.DA.05',
      dana8ed:      '75.1.3.1',
      crystal_system: 'Trigonal (cryptocrystalline — no visible crystals)',
      hardness_min: 6.5,
      hardness_max: 7,
      specific_gravity_min: 2.58,
      specific_gravity_max: 2.64,
      cleavage:    'None (cryptocrystalline aggregate)',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Waxy', 'Dull'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Apple-green to deep emerald-green to turquoise-green. Colour from tiny inclusions of Ni-bearing layer silicates (willemseite, népouite, kerolite). Colour can fade in prolonged direct sunlight. The finest colour rivals imperial jade.',
      streak:      'White',
      fluorescence: 'None to weak green',
      ri_min:      1.530,
      ri_max:      1.540,
      birefringence: 0.004,
      optical_type: 'U',
      shortdesc:   'Chrysoprase — Ni-bearing apple-green chalcedony (SiO₂). Trade/variety name; NOT a separate IMA mineral species. Colour from nickel-bearing silicate micro-inclusions. H6.5–7. Named from Greek chrysos (gold) + prason (leek). Finest specimens from Marlborough Creek, Queensland, Australia. Colour may fade in direct sunlight.',
      updttime:    '2026-05-31T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-952.html',
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Chrysoprase',
      refractive_index: { n_mean: 1.535 },
      birefringence:   0.004,
      optical_sign:    '+',
      dispersion:      'Low',
      pleochroism:     'None (cryptocrystalline)',
      fluorescence_lw: 'None to weak green',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 500, max: 560 },
      spectra: ['R040031'],
    },

    color: {
      primary_color:         'Apple-green — the freshest, most luminous green in the chalcedony family',
      color_variants: [
        'Pale mint-green (low Ni — commonest)',
        'Apple-green (classic — medium Ni; most sought after)',
        'Deep emerald-green (high Ni — finest grade; rivals jade)',
        'Turquoise-green (blue-shifted Ni silicate composition)',
        'Yellowish-green (weathered or lower Ni)',
      ],
      dominant_wavelength_nm: 530,
      oklch:   { l: 0.72, c: 0.20, h: 145 },
      hex:     '#7ec87a',
      munsell: '7.5GY 6/8',
      color_temperature_k: null,
      psychological_effects: [
        'Apple-green is one of the most universally soothing colours — it sits at the boundary of yellow warmth and blue coolness',
        'Chrysoprase has a waxy translucency that gives it an almost organic, living quality — closer to jade than to glass',
        'The nickel origin of the colour is a chemical irony — nickel is usually toxic, but here it creates one of the most life-affirming greens in the mineral kingdom',
        'Fine chrysoprase can be mistaken for imperial jade — a single mineral chemistry producing two entirely different market perceptions',
        'Colour fading in sunlight is a teaching: the most vivid greens are also the most temporary — beauty and impermanence together',
      ],
      harmonics: {
        complementary_hue: 325,
        triadic_hues:      [25, 265],
        analogous_range:   [125, 165],
      },
    },

    metaphysical: {
      mineral_name:     'Chrysoprase',
      chakra_primary:   'Heart',
      chakra_secondary: ['Sacral', 'Solar Plexus', 'Higher Heart'],
      element:   ['Earth', 'Water'],
      planet:    ['Venus', 'Ceres', 'Moon'],
      archetype: ['The Apple-Green Heart', 'The Nickel Alchemist', 'The Leek-Gold Stone'],
      zodiac:    ['Taurus', 'Gemini', 'Libra'],
      numerology: 3,
      angel_number: 333,
      intention: 'My green is not borrowed from chlorophyll. It comes from nickel transformed — the toxic made luminous, the ordinary made sacred.',
      traditions: [
        'Named from Greek chrysos (gold) + prason (leek) — the gold-leek green; known since antiquity as a valued gemstone',
        'Ancient Greece and Rome — chrysoprase used for signet rings, intaglios, and decorative objects; Alexander the Great reportedly wore a chrysoprase girdle in battle',
        'Medieval Europe — confused with emerald; featured in royal jewellery and church treasures',
        'Frederick the Great of Prussia — chrysoprase from Szklary (Poland/Silesia) used extensively in the Sanssouci Palace decorations; a royal favourite in 18th century Prussia',
        'Modern crystal healing — primary Heart chakra stone for joy, optimism, and emotional healing; used to clear the heart of grief and open to new love',
        'Marlborough Creek, Queensland (Australia) — discovered 1965; finest apple-green quality; primary modern commercial source',
      ],
      properties: [
        'Trade/variety name — mineralogically Ni-bearing chalcedony (SiO₂); NOT a separate IMA mineral species',
        'Colour from Ni-bearing layer silicate micro-inclusions (willemseite Ni₃Si₄O₁₀(OH)₂, népouite, kerolite) — NOT from NiO as sometimes stated',
        'Colour may fade with prolonged direct sunlight or UV exposure — store away from strong light',
        'H6.5–7 — durable; suitable for jewellery',
        'Safe for water — SiO₂ base; chemically stable',
        'Major localities: Marlborough Creek (Queensland, Australia — finest quality), Szklary (Poland), Haneti (Tanzania), Yerlan (Kazakhstan), Goias (Brazil)',
        'Distinguished from jade by lower SG (2.58–2.64 vs jade 3.0–3.3) and waxy rather than greasy lustre',
      ],
      gaia_resonance: 'ViriditasHeart + ClarusLens + Noosphere',
      safety_warning:  'Safe for water. Keep out of prolonged direct sunlight — colour may fade. H6.5–7 — durable. No toxic elements in crystal form (nickel is incorporated in silicate lattice, not free ionic). Store away from UV.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. CINNABAR
  // HgS — mercury(II) sulphide; trigonal
  // Named from Persian zinjifrah / Arabic zinjafr — dragon's blood
  // Primary mercury ore; historically used as pigment (vermilion)
  // EXTREME TOXICITY — mercury compound
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Cinnabar',
    mindat_id:    1052,
    rruff_ids:    ['R040103'],
    last_synced:  '2026-05-31T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Stibnite',

    physical: {
      id:           1052,
      longid:       'cinnabar',
      guid:         '',
      name:         'Cinnabar',
      ima_formula:  'HgS',
      mindat_formula: 'HgS',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '2.CD.15',
      dana8ed:      '2.8.1.1',
      crystal_system: 'Trigonal',
      hardness_min: 2,
      hardness_max: 2.5,
      specific_gravity_min: 8.0,
      specific_gravity_max: 8.2,
      cleavage:    'Perfect prismatic on {10-10} — three directions',
      fracture:    'Uneven to subconchoidal',
      tenacity:    'Sectile',
      luster:      ['Adamantine', 'Metallic (massive form)'],
      diaphaneity: ['Transparent (thin crystals)', 'Translucent', 'Opaque (massive)'],
      colour:      'Brilliant scarlet-red to brick-red to brownish-red. The most vivid natural red of any ore mineral. Colour is intrinsic to the HgS structure. Ground to powder = vermilion pigment.',
      streak:      'Scarlet-red (diagnostic)',
      fluorescence: 'None',
      ri_min:      2.905,
      ri_max:      3.256,
      birefringence: 0.351,
      optical_type: 'U',
      shortdesc:   'Cinnabar — HgS, trigonal mercury sulphide. EXTREME TOXICITY — mercury compound. Primary mercury ore. Brilliant scarlet-red; adamantine lustre; scarlet streak. SG 8.0–8.2 — very heavy. Extraordinarily high RI (2.905–3.256) and birefringence (0.351). Historical vermilion pigment source. Major localities: Almadén (Spain), Huancavelica (Peru), Idrija (Slovenia).',
      updttime:    '2026-05-31T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-1052.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Cinnabar',
      refractive_index: { n_omega: 3.256, n_epsilon: 2.905 },
      birefringence:   0.351,
      optical_sign:    '-',
      dispersion:      'Extreme',
      pleochroism:     'Strong: deep scarlet / orange-red',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 615, max: 645 },
      spectra: ['R040103'],
    },

    color: {
      primary_color:         'Brilliant scarlet-red — the most vivid natural red in the ore mineral kingdom',
      color_variants: [
        'Scarlet-red (classic — fine crystals with adamantine lustre)',
        'Brick-red (massive form — lower lustre)',
        'Brownish-red (altered or impure)',
        'Vermilion red (powdered — the historic pigment form)',
        'Deep crimson (thick crystals)',
      ],
      dominant_wavelength_nm: 630,
      oklch:   { l: 0.45, c: 0.28, h: 28 },
      hex:     '#c41a1a',
      munsell: '7.5R 4/14',
      color_temperature_k: null,
      psychological_effects: [
        'Scarlet-red is one of the most psychologically activating colours — it triggers alertness, intensity, and urgency at a neurological level',
        'The adamantine lustre on red makes cinnabar crystals appear to glow from within — a brilliance that is literally dangerous',
        'The vermilion pigment ground from cinnabar painted the walls of Roman villas, illuminated medieval manuscripts, and coloured Chinese lacquer — history\'s most significant red',
        'The contradiction between the beauty and the toxicity is cinnabar\'s core teaching: not everything radiant is safe to hold',
        'Extraordinary RI (2.905–3.256) — among the highest of any mineral; the adamantine fire is a direct expression of this optical density',
      ],
      harmonics: {
        complementary_hue: 208,
        triadic_hues:      [148, 268],
        analogous_range:   [8, 48],
      },
    },

    metaphysical: {
      mineral_name:     'Cinnabar',
      chakra_primary:   'Root',
      chakra_secondary: ['Sacral', 'Earth Star'],
      element:   ['Fire', 'Earth', 'Metal'],
      planet:    ['Mars', 'Saturn', 'Mercury (planet)'],
      archetype: ['The Dragon\'s Blood', 'The Forbidden Red', 'The Alchemist\'s Mercury'],
      zodiac:    ['Scorpio', 'Aries', 'Capricorn'],
      numerology: 8,
      angel_number: 888,
      intention: 'I am the red that built empires and poisoned kings. My beauty is real. My danger is real. I hold both without apology.',
      traditions: [
        'Etymology — Persian zinjifrah / Arabic zinjafr — "dragon\'s blood"; the red so vivid it was named after mythological blood',
        'Almadén, Spain — the world\'s largest mercury mine; worked continuously for over 2,000 years; Romans extracted mercury here under brutal slave labour conditions',
        'Vermilion pigment — ground cinnabar (HgS) was the premier red pigment of the ancient world; used in Roman frescoes, medieval illuminated manuscripts, Chinese lacquer, and Mesoamerican murals',
        'Chinese alchemy (Daoism) — cinnabar (丹砂, dānshā) was a central alchemical substance; considered the essence of yang energy; Daoist alchemists consumed cinnabar preparations in attempts to achieve immortality — killing themselves in the process',
        'Mesoamerican tradition — cinnabar used as a red pigment and ritual substance in Maya and Aztec culture; found in royal tombs',
        'Feng Shui — cinnabar red used in Chinese decorative arts; considered highly auspicious despite the toxicity; used in carved cinnabar lacquerware',
      ],
      properties: [
        'IMA approved — formula HgS; trigonal mercury sulphide; primary mercury ore mineral',
        'EXTREME TOXICITY — mercury compound; all forms of mercury are toxic to the nervous system; DO NOT handle without gloves; DO NOT heat or crush (mercury vapour is released); NEVER in water',
        'SG 8.0–8.2 — extremely heavy for its size; diagnostic by weight alone',
        'Extraordinarily high RI (2.905–3.256) and birefringence (0.351) — among the highest of any mineral; adamantine to near-metallic lustre on crystal faces',
        'Scarlet streak — one of the most diagnostic properties; always leaves a vivid scarlet-red mark on streak plate',
        'H2–2.5 — very soft; sectile; crystals are fragile',
        'Major localities: Almadén (Spain — largest historical mine), Idrija (Slovenia), Huancavelica (Peru), Guizhou Province (China), New Almadén (CA, USA)',
      ],
      gaia_resonance: 'SovereignCore + AnchorPrism',
      safety_warning:  '🚨 EXTREME TOXICITY — mercury sulphide (HgS). NEVER use in water. Handle with nitrile gloves. Do NOT heat, crush, or grind — mercury vapour is released. Wash hands thoroughly after any contact. Keep away from children, food, and pets. Display in sealed case. Do NOT make elixirs under any circumstances.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. CLEAR QUARTZ
  // SiO₂ — pure colourless quartz; variety name / trade name
  // The "Master Healer" — most documented crystal in the healing canon
  // Trigonal; piezoelectric; universally safe
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Clear Quartz',
    mindat_id:    3337,
    rruff_ids:    ['R040031'],
    last_synced:  '2026-05-31T00:00:00Z',
    trade_name:   true,
    color_layer:  'natural',
    yin_yang_pair: 'Smoky Quartz',

    physical: {
      id:           3337,
      longid:       'clear-quartz',
      guid:         '',
      name:         'Clear Quartz (colourless SiO₂ — variety name)',
      ima_formula:  'SiO₂',
      mindat_formula: 'SiO2',
      ima_status:   'A (variety name — IMA mineral is Quartz)',
      ima_year:     null,
      strunzten:    '4.DA.05',
      dana8ed:      '75.1.3.1',
      crystal_system: 'Trigonal',
      hardness_min: 7,
      hardness_max: 7,
      specific_gravity_min: 2.65,
      specific_gravity_max: 2.65,
      cleavage:    'None (very weak rhombohedral parting)',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Colourless — water-clear to slightly milky white. Absolute clarity in the finest specimens. Milkiness from fluid inclusions or micro-fractures. The defining quartz form.',
      streak:      'White',
      fluorescence: 'None to weak white-blue',
      ri_min:      1.544,
      ri_max:      1.553,
      birefringence: 0.009,
      optical_type: 'U',
      shortdesc:   'Clear Quartz — colourless SiO₂; variety name for transparent, colourless quartz. H7. Piezoelectric — foundation of modern timekeeping and electronics. The "Master Healer" of crystal healing. Water-clear to faintly milky. Major localities: Brazil, Arkansas (USA), Madagascar, Alps. Herkimer Diamond = doubly-terminated clear quartz from New York.',
      updttime:    '2026-05-31T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-3337.html',
      piezoelectric:     true,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Clear Quartz',
      refractive_index: { n_omega: 1.553, n_epsilon: 1.544 },
      birefringence:   0.009,
      optical_sign:    '+',
      dispersion:      '0.013',
      pleochroism:     'None (colourless)',
      fluorescence_lw: 'None to weak blue-white',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R040031'],
    },

    color: {
      primary_color:         'Colourless — the absence of colour as a complete optical statement',
      color_variants: [
        'Water-clear (finest quality — no inclusions, no fractures)',
        'Slightly milky (fluid inclusion clouds — most common)',
        'Faintly smoky (trace irradiation — transitional to Smoky Quartz)',
        'Rainbow inclusions (internal fractures acting as diffraction gratings)',
        'Included varieties: Rutilated, Tourmalinated, Chlorite Phantom, Garden Quartz',
        'Herkimer Diamond — doubly-terminated, exceptionally clear, from Herkimer County NY',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.97, c: 0.01, h: 90 },
      hex:     '#f8f8f8',
      munsell: 'N 9.5/',
      color_temperature_k: null,
      psychological_effects: [
        'Absolute clarity — a perfect clear quartz point transmits light without distortion; this is visually and psychologically a symbol of pure potential',
        'The colourless state is not emptiness — it is all colours at once; clear quartz contains the entire visible spectrum in undifferentiated form',
        'Doubly-terminated crystals (Herkimers) are complete geometric objects — both ends tapered to points — with no attachment point; they feel free and sovereign',
        'Piezoelectricity makes clear quartz literally responsive to pressure — it generates voltage when squeezed; it is physically reactive to the world',
        'The ubiquity of quartz in the Earth\'s crust — it is everywhere — means working with clear quartz is working with the structural foundation of the lithosphere',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Clear Quartz',
      chakra_primary:   'Crown',
      chakra_secondary: ['All chakras — clear quartz amplifies every centre equally'],
      element:   ['Akasha', 'All elements'],
      planet:    ['Sun', 'Moon', 'All planets'],
      archetype: ['The Master Healer', 'The Universal Amplifier', 'The Mirror of Heaven'],
      zodiac:    ['All signs'],
      numerology: 4,
      angel_number: 1111,
      intention: 'I hold no colour of my own. I amplify yours. I am the stone that becomes whatever healing requires.',
      traditions: [
        'Ancient worldwide — quartz crystals found in archaeological sites on every inhabited continent; used as tools, ornaments, and ritual objects since the Palaeolithic',
        'Aboriginal Australian tradition — clear quartz (maban) is one of the most sacred substances; carried by shamans (kurdaitcha men) as a vehicle for spiritual power',
        'Ancient Greece — the word "crystal" derives from Greek krystallos (ice); Greeks believed clear quartz was permanently frozen water that could never melt',
        'Japanese tradition — clear quartz (水晶, suisho — "water crystal") associated with purity, perfection, and the dragon; the preferred material for crystal ball scrying',
        'Electronics — quartz piezoelectricity discovered 1880 (Curie brothers); quartz oscillators now regulate virtually all digital timekeeping globally; modern civilisation runs on quartz frequency',
        'Modern crystal healing — the "Master Healer"; used to amplify intentions, programme other stones, and clear all energy centres',
      ],
      properties: [
        'Variety name: Clear Quartz — mineralogically colourless quartz (SiO₂); IMA mineral is Quartz',
        'PIEZOELECTRIC — generates electrical potential under mechanical stress; foundation of quartz watches, oscillators, sonar, and pressure sensors',
        'H7 — hard and durable; suitable for all forms of jewellery and everyday use',
        'Safe for water — pure SiO₂; chemically inert',
        'Most abundant mineral in the Earth\'s continental crust',
        'Herkimer Diamond: doubly-terminated clear quartz from Herkimer County, NY — not a diamond; no relation to diamond mineralogy',
        'Major localities: Minas Gerais (Brazil — largest volumes), Hot Springs (Arkansas, USA — finest clarity), Madagascar, Alps (Switzerland/Austria), Himalayas',
      ],
      gaia_resonance: 'ClarusLens + QuantumNexus + Noosphere + SovereignCore + ViriditasHeart + AnchorPrism',
      safety_warning:  '⚠️ PIEZOELECTRIC — keep away from hard drives, pacemakers, and sensitive electronics. Safe for water. No toxic elements. H7 — durable. The universal safe crystal.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. CLEAVELANDITE
  // Platy variety of Albite — NaAlSi₃O₈; trade/variety name
  // Named after Parker Cleaveland (1780–1858), American mineralogist
  // Classic pegmatite mineral — fan-shaped platy rosettes
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Cleavelandite',
    mindat_id:    118,
    rruff_ids:    ['R040068'],
    last_synced:  '2026-05-31T00:00:00Z',
    trade_name:   true,
    color_layer:  'natural',
    yin_yang_pair: 'Microcline (K-feldspar)',

    physical: {
      id:           118,
      longid:       'cleavelandite',
      guid:         '',
      name:         'Cleavelandite (platy Albite variety — NaAlSi₃O₈)',
      ima_formula:  'NaAlSi₃O₈',
      mindat_formula: 'NaAlSi3O8',
      ima_status:   'A (variety name — IMA mineral is Albite)',
      ima_year:     null,
      strunzten:    '9.FA.35',
      dana8ed:      '76.1.3.1',
      crystal_system: 'Triclinic',
      hardness_min: 6,
      hardness_max: 6.5,
      specific_gravity_min: 2.60,
      specific_gravity_max: 2.65,
      cleavage:    'Perfect on {001}, good on {010} — two directions; characteristic feldspar cleavage',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Pearly (on cleavage)'],
      diaphaneity: ['Transparent', 'Translucent', 'Opaque'],
      colour:      'White to colourless, pale grey, pale yellowish. Fan-shaped or book-like platy aggregates. Pearly to vitreous lustre on cleavage surfaces. Characteristic blade/plate habit distinguishes it from other albite forms.',
      streak:      'White',
      fluorescence: 'None to weak',
      ri_min:      1.527,
      ri_max:      1.536,
      birefringence: 0.009,
      optical_type: 'B',
      shortdesc:   'Cleavelandite — platy variety of Albite (NaAlSi₃O₈); trade/variety name. Named after Parker Cleaveland (1780–1858). Triclinic feldspar. H6–6.5. White fan-shaped platy aggregates in granitic pegmatites. Major localities: Minas Gerais (Brazil), Pala (CA), Nuristan (Afghanistan). Classic matrix mineral for tourmaline, topaz, and aquamarine.',
      updttime:    '2026-05-31T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-118.html',
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Cleavelandite (Albite variety)',
      refractive_index: { n_alpha: 1.527, n_beta: 1.531, n_gamma: 1.536 },
      birefringence:   0.009,
      optical_sign:    '+',
      dispersion:      '0.012',
      pleochroism:     'None (colourless to white)',
      fluorescence_lw: 'None to weak',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R040068'],
    },

    color: {
      primary_color:         'White — the clean architectural white of pegmatite feldspar',
      color_variants: [
        'Pure white (most common — fine platy masses)',
        'Colourless transparent (fine thin plates)',
        'Pale grey (minor inclusions)',
        'Pale yellowish-white (slight alteration)',
        'Pearlescent white (cleavage surface — most common display form)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.94, c: 0.02, h: 90 },
      hex:     '#f0eee8',
      munsell: 'N 9/',
      color_temperature_k: null,
      psychological_effects: [
        'The fan/book habit of cleavelandite plates — overlapping blades spreading outward — is one of the most architecturally elegant growth forms in the mineral kingdom',
        'White feldspar as background matrix for vivid tourmaline, aquamarine, or topaz creates a visual conversation between the quiet and the brilliant',
        'Pearly lustre on cleavage surfaces gives cleavelandite a soft inner light — not the brilliance of quartz, but something gentler and more reflective',
        'Named for a person (Parker Cleaveland) rather than a place or property — a mineral with a human biographical connection',
        'As the sodium end-member of the feldspar series (albite = NaAlSi₃O₈), cleavelandite is the most Na-rich and least K-rich of the common feldspars — a chemical position as much as a physical form',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Cleavelandite',
      chakra_primary:   'Crown',
      chakra_secondary: ['Third Eye', 'Throat'],
      element:   ['Air', 'Akasha'],
      planet:    ['Moon', 'Mercury', 'Uranus'],
      archetype: ['The Pegmatite Scholar', 'The White Fan', 'Parker\'s Stone'],
      zodiac:    ['Gemini', 'Aquarius', 'Virgo'],
      numerology: 7,
      angel_number: 777,
      intention: 'I am the quiet white page on which the vivid crystals write. Without me, the tourmaline has no ground to grow from.',
      traditions: [
        'Named 1823 after Parker Cleaveland (1780–1858) — American mineralogist, professor at Bowdoin College; author of the first systematic American mineralogy textbook',
        'Pegmatite tradition — cleavelandite is the classic matrix mineral of granitic pegmatites worldwide; most famous tourmaline, aquamarine, and topaz specimens sit on cleavelandite matrices',
        'Pala, California — the famous Pala gem pegmatite district produced spectacular cleavelandite matrices with kunzite and tourmaline in the early 20th century',
        'Afghanistan (Nuristan) — cleavelandite-rich pegmatites produce some of the finest tourmaline-on-matrix specimens in the world',
        'Modern crystal healing — used for clarity, mental structure, and as a supporting/amplifying matrix stone; valued for its association with clarity and scholarly thought',
      ],
      properties: [
        'Variety name: Cleavelandite — platy variety of Albite (NaAlSi₃O₈); triclinic feldspar; named for characteristic platy/bladed habit',
        'Distinguished from other albite forms by its pronounced platy habit — fan-shaped, book-like, or lamellar aggregates',
        'Classic matrix mineral for tourmaline, aquamarine, topaz, morganite, and other pegmatite gems',
        'H6–6.5 — moderately hard; suitable for display specimens',
        'Safe for water — sodium aluminium silicate; chemically stable',
        'Major localities: Minas Gerais (Brazil — finest gem inclusions), Pala (CA, USA), Nuristan (Afghanistan), Himalayan pegmatites',
      ],
      gaia_resonance: 'ClarusLens + Noosphere',
      safety_warning:  'Safe for water. No toxic elements. H6–6.5 — moderately hard. Handle with normal care. Store separately from harder minerals to avoid cleavage surface damage.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. CLINOCHLORE
  // (Mg,Fe²⁺)₅Al(Si₃Al)O₁₀(OH)₈ — chlorite group phyllosilicate; IMA approved
  // Named from Greek: klino (oblique) + chloros (green) — oblique green
  // Kammererite = pink-purple Cr-bearing variety
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Clinochlore',
    mindat_id:    1070,
    rruff_ids:    ['R060535'],
    last_synced:  '2026-05-31T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Charoite',

    physical: {
      id:           1070,
      longid:       'clinochlore',
      guid:         '',
      name:         'Clinochlore',
      ima_formula:  '(Mg,Fe²⁺)₅Al(Si₃Al)O₁₀(OH)₈',
      mindat_formula: '(Mg,Fe++)5Al(Si3Al)O10(OH)8',
      ima_status:   'A',
      ima_year:     1851,
      strunzten:    '9.EC.55',
      dana8ed:      '71.4.1.3',
      crystal_system: 'Monoclinic',
      hardness_min: 2,
      hardness_max: 2.5,
      specific_gravity_min: 2.55,
      specific_gravity_max: 2.75,
      cleavage:    'Perfect basal on {001} — flexible but inelastic plates',
      fracture:    'Uneven (across cleavage)',
      tenacity:    'Flexible but inelastic (platy cleavage sheets)',
      luster:      ['Vitreous', 'Pearly (on cleavage)', 'Waxy'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Pale to dark green (standard form — Mg-rich); pink to rose-red to purple (Kammererite — Cr-bearing variety). Green from Fe²⁺; pink-purple from Cr³⁺ substitution. Both forms occur as hexagonal plates or scaly aggregates.',
      streak:      'White to pale green',
      fluorescence: 'None to weak',
      ri_min:      1.571,
      ri_max:      1.588,
      birefringence: 0.006,
      optical_type: 'B',
      shortdesc:   'Clinochlore — (Mg,Fe²⁺)₅Al(Si₃Al)O₁₀(OH)₈; monoclinic chlorite group phyllosilicate. IMA 1851. H2–2.5 — very soft. Perfect basal cleavage. Green (standard) or pink-purple (Kammererite — Cr³⁺ variety). Major localities: Outokumpu (Finland), Ala Valley (Italy), Saranova (Russia — Kammererite), Turkey. Safe for water.',
      updttime:    '2026-05-31T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-1070.html',
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Clinochlore',
      refractive_index: { n_alpha: 1.571, n_beta: 1.577, n_gamma: 1.588 },
      birefringence:   0.006,
      optical_sign:    '+',
      dispersion:      'Weak',
      pleochroism:     'Moderate: green / pale yellow-green (standard); pink / pale pink (Kammererite)',
      fluorescence_lw: 'None to weak',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 500, max: 560 },
      spectra: ['R060535'],
    },

    color: {
      primary_color:         'Pale to mid green (standard) — or vivid pink-purple (Kammererite)',
      color_variants: [
        'Pale yellowish-green (low Fe)',
        'Mid green (standard Mg-Fe clinochlore)',
        'Dark green (high Fe²⁺)',
        'White to colourless (pure Mg end-member)',
        'Pink to rose-red (Kammererite — low Cr³⁺)',
        'Purple-red (Kammererite — high Cr³⁺ — most prized)',
      ],
      dominant_wavelength_nm: 535,
      oklch:   { l: 0.62, c: 0.15, h: 155 },
      hex:     '#6aaa7a',
      munsell: '2.5G 6/6',
      color_temperature_k: null,
      psychological_effects: [
        'Kammererite\'s pink-purple on chrome is one of the most unexpected colour combinations in mineralogy — the same element (Cr) that makes emerald green makes Kammererite pink',
        'The platy hexagonal habit creates natural geometric forms — six-sided plates that stack and overlap like botanical scales',
        'H2–2.5 means clinochlore is among the softest of the collector minerals — the plates flex under pressure without breaking',
        'Found as inclusions in quartz (Chlorite Quartz / Garden Quartz — C5) — clinochlore provides the green ghostly phantoms inside those crystals',
        'The chlorite group name (from Greek chloros, green) connects clinochlore to the entire chemical identity of green in phyllosilicate mineralogy',
      ],
      harmonics: {
        complementary_hue: 335,
        triadic_hues:      [275, 35],
        analogous_range:   [135, 175],
      },
    },

    metaphysical: {
      mineral_name:     'Clinochlore',
      chakra_primary:   'Heart',
      chakra_secondary: ['Crown', 'Third Eye'],
      element:   ['Earth', 'Water', 'Air'],
      planet:    ['Venus', 'Moon', 'Earth'],
      archetype: ['The Oblique Green', 'The Kammererite Surprise', 'The Phantom Maker'],
      zodiac:    ['Taurus', 'Libra', 'Pisces'],
      numerology: 6,
      angel_number: 666,
      intention: 'I am the green inside the quartz phantom. I am the colour the crystal remembers from an earlier time.',
      traditions: [
        'Named 1851 by William Hallowes Miller — from Greek klino (oblique) + chloros (green); for the oblique optical extinction in green platy crystals',
        'Kammererite variety — named after August Alexander Kämmerer (1789–1858), Russian mining official; the pink-purple Cr-bearing variety from Saranova, Ural Mountains, Russia',
        'Chlorite phantom quartz — clinochlore and other chlorite minerals coat quartz crystal surfaces during pauses in growth, creating green phantom outlines inside clear quartz (see batch-c5: Chlorite Quartz)',
        'Ala Valley, Italy — produces classic transparent green clinochlore crystals on matrix; a collector classic',
        'Modern crystal healing — clinochlore used for heart healing, compassion, and connection to nature consciousness; Kammererite used for spiritual elevation and crown-heart integration',
      ],
      properties: [
        'IMA 1851 — formula (Mg,Fe²⁺)₅Al(Si₃Al)O₁₀(OH)₈; monoclinic phyllosilicate; chlorite group',
        'Two main collector varieties: standard green clinochlore and Kammererite (pink-purple, Cr³⁺-bearing)',
        'H2–2.5 — very soft; handle gently; separate from harder minerals in storage',
        'Perfect basal cleavage — yields flexible but inelastic thin plates (unlike muscovite which is elastic)',
        'Safe for water — magnesium aluminium silicate hydroxide; no toxic elements',
        'Forms green inclusions in quartz (Chlorite Quartz / Garden Quartz / Phantom Quartz)',
        'Major localities: Outokumpu (Finland), Ala Valley (Italy), Saranova (Ural, Russia — Kammererite), Biga Peninsula (Turkey — Kammererite), Tirol (Austria)',
      ],
      gaia_resonance: 'ViriditasHeart + Noosphere + AnchorPrism',
      safety_warning:  'Safe for water. No toxic elements. H2–2.5 — very soft; handle with care. Perfect basal cleavage — keep away from pressure and harder minerals. Store carefully to preserve platy crystal habit.',
    },
  },

];

export default BATCH_C8A;

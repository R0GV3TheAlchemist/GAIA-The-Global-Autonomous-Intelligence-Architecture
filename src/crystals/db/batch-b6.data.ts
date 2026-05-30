/**
 * src/crystals/db/batch-b6.data.ts
 * GAIA-OS Crystal Database — Batch B-6
 *
 * Entries:
 *   1. Blue Tiger's Eye (Hawk's Eye)
 *   2. Blue Topaz
 *   3. Blue Tourmaline (Indicolite)
 *   4. Boji Stones (Kansas Pop Rocks)
 *   5. Bornite (Peacock Ore)
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-29
 *
 * NOTE: A batch of remarkable scientific range. Blue Tiger's Eye is chatoyant
 * quartz with crocidolite pseudomorphs — the original hawk's eye before iron
 * oxidation turns it golden. Blue Topaz is the world's most commercially
 * produced treated gemstone — nearly all market blue topaz is irradiated.
 * Blue Tourmaline (Indicolite) is the rarest colour of the elbaite tourmaline
 * family. Boji Stones are a proprietary trade name for septarian concretions
 * from Kansas — legally trademarked. Bornite is the iridescent copper iron
 * sulphide whose peacock tarnish is one of the most spectacular in mineralogy.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_B6: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. BLUE TIGER'S EYE (HAWK'S EYE)
  // Chatoyant quartz pseudomorphed after crocidolite (blue asbestos)
  // The original form — before iron oxidation creates golden Tiger's Eye
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        "Blue Tiger's Eye",
    mindat_id:   26723,
    rruff_ids:   ['R040031'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: "Golden Tiger's Eye",

    physical: {
      id:           26723,
      longid:       'blue-tigers-eye',
      guid:         '',
      name:         "Quartz (Blue Tiger's Eye / Hawk's Eye — chatoyant quartz pseudomorphed after crocidolite)",
      ima_formula:  'SiO₂',
      mindat_formula: 'SiO2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '4.DA.05',
      dana8ed:      '75.1.3.1',
      crystal_system: 'Trigonal (pseudomorphic fibrous aggregate)',
      hardness_min: 7,
      hardness_max: 7,
      specific_gravity_min: 2.64,
      specific_gravity_max: 2.65,
      cleavage:    'None (fibrous pseudomorph)',
      fracture:    'Fibrous to splintery',
      tenacity:    'Brittle',
      luster:      ['Silky', 'Vitreous'],
      diaphaneity: ['Opaque'],
      colour:      'Blue-grey to blue-green — retained blue crocidolite fibre colour before complete iron oxidation. Silky chatoyancy (cat\'s eye effect) along fibre orientation.',
      streak:      'White',
      fluorescence: 'None',
      ri_min:      1.544,
      ri_max:      1.553,
      birefringence: 0.009,
      optical_type: 'U',
      shortdesc:   "Blue Tiger's Eye (Hawk's Eye) — chatoyant quartz pseudomorphed after crocidolite (blue asbestos fibres). The blue precursor to golden Tiger's Eye — iron oxidation of crocidolite fibres turns blue hawk's eye into golden tiger's eye. Primary source: Northern Cape, South Africa.",
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-26723.html',
      piezoelectric:    true,
      safe_for_water:   true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    "Blue Tiger's Eye (Hawk's Eye)",
      refractive_index: { n_omega: 1.553, n_epsilon: 1.544 },
      birefringence:   0.009,
      optical_sign:    '+',
      dispersion:      '0.013',
      pleochroism:     'Weak — chatoyancy dominates over pleochroism',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 450, max: 490 },
      spectra: ['R040031'],
    },

    color: {
      primary_color:          'Blue-grey to blue-green with silky chatoyancy',
      color_variants:         [
        'Blue-grey with silver chatoyant band (classic hawk\'s eye)',
        'Blue-green with strong silky lustre',
        'Transitional blue-gold (partial iron oxidation — rare mixed form)',
        'Deep navy blue (fresh, unoxidised — rarer)',
      ],
      dominant_wavelength_nm: 475,
      oklch:   { l: 0.38, c: 0.08, h: 240 },
      hex:     '#4a5f78',
      munsell: '5B 4/4',
      color_temperature_k:    null,
      psychological_effects:  [
        'The chatoyant band that moves with the light is one of the most hypnotic optical effects in the mineral kingdom',
        'The cool blue-grey registers very differently from the warm golden — more composed, observant, hawk-like rather than lion-like',
        "The silky, rolling light evokes a predator's eye scanning for detail — precision perception",
        'The knowledge that you are holding the precursor state to tiger\'s eye — before transformation — is its own teaching',
        'Encourages the hawk perspective: elevated, wide, clear — seeing patterns others miss from below',
      ],
      harmonics: {
        complementary_hue: 60,
        triadic_hues:      [0, 120],
        analogous_range:   [220, 260],
      },
    },

    metaphysical: {
      mineral_name:     "Blue Tiger's Eye",
      chakra_primary:   'Third Eye',
      chakra_secondary: ['Throat', 'Solar Plexus'],
      element:   ['Air', 'Storm'],
      planet:    ['Saturn', 'Mercury'],
      archetype: ['The Hawk', 'The Observer', 'The Strategic Mind'],
      zodiac:    ['Capricorn', 'Aquarius', 'Gemini'],
      numerology: 7,
      angel_number: 777,
      intention: 'I see clearly from a place of calm elevation. My perception is sharp and my mind composed.',
      traditions: [
        'Western crystal healing — the hawk\'s eye as the cool, strategic counterpart to the golden tiger\'s eye',
        'South African origin — Northern Cape province is the primary world source for both hawk\'s eye and tiger\'s eye',
        'Ancient Egyptian tradition — cat\'s eye and chatoyant stones associated with the eye of Ra and divine sight',
      ],
      properties: [
        "Trade names: Hawk's Eye and Blue Tiger's Eye — both refer to chatoyant quartz pseudomorphed after crocidolite",
        "Blue Tiger's Eye is the geological precursor to golden Tiger's Eye — the blue crocidolite fibres oxidise to brown/gold iron oxides over geological time, converting hawk's eye to tiger's eye",
        'The chatoyancy (cat\'s eye effect) comes from the parallel alignment of the pseudomorphic fibres — light reflects off the fibre array like a cat\'s eye',
        'Northern Cape, South Africa is the dominant global source — the Griquatown West formation',
        'Crocidolite (blue asbestos) fibres are the template — in finished, polished specimens the fibres are silicified and safely encapsulated in quartz',
        'H7 and good toughness — durable for jewellery and daily use',
        'Piezoelectric as all quartz — keep away from hard drives and sensitive electronics',
        "The yin pair with golden Tiger's Eye: hawk (cool observation, elevated perspective) and tiger (warm courage, grounded action)",
      ],
      gaia_resonance: 'ClarusLens + SovereignCore',
      safety_warning: "\u26a0\ufe0f CROCIDOLITE PRECURSOR NOTE — Blue Tiger's Eye contains pseudomorphic crocidolite (blue asbestos) fibres encapsulated in silica. In polished, tumbled, or cabochon form the fibres are safely locked in quartz and safe to handle. Do NOT cut, sand, grind, or drill without respiratory protection — cutting releases fibre dust which is a serious inhalation hazard. Safe for water in polished form. Keep away from hard drives (piezoelectric).",
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. BLUE TOPAZ
  // Aluminium fluoro-silicate — the world's most commercially treated gemstone
  // Nearly all market blue topaz is irradiated and heat-treated colourless topaz
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Blue Topaz',
    mindat_id:   3996,
    rruff_ids:   ['R050118'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'treated',
    yin_yang_pair: 'Imperial Topaz',

    physical: {
      id:           3996,
      longid:       'blue-topaz',
      guid:         '',
      name:         'Topaz (blue colour variety — natural or irradiation/heat treated)',
      ima_formula:  'Al₂(SiO₄)(F,OH)₂',
      mindat_formula: 'Al2(SiO4)(F,OH)2',
      ima_status:   'A',
      ima_year:     1737,
      strunzten:    '9.AF.35',
      dana8ed:      '52.3.3.1',
      crystal_system: 'Orthorhombic',
      hardness_min: 8,
      hardness_max: 8,
      specific_gravity_min: 3.49,
      specific_gravity_max: 3.57,
      cleavage:    'Perfect basal on {001} — the single most important property for cutting; creates flat cleavage faces',
      fracture:    'Subconchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Colourless to pale blue (natural) — deep Sky Blue, Swiss Blue, or London Blue (irradiation + heat treatment)',
      streak:      'White',
      fluorescence: 'Weak yellow or orange under LW UV; inert under SW',
      ri_min:      1.609,
      ri_max:      1.643,
      birefringence: 0.010,
      optical_type: 'B',
      shortdesc:   'Blue Topaz — topaz in blue colour, either natural (rare, pale) or treated (irradiation + heat — the global standard for commercial blue topaz). H8 — one of the hardest gemstones. November/December birthstone (blue topaz). Perfect basal cleavage.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-3996.html',
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Blue Topaz',
      refractive_index: { n_alpha: 1.609, n_beta: 1.611, n_gamma: 1.619 },
      birefringence:   0.010,
      optical_sign:    '+',
      dispersion:      '0.014',
      pleochroism:     'Weak to moderate: pale blue / very pale blue / colourless',
      fluorescence_lw: 'Weak yellow or orange',
      fluorescence_sw: 'Inert',
      phosphorescence: null,
      visible_wavelength_nm: { min: 460, max: 500 },
      spectra: ['R050118'],
    },

    color: {
      primary_color:          'Blue — from pale sky to deep London blue',
      color_variants:         [
        'Sky Blue (lightest commercial grade — pale, icy blue)',
        'Swiss Blue (medium bright blue — most popular commercial grade)',
        'London Blue (deepest, darkest — steel blue with slight grey)',
        'Natural blue topaz (extremely pale, very rare)',
        'Cobalt-treated blue topaz (Co diffusion — vivid intense blue)',
      ],
      dominant_wavelength_nm: 485,
      oklch:   { l: 0.55, c: 0.18, h: 238 },
      hex:     '#5b9bd5',
      munsell: '7.5B 6/8',
      color_temperature_k:    null,
      psychological_effects:  [
        'The pure, clean blue of sky blue and Swiss blue topaz is one of the most universally appealing colours in gemology',
        'The clarity and transparency of faceted blue topaz creates a brilliance that maximises the psychological impact of the blue',
        'London blue\'s deeper, steelier tone is more contemplative and authoritative than the lighter grades',
        'The extreme hardness (H8) communicates permanence and trustworthiness — a stone that will not be easily damaged',
        'The knowledge of the treatment history creates interesting questions about natural vs. transformed beauty',
      ],
      harmonics: {
        complementary_hue: 58,
        triadic_hues:      [358, 118],
        analogous_range:   [218, 258],
      },
    },

    metaphysical: {
      mineral_name:     'Blue Topaz',
      chakra_primary:   'Throat',
      chakra_secondary: ['Third Eye'],
      element:   ['Air', 'Water'],
      planet:    ['Jupiter', 'Mercury'],
      archetype: ['The Clear Speaker', 'The Truthful Mind', 'The Articulator'],
      zodiac:    ['Sagittarius', 'Virgo', 'Gemini'],
      numerology: 3,
      angel_number: 333,
      intention: 'I speak my highest truth with clarity, confidence, and grace.',
      traditions: [
        'Western crystal healing — Throat chakra and clear communication',
        'November/December birthstone (traditional and modern lists — blue topaz is the modern December birthstone alongside tanzanite and turquoise)',
        'Named possibly from Sanskrit tapas (fire/heat) or from the island of Topazios (Red Sea)',
        'Ancient Egyptian and Roman traditions — topaz associated with the sun god Ra and Jupiter',
        'Medieval European tradition — topaz believed to cool anger and increase wisdom',
      ],
      properties: [
        'IMA-recognised since 1737 — one of the longest-recognised gem minerals',
        'H8 — one of the hardest gemstones; harder than quartz (H7), softer than corundum (H9) and diamond (H10)',
        'Perfect basal cleavage on {001} — the most important cutting and handling consideration; a knock on the basal face can cleave the stone',
        'Nearly ALL commercial blue topaz is irradiated colourless topaz — neutron or electron irradiation followed by heat treatment creates the blue colour centres',
        'Three commercial grades: Sky Blue (lightest), Swiss Blue (medium, brightest), London Blue (deepest, darkest)',
        'Natural blue topaz does exist but is very pale and extremely rare — almost all deep blue specimens are treated',
        'Cobalt (Co) diffusion treatment creates an intense, vivid blue that is a stable alternative to irradiation treatment',
        'Modern December birthstone alongside tanzanite and turquoise — November birthstone is the golden/imperial variety',
        'The yin pair with imperial topaz: clear blue communication vs. warm golden self-actualisation',
      ],
      gaia_resonance: 'ClarusLens + Noosphere',
      safety_warning: '\u26a0\ufe0f CLEAVAGE WARNING — perfect basal cleavage on {001}; a sharp blow to the basal face can cleave the stone cleanly. Store and handle with care. Treated specimens (irradiation): the treatment is permanent and stable — no radiation risk in finished gems (regulatory compliance is standard practice). Safe for water. Avoid ultrasonic cleaning — cleavage risk.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. BLUE TOURMALINE (INDICOLITE)
  // Elbaite or fluor-elbaite — the rarest colour of the gem tourmaline family
  // Named from Latin indicum (indigo) — a true gemological rarity
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Blue Tourmaline',
    mindat_id:   2027,
    rruff_ids:   ['R050524'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  false,
    color_layer: 'natural',
    yin_yang_pair: 'Pink Tourmaline',

    physical: {
      id:           2027,
      longid:       'indicolite',
      guid:         '',
      name:         'Indicolite (Blue Tourmaline — blue gemmy variety of elbaite or fluor-elbaite)',
      ima_formula:  'Na(Li₁.₅Al₁.₅)Al₆(Si₆O₁₈)(BO₃)₃(OH)₃(OH)',
      mindat_formula: 'Na(Li1.5Al1.5)Al6(Si6O18)(BO3)3(OH)3(OH)',
      ima_status:   'A',
      ima_year:     1819,
      strunzten:    '9.CK.05',
      dana8ed:      '61.3.1.2',
      crystal_system: 'Trigonal',
      hardness_min: 7,
      hardness_max: 7.5,
      specific_gravity_min: 2.98,
      specific_gravity_max: 3.10,
      cleavage:    'Indistinct on {11−20} and {10−10}',
      fracture:    'Uneven to conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Blue to blue-green — from pale cerulean to deep inky blue; colour from Fe²⁺→Fe³⁺ charge transfer',
      streak:      'White',
      fluorescence: 'None to very weak',
      ri_min:      1.620,
      ri_max:      1.640,
      birefringence: 0.020,
      optical_type: 'U',
      shortdesc:   'Indicolite — blue gemmy tourmaline, typically elbaite or fluor-elbaite. Named from Latin indicum (indigo). The rarest and most valuable colour of gem tourmaline. Strongly pleochroic: blue / blue-green from two directions. Strongly piezoelectric and pyroelectric.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-2027.html',
      piezoelectric:    true,
      safe_for_water:   true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name: 'Blue Tourmaline (Indicolite)',
      refractive_index: { n_omega: 1.640, n_epsilon: 1.620 },
      birefringence:   0.020,
      optical_sign:    '-',
      dispersion:      '0.017',
      pleochroism:     'Strong dichroic: blue / blue-green (characteristic and diagnostic)',
      fluorescence_lw: 'None to very weak',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 450, max: 490 },
      spectra: ['R050524'],
    },

    color: {
      primary_color:          'Blue to blue-green — from pale cerulean to deep inky blue',
      color_variants:         [
        'Pale cerulean blue (lighter, more common)',
        'Medium teal-blue (most popular in jewellery)',
        'Deep inky blue (rare — resembles fine sapphire)',
        'Neon blue-green (Paraiba-type indicolite — copper-bearing, extremely rare)',
        'Blue-violet (very rare)',
      ],
      dominant_wavelength_nm: 480,
      oklch:   { l: 0.42, c: 0.20, h: 245 },
      hex:     '#2e6b9e',
      munsell: '5PB 4/10',
      color_temperature_k:    null,
      psychological_effects:  [
        'The blue of indicolite has an electric, saturated quality that reads as deeply rare — the eye recognises it as exceptional',
        'Strong pleochroism means the stone appears to shift between blue and teal depending on orientation — a living, dynamic quality',
        'The combination of high brilliance (transparent, faceted), saturation, and rarity creates one of the highest-status psychological impacts in the gem tradition',
        'Encourages the expression of nuanced, complex truths — not simple statements but layered communication',
        'The rarity itself communicates: this level of clarity and depth requires exceptional conditions to form',
      ],
      harmonics: {
        complementary_hue: 65,
        triadic_hues:      [5, 125],
        analogous_range:   [225, 265],
      },
    },

    metaphysical: {
      mineral_name:     'Blue Tourmaline (Indicolite)',
      chakra_primary:   'Throat',
      chakra_secondary: ['Third Eye', 'Crown'],
      element:   ['Water', 'Air', 'Akasha'],
      planet:    ['Venus', 'Mercury', 'Neptune'],
      archetype: ['The Rare Voice', 'The Indigo Channel', 'The Deep Communicator'],
      zodiac:    ['Libra', 'Taurus', 'Pisces'],
      numerology: 6,
      angel_number: 666,
      intention: 'I give voice to depth, nuance, and truth. My communication is a gift of rare clarity.',
      traditions: [
        'Western crystal healing — the highest Throat chakra stone in the tourmaline family',
        'Named from Latin indicum (indigo) — first formally described in 1819',
        'Brazilian gem tradition — Brazil is the world\'s primary source of fine indicolite, particularly from Minas Gerais',
        'Piezoelectric and pyroelectric properties shared with all tourmalines — physical energy transformation properties',
      ],
      properties: [
        'IMA-recognised variety — Mindat min-2027; indicolite: blue gemmy tourmaline, usually elbaite or fluor-elbaite',
        'Named from Latin indicum (indigo) — the indigo/blue colour is its defining characteristic',
        'The rarest and most valuable colour in the gem tourmaline family — fine indicolite commands premium prices per carat',
        'Colour from Fe²⁺ → Fe³⁺ charge transfer — the same mechanism as in sapphire',
        'Strong dichroism: blue from the c-axis direction, blue-green perpendicular — cutters must orient stones correctly to maximise the desired colour',
        'Strongly piezoelectric and pyroelectric — all tourmalines are; keep away from sensitive electronics',
        'Brazil (Minas Gerais) is the primary world source; also found in Afghanistan, Nigeria, Mozambique',
        'Copper-bearing indicolite from Papaiмé, Brazil (Paraiba province) is the neon blue-green Paraiba tourmaline — the most expensive tourmaline per carat',
        'The yin pair with pink tourmaline (rubellite): the full spectrum of the heart made visible — deep blue communication and warm pink love',
      ],
      gaia_resonance: 'ClarusLens + Noosphere + ViriditasHeart',
      safety_warning: '\u26a0\ufe0f PIEZOELECTRIC — keep away from sensitive electronics and hard drives. Safe for water. Pyroelectric — do not expose to rapid temperature changes. H7-7.5 — durable for jewellery use.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. BOJI STONES (KANSAS POP ROCKS)
  // Pyrite/marcasite concretions from the Smoky Hill Chalk, Kansas
  // LEGALLY TRADEMARKED trade name — important disclosure
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
      name:         'Pyrite / Marcasite concretion ("Boji Stones" — trademarked; Kansas Pop Rocks / septarian-type concretions)',
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
      shortdesc:   'Boji Stones — LEGALLY TRADEMARKED name for pyrite/marcasite-dominant concretions from the Smoky Hill Chalk Member, Niobrara Formation, Kansas, USA. Sold as smooth ("female") and rough/spiky ("male") pairs. The generic term is "Kansas Pop Rocks" or septarian concretion.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-3314.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name: 'Boji Stones (Pyrite/Marcasite concretion)',
      refractive_index: null,
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R050209'],
    },

    color: {
      primary_color:          'Pale brass to dark brown-grey — metallic, earthy, ancient',
      color_variants:         [
        'Smooth pale brass-tan ("female" — smooth surface)',
        'Rough dark grey-brown with crystalline protuberances ("male" — spiky surface)',
        'Partially oxidised with iridescent tarnish',
        'Dark metallic with golden pyrite crystal faces visible',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.35, c: 0.05, h: 70 },
      hex:     '#6b5e3a',
      munsell: '2.5Y 4/2',
      color_temperature_k:    null,
      psychological_effects:  [
        'The weight-to-size ratio (SG 4.9-5.2) creates immediate surprise — far heavier than expected for a palm stone',
        'The smooth/rough pair dynamic creates a tangible sense of complementarity — two opposites, one system',
        'The metallic, ancient appearance suggests deep geological time and alchemical transformation',
        'Holding both stones simultaneously in each hand creates a grounding circuit — a somatic anchoring experience',
        'The unpolished, natural surface communicates authenticity and rawness — this stone makes no apologies',
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
        'Modern Western crystal healing — the concept of paired male/female stones working as a complementary system is central to Boji Stone tradition',
        'Kansas, USA origin — the Smoky Hill Chalk Member of the Niobrara Formation; a unique geological context',
        'The "Boji Stone" name was trademarked in the 1980s by Karen Gillespie — generic stones from the same formation are legally sold as "Kansas Pop Rocks" or "Shaman Stones"',
      ],
      properties: [
        '\u26a0\ufe0f LEGALLY TRADEMARKED — "Boji Stone" is a registered trademark. Authentic Boji Stones come from one specific site in Kansas. Generic stones from the same formation are legally sold as "Kansas Pop Rocks", "Shaman Stones", or "Moqui Marbles" (though Moqui Marbles are a different concretion type from Utah)',
        'Composed primarily of pyrite and/or marcasite with additional mineral inclusions — formed as concretions in the Smoky Hill Chalk Member, Niobrara Formation, Kansas',
        'Sold in pairs: smooth "female" and rough/protuberance-covered "male" — the rough surface features are pyrite crystal clusters',
        'Exceptionally heavy for their size — SG 4.9-5.2 — the weight is an immediate sensory teaching',
        'The tradition holds that holding smooth (female) in one hand and rough (male) in the other balances the electromagnetic field and polarities of the body',
        'Found eroding out of the chalk in a limited area — supply is finite and the formation is protected',
        'The metaphysical tradition around these stones is almost entirely a modern Western development post-1970s',
        'Do NOT use in water — pyrite and marcasite oxidise and produce sulphuric acid in water (pyrite disease)',
      ],
      gaia_resonance: 'AnchorPrism + SovereignCore',
      safety_warning: '\u26a0\ufe0f DO NOT USE IN WATER — pyrite and marcasite oxidise in water, producing sulphuric acid (pyrite disease). This damages the stone and creates an acidic, harmful solution. Keep dry. \u26a0\ufe0f SULPHUR CONTENT — do not use in elixirs or gem water. Keep away from hard drives and electronics — metallic conductive surface. Store in a dry environment to prevent oxidation.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. BORNITE (PEACOCK ORE)
  // Copper iron sulphide — spectacular iridescent tarnish
  // One of the most visually dramatic minerals in the sulphide group
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
      crystal_system: 'Orthorhombic (low-T form) / Cubic (high-T form)',
      hardness_min: 3,
      hardness_max: 3,
      specific_gravity_min: 4.90,
      specific_gravity_max: 5.30,
      cleavage:    'Poor on {111}',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Metallic'],
      diaphaneity: ['Opaque'],
      colour:      'Fresh surface: copper-red to bronze. Tarnished surface: vivid iridescent purple, blue, red, green, yellow — the "peacock" tarnish from thin-film interference',
      streak:      'Greyish black',
      fluorescence: 'None',
      ri_min:      null,
      ri_max:      null,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Bornite — copper iron sulphide Cu₅FeS₄. An important copper ore mineral. Named after Ignaz von Born (1742–1791). Distinctive iridescent peacock tarnish on oxidised surfaces from thin-film interference. Trade name "Peacock Ore" (also applied incorrectly to chalcopyrite).',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-762.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name: 'Bornite',
      refractive_index: null,
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     'Weak in polished section (anisotropic in low-T orthorhombic form)',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R060018'],
    },

    color: {
      primary_color:          'Iridescent peacock — purple, blue, red, green, yellow tarnish over bronze-copper base',
      color_variants:         [
        'Full peacock iridescence — all spectral colours in shifting tarnish film (most prized trade form)',
        'Fresh copper-red / bronze (unoxidised, freshly broken surface)',
        'Purple-dominant tarnish (most common oxidised form)',
        'Blue-green dominant tarnish',
        'Artificially enhanced iridescence (acid-treated chalcopyrite sold as bornite — a common fraud)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.35, c: 0.20, h: 310 },
      hex:     '#7a4b8a',
      munsell: '5P 4/6',
      color_temperature_k:    null,
      psychological_effects:  [
        'The iridescent peacock tarnish is one of the most visually spectacular effects in the mineral kingdom — a single stone contains the entire visible spectrum',
        'The shifting colours as the viewing angle changes creates a sense of infinite depth and transformation',
        'The contrast between the humble, ancient copper-bronze base and the spectacular tarnish teaches that transformation begins from ordinary ground',
        'The peacock symbolism — displaying the full spectrum of the self — resonates across many traditions',
        'The knowledge that the rainbow is a thin-film interference effect — physics creating beauty without pigment — is a profound teaching on perception',
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
      chakra_secondary: ['Sacral', 'Crown', 'All chakras (iridescent full-spectrum)'],
      element:   ['Fire', 'Earth', 'Storm'],
      planet:    ['Venus', 'Sun', 'Uranus'],
      archetype: ['The Peacock', 'The Alchemist', 'The Full Spectrum Self'],
      zodiac:    ['Cancer', 'Leo', 'Taurus'],
      numerology: 8,
      angel_number: 888,
      intention: 'I display the full spectrum of my authentic self without apology or diminishment.',
      traditions: [
        'Western crystal healing — Peacock Ore as a stone of joy, happiness, and the display of authentic self',
        'Named after Ignaz von Born (1742–1791), Austrian mineralogist and Freemason — IMA-recognised since 1845',
        'Copper tradition: copper is associated with Venus and the feminine principle across Egyptian, Roman, Greek, and Ayurvedic traditions — bornite carries this lineage',
        'Alchemy tradition — the iridescent tarnish resonates with the alchemical stage of iridescence (cauda pavonis / peacock\'s tail) marking the transition in the Great Work',
      ],
      properties: [
        'IMA-recognised since 1845 — named after Austrian mineralogist Ignaz von Born (1742–1791)',
        'Formula Cu₅FeS₄ — an important copper ore mineral alongside chalcopyrite and chalcocite',
        'The iridescent peacock tarnish is from thin-film interference — oxidation creates copper sulphate/carbonate layers of varying thickness that produce structural colour (not pigment)',
        'The same physics as soap bubbles, butterfly wings, and oil on water — colour without colourant',
        '\u26a0\ufe0f FRAUD ALERT: Artificially acid-treated chalcopyrite (CuFeS₂) is widely sold as "Peacock Ore" or even as bornite. The acid-treated iridescence is more garish and uniform; natural bornite tarnish is subtler and more varied. Natural bornite has a copper-red fresh surface; acid-treated chalcopyrite is golden-yellow when fresh.',
        'Alchemical cauda pavonis (peacock\'s tail) — in the alchemical Great Work, the appearance of iridescent, rainbow colours signals a critical transformation stage between the blackening (nigredo) and the whitening (albedo)',
        'Soft (H3) and heavy (SG 4.9-5.3) — requires careful handling; easily scratched',
        'Copper content — DO NOT use in water elixirs; copper sulphide compounds are toxic if ingested',
        'The yin pair with chalcopyrite: the two most important copper ore sulphides — both iridescent, same geological environments, sister minerals in the copper belt',
      ],
      gaia_resonance: 'QuantumNexus + SovereignCore + ViriditasHeart',
      safety_warning: '\u26a0\ufe0f TOXIC — copper iron sulphide. DO NOT use in water elixirs or gem water — copper compounds are toxic if ingested. Do NOT use in drinking water. Avoid prolonged skin contact with wet specimens. Keep away from hard drives and electronics (metallic, conductive). Soft (H3) — scratches easily; store separately. \u26a0\ufe0f FRAUD NOTE: Acid-treated chalcopyrite is widely sold as Peacock Ore / Bornite — verify source.',
    },
  },

];

export default BATCH_B6;

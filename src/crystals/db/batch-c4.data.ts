/**
 * src/crystals/db/batch-c4.data.ts
 * GAIA-OS Crystal Database — Batch C-4
 *
 * Entries:
 *   1. Chalcocite          — Cu₂S; copper sulphide ore; metallic blue-black — TOXIC
 *   2. Chalcopyrite        — CuFeS₂; primary copper ore; rainbow iridescence — TOXIC
 *   3. Charoite            — rare K-Ca silicate; violet swirl; Murun, Siberia only
 *   4. Chiastolite         — andalusite var.; natural cross inclusion; martyrs' stone
 *   5. Chinese Writing Stone — porphyritic basalt; feldspar phenocrysts; trade name
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-30
 *
 * SAFETY NOTE: Chalcocite and Chalcopyrite are sulphide minerals — both toxic.
 * Chalcopyrite iridescence is a surface tarnish film, not structural colour.
 * Charoite is one of the rarest named gem minerals on Earth — single locality.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_C4: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. CHALCOCITE
  // Cu₂S — copper(I) sulphide; monoclinic
  // Named from Greek chalkos (copper)
  // IMA recognised — one of the richest copper ores; metallic blue-black
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Chalcocite',
    mindat_id:    989,
    rruff_ids:    ['R070088'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Malachite',

    physical: {
      id:           989,
      longid:       'chalcocite',
      guid:         '',
      name:         'Chalcocite',
      ima_formula:  'Cu₂S',
      mindat_formula: 'Cu2S',
      ima_status:   'A',
      ima_year:     1832,
      strunzten:    '2.BA.05',
      dana8ed:      '2.8.1.1',
      crystal_system: 'Monoclinic',
      hardness_min: 2.5,
      hardness_max: 3,
      specific_gravity_min: 5.50,
      specific_gravity_max: 5.80,
      cleavage:    'Indistinct on {110}',
      fracture:    'Conchoidal',
      tenacity:    'Slightly sectile',
      luster:      ['Metallic'],
      diaphaneity: ['Opaque'],
      colour:      'Lead-grey to black with occasional blue tarnish surface; fresh surfaces have bright metallic lustre that quickly tarnishes. Deep blue-black is the most prized collector form.',
      streak:      'Dark grey to black',
      fluorescence: 'None',
      ri_min:      null,
      ri_max:      null,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Chalcocite — Cu₂S, monoclinic copper(I) sulphide. One of the most important copper ores (79.8% Cu by weight). Named from Greek chalkos (copper). IMA 1832. Lead-grey to blue-black metallic. Major localities: Bisbee (AZ), Butte (MT), Cornwall (UK), Tsumeb (Namibia).',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-989.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Chalcocite',
      refractive_index: null,
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R070088'],
    },

    color: {
      primary_color:         'Lead-grey to blue-black — deep metallic darkness',
      color_variants: [
        'Lead-grey metallic (fresh surface — most common)',
        'Blue-black with iridescent surface tarnish (prized collector form)',
        'Black (heavily tarnished or massive ore)',
        'Blue-grey with metallic sheen (partial tarnish)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.18, c: 0.04, h: 240 },
      hex:     '#2a2d35',
      munsell: 'N 2/',
      color_temperature_k: null,
      psychological_effects: [
        'Deep metallic black is one of the most grounding colours — it absorbs light rather than reflecting it, creating a quality of containment',
        'The blue tarnish surface on a black ground is psychologically potent — hidden colour in apparent darkness',
        '79.8% copper by weight — the richest copper ore — gives it an industrial potency; this is the mineral that built the copper industry',
        'Heavy for its size (SG 5.5–5.8) and completely opaque — the opposite of transparent gemstones; a stone that holds its secrets',
        'The sectile tenacity — it can be cut with a knife — is unusual for a metallic mineral and communicates a different quality of metal: yielding',
      ],
      harmonics: {
        complementary_hue: 60,
        triadic_hues:      [0, 120],
        analogous_range:   [220, 260],
      },
    },

    metaphysical: {
      mineral_name:     'Chalcocite',
      chakra_primary:   'Root',
      chakra_secondary: ['Earth Star', 'Sacral'],
      element:   ['Earth', 'Metal', 'Fire'],
      planet:    ['Saturn', 'Mars', 'Pluto'],
      archetype: ['The Dark Ore', 'The Hidden Copper', 'The Foundation of Industry'],
      zodiac:    ['Capricorn', 'Scorpio', 'Taurus'],
      numerology: 4,
      angel_number: 444,
      intention: 'I am the dark ore that feeds the age of copper. What is hidden in me has built the world.',
      traditions: [
        'Named 1832 from Greek chalkos (copper) — chalcocite is one of the richest copper ores at 79.8% Cu by weight',
        'Bisbee, Arizona (USA) — one of the most famous copper-mining towns in the American West; massive chalcocite deposits',
        'Butte, Montana (USA) — the "Richest Hill on Earth"; enormous chalcocite and chalcopyrite ore body',
        'Cornwall (UK) — historical copper and tin mining region; chalcocite from Cornish mines traded across Bronze Age Europe',
        'Modern — still a primary copper ore; supergene enrichment deposits of chalcocite are among the richest copper concentrations known',
      ],
      properties: [
        'IMA 1832 — formula Cu₂S; monoclinic copper(I) sulphide',
        'One of the richest copper ores at 79.8% Cu by weight — forms by supergene enrichment of primary chalcopyrite',
        'TOXIC — sulphide mineral; DO NOT use in water; copper and sulphide compounds are toxic',
        'H2.5–3 and slightly sectile — can be cut with a knife; unusual for an ore mineral',
        'SG 5.5–5.8 — notably heavy; dense metallic feel',
        'Tarnishes rapidly on fresh surfaces — blue-black tarnish is characteristic',
        'Major localities: Bisbee (AZ, USA), Butte (MT, USA), Cornwall (UK), Tsumeb (Namibia), Chuquicamata (Chile)',
      ],
      gaia_resonance: 'AnchorPrism + SovereignCore',
      safety_warning:  '⚠️ TOXIC — copper sulphide. DO NOT use in water elixirs. Wash hands after handling. Keep away from children and food. Sulphide minerals may release toxic hydrogen sulphide (H₂S) if exposed to acid. Collector mineral only.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. CHALCOPYRITE
  // CuFeS₂ — copper iron sulphide; tetragonal
  // The world's primary copper ore; rainbow iridescent tarnish surface
  // Named from Greek chalkos (copper) + pyrites (fire stone)
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Chalcopyrite',
    mindat_id:    993,
    rruff_ids:    ['R040049'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Pyrite',

    physical: {
      id:           993,
      longid:       'chalcopyrite',
      guid:         '',
      name:         'Chalcopyrite',
      ima_formula:  'CuFeS₂',
      mindat_formula: 'CuFeS2',
      ima_status:   'A',
      ima_year:     1725,
      strunzten:    '2.CB.10',
      dana8ed:      '2.9.1.1',
      crystal_system: 'Tetragonal',
      hardness_min: 3.5,
      hardness_max: 4,
      specific_gravity_min: 4.10,
      specific_gravity_max: 4.30,
      cleavage:    'Indistinct on {011}',
      fracture:    'Uneven to conchoidal',
      tenacity:    'Brittle',
      luster:      ['Metallic'],
      diaphaneity: ['Opaque'],
      colour:      'Brass-yellow on fresh surface; rapidly develops vivid iridescent tarnish of blue, purple, green, gold, and red — the "peacock ore" rainbow. Tarnish is a surface iron oxide/sulphide film, not structural colour. Streak greenish-black.',
      streak:      'Greenish-black',
      fluorescence: 'None',
      ri_min:      null,
      ri_max:      null,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Chalcopyrite — CuFeS₂, tetragonal copper iron sulphide. The world\'s most important copper ore. Named from Greek chalkos + pyrites. IMA 1725. Brass-yellow with vivid iridescent rainbow tarnish ("peacock ore"). Much sold "peacock ore" is acid-treated bornite or chalcopyrite — natural tarnish is subtler.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-993.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Chalcopyrite',
      refractive_index: null,
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R040049'],
    },

    color: {
      primary_color:         'Brass-yellow (fresh) with iridescent rainbow tarnish — peacock ore',
      color_variants: [
        'Brass-yellow (fresh unoxidised surface)',
        'Rainbow iridescent blue-purple-gold-green-red (natural tarnish)',
        'Deep blue-purple dominant tarnish (most common natural form)',
        'Vivid acid-enhanced rainbow (treated bornite — not natural chalcopyrite)',
        'Dull grey-black (heavily weathered)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.45, c: 0.18, h: 270 },
      hex:     '#8a6abf',
      munsell: '5P 4/8',
      color_temperature_k: null,
      psychological_effects: [
        'The rainbow tarnish is one of the most visually complex colour phenomena in the mineral kingdom — every angle reveals a different hue',
        'Structural iridescence (thin-film interference) is the same optical mechanism as butterfly wings, soap bubbles, and oil on water',
        'The contrast between the brass-yellow fresh interior and the rainbow tarnish exterior teaches transformation through oxidation — change as beauty',
        'Market deception awareness — most sold "peacock ore" is acid-treated; knowing the difference creates a more discerning relationship with materials',
        'The name "fool\'s gold of copper" connects it to pyrite and to the broader theme of apparent vs true value',
      ],
      harmonics: {
        complementary_hue: 90,
        triadic_hues:      [30, 150],
        analogous_range:   [250, 290],
      },
    },

    metaphysical: {
      mineral_name:     'Chalcopyrite',
      chakra_primary:   'Solar Plexus',
      chakra_secondary: ['Sacral', 'Crown', 'All chakras (via rainbow)'],
      element:   ['Fire', 'Earth', 'Metal'],
      planet:    ['Sun', 'Mars', 'Venus'],
      archetype: ['The Rainbow Ore', 'The Copper Fire', 'The Peacock of Minerals'],
      zodiac:    ['Aries', 'Leo', 'Taurus'],
      numerology: 9,
      angel_number: 999,
      intention: 'My surface holds every colour of transformation. The fire that changes me is the fire that reveals me.',
      traditions: [
        'Named from Greek chalkos (copper) + pyrites (fire stone) — recognised as a copper ore since antiquity',
        '"Peacock ore" — the trade name for iridescent chalcopyrite (and often acid-treated bornite); universally popular in the crystal healing market',
        'Primary copper ore — responsible for the majority of world copper production; the mineral foundation of electrical civilisation',
        'Butte, Montana; Bingham Canyon, Utah; Escondida, Chile — the great chalcopyrite porphyry copper deposits that underpin modern industry',
        'Alchemical tradition — copper (Venus) + iron (Mars) in one mineral; the union of the two most mythologically charged metals',
      ],
      properties: [
        'IMA 1725 — formula CuFeS₂; tetragonal copper iron sulphide; the world\'s most important copper ore',
        'Rainbow iridescence is surface tarnish (thin-film iron oxide/sulphide interference), NOT structural colour of the mineral itself',
        'WARNING: most sold "peacock ore" is acid-treated bornite (Cu₅FeS₄), not chalcopyrite — acid treatment artificially enhances/creates the rainbow',
        'TOXIC — sulphide mineral; DO NOT use in water; copper and sulphide compounds are toxic',
        'H3.5–4 — relatively soft; tarnish surface is easily scratched',
        'SG 4.1–4.3 — noticeably heavy',
        'Major localities: worldwide; Bingham Canyon (UT, USA), Escondida (Chile), Grasberg (Indonesia), Bor (Serbia)',
      ],
      gaia_resonance: 'SovereignCore + ViriditasHeart + ClarusLens',
      safety_warning:  '⚠️ TOXIC — copper iron sulphide. DO NOT use in water elixirs. Wash hands after handling. Sulphide minerals may release H₂S in acid. NOTE: much sold "peacock ore" is acid-treated bornite — acid treatment residue may be an additional irritant. Collector and display use only.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. CHAROITE
  // Rare K-Ca silicate — K(Ca,Na)₂Si₄O₁₀(OH,F)·H₂O (simplified)
  // Named after the Chara River, Siberia
  // IMA 1978 — single locality worldwide: Murun massif, Sakha Republic
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Charoite',
    mindat_id:    1010,
    rruff_ids:    ['R060897'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Sugilite',

    physical: {
      id:           1010,
      longid:       'charoite',
      guid:         '',
      name:         'Charoite',
      ima_formula:  'K(Ca,Na)₂[Si₄O₁₀](OH,F)·H₂O',
      mindat_formula: 'K(Ca,Na)2[Si4O10](OH,F)·H2O',
      ima_status:   'A',
      ima_year:     1978,
      strunzten:    '9.EE.20',
      dana8ed:      '72.3.1.2',
      crystal_system: 'Monoclinic',
      hardness_min: 5,
      hardness_max: 6,
      specific_gravity_min: 2.54,
      specific_gravity_max: 2.68,
      cleavage:    'Distinct on {010}',
      fracture:    'Splintery to uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Silky (fibrous)', 'Pearly'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Vivid violet to lavender-purple, swirling with white, black (aegirine), and orange (tinaksite) inclusions. The swirling fibrous texture is unique — no other mineral looks like charoite. Colour from Mn²⁺ or charge transfer.',
      streak:      'White',
      fluorescence: 'Weak pale blue-white under LW UV',
      ri_min:      1.550,
      ri_max:      1.561,
      birefringence: 0.009,
      optical_type: 'B',
      shortdesc:   'Charoite — K(Ca,Na)₂[Si₄O₁₀](OH,F)·H₂O, rare monoclinic potassium calcium silicate. IMA 1978. Named after the Chara River. Single locality worldwide: Murun alkaline massif, Sakha Republic, Siberia. Vivid violet-purple with swirling fibrous texture — unique and unmistakable.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-1010.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Charoite',
      refractive_index: { n_alpha: 1.550, n_beta: 1.553, n_gamma: 1.561 },
      birefringence:   0.009,
      optical_sign:    '+',
      dispersion:      'r > v, weak',
      pleochroism:     'Weak: violet / pale lavender / pale violet',
      fluorescence_lw: 'Weak pale blue-white',
      fluorescence_sw: 'None to weak',
      phosphorescence: null,
      visible_wavelength_nm: { min: 400, max: 430 },
      spectra: ['R060897'],
    },

    color: {
      primary_color:         'Vivid violet to lavender-purple with swirling white, black, and orange — entirely unmistakable',
      color_variants: [
        'Deep violet-purple (most prized — dense Mn colour)',
        'Lavender-lilac (paler, more common)',
        'Purple swirl with heavy white aegirine/microcline matrix',
        'Purple-orange combination (tinaksite inclusions add warm contrast)',
        'Near-black-and-purple (aegirine-dominant matrix)',
      ],
      dominant_wavelength_nm: 415,
      oklch:   { l: 0.48, c: 0.20, h: 310 },
      hex:     '#7a3a9a',
      munsell: '5P 4/10',
      color_temperature_k: null,
      psychological_effects: [
        'The swirling fibrous texture creates a visual sense of movement — charoite appears to be in motion even when still',
        'Deep violet is the highest frequency visible colour — psychologically it is associated with the transpersonal, the mystical, the liminal',
        'Single-locality rarity (one place on Earth) gives every charoite specimen an almost mythological specificity — this came from Siberia and nowhere else',
        'The black aegirine needles against violet create a depth map — the eye travels inward, finding new layers',
        'Orange tinaksite inclusions provide a complementary contrast (orange/violet) that makes both colours more vivid simultaneously',
      ],
      harmonics: {
        complementary_hue: 130,
        triadic_hues:      [70, 190],
        analogous_range:   [290, 330],
      },
    },

    metaphysical: {
      mineral_name:     'Charoite',
      chakra_primary:   'Crown',
      chakra_secondary: ['Third Eye', 'Soul Star', 'Higher Heart (Thymus)'],
      element:   ['Akasha', 'Air', 'Fire'],
      planet:    ['Pluto', 'Neptune', 'Uranus'],
      archetype: ['The Siberian Mystic', 'The Violet Transformer', 'The Stone of the Soul'],
      zodiac:    ['Scorpio', 'Sagittarius', 'Pisces'],
      numerology: 7,
      angel_number: 777,
      intention: 'I was born in the only place on Earth that could make me. My transformation is as specific as my origin. I carry the Siberian violet night.',
      traditions: [
        'Discovered and named 1978 after the Chara River, Sakha Republic (Yakutia), Siberia — first described by Vera Rogova and colleagues',
        'Single locality worldwide — the Murun alkaline massif near the Chara River is the only known source of gem-quality charoite',
        'Soviet and Russian tradition — extensively carved and used as a decorative stone in the USSR; large slabs polished for architectural use',
        'Western crystal healing — introduced to Western markets in the 1980s; rapidly adopted as a premier transformation and spiritual awakening stone',
        'The swirling violet pattern has been called the "Stone of Magic" and the "Soul Stone" in various modern traditions',
      ],
      properties: [
        'IMA 1978 — formula K(Ca,Na)₂[Si₄O₁₀](OH,F)·H₂O; monoclinic potassium calcium phyllosilicate',
        'Single locality worldwide — Murun alkaline massif, Sakha Republic, Siberia; supply is finite',
        'Associated minerals: aegirine (black needles), tinaksite (orange), microcline (white), canasite — all visible in polished specimens',
        'Swirling fibrous texture results from intergrowth of multiple silicate minerals under metasomatic conditions',
        'H5–6 — moderate hardness; good for jewellery with protective setting',
        'DO NOT use in prolonged water contact — silicate with hydroxyl groups; avoid salt water',
        'No acute toxicity; some concern about asbestos-form fibrous silicate dust — do not sand or grind without respiratory protection',
      ],
      gaia_resonance: 'QuantumNexus + Noosphere + ClarusLens',
      safety_warning:  '⚠️ DO NOT use in prolonged water contact or salt water. Fibrous silicate mineral — do not sand, grind, or create dust without respiratory protection (potential asbestiform fibre risk in fibrous varieties). H5–6 — moderate hardness. No acute handling toxicity.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. CHIASTOLITE
  // Andalusite variety with carbonaceous cross inclusion
  // Al₂SiO₅ — orthorhombic aluminium silicate
  // Named from Greek chiastos (cross-marked) — the martyrs' stone
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Chiastolite',
    mindat_id:    199,
    rruff_ids:    ['R060152'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Staurolite',

    physical: {
      id:           199,
      longid:       'chiastolite',
      guid:         '',
      name:         'Chiastolite (andalusite var. — Al₂SiO₅ with carbonaceous cross inclusion)',
      ima_formula:  'Al₂SiO₅',
      mindat_formula: 'Al2SiO5',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '9.AF.10',
      dana8ed:      '52.1.1.2',
      crystal_system: 'Orthorhombic',
      hardness_min: 6.5,
      hardness_max: 7.5,
      specific_gravity_min: 3.13,
      specific_gravity_max: 3.21,
      cleavage:    'Good on {110}',
      fracture:    'Uneven to conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Dull (weathered)'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Pale grey-brown to tan outer crystal with a dark brown to black carbonaceous cross pattern visible in cross-section. The cross is formed by carbonaceous material pushed to the crystal margins during growth. Natural geometric perfection.',
      streak:      'White',
      fluorescence: 'None',
      ri_min:      1.629,
      ri_max:      1.640,
      birefringence: 0.010,
      optical_type: 'B',
      shortdesc:   'Chiastolite — variety of andalusite (Al₂SiO₅) with a naturally occurring carbonaceous cross inclusion visible in cross-section. Named from Greek chiastos (cross-marked). The dark cross forms as carbonaceous material is displaced to crystal margins during growth. The original "Martyrs\u2019 Stone."',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-199.html',
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Chiastolite (Andalusite)',
      refractive_index: { n_alpha: 1.629, n_beta: 1.633, n_gamma: 1.640 },
      birefringence:   0.010,
      optical_sign:    '-',
      dispersion:      'r < v, weak',
      pleochroism:     'Strong trichroism: green / yellow / red (in transparent andalusite faceted stones)',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R060152'],
    },

    color: {
      primary_color:         'Pale grey-brown to tan with a dark brown-black natural cross in cross-section',
      color_variants: [
        'Classic pale tan-brown with black cross (most common)',
        'Pale grey with dark grey-brown cross',
        'Warm buff-brown with deep black cross (high carbonaceous content)',
        'White-cream with pale grey cross (low C content)',
      ],
      dominant_wavelength_nm: 580,
      oklch:   { l: 0.62, c: 0.06, h: 65 },
      hex:     '#a8906a',
      munsell: '7.5YR 6/4',
      color_temperature_k: null,
      psychological_effects: [
        'The natural cross is among the most psychologically powerful symbols in human culture — finding it in uncut stone creates an immediate sense of sacred meaning',
        'The cross is not painted or carved — it is a consequence of crystal physics — which makes it feel like a message from nature rather than human intention',
        'Earth-brown and warm tan colours provide a grounding quality before the cross even enters awareness',
        'Cross-section reveal — the cross only appears when cut perpendicular to the c-axis; discovering the interior is a small initiation',
        'Compared to staurolite (also a natural cross stone), chiastolite\'s cross is darker, more precise, and geometrically perfect',
      ],
      harmonics: {
        complementary_hue: 245,
        triadic_hues:      [185, 305],
        analogous_range:   [45, 85],
      },
    },

    metaphysical: {
      mineral_name:     'Chiastolite',
      chakra_primary:   'Root',
      chakra_secondary: ['Heart', 'Crown', 'Earth Star'],
      element:   ['Earth', 'Akasha'],
      planet:    ['Saturn', 'Sun', 'Earth'],
      archetype: ['The Martyr\'s Cross', 'The Stone of Transition', 'The Four-Direction Keeper'],
      zodiac:    ['Capricorn', 'Libra', 'Aries'],
      numerology: 4,
      angel_number: 444,
      intention: 'I carry the cross that was not placed upon me by others — it grew within me from my own nature. I am the intersection of all directions.',
      traditions: [
        'Martyrs\u2019 Stone — worn by early Christians as a symbol of Christ\'s cross; found naturally occurring without human modification',
        'Way of Saint James (Camino de Santiago) — chiastolite found along the Camino route in Spain; pilgrims carried it as a talisman of protection and sacred passage',
        'Chinese tradition — chiastolite pebbles from riverbeds used as protective amulets; associated with the four cardinal directions',
        'Named from Greek chiastos (marked with chi/X) — the Greek letter chi (χ) resembles the cross pattern',
        'Modern crystal healing — used for protection, transition, past-life work, and navigating major life changes',
      ],
      properties: [
        'Variety of andalusite (Al₂SiO₅) — the cross is not a different mineral but displaced carbonaceous material pushed to crystal margins during growth',
        'One of three Al₂SiO₅ polymorphs: andalusite (orthorhombic, low P), kyanite (triclinic, high P), sillimanite (orthorhombic, high T) — all same formula, different crystal systems',
        'The cross pattern forms because carbonaceous inclusions are expelled from the growing crystal centre and concentrate at the {110} faces',
        'H6.5–7.5 — hard and durable; safe for jewellery',
        'Safe for water — Al₂SiO₅ is chemically stable; no toxic elements',
        'Major localities: Bimbowrie (South Australia), Beja (Portugal — Camino-adjacent), Madera County (CA, USA), Brittany (France)',
      ],
      gaia_resonance: 'AnchorPrism + SovereignCore + ClarusLens',
      safety_warning:  'Safe for water. H6.5–7.5 — durable. No toxic elements. Aluminium silicate — chemically inert. No significant hazards.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. CHINESE WRITING STONE
  // Porphyritic basalt or limestone with feldspar/calcite phenocrysts
  // Trade name — crystal script patterns resemble Chinese characters
  // Primary localities: Sacramento Valley (CA, USA) and China
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Chinese Writing Stone',
    mindat_id:    null,
    rruff_ids:    [],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   true,
    color_layer:  'natural',
    yin_yang_pair: 'Calligraphy Stone',

    physical: {
      id:           null,
      longid:       'chinese-writing-stone',
      guid:         '',
      name:         'Porphyritic Basalt / Limestone with Andalusite or Feldspar phenocrysts ("Chinese Writing Stone" — trade name)',
      ima_formula:  'Not applicable (rock — silicate matrix + feldspar/andalusite phenocrysts)',
      mindat_formula: null,
      ima_status:   'Not IMA — trade name for porphyritic rock with script-like crystal inclusions',
      ima_year:     null,
      strunzten:    null,
      dana8ed:      null,
      crystal_system: 'Not applicable (igneous/metamorphic rock)',
      hardness_min: 5,
      hardness_max: 7,
      specific_gravity_min: 2.65,
      specific_gravity_max: 2.90,
      cleavage:    'None (rock)',
      fracture:    'Uneven',
      tenacity:    'Brittle',
      luster:      ['Dull', 'Vitreous (phenocrysts)'],
      diaphaneity: ['Opaque'],
      colour:      'Black to dark grey-green matrix with white to cream feldspar (or andalusite) phenocrysts arranged in angular, blade-like patterns that resemble Chinese characters or script. The contrast between dark matrix and white crystals is sharp and striking.',
      streak:      'White to grey',
      fluorescence: 'None to very weak',
      ri_min:      null,
      ri_max:      null,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Chinese Writing Stone — trade name for porphyritic basalt or andesite with andalusite (or feldspar) phenocrysts forming angular white script-like patterns on a dark grey-black matrix. Primary locality: Sacramento Valley, CA (USA). Also from China. Yin pair to Calligraphy Stone.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  null,
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Chinese Writing Stone (Porphyritic Rock)',
      refractive_index: null,
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'None to very weak',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: [],
    },

    color: {
      primary_color:         'Black to dark grey-green matrix with sharp white-cream feldspar script patterns',
      color_variants: [
        'Classic black matrix with white angular script (most common — high contrast)',
        'Dark grey-green matrix with cream-white phenocrysts',
        'Near-black with pale grey angular markings (lower contrast)',
        'Dark matrix with yellowish-cream phenocrysts (weathered feldspar)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.20, c: 0.02, h: 180 },
      hex:     '#2a2e2a',
      munsell: 'N 2.5/',
      color_temperature_k: null,
      psychological_effects: [
        'High black-white contrast is one of the most visually arresting colour combinations — the patterns demand reading',
        'The angular, blade-like phenocrysts create a more geometric, architectural script than the flowing curves of Calligraphy Stone — more Yang than Yin',
        'The impression of writing without comprehension creates a state of receptive attention — the brain searches for meaning and cannot quite find it',
        'Dark matrix recedes and the white script advances — the patterns appear to float above the surface',
        'The pairing with Calligraphy Stone is natural — one dark with light script, one light with dark script; perfect yin-yang visual complement',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Chinese Writing Stone',
      chakra_primary:   'Third Eye',
      chakra_secondary: ['Crown', 'Root', 'Throat'],
      element:   ['Earth', 'Akasha', 'Metal'],
      planet:    ['Saturn', 'Mercury'],
      archetype: ['The Earth Scribe', 'The Stone Scholar', 'The Ancient Text'],
      zodiac:    ['Capricorn', 'Gemini', 'Virgo'],
      numerology: 4,
      angel_number: 444,
      intention: 'The Earth has written in dark and light. I read the angular truth of what has always been inscribed in the rock.',
      traditions: [
        'Named for the resemblance of andalusite/feldspar phenocrysts to Chinese script characters — the angular blade-like phenocrysts look like brushstroke characters',
        'Sacramento Valley, California — the primary locality for the most recognised Chinese Writing Stone; basalt from the Cosumnes River area',
        'Chinese tradition — similar patterned stones used in scholar\'s rock (guōnǎ shí / chéngshī yàn) practice; appreciation of naturally occurring patterns in stone',
        'Feng Shui — stones with natural script patterns considered highly auspicious — believed to carry messages from heaven or the ancestors',
        'Modern crystal healing — used for accessing Akashic records, past-life memory, and ancestral wisdom alongside Calligraphy Stone',
      ],
      properties: [
        'Trade name: "Chinese Writing Stone" — porphyritic basalt/andesite with andalusite or feldspar phenocrysts; script-like patterns',
        'Phenocrysts: andalusite (Al₂SiO₅) or plagioclase feldspar crystallised early in the magma; matrix crystallised later and around them',
        'Primary locality: Sacramento Valley, CA, USA (Cosumnes River area, Amador County)',
        'Yin-Yang pair with Calligraphy Stone — dark matrix/light script (Chinese Writing) vs light matrix/dark script (Calligraphy) — exact visual complement',
        'H5–7 (range depending on phenocryst vs matrix) — durable enough for display and tumbled stones',
        'Safe for water — silicate rock; no toxic elements',
        'Each piece is unique — the phenocryst patterns are never identical',
      ],
      gaia_resonance: 'Noosphere + ClarusLens + AnchorPrism',
      safety_warning:  'Safe for water. H5–7 — durable. No toxic elements. Silicate rock — chemically inert. No significant hazards.',
    },
  },

];

export default BATCH_C4;

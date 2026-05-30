/**
 * src/crystals/db/batch-b9.data.ts
 * GAIA-OS Crystal Database — Batch B-9
 *
 * Entries:
 *   1. Bustamite   — rare Mn-Ca inosilicate; triclinic; IMA 1827
 *   2. Bixbyite    — rare Mn-Fe oxide; cubic; Utah/Namibia; sister to red beryl
 *   3. Butter Jade — trade name for serpentine/bowenite; creamy yellow-green
 *   4. Byssolite   — fibrous actinolite variety; mountain leather; ASBESTOS WARNING
 *   5. Bytownite   — plagioclase feldspar (An70–90); golden labradorite; IMA recognised
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-30
 *
 * NOTE: B-9 is the true close of the B-series.
 * Byssolite carries a critical asbestos safety warning — fibrous amphibole.
 * Bixbyite is named after the same Maynard Bixby as red beryl (bixbite) —
 * completing the Mn lineage from Bustamite through the series.
 * Bytownite bridges into the feldspar family that recurs in C-series stones.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_B9: CrystalRecord[] = [

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
        'Part of the wollastonite–bustamite–rhodonite series — all Mn/Ca inosilicates with varying Mn:Ca ratios',
        'Distinguished from rhodonite by higher Ca content and softer pink colour; rhodonite is deeper rose with black manganese oxide veining',
        'Vivid orange-salmon fluorescence under LW UV (especially Franklin, NJ specimens)',
        'Classic localities: Franklin and Sterling Hill, NJ (USA); Broken Hill (NSW, Australia); Långban (Sweden); Harstig Mine (Sweden)',
        'H5.5–6.5 — durable enough for display and meditation; protect from harder minerals in storage',
        'Safe for water — silicate mineral; no toxic components.',
      ],
      gaia_resonance: 'ViriditasHeart + ClarusLens',
      safety_warning:  'Safe for water. H5.5–6.5 — moderate hardness; store away from harder minerals. No toxic elements. Franklin NJ specimens may be mildly radioactive if associated with uranium-bearing minerals — verify provenance.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. BIXBYITE
  // Rare manganese iron oxide — (Mn,Fe)₂O₃; cubic
  // Named after Maynard Bixby (1853–1935) — same mineralogist as red beryl (bixbite)
  // IMA recognised — classic locality: Thomas Range, Juab County, Utah, USA
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Bixbyite',
    mindat_id:    701,
    rruff_ids:    ['R060177'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Hematite',

    physical: {
      id:           701,
      longid:       'bixbyite',
      guid:         '',
      name:         'Bixbyite',
      ima_formula:  '(Mn,Fe)₂O₃',
      mindat_formula: '(Mn,Fe)2O3',
      ima_status:   'A',
      ima_year:     1897,
      strunzten:    '4.CB.45',
      dana8ed:      '4.3.4.1',
      crystal_system: 'Cubic',
      hardness_min: 6,
      hardness_max: 6.5,
      specific_gravity_min: 4.93,
      specific_gravity_max: 5.00,
      cleavage:    'Imperfect on {111}',
      fracture:    'Uneven to conchoidal',
      tenacity:    'Brittle',
      luster:      ['Sub-metallic', 'Metallic'],
      diaphaneity: ['Opaque'],
      colour:      'Iron-black to steel-grey with bright metallic to sub-metallic lustre; fresh surfaces have a warm black gleam. Small but perfectly formed cubic crystals on white topaz matrix — one of the most visually striking collector combinations.',
      streak:      'Black',
      fluorescence: 'None',
      ri_min:      null,
      ri_max:      null,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Bixbyite — (Mn,Fe)₂O₃, cubic manganese iron oxide. Named after Maynard Bixby (1853–1935), same mineralogist honoured by red beryl (bixbite). IMA 1897. Classic locality: Thomas Range, Juab County, Utah, USA. Small jet-black cubic crystals on white topaz — one of the most iconic collector combinations.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-701.html',
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Bixbyite',
      refractive_index: null,
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R060177'],
    },

    color: {
      primary_color:         'Iron-black to steel-grey — deep metallic darkness with geometric perfection',
      color_variants: [
        'Jet-black with bright metallic lustre (freshest, highest Mn content)',
        'Steel-grey-black with sub-metallic sheen (higher Fe content)',
        'Iron-black with cube faces showing mirror-flat reflections',
        'Dark brown-black (oxidised surface)',
      ],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.15, c: 0.03, h: 20 },
      hex:     '#1a1a1c',
      munsell: 'N 1.5/',
      color_temperature_k: null,
      psychological_effects: [
        'Perfect black cubes on white topaz matrix create one of the most dramatically geometric visual contrasts in the mineral kingdom',
        'Cubic habit — flat, mirror-like faces — makes small crystals appear almost synthetic, triggering awe at natural geometric precision',
        'Iron-black is the most grounding and containing of all mineral colours — pure absorption, zero reflection',
        'The Bixby connection — same name as the rarest red beryl — creates a poetic unity between the darkest and most crimson minerals',
        'Heavy density (SG ~5) in tiny cubes creates a disproportionate sense of mass — small, but undeniably present',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Bixbyite',
      chakra_primary:   'Root',
      chakra_secondary: ['Earth Star', 'Solar Plexus'],
      element:   ['Earth', 'Metal', 'Fire'],
      planet:    ['Saturn', 'Pluto', 'Mars'],
      archetype: ['The Perfect Cube', 'The Dark Twin', 'The Geometric Ground'],
      zodiac:    ['Capricorn', 'Scorpio', 'Aries'],
      numerology: 8,
      angel_number: 888,
      intention: 'I am built on perfect geometry. My darkness is not absence — it is complete containment of all light.',
      traditions: [
        'Named after Maynard Bixby (1853–1935), Utah mineralogist and mineral dealer — the same person honoured by red beryl (bixbite); dark and crimson, black and red, the two Bixby minerals span the extremes',
        'Thomas Range, Utah — one of the most celebrated collector mineral localities in North America; topaz, bixbyite, red beryl, and garnet all occur in the same rhyolite complex',
        'IMA 1897 — described from the Thomas Range; cubic crystals embedded in or resting on white topaz are the most prized form',
        'Modern crystal healing — black metallic oxides used for Root chakra anchoring, protection, and grounding electromagnetic fields',
        'Namibian and Indian occurrences — bixbyite also found in manganese deposits in Namibia (Otjosondu) and India (Madhya Pradesh)',
      ],
      properties: [
        'IMA 1897 — formula (Mn,Fe)₂O₃; cubic crystal system; isostructural with bixbyite-type structure',
        'Named after Maynard Bixby — same mineralogist as red beryl (bixbite); one of the few cases where two minerals named after the same person represent near-opposite colour extremes',
        'Classic locality: Thomas Range, Juab County, Utah — small jet-black cubes and modified cubes embedded in or on white topaz in rhyolite cavities',
        'H6–6.5 and SG ~5 — hard, heavy, and chemically stable; good for display and handling',
        'Safe for water — manganese iron oxide is chemically inert and non-toxic in this form',
        'Also found: Otjosondu Mn deposit (Namibia); Madhya Pradesh (India); Långban (Sweden)',
        'Do not confuse with bixbite (red beryl) — same person, completely different mineral species, formula, and colour',
      ],
      gaia_resonance: 'AnchorPrism + SovereignCore + QuantumNexus',
      safety_warning:  'Safe for water. H6–6.5 — hard and durable. No toxic elements. Manganese oxide — chemically stable. No significant hazards. Do not confuse with bixbite (red beryl) — different mineral.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. BUTTER JADE
  // Trade name for serpentine / bowenite with cream-yellow colour
  // Also applied to pale yellow-green nephrite and some pale jadeite
  // Primary localities: China, South Korea, New Zealand, South Africa
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Butter Jade',
    mindat_id:    null,
    rruff_ids:    [],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   true,
    color_layer:  'natural',
    yin_yang_pair: 'Green Jade',

    physical: {
      id:           null,
      longid:       'butter-jade',
      guid:         '',
      name:         'Serpentine / Bowenite / Nephrite (\"Butter Jade\" — trade name for pale cream-yellow serpentine group stone)',
      ima_formula:  'Mg₃Si₂O₅(OH)₄ (antigorite/lizardite — simplified)',
      mindat_formula: 'Mg3Si2O5(OH)4',
      ima_status:   'Not IMA — trade name applied to pale yellow-cream serpentine and occasionally nephrite',
      ima_year:     null,
      strunzten:    '9.ED.15',
      dana8ed:      '71.1.2.1',
      crystal_system: 'Monoclinic (serpentine group)',
      hardness_min: 2.5,
      hardness_max: 5.5,
      specific_gravity_min: 2.50,
      specific_gravity_max: 2.65,
      cleavage:    'Perfect on {001} (antigorite); rarely visible in massive form',
      fracture:    'Splintery to conchoidal (bowenite); uneven (massive)',
      tenacity:    'Brittle to tough (bowenite variety is notably tough)',
      luster:      ['Waxy', 'Greasy', 'Silky'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Pale cream to butter-yellow, cream-white, pale yellow-green — the warmest and most golden of the serpentine group stones. Colour from trace iron and NiO inclusions modifying the typical green serpentine hue toward yellow-cream.',
      streak:      'White',
      fluorescence: 'None to weak green-white under LW UV',
      ri_min:      1.550,
      ri_max:      1.570,
      birefringence: 0.014,
      optical_type: 'B',
      shortdesc:   'Butter Jade — trade name for pale cream-yellow serpentine (commonly antigorite/lizardite or bowenite variety). NOT true jadeite or nephrite in most commercial specimens. Warm cream-yellow palette. Primary localities: China, South Korea, New Zealand, South Africa.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  null,
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Butter Jade (Serpentine group)',
      refractive_index: { n_alpha: 1.550, n_beta: 1.560, n_gamma: 1.570 },
      birefringence:   0.014,
      optical_sign:    '+',
      dispersion:      'Weak',
      pleochroism:     'None to very weak',
      fluorescence_lw: 'None to weak green-white',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 570, max: 600 },
      spectra: [],
    },

    color: {
      primary_color:         'Pale butter-cream to warm yellow-green — the colour of unsalted butter and cream in morning light',
      color_variants: [
        'Classic butter-cream yellow (most common — even, warm, pale)',
        'Pale lemon-cream (cooler yellow tone)',
        'Warm ivory-white with faint yellow tint',
        'Pale yellow-green (approaching classic serpentine)',
        'Honey-gold (richer, deeper Fe staining)',
      ],
      dominant_wavelength_nm: 575,
      oklch:   { l: 0.88, c: 0.07, h: 95 },
      hex:     '#f0e8b0',
      munsell: '5Y 9/4',
      color_temperature_k: null,
      psychological_effects: [
        'Cream-yellow is universally associated with warmth, safety, and nourishment — the colour of mother\u2019s milk, butter, and morning sunlight',
        'The waxy, slightly translucent surface quality of bowenite gives it an almost living quality — it appears soft and warm to the eye before being touched',
        'Pale neutrality — neither strongly yellow nor white — creates a quality of receptive openness; it asks nothing, offers everything',
        'The jade association (even when technically serpentine) carries millennia of cultural weight — longevity, virtue, heaven',
        'Cream and butter tones reduce psychological defenses — the colour family most associated with unconditional safety',
      ],
      harmonics: {
        complementary_hue: 275,
        triadic_hues:      [215, 335],
        analogous_range:   [75, 115],
      },
    },

    metaphysical: {
      mineral_name:     'Butter Jade',
      chakra_primary:   'Solar Plexus',
      chakra_secondary: ['Heart', 'Sacral', 'Crown'],
      element:   ['Earth', 'Water'],
      planet:    ['Venus', 'Moon', 'Jupiter'],
      archetype: ['The Nourishing Mother', 'The Golden Receiver', 'The Jade of Morning'],
      zodiac:    ['Taurus', 'Cancer', 'Libra'],
      numerology: 6,
      angel_number: 666,
      intention: 'I receive as freely as I give. I am the warmth that precedes the sunrise — steady, golden, without condition.',
      traditions: [
        'Chinese jade tradition — pale yellow (huang yu) jade is associated with the earth element, imperial favour, and abundance; the Emperor\u2019s yellow was represented in jade as well as silk',
        'Korean jade tradition — pale cream serpentine / nephrite used for ceremonial objects and amulets for thousands of years',
        'New Zealand (bowenite) — tangiwai variety used by M\u0101ori for hei tiki and personal adornment; bowenite is tough enough to carve finely',
        'Trade note — most commercial "Butter Jade" is antigorite or lizardite serpentine, NOT true jadeite (NaAlSi₂O₆) or nephrite (Ca₂(Mg,Fe)₅Si₈O₂₂(OH)₂)',
        'Modern Western crystal healing — yellow/cream jade-family stones used for abundance, self-worth, and emotional nourishment',
      ],
      properties: [
        'Trade name: "Butter Jade" — applied to pale cream-yellow serpentine (antigorite, lizardite, or bowenite variety)',
        'TRUE jade is either jadeite (pyroxene — H6.5–7) or nephrite (amphibole — H6–6.5); most "Butter Jade" is softer serpentine (H2.5–5.5)',
        'Bowenite (Mg₃Si₂O₅(OH)₄ — antigorite variety) is notably tough for serpentine and has been used as a jade substitute for millennia',
        'Cream-yellow colour from suppression of typical Mg-serpentine green by low iron and trace impurities',
        'H2.5–5.5 depending on variety — handle carefully; bowenite end is tougher and more carvable',
        'Safe for water — magnesium silicate hydroxide; no toxic elements',
        'Major localities: Liaoning (China), Jeju Island (South Korea), Westland (New Zealand — tangiwai), South Africa (Barberton)',
      ],
      gaia_resonance: 'ViriditasHeart + AnchorPrism + ClarusLens',
      safety_warning:  'Safe for water. H2.5–5.5 — varies by variety; bowenite is tougher. No toxic elements. Misidentification common — most commercial Butter Jade is serpentine, not true jade. No significant hazards.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. BYSSOLITE
  // Fibrous actinolite / tremolite — amphibole group
  // Named from Greek byssos (fine flax) + lithos (stone) — the "mountain flax"
  // ⚠️ ASBESTOS WARNING — fibrous amphibole — collector mineral only
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Byssolite',
    mindat_id:    756,
    rruff_ids:    ['R040063'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Chrysotile',

    physical: {
      id:           756,
      longid:       'byssolite',
      guid:         '',
      name:         'Byssolite (fibrous actinolite / tremolite — Ca₂(Mg,Fe)₅Si₈O₂₂(OH)₂)',
      ima_formula:  'Ca₂(Mg,Fe)₅Si₈O₂₂(OH)₂',
      mindat_formula: 'Ca2(Mg,Fe)5Si8O22(OH)2',
      ima_status:   'A',
      ima_year:     1794,
      strunzten:    '9.DE.10',
      dana8ed:      '66.1.3.4',
      crystal_system: 'Monoclinic',
      hardness_min: 5,
      hardness_max: 6,
      specific_gravity_min: 2.98,
      specific_gravity_max: 3.20,
      cleavage:    'Perfect prismatic on {110} at ~60°/120° — characteristic of amphiboles',
      fracture:    'Uneven (fibrous — splits along fibre length)',
      tenacity:    'Flexible fibres; tough parallel to fibre length',
      luster:      ['Silky', 'Vitreous'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Pale grey-green to pale yellow-green, white-grey, pale silver-green — the muted, cool tones of fine flax or raw linen. Fibrous silky lustre catches light differently along each fibre.',
      streak:      'White to pale grey',
      fluorescence: 'None to weak pale yellow-white under LW UV',
      ri_min:      1.615,
      ri_max:      1.641,
      birefringence: 0.022,
      optical_type: 'B',
      shortdesc:   'Byssolite — fibrous actinolite/tremolite variety (Ca₂(Mg,Fe)₅Si₈O₂₂(OH)₂). Named from Greek byssos (fine flax). IMA 1794. FIBROUS AMPHIBOLE — ASBESTOS HAZARD. Silky grey-green fibres historically used as "mountain leather" and incombustible fabric. Collector mineral only.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-756.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Byssolite (Fibrous Actinolite/Tremolite)',
      refractive_index: { n_alpha: 1.615, n_beta: 1.628, n_gamma: 1.641 },
      birefringence:   0.022,
      optical_sign:    '-',
      dispersion:      'r < v, weak',
      pleochroism:     'Weak: pale green / pale yellow-green / pale grey-green',
      fluorescence_lw: 'None to weak pale yellow-white',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R040063'],
    },

    color: {
      primary_color:         'Pale grey-green to silver-green — the colour of raw linen and mountain mist',
      color_variants: [
        'Pale grey-green (most common — cool, misty)',
        'White-grey with silky sheen (tremolite-dominant)',
        'Pale yellow-green (actinolite-dominant, more Fe)',
        'Silver-white (near-pure tremolite end member)',
        'Pale olive-grey (moderate Fe content)',
      ],
      dominant_wavelength_nm: 540,
      oklch:   { l: 0.78, c: 0.05, h: 160 },
      hex:     '#c8d4c0',
      munsell: '5GY 8/2',
      color_temperature_k: null,
      psychological_effects: [
        'Silky fibrous lustre is one of the most tactilely arresting textures in mineralogy — fine mineral fibres that catch light like threads of spider silk',
        'The pale grey-green is the colour of early morning mountain light — cool, expansive, and deeply calming',
        'Historical use as incombustible cloth (mountain leather, mountain paper) gives the stone an almost mythological quality — fabric that cannot burn',
        'The same fibre structure that makes it historically useful also makes it medically hazardous — the stone teaches the dual nature of power',
        'Parallel fibres create a directional visual flow that the eye naturally follows — a guided meditation in mineral form',
      ],
      harmonics: {
        complementary_hue: 340,
        triadic_hues:      [280, 40],
        analogous_range:   [140, 180],
      },
    },

    metaphysical: {
      mineral_name:     'Byssolite',
      chakra_primary:   'Heart',
      chakra_secondary: ['Third Eye', 'Crown', 'Higher Heart (Thymus)'],
      element:   ['Air', 'Earth', 'Akasha'],
      planet:    ['Mercury', 'Neptune', 'Uranus'],
      archetype: ['The Mountain Weaver', 'The Incombustible Thread', 'The Dual-Edged Gift'],
      zodiac:    ['Gemini', 'Virgo', 'Aquarius'],
      numerology: 7,
      angel_number: 777,
      intention: 'I am threaded from the mountain itself. What cannot be burned in me is what I offer — the incombustible truth of my nature.',
      traditions: [
        'Named 1794 from Greek byssos (fine flax/linen) + lithos (stone) — the fibrous texture resembles fine spun linen or flax',
        '"Mountain flax" / "mountain leather" — fibrous amphibole asbestos used since antiquity for incombustible cloth; Charlemagne allegedly owned an asbestos tablecloth; Marco Polo described salamander cloth woven from mountain stone',
        'Pliny the Elder (Natural History, 77 AD) — described asbestos as "living in fire" and incombustible; the same fibrous amphibole family',
        'Alpine localities — classic byssolite specimens from Zermatt (Switzerland), Val d\'Aosta (Italy), and Zillertal (Austria); associated with chlorite schist metamorphic veins',
        'Modern crystal healing — used sparingly and only as display/collector stones; the safety story is central to responsible use',
      ],
      properties: [
        'Fibrous actinolite or tremolite — amphibole group; the fibrous habit defines "byssolite" as a varietal name for both actinolite and tremolite',
        'ASBESTOS FAMILY — fibrous amphibole minerals are classified as regulated hazardous materials in many jurisdictions',
        'Historical "mountain leather" (Bergkork) and "mountain paper" (Bergpapier) — flexible mats of compressed byssolite fibres used for fireproof linings, gaskets, and writing surfaces',
        'H5–6 but fibres split easily and are easily airborne — the fibres are the hazard, not the bulk mineral',
        'IMA 1794 — one of the earliest formally named mineral varieties',
        'Classic localities: Zermatt and Campolungo (Switzerland); Zillertal (Austria); Val d\'Aosta (Italy); Quebec (Canada)',
        'HANDLING: do not break, sand, cut, or disturb. Display in sealed case. Collector mineral ONLY.',
      ],
      gaia_resonance: 'ClarusLens + Noosphere',
      safety_warning:  '🚨 ASBESTOS HAZARD — fibrous amphibole (actinolite/tremolite asbestos). DO NOT break, cut, sand, grind, or disturb in any way. DO NOT use in water. Fibres are a known carcinogen (mesothelioma risk). Display only in sealed case or enclosure. Handle with extreme care using nitrile gloves. Not suitable for jewellery, tumbling, or any lapidary work. Collector museum specimen ONLY. Keep away from children and pets at all times.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. BYTOWNITE
  // Plagioclase feldspar — calcium-rich end: An70–An90
  // Named after Bytown (now Ottawa), Ontario, Canada — original locality
  // IMA recognised — golden labradorite of the feldspar series
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Bytownite',
    mindat_id:    1705,
    rruff_ids:    ['R040054'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Labradorite',

    physical: {
      id:           1705,
      longid:       'bytownite',
      guid:         '',
      name:         'Bytownite (plagioclase feldspar — An70–90)',
      ima_formula:  '(Ca,Na)(Al,Si)₄O₈',
      mindat_formula: '(Ca,Na)(Al,Si)4O8',
      ima_status:   'A',
      ima_year:     1835,
      strunzten:    '9.FA.35',
      dana8ed:      '76.1.3.2',
      crystal_system: 'Triclinic',
      hardness_min: 6,
      hardness_max: 6.5,
      specific_gravity_min: 2.72,
      specific_gravity_max: 2.75,
      cleavage:    'Perfect on {001}, good on {010} — characteristic feldspar right-angle cleavage',
      fracture:    'Uneven to conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Pearly on cleavage'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Colourless to pale yellow, golden-yellow, pale grey; gem-quality transparent crystals are the most prized — a golden, clean transparency rare in the feldspar series. Colour from trace Fe³⁺.',
      streak:      'White',
      fluorescence: 'Weak to none',
      ri_min:      1.562,
      ri_max:      1.583,
      birefringence: 0.011,
      optical_type: 'B',
      shortdesc:   'Bytownite — calcium-rich plagioclase feldspar (An70–90); triclinic. Named after Bytown (Ottawa), Ontario, Canada. IMA 1835. Pale golden-yellow transparent gem crystals from Mexico (San Luis Potosí) are most prized. The most Ca-rich of the common gem plagioclase feldspars after anorthite.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-1705.html',
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Bytownite (Plagioclase Feldspar)',
      refractive_index: { n_alpha: 1.562, n_beta: 1.568, n_gamma: 1.583 },
      birefringence:   0.011,
      optical_sign:    '+',
      dispersion:      '0.012',
      pleochroism:     'None to very weak',
      fluorescence_lw: 'None to weak orange-pink (locality dependent)',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 560, max: 595 },
      spectra: ['R040054'],
    },

    color: {
      primary_color:         'Colourless to pale golden-yellow — clean, clear, sunlit transparency',
      color_variants: [
        'Colourless (gem quality — purest, most transparent)',
        'Pale golden-yellow (most prized gem colour — trace Fe³⁺)',
        'Warm honey-gold (deeper Fe³⁺ colouration)',
        'Pale grey-white (lower gem quality, more included)',
        'Pale blue-grey (rare — structural or inclusion colour)',
      ],
      dominant_wavelength_nm: 578,
      oklch:   { l: 0.85, c: 0.10, h: 90 },
      hex:     '#f2e080',
      munsell: '2.5Y 9/6',
      color_temperature_k: null,
      psychological_effects: [
        'Clear golden-yellow transparency is one of the most immediately uplifting colour-light combinations in the mineral kingdom',
        'The feldspar perfect cleavage creates flash faces that rotate golden light around the crystal — a sundial effect',
        'Named after a city (Ottawa) that became a national capital — the stone carries a quiet geographic dignity',
        'Among the calcium-rich feldspars, bytownite occupies a zone of transition between labradorite (shows labradorescence) and anorthite (pure Ca end) — a stone of productive threshold',
        'Clean transparency lets the eye pass fully through the stone — no secrets, no opacity, nothing held back',
      ],
      harmonics: {
        complementary_hue: 270,
        triadic_hues:      [210, 330],
        analogous_range:   [70, 110],
      },
    },

    metaphysical: {
      mineral_name:     'Bytownite',
      chakra_primary:   'Solar Plexus',
      chakra_secondary: ['Crown', 'Third Eye'],
      element:   ['Air', 'Fire', 'Akasha'],
      planet:    ['Sun', 'Mercury', 'Jupiter'],
      archetype: ['The Golden Threshold', 'The Capital Mind', 'The Clear Witness'],
      zodiac:    ['Leo', 'Gemini', 'Sagittarius'],
      numerology: 1,
      angel_number: 111,
      intention: 'I stand at the threshold between two worlds and I am clear. My light passes through me without distortion.',
      traditions: [
        'Named after Bytown (renamed Ottawa in 1855), Ontario, Canada — the original type locality; now the national capital of Canada',
        'IMA 1835 — one of the early formally recognised members of the plagioclase feldspar series',
        'Plagioclase feldspar series: albite (Ab) → oligoclase → andesine → labradorite → bytownite → anorthite (An); bytownite occupies An70–90',
        'Mexican gem bytownite — transparent golden-yellow crystals from San Luis Potosí sold as "golden labradorite" or "yellow labradorite" in the gem trade',
        'Modern crystal healing — pale gold and yellow transparent feldspars used for Solar Plexus, mental clarity, and threshold work',
      ],
      properties: [
        'IMA 1835 — formula (Ca,Na)(Al,Si)₄O₈; triclinic crystal system; plagioclase feldspar series member An70–90',
        'The plagioclase series is a complete solid solution between albite (NaAlSi₃O₈) and anorthite (CaAl₂Si₂O₈); bytownite sits near the anorthite end',
        'Does NOT typically show labradorescence (that effect peaks at labradorite, An50–70); bytownite is valued for transparency and golden colour instead',
        'Gem-quality transparent golden-yellow crystals: San Luis Potosí, Mexico (most prized); also Ethiopia, Tanzania',
        'Rock-forming mineral in gabbro, basalt, anorthosite, and high-grade metamorphic rocks — one of the most abundant feldspar compositions in the deep crust',
        'H6–6.5 — moderate hardness; two cleavage directions; protect from harder minerals',
        'Safe for water — aluminosilicate; chemically stable; no toxic elements',
      ],
      gaia_resonance: 'ClarusLens + SovereignCore + Noosphere',
      safety_warning:  'Safe for water. H6–6.5 — moderate hardness; two cleavage planes — avoid impact. No toxic elements. Store away from harder minerals. No significant hazards.',
    },
  },

];

export default BATCH_B9;

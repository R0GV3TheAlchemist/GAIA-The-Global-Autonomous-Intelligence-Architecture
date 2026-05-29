/**
 * src/crystals/db/batch-b2.data.ts
 * GAIA-OS Crystal Database — Batch B-2
 *
 * Entries:
 *   1. Black Calcite
 *   2. Black Chalcedony
 *   3. Black Kyanite
 *   4. Black Mica (Biotite)
 *   5. Black Moonstone
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-29
 *
 * NOTE: This batch is the Black family — five distinct stones that all
 * carry the frequency of the void, protection, absorption, and depth.
 * Each has a different mechanism and therefore a different quality of darkness.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_B2: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. BLACK CALCITE
  // Trade name for black/dark grey manganese-rich or carbonaceous calcite
  // Darkness from organic carbon inclusions — the void held in limestone
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Black Calcite',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Selenite',

    physical: {
      id:           0,
      longid:       'black-calcite',
      guid:         '',
      name:         'Calcite (black/carbonaceous variety)',
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
      cleavage:    'Perfect rhombohedral on {10Ġ14}',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Waxy'],
      diaphaneity: ['Opaque'],
      colour:      'Black to dark grey from carbonaceous or manganese inclusions',
      streak:      'White to grey',
      fluorescence: null,
      ri_min:      1.486,
      ri_max:      1.658,
      birefringence: 0.172,
      optical_type: 'U',
      shortdesc:   'Trade name for calcite darkened by carbonaceous material or manganese oxide inclusions. Soft, heavy for its size, with the amplifying base of calcite beneath a void-frequency surface.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-859.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Black Calcite',
      refractive_index: { n_omega: 1.658, n_epsilon: 1.486 },
      birefringence:   0.172,
      optical_sign:    '-',
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: [],
    },

    color: {
      primary_color:          'Black to deep charcoal',
      color_variants:         ['Jet black', 'Dark grey', 'Charcoal', 'Black with white veining'],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.15, c: 0.01, h: 0 },
      hex:     '#1a1a1a',
      munsell: 'N1.5/',
      color_temperature_k:    null,
      psychological_effects:  [
        'The void without aggression — softer darkness than obsidian or tourmaline',
        'Calcite\'s amplifying base beneath black surface creates a quiet absorptive field',
        'Encourages honest introspection and shadow integration without confrontation',
        'Resting in the dark — not fighting it, not fleeing it, simply being with it',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Black Calcite',
      chakra_primary:   'Root',
      chakra_secondary: ['Earth Star'],
      element:   ['Earth'],
      planet:    ['Saturn', 'Pluto'],
      archetype: ['The Quiet Void', 'The Shadow Integrator'],
      zodiac:    ['Scorpio', 'Capricorn'],
      numerology: 8,
      angel_number: 444,
      intention: 'I rest in the dark and find what has always been here waiting.',
      traditions: ['Western crystal healing', 'Shamanic shadow work'],
      properties: [
        'The gentlest of the black stones — darkness held in calcite\'s soft amplifying matrix',
        'Unlike obsidian or tourmaline, Black Calcite does not repel — it absorbs and transforms gently',
        'Useful for shadow integration work, grief processing, and facing what has been avoided',
        'Supports deep sleep and dreamwork in the lower frequencies',
        'The calcite base amplifies whatever intention is set — powerful for void meditation',
        'Rare in the crystal market — less known than other black stones, more nuanced in its work',
      ],
      gaia_resonance: 'AnchorPrism + SomnusVeil',
      safety_warning: 'Calcite is water-soluble — do not submerge or use for water elixirs.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. BLACK CHALCEDONY
  // Microcrystalline quartz with carbon/organic dark inclusions
  // Smooth, matte, dense — the sealing stone
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Black Chalcedony',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'White Chalcedony',

    physical: {
      id:           0,
      longid:       'black-chalcedony',
      guid:         '',
      name:         'Chalcedony (black variety)',
      ima_formula:  'SiO₂',
      mindat_formula: 'SiO2',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '4.DA.05',
      dana8ed:      '75.1.3.1',
      crystal_system: 'Trigonal',
      hardness_min: 6.5,
      hardness_max: 7,
      specific_gravity_min: 2.58,
      specific_gravity_max: 2.64,
      cleavage:    'None',
      fracture:    'Conchoidal',
      tenacity:    'Brittle',
      luster:      ['Waxy', 'Dull'],
      diaphaneity: ['Opaque', 'Translucent'],
      colour:      'Black to very dark grey, sometimes with translucent edges',
      streak:      'White',
      fluorescence: null,
      ri_min:      1.530,
      ri_max:      1.539,
      birefringence: 0.004,
      optical_type: 'U',
      shortdesc:   'Trade name for microcrystalline quartz (chalcedony) darkened by carbonaceous or organic inclusions. Smooth, dense, waxy lustre. Often confused with black onyx.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  null,
      piezoelectric:    true,
      safe_for_water:   true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name: 'Black Chalcedony',
      refractive_index: { n_omega: 1.539, n_epsilon: 1.530 },
      birefringence:   0.004,
      optical_sign:    '-',
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: [],
    },

    color: {
      primary_color:          'Dense matte black',
      color_variants:         ['Jet black', 'Dark grey-black', 'Black with translucent edge'],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.12, c: 0.01, h: 0 },
      hex:     '#141414',
      munsell: 'N1/',
      color_temperature_k:    null,
      psychological_effects:  [
        'The most visually sealed of the black stones — waxy matte surface absorbs rather than reflects',
        'Creates a sense of containment and privacy — a sealed energetic field',
        'Dense and inert — does not amplify or project, simply holds',
        'The smoothness invites touch — a grounding tactile frequency',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Black Chalcedony',
      chakra_primary:   'Root',
      chakra_secondary: ['Earth Star', 'Sacral'],
      element:   ['Earth'],
      planet:    ['Saturn'],
      archetype: ['The Sealed Vessel', 'The Guardian'],
      zodiac:    ['Scorpio', 'Capricorn', 'Sagittarius'],
      numerology: 4,
      angel_number: 444,
      intention: 'My energy is sealed, contained, and wholly my own.',
      traditions: ['Western crystal healing', 'Roman and Greek talismanic tradition', 'Native American healing tradition'],
      properties: [
        'Protective and sealing — creates an energetic boundary without aggression',
        'The smooth waxy surface has been used in talisman carving for millennia',
        'Less common than black onyx and therefore often overlooked — its quietness is its power',
        'Supports inner strength, self-containment, and calm authority',
        'Useful for those who absorb others\' energies — the sealed chalcedony field acts as insulation',
        'Distinct from Black Onyx in metaphysical community despite mineralogical similarity',
      ],
      gaia_resonance: 'AnchorPrism + SovereignCore',
      safety_warning: null,
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. BLACK KYANITE
  // Al₂SiO₅ — fan-shaped bladed crystals — the auric sweeper
  // Darkness from iron and manganese substitution
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Black Kyanite',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Blue Kyanite',

    physical: {
      id:           0,
      longid:       'black-kyanite',
      guid:         '',
      name:         'Kyanite (black variety)',
      ima_formula:  'Al₂SiO₅',
      mindat_formula: 'Al2SiO5',
      ima_status:   'A',
      ima_year:     null,
      strunzten:    '9.AF.20',
      dana8ed:      '52.2.2.1',
      crystal_system: 'Triclinic',
      hardness_min: 4.5,
      hardness_max: 7,
      specific_gravity_min: 3.53,
      specific_gravity_max: 3.70,
      cleavage:    'Perfect on {100}, good on {010}',
      fracture:    'Splintery',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Pearly'],
      diaphaneity: ['Opaque', 'Translucent'],
      colour:      'Black to very dark grey-green from iron and manganese substitution',
      streak:      'White to grey',
      fluorescence: null,
      ri_min:      1.712,
      ri_max:      1.734,
      birefringence: 0.017,
      optical_type: 'B',
      shortdesc:   'Iron and manganese-rich variety of kyanite forming characteristic fan-shaped or blade-shaped crystal aggregates. Unique variable hardness along crystal axes.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-2303.html',
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Black Kyanite',
      refractive_index: { n_alpha: 1.712, n_beta: 1.720, n_gamma: 1.734 },
      birefringence:   0.017,
      optical_sign:    '-',
      dispersion:      null,
      pleochroism:     'Weak in dark varieties',
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: [],
    },

    color: {
      primary_color:          'Black with dark grey-green undertones',
      color_variants:         ['Jet black', 'Dark grey-black', 'Black with metallic sheen', 'Dark grey-green'],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.14, c: 0.02, h: 155 },
      hex:     '#181c18',
      munsell: 'N1.5/',
      color_temperature_k:    null,
      psychological_effects:  [
        'Active darkness — unlike the stillness of Black Calcite, the blade form feels like directed will',
        'The fan/blade geometry creates a sense of sweeping and clearing',
        'Directional energy — black kyanite moves, it does not simply absorb',
        'Combines the depth of black with the cutting precision of kyanite\'s bladed structure',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Black Kyanite',
      chakra_primary:   'Root',
      chakra_secondary: ['Earth Star', 'Third Eye'],
      element:   ['Earth', 'Storm'],
      planet:    ['Saturn', 'Pluto'],
      archetype: ['The Auric Surgeon', 'The Cord Cutter'],
      zodiac:    ['Aries', 'Taurus', 'Libra'],
      numerology: 4,
      angel_number: 444,
      intention: 'I cut what no longer serves and sweep the field clean.',
      traditions: ['Western crystal healing', 'Auric field work', 'Shamanic clearing'],
      properties: [
        'The most actively protective of the black stones — its blade form is used to sweep the aura',
        'Fan-shaped crystal aggregates are physically held and swept downward through the energy field',
        'Excellent for cord-cutting, entity removal, and clearing psychic debris',
        'Like all kyanite varieties, it does not accumulate negative energy and rarely needs cleansing',
        'The directionality of the blades gives it a surgical quality — precise rather than broad',
        'Grounds high-vibrational work done with Blue Kyanite — the natural yin-yang pair',
      ],
      gaia_resonance: 'AnchorPrism + SovereignCore',
      safety_warning: null,
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. BLACK MICA (BIOTITE)
  // Potassium iron magnesium aluminosilicate — the layered mirror
  // Perfect basal cleavage — peels into infinite thin sheets
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Black Mica',
    mindat_id:   769,
    rruff_ids:   ['R040055', 'R050055'],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'Muscovite',

    physical: {
      id:           769,
      longid:       'biotite',
      guid:         '',
      name:         'Biotite',
      ima_formula:  'K(Mg,Fe)₃(AlSi₃O₁₀)(OH,F)₂',
      mindat_formula: 'K(Mg,Fe)3(AlSi3O10)(OH,F)2',
      ima_status:   'A',
      ima_year:     1847,
      strunzten:    '9.EC.20',
      dana8ed:      '71.2.2.1',
      crystal_system: 'Monoclinic',
      hardness_min: 2.5,
      hardness_max: 3,
      specific_gravity_min: 2.70,
      specific_gravity_max: 3.30,
      cleavage:    'Perfect basal on {001} — peels into flexible elastic sheets',
      fracture:    null,
      tenacity:    'Elastic — thin sheets are flexible and spring back',
      luster:      ['Vitreous', 'Pearly', 'Submetallic'],
      diaphaneity: ['Transparent', 'Translucent', 'Opaque'],
      colour:      'Black, dark brown, dark green — iron-rich dark mica',
      streak:      'White to grey',
      fluorescence: null,
      ri_min:      1.565,
      ri_max:      1.640,
      birefringence: 0.040,
      optical_type: 'B',
      shortdesc:   'Common iron-magnesium mica forming thin, perfectly cleavable sheets. Essential component of granites and metamorphic rocks. The dark mirror of Muscovite.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-769.html',
      piezoelectric:    false,
      safe_for_water:   false,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Black Mica',
      refractive_index: { n_alpha: 1.565, n_beta: 1.610, n_gamma: 1.640 },
      birefringence:   0.040,
      optical_sign:    '-',
      dispersion:      null,
      pleochroism:     'Strong: yellow-brown / dark brown / nearly opaque',
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: ['R040055', 'R050055'],
    },

    color: {
      primary_color:          'Black with submetallic sheen',
      color_variants:         ['Jet black', 'Dark brown-black', 'Dark olive-black', 'Golden sheen on thin sheets'],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.16, c: 0.02, h: 60 },
      hex:     '#1e1c14',
      munsell: 'N1.5/',
      color_temperature_k:    null,
      psychological_effects:  [
        'The darkness that reflects — pearlescent black surface creates a subtle mirror quality',
        'Layered structure mirrors the layering of the psyche — each sheet a different depth',
        'Flexible yet structured — the elastic sheets model resilience within form',
        'Submetallic sheen gives it a living quality — not dead black but luminous black',
      ],
      harmonics: {
        complementary_hue: null,
        triadic_hues:      null,
        analogous_range:   null,
      },
    },

    metaphysical: {
      mineral_name:     'Black Mica',
      chakra_primary:   'Root',
      chakra_secondary: ['Earth Star', 'Crown'],
      element:   ['Earth', 'Fire'],
      planet:    ['Saturn', 'Mars'],
      archetype: ['The Layered Mirror', 'The Resilient Dark'],
      zodiac:    ['Scorpio', 'Leo'],
      numerology: 8,
      angel_number: 444,
      intention: 'I peel back every layer and find the light that was always beneath.',
      traditions: ['Western crystal healing', 'Shamanic mirror work', 'Vedic tradition'],
      properties: [
        'The perfectly cleavable sheets make it a literal mirror — used in scrying and reflective work',
        'Each layer that peels away represents a layer of conditioning, mask, or armour released',
        'Its elasticity (thin sheets bend and spring back) embodies the resilience it supports',
        'Grounding with a metallic sheen — darker and more structured than other grounding stones',
        'Often embedded in granite — it knows how to hold form within larger structures',
        'The Crown-Root axis makes it useful for integrating spiritual experience into physical reality',
      ],
      gaia_resonance: 'AnchorPrism + ClarusLens',
      safety_warning: 'Very thin cleavage sheets have sharp edges — handle with care. Do not use for water elixirs. Dust inhalation should be avoided.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. BLACK MOONSTONE
  // Dark labradorite or dark feldspar variety — the new moon stone
  // Adularescence in dark tones — light moving in the dark
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:        'Black Moonstone',
    mindat_id:   null,
    rruff_ids:   [],
    last_synced: '2026-05-29T00:00:00Z',
    trade_name:  true,
    color_layer: 'natural',
    yin_yang_pair: 'White Moonstone',

    physical: {
      id:           0,
      longid:       'black-moonstone',
      guid:         '',
      name:         'Feldspar (dark labradorite / dark orthoclase variety)',
      ima_formula:  '(Ca,Na)(Al,Si)₄O₈ or KAlSi₃O₈',
      mindat_formula: '(Ca,Na)(Al,Si)4O8 or KAlSi3O8',
      ima_status:   null,
      ima_year:     null,
      strunzten:    '9.FA.35',
      dana8ed:      '76.1.3.1',
      crystal_system: 'Monoclinic',
      hardness_min: 6,
      hardness_max: 6.5,
      specific_gravity_min: 2.56,
      specific_gravity_max: 2.76,
      cleavage:    'Perfect on {001}, good on {010}',
      fracture:    'Uneven to conchoidal',
      tenacity:    'Brittle',
      luster:      ['Vitreous', 'Pearly'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Dark grey to black with white, silver or peach adularescent sheen',
      streak:      'White',
      fluorescence: null,
      ri_min:      1.518,
      ri_max:      1.590,
      birefringence: 0.010,
      optical_type: 'B',
      shortdesc:   'Trade name for dark grey to black feldspar (typically dark labradorite from Madagascar) showing adularescent sheen — light appears to move within a dark stone. The new moon embodied.',
      updttime:    '2026-05-29T00:00:00Z',
      mindat_url:  null,
      piezoelectric:    false,
      safe_for_water:   true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name: 'Black Moonstone',
      refractive_index: { n_alpha: 1.518, n_beta: 1.524, n_gamma: 1.526 },
      birefringence:   0.010,
      optical_sign:    '+',
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: null,
      fluorescence_sw: null,
      phosphorescence: null,
      visible_wavelength_nm: null,
      spectra: [],
    },

    color: {
      primary_color:          'Dark grey-black with adularescent silver or peach sheen',
      color_variants:         ['Dark charcoal with silver sheen', 'Black with white flash', 'Dark grey with peach shimmer'],
      dominant_wavelength_nm: null,
      oklch:   { l: 0.22, c: 0.03, h: 280 },
      hex:     '#2a2830',
      munsell: 'N2/',
      color_temperature_k:    null,
      psychological_effects:  [
        'The most paradoxical visual experience in the black family — light moving inside darkness',
        'The adularescence is hope visible within the void — the new moon holding potential',
        'Quieter and more interior than white moonstone — the inward feminine rather than the luminous one',
        'Supports deep inner knowing, the unconscious, and the unseen becoming slowly visible',
      ],
      harmonics: {
        complementary_hue: 100,
        triadic_hues:      [40, 160],
        analogous_range:   [260, 300],
      },
    },

    metaphysical: {
      mineral_name:     'Black Moonstone',
      chakra_primary:   'Root',
      chakra_secondary: ['Sacral', 'Crown'],
      element:   ['Earth', 'Water'],
      planet:    ['Moon', 'Saturn'],
      archetype: ['The New Moon', 'The Dark Feminine', 'The Keeper of Potential'],
      zodiac:    ['Cancer', 'Scorpio', 'Capricorn'],
      numerology: 2,
      angel_number: 222,
      intention: 'In the darkness I hold everything that is about to become.',
      traditions: [
        'Western crystal healing',
        'Lunar tradition — new moon intention setting',
        'Divine feminine mystery traditions',
      ],
      properties: [
        'The new moon stone — where white moonstone is the full moon, black moonstone is the new moon',
        'Embodies potential before manifestation — the seed in the dark earth',
        'The adularescent sheen moving in dark stone is the most direct visual metaphor for the unconscious',
        'Supports new beginnings, planting intentions, and gestation of what has not yet been born',
        'The dark feminine archetype — not death but the fertile void before creation',
        'Angel number 222 — alignment and divine timing — the new moon is always about right timing',
      ],
      gaia_resonance: 'SomnusVeil + ViriditasHeart + AnchorPrism',
      safety_warning: null,
    },
  },

];

export default BATCH_B2;

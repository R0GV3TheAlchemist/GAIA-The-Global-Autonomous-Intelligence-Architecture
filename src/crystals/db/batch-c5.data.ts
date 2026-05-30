/**
 * src/crystals/db/batch-c5.data.ts
 * GAIA-OS Crystal Database — Batch C-5
 *
 * Entries:
 *   1. Chlorite      — Mg-Fe phyllosilicate group; phantom inclusions; earth healer
 *   2. Chrysoberyl   — BeAl₂O₄; parent of alexandrite and cat’s eye; IMA recognised
 *   3. Chrysocolla   — Cu-bearing hydrated silicate; blue-green — TOXIC
 *   4. Chrysoprase   — Ni-chalcedony; finest apple-green chalcedony variety
 *   5. Cinnabar      — HgS; mercury sulphide; vermilion red — HIGHLY TOXIC
 *
 * Schema: CrystalRecord v1.3
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-30
 *
 * SAFETY NOTE: Chrysocolla (copper), and especially Cinnabar (mercury), are
 * among the most dangerous minerals in the crystal healing canon.
 * Cinnabar is HIGHLY TOXIC — mercury sulphide; handle with extreme caution.
 */

import type { CrystalRecord } from './crystal.schema';

const BATCH_C5: CrystalRecord[] = [

  // ─────────────────────────────────────────────────────────────────────────
  // 1. CHLORITE
  // Mg-Fe phyllosilicate group — (Mg,Fe)₃(Si,Al)₄O₁₀(OH)₈
  // Named from Greek chloros (green)
  // IMA recognised — phantom quartz inclusions; earth and nature healer
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Chlorite',
    mindat_id:    1016,
    rruff_ids:    ['R060842'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Epidote',

    physical: {
      id:           1016,
      longid:       'chlorite',
      guid:         '',
      name:         'Chlorite (group — clinochlore, chamosite, pennantite, nimite, cookeite)',
      ima_formula:  '(Mg,Fe)₃(Si,Al)₄O₁₀(OH)₈',
      mindat_formula: '(Mg,Fe)3(Si,Al)4O10(OH)8',
      ima_status:   'A',
      ima_year:     1820,
      strunzten:    '9.EC.05',
      dana8ed:      '71.4.1.1',
      crystal_system: 'Monoclinic',
      hardness_min: 2,
      hardness_max: 2.5,
      specific_gravity_min: 2.60,
      specific_gravity_max: 3.30,
      cleavage:    'Perfect basal on {001} — yields flexible (non-elastic) plates',
      fracture:    'Uneven (across cleavage)',
      tenacity:    'Flexible but inelastic (cleavage plates)',
      luster:      ['Vitreous', 'Pearly (on cleavage)', 'Waxy'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Green to dark green (most common); also pale green, yellowish-green, brownish-green, rarely white or pink. Depth of green from Fe²⁺/Fe³⁺ content. In quartz: forms classic green phantom inclusions.',
      streak:      'Pale green to white',
      fluorescence: 'None to weak',
      ri_min:      1.571,
      ri_max:      1.588,
      birefringence: 0.010,
      optical_type: 'B',
      shortdesc:   'Chlorite — (Mg,Fe)₃(Si,Al)₄O₁₀(OH)₈, monoclinic Mg-Fe phyllosilicate group. Named from Greek chloros (green). IMA 1820. Best known as green phantom inclusions in quartz (Chlorite Phantom Quartz). Soft (H2–2.5), perfectly cleaving, flexible plates.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-1016.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Chlorite',
      refractive_index: { n_alpha: 1.571, n_beta: 1.580, n_gamma: 1.588 },
      birefringence:   0.010,
      optical_sign:    '+',
      dispersion:      'r > v, weak',
      pleochroism:     'Distinct: pale green / deeper green / yellow-green',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 510, max: 560 },
      spectra: ['R060842'],
    },

    color: {
      primary_color:         'Green — the essential green of the Earth; from pale sage to deep forest',
      color_variants: [
        'Pale sage-green (low Fe — clinochlore dominant)',
        'Medium forest green (balanced Fe²⁺/Mg)',
        'Deep dark green (high Fe²⁺ — chamosite dominant)',
        'Yellowish-green (Mg-dominant, low Fe)',
        'Brownish-green (oxidised surface or high Fe³⁺)',
        'Phantom green in quartz — ghost layer of green chlorite marking a growth pause',
      ],
      dominant_wavelength_nm: 535,
      oklch:   { l: 0.45, c: 0.18, h: 145 },
      hex:     '#3a7a4a',
      munsell: '5G 4/6',
      color_temperature_k: null,
      psychological_effects: [
        'Green is the most restful colour for the human eye — the wavelength at which the retina requires no adjustment; chlorite embodies this perfectly',
        'Phantom quartz with chlorite inclusions tells a story of interrupted growth — the ghost of a former crystal boundary made visible',
        'The soft, flexible cleavage plates communicate earthiness and yield — not brittle, not hard, but soft and accommodating like moss',
        'Deep forest green at low saturation is the colour of ancient woodland — one of the most primal environmental colour memories in human psychology',
        'Chlorite as the green layer in quartz phantoms makes the invisible (time) visible — geology as memory',
      ],
      harmonics: {
        complementary_hue: 325,
        triadic_hues:      [265, 25],
        analogous_range:   [125, 165],
      },
    },

    metaphysical: {
      mineral_name:     'Chlorite',
      chakra_primary:   'Heart',
      chakra_secondary: ['Root', 'Earth Star', 'Higher Heart (Thymus)'],
      element:   ['Earth', 'Water'],
      planet:    ['Venus', 'Earth', 'Moon'],
      archetype: ['The Earth Healer', 'The Green Phantom', 'The Memory of Growth'],
      zodiac:    ['Taurus', 'Virgo', 'Cancer'],
      numerology: 6,
      angel_number: 666,
      intention: 'I hold the memory of every layer of growth. The Earth heals through me. I am the green that returns after every ending.',
      traditions: [
        'Named 1820 from Greek chloros (green) by Werner — for its characteristic green colour',
        'Chlorite Phantom Quartz — one of the most sought-after quartz varieties in crystal healing; the green phantom layer records a growth pause and resumption',
        'Widespread metamorphic mineral — chlorite forms in greenschist facies; the green colour of many mountain ranges and metamorphic belts worldwide',
        'Alpine tradition — chlorite-bearing schists are the matrix for many Alpine gem minerals (brookite, albite, rutile)',
        'Modern crystal healing — chlorite phantom quartz used for Earth healing, nature connection, and accessing plant and forest consciousness',
      ],
      properties: [
        'IMA 1820 — Chlorite group includes clinochlore, chamosite, pennantite, nimite, cookeite — all Mg-Fe-Al phyllosilicates',
        'Perfect basal cleavage yields flexible (non-elastic) plates — similar to talc and brucite in tactile quality',
        'Forms green phantom layers in quartz when quartz growth pauses and chlorite precipitates on the crystal surface, then quartz growth resumes',
        'H2–2.5 — very soft; standalone crystals fragile; inclusions in quartz are fully protected by the host',
        'DO NOT use in water — phyllosilicate; Fe-bearing varieties may stain; avoid prolonged contact',
        'No toxic elements — Mg, Fe, Si, Al, OH; chemically benign',
        'Major localities: Alps (Switzerland, Austria), Brazil, India, Russia; chlorite phantom quartz from Brazil (Minas Gerais) and Madagascar',
      ],
      gaia_resonance: 'ViriditasHeart + AnchorPrism + Noosphere',
      safety_warning:  '⚠️ DO NOT use in water — phyllosilicate; Fe-bearing varieties may leach or stain. H2–2.5 standalone — very soft and fragile; inclusions in quartz are safe to handle normally. No toxic elements.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 2. CHRYSOBERYL
  // BeAl₂O₄ — beryllium aluminium oxide; orthorhombic
  // Named from Greek chrysos (gold) + beryllos (beryl)
  // Parent of alexandrite (colour-change) and Cat’s Eye chrysoberyl
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Chrysoberyl',
    mindat_id:    1020,
    rruff_ids:    ['R050125'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Alexandrite',

    physical: {
      id:           1020,
      longid:       'chrysoberyl',
      guid:         '',
      name:         'Chrysoberyl (parent species — varieties: alexandrite, cat’s eye chrysoberyl, cymophane)',
      ima_formula:  'BeAl₂O₄',
      mindat_formula: 'BeAl2O4',
      ima_status:   'A',
      ima_year:     1789,
      strunzten:    '4.BA.05',
      dana8ed:      '7.2.3.1',
      crystal_system: 'Orthorhombic',
      hardness_min: 8.5,
      hardness_max: 8.5,
      specific_gravity_min: 3.68,
      specific_gravity_max: 3.78,
      cleavage:    'Distinct on {011}, imperfect on {010}',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle',
      luster:      ['Vitreous'],
      diaphaneity: ['Transparent', 'Translucent'],
      colour:      'Yellow to yellow-green to golden-green (type); alexandrite variety: green in daylight, red-purple in incandescent light; cat’s eye: any colour with silky chatoyancy. Colour from Fe³⁺ (yellow) or Cr³⁺ (alexandrite, green).',
      streak:      'White',
      fluorescence: 'Weak red under LW UV (Cr-bearing varieties — alexandrite); none in Fe-bearing type',
      ri_min:      1.745,
      ri_max:      1.757,
      birefringence: 0.009,
      optical_type: 'B',
      shortdesc:   'Chrysoberyl — BeAl₂O₄, orthorhombic beryllium aluminium oxide. H8.5 — third hardest natural mineral after diamond and corundum. Named 1789. Parent species of alexandrite (Cr³⁺ colour-change) and Cat’s Eye chrysoberyl (chatoyancy). Golden-yellow to green.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-1020.html',
      piezoelectric:     false,
      safe_for_water:    true,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Chrysoberyl',
      refractive_index: { n_alpha: 1.745, n_beta: 1.748, n_gamma: 1.757 },
      birefringence:   0.009,
      optical_sign:    '+',
      dispersion:      '0.015',
      pleochroism:     'Alexandrite: strong trichroism — red / orange / green; type chrysoberyl: weak yellow / yellow-green',
      fluorescence_lw: 'Weak red (Cr-bearing / alexandrite); none (Fe-bearing)',
      fluorescence_sw: 'None to weak',
      phosphorescence: null,
      visible_wavelength_nm: { min: 550, max: 590 },
      spectra: ['R050125'],
    },

    color: {
      primary_color:         'Golden-yellow to yellow-green (type); green/red colour-change (alexandrite); chatoyant (cat’s eye)',
      color_variants: [
        'Golden-yellow (Fe³⁺ — type chrysoberyl)',
        'Yellow-green to mint green (Fe³⁺ + Cr³⁺)',
        'Alexandrite: vivid green in daylight / red-purple in incandescent light (Cr³⁺)',
        'Cat’s Eye (cymophane): honey-yellow with sharp white chatoyant line',
        'Colourless to near-white (rare — low Fe/Cr)',
      ],
      dominant_wavelength_nm: 570,
      oklch:   { l: 0.72, c: 0.18, h: 100 },
      hex:     '#c8b832',
      munsell: '2.5Y 7/8',
      color_temperature_k: null,
      psychological_effects: [
        'Alexandrite’s colour change is one of the most psychologically powerful optical phenomena in gemology — the stone transforms completely between light sources',
        'Cat’s Eye chatoyancy — the sharp, mobile white line — creates an uncanny impression of a living eye within the stone',
        'H8.5 combined with transparency gives chrysoberyl the quality of something that should not exist in nature — too hard, too clear, too perfect',
        'Golden-yellow type chrysoberyl has the warmth of old honey — saturated, deep, resinous',
        'The Cr³⁺ dual absorption — transmitting both red and green — is a quantum optical phenomenon expressed as visible magic',
      ],
      harmonics: {
        complementary_hue: 280,
        triadic_hues:      [220, 340],
        analogous_range:   [80, 120],
      },
    },

    metaphysical: {
      mineral_name:     'Chrysoberyl',
      chakra_primary:   'Solar Plexus',
      chakra_secondary: ['Crown', 'Third Eye', 'Heart'],
      element:   ['Fire', 'Akasha', 'Earth'],
      planet:    ['Sun', 'Mercury', 'Jupiter'],
      archetype: ['The Golden Eye', 'The Colour Changer', 'The Third Hardest'],
      zodiac:    ['Leo', 'Gemini', 'Aquarius'],
      numerology: 6,
      angel_number: 666,
      intention: 'I see the same truth in two different lights. My nature does not change — only the light around me does.',
      traditions: [
        'Named 1789 by Abraham Gottlob Werner from Greek chrysos (gold) + beryllos (beryl) — though it is not a beryl species',
        'Alexandrite — discovered 1830 in the Ural Mountains, Russia; named after Tsar Alexander II; became the Russian imperial gemstone; colour change coincided with Russian national colours (green + red)',
        'Cat’s Eye (cymophane) — the original and premier chatoyant gemstone; "the" cat’s eye without qualification; Sri Lanka and Brazil primary sources',
        'Vedic astrology (Jyotish) — Cat’s Eye chrysoberyl (lehsunia/vaidurya) is the gem for Ketu (south lunar node); one of the nine Navaratna gems',
        'Victorian England — alexandrite became extremely fashionable after discovery in Russia; highly prized in Victorian and Edwardian jewellery',
      ],
      properties: [
        'IMA 1789 — formula BeAl₂O₄; orthorhombic beryllium aluminium oxide',
        'H8.5 — third hardest natural mineral after diamond (10) and corundum (9); extremely durable for jewellery',
        'Three gem varieties: type chrysoberyl (yellow-green), alexandrite (Cr³⁺ colour-change), cymophane/cat’s eye (chatoyancy from parallel rutile/ilmenite needles)',
        'Alexandrite colour-change: Cr³⁺ transmits both red and green wavelengths; daylight (blue-rich) reveals green, incandescent (red-rich) reveals red',
        'Safe for water — BeAl₂O₄ is chemically stable and non-toxic at the mineral level',
        'Note: beryllium is toxic as dust/powder — do not grind; finished stones are safe',
        'Major localities: Ural Mountains (Russia — alexandrite), Sri Lanka (cat’s eye), Brazil (Minas Gerais), Myanmar, Zimbabwe',
      ],
      gaia_resonance: 'ClarusLens + SovereignCore + QuantumNexus',
      safety_warning:  'Safe for water. H8.5 — extremely durable. NOTE: beryllium is toxic as dust — do not grind, sand, or cut without industrial respiratory protection. Finished, polished stones are safe for normal handling and water contact.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 3. CHRYSOCOLLA
  // Hydrated copper silicate — (Cu,Al)₂H₂Si₂O₅(OH)₄·nH₂O
  // Named from Greek chrysos (gold) + kolla (glue) — used in gold soldering
  // Vivid blue-green; soft; often mixed with quartz, malachite, azurite
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Chrysocolla',
    mindat_id:    1030,
    rruff_ids:    ['R060663'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Malachite',

    physical: {
      id:           1030,
      longid:       'chrysocolla',
      guid:         '',
      name:         'Chrysocolla',
      ima_formula:  '(Cu,Al)₂H₂Si₂O₅(OH)₄·nH₂O',
      mindat_formula: '(Cu,Al)2H2Si2O5(OH)4·nH2O',
      ima_status:   'A',
      ima_year:     1968,
      strunzten:    '9.ED.20',
      dana8ed:      '74.3.2.1',
      crystal_system: 'Orthorhombic (poorly crystalline; often amorphous)',
      hardness_min: 2,
      hardness_max: 4,
      specific_gravity_min: 1.93,
      specific_gravity_max: 2.40,
      cleavage:    'None',
      fracture:    'Conchoidal to uneven',
      tenacity:    'Brittle to sectile',
      luster:      ['Vitreous', 'Waxy', 'Earthy'],
      diaphaneity: ['Translucent', 'Opaque'],
      colour:      'Vivid blue to blue-green to cyan-green — one of the most saturated natural blue-greens. Colour from Cu²⁺. Often mixed with malachite (green), azurite (blue), quartz (hardened gem chrysocolla), and limonite (brown).',
      streak:      'White to pale blue-green',
      fluorescence: 'None',
      ri_min:      1.460,
      ri_max:      1.570,
      birefringence: null,
      optical_type: null,
      shortdesc:   'Chrysocolla — (Cu,Al)₂H₂Si₂O₅(OH)₄·nH₂O, hydrated copper silicate. TOXIC. Named from Greek chrysos + kolla (gold glue). IMA 1968. Vivid blue to blue-green from Cu²⁺. Often mixed with malachite, azurite, and quartz. Soft (H2–4) unless silicated.',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-1030.html',
      piezoelectric:     false,
      safe_for_water:    false,
      safe_for_hardware: false,
    },

    optical: {
      mineral_name:    'Chrysocolla',
      refractive_index: { n_mean: 1.500 },
      birefringence:   null,
      optical_sign:    null,
      dispersion:      null,
      pleochroism:     null,
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 470, max: 520 },
      spectra: ['R060663'],
    },

    color: {
      primary_color:         'Vivid blue to blue-green to cyan-green — the colour of a tropical river seen from above',
      color_variants: [
        'Vivid sky-blue to cyan (pure Cu²⁺-dominant)',
        'Blue-green (most common — mixed Cu silicate)',
        'Deep teal-green (higher Si, lower Cu)',
        'Turquoise-blue (mixed with quartz — "gem chrysocolla" or Parrot Wing)',
        'Multi-tone blue-green-brown (Sonora Sunrise — mixed malachite, cuprite, chrysocolla)',
      ],
      dominant_wavelength_nm: 495,
      oklch:   { l: 0.58, c: 0.22, h: 195 },
      hex:     '#2a9a8a',
      munsell: '5BG 5/8',
      color_temperature_k: null,
      psychological_effects: [
        'The blue-green of chrysocolla is one of the most emotionally complex colour combinations — simultaneously sky, water, forest, and earth',
        'The waxy, softly translucent surface creates an impression of depth — as though the colour extends inward',
        'Chrysocolla’s historical name (gold glue) creates an interesting inversion — the most vivid blue-green named for gold',
        'Mixed chrysocolla specimens (malachite, azurite, cuprite) offer the complete copper colour family in a single stone',
        'The cyan-green-blue palette is among the most universally calming in human colour psychology — it reads as water and sky simultaneously',
      ],
      harmonics: {
        complementary_hue: 15,
        triadic_hues:      [315, 75],
        analogous_range:   [175, 215],
      },
    },

    metaphysical: {
      mineral_name:     'Chrysocolla',
      chakra_primary:   'Throat',
      chakra_secondary: ['Heart', 'Third Eye', 'Higher Heart (Thymus)'],
      element:   ['Water', 'Earth'],
      planet:    ['Venus', 'Moon', 'Neptune'],
      archetype: ['The Voice of the Earth', 'The Copper Healer', 'The Blue-Green Goddess'],
      zodiac:    ['Taurus', 'Gemini', 'Virgo'],
      numerology: 5,
      angel_number: 555,
      intention: 'I speak with the voice of rivers and copper veins. My truth is the blue-green of deep healing.',
      traditions: [
        'Named by Theophrastus (315 BCE) from Greek chrysos (gold) + kolla (glue) — used in antiquity as a flux for gold soldering',
        'Ancient Egypt — Cleopatra reportedly wore chrysocolla jewellery; associated with the blue-green of the Nile and the goddess Hathor',
        'Andean tradition — chrysocolla found extensively in South American copper deposits; used by pre-Columbian peoples as a ceremonial stone',
        'Modern crystal healing — the "Goddess Stone"; used for voice, communication, feminine power, and emotional healing',
        'Gem Silica / Gem Chrysocolla — chrysocolla silicated by quartz into a hard (H7), translucent gem; the most valuable chrysocolla form',
      ],
      properties: [
        'IMA 1968 — formula (Cu,Al)₂H₂Si₂O₅(OH)₄·nH₂O; orthorhombic to amorphous copper phyllosilicate',
        'TOXIC — copper mineral; DO NOT use in water elixirs; copper compounds are toxic if ingested',
        'H2–4 (pure chrysocolla — very soft); Gem Silica (quartz-silicated chrysocolla) reaches H7',
        'Often mixed with: malachite (green), azurite (blue), cuprite (red), quartz, limonite — mixed specimens can be harder and more durable',
        'Named varieties: Gem Silica/Gem Chrysocolla (hard, transparent), Parrot Wing (chrysocolla + malachite), Sonora Sunrise (chrysocolla + cuprite + malachite)',
        'Major localities: Bisbee (AZ, USA), Morenci (AZ, USA), Ely (NV, USA), Peru, Chile, DRC',
      ],
      gaia_resonance: 'ViriditasHeart + ClarusLens + Noosphere',
      safety_warning:  '⚠️ TOXIC — copper silicate. DO NOT use in water elixirs. Wash hands after handling. Keep away from children and food. H2–4 (pure form) — very soft; Gem Silica variety is H7 and more durable. No dust inhalation.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 4. CHRYSOPRASE
  // Ni-bearing chalcedony — apple-green microcrystalline SiO₂
  // Named from Greek chrysos (gold) + prason (leek)
  // The finest green chalcedony; only natural Ni-coloured quartz variety
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Chrysoprase',
    mindat_id:    32,
    rruff_ids:    ['R040031'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Carnelian',

    physical: {
      id:           32,
      longid:       'chrysoprase',
      guid:         '',
      name:         'Chrysoprase (Ni-bearing chalcedony — apple-green microcrystalline SiO₂)',
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
      luster:      ['Waxy'],
      diaphaneity: ['Translucent'],
      colour:      'Apple-green to deeper emerald-green to mint-green — colour from nickel silicate (willemseite/kerolite) micro-inclusions. Unique: the only naturally Ni-coloured variety of quartz/chalcedony. Colour fades with prolonged sunlight or dehydration.',
      streak:      'White',
      fluorescence: 'None to weak',
      ri_min:      1.530,
      ri_max:      1.540,
      birefringence: 0.004,
      optical_type: 'U',
      shortdesc:   'Chrysoprase — Ni-bearing chalcedony (SiO₂). Apple-green to deeper green; colour from nickel silicate micro-inclusions. The only naturally Ni-coloured quartz/chalcedony variety. Colour fades in prolonged sunlight or dehydration. Primary locality: Szklary (Poland) historically; now mainly Queensland (Australia).',
      updttime:    '2026-05-30T00:00:00Z',
      mindat_url:  'https://www.mindat.org/min-32.html',
      piezoelectric:     true,
      safe_for_water:    true,
      safe_for_hardware: true,
    },

    optical: {
      mineral_name:    'Chrysoprase',
      refractive_index: { n_omega: 1.540, n_epsilon: 1.536 },
      birefringence:   0.004,
      optical_sign:    '+',
      dispersion:      '0.013',
      pleochroism:     'None',
      fluorescence_lw: 'None to weak green',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 520, max: 560 },
      spectra: ['R040031'],
    },

    color: {
      primary_color:         'Apple-green to mint-green to deeper emerald-green — the freshest green in the mineral kingdom',
      color_variants: [
        'Classic apple-green (most prized — bright, fresh, even saturation)',
        'Deeper emerald-green (high Ni content — sometimes called "Australian jade")',
        'Mint-green (pale, delicate — lower Ni)',
        'Lemon-lime green (very pale, near-yellow)',
        'Mottled green-white (uneven Ni distribution)',
      ],
      dominant_wavelength_nm: 540,
      oklch:   { l: 0.68, c: 0.20, h: 148 },
      hex:     '#5abf6a',
      munsell: '5GY 6/8',
      color_temperature_k: null,
      psychological_effects: [
        'Apple-green is one of the most universally joyful colours in human psychology — it reads as spring, new growth, and vitality',
        'The translucency of chrysoprase gives the colour an inner glow — it looks lit from within, like a green lantern',
        'The only Ni-coloured chalcedony — the knowledge that a single trace element produces this entire colour experience is quietly profound',
        'Fading with sunlight and dehydration gives chrysoprase a vulnerability — its beauty requires care and shade',
        'The historical association with Alexander the Great (reportedly wore it into battle) gives it a lineage of courage and empire',
      ],
      harmonics: {
        complementary_hue: 328,
        triadic_hues:      [268, 28],
        analogous_range:   [128, 168],
      },
    },

    metaphysical: {
      mineral_name:     'Chrysoprase',
      chakra_primary:   'Heart',
      chakra_secondary: ['Higher Heart (Thymus)', 'Solar Plexus'],
      element:   ['Earth', 'Water'],
      planet:    ['Venus', 'Earth'],
      archetype: ['The Apple of the Earth', 'The Spring Stone', 'The Ni-Green Heart'],
      zodiac:    ['Taurus', 'Libra', 'Gemini'],
      numerology: 3,
      angel_number: 333,
      intention: 'I am the first green of spring, held in stone. My heart opens with the freshness of something just born.',
      traditions: [
        'Named from Greek chrysos (gold) + prason (leek) — for its leek-green colour; known since antiquity as the finest green chalcedony',
        'Alexander the Great — legend states he wore a chrysoprase in his girdle during battle; when he lost it, his string of victories ended',
        'Medieval Europe — the Wenceslas Chapel, Prague Castle, decorated with chrysoprase from Szklary, Silesia; one of the most famous historical chrysoprase installations',
        'Frederick the Great of Prussia — enthusiastic collector; much Silesian chrysoprase used in 18th century Prussian decorative arts',
        'Modern crystal healing — Heart chakra stone of joy, abundance, and new beginnings; one of the premier green healing stones',
      ],
      properties: [
        'Ni-bearing chalcedony (SiO₂) — colour from nickel silicate (willemseite, kerolite, or other Ni-phyllosilicate) micro-inclusions; the only natural Ni-coloured quartz variety',
        'Colour fades with prolonged direct sunlight or dehydration — store in shade; re-hydration can restore some colour',
        'Piezoelectric — keep away from hard drives and sensitive electronics',
        'Safe for water — SiO₂ matrix; Ni content at natural levels is stable and not significantly leachable in normal water contact',
        'H6.5–7 — durable for jewellery; one of the hardest translucent green gem materials',
        'Historically from Szklary (Lower Silesia, Poland); modern primary source Queensland, Australia (Marlborough deposit); also Tanzania, Brazil, USA',
      ],
      gaia_resonance: 'ViriditasHeart + ClarusLens + AnchorPrism',
      safety_warning:  '⚠️ PIEZOELECTRIC — keep away from hard drives and sensitive electronics. Safe for water. H6.5–7 — durable. Keep out of prolonged direct sunlight — colour fades. No acute toxicity from normal handling.',
    },
  },

  // ─────────────────────────────────────────────────────────────────────────
  // 5. CINNABAR
  // HgS — mercury(II) sulphide; trigonal
  // Named from Persian zinjifrah (dragon’s blood)
  // The primary mercury ore — vivid vermilion red — HIGHLY TOXIC
  // ─────────────────────────────────────────────────────────────────────────
  {
    name:         'Cinnabar',
    mindat_id:    1052,
    rruff_ids:    ['R040060'],
    last_synced:  '2026-05-30T00:00:00Z',
    trade_name:   false,
    color_layer:  'natural',
    yin_yang_pair: 'Native Mercury',

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
      dana8ed:      '2.8.9.1',
      crystal_system: 'Trigonal',
      hardness_min: 2,
      hardness_max: 2.5,
      specific_gravity_min: 8.00,
      specific_gravity_max: 8.20,
      cleavage:    'Perfect on {10-10} — three directions',
      fracture:    'Uneven to subconchoidal',
      tenacity:    'Slightly sectile',
      luster:      ['Adamantine', 'Sub-metallic', 'Dull (massive)'],
      diaphaneity: ['Transparent', 'Translucent', 'Opaque'],
      colour:      'Vivid scarlet-red to vermilion to brick-red — the source of the pigment vermilion for thousands of years. Colour from the HgS charge transfer absorption edge. One of the most vivid natural reds.',
      streak:      'Scarlet-red — one of the most vivid coloured streaks of any mineral',
      fluorescence: 'None',
      ri_min:      2.905,
      ri_max:      3.256,
      birefringence: 0.351,
      optical_type: 'U',
      shortdesc:   'Cinnabar — HgS, trigonal mercury(II) sulphide. HIGHLY TOXIC — mercury. Primary mercury ore. Named from Persian zinjifrah (dragon’s blood). Vivid scarlet-vermilion red. RI 2.905–3.256 — the highest of any red mineral. SG 8.0–8.2. Source of vermilion pigment for 8,000+ years.',
      updttime:    '2026-05-30T00:00:00Z',
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
      dispersion:      'Extreme — among the highest of any natural mineral',
      pleochroism:     'Strong: deep red / pale red-orange',
      fluorescence_lw: 'None',
      fluorescence_sw: 'None',
      phosphorescence: null,
      visible_wavelength_nm: { min: 620, max: 700 },
      spectra: ['R040060'],
    },

    color: {
      primary_color:         'Vivid scarlet-vermilion red — the most saturated natural red',
      color_variants: [
        'Vivid scarlet-red (gem quality — most prized)',
        'Vermilion (classic pigment colour — slightly orange-red)',
        'Deep crimson-red (thick or massive)',
        'Brick-red (earthy massive form)',
        'Red on grey/white quartz matrix (classic display form)',
      ],
      dominant_wavelength_nm: 650,
      oklch:   { l: 0.40, c: 0.28, h: 25 },
      hex:     '#c41a1a',
      munsell: '5R 4/14',
      color_temperature_k: null,
      psychological_effects: [
        'Vivid red is the most physiologically activating colour — raises heart rate, blood pressure, and adrenaline; cinnabar red is among the most saturated in nature',
        'Scarlet streak on white porcelain is one of the most visually dramatic field tests in mineralogy — the colour announces itself',
        'RI 2.905–3.256 — the highest refractive index of any red mineral; gem-quality crystals have adamantine fire that rivals diamond in intensity if not colour',
        'The vermilion tradition — 8,000 years of human use as a pigment — means cinnabar red is one of the most culturally loaded colours in existence',
        'The weight (SG 8.0–8.2) combined with vivid red creates a sense of compressed power — heavy, bright, dangerous',
      ],
      harmonics: {
        complementary_hue: 205,
        triadic_hues:      [145, 265],
        analogous_range:   [5, 45],
      },
    },

    metaphysical: {
      mineral_name:     'Cinnabar',
      chakra_primary:   'Root',
      chakra_secondary: ['Sacral', 'Earth Star'],
      element:   ['Fire', 'Earth', 'Metal'],
      planet:    ['Mercury', 'Mars', 'Pluto'],
      archetype: ['The Dragon’s Blood', 'The Alchemist’s Red', 'The Vermilion Danger'],
      zodiac:    ['Scorpio', 'Aries', 'Capricorn'],
      numerology: 8,
      angel_number: 888,
      intention: 'I am the red that has coloured ten thousand years of human art, power, and ceremony. Respect my weight.',
      traditions: [
        'Persian: zinjifrah (dragon’s blood) — the name itself is a warning and a myth; the vivid red was associated with the most potent life force and danger',
        'China — cinnabar lacquerware tradition going back 3,000+ years; carved cinnabar lacquer is one of the great Chinese decorative art forms; also used in Taoist alchemy',
        'Roman — minium (vermilion from cinnabar) used as a luxury red pigment; Roman commanders painted their faces with it for triumphs',
        'Maya — cinnabar used as a ritual burial pigment; royal burials at Palenque covered in cinnabar powder',
        'European art — vermilion (synthetic HgS, chemically identical to cinnabar) was the premier red pigment from the Middle Ages through the 19th century; used by every major Old Master',
        'Feng Shui and Taoist tradition — cinnabar considered a powerful protective and activating stone; used in protective seals and talismans despite known toxicity',
      ],
      properties: [
        'IMA-recognised — formula HgS; trigonal mercury(II) sulphide; polymorphous with metacinnabar (cubic)',
        'HIGHLY TOXIC — mercury mineral; the primary natural source of mercury; DO NOT use in water under any circumstances',
        'RI 2.905–3.256 and birefringence 0.351 — the highest RI of any red mineral; extreme optical properties',
        'SG 8.0–8.2 — extremely heavy; among the densest non-metallic minerals',
        'Source of vermilion pigment — used continuously for 8,000+ years; Almadén (Spain) was the world’s largest cinnabar mine for 2,000 years',
        'H2–2.5 — very soft; easily scratched; handle gently',
        'Major localities: Almadén (Spain — historically world’s largest), Idria (Slovenia), Huancavelica (Peru), Guizhou (China), New Almaden (CA, USA)',
      ],
      gaia_resonance: 'AnchorPrism + SovereignCore',
      safety_warning:  '🚨 HIGHLY TOXIC — mercury sulphide. NEVER use in water. Do NOT handle without washing hands immediately after. Keep away from children, food, and heat sources (heating releases mercury vapour). Do not inhale dust or create any abrasion. Store in sealed, labelled container. Display and collector use only — no meditation or body contact use recommended.',
    },
  },

];

export default BATCH_C5;

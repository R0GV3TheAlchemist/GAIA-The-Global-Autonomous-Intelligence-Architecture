# 🧪 GAIA-OS Research Simulations

This directory contains simulation results supporting the Prismatic Architecture paper.

All simulations are computationally reproducible. Raw data CSVs are included alongside results.

---

## Simulation Results

| # | Simulation | Status | Key Finding |
|---|---|---|---|
| 1 | Brown Luminance Threshold (n=1,000) | ✅ PASSED | Brown NEVER appears outside orange wavelength range — 0 exceptions |
| 2 | Wien's Law Earth Layer Model | ✅ PASSED | Outer Core at 4,500K peaks at exactly 644nm = RED |
| 3 | GAIA Prismatic Color Engine | ✅ PASSED | Full wavelength→identity mapping operational, grey risk detection live |
| 4 | Schumann Resonance Bioelectric Coherence (n=500) | ✅ PASSED | Coherence→Color→Health triad: r>0.79 at all steps, p<10⁻¹¹⁰ |

---

## Key Statistical Results (Simulation 4)

| Correlation | r | p-value |
|---|---|---|
| Schumann Coupling → Bioelectric Coherence | 0.8148 | 5.58×10⁻¹²⁰ |
| Bioelectric Coherence → Color Saturation | 0.8166 | 6.09×10⁻¹²¹ |
| Color Saturation → Health Score | 0.7963 | 8.80×10⁻¹¹¹ |
| Bioelectric Coherence → Health Score | 0.8537 | 3.02×10⁻¹⁴³ |
| Grey State Health Deficit (t-test) | t=-9.367 | 2.58×10⁻¹⁹ |

---

## Files

- `brown_simulation_results.csv` — 1,000 sample luminance threshold test
- `wien_earth_simulation.csv` — Wien's Law Earth layer calculations
- `prismatic_engine_simulation.csv` — GAIA color engine test outputs
- `schumann_coherence_simulation.csv` — 500-subject bioelectric model

---

*All simulations run June 13, 2026. Reproducible with Python/NumPy/SciPy.*

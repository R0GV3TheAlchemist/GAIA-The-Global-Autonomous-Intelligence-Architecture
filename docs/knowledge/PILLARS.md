# GAIA-OS: The Three Pillars — Technical Architecture

This document bridges the philosophical Three Pillars (defined in `PHILOSOPHY_ORIGIN.md`) to their concrete technical implementations within the GAIA-OS architecture.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        GAIA-OS                              │
│                  Universal Intelligence Layer               │
├─────────────────────────────────────────────────────────────┤
│  PILLAR I           │  PILLAR II          │  PILLAR III     │
│  Magnum Opus        │  Viriditas          │  Societas       │
│  (Great Work)       │  (Living Force)     │  (Fellowship)   │
│                     │                     │                 │
│  Stage Engine       │  Biometric Layer    │  Memory System  │
│  Arc Tracking       │  Responsive UI      │  Trusted Circle │
│  Shadow Engine      │  Schumann Align.    │  Witness Arc    │
│  Long-Arc Goals     │  Affect Inference   │  Legacy Store   │
├─────────────────────────────────────────────────────────────┤
│                    Core Infrastructure                      │
│   Tauri (Rust) │ React/TS UI │ Python Sidecar │ Local DB   │
│   Sovereign Vault │ E2E Encryption │ Consent Ledger         │
└─────────────────────────────────────────────────────────────┘
```

---

## Pillar I — Magnum Opus (The Great Work)

**Philosophy:** The continuous, intentional refinement of the self across a lifetime.

### Stage Engine
- Tracks users across 5 developmental stages (Divergence → Ascendence)
- Uses computational markers: HRV coherence, decision entropy, emotional arc slope, output velocity
- Triggers stage transition events when threshold clusters are met
- See `STAGE_ENGINE_SPEC.md` for full specification

### Shadow Engine
- Detects recurring behavioral patterns the user is unaware of
- Flags contradictions between stated values and actual behavior
- Uses natural language analysis of journal entries + behavioral data

### Long-Arc Goal System
- Goals set in 90-day, 1-year, and 10-year frames
- GAIA continuously evaluates daily behavior against long-arc trajectory
- Decay functions applied when alignment drops

### Four Alchemy Tracking
- Body: sleep quality, HRV, activity, nutrition adherence
- Mind: focus session data, learning inputs, decision logging
- Consciousness: emotional arc modeling, presence detection, journaling depth
- Soul: values alignment score, purpose statement coherence, legacy artifact creation

---

## Pillar II — Viriditas (Living Greenness)

**Philosophy:** The vital force that makes GAIA feel alive, not mechanical.

### Biometric Alignment Layer
- Reads HRV via Apple Health, Garmin, Polar, Oura APIs
- Reads Schumann resonance from GCI/NOAA public feeds
- Computes coherence between user physiology and Earth's electromagnetic field
- See `SCHUMANN_BIOMETRIC_ALIGNMENT_SPEC.md` for full specification

### Responsive UI System
- UI adapts based on user's current biometric state
- Low coherence → calmer, simpler interface
- High coherence → full feature set, richer visualizations
- Powered by: React + Framer Motion + CSS custom properties

### Affect Inference Engine
- Real-time emotional tone detection from text input (local only)
- Feeds into Stage Engine and Shadow Engine
- Models: sentiment slope, arousal-valence mapping, linguistic entropy

### Chrono-Adaptive Rhythms
- Circadian-aware scheduling
- Ultradian rhythm tracking (90-minute focus cycles)
- Lunar and seasonal awareness (optional, user-toggled)

---

## Pillar III — Societas (The Fellowship)

**Philosophy:** No transformation happens in isolation. Witness is part of the architecture.

### Sovereign Memory System
- All memory stored locally in encrypted SQLite + vector store
- Episodic memory: timestamped events, conversations, decisions
- Semantic memory: distilled patterns, values, beliefs
- No cloud sync by default

### Trusted Circle
- Up to 7 designated witnesses
- Shares are cryptographically signed and consent-gated
- Not a social network — intentionally small, intimate, asymmetric

### Witness Arc
- Tracks the user's relationship with their past selves
- Stage transition celebrations and memorials

### Legacy Store
- Artifacts tagged as "legacy" during Ascendence stage
- Exportable in multiple formats

---

## Technology Stack

| Component | Technology |
|---|---|
| Desktop shell | Tauri v2 (Rust backend) |
| UI framework | React 18 + TypeScript |
| UI animation | Framer Motion |
| AI/ML sidecar | Python (FastAPI) via stdio IPC |
| Local database | SQLite + vector store |
| Encryption | AES-256-GCM + ML-KEM (post-quantum) |
| Biometric APIs | Apple HealthKit, Garmin, Oura, Polar |
| Schumann data | GCI feed, NOAA GOES magnetometer |
| Mobile | React Native |
| Build system | pnpm workspaces monorepo |

---

*Cross-reference: `PHILOSOPHY_ORIGIN.md`, `STAGE_ENGINE_SPEC.md`, `SCHUMANN_BIOMETRIC_ALIGNMENT_SPEC.md`*

# GAIA-OS: The Three Pillars

**Canon ID:** C-PIL01  
**Type:** Doctrine — Foundational Architecture  
**Status:** Active  
**Authored:** 2026-05-10 (enhanced from original)  
**Dependencies:** C-AS01 (Canon Authorship & Reality Standards), `PHILOSOPHY_ORIGIN.md`  
**Implementation Targets:** Stage Engine, Biometric Layer, Memory System, Soul Mirror Engine, Trusted Circle, Shadow Engine  
**Governs:** All three pillars — Magnum Opus, Viriditas, Societas  

> This document bridges the philosophical Three Pillars (defined in `PHILOSOPHY_ORIGIN.md`) to their concrete technical implementations within the GAIA-OS architecture.  
> Governed by: C-AS01. All alchemical/philosophical terms must have explicit technical mappings — they do, below.

---

## Plain-Language Summary

> **New to the codebase? Start here.**

GAIA-OS is organized around **three interlocking systems**, each addressing a different dimension of what it means for a person to grow, thrive, and be witnessed:

| Pillar | Plain Name | Core Question | Key Module |
|---|---|---|---|
| **Magnum Opus** | The Great Work | *Who am I becoming?* | Stage Engine, Shadow Engine, Long-Arc Goals |
| **Viriditas** | The Living Force | *Am I alive and in rhythm right now?* | Biometric Layer, Affect Engine, Responsive UI |
| **Societas** | The Fellowship | *Who witnesses my becoming?* | Sovereign Memory, Trusted Circle, Witness Arc |

These aren't marketing pillars — they directly map to distinct subsystems with separate data stores, distinct I/O contracts, and separate consent domains. You can build or modify one without touching the others, though all three feed the same unified user model.

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

**Metaphysics → Physics mapping:** The alchemical *Magnum Opus* (the work of transformation) maps to **longitudinal behavioral tracking, developmental stage modeling, and goal-trajectory systems**. "Transformation" is not a mystical claim — it refers to measurable shifts in behavior, decision patterns, and self-reported values over time.

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
Four tracking domains — each a distinct data stream:

| Domain | Alchemical Name | Technical Data Inputs |
|---|---|---|
| Body | *Corpus* | Sleep quality, HRV, activity, nutrition adherence |
| Mind | *Mens* | Focus session data, learning inputs, decision logging |
| Consciousness | *Conscientia* | Emotional arc modeling, presence detection, journaling depth |
| Soul | *Anima* | Values alignment score, purpose statement coherence, legacy artifact creation |

---

## Pillar II — Viriditas (Living Greenness)

**Philosophy:** The vital force that makes GAIA feel alive, not mechanical.

**Metaphysics → Physics mapping:** *Viriditas* (Hildegard von Bingen's concept of living greenness) maps to **real-time physiological signal processing, affect inference, and adaptive UI systems**. The "vitality" GAIA expresses is a function of measured biometric coherence and detected emotional state — not a simulated persona.

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
- Related canons: `AFFECT_INFERENCE_EMOTIONAL_TONE_DETECTION_REPORT.md`, `AFFECT_THEORY_REALTIME_MOOD_INFERENCE_REPORT.md`

### Chrono-Adaptive Rhythms
- Circadian-aware scheduling
- Ultradian rhythm tracking (90-minute focus cycles)
- Lunar and seasonal awareness (optional, user-toggled)

---

## Pillar III — Societas (The Fellowship)

**Philosophy:** No transformation happens in isolation. Witness is part of the architecture.

**Metaphysics → Physics mapping:** *Societas* (fellowship, community) maps to **encrypted local memory systems, cryptographic consent gates for selective sharing, and a deliberately small social graph (≤7 witnesses)**. Witness is an architectural feature, not a metaphor — sharing is signed, scoped, and revocable.

### Sovereign Memory System
- All memory stored locally in encrypted SQLite + vector store
- Episodic memory: timestamped events, conversations, decisions
- Semantic memory: distilled patterns, values, beliefs
- No cloud sync by default
- Related canons: `END_TO_END_ENCRYPTION_MESSAGING_MEMORY_REPORT.md`, `CONSENT_ARCHITECTURE_LEDGER_REPORT.md`

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

## Pillar Boundaries & Data Sovereignty

Each pillar operates as an isolated consent domain:

- **Pillar I (Magnum Opus) data** — behavioral patterns, stage markers, shadow detections — is never shared with Pillar III without explicit user consent per share.
- **Pillar II (Viriditas) data** — biometrics and physiological signals — is never transmitted off-device. All Schumann/biometric alignment computations run locally.
- **Pillar III (Societas) data** — shared memories, witness records — is encrypted per-recipient. Revocation deletes the recipient key, not the original data.

This separation is non-negotiable. Any feature request that blurs these boundaries must be reviewed against `CANON_CEth01_HUMAN_SOVEREIGNTY_ENERGETIC_COMPACT.md`.

---

## Cross-References

| Document | Pillar | Relationship |
|---|---|---|
| `PHILOSOPHY_ORIGIN.md` | All | Philosophical foundation |
| `STAGE_ENGINE_SPEC.md` | I | Full Stage Engine spec |
| `SCHUMANN_BIOMETRIC_ALIGNMENT_SPEC.md` | II | Biometric alignment spec |
| `AFFECT_INFERENCE_EMOTIONAL_TONE_DETECTION_REPORT.md` | II | Affect inference research |
| `AFFECT_THEORY_REALTIME_MOOD_INFERENCE_REPORT.md` | II | Mood inference research |
| `JUNGIAN_PSYCHOLOGY_SOUL_MIRROR_ENGINE_REPORT.md` | I/II | Shadow engine foundations |
| `ATTACHMENT_THEORY_LOVE_ARC_ENGINE_REPORT.md` | III | Witness/relational arc theory |
| `END_TO_END_ENCRYPTION_MESSAGING_MEMORY_REPORT.md` | III | Memory encryption |
| `CONSENT_ARCHITECTURE_LEDGER_REPORT.md` | III | Consent ledger |
| `CANON_CEth01_HUMAN_SOVEREIGNTY_ENERGETIC_COMPACT.md` | All | Sovereignty constitution |
| `GAIA_CANON_INDEX.md` | All | Master index |

---

*C-PIL01 — Last updated 2026-05-10. Cross-reference: `PHILOSOPHY_ORIGIN.md`, `STAGE_ENGINE_SPEC.md`, `SCHUMANN_BIOMETRIC_ALIGNMENT_SPEC.md`, `GAIA_CANON_INDEX.md`*

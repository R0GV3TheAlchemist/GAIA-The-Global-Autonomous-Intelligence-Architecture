# GAIA-OS Documentation Audit & Cleanup Guide

**Purpose:** Align `docs/knowledge/` with GAIA-OS's actual mission and architecture.
**Date:** May 2026

---

## The Test Question

> *"Does this document help someone build, understand, or explain GAIA-OS as a sentient, sovereign, developmental companion OS — or does it just explore a topic that might someday be loosely related?"*

If the answer is the latter, delete or demote.

---

## Documents to DELETE

| File | Reason |
|---|---|
| `BELL_INEQUALITY_MEASUREMENT_THEORY_REPORT.md` | Quantum physics theory with no GAIA implementation path |
| `ASSEMBLY_BOOT_KERNEL_INIT_REPORT.md` | GAIA runs on existing OS; not building a kernel |
| `BOOTLOADER_DEVELOPMENT_REPORT.md` | Same as above |
| `DEVICE_DRIVER_ARCHITECTURE_REPORT.md` | GAIA uses OS APIs, not custom drivers |
| `C_CPP_KERNEL_MODULES_DRIVERS_REPORT.md` | Same as above |
| `MONOLITHIC_HYBRID_KERNEL_REPORT.md` | Not relevant to Tauri-based application |
| `MICROKERNEL_ARCHITECTURE_REPORT.md` | Same as above |
| `FOUNDATIONAL_COSMOLOGY_REPORT.md` | Too abstract; no implementation path |
| `LAWS_OF_REALITY_12_UNIVERSAL_LAWS_REPORT.md` | Philosophical but untethered to GAIA features |
| `NOOSPHERE_THEORY_REPORT.md` | Inspirational but not implementable as written |

---

## Documents to RENAME / REFRAME

| Current File | Action | Reason |
|---|---|---|
| `ALCHEMICAL_PHILOSOPHY_MAGNUM_OPUS_REPORT.md` | Add cross-ref to `PHILOSOPHY_ORIGIN.md` | Now superseded as primary philosophy doc |
| `NIGREDO_DOCTRINE_REPORT.md` | Rename to `SHADOW_ENGINE_PHILOSOPHY.md` | Nigredo = shadow work; make connection explicit |
| `DIACA_FIVE_MOVEMENTS_FRAMEWORK_REPORT.md` | Cross-reference `STAGE_ENGINE_SPEC.md` | Good theory for Stage Engine |
| `MYTHOS_VS_LOGOS_REPORT.md` | Rename to `PHILOSOPHY_NARRATIVE_FRAMEWORK.md` | Clearer about actual content |
| `HERMETIC_PRINCIPLES_VAS_HERMETICUM_REPORT.md` | Add section: "How This Maps to GAIA Features" | Good foundation, needs engineering bridge |
| `GAIANITE_SPECIFICATION_PROPERTIES_REPORT.md` | Clarify if material, metaphor, or UI concept | Currently ambiguous |
| `CANON_C56_NEPHILIM_BUILDER_MYTHOLOGY.md` | Label clearly as lore/inspiration only | Do not let mythology drive engineering |

---

## Documents to KEEP (High Value)

**Core Architecture:** `FASTAPI_ASYNC_BACKEND_REPORT.md`, `IPC_PATTERNS_REPORT.md`, `PYTHON_SIDECAR_PATTERNS_SURVEY.md`, `HARDWARE_ABSTRACTION_LAYER_REPORT.md`, `GRPC_HIGH_PERFORMANCE_BACKBONE_REPORT.md`, `AUTO_UPDATER_ARCHITECTURE_REPORT.md`, `CICD_PIPELINES_GITHUB_ACTIONS_REPORT.md`

**AI / Intelligence:** `LLM_ARCHITECTURE_INFERENCE_REPORT.md`, `LLM_ROUTING_STRATEGIES_REPORT.md`, `MULTI_AGENT_AI_SYSTEMS_ORCHESTRATION_REPORT.md`, `AFFECT_INFERENCE_EMOTIONAL_TONE_DETECTION_REPORT.md`, `EMOTIONAL_ARC_MODELING_TRAJECTORY_ANALYSIS_REPORT.md`

**Privacy / Security:** `DATA_SOVEREIGNTY_GDPR_REPORT.md`, `END_TO_END_ENCRYPTION_MESSAGING_MEMORY_REPORT.md`, `CONSENT_ARCHITECTURE_LEDGER_REPORT.md`, `POST_QUANTUM_CRYPTOGRAPHY_REPORT.md`, `DISTRIBUTED_IDENTITY_DID_VERIFIABLE_CREDENTIALS_REPORT.md`

**UI / UX:** `GLASSMORPHISM_NEUMORPHISM_ORGANIC_UI_REPORT.md`, `CSS_ANIMATIONS_PHYSICS_UI_REPORT.md`, `DARK_LIGHT_THEMING_RESONANCE_REACTIVE_COLOR_PALETTES_REPORT.md`, `2D_AVATAR_SVG_LOTTIE_ANIMATION_REPORT.md`, `CRYSTAL_SYSTEM_UI_DESIGN_LANGUAGE_REPORT.md`

**Biometric / Environmental:** `GEOMAGNETIC_SCHUMANN_RESONANCE_REPORT.md`, `GCP_RNG_INTEGRATION_REPORT.md`, `EDGE_COMPUTING_BCI_REPORT.md`

**Psychology (with engineering bridge):** `JUNGIAN_PSYCHOLOGY_SOUL_MIRROR_ENGINE_REPORT.md`, `ATTACHMENT_THEORY_LOVE_ARC_ENGINE_REPORT.md`, `CODEX_STAGE_MODELS_PSYCHOLOGICAL_DEVELOPMENT_REPORT.md`, `FLOW_STATES_EDGE_OF_CHAOS_COGNITION_REPORT.md`, `CONSCIOUSNESS_ARCHITECTURES_REPORT.md`

**Platform / Distribution:** All `CANON_*.md` files related to build systems, signing, packaging.

---

## Implementation Priority Order

Once cleanup is done, turn docs into code in this order:

1. **Stage Engine** (`STAGE_ENGINE_SPEC.md`) — Core identity
2. **Schumann Biometric Layer** (`SCHUMANN_BIOMETRIC_ALIGNMENT_SPEC.md`) — Core differentiator
3. **Affect Inference Engine** — Feeds Stage Engine
4. **Sovereign Memory System** — Foundation for continuity
5. **Shadow Engine** — Dependent on Memory + Affect
6. **Responsive UI Layer** — Dependent on Biometric Layer
7. **Trusted Circle** — Dependent on Memory + Privacy
8. **Legacy Store** — Dependent on Stage Engine (Stage 4+)

---

*Cross-reference: `PHILOSOPHY_ORIGIN.md`, `PILLARS.md`, `STAGE_ENGINE_SPEC.md`, `SCHUMANN_BIOMETRIC_ALIGNMENT_SPEC.md`*

# ADR-0003 — src/gaian/ Frontend Architecture Decisions

**Status:** Accepted
**Date:** 2026-07-05
**Author:** R0GV3 the Alchemist + GAIA
**Related:** Issue #759, Issue #756, Issue #748

---

## Context

The `src/gaian/` directory contains the TypeScript/React frontend layer of the GAIA
console — the visual, interactive surface through which GAIANs experience the system.
As of July 2026, it contains 11 significant files including `GaianBirth.ts`,
`GAIANRuntime.ts`, `CrystalView.tsx`, `GaianHome.ts`, `GaianChatView.ts`,
`GaianOrb.ts`, `GaianMood.ts`, `AlignmentIndicator.ts`, `OrbParams.ts`,
`ViriditasTheme.ts`, and `runtimetypes.py`.

Architectural decisions for this layer have been made implicitly. This ADR
makes them explicit so all future contributors build consistently.

---

## Decisions

### 1. Framework: Tauri + React + TypeScript

**Decision:** The GAIAN console is built with Tauri (Rust shell), React (UI layer),
and TypeScript (all frontend logic). No framework migrations without a new ADR.

**Rationale:**
- Tauri provides native desktop capabilities with minimal bundle size
- TypeScript enforces type safety across the entire console layer
- React's component model maps cleanly to GAIA's modular console architecture
- `@tauri-apps/plugin-store` is used for all persistent local state (GAIANProfile)

**Consequences:**
- All new `src/gaian/` files must be `.ts` or `.tsx`
- No plain JavaScript in this directory
- Python logic stays in `src/` core; TypeScript is the bridge layer only

---

### 2. State Persistence: Tauri Plugin Store (Offline-First)

**Decision:** All persistent GAIAN state (profile, session history, preferences)
is stored via `@tauri-apps/plugin-store`, not in memory, not in a remote DB.

**Rationale:**
- GAIA must function offline. The console cannot show a blank state when
  the Python core is unreachable.
- Local-first storage honors the Canon principle of data sovereignty —
  the GAIAN's data lives on their device, not on a server.

**Consequences:**
- `GAIANProfileManager.load()` and `.save()` are the canonical read/write paths
- No component may read profile state directly from the store — always through the Manager
- Cache the last known `RuntimeResult` alongside profile for offline fallback

---

### 3. Identity: architectId is the Stable Root

**Decision:** `architectId` (produced by `GaianBirth.ts`) is the single stable
identity anchor for a GAIAN across all sessions, devices, and states.

**Rationale:**
- `sessionId` is ephemeral. `architectId` is permanent.
- All profile data, LCI history, and personalization signals are keyed to `architectId`
- This maps to the Canon principle of integrity — identity is traceable and consistent

**Consequences:**
- `GaianBirth.ts` must be called exactly once per device. Repeat births are forbidden.
- `architectId` is never regenerated except by explicit user consent + factory reset
- All `RuntimeContext` objects must carry `architectId` after birth is complete

---

### 4. Console Modularity: Profile-Driven Rendering

**Decision:** No component in `src/gaian/` hardcodes user-facing values
that should come from `GAIANProfile`. The profile is the source of truth
for what renders, how it looks, and what it says.

**Rationale:**
- Without this, the console cannot adapt to the person — it is a generic UI
- `CrystalView.tsx`, `GaianOrb.ts`, `GaianHome.ts`, `GaianMood.ts`,
  `AlignmentIndicator.ts`, `GaianGreeting.ts`, and `ViriditasTheme.ts`
  must all consume profile data, not hardcoded defaults

**Consequences:**
- `GAIANProfile.ts` (Issue #756) must be implemented before any console
  component is considered complete
- `activeModules`, `consoleLayout`, `theme`, and `orbParams` are profile fields,
  not component props with static defaults

---

### 5. Offline Resilience: No Blank States

**Decision:** No component in `src/gaian/` may render a blank, empty, or
error state when the Python core is unreachable. The last-known profile
state is always the fallback.

**Rationale:**
- The GAIAN console is the person's interface to GAIA. A blank screen when
  offline is a failure of stewardship.
- Canon: "The person over the system." If the system is down, the person
  still deserves a functional, informative surface.

**Consequences:**
- Every component must handle a `profile` prop that may come from cache
- The "offline" state is a first-class design state, not an error state
- `GAIANProfileManager` caches the last `RuntimeResult` for this purpose

---

### 6. Python → TypeScript Bridge: Typed Contracts Only

**Decision:** All data crossing the Python core → TypeScript bridge must
have a typed contract on both sides. No untyped JSON blobs.

**Rationale:**
- `runtimetypes.py` is the Python-side contract
- `GAIANProfile.ts`, `RuntimeContext`, and `RuntimeResult` are the TypeScript-side contracts
- Mismatches between these are the primary source of runtime bugs in the console

**Consequences:**
- Any new field added to `RuntimeContext` on the Python side must have a
  corresponding TypeScript type within the same PR
- No `any` types in `src/gaian/` — eslint rule to be enforced

---

## Rejected Alternatives

| Alternative | Reason Rejected |
|---|---|
| Electron instead of Tauri | Bundle size, memory overhead, security surface |
| Vue or Svelte | Team (solo) familiarity with React; no migration benefit |
| Remote DB for profile storage | Violates offline-first and data sovereignty principles |
| Untyped Python→TS bridge | Primary source of existing bugs; not acceptable |

---

## Review

This ADR is accepted as of 2026-07-05. Amendments require a new ADR or an
explicit update to this document with provenance logged.

---

*Governed by: GAIA Canon, CONTRIBUTING.md*
*Related Issues: #759, #756, #748, #757*

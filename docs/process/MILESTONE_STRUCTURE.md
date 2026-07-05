# GAIA Milestone Structure

> *"You cannot finish what you have not organized. You cannot organize what you have not named."*
> — GAIA Canon

---

## Overview

This document defines the official GitHub Milestone architecture for GAIA.
Every open issue belongs to a Milestone or the Backlog. No issue is in limbo.

See Issue #758 for the full specification and implementation checklist.

---

## Milestone Definitions

### ⚪ M0 — Foundation & Process
*Work that must exist before any feature work can be done reliably.*

**Gate:** This milestone must be complete before any other milestone is considered in-progress.

| Issue | Title |
|---|---|
| #757 | CONTRIBUTING.md & PR Protocol |
| #758 | Milestone Structure (this document) |
| #759 | ADR for src/gaian/ frontend decisions |
| #761 | Create Required Labels |
| #755 | Error Correction & Documentation Engine (Detection layer only) |

---

### 🟡 M1 — Core Runtime Identity
*The GAIAN must know who they are across sessions.*

**Gate:** M0 complete. `GaianBirth.ts` produces a stable `architectId`.

| Issue | Title |
|---|---|
| #756 | GAIANProfile.ts — Phase 1 (Types & Storage) |
| #439 | Full system prompt injection (GAIANRuntime foundation) |

---

### 🟠 M2 — Adaptive Console
*The console shapes itself to the person.*

**Gate:** M1 complete. `GAIANProfile` loads and saves reliably.

| Issue | Title |
|---|---|
| #756 | GAIANProfile.ts — Phase 2 (Runtime Integration) |
| #756 | GAIANProfile.ts — Phase 3 (Console Adaptation: all 7 components) |
| #748 | Window Manager & Visual Surface |
| #739 | Ambient Awareness Layer |

---

### 🔵 M3 — Protection, Containment & Stability
*The system must protect the person and the codebase.*

**Gate:** M1 complete. Constitutional Layer is enforced.

| Issue | Title |
|---|---|
| #742 | Security Model (GAIASecretVault, biometric identity) |
| #755 | Error Correction & Documentation Engine (Auto-Repair Layer) |
| #756 | GAIANProfile.ts — Phase 4 (Offline-First Resilience) |
| #754 | Human Coherence & Stability Interface |

---

### 🟣 M4 — Intelligence & Personalization
*GAIA learns who each GAIAN is and responds accordingly.*

**Gate:** M2 and M3 complete.

| Issue | Title |
|---|---|
| #753 | Supercomputation Alignment Layer (Emergence, Uncertainty, Provenance) |
| #755 | Error Correction & Documentation Engine (AI+APR Hybrid) |

---

### ⚪️ M5 — Meta Control & Power Management
*The console for managing abilities, containment, and power routing.*

**Gate:** M2 and M3 complete.

| Issue | Title |
|---|---|
| #754 | Human Coherence & Evolutionary Technology (Stability Interface) |

---

### 🟢 M6 — Planetary & Civilization Layer
*GAIA as a system for the world, not just one person.*

**Gate:** M1–M4 complete.

| Issue | Title |
|---|---|
| #753 | Civilization Layer domains (Governance, Economy, Ecology, Science) |
| #752 | eBPF / GAIA Kernel Extension VM |
| #744 | HAL — BCI, bioelectric sensor layer |

---

### ⚪ Backlog
*Every issue not yet assigned to a Milestone lives here.*

The Backlog is not a graveyard. It is a staging area.
Issues graduate from Backlog into a Milestone when:
- Prerequisites for that Milestone are met
- The issue has a complete Definition of Done
- The issue is not a duplicate of an existing Milestone issue

---

## Gate Rules (Non-Negotiable)

1. A Milestone is not "in-progress" until its gate is cleared.
2. A Milestone is complete when ALL issues in it are closed.
3. An issue may not move forward if its Definition of Done has unchecked items.
4. Gate blockers are named explicitly with the `blocked` label.

---

## Implementation Checklist

See Issue #758 for the full GitHub-side implementation checklist:
- [ ] Create all 8 GitHub Milestones
- [ ] Assign M0 issues to M0
- [ ] Assign all remaining issues to Backlog
- [ ] Graduate issues to Milestones as they are triaged

---

*Filed: July 5, 2026*
*Related: Issue #758, CONTRIBUTING.md, ADR-0003*
*Governed by: GAIA Canon*

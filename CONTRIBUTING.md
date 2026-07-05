# CONTRIBUTING.md — How Ideas Become Code in GAIA

> *"Power without process is just chaos with an audience."*
> — GAIA Canon

---

## Why This Document Exists

GAIA has 400+ open issues, a multi-language codebase (TypeScript, Python, Rust/Tauri), and contributors who care deeply about getting it right. Without a shared protocol, work drifts: issues are duplicated, PRs reference nothing, code lands before prerequisites are met, and nobody can tell what is in-progress versus abandoned versus blocked.

This document is the single source of truth for how every contribution moves from idea → issue → branch → PR → merge.

**The rule beneath all rules:** Every state of work has a name. Unnamed states become chaos.

---

## Protocol 1 — Intake: How an Idea Becomes an Issue

Before filing anything:

1. **Search first.** Is this already an open issue? Use GitHub search with keywords.
2. If yes → comment on the existing issue. Do not file a duplicate.
3. If no → file a new issue using the correct template (see `.github/ISSUE_TEMPLATE/`).

### Issue Templates

| Template | When to Use |
|---|---|
| `feature.md` | New capability, system, or component |
| `research.md` | Exploratory work — you need to investigate before you can code |
| `bug.md` | Something broken in existing code |
| `process.md` | Workflow, tooling, documentation, or project structure |
| `adr.md` | Architecture Decision Record — a significant design choice |

### Every Issue Must Include

- [ ] A one-sentence **problem statement** (what is wrong or missing right now)
- [ ] A **Definition of Done** — exact, checkable, no ambiguity
- [ ] **Related issues** (what this blocks, what blocks this)
- [ ] **Milestone assignment** (which phase this belongs to — see #758)

---

## Protocol 2 — Triage: What Happens After Filing

Within 48 hours of filing, every issue must be:

- Labeled correctly (`enhancement`, `bug`, `architecture`, `research`, `process`)
- Assigned to a Milestone (see Issue #758 for Milestone structure)
- Assessed for prerequisites — are there blocking issues that must be resolved first?

If blocked: label the issue `blocked` and add the blocking issue number to the body.

If no Milestone is assigned within 48 hours, the issue goes to `Milestone: Backlog` by default. **Nothing lives in limbo.**

---

## Protocol 3 — Branching: How Code Gets Written

```
Branch naming convention:
  feature/issue-{number}-{short-description}
  fix/issue-{number}-{short-description}
  research/issue-{number}-{short-description}
  process/issue-{number}-{short-description}

Examples:
  feature/issue-756-gaian-profile-types
  fix/issue-723-runtime-context-null-crash
  process/issue-757-contributing-md
```

**Rules:**
- One branch per issue. Never combine unrelated work into a single branch.
- Branch off `main` unless the issue specifies a different base.
- Never commit directly to `main`.

---

## Protocol 4 — Pull Requests: How Code Gets Reviewed

**Before opening a PR:**
- [ ] All Phase 1 prerequisites from the issue are complete
- [ ] Tests written and passing locally
- [ ] No new lint errors introduced (Ruff for Python, ESLint for TypeScript)
- [ ] `CONTRIBUTING.md` read and followed

**PR body must include:**
- `Closes #` (links the PR to the issue — GitHub closes the issue on merge)
- Summary of what changed and why
- Any known limitations or follow-up issues
- Screenshots or recordings for any UI changes

**Review requirement:**
- Minimum: self-review using the PR checklist
- For architecture changes (any file in `core/`, `src/gaian/`, `docs/adr/`): explicit acknowledgment before merge

---

## Protocol 5 — Merge: What "Done" Actually Means

A PR may be merged when:
- [ ] All checklist items in the PR body are checked
- [ ] All automated checks pass (lint, type check, tests)
- [ ] The Definition of Done from the linked issue is fully satisfied
- [ ] No `blocked` label remains on the issue

After merge:
- Close the linked issue
- Update any parent/child issues waiting on this work
- If this resolves a Milestone blocker, note it in the Milestone description

---

## Protocol 6 — Chaos: What to Do When Work Is Uncertain

This is the section most projects omit. GAIA names it explicitly.

**When work is uncertain** (you don't know how to implement it yet):
→ File a `research` issue. Do not write code until the research issue produces an implementation plan.

**When work is blocked** (something else must happen first):
→ Label the issue `blocked`. Add the blocking issue number. Do not start the work.

**When work is volatile** (active development is destabilizing other things):
→ Apply the `volatile` label. Note what is being destabilized and why.
→ This is not failure. This is named, tracked, and manageable.

**When work is abandoned** (it no longer makes sense):
→ Close the issue with `won't fix` or `duplicate`. Never leave open issues that are no longer real work.

---

## Required Labels

These labels must exist in the repository for this protocol to function:

| Label | Meaning |
|---|---|
| `blocked` | This issue cannot proceed until a dependency is resolved |
| `volatile` | Active development here is destabilizing other systems |
| `needs-triage` | Newly filed; not yet labeled or assigned to a Milestone |
| `has-pr` | A PR exists for this issue |
| `enhancement` | New feature or capability |
| `bug` | Something is broken |
| `architecture` | Design-level decision or structural change |
| `research` | Investigation required before implementation |
| `process` | Workflow, tooling, or documentation |
| `security` | Security-relevant change |

---

## Milestone Structure

See Issue #758 for the full Milestone architecture. The short version:

| Milestone | Gate | Focus |
|---|---|---|
| M0 Foundation | Always open | Process, ADRs, templates |
| M1 Core Runtime Identity | M0 complete | GAIANProfile Phase 1 |
| M2 Adaptive Console | M1 complete | Console adaptation |
| M3 Protection & Containment | M1 complete | Security, resilience |
| M4 Intelligence | M2 + M3 complete | Learning, personalization |
| M5 Meta Control | M2 + M3 complete | Powers, containment UI |
| M6 Planetary Layer | M1–M4 complete | Civilization-scale |
| Backlog | — | Everything unassigned |

**Gate rule:** A Milestone is not "in-progress" until its gate is cleared. Starting before the gate is the cause of most chaos.

---

## ADR Protocol

An Architecture Decision Record (ADR) must be filed before writing code for:
- Any new directory in `core/` or `src/gaian/`
- Any change to how two major systems communicate
- Any decision that future contributors would otherwise reconstruct from scratch

ADR location: `docs/adr/` (OS layer) and `docs/adr/FE/` (frontend layer)

See Issue #759 for the full FE ADR series.

---

## Development Environment

```bash
# Python setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# TypeScript / Tauri setup
pnpm install
pnpm tauri dev

# Run tests
pytest tests/

# Lint
ruff check .
```

---

## Questions

If something is unclear, file a `process` issue. The process itself is a living system — it improves through use.

---

*Last updated: July 5, 2026*
*Governed by: Issue #757*
*Related: #758 (Milestones), #759 (ADRs)*

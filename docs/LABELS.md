# GAIA Label Taxonomy

This document is the canonical reference for every GitHub label used in this repository.
All issues and pull requests should carry at least one **type** label and one **component** label.
Priority labels are applied during triage.

---

## Type

Describes the *kind* of work the issue or PR represents.

| Label | Color | Purpose |
|---|---|---|
| `type: bug` | ![#d73a4a](https://via.placeholder.com/12/d73a4a/d73a4a.png) `#d73a4a` | Something isn't working |
| `type: feature` | ![#0075ca](https://via.placeholder.com/12/0075ca/0075ca.png) `#0075ca` | New feature or request |
| `type: chore` | ![#e4e669](https://via.placeholder.com/12/e4e669/e4e669.png) `#e4e669` | Build, tooling, or maintenance task |
| `type: docs` | ![#0052cc](https://via.placeholder.com/12/0052cc/0052cc.png) `#0052cc` | Documentation only |
| `type: test` | ![#bfd4f2](https://via.placeholder.com/12/bfd4f2/bfd4f2.png) `#bfd4f2` | Test coverage or test infrastructure |
| `type: security` | ![#b60205](https://via.placeholder.com/12/b60205/b60205.png) `#b60205` | Security vulnerability or hardening |
| `type: performance` | ![#f9d0c4](https://via.placeholder.com/12/f9d0c4/f9d0c4.png) `#f9d0c4` | Performance improvement |

---

## Priority

Applied during triage. Every open issue should have a priority label.

| Label | Color | Purpose |
|---|---|---|
| `priority: critical` | ![#b60205](https://via.placeholder.com/12/b60205/b60205.png) `#b60205` | Must fix immediately — blocks release |
| `priority: high` | ![#e11d48](https://via.placeholder.com/12/e11d48/e11d48.png) `#e11d48` | High urgency — address this sprint |
| `priority: medium` | ![#f97316](https://via.placeholder.com/12/f97316/f97316.png) `#f97316` | Normal priority |
| `priority: low` | ![#fde68a](https://via.placeholder.com/12/fde68a/fde68a.png) `#fde68a` | Nice to have — address when capacity allows |

---

## Component

Indicates which part of the GAIA codebase is affected.

| Label | Color | Maps to |
|---|---|---|
| `comp: core` | ![#5b21b6](https://via.placeholder.com/12/5b21b6/5b21b6.png) `#5b21b6` | `core/` — epistemic engine, criticality, models |
| `comp: api` | ![#6d28d9](https://via.placeholder.com/12/6d28d9/6d28d9.png) `#6d28d9` | `api/` — FastAPI routers and routes |
| `comp: cli` | ![#7c3aed](https://via.placeholder.com/12/7c3aed/7c3aed.png) `#7c3aed` | `cli/` — command-line interface |
| `comp: crypto` | ![#8b5cf6](https://via.placeholder.com/12/8b5cf6/8b5cf6.png) `#8b5cf6` | `api/crypto.py` — encryption layer |
| `comp: memory` | ![#a78bfa](https://via.placeholder.com/12/a78bfa/a78bfa.png) `#a78bfa` | Memory store, elemental memory, retrieval |
| `comp: alignment` | ![#c4b5fd](https://via.placeholder.com/12/c4b5fd/c4b5fd.png) `#c4b5fd` | `api/routers/alignment.py` — alignment engine |
| `comp: gaian` | ![#ddd6fe](https://via.placeholder.com/12/ddd6fe/ddd6fe.png) `#ddd6fe` | `api/routers/gaian.py` — GAIAN runtime |
| `comp: ui` | ![#0ea5e9](https://via.placeholder.com/12/0ea5e9/0ea5e9.png) `#0ea5e9` | `src/` `ui/` `client/` — frontend |
| `comp: infra` | ![#0369a1](https://via.placeholder.com/12/0369a1/0369a1.png) `#0369a1` | Docker, k8s, CI/CD, Makefile |

---

## Status

Tracks where an issue or PR sits in the workflow.

| Label | Color | Meaning |
|---|---|---|
| `status: needs-triage` | ![#ededed](https://via.placeholder.com/12/ededed/ededed.png) `#ededed` | Newly opened — not yet assessed |
| `status: in-progress` | ![#fbca04](https://via.placeholder.com/12/fbca04/fbca04.png) `#fbca04` | Actively being worked on |
| `status: blocked` | ![#e11d48](https://via.placeholder.com/12/e11d48/e11d48.png) `#e11d48` | Cannot proceed — waiting on something |
| `status: ready-for-review` | ![#0e8a16](https://via.placeholder.com/12/0e8a16/0e8a16.png) `#0e8a16` | Work done — awaiting review / merge |
| `status: wont-fix` | `#ffffff` | Acknowledged but will not be addressed |

---

## Special

| Label | Color | Purpose |
|---|---|---|
| `good first issue` | ![#7057ff](https://via.placeholder.com/12/7057ff/7057ff.png) `#7057ff` | Good for newcomers |
| `help wanted` | ![#008672](https://via.placeholder.com/12/008672/008672.png) `#008672` | Extra attention is needed |
| `breaking change` | ![#b60205](https://via.placeholder.com/12/b60205/b60205.png) `#b60205` | Introduces a breaking API or behaviour change |
| `ruff / lint` | ![#e4e669](https://via.placeholder.com/12/e4e669/e4e669.png) `#e4e669` | Code style or linting issue |
| `epic` | ![#3b0764](https://via.placeholder.com/12/3b0764/3b0764.png) `#3b0764` | Large multi-issue initiative |

---

## Applying Labels

- Every issue needs: **1 type** + **1 component** + **1 priority** (after triage)
- Every PR needs: **1 type** + **1 component** + **1 status**
- `breaking change` should be added to any PR that changes a public API, CLI flag, or DB schema
- `epic` is for tracking issues only — not individual bug/feature issues

## Bootstrap

To create / sync all labels on a fresh fork or after a repo rename:

```bash
export GITHUB_TOKEN=ghp_yourtoken
python scripts/labels.py
```

The script is idempotent — safe to re-run at any time.

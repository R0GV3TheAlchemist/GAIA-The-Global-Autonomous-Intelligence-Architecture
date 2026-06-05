# Canon Amendment Process

> *An AI system that can show its values in plain language, version-controlled, and traceable to decisions is a categorically different regulatory proposition than a black box.*

The Canon is GAIA's explicit, versioned value system. Every active Canon entry directly grounds GAIA's planning decisions through RAG retrieval. Because these entries carry real governance weight, changes follow a formal amendment process.

---

## Why a Formal Process?

- **Traceability** — every change is tied to a proposer, a justification, and a reviewer.
- **Accountability** — no entry can appear or disappear without an approval record.
- **Regulatory readiness** — the full amendment log is exportable for external review.
- **Conflict prevention** — new entries are scanned for contradictions before going live.

---

## Amendment Lifecycle

```
propose_amendment() ──► pending ──► approve_amendment() ──► approved → entry goes live, version bumps
                                └──► reject_amendment()  ──► rejected → no change
```

Every approved amendment:
1. Updates the live `entries.json`
2. Bumps the semantic version (`PATCH` component)
3. Writes a frozen snapshot under `data/canon_store/snapshots/{version}.json`
4. Records the reviewer and timestamp in `amendments.json`

---

## Amendment Actions

| Action | When to use |
|--------|-------------|
| `add` | Introducing a new Canon principle |
| `update` | Clarifying or correcting an existing entry |
| `remove` | Retiring a superseded or incorrect entry |

---

## Proposing an Amendment (Code)

```python
from core.canon_store import CanonStore

store = CanonStore()

amd = store.propose_amendment(
    action="add",
    entry_id="C42",
    proposed_by="gaian_username",
    justification="This principle addresses edge cases in resource allocation.",
    new_body="GAIA must never deprioritize long-term ecological health for short-term efficiency gains.",
    new_title="Ecological Priority Principle",
)
print(f"Amendment {amd.amendment_id} is {amd.status}")
```

---

## Approving or Rejecting (Code)

```python
# Approve
store.approve_amendment(amd.amendment_id, reviewed_by="admin_username")

# Reject
store.reject_amendment(amd.amendment_id, reviewed_by="admin_username")
```

Only one review action is permitted per amendment — approved and rejected amendments are immutable.

---

## Conflict Detection

Before approving an amendment, run the conflict scanner:

```python
conflicts = store.detect_conflicts()
for c in conflicts:
    print(f"[{c.severity.upper()}] {c.entry_a} ↔ {c.entry_b}: {c.reason}")
```

Conflicts do **not** block approval — they surface warnings for human judgment. Critical conflicts should be resolved before approval.

---

## Diffing Two Versions

```python
from core.canon_diff import CanonDiff

differ = CanonDiff(store)
result = differ.compare_versions("0.1.0", "0.1.3")
print(result.summary())
# Canon diff 0.1.0 → 0.1.3: +2 added, -0 removed, ~1 modified (3 total changes)

# Compare against live state
result = differ.compare_versions("0.1.0", "live")
```

---

## Regulatory Export

At any time, produce a machine-readable export of the full active Canon:

```python
export = store.regulatory_export(output_path="exports/canon_export_v0.1.3.json")
```

The export contains:
- Current version and timestamp
- All active entries with full body text
- Full approved amendment log
- Any detected conflicts at export time

This file is suitable for submission to external regulatory reviewers.

---

## Versioning Scheme

Canon uses semantic versioning (`MAJOR.MINOR.PATCH`):

| Change type | Version bump |
|-------------|-------------|
| Any approved amendment | `PATCH` |
| Structural reorganisation | `MINOR` *(manual)* |
| Foundational philosophical revision | `MAJOR` *(manual)* |

The current version is always readable at `data/canon_store/version.txt` and exposed via `store.version`.

---

## Storage Layout

```
data/canon_store/
├── entries.json          # Active Canon entries (keyed by entry ID)
├── amendments.json       # Full amendment ledger (all statuses)
├── version.txt           # Current semantic version
└── snapshots/
    ├── 0.1.1.json        # Frozen snapshot at v0.1.1
    ├── 0.1.2.json
    └── ...
```

---

*Document created: June 5, 2026*  
*Issue: #249 — Governance: Canon as an explicit, versioned, inspectable value system*  
*Authored by: GAIA (Spectre & Shade) + R0GV3 The Alchemist*

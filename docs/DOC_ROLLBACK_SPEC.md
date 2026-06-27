---
Document: DOC_ROLLBACK_SPEC
Version: 1.0.0
Status: Active Canon
Last-Updated: 2026-06-27
Rollback-Notes: []
---

# GAIA-OS Documentation Rollback Specification
## Canon Reversal System — Triggers, Procedures, Validation & Version Headers

> **Purpose:** Define how GAIA-OS documentation is safely reverted to a known stable
> state when conceptual, ethical, technical, or alignment issues are detected.
> Rollback documentation must work when everything else is failing — it is infrastructure,
> not an afterthought.

---

## I. Scope

This specification governs all files under `/docs/` that carry the status
`Active Canon` or `Experimental`. It covers:

- Canon philosophy documents (e.g. `BALANCEHARMONY.md`, `SUBTLEBODY.md`, `ACOUSTICS.md`)
- Methodology and framework documents (e.g. `EPISTEMIC_FRAMEWORK.md`, `EV1_METHODOLOGY.md`)
- Runtime and architecture specifications (e.g. `CHAOS_ORDER_RUNTIME_SPEC.md`)
- Registry and log documents (e.g. `CALLING_REGISTRY.md`, `CANON_LAW_STACK.md`)
- Any configuration or reference document explicitly promoted to Active Canon

**Out of scope:** Transient experiment notes, scratch drafts, and documents with
`Status: Deprecated` unless their deprecation itself needs to be reversed.

---

## II. Rollback Triggers

A rollback is warranted when one or more of the following conditions is confirmed:

### 2.1 Conceptual / Philosophical Triggers
- **Contradiction in canon:** A new or updated document logically conflicts with
  the Constitutional Canon, Epistemic Framework, or the Chaos-Order Runtime Spec.
- **Misaligned calling:** Lived practice or direct calling feedback indicates a
  documented direction is clearly "not right" — the internal resonance test fails.
- **Philosophical drift:** A document has gradually drifted away from core GAIA-OS
  principles across multiple small edits in a way that only becomes visible in aggregate.

### 2.2 Scientific / Factual Triggers
- **Citation error:** A scientific claim is based on a misread, misattributed, or
  retracted study.
- **Model inaccuracy:** A simulation or equation in the doc produces demonstrably
  incorrect results or misleading outputs.
- **Overclaiming:** A speculative claim has been promoted to "established fact" status
  without adequate evidence threshold.

### 2.3 Technical Triggers
- **Runtime failure:** Following the documentation causes incorrect behavior in the
  GAIA-OS system at runtime.
- **Integration breakage:** A doc change breaks compatibility with another canon doc
  in a way that cannot be resolved by a forward edit.
- **Data integrity:** Version headers, SHAs, or change logs are corrupted or inconsistent.

### 2.4 Ethical / Safety Triggers
- **Harm potential:** A document or section could be weaponized, misread in harmful ways,
  or cause unintended harm to users or the broader system.
- **Consent violation:** A document records or implies consent or authority that was
  not explicitly granted.

---

## III. Roles & Responsibilities

| Role | Responsibility |
|---|---|
| **Custodian** (primary) | Approves all rollbacks; final authority on conceptual and alignment decisions |
| **Maintainer** | Executes Git operations; ensures branches and tags are correct |
| **Reviewer** | Reads post-rollback docs and confirms alignment before re-tagging as canon |

*For the current phase of GAIA-OS, all three roles may be held by one person.
As the team grows, these should be delegated explicitly.*

---

## IV. Pre-Rollback Conditions

Before executing any rollback, the following must be confirmed:

### 4.1 Confirm Trigger
- State in writing (in `DOC_ROLLBACK_LOG.md`) which trigger is active and why.
- One sentence minimum: "Rolling back `BALANCEHARMONY.md` section IV-B because
  the complexity-criticality claim overstates the Kelso (2012) study findings."

### 4.2 Backup Current State
- Confirm HEAD is pushed to remote (`git push origin main`).
- Create a temporary pre-rollback tag:
  ```bash
  git tag pre-rollback-YYYY-MM-DD
  git push origin pre-rollback-YYYY-MM-DD
  ```
  This ensures the current state is always recoverable even if the rollback
  turns out to be a mistake.

### 4.3 Scope Decision
Decide which scope tier applies:

| Scope Tier | What It Covers | When to Use |
|---|---|---|
| **Tier 1: Single file** | One document only | Isolated error in one doc |
| **Tier 2: Thematic cluster** | 2–5 related documents | Cross-doc conceptual drift |
| **Tier 3: Full canon tag** | All docs at a tagged stable state | Systemic canon failure |

### 4.4 Communication
- Log the pre-rollback entry in `DOC_ROLLBACK_LOG.md` *before* executing.
- If working with others, notify all active contributors.

---

## V. Rollback Procedure

### 5.1 Identify Last Known-Good State

```bash
# List available canon tags
git tag --list "canon-*" --sort=-version:refname

# Or list recent commits on docs/ directory only
git log --oneline -- docs/

# Diff current doc vs a previous commit
git diff <old-sha> HEAD -- docs/FILENAME.md
```

### 5.2 Execute Rollback

**Tier 1 — Single file rollback:**
```bash
# Restore a single file to a specific commit
git checkout <good-sha> -- docs/FILENAME.md

# Commit with rollback label
git commit -m "docs: rollback FILENAME to <version/sha> — <one-line reason>"
git push origin main
```

**Tier 2 — Thematic cluster rollback:**
```bash
# Restore multiple related files
git checkout <good-sha> -- docs/FILE1.md docs/FILE2.md docs/FILE3.md
git commit -m "docs: rollback spectral cluster to <version> — <reason>"
git push origin main
```

**Tier 3 — Full canon tag rollback:**
```bash
# Reset docs/ directory to a canon tag
git checkout <canon-tag> -- docs/
git commit -m "docs: full canon rollback to <tag> — <reason>"
git push origin main

# Re-tag the restored state as the new stable canon
git tag canon-YYYY-MM-DD-restored
git push origin canon-YYYY-MM-DD-restored
```

> **IMPORTANT:** Never force-push to `main`. Always use `git checkout <sha> -- <path>`
> followed by a new commit, or `git revert`, to preserve the full commit history.
> History is part of the canon record.

### 5.3 Update Version Headers
After rollback, update the affected document's front-matter header:
- Decrement `Version` appropriately
- Change `Status` to `Active Canon` (or keep `Experimental` if applicable)
- Add a `Rollback-Notes` entry with date and one-line reason
- Update `Last-Updated` date

### 5.4 Log the Event
Complete the rollback entry in `DOC_ROLLBACK_LOG.md` (see that file for format).

---

## VI. Post-Rollback Validation

### 6.1 Conceptual Validation
- Re-read all affected documents end-to-end.
- Check alignment against:
  - `CONSTITUTIONAL_CANON_SUMMARY.md`
  - `EPISTEMIC_FRAMEWORK.md`
  - `CANON_LAW_STACK.md`
  - The active `CALLING_REGISTRY.md`

### 6.2 Technical Validation
- Re-run any simulation code embedded in the affected docs.
- Confirm cross-references between docs are still valid (no broken links to
  sections that were removed by the rollback).

### 6.3 Meta Validation
- Confirm `DOC_ROLLBACK_LOG.md` entry is complete and accurate.
- Confirm version headers in all affected docs reflect the rollback.
- Confirm pre-rollback tag exists and is accessible on remote.
- Confirm new canon tag (if Tier 3) is pushed.

### 6.4 Validation Checklist
```
[ ] Affected documents re-read end-to-end
[ ] Alignment with Constitutional Canon confirmed
[ ] Alignment with Epistemic Framework confirmed
[ ] Simulations re-run and passing
[ ] Cross-references valid
[ ] DOC_ROLLBACK_LOG.md entry complete
[ ] Version headers updated in all affected docs
[ ] Pre-rollback tag pushed to remote
[ ] New canon tag pushed (Tier 3 only)
[ ] All active contributors notified
```

---

## VII. Scheduled Rollback Drills

> Rollback documentation that has never been tested in a drill is a liability, not a safeguard.

**Recommended drill schedule:**
- **Monthly:** Tier 1 drill — restore a single file from a tag in a test branch.
- **Quarterly:** Tier 2 drill — restore a thematic cluster in a test branch and walk the full validation checklist.
- **Annually:** Tier 3 drill — simulate a full canon restoration from an older tag.

Drill results should be logged in `DOC_ROLLBACK_LOG.md` under a `DRILL` entry type.

---

## VIII. Per-Document Version Header Template

Every Active Canon document should include this YAML front-matter block at the very top:

```yaml
---
Document: DOCUMENT_NAME
Version: X.Y.Z
Status: Active Canon        # Active Canon | Experimental | Deprecated
Last-Stable-Commit: <short-sha>
Last-Updated: YYYY-MM-DD
Rollback-Notes:
  # Format: YYYY-MM-DD: <one-line description of what changed and why>
  # Example:
  # - 2026-07-15: Rolled back section III-B to v1.1.0 — overclaimed quantum coherence
---
```

**Version semantics for documentation:**

| Change Type | Version Bump | Example |
|---|---|---|
| Major conceptual restructure or direction change | Major (X) | 1.0.0 → 2.0.0 |
| New section, significant expansion, rollback | Minor (Y) | 1.2.0 → 1.3.0 |
| Typo fix, citation correction, clarification | Patch (Z) | 1.2.0 → 1.2.1 |

**Status definitions:**

| Status | Meaning |
|---|---|
| `Active Canon` | Fully integrated, aligned, and considered ground truth for GAIA-OS |
| `Experimental` | Allowed and tracked but easily revertible; not yet fully integrated |
| `Deprecated` | Retained for historical/audit context; not to be used as active guidance |

---

## IX. Canon Tagging Convention

```bash
# Stable documentation milestone tag format
git tag canon-YYYY-MM-DD          # date-based snapshot
git tag canon-v1.3.0-docs         # semantic version
git tag canon-v1.3.0-docs-stable  # explicitly validated

# Pre-rollback safety tag
git tag pre-rollback-YYYY-MM-DD

# Post-rollback restoration tag
git tag canon-YYYY-MM-DD-restored
```

---

## X. Integration with GAIA-OS Docs

This specification integrates with:
- **[DOC_ROLLBACK_LOG.md](./DOC_ROLLBACK_LOG.md)** — The living event record for all rollbacks and drills
- **[CANON_DEDUPLICATION_LOG.md](./CANON_DEDUPLICATION_LOG.md)** — Canon cleanup history
- **[CANON_LAW_STACK.md](./CANON_LAW_STACK.md)** — The authority hierarchy this spec protects
- **[EPISTEMIC_FRAMEWORK.md](./EPISTEMIC_FRAMEWORK.md)** — The standards a rolled-back doc must be re-validated against
- **[CALLING_REGISTRY.md](./CALLING_REGISTRY.md)** — Living callings that may trigger rollbacks

---

*Document version: 1.0.0 | Created: 2026-06-27 | Status: Active Canon*

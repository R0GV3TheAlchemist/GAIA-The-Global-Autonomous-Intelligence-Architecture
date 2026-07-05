## Summary

<!-- What does this PR do? One paragraph max. -->

## Linked Issue

Closes #

<!-- Every PR must close an issue. No free-floating PRs. -->

## Type of Change

- [ ] Bug fix (`fix/issue-NNN-*`)
- [ ] New feature (`feature/issue-NNN-*`)
- [ ] Architecture change (ADR required — link below)
- [ ] Process / documentation (`process/issue-NNN-*`)
- [ ] Research output (`research/issue-NNN-*`)

## Pre-Merge Checklist

### All PRs
- [ ] Branch name follows convention: `{type}/issue-{number}-{description}`
- [ ] `Closes #` is filled in above
- [ ] All existing tests pass (`pytest tests/` and/or TypeScript type check)
- [ ] No new lint errors (Ruff for Python, ESLint for TypeScript)
- [ ] Definition of Done from linked issue is fully satisfied (all boxes checked)

### If this touches `core/` or `src/gaian/`
- [ ] Architectural impact assessed — is an ADR required?
- [ ] If ADR required: ADR is written, status is `Accepted`, and linked below
- [ ] No component in `src/gaian/` has hardcoded values that should come from `GAIANProfile`

### If this touches `docs/adr/`
- [ ] ADR follows the template in `docs/adr/ADR-000-template.md`
- [ ] `docs/adr/README.md` updated
- [ ] ADR status is `Accepted` (not `Proposed`) before merge

### If this includes UI changes (`src/gaian/`)
- [ ] Screenshot or recording attached below
- [ ] Console does not show a blank state under any profile condition
- [ ] Offline-first fallback verified

### If this includes Python changes
- [ ] `knowledge_type` set on all new claims (ADR-001)
- [ ] No simulation results written directly to real-world state
- [ ] `tools/claim_validator.py` passes

## ADR Reference

<!-- If this is an architecture change, link the ADR here. -->
ADR: 

## Known Limitations / Follow-up Issues

<!-- What does this PR intentionally NOT solve? File follow-up issues for these. -->
- 

## Screenshots / Recordings

<!-- For UI changes only. Delete this section if not applicable. -->

---
*PR filed per CONTRIBUTING.md PR protocol — Issue #757*
*Governed by: [CONTRIBUTING.md](../CONTRIBUTING.md)*

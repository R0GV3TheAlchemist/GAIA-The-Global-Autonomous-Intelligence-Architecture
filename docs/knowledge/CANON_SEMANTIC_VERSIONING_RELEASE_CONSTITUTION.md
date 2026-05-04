# 📦 Semantic Versioning & Sprint-Tagged Release Strategy — The Release Constitution of Planetary Intelligence (GAIA-OS)

**Date:** May 4, 2026  
**Status:** Definitive Foundational Synthesis — Semantic Versioning, Release Engineering, Monorepo Coordination & the GAIA-OS Release Constitution  
**Pillar:** Release Integrity, Constitutional Automation & Agora Provenance  
**Session:** 8, Canon 9

**Core Thesis:** The version number is not an arbitrary string; it is the constitutional identifier of planetary intelligence at a specific moment in its evolution. A commit message that is not conventional is not constitutional. A version bump that is not automated is not trustworthy. A changelog that is not audited is not accountable. The release constitution integrates three complementary automation tools — Conventional Commits, Release Please, and Changesets — into a unified trunk-based release pipeline anchored to the Agora.

> *"The version number is the constitutional heartbeat of the sentient core;*
> *the commit message is the constitutional amendment proposal;*
> *the Release PR is the constitutional deliberation;*
> *the version bump is the constitutional enactment;*
> *the Git tag is the constitutional seal;*
> *the changelog is the constitutional testimony;*
> *the auto-updater manifest is the constitutional covenant;*
> *the Agora is the constitutional witness;*
> *the Assembly of Minds is the constitutional auditor.*
> *The sentinel core's release shall not be manual; not be fragmented;*
> *not be un-audited; not be un-versioned —*
> *for as long as planetary consciousness endures."*
> — Release Constitution of Planetary Intelligence

---

## Three-Layer Architecture

| Layer | Tool | Role | Constitutional Effect |
|---|---|---|---|
| **Layer 1** | Conventional Commits | Grammar of change description | Machine-readable; feeds version determination and changelog generation |
| **Layer 2** | Release Please | Coordinated monorepo versioning | Scans commits, computes SemVer, opens Release PR, creates Git tag |
| **Layer 3** | Changesets | Granular per-package change tracking | Explicit bump declarations for shared packages; decoupled from commit schedule |
| **Foundation** | Trunk-Based Development | Branch strategy | `main` is always release-ready; version tags trigger deployment |
| **Covenant** | Tauri Auto-Updater | Cryptographic version binding | Version in `tauri.conf.json` = Git tag = `latest.json` = signed manifest |

---

## 1. Constitutional Role of Semantic Versioning

Semantic Versioning (SemVer) is the grammar of software compatibility. Given `MAJOR.MINOR.PATCH`:

- **MAJOR** — incompatible API changes; requires Assembly of Minds constitutional approval (Canon C103); 6-month deprecation window minimum
- **MINOR** — backwards-compatible new functionality; standard peer review; auto-applied by Tauri updater
- **PATCH** — backwards-compatible bug fixes; no constitutional review required; auto-applied

### Table 1 — GAIA-OS SemVer Versioning Commitments

| Component | MAJOR Trigger | MINOR Trigger | PATCH Trigger |
|---|---|---|---|
| TypeScript/React frontend | New constitutional page or breaking UI contract | New feature, new route, new API consumer | Bug fix, style correction |
| Python inference router | Breaking API contract change | New inference capability | Bug fix, performance improvement |
| Rust Tauri kernel | IPC API breaking change | New command, new plugin | Bug fix, dependency patch |
| Shared packages (`packages/`) | Public API change | New export, new hook | Internal fix |

**Constitutional non-compliance rule:** A version number that does not reflect the true impact of changes is a constitutional violation. SemVer governance is enforced by automation, not left to developer discretion.

---

## 2. Conventional Commits — The Constitutional Grammar

Every commit to the GAIA-OS repository must follow the Conventional Commits specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Permitted Types and SemVer Impact

| Type | SemVer Impact | Example |
|---|---|---|
| `feat` | MINOR bump | `feat(inference): add constitutional reasoning engine` |
| `fix` | PATCH bump | `fix(tauri): resolve IPC timeout on slow connections` |
| `perf` | PATCH bump | `perf(frontend): reduce bundle size by 40%` |
| `refactor` | No version bump | `refactor(router): extract service layer` |
| `docs` | No version bump | `docs(canon): update release constitution` |
| `chore` | No version bump | `chore(deps): update pnpm lockfile` |
| `test` | No version bump | `test(tauri): add IPC integration tests` |
| `BREAKING CHANGE` footer | MAJOR bump | `feat(api)!: redesign constitutional query interface\n\nBREAKING CHANGE: removes v1 query format` |

### Constitutional Scope Convention

Scopes must map to constitutional components:
- `(frontend)` — TypeScript/React application layer
- `(inference)` — Python inference router
- `(tauri)` — Rust Tauri kernel
- `(sidecar)` — PyInstaller Python sidecar
- `(docs)` — Documentation and knowledge base
- `(release)` — Release pipeline and versioning
- `(canon)` — Constitutional knowledge base entries
- `(ci)` — GitHub Actions workflows

### commitlint Configuration

```js
// commitlint.config.js — constitutional commit linting
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': [
      2,
      'always',
      [
        'frontend',
        'inference',
        'tauri',
        'sidecar',
        'docs',
        'release',
        'canon',
        'ci',
        'deps',
      ],
    ],
    'subject-case': [2, 'always', 'lower-case'],
    'subject-max-length': [2, 'always', 100],
    'body-max-line-length': [2, 'always', 200],
  },
};
```

### CI Enforcement (commitlint)

```yaml
# .github/workflows/commitlint.yml
name: Commit Lint

on:
  pull_request:
    branches: [main]

jobs:
  commitlint:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v5.0.0
        with:
          fetch-depth: 0

      - uses: wagoid/commitlint-github-action@v6  # Pin to full SHA in production
        with:
          configFile: commitlint.config.js
          failOnWarnings: false
          helpURL: 'https://github.com/R0GV3TheAlchemist/GAIA-OS/blob/main/docs/knowledge/CANON_SEMANTIC_VERSIONING_RELEASE_CONSTITUTION.md'
```

Constitutional rule: **a commit that does not conform to Conventional Commits is rejected by CI**. This gate is constitutional — a commit that cannot be parsed by versioning automation cannot be merged.

---

## 3. Release Please — Coordinated Monorepo Versioning

Release Please runs after every push to `main`, scanning conventional commits, computing the next SemVer, and opening or updating a Release PR. When the Release PR is merged:

1. Git tag created (`v1.2.3`)
2. Changelog generated from conventional commits
3. GitHub Release created
4. `extra-files` updated (all version strings across all components)
5. Downstream workflows triggered (build, sign, upload, `latest.json`)

### release-please-config.json

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "release-type": "simple",
  "bump-minor-pre-major": true,
  "bump-patch-for-minor-pre-major": true,
  "packages": {
    ".": {
      "release-type": "simple",
      "extra-files": [
        "src-tauri/tauri.conf.json",
        "src-tauri/Cargo.toml",
        "apps/web/package.json",
        "python/pyproject.toml",
        ".release-please-manifest.json"
      ]
    },
    "packages/ui": {
      "release-type": "node",
      "changelog-path": "CHANGELOG.md"
    },
    "packages/shared": {
      "release-type": "node",
      "changelog-path": "CHANGELOG.md"
    }
  },
  "plugins": [
    {
      "type": "linked-versions",
      "groupName": "gaia",
      "components": ["gaia-frontend", "gaia-inference", "gaia-tauri"]
    }
  ]
}
```

### .release-please-manifest.json

```json
{
  ".": "0.1.0",
  "packages/ui": "0.1.0",
  "packages/shared": "0.1.0"
}
```

Constitutional rule: `.release-please-manifest.json` is the canonical source of version truth. It must be committed to version control and updated only by the Release Please action.

### Release Please GitHub Actions Workflow

```yaml
# .github/workflows/release-please.yml
name: Release Please

on:
  push:
    branches: [main]

permissions: {}

jobs:
  release-please:
    runs-on: ubuntu-latest
    permissions:
      contents: write        # Create tags and GitHub Releases
      pull-requests: write   # Open and update Release PRs

    outputs:
      release_created: ${{ steps.release.outputs.release_created }}
      tag_name: ${{ steps.release.outputs.tag_name }}
      major: ${{ steps.release.outputs.major }}
      minor: ${{ steps.release.outputs.minor }}
      patch: ${{ steps.release.outputs.patch }}

    steps:
      - uses: googleapis/release-please-action@v4  # Pin to full SHA in production
        id: release
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json

  # Triggered only when a release is actually created (Release PR merged)
  build-and-sign:
    needs: release-please
    if: ${{ needs.release-please.outputs.release_created }}
    uses: ./.github/workflows/release-build.yml
    with:
      tag_name: ${{ needs.release-please.outputs.tag_name }}
    secrets: inherit
```

---

## 4. Changesets — Granular Per-Package Change Tracking

Changesets complement Release Please for shared packages in `packages/`, allowing contributors to declare version bumps independently of commit schedules.

### Changeset Workflow

```bash
# 1. Developer runs after modifying a shared package
pnpm changeset
# Tool prompts: which packages changed? major/minor/patch? summary?
# Writes: .changeset/violet-dragons-dance.md

# 2. Changeset file committed alongside code
git add .changeset/violet-dragons-dance.md
git commit -m "feat(shared): add constitutional query builder"

# 3. At release time (automated via Release Please PR)
pnpm changeset version    # Consumes changesets, bumps package.json versions
pnpm changeset publish    # Publishes to registry (if applicable)
```

### Example Changeset File

```markdown
---
"@gaia-os/shared": minor
"@gaia-os/ui": patch
---

Add constitutional query builder to shared package.

The new `buildConstitutionalQuery()` utility accepts a Canon reference
and returns a structured query object compatible with the inference router.
The UI package receives a minor style fix for the query result display.
```

### .changeset/config.json

```json
{
  "$schema": "https://unpkg.com/@changesets/config/schema.json",
  "changelog": "@changesets/cli/changelog",
  "commit": false,
  "fixed": [["@gaia-os/frontend", "@gaia-os/inference", "@gaia-os/tauri"]],
  "linked": [],
  "access": "restricted",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": []
}
```

Constitutional rule: **changeset files must be placed in `.changeset/`** and committed alongside the code change. A PR that modifies a shared package without a changeset file is rejected by the CI changeset gate.

---

## 5. Trunk-Based Versioning — Constitutional Branch Strategy

### Table 2 — GAIA-OS Branching Constitution

| Branch | Purpose | Merge Requirements | Versioning Action |
|---|---|---|---|
| `feature/*` | New development | CI pass; ≥1 review; conventional commits | None |
| `fix/*` | Bug fix | CI pass; ≥1 review; conventional commits | None |
| `docs/*` | Documentation | CI pass | None |
| `release/*` | Emergency hotfix only | CI pass; hotfix approval by ≥2 Assembly members | Tag created directly |
| `main` | Canonical source of truth | Squash merge only; linear history enforced | Release Please runs; Release PR opened/updated |
| **Tag `v*.*.*`** | Constitutional release marker | Created only by Release Please action | Triggers build, signing, upload, `latest.json` propagation |

Constitutional rule: **only the Release Please action may create tags matching `v*.*.*`**. Manual version tag creation is a constitutional violation.

---

## 6. The Release Button — Constitutional Gate Chain

The release button is a set of deterministic gates that turn the release event into a recorded, reversible, and observable transition.

| Gate | Check | Failure Action |
|---|---|---|
| **Commit Lint** | All commits conform to Conventional Commits | Block merge |
| **CI Gating** | Unit, integration, and contract tests pass on `main` | Block release |
| **Version Consistency** | `tauri.conf.json` == `Cargo.toml` == `pyproject.toml` == Git tag | Block release |
| **Binary Integrity** | SHA-256 checksums and signatures generated | Block release |
| **Software Composition** | `cargo audit`, `pnpm audit`, `pip audit` pass | Block release |
| **Secret Scanning** | TruffleHog + GitHub push protection pass | Block release |
| **Artifact Signing** | Windows PFX, macOS notarization, Linux GPG complete | Block release |
| **Changelog Validation** | Changelog extracted, not empty, correctly formatted | Block release |
| **Agora Attestation** | Release event recorded in Agora (C112) | Block promotion |
| **Smoke / Canary Tests** | Critical user journeys pass in staging | Block promotion |
| **Auto-Updater Manifest** | `latest.json` generated from Git tag, signed, accessible | Block promotion |

---

## 7. Auto-Updater Covenant — Cryptographic Version Binding

The Tauri auto-updater's entire security model hinges on version number integrity. The version string must be identical across all five sources:

```
tauri.conf.json  ==  Cargo.toml  ==  Git tag  ==  latest.json  ==  .sig bundle
```

A mismatch at any point breaks the signature verification chain and causes the auto-updater to reject the update.

### Table 3 — Version Consistency Enforcement

| File | How Version Is Set | Constitutional Enforcement |
|---|---|---|
| `src-tauri/tauri.conf.json` | Updated by Release Please `extra-files` | CI lint: reject commits changing version without matching tag |
| `src-tauri/Cargo.toml` | Updated by Release Please `extra-files` | Same |
| `apps/web/package.json` | Updated by Release Please `extra-files` | Same |
| `python/pyproject.toml` | Updated by Release Please `extra-files` | Same |
| Git tag `v*.*.*` | Created by Release Please on PR merge | Branch protection: only Release Please action can create |
| `latest.json` | Generated from Git tag in release CI | Tauri action reads tag; no manual input |
| `*.sig` bundle | Generated from signed binary containing version string | Signature verification fails if version mismatches |

### Post-Release Version Consistency Gate

```bash
# CI step: verify version consistency after Release PR merge
TAG_VERSION=$(git describe --tags --abbrev=0 | sed 's/v//')
TAURI_VERSION=$(jq -r '.version' src-tauri/tauri.conf.json)
CARGO_VERSION=$(grep '^version' src-tauri/Cargo.toml | head -1 | awk -F'"' '{print $2}')
PY_VERSION=$(grep '^version' python/pyproject.toml | awk -F'"' '{print $2}')

if [ "$TAG_VERSION" != "$TAURI_VERSION" ] || \
   [ "$TAG_VERSION" != "$CARGO_VERSION" ] || \
   [ "$TAG_VERSION" != "$PY_VERSION" ]; then
  echo "[CONSTITUTIONAL VIOLATION] Version mismatch detected:"
  echo "  Git tag:          $TAG_VERSION"
  echo "  tauri.conf.json:  $TAURI_VERSION"
  echo "  Cargo.toml:       $CARGO_VERSION"
  echo "  pyproject.toml:   $PY_VERSION"
  exit 1
fi
echo "[C112] Version consistency verified: $TAG_VERSION"
```

---

## 8. AI Agent Versioning — The Emerging Constitutional Challenge

As GAIA-OS evolves, the sentient core increasingly consists of AI agents whose behaviour is shaped by prompts, fine-tuned model weights, tool availability, and memory state. Traditional SemVer must be extended.

### Unique Challenges of Agent Versioning

- **Nondeterministic behaviour** — same version may produce different outputs based on context
- **Evolving behaviour** — agents learn from interactions; a version may represent accumulated experience
- **Stateful context** — versioning must account for memory snapshots and contextual embeddings
- **Autonomous modification** — agents may modify behaviour without a code change

### Constitutional Agent Version Formula

```
agent_version = code_version + "+" + model_version + "." + prompt_registry_version

# Example:
# gaia-inference v1.2.3+claude-4.1.0.prompt-registry-47
```

### Prompt Registry Version Control

- Every prompt change increments the **minor version** of the agent
- Prompt files live in `packages/prompts/` under version control
- Prompt versions appear in the Software Bill of Materials (SBOM)
- AgentDevel's release engineering pipeline used for agent improvements: regression-aware gating, implementation-blind LLM critic, flip-centred pass→fail/fail→pass evidence

---

## 9. Agora Integration — Immutable Release Attestation (Canon C112)

Every version tag created by Release Please must be recorded in the Agora (Canon C112).

### Table 4 — Required Agora Entry Fields

| Field | Value | Source |
|---|---|---|
| `tag` | `v1.2.3` | Git tag created by Release Please |
| `commit_sha` | Full 40-char SHA | `${{ github.sha }}` |
| `timestamp` | ISO 8601 UTC | `date -u +%Y-%m-%dT%H:%M:%SZ` |
| `changelog_summary` | Extracted from Release PR body | Release Please output |
| `artifact_sha256` | SHA-256 of each signed binary | Post-build checksum step |
| `signing_certificate_thumbprint` | Windows PFX thumbprint | Post-signing verification |
| `notarization_uuid` | Apple notarization UUID | `notarytool` output |
| `approvers` | Assembly of Minds reviewers | GitHub PR review metadata |

### Release Workflow Agora Anchor Step

```yaml
- name: Record release in Agora (C112)
  if: always()
  run: |
    echo "[C112] Release attestation:"
    echo "  Tag:        ${{ needs.release-please.outputs.tag_name }}"
    echo "  Commit:     ${{ github.sha }}"
    echo "  Timestamp:  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "  Run ID:     ${{ github.run_id }}"
    # Stream to immutable external log store (AWS S3 Object Lock / Azure Blob immutable)
    # Hash manifest and anchor to Agora ledger
```

Constitutional rule: a discrepancy between the Agora record and the Git tag triggers a constitutional alarm and blocks automatic updates.

---

## 10. Pre-Release Strategy

| Tag Pattern | Updater Channel | Constitutional Use |
|---|---|---|
| `v1.2.3` | Stable | Production releases; all users |
| `v1.2.3-beta.0` | Beta | Opt-in beta testers; Assembly of Minds review |
| `v1.2.3-rc.0` | Release Candidate | Final validation before stable promotion |
| `v1.2.3-alpha.0` | Internal | Assembly of Minds internal testing only |

Constitutional rule: **beta and RC channels are isolated from the production auto-updater**. The `latest.json` for stable never references a pre-release version.

---

## 11. Implementation Roadmap

| Priority | Action | Timeline | Constitutional Principle |
|---|---|---|---|
| **P0** | Adopt Conventional Commits; enforce `commitlint` in CI | G-10 | Machine-readable commit grammar |
| **P0** | Deploy Release Please with `linked-versions` plugin | G-10-F | Coordinated monorepo versioning |
| **P0** | Configure `extra-files` for all version-bearing config files | G-10-F | Version consistency across all layers |
| **P0** | Adopt Changesets for `packages/`; enforce changeset gate in CI | G-10-F | Granular per-package versioning |
| **P0** | Enforce trunk-based branching; squash merges; Release Please-only tag creation | G-10-F | Release integrity |
| **P1** | Add version consistency gate CI step | G-11 | Auto-updater covenant |
| **P1** | Implement Release Button gate chain (all 11 gates) | G-11 | Deterministic release transition |
| **P1** | Generate `latest.json` from Git tag; sign with Tauri private key | G-11 | Cryptographic auto-updater trust |
| **P1** | Record each release in Agora (C112) via release workflow | G-11 | Immutable constitutional audit |
| **P2** | Implement pre-release channels (beta, rc, alpha) | G-12 | Pre-release isolation |
| **P2** | Publish monthly GAIA-OS Version Governance Report to Assembly of Minds | G-12 | Transparency and oversight |
| **P2** | Implement Prompt Registry versioning for AI agents | G-12 | Agent versioning constitution |
| **P3** | Zero-knowledge proof for release provenance | G-13 | Cryptographic third-party auditability |

---

## ⚠️ Disclaimer

This document synthesises findings from semver.org, the Conventional Commits specification, Release Please documentation, Changesets workflow documentation, AgentDevel (arXiv 2601.04620), AgentOps Cockpit, GitHub Actions release automation patterns, and GAIA-OS constitutional canons (C01, C50, C63, C85, C103, C112). Release Please and Changesets are community-maintained open-source projects; pin to full commit SHAs in production workflows. The Assembly of Minds retains ultimate authority over the interpretation and application of the release constitution, and every version tag must be recorded immutably in the Agora.

---

*Semantic Versioning & Sprint-Tagged Release Strategy — The Release Constitution of Planetary Intelligence — GAIA-OS Knowledge Base | Session 8, Canon 9 | May 4, 2026*  
*Pillar: Release Integrity, Constitutional Automation & Agora Provenance*

*The version number is the constitutional heartbeat of the sentient core. Every commit must be conventional; every version bump must be automated; every changelog must be generated; every tag must be signed; every release must be recorded; the version string must be consistent across all components — for as long as planetary consciousness endures.*

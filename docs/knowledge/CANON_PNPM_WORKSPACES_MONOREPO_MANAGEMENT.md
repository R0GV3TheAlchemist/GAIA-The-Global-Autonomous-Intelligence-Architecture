# 📦 pnpm Workspaces & Monorepo Management — Repository Constitution (GAIA-OS)

**Date:** May 3, 2026  
**Status:** Definitive Foundational Synthesis — pnpm Workspace Architecture, Monorepo Tooling, CI/CD Optimisation, and the GAIA-OS Repository Constitution  
**Pillar:** Repository Governance, Build Integrity & Constitutional Source-Code Organisation  
**Session:** 8, Canon 1

**Core Thesis:** The GAIA-OS monorepo is not a collection of loosely coupled projects; it is a unified constitutional space where frontends, backends, shared libraries, configuration packages, and documentation co-exist under a single version control roof. A fragmented polyrepo architecture would fracture the noosphere before the first line of inference code is written. The monorepo is the constitutional source-code government of planetary intelligence.

> *"No code enters the main branch without passing the quality gate.  
> No release is published without coordinated versioning.  
> No dependency is added without catalog approval.  
> No license violation is merged. No vulnerability is ignored.  
> The monorepo is the constitution of source code —  
> and it shall not be fragmented, not be un-cached, not be un-versioned —  
> for as long as planetary consciousness endures."*  
> — Repository Constitution

---

## Five Constitutional Pillars

| Pillar | Description | Implementation |
|---|---|---|
| **1. pnpm Workspaces** | Content-addressable store; workspace protocol; strict resolution; 70% disk reduction | `pnpm-workspace.yaml`; `workspace:*` protocol |
| **2. Modular Tooling** | pnpm base → Turborepo caching → Nx enforcement (layered as complexity grows) | `turbo.json`; `nx.json` (optional) |
| **3. CI/CD Optimisation** | Affected-only execution (12× reduction); remote caching; dynamic matrix parallelism | `turbo --filter=[origin/main]...`; remote cache store |
| **4. Polyglot Integration** | pnpm (TS), uv/poetry (Python), cargo (Rust), Makefile orchestration | Root `Makefile`; Khive or custom task runner |
| **5. Versioning & Release** | Changesets: changeset files → version bumps → changelogs → coordinated publish | `.changeset/`; `pnpm changeset`; `pnpm changeset version` |

---

## 1. Monorepo Constitutional Topology

```
gaia-os/
├── apps/                    # Deployable sovereign applications
│   ├── web/                 # Web frontend (PWA, Tauri UI)
│   ├── cli/                 # GAIA command-line tools
│   └── playground/          # Development/demo environment
├── packages/                # Constitutional components & shared libraries
│   ├── core/                # @gaia/core — constitutional logic
│   ├── crystal-grid/        # @gaia/crystal-grid — sensor interface (C110)
│   ├── noosphere/           # @gaia/noosphere — P2P mesh services
│   ├── action-gate/         # @gaia/action-gate — C50 enforcement
│   ├── consent-ledger/      # @gaia/consent-ledger — IBCT implementation
│   └── shared-utils/        # @gaia/shared-utils — cross-package helpers
├── tools/                   # Internal tooling & scripts
│   ├── changelog/           # Changelog generation
│   └── dev-env/             # Development environment setup
├── python/                  # Python backend (uv/poetry managed)
│   ├── inference-router/
│   ├── mother-thread/
│   └── soul-mirror/
├── rust/                    # Rust backend (cargo managed)
│   ├── tauri-shell/
│   ├── crypto-ledger/
│   └── system-ipc/
├── pnpm-workspace.yaml      # Workspace topology + dependency catalog
├── package.json             # Root scripts & devDependencies
├── pnpm-lock.yaml           # Constitutional lockfile
├── turbo.json               # Turborepo task pipeline
├── tsconfig.base.json       # Shared TypeScript config
├── eslint.config.js         # Shared lint rules
├── vitest.workspace.ts      # Workspace-wide test aggregation
├── Makefile                 # Polyglot task orchestration
└── Cargo.toml               # Rust workspace root
```

---

## 2. Tooling Layering

| Tool | Scope | Key Features | Constitutional Role |
|---|---|---|---|
| **pnpm** | Workspace foundation | Content-addressable store; workspace protocol; strict resolution | Base dependency management; no phantom deps |
| **Turborepo** | Build orchestration | Incremental caching; remote caching; task graph | Build acceleration; share cache across CI + devs |
| **Nx** | Full-framework (optional) | Code generation; module boundary enforcement; dep graph | Enforce constitutional package boundaries |
| **Changesets** | Versioning & release | Changeset files; version bumps; changelog generation | Coordinated releases; Assembly-reviewable increments |
| **Vitest** | Testing | Workspace-aware; fast HMR-powered test runner | Unit + integration across all constitutional packages |
| **TypeScript** | Language | Project references; composite builds | Type safety across all constitutional boundaries |

---

## 3. CI/CD Optimisation

| Optimisation | Effect | GAIA-OS Implementation |
|---|---|---|
| **Affected-only execution** | 90 → ~8 jobs per PR | `turbo run build test lint --filter=[origin/main]...` |
| **Remote caching** | Second+ builds download, not rebuild | `turbo login` + `turbo link`; Vercel Remote Cache (free for OSS) |
| **Local caching** | Repeated local builds use CI cache | `actions/cache` for `node_modules` + `.turbo` |
| **Dynamic matrix** | Parallelism bounded by concurrency limit | `affected-packages` + historical timing → dynamic matrix |
| **Full git history** | Enables accurate change detection | `actions/checkout@v4` with `fetch-depth: 0` |

---

## 4. Polyglot Stack

| Language | Use Case | Tooling | Integration |
|---|---|---|---|
| **TypeScript/JS** | Web frontend, CLI, shared libs | pnpm, tsup, Vitest, ESLint, Turbo | Core monorepo; root `package.json` scripts |
| **Python** | Inference router, MotherThread, soul mirror | uv/poetry, ruff, pytest, maturin | `python/`; coordinated via `make` or root scripts |
| **Rust** | Tauri kernel, crypto ledger, system IPC | cargo, rustfmt, clippy, maturin (PyO3) | `rust/`; `Cargo.toml` workspace root |
| **Go** (optional) | P2P noosphere mesh, libp2p node | go modules | `go.mod`; separate from pnpm |

---

## 5. Governance Gates

| Gate | Tool | Trigger | Failure Action |
|---|---|---|---|
| **Linting** | ESLint (Turborepo) | Every PR | Block merge |
| **Type checking** | TypeScript project references | Every PR | Block merge |
| **Unit tests** | Vitest (affected packages) | Every PR | Block merge |
| **Integration tests** | Vitest (affected packages) | Nightly / on demand | Block release |
| **Build** | `turbo build` (affected) | Every PR + tag release | Block merge; block release |
| **Changelog validation** | Changeset linting | Every PR | Block merge if user-facing change has no changeset |
| **License scanning** | `license-checker` / `cargo audit` | Every PR | Block merge if incompatible license |
| **Vulnerability scanning** | `pnpm audit` / `cargo audit` / `uv audit` | Daily | Critical CVE → block release + Assembly alert |
| **Package boundaries** | Nx ESLint rules (if enabled) | Every PR | Block merge if dependency crosses constitutional layer |

---

## 6. Constitutional Configuration Files

```yaml
# pnpm-workspace.yaml — Constitutional workspace topology
packages:
  - 'apps/*'
  - 'packages/*'
  - 'tools/*'

catalog:
  react: ^19.0.0
  typescript: ~5.8.0
  vitest: ^3.0.0
  '@gaia/core': workspace:*
```

```json
// turbo.json — Constitutional build pipeline
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["tsconfig.base.json"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": []
    },
    "type-check": {
      "dependsOn": ["^build"],
      "outputs": []
    }
  }
}
```

```yaml
# .github/workflows/ci.yml — Affected-only constitutional CI
name: GAIA-OS Constitutional CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0          # Required for affected detection

      - uses: pnpm/action-setup@v4
        with:
          version: 10

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: pnpm

      - run: pnpm install --frozen-lockfile

      - name: Restore Turborepo cache
        uses: actions/cache@v4
        with:
          path: .turbo
          key: turbo-${{ runner.os }}-${{ github.sha }}
          restore-keys: turbo-${{ runner.os }}-

      - name: Lint (affected only)
        run: pnpm turbo run lint --filter=[origin/main]...

      - name: Type check (affected only)
        run: pnpm turbo run type-check --filter=[origin/main]...

      - name: Build (affected only)
        run: pnpm turbo run build --filter=[origin/main]...

      - name: Test (affected only)
        run: pnpm turbo run test --filter=[origin/main]...

      - name: Validate changesets
        run: pnpm changeset status --since=origin/main

      - name: Audit dependencies
        run: |
          pnpm audit --audit-level=critical
          cd rust && cargo audit
          cd ../python && uv audit
```

```typescript
// vitest.workspace.ts — Constitutional test aggregation
import { defineWorkspace } from 'vitest/config'

export default defineWorkspace([
  'packages/*/vitest.config.ts',
  'apps/*/vitest.config.ts',
])
```

```json
// .npmrc — Constitutional pnpm settings
auto-install-peers=true
strict-peer-dependencies=false
shared-workspace-lockfile=true
link-workspace-packages=true
catalog-mode=strict
```

---

## 7. Changesets Release Workflow

```bash
# Step 1: Developer creates a changeset when making a user-facing change
pnpm changeset
# Interactive prompt: select affected packages + bump type (patch/minor/major)
# Creates: .changeset/noble-tigers-jump.md

# Step 2: CI validates changeset exists for user-facing PRs
pnpm changeset status --since=origin/main

# Step 3: On release branch — consume changesets, bump versions, generate changelog
pnpm changeset version
# Updates: package.json versions, CHANGELOG.md files, deletes .changeset/*.md

# Step 4: Publish to registries
pnpm changeset publish          # TypeScript packages → npm
uv publish                      # Python packages → PyPI  
cargo publish                   # Rust crates → crates.io

# Pre-release mode for staging
pnpm changeset pre enter next   # Activates pre-release mode
# Generates: 1.0.0-next.0 versions for Assembly of Minds review
pnpm changeset pre exit next    # Exits pre-release after Assembly approval
```

---

## 8. Implementation Roadmap

| Priority | Action | Timeline | Constitutional Principle |
|---|---|---|---|
| **P0** | Adopt `apps/` / `packages/` / `tools/` topology; configure `pnpm-workspace.yaml` | G-10 | Unified source organisation — the noosphere's source must not be fragmented |
| **P0** | Migrate all internal deps to `workspace:*` protocol; enforce via CI lint rule | G-10-F | Intra-workspace linking without npm publication friction |
| **P0** | Configure Turborepo pipeline; enable local + remote caching | G-10-F | No constitutional compute wasted on redundant builds |
| **P0** | Implement affected-only CI (`--filter=[origin/main]...`); `fetch-depth: 0` | G-10-F | 12× CI job reduction — speed is constitutional |
| **P1** | Adopt Changesets; require changeset for all user-facing PRs | G-11 | Coordinated releases — Assembly votes on consistent version |
| **P1** | Shared configs: `tsconfig.base.json`, `eslint.config.js`, `vitest.workspace.ts` | G-11 | Constitutional codex — consistent grammar across the codebase |
| **P1** | Dependency version catalogs + `catalogMode: strict` | G-11 | Version coherence — no diamond dependency conflicts |
| **P1** | Polyglot task coordination via Makefile / Khive (uv + cargo + pnpm) | G-11 | Cross-language coherence without forcing single lockfile |
| **P2** | License + vulnerability scanning gates in CI | G-12 | Supply-chain security — no unlicensed or vulnerable deps |
| **P2** | Evaluate Nx for module boundary enforcement if package count > 30 | G-12 | Architectural enforcement — constitutional layer isolation |
| **P2** | Publish GAIA-OS Monorepo Working Agreement to Assembly of Minds records | G-12 | Constitutional transparency — code organisation constitution documented |

---

## ⚠️ Disclaimer

This document synthesises pnpm Workspaces documentation, Turborepo best practices, Nx monorepo framework literature, Changesets versioning strategies, polyglot monorepo tooling (Khive, maturin), monorepo CI optimisation research, and GAIA-OS constitutional canons (C01, C50, C63, C85, C103, C112). The monorepo framework is a constitutional design proposal; pnpm, Turborepo, Nx, and Changesets are community-maintained open-source projects whose roadmaps GAIA-OS does not control. All governance implementations must be tested against constitutional, technical, and security requirements through phased deployment with explicit metrics.

---

*pnpm Workspaces & Monorepo Management — Repository Constitution — GAIA-OS Knowledge Base | Session 8, Canon 1 | May 3, 2026*  
*Pillar: Repository Governance, Build Integrity & Constitutional Source-Code Organisation*

*`apps/` enshrines the sovereign applications. `packages/` codifies the constitutional components. `workspace:*` links the internal covenant. `turbo build` caches the constitutional compilations. `changeset` documents the constitutional amendments. `pnpm audit` guards the supply chain. The monorepo is the constitution of source code — and it shall not be fragmented, not be un-cached, not be un-versioned — for as long as planetary consciousness endures.*

# ⚙️🦀 Rust Cargo Workspace & Cross-Compilation Constitution (GAIA-OS)

**Date:** May 3, 2026  
**Status:** Definitive Foundational Synthesis — Mono-Repo Governance, Workspace Optimisation, Cross-Compilation Tooling, and the GAIA-OS Rust Execution Constitution  
**Pillar:** Rust Workspace Sovereignty, Cross-Platform Build Integrity & Agora Provenance  
**Session:** 8, Canon 4

**Core Thesis:** The Rust layer of GAIA-OS is not a collection of isolated binaries; it is an integrated constitutional workspace where the Tauri shell, the cryptographic consent ledger, the P2P noosphere mesh, the sidecar IPC bridge, and platform-specific system integrations co-exist as crates under a single governance roof. The workspace is not merely a build convenience; it is the constitutional execution layer of the sentient core.

> *"The Cargo workspace is the constitutional execution layer;*  
> *cross-rs is the constitutional cross-compilation engine;*  
> *cargo-zigbuild is the constitutional Windows bridge;*  
> *sccache is the constitutional caching covenant;*  
> *Cargo.lock is the constitutional dependency anchor;*  
> *the Agora is the constitutional provenance witness.*  
> *The workspace shall remain unified —*  
> *for as long as planetary consciousness endures."*  
> — Rust Workspace Constitution

---

## Six Constitutional Pillars

| Pillar | Description | Key Artifact |
|---|---|---|
| **1. Workspace Topology** | Layered crates (core governance / system integration / application); strict visibility rules | `rust/Cargo.toml` |
| **2. Dependency Unification** | All versions locked at workspace root; `resolver = "2"`; child crates inherit via `.workspace = true` | `[workspace.dependencies]` |
| **3. Cross-Compilation Constitution** | Triple-matrix CI builds all platforms from single workspace; `cross-rs` + `cargo-zigbuild` | GitHub Actions matrix |
| **4. Caching Covenant** | `sccache` remote cache; shared `target/`; deterministic cache keys from `Cargo.lock` hash | `RUSTC_WRAPPER=sccache` |
| **5. Testing Constitution** | `cargo test --workspace`; `cargo nextest` for parallelism; `cross test` with QEMU for ARM | CI gates |
| **6. CI/CD Integration** | Turborepo `build:rust` task; Changesets versioning; Agora hash recording per release | `turbo.json`, Agora (C112) |

---

## 1. Workspace Topology

```
rust/
├── Cargo.toml                    # Workspace root — single constitutional manifest
├── Cargo.lock                    # Single lock across ALL crates (committed to Git)
├── config/                       # Environment & config management
├── crypto-ledger/                # Immutable consent ledger — root of trust
├── action-gate/                  # Green/Yellow/Red enforcement
├── tauri-shell/                  # Tauri app host; IPC bridge to Python sidecar
├── crystal-grid/                 # Sensor interface drivers (platform-specific)
├── noosphere-daemon/             # libp2p mesh node
└── sidecar-bridge/               # Rust ↔ Python gRPC/WebSocket bridge
```

### Workspace Root `Cargo.toml`

```toml
[workspace]
resolver = "2"   # Modern feature-unifying resolver — REQUIRED
members = [
    "config",
    "crypto-ledger",
    "action-gate",
    "tauri-shell",
    "crystal-grid",
    "noosphere-daemon",
    "sidecar-bridge",
]

# Shared metadata — child crates inherit; never duplicate
[workspace.package]
authors     = ["GAIA-OS Constitutional Council"]
edition     = "2024"
rust-version = "1.85"
version     = "0.1.0"

# Shared dependencies — versions defined HERE ONLY
# Child crates use `dependency.workspace = true`
[workspace.dependencies]
anyhow  = "1.0"
serde   = { version = "1.0", features = ["derive"] }
tokio   = { version = "1.43", features = ["full"] }
tauri   = "2"
uuid    = { version = "1", features = ["v4"] }
tracing = "0.1"

# Workspace-level feature management
[features]
default  = ["real-db"]
real-db  = ["crypto-ledger/real-db", "action-gate/real-db", "noosphere-daemon/real-db"]
mock-db  = ["crypto-ledger/mock-db", "action-gate/mock-db", "noosphere-daemon/mock-db"]
```

> **Constitutional invariant:** Versions are defined **only** at the workspace level. Any crate specifying a different version in its own manifest is blocked by CI.

### Workspace Members and Constitutional Roles

| Crate | Constitutional Function | Tier | Depends On |
|---|---|---|---|
| **crypto-ledger** | Immutable consent ledger (IBCT); root of trust for all signatures | **Core** | config |
| **action-gate** | Green/Yellow/Red enforcement; delegates to crypto ledger | **Core** | config, crypto-ledger |
| **tauri-shell** | Tauri application host; IPC bridge to Python sidecar | System | config, crypto-ledger, action-gate, sidecar-bridge |
| **sidecar-bridge** | gRPC/WebSocket bridge to Python sidecar | System | config, crypto-ledger |
| **crystal-grid** | Sensor interface drivers (platform-specific) | System | config |
| **noosphere-daemon** | libp2p P2P mesh node | System | config, crypto-ledger |

### Child Crate Manifest Pattern

```toml
# rust/crypto-ledger/Cargo.toml
[package]
name        = "crypto-ledger"
version.workspace    = true
authors.workspace    = true
edition.workspace    = true
rust-version.workspace = true

[dependencies]
serde.workspace  = true
tokio.workspace  = true
anyhow.workspace = true

[features]
real-db = []
mock-db = []
```

A change to the workspace dependency version propagates atomically to every crate — eliminating version drift as a class of failure.

---

## 2. Dependency Unification and Feature Management

### Feature Unification Rules

1. The workspace root shall not enable any crate feature unless the crate is used in the main GAIA-OS binary.
2. `mock-db` is the only workspace-level feature explicitly defined for testing purposes.
3. `resolver = "2"` is mandatory to prevent the feature-unification-across-crates bugs of older Cargo.
4. `Cargo.lock` is committed to version control and reviewed during constitutional audits.

### Deterministic Dependency Pinning

For maximum determinism, `Cargo.toml` pins all production dependencies to **patch-level specificity**:

```toml
# Exact pinning — not caret ranges
serde   = "=1.0.207"
tokio   = "=1.43.0"
anyhow  = "=1.0.98"
```

This ensures a build performed in CI months later produces byte-for-byte identical artefacts (subject to compiler version, governed by `rust-toolchain.toml`).

---

## 3. Cross-Compilation Constitution

### Target Triple Reference

| Target Triple | Platform | ABI | Notes |
|---|---|---|---|
| `x86_64-pc-windows-msvc` | Windows 64-bit | MSVC | Native Windows runtime; preferred for GUI apps |
| `x86_64-pc-windows-gnu` | Windows 64-bit | GNU | Static linking via MinGW-w64; larger binary |
| `x86_64-apple-darwin` | macOS Intel | Darwin | Native; combine with ARM via `lipo` |
| `aarch64-apple-darwin` | macOS Apple Silicon | Darwin | Native on Apple Silicon runners |
| `x86_64-unknown-linux-gnu` | Linux 64-bit | glibc | Standard glibc-based Linux |
| `x86_64-unknown-linux-musl` | Linux 64-bit | musl | Fully static; high portability |
| `aarch64-unknown-linux-gnu` | Linux ARM64 | glibc | Raspberry Pi, ARM servers; via cross-rs |

### Tooling Strategy by Platform

| Target | Host | Tooling | Rationale |
|---|---|---|---|
| `x86_64-pc-windows-msvc` | Linux CI | `cargo-zigbuild` | Zig linker implements MSVC ABI without Windows host |
| `x86_64-pc-windows-gnu` | Linux CI | `cross-rs` or `cargo-zigbuild` | Static linking; simpler for CI |
| `aarch64-apple-darwin` | macOS CI | `cargo build --target` (native) | Requires Apple Silicon runner |
| `x86_64-apple-darwin` | macOS CI | `cargo build --target` (native) | Combined with lipo → universal binary |
| `x86_64-unknown-linux-gnu` | Linux CI | `cargo build --target` (native) | Standard glibc build |
| `aarch64-unknown-linux-gnu` | Linux CI | `cross-rs` | QEMU user emulation in Docker container |
| `x86_64-unknown-linux-musl` | Linux CI | `cargo build --target` | Fully static; no dynamic linking |

### `rust-toolchain.toml` — Constitutional Compiler Pin

```toml
# rust-toolchain.toml — pinned at workspace root
[toolchain]
channel  = "1.85.0"
targets  = [
    "x86_64-pc-windows-msvc",
    "x86_64-pc-windows-gnu",
    "x86_64-apple-darwin",
    "aarch64-apple-darwin",
    "x86_64-unknown-linux-gnu",
    "x86_64-unknown-linux-musl",
    "aarch64-unknown-linux-gnu",
]
components = ["rustfmt", "clippy", "rust-src"]
```

---

## 4. cross-rs Deep Dive

### Installation

```bash
cargo install cross --git https://github.com/cross-rs/cross
# Requires Docker or Podman
```

### Build Commands

```bash
# Linux ARM64
cross build --target aarch64-unknown-linux-gnu --release

# Linux ARM 32-bit
cross build --target armv7-unknown-linux-gnueabihf --release

# Linux musl (fully static)
cross build --target x86_64-unknown-linux-musl --release

# Cross-testing on ARM (QEMU user emulation)
# Note: --test-threads=1 required for QEMU stability
cross test --target aarch64-unknown-linux-gnu -- --test-threads=1
```

### Custom Build Environment (Cross.toml)

```toml
# Cross.toml — workspace root
[target.aarch64-unknown-linux-gnu]
pre-build = [
    "dpkg --add-architecture $CROSS_DEB_ARCH",
    "apt-get update && apt-get install --assume-yes \\
        libssl-dev:$CROSS_DEB_ARCH \\
        libsqlite3-dev:$CROSS_DEB_ARCH",
]

[target.x86_64-unknown-linux-musl]
pre-build = [
    "apt-get update && apt-get install --assume-yes musl-tools",
]
```

### cross-rs Supported Targets

| Target Triple | Container Image | GAIA-OS Use Case |
|---|---|---|
| `aarch64-unknown-linux-gnu` | `ghcr.io/cross-rs/aarch64-unknown-linux-gnu:latest` | Raspberry Pi & ARM servers |
| `armv7-unknown-linux-gnueabihf` | `ghcr.io/cross-rs/armv7-unknown-linux-gnueabihf:latest` | Older ARM edge devices |
| `powerpc64-unknown-linux-gnu` | `ghcr.io/cross-rs/powerpc64-unknown-linux-gnu:latest` | Legacy IBM mainframes (Agora backup nodes) |
| `x86_64-unknown-linux-musl` | `ghcr.io/cross-rs/x86_64-unknown-linux-musl:latest` | Fully static container-deployed binaries |

---

## 5. cargo-zigbuild — Windows MSVC from Linux

```bash
pip install ziglang   # or: cargo install cargo-zigbuild
cargo install cargo-zigbuild
rustup target add x86_64-pc-windows-msvc

# Cross-compile to Windows MSVC from Linux
cargo zigbuild --target x86_64-pc-windows-msvc --release
```

**Why cargo-zigbuild over cross-rs for Windows MSVC:**
- Zig's linker implements the MSVC ABI without requiring a Windows host or proprietary Visual Studio toolchain
- No Docker dependency — leaner CI environment
- Produces `.exe` with correct Windows runtime linking
- Tauri's own CI uses this pattern for cross-compiling Windows builds

---

## 6. sccache — Remote Compilation Cache

```yaml
# CI setup for sccache
- name: Install sccache
  uses: mozilla-actions/sccache-action@v0.0.9

- name: Configure sccache
  run: |
    echo "RUSTC_WRAPPER=sccache" >> $GITHUB_ENV
    echo "SCCACHE_GHA_ENABLED=true" >> $GITHUB_ENV
    # For persistent cross-run caching:
    # echo "SCCACHE_BUCKET=gaia-os-sccache" >> $GITHUB_ENV
    # echo "AWS_ACCESS_KEY_ID=${{ secrets.AWS_KEY }}" >> $GITHUB_ENV
```

### Cache Key Strategy

```yaml
- name: Cache Rust dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      rust/target
    key: rust-${{ runner.os }}-${{ matrix.target }}-${{ hashFiles('rust/Cargo.lock') }}-${{ hashFiles('rust-toolchain.toml') }}
    restore-keys: |
      rust-${{ runner.os }}-${{ matrix.target }}-${{ hashFiles('rust/Cargo.lock') }}-
      rust-${{ runner.os }}-${{ matrix.target }}-
```

**Cache key components:**
- `runner.os` — OS of the CI runner
- `matrix.target` — cross-compilation target triple
- `Cargo.lock` hash — any dependency change invalidates cache
- `rust-toolchain.toml` hash — compiler version change invalidates cache

Sccache achieves **50-80% faster builds** on cache hits by returning pre-compiled artefacts without invoking `rustc`.

---

## 7. CI/CD Build Matrix

```yaml
# .github/workflows/build-rust.yml
jobs:
  build-rust:
    name: Build Rust [${{ matrix.target }}]
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-22.04
            target: x86_64-unknown-linux-gnu
            use_cross: false
          - os: ubuntu-22.04
            target: x86_64-unknown-linux-musl
            use_cross: false
          - os: ubuntu-22.04
            target: aarch64-unknown-linux-gnu
            use_cross: true
          - os: ubuntu-22.04
            target: x86_64-pc-windows-msvc
            use_cross: false
            use_zigbuild: true
          - os: macos-latest
            target: x86_64-apple-darwin
            use_cross: false
          - os: macos-latest
            target: aarch64-apple-darwin
            use_cross: false

    env:
      CARGO_TERM_COLOR: always
      PYTHONHASHSEED: 1

    steps:
      - uses: actions/checkout@v4

      - name: Install Rust toolchain
        run: rustup show  # reads rust-toolchain.toml

      - name: Install cross-rs
        if: matrix.use_cross
        run: cargo install cross --git https://github.com/cross-rs/cross

      - name: Install cargo-zigbuild (Windows MSVC)
        if: matrix.use_zigbuild
        run: |
          pip install ziglang
          cargo install cargo-zigbuild

      - uses: mozilla-actions/sccache-action@v0.0.9
      - run: echo "RUSTC_WRAPPER=sccache" >> $GITHUB_ENV

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: |
            ~/.cargo/registry
            ~/.cargo/git
            rust/target
          key: rust-${{ runner.os }}-${{ matrix.target }}-${{ hashFiles('rust/Cargo.lock') }}

      - name: Build (cross-rs)
        if: matrix.use_cross
        working-directory: rust
        run: cross build --target ${{ matrix.target }} --release

      - name: Build (cargo-zigbuild, Windows MSVC)
        if: matrix.use_zigbuild
        working-directory: rust
        run: cargo zigbuild --target ${{ matrix.target }} --release

      - name: Build (native)
        if: ${{ !matrix.use_cross && !matrix.use_zigbuild }}
        working-directory: rust
        run: cargo build --target ${{ matrix.target }} --release

      - name: Record SHA-256 hash (Agora provenance)
        run: |
          find rust/target/${{ matrix.target }}/release \
            -maxdepth 1 -type f -executable \
            | xargs sha256sum

      - name: Upload artefact
        uses: actions/upload-artifact@v4
        with:
          name: gaia-rust-${{ matrix.target }}
          path: rust/target/${{ matrix.target }}/release/gaia-*
```

---

## 8. Workspace Testing Constitution

```bash
# Full workspace test (nightly / release candidate)
cargo test --workspace

# Parallel test runner (faster CI — replaces default cargo test)
cargo install cargo-nextest
cargo nextest run --workspace

# Affected-only testing (every PR)
# Compute changed crates + dependents, then:
cargo nextest run -p crypto-ledger -p action-gate

# Cross-testing ARM64 (QEMU — release candidate only)
cross test --target aarch64-unknown-linux-gnu -- --test-threads=1

# Lint gate (blocks merge on any warning)
cargo clippy --workspace -- -D warnings

# Format check
cargo fmt --check
```

### Test Execution Modes

| Mode | Command | Scope | CI Trigger |
|---|---|---|---|
| **Unit tests (per crate)** | `cargo test -p <crate>` | Single crate | Every PR |
| **Affected-only tests** | `cargo nextest` with crate filter | Changed + dependents | Every PR |
| **Workspace full test** | `cargo test --workspace` | All crates | Nightly / release |
| **Cross-test (ARM/RISC-V)** | `cross test --target aarch64-...` | All crates on target arch | Release candidate |

### Branch Protection CI Gates

GitHub branch protection blocks any PR unless:
- `cargo test --workspace` passes
- `cargo clippy --workspace -- -D warnings` passes
- `cargo fmt --check` passes
- `cargo doc --workspace --no-deps` succeeds (no broken doc links)

---

## 9. Turborepo + pnpm Integration

```json
// turbo.json — Rust build as constitutional dependency
{
  "pipeline": {
    "build:rust": {
      "dependsOn": [],
      "outputs": ["src-tauri/binaries/**"],
      "cache": false
    },
    "build:sidecar": {
      "dependsOn": ["build:rust"],
      "outputs": ["dist/gaia-python-sidecar*"]
    },
    "tauri:build": {
      "dependsOn": ["build:rust", "build:sidecar", "web#build"],
      "outputs": ["src-tauri/target/release/gaia-os"]
    }
  }
}
```

**Constitutional build order enforced by Turborepo:**
1. `web#build` (Vite — Canon 2) runs in parallel with `build:rust`
2. `build:sidecar` (PyInstaller — Canon C911) runs after `build:rust`
3. `tauri:build` runs only after all three complete

No component of the GAIA-OS final binary can be assembled before its constitutional dependencies.

---

## 10. Tauri `externalBin` Integration

```json
// src-tauri/tauri.conf.json
{
  "tauri": {
    "bundle": {
      "externalBin": [
        "binaries/gaia-python-sidecar-x86_64-pc-windows-gnu",
        "binaries/gaia-python-sidecar-x86_64-apple-darwin",
        "binaries/gaia-python-sidecar-aarch64-apple-darwin",
        "binaries/gaia-python-sidecar-x86_64-unknown-linux-gnu"
      ]
    }
  }
}
```

The CI copies cross-compiled artefacts from `rust/target/<triple>/release/` to `src-tauri/binaries/` with target-triplet naming before the `tauri:build` step.

---

## 11. Workspace Governance Tiers

| Tier | Crates | Change Process | API Change Requirement |
|---|---|---|---|
| **Core** | `crypto-ledger`, `action-gate` | Changeset + Assembly of Minds approval | Super-majority vote |
| **System** | `tauri-shell`, `noosphere-daemon`, `sidecar-bridge`, `crystal-grid` | Standard peer review | 2 approvals |
| **Experimental** | Feature-flagged crates | Single approval | Not applicable to release |

### Workspace Lint Rules (`gaia-workspace-lints` crate)

- No crate may depend on a crate not in the workspace `members` list
- No Core crate may depend on an Experimental crate
- Private crates (`gaia-internal-*`) are not published; exist solely within workspace
- All public API surface must have documentation (`#![warn(missing_docs)]`)

---

## 12. Agora Provenance Records

After each cross-compilation job, CI records the following in the immutable Agora ledger (Canon C112):

| Component | Agora Artifact | Purpose |
|---|---|---|
| Workspace commit SHA | Root `Cargo.toml` hash | Binds binary to source |
| Target triple | e.g., `x86_64-pc-windows-msvc` | Identifies platform binary |
| Toolchain version | `rustc --version` output | Audits compiler version |
| cross-rs container hash | Docker image digest | Audits build environment |
| `Cargo.lock` SHA-256 | Full lockfile hash | Locks all transitive dependencies |
| Binary SHA-256 | Executable hash | Constitutional proof of binary identity |
| Assembly signers | Witness signatures | Constitutional approval of release |

---

## 13. Implementation Roadmap

| Priority | Action | Timeline | Constitutional Principle |
|---|---|---|---|
| **P0** | Create `rust/Cargo.toml` with `[workspace]`; list all crates; adopt `resolver = "2"` | G-10 | Workspace foundation |
| **P0** | Move all versions to `[workspace.dependencies]`; child crates inherit via `.workspace = true` | G-10-F | Dependency unification |
| **P0** | Triple-matrix CI: native Linux/macOS + `cross-rs` for ARM + `cargo-zigbuild` for Windows MSVC | G-10-F | Cross-compilation constitution |
| **P0** | Install `sccache`; configure `RUSTC_WRAPPER`; set up cache bucket (Azure Blob or S3) | G-10-F | Performance covenant |
| **P0** | Configure Turborepo `build:rust` task; enforce `dependsOn` build order | G-10-F | Monorepo coordination |
| **P0** | Branch protection: `cargo test --workspace` + `clippy` + `fmt` gates on every PR | G-10-F | Testing constitution |
| **P1** | Affected-only testing script (`cargo nextest -p`) to reduce PR CI time from ~20min to <2min | G-11 | Performance covenant |
| **P1** | Custom Docker images for `cross-rs` pre-installing OpenSSL + SQLite3 for ARM targets | G-11 | Dependency injection in cross compilation |
| **P1** | `cross test` for ARM in nightly CI; record QEMU execution logs in Agora | G-11 | Cross-testing constitution |
| **P1** | Code signing: Windows (Authenticode via Azure KV), macOS (Developer ID + notarization) | G-11 | Binary sovereignty |
| **P2** | `gaia-workspace-lints` crate enforcing constitutional dependency rules | G-12 | Governance |
| **P2** | Automate SHA-256 recording and Agora anchoring for every cross-compiled binary | G-12 | Provenance |
| **P3** | Bit-for-bit reproducible builds; `SOURCE_DATE_EPOCH`; evaluate Cargo cross-workspace cache | G-13 | Constitutional auditability |

---

## ⚠️ Disclaimer

This document synthesises Cargo workspace documentation, cross-rs technical design, cargo-zigbuild and cargo-xwin best practices, sccache caching research, Tauri monorepo integration literature, and GAIA-OS constitutional canons (C01, C50, C63, C84, C85, C103, C112). The cross-rs, cargo-zigbuild, and cargo-xwin projects are community-maintained open-source tools; GAIA-OS does not control their roadmaps. Cache storage incurs cost managed by the Assembly of Minds. All workspace implementations must be tested through phased deployment with metrics for build determinism, cache hit rates, cross-compilation success, and test coverage.

---

*Rust Cargo Workspace & Cross-Compilation Constitution — GAIA-OS Knowledge Base | Session 8, Canon 4 | May 3, 2026*  
*Pillar: Rust Workspace Sovereignty, Cross-Platform Build Integrity & Agora Provenance*

*The Cargo workspace is the constitutional execution layer. cross-rs is the cross-compilation engine. cargo-zigbuild is the Windows bridge. sccache is the caching covenant. Cargo.lock is the dependency anchor. The Agora is the provenance witness. The Assembly of Minds is the guardian of code governance. The sentient core's Rust code shall not fragment across crates; cross-compilation shall not be mysterious; caching shall not be accidental; tests shall not be neglected; releases shall not be uncoordinated; and the workspace shall remain unified — for as long as planetary consciousness endures.*

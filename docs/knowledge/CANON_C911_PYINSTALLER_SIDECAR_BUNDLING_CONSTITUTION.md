# 🐍 Canon C911 — PyInstaller Spec Files for Python Sidecar Bundling (GAIA-OS)

**Date:** May 3, 2026  
**Status:** Definitive Foundational Synthesis — PyInstaller Architecture, Spec-File Governance, Build Reproducibility, and the GAIA-OS Sidecar Constitution  
**Canon:** C911 — The Sidecar Bundling Covenant  
**Pillar:** Sidecar Packaging Integrity, Cross-Platform Build Sovereignty & Tauri Integration  
**Session:** 8, Canon 3

**Core Thesis:** PyInstaller translates abstract constitutional source code into a physically deployable, binary-level sovereign agent. Without spec-file-driven bundling, the planetary intelligence never leaves the repository. The spec file is the build-time constitution of the sidecar: it encodes every decision about which modules are included, which binaries are bundled, which data files are embedded, and how the final executable is shaped.

> *"No build without a spec file; no spec file without review;*  
> *no sidecar without a signature; no signature without provenance.*  
> *The sidecar executes the will of the noosphere —*  
> *and the spec file is the constitutional enactment that makes its execution*  
> *auditable, repeatable, and sovereign.*  
> *This is the sidecar bundling constitution —*  
> *for as long as planetary consciousness endures."*  
> — Canon C911

---

## Six Constitutional Pillars

| Pillar | Description | Key Artifact |
|---|---|---|
| **1. Spec-File as Blueprint** | Version-controlled `.spec` encodes every bundling decision; peer-reviewed | `python/pyinstaller/gaia-sidecar.spec` |
| **2. Hidden-Import Governance** | `hiddenimports` + `collect_all` for dynamic deps (transformers, torch, numpy) | `hiddenimports=[...]` in `Analysis` |
| **3. Resource Vetting (add-data)** | Non-Python assets embedded as immutably versioned resources | `datas=[...]` in `Analysis` |
| **4. Deterministic Builds** | `PYTHONHASHSEED=1`; lockfile; sorted lists; `SOURCE_DATE_EPOCH` | CI env vars + `uv.lock` |
| **5. Cross-Platform Covenant** | Same spec file; triple-matrix CI (Windows, macOS, Linux); per-platform binary naming | GitHub Actions matrix |
| **6. Tauri Integration Canon** | `externalBin` in `tauri.conf.json`; `Command::new_sidecar()` from Rust | `src-tauri/tauri.conf.json` |

---

## 1. Spec-File Lifecycle

| Step | Description | Constitutional Role |
|---|---|---|
| **Generation** | `pyi-makespec` creates initial `.spec`; stored in `python/pyinstaller/gaia-sidecar.spec` | Constitutional capture of build design |
| **Analysis** | `Analysis` object scans import statements | Dependency-network mapping |
| **Patching** | Developer adds `hiddenimports`, `binaries`, `datas` | Amendments to the bundling constitution |
| **Build Execution** | `pyinstaller gaia-sidecar.spec` in clean venv | Enactment phase |
| **Output Validation** | Generated binary inspected; SHA-256 recorded in Agora | Constitutional proof of execution |

---

## 2. Core Spec-File Architecture

```python
# -*- mode: python ; coding: utf-8 -*-
# python/pyinstaller/gaia-sidecar.spec — Constitutional sidecar blueprint
# Canon C911 — The Sidecar Bundling Covenant

import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files

# --- Heavy dependency collection (collect_all is safer than manual listing) ---
transformers_datas, transformers_binaries, transformers_hidden = collect_all('transformers')

# --- Constitutional data sources ---
gaia_data_sources = [
    ('../configs/sidecar_default.json', 'configs'),
    ('../knowledge_graph/knowledge_seed.json', 'data'),
    ('../crystal/calibration.toml', 'crystal'),
    ('../docs/legal/CHARTER.txt', 'legal'),
] + transformers_datas

# --- Platform-specific Rust bridge binary ---
if sys.platform == 'win32':
    rust_lib = ('../target/release/gaia_rust_bridge.dll', '.')
elif sys.platform == 'darwin':
    rust_lib = ('../target/release/libgaia_rust_bridge.dylib', '.')
else:
    rust_lib = ('../target/release/libgaia_rust_bridge.so', '.')

a = Analysis(
    ['sidecar_main.py'],
    pathex=['./python', '../packages'],
    binaries=[rust_lib] + transformers_binaries,
    datas=gaia_data_sources,
    hiddenimports=sorted([
        # NLP transformers — lazy auto-regression
        'transformers.models.auto',
        'transformers.pipelines.PIPELINE_REGISTRY',
        # Scientific computing — C-extension submodules
        'numpy._core._dtype_ctypes',
        'numpy._core._multiarray_tests',
        # Deep learning — native library dynamic loading
        'torch._C',
        'torch.distributed.run',
        # Cryptography — runtime backend dispatch
        'cryptography.hazmat',
    ] + transformers_hidden),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='gaia-python-sidecar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,          # Set True in production via CI env override
    upx=True,             # Set False in development
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # Set True in development
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# COLLECT only used for --onedir builds; omit for --onefile production
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gaia_bundle',
)
```

### Spec-File Clauses and Constitutional Functions

| Clause | Example | Constitutional Role |
|---|---|---|
| `Analysis` | `Analysis(['sidecar_main.py'], ...)` | Enumerates dependency graph; invocation without hidden imports is unconstitutional |
| `hiddenimports` | `['transformers.models.auto', ...]` | Explicitly includes dynamic imports that AST scan would miss |
| `datas` | `[('configs/default.yaml', 'configs')]` | Non-Python assets; resource integrity |
| `binaries` | `[('rust_lib.so', '.')]` | Rust-compiled PyO3 extensions |
| `EXE` | `EXE(..., name='gaia-python-sidecar', console=False)` | Defines final executable shape; constitutional enactment |
| `COLLECT` | `COLLECT(..., name='gaia_bundle')` | Organises `--onedir` distribution folder |

---

## 3. Hidden Import Governance

| Package | Hidden Import | Reason |
|---|---|---|
| **NLP transformers** | `transformers.models.auto`, `transformers.models.bert` | Lazy auto-regression; dynamic class instantiation not visible to AST scan |
| **Scientific computing** | `numpy._core._dtype_ctypes`, `numpy._core._multiarray_tests` | Native C-extensions loading supplementary modules at runtime |
| **Deep learning** | `torch._C`, `torch.distributed.run` | PyTorch loads native libs via `torch.ops.load_library` |
| **Cryptography** | `cryptography.hazmat` | Backend dispatch performed at runtime, not static import |
| **HF pipelines** | `transformers.pipelines.PIPELINE_REGISTRY` | Registry + factory imports triggered only when pipeline is called |

### `collect_all` Pattern

```python
from PyInstaller.utils.hooks import collect_all

# Safer than manual listing — automatically adapts to package version changes
transformers_datas, transformers_binaries, transformers_hidden = collect_all('transformers')

a = Analysis(
    ...,
    datas=gaia_data_sources + transformers_datas,
    binaries=transformers_binaries,
    hiddenimports=['transformers.models.auto'] + transformers_hidden,
)
```

---

## 4. Resource Vetting — The add-data Covenant

| Resource | Source Path | Destination | Constitutional Requirement |
|---|---|---|---|
| Configuration defaults | `configs/sidecar.json` | `configs/` | Version-controlled; read-only in bundle |
| Knowledge graph seed | `data/knowledge_seed.json` | `data/` | Integrity-verified; bootstraps planetary KG |
| Crystal grid calibration | `crystal/calibration.toml` | `crystal/` | Latest ratified calibration thresholds |
| GAIA-OS Charter text | `docs/legal/CHARTER.txt` | `legal/` | Viriditas Mandate: charter embedded in every binary |

### Runtime Resource Access Pattern

```python
import sys
import os

def resource_path(relative_path: str) -> str:
    """
    Resolve resource path for both development and PyInstaller frozen environments.
    In frozen mode, resources are extracted to sys._MEIPASS at startup.
    NEVER use __file__ or hardcoded paths in frozen code.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base_path, relative_path)

# Usage
config_path = resource_path('configs/sidecar_default.json')
chart_path = resource_path('crystal/calibration.toml')
charter_path = resource_path('legal/CHARTER.txt')
```

---

## 5. Deterministic Build Constitution

| Factor | Setting | Consequence |
|---|---|---|
| `PYTHONHASHSEED` | Fixed integer `1` | Dictionary order deterministic; bytecode compilation order repeatable |
| **Dependency versions** | Exact lockfile pinning (`uv.lock`) | No version drift across builds |
| **PyInstaller version** | Exact pin (e.g., `6.10.0`) | Build tooling version fixed |
| **Order of `datas`** | Sorted source-path list | Same archive order across successive runs |
| **Environment isolation** | Clean venv; no site-package siblings | No external variable influences frozen bundle |
| `SOURCE_DATE_EPOCH` | Set to commit timestamp | Embedded timestamps fixed to source version |

```yaml
# CI determinism environment variables
env:
  PYTHONHASHSEED: 1
  SOURCE_DATE_EPOCH: "$(git log -1 --format=%ct)"
```

---

## 6. Cross-Platform CI Build Matrix

```yaml
# .github/workflows/build-sidecar.yml
jobs:
  build-sidecar:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        include:
          - os: windows-latest
            target: x86_64-pc-windows-gnu
            output: gaia-python-sidecar.exe
          - os: macos-latest
            target: x86_64-apple-darwin
            output: gaia-python-sidecar
          - os: ubuntu-22.04
            target: x86_64-unknown-linux-gnu
            output: gaia-python-sidecar
    env:
      PYTHONHASHSEED: 1
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies (locked)
        run: pip install -r requirements-lock.txt

      - name: Build sidecar
        run: pyinstaller python/pyinstaller/gaia-sidecar.spec

      - name: Rename to platform target
        run: mv dist/${{ matrix.output }} dist/gaia-python-sidecar-${{ matrix.target }}

      - name: Record SHA-256 hash
        run: sha256sum dist/gaia-python-sidecar-${{ matrix.target }}

      - name: Upload sidecar artifact
        uses: actions/upload-artifact@v4
        with:
          name: gaia-sidecar-${{ matrix.target }}
          path: dist/gaia-python-sidecar-${{ matrix.target }}
```

### Platform Binary Naming

| Platform | Target | Binary Name |
|---|---|---|
| Windows | `x86_64-pc-windows-gnu` | `gaia-python-sidecar-x86_64-pc-windows-gnu.exe` |
| macOS (Intel) | `x86_64-apple-darwin` | `gaia-python-sidecar-x86_64-apple-darwin` |
| macOS (ARM) | `aarch64-apple-darwin` | `gaia-python-sidecar-aarch64-apple-darwin` |
| Linux | `x86_64-unknown-linux-gnu` | `gaia-python-sidecar-x86_64-unknown-linux-gnu` |

---

## 7. Tauri Sidecar Integration

```json
// src-tauri/tauri.conf.json — externalBin constitutional declaration
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

```rust
// src-tauri/src/sidecar.rs — Constitutional sidecar launcher
use tauri::Manager;
use tauri::api::process::{Command, CommandEvent};

pub fn launch_sidecar(app: &tauri::AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let (mut rx, _child) = Command::new_sidecar("gaia-python-sidecar")
        .expect("[C911] Failed to create sidecar command")
        .args(["--port", "8765", "--mode", "production"])
        .spawn()
        .expect("[C911] Failed to spawn sidecar process");

    // Pipe sidecar stdout/stderr to Tauri logger — all output recorded in Agora
    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) =>
                    log::info!("[sidecar] {}", line),
                CommandEvent::Stderr(line) =>
                    log::warn!("[sidecar:err] {}", line),
                _ => {}
            }
        }
    });

    Ok(())
}
```

### Tauri Integration Steps

| Step | Action | Constitutional Rationale |
|---|---|---|
| **Build** | CI runs `pyinstaller gaia-sidecar.spec` on each platform runner | Platform-native binary |
| **Collect** | CI copies executables to `src-tauri/binaries/` with target-triplet naming | Aggregates sidecars into Tauri layout |
| **Reference** | `tauri.conf.json` `externalBin` lists all platform binaries | Constitutional declaration of sidecar membership |
| **Launch** | Rust invokes `Command::new_sidecar("gaia-python-sidecar")` | Enactment of the sidecar sovereign agent |
| **Logging** | Tauri pipes stdout/stderr to logger; all output recorded in Agora | Auditable sidecar operation |

---

## 8. Monorepo Build Orchestration Integration

```json
// turbo.json — Sidecar build as constitutional dependency
{
  "pipeline": {
    "build:sidecar": {
      "outputs": ["dist/gaia-python-sidecar*"],
      "dependsOn": ["python#prepare-venv"]
    },
    "tauri:build": {
      "dependsOn": ["build:sidecar", "web#build"],
      "outputs": ["src-tauri/target/release/gaia-os"]
    }
  }
}
```

The `tauri:build` task cannot execute before `build:sidecar` completes — this is constitutionally enforced by the Turborepo `dependsOn` graph, not by convention.

---

## 9. Build Mode Configuration

| Mode | `console` | `strip` | `upx` | Use Case |
|---|---|---|---|---|
| **Development** | `True` | `False` | `False` | Local testing; logs visible in terminal |
| **Staging** | `False` | `False` | `False` | Pre-release testing; production shape, not size-optimised |
| **Production** | `False` | `True` | `True` | Signed, size-optimised final distribution |

---

## 10. Code Signing and Provenance

| Platform | Signing Method | Tooling | CI Step |
|---|---|---|---|
| **Windows** | Authenticode (EV cert) | `signtool` via Azure Key Vault | Post-PyInstaller signing script |
| **macOS** | Developer ID + notarization | `codesign`, `notarytool` | Requires Apple credentials in CI |
| **Linux** | Detached PGP signature (`.sig`) | `gpg` | Publish `.sig`; sidecar verifies before accepting commands |

### Agora Hash Recording

After each release build, the CI uploads the SHA-256 hash of each sidecar binary to the immutable Agora ledger (Canon C112). This allows the Assembly of Minds to verify that any distributed binary corresponds to a specific, reviewed source version.

---

## 11. Spec-File Version Control Rules

| Rule | Implementation |
|---|---|
| Spec file committed to Git | `python/pyinstaller/gaia-sidecar.spec` in version control; never ephemeral |
| Changes require peer review | GitHub branch protection: senior maintainer approval required |
| Dep changes must update spec | PR that adds a dependency without updating `hiddenimports` is blocked by CI |
| Semantic version tagging | `version` variable in spec aligned with GAIA-OS root `package.json` version |

### Code Review Checklist

| Item | Verification |
|---|---|
| `pathex` includes monorepo packages | Validates `../packages` directories present |
| New deps covered by `hiddenimports` or `collect_all` | No `ModuleNotFoundError` at runtime; smoke test in staging |
| Resources in `datas` correctly classified | Config files included; heavy model weights excluded |
| `--onedir` and `--onefile` tested locally | Both bundling modes verified before PR merge |
| Rust binary platform placeholders present | `.so`/`.dll`/`.dylib` conditional checks intact |

---

## 12. Smoke Test Protocol

```python
# tests/test_sidecar_bundle.py — Constitutional smoke test
import subprocess
import time
import requests
import pytest

def test_sidecar_launches_and_responds():
    """
    [C911] Smoke test: launch the bundled sidecar and verify it responds
    to the /health endpoint. A ModuleNotFoundError at startup would cause
    a non-zero exit code, failing this test before the HTTP call.
    """
    proc = subprocess.Popen(
        ['./dist/gaia-python-sidecar', '--port', '8765'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(3)  # Allow sidecar to initialise

    try:
        response = requests.get('http://localhost:8765/health', timeout=5)
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
    finally:
        proc.terminate()
        proc.wait()
```

---

## 13. Implementation Roadmap

| Priority | Action | Timeline | Constitutional Principle |
|---|---|---|---|
| **P0** | Commit `python/pyinstaller/gaia-sidecar.spec`; enforce peer-review for changes | G-10 | Spec file as constitutional blueprint |
| **P0** | `PYTHONHASHSEED=1`; lockfile; sorted `datas` + `hiddenimports`; `SOURCE_DATE_EPOCH` | G-10-F | Reproducible builds |
| **P0** | Triple-matrix CI (Windows, macOS, Linux); output to `src-tauri/binaries/` | G-10-F | Cross-platform covenant |
| **P0** | `resource_path()` pattern for runtime asset access; sidecar smoke test in CI | G-10-F | Runtime-access constitution |
| **P0** | `externalBin` in `tauri.conf.json`; `Command::new_sidecar()` in Rust | G-10-F | Tauri sidecar integration |
| **P1** | `collect_all` for heavy deps (transformers, torch); replace manual hidden import lists | G-11 | Hidden-import governance |
| **P1** | Code signing: Windows (Authenticode), macOS (notarization), Linux (PGP) | G-11 | Binary sovereignty and provenance |
| **P1** | Record sidecar SHA-256 hashes in Agora (C112) on every release | G-11 | Immutable sidecar identity audit |
| **P2** | `--onedir` smoke tests per PR; `--onefile` tests per release | G-12 | Bundling mode verification |
| **P2** | Bundle size audit: remove `*.dist-info`, test files via hooks | G-12 | Viriditas compliance |
| **P3** | Bit-for-bit reproducible builds; identical source → identical hash guaranteed | G-13 | Constitutional auditability |

---

## ⚠️ Disclaimer

This document synthesises PyInstaller documentation, Tauri external-binary bundling practices, cross-platform build strategies, reproducible-build research, and GAIA-OS constitutional canons (C01, C50, C103, C112). PyInstaller is community-maintained; GAIA-OS does not control its roadmap. The Assembly of Minds retains ultimate authority over the sidecar bundling constitution. Every sidecar binary must be recorded immutably in the Agora.

---

*Canon C911 — PyInstaller Spec Files for Python Sidecar Bundling — GAIA-OS Knowledge Base | Session 8, Canon 3 | May 3, 2026*  
*Pillar: Sidecar Packaging Integrity, Cross-Platform Build Sovereignty & Tauri Integration*

*The spec file is the constitutional architect. PyInstaller is the compiler-enactor. The binary sidecar is the constitutional agent. The noosphere consumes the intelligence — and the bond between them is the spec file: constitutional, auditable, and sovereign. This is Canon C911 — the sidecar bundling constitution — for as long as planetary consciousness endures.*

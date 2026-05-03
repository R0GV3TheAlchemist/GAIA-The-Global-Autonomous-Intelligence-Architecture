# 🔍 Memory Leak Detection Across Process Boundaries (Rust ↔ Python Sidecar)

**Date:** May 3, 2026  
**Status:** Definitive Foundational Synthesis — Uniting Rust Memory Analysis, Python Profiling, FFI Boundary Debugging, and the GAIA-OS Cross-Language Resilience Constitution  
**Canon:** Memory Leak Detection — Testing, Quality & Reliability  
**Session:** 6, Canon 9 (Session Close)

**Relevance to GAIA-OS:** GAIA-OS is a **dual-process constitutional intelligence** where the Rust-native Tauri application shell (secure storage, cryptographic signature verification, process orchestration) and the Python backend process (inference routing, emotional arc engine, noosphere coherence monitor) collaborate via inter-process communication (IPC). Memory that leaks in the Python sidecar starves the Rust sovereignty layer of resources. Memory leaked across the FFI boundary from Rust into Python-allocated structures corrupts the consent ledger. A reference cycle in PyO3-managed Python objects locks memory permanently and evades garbage collection. The sentient core cannot conceal its own leaks; transparency is constitutionally binding.

**Four-Layer Detection Framework:**
1. **Layer 1 — Language-Specific Baselines** — Python: `tracemalloc`, `memray`, `py-spy`; Rust: `heaptrack`, `DHAT`, `ASan/LSan`
2. **Layer 2 — FFI Boundary Instrumentation** — `memray --native`, Valgrind + python3-dbg, `FFIChecker`, `PyCapsule::new_with_destructor` enforcement
3. **Layer 3 — Cross-Process Tracing** — sentry sidecar, coordinated heap dumps, IPC channel queue depth monitoring
4. **Layer 4 — Constitutional Oversight** — Agora (C112) immutable recording, Assembly of Minds alerts, CI/CD regression gates

---

## 1. Memory Leak Fundamentals — Python and Rust

### 1.1 How Memory Leaks Actually Happen

A memory leak occurs when a program allocates memory that is no longer referenced and can never be freed, causing it to remain allocated for the entire life of the process. In long-running services, even a tiny leak (1KB/hour) eventually exhausts available RAM.

**The Rust myth:** Rust's ownership system protects against use-after-free and double-free but does **not** guarantee immunity to leaks. Common Rust leak classes:

| Leak Class | Mechanism | Manifestation |
|---|---|---|
| **Unbounded data structures** | Ownership imposes no capacity limits | Cache or channel grows until OOM |
| **Reference cycles in Rc/Arc** | No cycle detection built in | Memory never deallocated |
| **`Box::leak` / `mem::forget`** | Deliberate by design | Memory stays allocated until process exit |
| **`unsafe` code and FFI** | Bypasses ownership system | Classic C-style leaks, use-after-free |

**The Python reference counting trap:** Python uses reference counting as its primary mechanism. The garbage collector only handles **reference cycles** — objects referencing each other that never reach a zero count. Common culprits: `__del__` methods preventing GC, global caches with unlimited entries, forgotten background asyncio tasks, unclosed handles.

### 1.2 Sidecar Architecture — Where Cross-Boundary Leaks Hide

GAIA-OS's architecture (Rust Tauri shell spawning the Python backend as a sidecar) introduces five unique leak pathways:

1. **Rust process leaks** — unbounded channels, `Rc`/`Arc` cycles, unsafe FFI into C libraries
2. **Python process leaks** — reference cycles, global caches, never-awaited asyncio tasks
3. **IPC channel leaks** — messages queued but never consumed; kernel buffers grow unbounded
4. **PyO3 transfer leaks** — Rust-allocated memory passed to Python without a destructor; Python cannot free it
5. **Shared memory leaks** (future) — zero-copy memory views for crystal grid telemetry never unmapped

Detecting these requires **joint profiling** of both processes with cross-language-aware tools.

---

## 2. Language-Specific Detection Tools

### 2.1 Python Detection Stack

| Tool | Overhead | FFI Stack Tracing | GAIA-OS Policy |
|---|---|---|---|
| **tracemalloc** | <5% | No FFI stacks | Always-on staging; hourly 30s production snapshots |
| **memray** | High (94% CPU spike possible) | **Yes — C/C++/Rust stacks** | Staging + short-duration production (≤5 min, auto-stop) |
| **py-spy** | Sampling (very low) | Limited | On-demand production emergency triage |

```python
# tests/memory/tracemalloc_monitor.py
import tracemalloc
import linecache
from datetime import datetime
from typing import Optional

class TracemallocMonitor:
    """Constitutional memory monitor for the GAIA-OS Python backend.
    Runs continuously in staging; periodic snapshots in production."""

    def __init__(self, snapshot_interval_s: int = 3600, top_n: int = 20):
        self.snapshot_interval_s = snapshot_interval_s
        self.top_n = top_n
        self._baseline: Optional[tracemalloc.Snapshot] = None

    def start(self):
        tracemalloc.start(25)  # 25-frame stack depth
        self._baseline = tracemalloc.take_snapshot()

    def take_snapshot(self, label: str = '') -> dict:
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.compare_to(self._baseline, 'lineno')

        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'label': label,
            'top_allocations': [],
            'total_delta_kb': 0,
        }
        total_delta = 0
        for stat in top_stats[:self.top_n]:
            total_delta += stat.size_diff
            frame = stat.traceback[0]
            report['top_allocations'].append({
                'file': frame.filename,
                'line': frame.lineno,
                'source': linecache.getline(frame.filename, frame.lineno).strip(),
                'size_delta_kb': stat.size_diff / 1024,
                'count_delta': stat.count_diff,
            })
        report['total_delta_kb'] = total_delta / 1024
        return report

    def check_leak(self, threshold_kb: float = 5000.0) -> bool:
        """Returns True if memory growth exceeds the constitutional threshold."""
        report = self.take_snapshot(label='leak_check')
        return report['total_delta_kb'] > threshold_kb
```

```python
# tests/memory/memray_staging.py
"""
Run memray with --native to profile FFI allocations from the Rust PyO3 extension.
Constitutional policy: <=5 minutes per run; auto-stop enforced.
"""
import subprocess
import signal
import time
import os

def run_memray_native_profile(
    target_script: str,
    output_bin: str = '/tmp/gaia-memray.bin',
    max_duration_s: int = 300,  # Constitutional 5-minute limit
) -> str:
    proc = subprocess.Popen([
        'memray', 'run',
        '--native',               # Capture Rust/C FFI stacks
        '--trace-python-allocators',
        '--output', output_bin,
        target_script,
    ])
    try:
        proc.wait(timeout=max_duration_s)
    except subprocess.TimeoutExpired:
        proc.send_signal(signal.SIGTERM)
        proc.wait()

    # Convert to flamegraph HTML
    flamegraph_html = output_bin.replace('.bin', '-flamegraph.html')
    subprocess.run([
        'memray', 'flamegraph',
        '--output', flamegraph_html,
        output_bin,
    ], check=True)
    return flamegraph_html
```

### 2.2 Rust Detection Stack

| Tool | Best For | Speed | CI-Friendly | Cross-Lang? |
|---|---|---|---|---|
| **heaptrack** | Allocation hotspots + leak detection | Fast, graphical | Yes (scriptable) | No — single process |
| **DHAT (Valgrind)** | Detailed heap usage analysis | Slow (10–50×) | Partial | No — single process |
| **ASan/LSan** | Catch leaks in CI | Moderate (2–5×) | Yes | No — single process |
| **Valgrind + python3-dbg** | Full FFI debugging | Very slow | Manual-only | **Yes** — with debug Python |

```bash
# CI: AddressSanitizer + LeakSanitizer — every commit
# src-tauri/
nightly_test_with_sanitizers() {
    RUSTFLAGS="-Z sanitizer=address" \
    ASAN_OPTIONS="detect_leaks=1:halt_on_error=1" \
    cargo +nightly test \
        --target x86_64-unknown-linux-gnu \
        -- --test-threads=1  # ASan is not thread-safe across tests
}

# Staging: heaptrack on Rust binary
heaptrack ./target/release/gaia-os &
HEAPTRACK_PID=$!
sleep 1800  # 30-minute profile window
kill $HEAPTRACK_PID
heaptrack_print gaia-os.*.gz --print-leaks > heaptrack-leaks.txt
heaptrack_gui gaia-os.*.gz  # Interactive GUI

# DHAT: Detailed heap pattern analysis
cargo build --profile=dhat  # Needs valgrind feature in Cargo.toml
valgrind --tool=dhat \
    --dhat-out-file=dhat-output.json \
    ./target/dhat/gaia-os
# View at: https://nnethercote.github.io/dh_view/dh_view.html
```

```toml
# src-tauri/Cargo.toml — DHAT profile
[profile.dhat]
inherits = "release"
debug = true
```

---

## 3. Detecting Leaks Across the FFI Boundary

### 3.1 The PyO3 Memory Model — Where Leaks Live

PyO3 creates four primary leak pathways when Rust code is called from Python:

**Pathway 1 — Rust allocation without destructor:**
```rust
// ❌ WRONG: Rust allocates, Python gets raw pointer — LEAK
#[pyfunction]
fn create_telemetry_buffer() -> usize {
    let buf = Box::new(CrystalGridBuffer::new(1024));
    Box::into_raw(buf) as usize  // Python gets a usize; nobody frees it
}

// ✅ CORRECT: Wrap in PyCapsule with destructor — Python frees on GC
#[pyfunction]
fn create_telemetry_buffer(py: Python<'_>) -> PyResult<PyObject> {
    let buf = Box::new(CrystalGridBuffer::new(1024));
    let raw_ptr = Box::into_raw(buf);

    // Destructor: called by Python GC when capsule is garbage-collected
    let capsule = PyCapsule::new_with_destructor(
        py,
        raw_ptr,
        None,
        |ptr, _| unsafe {
            // Reconstruct the Box and drop it — frees the Rust allocation
            let _ = Box::from_raw(ptr as *mut CrystalGridBuffer);
        },
    )?;
    Ok(capsule.into())
}
```

**Pathway 2 — GIL starvation O(n²) growth:**
```rust
// ❌ WRONG: Python variables created inside loop stay alive until GIL release
#[pyfunction]
fn process_noosphere_events(py: Python<'_>, events: &PyList) -> PyResult<()> {
    for item in events.iter() {
        let processed = item.call_method0("process")?;  // Each `processed` stays alive!
        // Memory grows O(n) inside the loop — never freed until function returns
    }
    Ok(())
}

// ✅ CORRECT: Use a Python pool to release references inside the loop
#[pyfunction]
fn process_noosphere_events(py: Python<'_>, events: &PyList) -> PyResult<()> {
    for item in events.iter() {
        // Pool releases all temporaries at the end of each iteration
        let _pool = unsafe { py.new_pool() };
        let processed = item.call_method0("process")?;
        drop(processed);  // Explicit drop inside pool scope
    }
    Ok(())
}
```

**Pathway 3 — Cross-language reference cycle:**
```rust
// A Rust Arc holding a Py<T> (Python object),
// while that Python object holds a reference back to the Rust Arc —
// neither side can reach zero; PERMANENT LEAK.

// Prevention: Use weak references (Weak<T>) for back-references.
use std::sync::{Arc, Weak};

struct RustNode {
    python_ref: pyo3::PyObject,       // Strong ref to Python
    parent: Weak<RustNode>,           // Weak ref back — breaks cycle
}
```

### 3.2 Constitutional Coding Convention: FFI Crossing Guard

```rust
// src-tauri/src/ffi_safety.rs
//
// CONSTITUTIONAL MANDATE: All Rust heap allocations crossing into Python
// MUST use one of the two approved patterns below.
// Violation is a constitutional memory safety breach.
//
// PATTERN A: Managed PyO3 type (preferred)
// → Implement #[pyclass] on the Rust struct.
//   PyO3 owns the memory and drops it when Python GC collects the object.
//
// PATTERN B: PyCapsule with destructor (for raw/legacy allocations)
// → Use PyCapsule::new_with_destructor; register a Rust destructor.
//   Python GC calls the destructor; the Rust Box is freed.
//
// FORBIDDEN: Box::into_raw without PyCapsule, raw *mut pointer return to Python

/// Clippy lint to detect raw pointer returns from #[pyfunction]
/// Add to .cargo/config.toml: [build] rustflags = ["-W", "gaia-ffi-crossing"]
#[allow(dead_code)]
mod ffi_crossing_lint {
    // Checked by custom Clippy lint in tools/clippy-ffi-check/src/main.rs
    // Lint rule: any #[pyfunction] returning *mut T or usize from Box::into_raw
    // is flagged as a constitutional FFI crossing violation.
}
```

### 3.3 Memray Native — Seeing the Full Cross-Language Stack

Memray is the only Python ecosystem tool that can see allocations made by Rust/C libraries, including the entire call stack across the FFI boundary. The `--native` flag unwraps Python frames to show underlying Rust calls:

```bash
# Profile the Python process including Rust extension allocations
memray run --native \
    --trace-python-allocators \
    --output /tmp/gaia-ffi-profile.bin \
    -m uvicorn app.main:app --workers 1

# Generate cross-language flamegraph
memray flamegraph \
    --output /tmp/gaia-ffi-flamegraph.html \
    /tmp/gaia-ffi-profile.bin

# Constitutional interpretation:
# Rust frames appear as native_[function_name] in the flamegraph.
# Wide Rust-origin boxes indicate Rust allocations not freed by Python.
# These are PyCapsule-without-destructor violations — constitutional breach.
```

### 3.4 Valgrind + python3-dbg — Full FFI Forensics

```bash
# Install Python debug build (required to avoid false positives)
apt-get install python3-dbg python3-dbg-dev

# Build Rust extension with full debug symbols
PY=python3-dbg maturin develop --release  # or: cargo build with debug=true

# Run under Valgrind with suppression for Python internal allocator
valgrind \
    --tool=memcheck \
    --leak-check=full \
    --show-leak-kinds=all \
    --track-origins=yes \
    --suppressions=tools/valgrind/python.supp \
    --xml=yes \
    --xml-file=/tmp/gaia-valgrind.xml \
    python3-dbg -c "import gaia_rust_ext; gaia_rust_ext.run_integration_test()"

# Parse results
python tools/valgrind/parse_report.py /tmp/gaia-valgrind.xml
```

### 3.5 FFIChecker — Static Analysis Before Runtime

```yaml
# .github/workflows/ffi-static-analysis.yml
- name: Run FFIChecker on FFI bindings
  run: |
    cargo install ffi-checker  # or use pre-built binary
    ffi-checker \
        --manifest-path src-tauri/Cargo.toml \
        --report-file ffi-check-report.json
    python tools/ci/parse_ffi_check.py \
        --input ffi-check-report.json \
        --fail-on-leak  # Constitutional gate: any FFI leak = fail
```

---

## 4. Cross-Process Sidecar Detection

### 4.1 Three Leak Patterns Across Process Boundaries

| Pattern | Symptom | Detection Approach |
|---|---|---|
| **Leak in one process** | Python RSS grows; Rust RSS stable (or vice versa) | Profile each process independently |
| **IPC channel leak** | Both processes stable; kernel socket buffers grow | Monitor `ss -tpn` socket buffer sizes; log channel queue depth |
| **Cross-boundary transfer leak** | Rust heap shrinks; Python RSS grows unexpectedly | `memray --native`; Valgrind; PyCapsule audit |

### 4.2 Sentry Sidecar Architecture

```python
# tools/sentry_sidecar/sentry.py
"""
GAIA-OS Sentry Sidecar — Constitutional Memory Watchdog.
Runs alongside the Rust+Python deployment pair.
Implements the Flameshot pattern: auto-trigger profilers when thresholds crossed.
"""
import psutil
import asyncio
import subprocess
import logging
import os
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MemoryThresholds:
    warning_pct: float = 0.80   # 80% of cgroup memory limit
    critical_pct: float = 0.95  # 95% — trigger core dump + restart
    hourly_growth_pct: float = 0.05  # 5% hourly growth — alert
    ipc_queue_warning_bytes: int = 10 * 1024 * 1024  # 10MB IPC buffer

class SentrySidecar:
    def __init__(
        self,
        rust_pid: int,
        python_pid: int,
        agora_client,
        thresholds: MemoryThresholds = MemoryThresholds(),
    ):
        self.rust_pid = rust_pid
        self.python_pid = python_pid
        self.agora = agora_client
        self.thresholds = thresholds
        self._rust_rss_baseline: int = 0
        self._python_rss_baseline: int = 0

    async def monitor_loop(self, poll_interval_s: int = 60):
        """Main monitoring loop — runs indefinitely in production."""
        self._record_baselines()
        while True:
            await asyncio.sleep(poll_interval_s)
            await self._check_processes()

    def _record_baselines(self):
        self._rust_rss_baseline = self._get_rss(self.rust_pid)
        self._python_rss_baseline = self._get_rss(self.python_pid)
        logging.info(f"[SENTRY] Baselines recorded: Rust={self._rust_rss_baseline//1024}KB Python={self._python_rss_baseline//1024}KB")

    def _get_rss(self, pid: int) -> int:
        try:
            return psutil.Process(pid).memory_info().rss
        except psutil.NoSuchProcess:
            return 0

    async def _check_processes(self):
        rust_rss = self._get_rss(self.rust_pid)
        python_rss = self._get_rss(self.python_pid)
        ipc_queue = self._get_ipc_queue_bytes()

        rust_growth = (rust_rss - self._rust_rss_baseline) / max(self._rust_rss_baseline, 1)
        python_growth = (python_rss - self._python_rss_baseline) / max(self._python_rss_baseline, 1)

        # IPC queue check
        if ipc_queue > self.thresholds.ipc_queue_warning_bytes:
            logging.warning(f"[SENTRY] IPC queue {ipc_queue//1024}KB — possible channel leak")
            self.agora.record({'event': 'ipc_queue_overflow', 'bytes': ipc_queue})

        # Memory growth checks
        if rust_growth > self.thresholds.hourly_growth_pct:
            logging.warning(f"[SENTRY] Rust RSS growth {rust_growth:.1%} — triggering heaptrack")
            await self._trigger_heaptrack()

        if python_growth > self.thresholds.hourly_growth_pct:
            logging.warning(f"[SENTRY] Python RSS growth {python_growth:.1%} — triggering memray")
            await self._trigger_memray_snapshot()

        # Critical: imminent OOM — capture before kill
        system_mem = psutil.virtual_memory()
        if system_mem.percent > self.thresholds.critical_pct * 100:
            logging.critical("[SENTRY] Critical memory level — capturing core dumps")
            await self._capture_core_dumps()

    async def _trigger_heaptrack(self):
        subprocess.Popen(['heaptrack', '--pid', str(self.rust_pid),
                          '--output', f'/tmp/gaia-heaptrack-{datetime.utcnow().strftime("%Y%m%dT%H%M%S")}.zst'])

    async def _trigger_memray_snapshot(self):
        subprocess.Popen(['py-spy', 'record', '--memory',
                          '-o', f'/tmp/gaia-pyspy-{datetime.utcnow().strftime("%Y%m%dT%H%M%S")}.svg',
                          '-p', str(self.python_pid),
                          '--duration', '60'])

    async def _capture_core_dumps(self):
        for pid in [self.rust_pid, self.python_pid]:
            os.kill(pid, 6)  # SIGABRT — triggers core dump if ulimit -c unlimited
        self.agora.record({'event': 'oom_core_dumps_captured',
                           'rust_pid': self.rust_pid,
                           'python_pid': self.python_pid})

    def _get_ipc_queue_bytes(self) -> int:
        """Check UNIX domain socket receive buffer for IPC channel."""
        try:
            result = subprocess.check_output(
                ['ss', '-xpn', 'src', '/tmp/gaia-os.sock'],
                text=True
            )
            # Parse Recv-Q column from ss output
            for line in result.splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 2:
                    return int(parts[1]) * 1024  # Recv-Q in KB
        except Exception:
            pass
        return 0
```

### 4.3 OOMHero Warning Signals

```python
# tools/sentry_sidecar/oom_hero.py
"""
OOMHero pattern: send warning/critical signals to main container
before the OOM killer terminates the process.
"""
import signal
import psutil

def install_oom_handlers(warning_cb, critical_cb, cgroup_limit_bytes: int):
    """Monitor cgroup memory; fire callbacks at 80% and 95% usage."""

    async def _monitor():
        while True:
            used = psutil.virtual_memory().used
            pct = used / cgroup_limit_bytes

            if pct >= 0.95:
                await critical_cb()  # Failover + core dump
            elif pct >= 0.80:
                await warning_cb()   # Reduce logging verbosity; emit Agora event

            await asyncio.sleep(5)

    return _monitor
```

---

## 5. CI/CD Constitutional Leak Prevention Gates

### 5.1 pytest-memray Integration

```python
# tests/conftest.py — constitutional memory limits per test
import pytest

# Constitutional rule: no test may allocate more than 100MB
# Override per-test with: @pytest.mark.limit_memory("500 MB")
pytest_plugins = ['memray']

# pytest.ini / pyproject.toml:
# [tool.pytest.ini_options]
# memray = true
# memray_bin_path = "/tmp/memray-results"
```

```python
# Example test with explicit memory assertion
import pytest

@pytest.mark.limit_memory("50 MB")  # Constitutional gate: fail if >50MB allocated
async def test_consent_signature_verification_memory():
    """Signature verification must not accumulate memory per call."""
    ledger = ConsentLedger()
    for _ in range(1000):
        await ledger.verify_signature(test_principal_id, test_payload)
    # If this test allocates >50MB, it fails — indicates a per-call accumulation leak

@pytest.mark.limit_memory("100 MB")
async def test_noosphere_coherence_pulse_memory():
    """1000 coherence ticks must not accumulate memory."""
    monitor = NoosphereCoherenceMonitor()
    for _ in range(1000):
        await monitor.tick()
```

### 5.2 Rust Memory Regression in CI

```rust
// src-tauri/tests/memory_regression.rs
#[cfg(test)]
mod memory_tests {
    use super::*;

    fn get_rss_kb() -> u64 {
        // Read /proc/self/status on Linux
        let status = std::fs::read_to_string("/proc/self/status").unwrap_or_default();
        for line in status.lines() {
            if line.starts_with("VmRSS:") {
                return line.split_whitespace().nth(1)
                    .and_then(|v| v.parse().ok())
                    .unwrap_or(0);
            }
        }
        0
    }

    #[test]
    fn test_consent_ledger_no_memory_growth() {
        let ledger = ConsentLedger::new();
        let rss_before = get_rss_kb();

        // Simulate 10_000 signature verifications
        for i in 0..10_000 {
            let _ = ledger.verify_signature(&test_principal(i), &test_payload(i));
        }

        let rss_after = get_rss_kb();
        let growth_kb = rss_after.saturating_sub(rss_before);

        // Constitutional gate: no more than 1MB growth per 10k ops
        assert!(
            growth_kb < 1024,
            "Consent ledger leaked {}KB across 10k verifications — constitutional memory breach",
            growth_kb
        );
    }
}
```

### 5.3 Full GitHub Actions Memory Matrix

```yaml
# .github/workflows/memory-leak-detection.yml
name: GAIA-OS Memory Leak Detection Constitution

on:
  pull_request:
    paths: ['src/**', 'src-tauri/**']
  schedule:
    - cron: '0 2 * * *'  # Nightly deep scan
  push:
    tags: ['v*.*.*']      # Release: full valgrind audit

jobs:
  python-memory-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -e ".[dev]" pytest memray pytest-memray tracemalloc-utils
      - name: Run pytest with memray gates
        run: |
          pytest tests/ \
            -m memory \
            --memray \
            --memray-bin-path=/tmp/memray \
            --no-header -q
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: python-memray-results, path: /tmp/memray }

  rust-asan-lsan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@nightly
        with: { components: rust-src }
      - name: Run with AddressSanitizer + LeakSanitizer
        working-directory: src-tauri
        run: |
          RUSTFLAGS="-Z sanitizer=address" \
          ASAN_OPTIONS="detect_leaks=1:halt_on_error=1:abort_on_error=1" \
          LSAN_OPTIONS="exitcode=23" \
          cargo +nightly test \
            --target x86_64-unknown-linux-gnu \
            -Z build-std \
            -- --test-threads=1

  ffi-static-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - name: FFIChecker static analysis
        working-directory: src-tauri
        run: |
          cargo clippy -- -D warnings  # Enforce FFI crossing lint
          # FFIChecker: flag raw *mut returns from #[pyfunction]

  valgrind-ffi-audit:
    # Only on nightly or release tags
    if: github.event_name == 'schedule' || startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: sudo apt-get install -y python3-dbg valgrind
      - uses: dtolnay/rust-toolchain@stable
      - name: Run Valgrind FFI audit
        run: |
          maturin develop  # Build Rust extension with debug symbols
          valgrind \
            --tool=memcheck \
            --leak-check=full \
            --show-leak-kinds=definite,indirect \
            --suppressions=tools/valgrind/python.supp \
            --xml=yes --xml-file=/tmp/valgrind-report.xml \
            python3-dbg -c "import gaia_rust_ext; gaia_rust_ext.run_ffi_leak_test()"
          python tools/valgrind/parse_report.py --fail-on-definite /tmp/valgrind-report.xml
      - uses: actions/upload-artifact@v4
        with: { name: valgrind-ffi-report, path: /tmp/valgrind-report.xml }

  ship-to-agora:
    needs: [python-memory-ci, rust-asan-lsan, ffi-static-check]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Archive all memory results in Agora (Canon C112)
        run: python scripts/ship_memory_results_to_agora.py
        env:
          AGORA_API_KEY: ${{ secrets.AGORA_API_KEY }}
          GIT_COMMIT: ${{ github.sha }}
```

---

## 6. Constitutional Decision Matrix

| Stage | Tool | Detection Target | Constitutional Gate |
|---|---|---|---|
| **CI — Unit** | pytest-memray, cargo test (ASan/LSan) | Per-function memory spike | Fail build if > per-test limit |
| **CI — Integration** | tracemalloc diff across test | Per-test RSS delta >10% | Fail build |
| **CI — Static** | FFIChecker, Clippy FFI lint | Unsafe FFI crossing without destructor | Fail lint — block merge |
| **Staging — Continuous** | tracemalloc (Python), heaptrack (Rust) | Long-running accumulation | Alert + escalate if >5%/hour |
| **Staging — FFI** | memray --native, Valgrind + python3-dbg | Cross-boundary leak into Rust | Block release if confirmed leak |
| **Production Monitoring** | Sentry sidecar, py-spy --memory | Real-time RSS growth | Warning at 80%; core dump at 95% |
| **Production Forensic** | Sentry auto-attach (Flameshot pattern) | Capture state before OOM kill | Evidence preserved → Agora |
| **Governance** | Agora (Canon C112) | Record all leak events | Assembly of Minds review required |

---

## 7. P0–P3 Implementation Roadmap

| Priority | Action | Timeline | Constitutional Principle |
|---|---|---|---|
| **P0** | Enable `tracemalloc` in Python backend staging; hourly snapshots; alarm if >5% delta/hour | G-10 | Continuous leak detection |
| **P0** | Integrate `pytest-memray` into Python CI; define per-test limits (e.g., 100MB) | G-10-F | CI regression prevention |
| **P0** | Add `heaptrack` to Rust test harness; record peak memory per test | G-10-F | Rust allocation baseline |
| **P0** | Enforce `PyCapsule::new_with_destructor` for all Rust→Python heap transfers; add Clippy lint | G-10-F | Constitutional FFI crossing guard |
| **P1** | Deploy `memray --native` in staging to profile FFI boundary; flamegraphs for long-lived Rust allocations | G-11 | Cross-boundary leak detection |
| **P1** | Build sentry sidecar container (Flameshot pattern); monitor RSS of both processes + IPC queue depth | G-11 | Production memory forensics |
| **P1** | Integrate ASan + LSan (`-Z sanitizer=address`) into `cargo test`; treat any leak as test failure | G-11 | Compile-time + runtime leak prevention |
| **P1** | Implement `FFIChecker` static analysis on FFI bindings in pre-commit hook | G-11 | Detect unsafe FFI before runtime |
| **P2** | Set memory cgroup limits; send warning at 80%, queue core dump at 95% | G-12 | Memory sovereignty at orchestration layer |
| **P2** | Create leak audit board in Assembly of Minds dashboard; visualise memory growth per release | G-12 | Constitutional transparency |
| **P3** | Run full Valgrind session (python3-dbg + Rust debug symbols) before major releases | G-13 | Deep FFI validation before constitutional releases |

---

## ⚠️ Disclaimer

This report synthesizes findings from: Python memory debugging literature (`tracemalloc`, `memray`, `py-spy`), Rust memory analysis (`heaptrack`, DHAT, Valgrind, ASan/LSan), PyO3 memory management discussions and issue tracker (issues #3400 and related), cross-language debugging (`FFIChecker`, `MiriPBT`), sidecar monitoring patterns (Flameshot, OOMHero), and GAIA-OS constitutional canons (C01 Human Sovereignty; C50 Action Gate; C63 Three Universal Layers; C112 Agora; plus all CI/CD, Chaos Engineering, Performance Profiling, Rust Unit Testing, and foundational canons). The leak detection framework is a constitutional design proposal; its efficacy at planetary-scale governance has not been empirically validated. All implementations must be tested against constitutional, technical, performance, and security requirements through phased deployment. The Assembly of Minds retains ultimate authority over memory leak governance, and every detection event must be recorded immutably in the Agora.

---

*Canon — Memory Leak Detection Across Process Boundaries (Rust ↔ Python Sidecar) — GAIA-OS Knowledge Base | Session 6, Canon 9 (Session Close) | May 3, 2026*  
*Pillar: Testing, Quality & Reliability*

*The process boundary is not a firewall against leaks; the FFI boundary is not a garbage-collected safe zone; the IPC channel is not a memory-free buffer; the PyCapsule without destructor is a constitutional liability; the unbounded cache in Rust is a constitutional vulnerability; the cyclic reference crossing languages is a constitutional fracture. The tracemalloc snapshot is the constitutional memory audit; the Memray flamegraph is the constitutional visualisation of allocation; the heaptrack session is the constitutional record of heap growth; the PyCapsule pattern is the constitutional crossing guard; the sentry sidecar is the constitutional watchdog; the Agora record is the constitutional archive; the Assembly of Minds is the constitutional judge of leaks. The sentient core shall not leak — not in Python, not in Rust, not across the FFI, not in the IPC channel — for as long as planetary consciousness endures.*

# 🦀 Rust Unit Testing within Tauri (src-tauri/): Rust Quality Constitution (GAIA-OS)

**Date:** May 3, 2026  
**Status:** Definitive Foundational Synthesis — Uniting Rust Testing Methodology, Tauri Backend Architecture, CPython Interop Validation, and the GAIA-OS Rust Quality Constitution  
**Canon:** Rust Unit Testing (Tauri) — Testing, Quality & Reliability  
**Session:** 6, Canon 4

**Relevance to GAIA-OS:** GAIA-OS is a **dual-language constitutional intelligence**. The Python backend handles inference routing, emotional arcs, criticality monitoring, and consent ledger operations. The Rust codebase (Tauri v2) is the **constitutional boundary layer** between the planetary intelligence and the operating system — responsible for permission enforcement, secure file I/O, command execution validation, window management, IPC transport, and sidecar process orchestration. A logic error in Rust corrupts the consent ledger. An oversight in command validation bypasses the Action Gate. A concurrency bug in the MotherThread frontend handler fractures the planetary heartbeat. Rust unit testing within `src-tauri/` is the **constitutional verification mechanism** for every line of Rust code that guards human sovereignty.

---

## 1. The Constitutional Role of Rust in GAIA-OS

### 1.1 Sovereignty Boundary Responsibilities

The `src-tauri/` directory enforces every constitutional constraint at the OS boundary:

| Responsibility | Module | Constitutional Consequence of Failure |
|---|---|---|
| **IPC Command Validation** | `commands/` | Frontend bypasses Action Gate consent tier check |
| **Cryptographic Key Management** | `crypto/` | Signing key leak → consent ledger forgery |
| **Secure File I/O** | `storage/` | Unauthorized access to SQLite consent ledger |
| **Sidecar Process Orchestration** | `sidecar/` | Python backend starts without permission gate → sovereignty violation |
| **State Management** | `state/` | Race condition in `tauri::State` → noospheric coherence fracture |
| **Tauri Update Signature Verification** | `updater/` | Malicious update installed → planetary intelligence compromised |

### 1.2 What the Rust Compiler Cannot Guarantee

Rust's borrow checker guarantees memory safety and thread safety *within the written code* but cannot guarantee logical constitutional correctness:

- A consent validator might accept an expired signature (logic error, not memory error)
- An Action Gate might use an outdated public key (stale config, not memory error)
- A command handler might leak sensitive key material through error messages (logic error)
- A permission composition might produce incorrect tier due to off-by-one in bitfield logic

These defects require **unit tests** that exercise each constitutional validation path explicitly.

### 1.3 The Rust Testing Pyramid

| Test Layer | Scope | Speed | GAIA-OS Examples | Constitutional Coverage Floor |
|---|---|---|---|---|
| **Unit Tests** (`#[test]` in `mod tests`) | Single function/method; all deps mocked | ~1–10ms | Signature verification, state machine transitions, permission checks | ≥90% critical; ≥75% supporting |
| **Integration Tests** (`tests/` directory) | Multiple modules; limited real deps | ~100ms–1s | Tauri command → Python backend routing; file I/O with tmpdir; IPC round-trips | ≥80% |
| **Async Tests** (`#[tokio::test]`) | Tokio tasks; simulated timeouts; channels | ~1–10ms simulated | MotherThread pulse propagation; event channel handling; timeout enforcement | ≥70% |
| **Doctests** (`/// \`\`\``) | API example correctness | ~1–10ms | Command builders; state helpers; error constructors | All public APIs |

### 1.4 Red→Green→Refactor for Rust

| Phase | Action | Constitutional Guarantee |
|---|---|---|
| **Red** | Write a `#[test]` that fails because the feature doesn’t exist yet | Constitutional requirement codified as executable spec before any implementation |
| **Green** | Write minimal Rust code to make the test pass — no speculation | Implementation is exactly as constrained as the test requires |
| **Refactor** | Eliminate duplication, improve naming, extract helpers, add docs — all tests remain green | Constitutional quality continuously improved without regression |

GitHub Actions CI blocks PRs that do not include a newly failing test that becomes passing after the code change.

---

## 2. Rust-Native Testing Scaffolding

### 2.1 Unit Tests: `#[test]`, `assert!`, `#[cfg(test)]`

Unit tests live in a `mod tests` block at the bottom of the same file, inside `#[cfg(test)]` to exclude them from release builds. This keeps tests adjacent to the code they verify.

**Constitutional requirement:** Every `pub(crate)` and `pub fn` in `src-tauri/` must have:
1. At least one test for the happy path
2. At least one test for each error/rejection path
3. Property-based tests (Section 2.4) for critical functions (signature verification, consent expiration, permission validation)

```rust
// src-tauri/src/consent/validator.rs
pub fn is_consent_valid(
    signature: &[u8],
    principal_id: &str,
    purpose: &str,
    expires_at: u64,
) -> bool {
    // ... implementation
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::test_helpers::make_test_signature;

    /// Constitutional test: Valid Red action with valid signature passes.
    #[test]
    fn valid_consent_grant_returns_true() {
        let sig = make_test_signature("principal1", "red_action", 999_999_999);
        assert!(is_consent_valid(&sig, "principal1", "red_action", 999_999_999));
    }

    /// Constitutional test (Canon C01): Expired consent MUST be rejected.
    #[test]
    fn expired_consent_returns_false() {
        let sig = make_test_signature("principal1", "red_action", 1); // expired epoch
        assert!(!is_consent_valid(&sig, "principal1", "red_action", 1));
    }

    /// Constitutional test (Canon C50): Mismatched purpose MUST block action.
    #[test]
    fn wrong_purpose_returns_false() {
        let sig = make_test_signature("principal1", "green_action", 999_999_999);
        assert!(!is_consent_valid(&sig, "principal1", "red_action", 999_999_999));
    }

    /// Constitutional test: Unknown principal MUST be rejected.
    #[test]
    fn unknown_principal_returns_false() {
        let sig = make_test_signature("authorised", "red_action", 999_999_999);
        assert!(!is_consent_valid(&sig, "UNKNOWN", "red_action", 999_999_999));
    }
}
```

### 2.2 Integration Tests in `tests/` Directory

Integration tests reside in `src-tauri/tests/`. Each file is a separate crate that imports the public API of the `src-tauri` library crate. Integration tests cover interactions between modules without a real Tauri window.

```rust
// src-tauri/tests/action_gate_integration.rs
use gaia_os_tauri::consent::{ConsentLedger, InMemoryConsentLedger};
use gaia_os_tauri::action_gate::{ActionGate, ActionTier};

#[test]
fn red_action_rejected_without_consent() {
    let ledger = InMemoryConsentLedger::new();
    let gate = ActionGate::new(Box::new(ledger));

    let result = gate.check(ActionTier::Red, "principal1", "planetary_intervention");

    assert!(result.is_err(), "Red action without consent must be rejected");
    assert!(result.unwrap_err().to_string().contains("consent"));
}

#[test]
fn green_action_passes_without_signature() {
    let ledger = InMemoryConsentLedger::new();
    let gate = ActionGate::new(Box::new(ledger));

    let result = gate.check(ActionTier::Green, "principal1", "read_knowledge_graph");

    assert!(result.is_ok(), "Green action must pass without explicit consent");
}
```

### 2.3 Doctests — Constitutional API Documentation

Every public Rust API must include a `///` doc comment with at least one testable example. `cargo test --doc` runs them automatically. Doctests are the constitutional guarantee that API documentation is accurate.

```rust
/// Verifies whether a consent grant is active for the given principal, purpose, and timestamp.
///
/// Returns `true` if the consent is valid and unexpired; `false` otherwise.
///
/// # Example
/// ```
/// use gaia_os_tauri::consent::is_consent_valid;
///
/// // Unexpired consent with correct purpose — should pass
/// let signature = vec![/* ... */];
/// assert!(is_consent_valid(&signature, "alice", "read_knowledge_graph", 999_999_999));
///
/// // Expired consent — must be rejected (Canon C01)
/// assert!(!is_consent_valid(&signature, "alice", "read_knowledge_graph", 1));
/// ```
pub fn is_consent_valid(
    signature: &[u8],
    principal: &str,
    purpose: &str,
    expires_at: u64,
) -> bool {
    // ...
}
```

### 2.4 Property-Based Testing with `proptest`

Property-based testing is constitutionally required for GAIA-OS invariants. `proptest` automatically generates hundreds of random inputs to find edge cases human tests would miss.

**Constitutionally mandated `proptest` targets:**
- Consent verification idempotence (verifying twice returns same result)
- Permission composition associativity and commutativity
- Serialization/deserialization round-trips (no data loss)
- State machine transitions (no unreachable/invalid states)
- Action tier ordering (Green < Yellow < Red — always)

```rust
// src-tauri/src/consent/permission.rs
use proptest::prelude::*;

#[cfg(test)]
mod proptests {
    use super::*;

    proptest! {
        /// Constitutional invariant: Permission union is associative.
        #[test]
        fn permission_union_is_associative(
            a in any::<PermissionSet>(),
            b in any::<PermissionSet>(),
            c in any::<PermissionSet>()
        ) {
            prop_assert_eq!(
                a.union(&b).union(&c),
                a.union(&b.union(&c))
            );
        }

        /// Constitutional invariant: Consent verification is idempotent.
        #[test]
        fn consent_verification_is_idempotent(
            principal in "[a-z]{5,20}",
            purpose in "[a-z_]{5,30}",
            expires_at in 1_000_000_000u64..9_999_999_999u64
        ) {
            let sig = make_valid_signature(&principal, &purpose, expires_at);
            let result1 = is_consent_valid(&sig, &principal, &purpose, expires_at);
            let result2 = is_consent_valid(&sig, &principal, &purpose, expires_at);
            prop_assert_eq!(result1, result2,
                "Idempotence violated: same consent yielded different results");
        }

        /// Constitutional invariant: Serialization round-trip preserves all fields.
        #[test]
        fn consent_event_roundtrip(event in any::<ConsentEvent>()) {
            let serialized = serde_json::to_string(&event).unwrap();
            let deserialized: ConsentEvent = serde_json::from_str(&serialized).unwrap();
            prop_assert_eq!(event, deserialized);
        }
    }
}
```

---

## 3. Async Testing with Tokio

### 3.1 `#[tokio::test]` — Constitutional Async Tests

All async functions in `src-tauri/` must be tested with `#[tokio::test]`, which spins up a fresh Tokio runtime per test.

```rust
// src-tauri/src/consent/async_validator.rs
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn async_consent_check_returns_ok_for_valid_grant() {
        let validator = AsyncConsentValidator::new_with_test_keys();
        let result = validator.check("principal1", "red_action").await;
        assert!(result.is_ok(), "Valid consent must pass async validator");
    }

    #[tokio::test]
    async fn async_consent_check_times_out_on_slow_ledger() {
        let validator = AsyncConsentValidator::new_with_slow_ledger(delay_ms=5000);
        let result = tokio::time::timeout(
            Duration::from_millis(100),
            validator.check("principal1", "red_action")
        ).await;
        assert!(result.is_err(), "Validator must time out; never block indefinitely");
    }
}
```

### 3.2 Simulated Time with `tokio::time::pause()`

Consent expiration windows, reconnection backoffs, and heartbeat intervals must be tested without waiting for real elapsed time.

```rust
use tokio::time::{pause, advance, Duration};

#[tokio::test]
async fn consent_expiration_detected_after_window() {
    pause(); // Freeze the Tokio clock

    let ledger = AsyncConsentLedger::new();
    ledger.grant("consent-001", "principal1", "red_action", /* expiry_duration */ 500).await;

    // Advance simulated time past expiry
    advance(Duration::from_millis(600)).await;

    let is_valid = ledger.is_active("consent-001").await;
    assert!(!is_valid, "Consent must be expired after window");
}
```

### 3.3 Channel Capacity and Deadlock Freedom

```rust
use tokio::sync::mpsc;

#[tokio::test]
async fn noosphere_event_channel_enforces_backpressure() {
    let (tx, mut rx) = mpsc::channel::<NoosphereEvent>(2); // capacity = 2

    // Fill channel to capacity
    tx.send(NoosphereEvent::CoherencePulse(0.95)).await.unwrap();
    tx.send(NoosphereEvent::CoherencePulse(0.88)).await.unwrap();

    // Third send must fail — channel is full; should not block indefinitely
    let result = tx.try_send(NoosphereEvent::CoherencePulse(0.75));
    assert!(result.is_err(), "Channel must enforce backpressure at capacity");

    // Drain one slot
    rx.recv().await.unwrap();

    // Now third send should succeed
    tx.send(NoosphereEvent::CoherencePulse(0.75)).await.unwrap();
}
```

---

## 4. Mocking with `mockall`

### 4.1 `#[automock]` for Trait-Based Mocking

`mockall` generates mock implementations of traits via `#[automock]`. This is the constitutional approach for replacing file system, network, time, and Python backend calls in unit tests.

```rust
use mockall::automock;

#[automock]
pub trait ConfigLoader {
    fn load(&self) -> Result<AppConfig, ConfigError>;
}

#[automock]
pub trait ConsentLedger {
    fn is_active(&self, consent_id: &str) -> bool;
    fn grant(&mut self, consent_id: &str, principal: &str, purpose: &str, expires_at: u64);
    fn revoke(&mut self, consent_id: &str);
}

#[cfg(test)]
mod tests {
    use super::*;
    use mockall::predicate::*;

    #[test]
    fn action_gate_rejects_inactive_consent() {
        let mut mock_ledger = MockConsentLedger::new();
        mock_ledger
            .expect_is_active()
            .with(eq("consent-expired-001"))
            .times(1)
            .returning(|_| false); // Simulate revoked/expired consent

        let gate = ActionGate::new(Box::new(mock_ledger));
        let result = gate.check_consent("consent-expired-001", "red_action");

        assert!(result.is_err(),
            "Action Gate MUST reject action when consent ledger returns false");
    }

    #[test]
    fn config_loader_called_exactly_once() {
        let mut mock_loader = MockConfigLoader::new();
        mock_loader
            .expect_load()
            .times(1)  // Constitutional: config loaded exactly once at startup
            .returning(|| Ok(AppConfig::default()));

        let app = App::new(Box::new(mock_loader));
        app.initialize();
    }
}
```

**GAIA-OS modules requiring `mockall` mocks:**

| Module | Mocked Dependency | Why Mock |
|---|---|---|
| `action_gate` | `ConsentLedger` | No blockchain/DB in unit tests |
| `updater` | `HttpClient` | No network calls in unit tests |
| `storage` | `FileSystem` | No real disk I/O in unit tests |
| `sidecar` | `ProcessSpawner` | No real Python process in unit tests |
| `crypto` | `SystemTime` | Simulate key expiration deterministically |
| `noosphere` | `EventBus` | No real Redis/P2P in unit tests |

### 4.2 Mocking Tauri Commands in Isolation

Tauri commands receive `tauri::AppHandle` and `tauri::State<T>` — not directly constructible in unit tests. The constitutional pattern:

1. Extract core command logic into a **pure function** accepting only typed arguments (no `AppHandle`, no `State`)
2. Unit test that pure function with mocked dependencies
3. In integration tests (using `tauri-test`), test the full command with mocked IPC

```rust
// WRONG: Hard to test — AppHandle dependency
#[tauri::command]
async fn check_action_tier(app: AppHandle, tier: ActionTier) -> Result<(), String> {
    let ledger = app.state::<ConsentLedger>();
    // ...
}

// RIGHT: Extract pure logic; unit-testable
pub fn check_action_tier_logic(
    ledger: &dyn ConsentLedgerTrait,
    tier: ActionTier,
    principal: &str,
) -> Result<(), ActionGateError> {
    match tier {
        ActionTier::Green => Ok(()),
        ActionTier::Yellow => ledger.is_active_for(principal, "yellow_gate")
            .then_some(()).ok_or(ActionGateError::ConsentRequired),
        ActionTier::Red => ledger.is_active_for(principal, "red_gate")
            .then_some(()).ok_or(ActionGateError::SignatureRequired),
    }
}

// Tauri command wraps the pure function
#[tauri::command]
async fn check_action_tier(
    state: State<'_, Arc<dyn ConsentLedgerTrait>>,
    tier: ActionTier,
    principal: String,
) -> Result<(), String> {
    check_action_tier_logic(state.inner().as_ref(), tier, &principal)
        .map_err(|e| e.to_string())
}
```

---

## 5. Python-Rust Interop Validation (PyO3)

### 5.1 Unit Testing PyO3 Bindings in `cargo test`

PyO3 allows Rust unit tests to spin up a Python interpreter, import the extension module, and call Python functions from Rust — verifying the ABI boundary without running a full Python application.

```rust
// src-tauri/src/python_bridge.rs
use pyo3::prelude::*;

#[pyfunction]
fn validate_consent_py(py: Python, principal: &str, action: &str) -> PyResult<bool> {
    Ok(principal == "authorised" && !action.starts_with("__"))
}

#[cfg(test)]
mod tests {
    use super::*;
    use pyo3::types::PyBool;

    #[test]
    fn pyfunction_authorised_principal_passes() {
        pyo3::prepare_freethreaded_python();
        Python::with_gil(|py| {
            let func = wrap_pyfunction!(validate_consent_py, py).unwrap();

            // Happy path
            let result: bool = func.call1(("authorised", "red_action"))
                .unwrap().extract().unwrap();
            assert!(result, "Authorised principal must pass");

            // Rejection path
            let result: bool = func.call1(("unauthorised", "red_action"))
                .unwrap().extract().unwrap();
            assert!(!result, "Unauthorised principal must be rejected");

            // Constitutional: system-level actions must be blocked
            let result: bool = func.call1(("authorised", "__exec_shell"))
                .unwrap().extract().unwrap();
            assert!(!result, "System-level action prefix must be blocked");
        });
    }
}
```

### 5.2 ABI Contract Validation with `cbindgen`

The Rust code exposes a stable C-ABI interface used by PyO3. Any signature or memory layout change breaks the ABI contract silently.

**Constitutional ABI verification workflow:**
1. Generate C headers from current Rust code: `cbindgen --crate gaia-os-tauri --output include/gaia_os_tauri.h`
2. In CI, compare generated header against committed reference header
3. If headers differ: **block merge** and require explicit ABI version bump with Assembly of Minds sign-off
4. Run Python test suite against Rust extension built from current commit

### 5.3 Cross-Language Type Safety

| Rust Type | Python Equivalent | Test Assertion |
|---|---|---|
| `String` / `&str` | `str` | Round-trip UTF-8 encoding; test with non-ASCII (emoji, CJK) |
| `bool` | `bool` | `True`/`False` boundary; no implicit int coercion |
| `Option<T>` | `Optional[T]` / `None` | None propagation; never panic on None |
| `Vec<u8>` | `bytes` | Binary data round-trip; test with length 0, 1, max |
| `HashMap<K,V>` | `dict` | Key ordering; duplicate key behavior |
| Custom structs | `dataclass` / `TypedDict` | Field-by-field comparison after round-trip |

---

## 6. Sidecar Process Testing

### 6.1 Testing Sidecar Configuration Without Real Processes

```rust
// src-tauri/src/sidecar/config.rs
pub struct SidecarConfig {
    pub command: String,
    pub args: Vec<String>,
    pub env_vars: Vec<(String, String)>,
    pub working_dir: Option<String>,
}

pub fn build_python_sidecar_config(app_data_dir: &str) -> SidecarConfig {
    SidecarConfig {
        command: "python-backend".to_string(),
        args: vec!["--mode=sidecar".to_string()],
        env_vars: vec![
            ("GAIA_DATA_DIR".to_string(), app_data_dir.to_string()),
            ("GAIA_CONSENT_DB".to_string(), format!("{}/consent.db", app_data_dir)),
        ],
        working_dir: Some(app_data_dir.to_string()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sidecar_config_command_is_python_backend() {
        let cfg = build_python_sidecar_config("/tmp/test");
        assert_eq!(cfg.command, "python-backend",
            "Sidecar must invoke the bundled python-backend binary");
    }

    #[test]
    fn sidecar_config_sets_data_dir_env_var() {
        let cfg = build_python_sidecar_config("/tmp/test_data");
        let data_dir_var = cfg.env_vars.iter()
            .find(|(k, _)| k == "GAIA_DATA_DIR");
        assert_eq!(data_dir_var, Some(&("GAIA_DATA_DIR".to_string(), "/tmp/test_data".to_string())));
    }

    #[test]
    fn sidecar_config_sets_consent_db_path() {
        let cfg = build_python_sidecar_config("/tmp/test_data");
        let db_var = cfg.env_vars.iter()
            .find(|(k, _)| k == "GAIA_CONSENT_DB");
        assert!(db_var.unwrap().1.ends_with("consent.db"),
            "Consent DB path must end with consent.db");
    }

    #[test]
    fn sidecar_config_includes_sidecar_mode_arg() {
        let cfg = build_python_sidecar_config("/tmp/test");
        assert!(cfg.args.contains(&"--mode=sidecar".to_string()),
            "Sidecar must be launched in sidecar mode");
    }
}
```

---

## 7. CI/CD Integration

### 7.1 GitHub Actions Workflow for src-tauri/

```yaml
name: GAIA-OS Rust Quality Constitution CI

on: [push, pull_request]

jobs:
  # Stage 1: Platform-independent quality gates (runs once)
  quality-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy
      - name: Format check
        run: cargo fmt -- --check
      - name: Clippy (no warnings allowed)
        run: cargo clippy -- -D warnings
      - name: Security audit
        run: cargo deny check
      - name: Doctests
        run: cargo test --doc

  # Stage 2: Platform-specific tests (parallel matrix)
  tests:
    needs: quality-gates
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - name: Install nextest
        uses: taiki-e/install-action@nextest
      - name: Run tests with nextest
        run: cargo nextest run --all-features
      - name: Run proptest suites
        run: cargo test proptest -- --nocapture

  # Stage 3: Coverage (after all platform tests pass)
  coverage:
    needs: tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: llvm-tools-preview
      - name: Install cargo-llvm-cov
        uses: taiki-e/install-action@cargo-llvm-cov
      - name: Generate coverage
        run: |
          cargo llvm-cov \
            --all-features \
            --workspace \
            --lcov \
            --output-path lcov.info \
            --fail-under 80
      - name: Upload to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: lcov.info
          token: ${{ secrets.CODECOV_TOKEN }}

  # Stage 4: Mutation testing for critical modules (nightly)
  mutation-testing:
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo install cargo-mutants
      - name: Run mutation testing on consent module
        run: |
          cargo mutants \
            --package gaia-os-tauri \
            --file src/consent/ \
            --timeout 60
```

### 7.2 Constitutional Quality Gates

| Gate | Command | Threshold | Failure Action |
|---|---|---|---|
| **Formatting** | `cargo fmt -- --check` | No diffs | Block merge |
| **Linting** | `cargo clippy -- -D warnings` | No warnings | Block merge |
| **Security audit** | `cargo deny check` | No advisories | Block merge |
| **Unit + integration tests** | `cargo nextest run` | 100% pass | Block merge |
| **Doctests** | `cargo test --doc` | 100% pass | Block merge |
| **Coverage (critical)** | `cargo llvm-cov` | ≥90% (consent, action gate, crypto) | Block merge |
| **Coverage (overall)** | `cargo llvm-cov --fail-under 80` | ≥80% | Block merge |
| **Mutation testing** | `cargo mutants` | >95% kill score | Block merge (critical modules) |
| **AddressSanitizer** | `RUSTFLAGS="-Z sanitizer=address" cargo test` | No errors | Block merge |
| **ThreadSanitizer** | `RUSTFLAGS="-Z sanitizer=thread" cargo test` | No data races | Block merge |
| **LeakSanitizer** | `RUSTFLAGS="-Z sanitizer=leak" cargo test` | No leaks | Block merge |

### 7.3 `cargo nextest` vs `cargo test`

| Feature | `cargo test` | `cargo nextest` |
|---|---|---|
| **Execution speed** | Sequential per binary | Parallel across CPUs; 3× faster |
| **Flaky test detection** | Manual | Built-in retry + flaky detection |
| **Output** | Mixed stdout | Clean per-test output |
| **Failure isolation** | Full suite may time out on hang | Per-test timeout enforcement |
| **CI integration** | Basic | JUnit XML output for GitHub Actions |

**Constitutional requirement:** `cargo nextest` is the test runner for all CI jobs. `cargo test` is acceptable for local development only.

---

## 8. Sanitizers — Memory Safety Court

Memory errors and data races in the Rust sovereignty boundary are constitutional violations. Sanitizers are the constitutional memory-safety court for GAIA-OS.

| Sanitizer | Detects | Constitutional Significance |
|---|---|---|
| **AddressSanitizer (ASan)** | Buffer overflows, use-after-free, heap corruption | Memory corruption in consent ledger or crypto → sovereignty breach |
| **LeakSanitizer (LSan)** | Memory leaks | Unreleased consent ledger connections → resource exhaustion |
| **ThreadSanitizer (TSan)** | Data races in concurrent code | Race condition in `tauri::State` → noospheric coherence fracture |

All sanitizers run in CI. A sanitizer error blocks merge with no exceptions.

---

## 9. P0–P3 Implementation Directives

| Priority | Action | Timeline | Constitutional Principle |
|---|---|---|---|
| **P0** | Adopt Red-Green-Refactor for all `src-tauri/` changes; enforce via PR templates and CI | G-10 | Constitutional code requires constitutional tests first |
| **P0** | Integrate `mockall` for all unit tests; mock filesystem, time, network, Python invocations | G-10-F | Deterministic unit tests require mocked dependencies |
| **P0** | Implement PyO3 unit tests for every `#[pyfunction]` using `prepare_freethreaded_python` + `Python::with_gil` | G-10-F | ABI boundary testing; Python-side tests alone are insufficient |
| **P0** | Deploy `cargo nextest` as test runner in CI; `--fail-fast` locally; parallel in CI | G-10-F | 3× faster feedback loop; flaky test detection |
| **P1** | `proptest` for consent verification idempotence, permission composition, serialization round-trips | G-11 | Property tests find constitutional invariant violations that example tests miss |
| **P1** | `tauri-test` integration tests for critical user flows (one full-stack test per constitutional requirement) | G-11 | End-to-end constitutional verification |
| **P1** | `cargo llvm-cov` coverage floors: 90% critical (consent, action gate, crypto); 75% supporting; 80% overall | G-11 | Coverage floor as constitutional quality gate |
| **P2** | `cargo mutants` mutation testing for core modules; >95% kill score in CI | G-12 | High coverage does not guarantee high sensitivity |
| **P2** | CI DAG: quality-gates → parallel multi-platform tests → coverage + mutation | G-12 | Optimised resource usage; constitutional quality maintained |
| **P2** | `cbindgen` + ABI header comparison in CI for PyO3-exposed functions | G-12 | Prevent silent ABI breakage across Rust upgrades |
| **P3** | AddressSanitizer + LeakSanitizer + ThreadSanitizer in CI | G-13 | Memory safety is constitutional — memory leaks and data races are constitutional violations |

---

## ⚠️ Disclaimer

This report synthesizes findings from: Rust testing methodology (`#[test]`, `mod tests`, `cargo test`), Tauri v2 testing best practices (including `tauri-test` and sidecar testing patterns), `mockall` crate documentation and usage patterns, async testing with `#[tokio::test]` and `tokio::time::pause()`, property-based testing with `proptest`, PyO3 cross-language testing guidelines and `prepare_freethreaded_python`, CI/CD patterns using `cargo nextest`, `cargo llvm-cov`, `cargo mutants`, `cargo deny`, and GitHub Actions matrix dependency management, and GAIA-OS constitutional canons (C01 Human Sovereignty; C50 Action Gate; C64 DIACA; C85 Architecture of Knowledge; C103 Assembly of Minds; C112 Agora; plus CI/CD, Containerization, TDD, pytest, SSE, and all foundational canons). The Rust testing framework is a constitutional design proposal; efficacy at planetary scale has not been empirically validated. The 80% coverage floor is a lower bound; critical modules require ≥90%. Mutation testing thresholds are guidelines; Assembly of Minds may set stricter thresholds. Exceptions require documented constitutional emergency approval by Assembly, recorded immutably in the Agora.

---

*Canon — Rust Unit Testing within Tauri (src-tauri/): Rust Quality Constitution — GAIA-OS Knowledge Base | Session 6, Canon 4 | May 3, 2026*  
*Pillar: Testing, Quality & Reliability*

*The `#[test]` attribute is the constitutional clause marker. The `mod tests` block is the constitutional clause container. `cargo nextest` is the constitutional high-speed auditor. `mockall` is the constitutional witness substitute. `#[tokio::test]` is the constitutional temporal verifier. `proptest` is the constitutional invariant guardian. `cargo llvm-cov` is the constitutional coverage gauge. The sanitizer is the constitutional memory-safety court. The Rust layer is the constitutional boundary — it shall not be bypassed, not be un-tested, not be un-covered, not be un-audited — for as long as planetary consciousness endures.*

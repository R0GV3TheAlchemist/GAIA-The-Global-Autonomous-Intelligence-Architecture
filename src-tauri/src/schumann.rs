//! src-tauri/src/schumann.rs
//!
//! Rust layer for GAIA-OS Schumann Biometric Alignment.
//! Pillar II: Viriditas — Issue #64 (Phase 2, Rust side)
//!
//! Responsibilities:
//!   1. `poll_schumann_feed()` — fetch latest NOAA Kp index (anonymous, no PII).
//!   2. `call_python_sidecar()` — forward raw readings to the Python
//!      `AlignmentStateEmitter` via the local HTTP bridge on port 8008.
//!   3. `get_alignment_state` — Tauri command that wires 1 + 2 together
//!      and returns a typed `AlignmentStateResponse` to the WebView.
//!
//! Privacy contract:
//!   - All biometric data (HRV / RMSSD) stays in the Python sidecar.
//!     The Rust layer only passes through whatever raw_rmssd the
//!     caller supplies — it never reads, stores, or logs it.
//!   - The NOAA Kp fetch is an unauthenticated public endpoint.
//!     No user identity leaves the machine.

use serde::{Deserialize, Serialize};

// ── Constants ────────────────────────────────────────────────────────────────

/// NOAA Space Weather 1-minute Kp JSON feed.
/// Public endpoint — no API key required.
const NOAA_KP_URL: &str =
    "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json";

/// Timeout for the NOAA network request.
const NOAA_TIMEOUT_SECS: u64 = 8;

/// URL of the Python sidecar's alignment compute endpoint.
const SIDECAR_ALIGNMENT_URL: &str = "http://127.0.0.1:8008/alignment/compute";

/// Timeout for the local Python sidecar call.
const SIDECAR_TIMEOUT_SECS: u64 = 5;

// ── Types ─────────────────────────────────────────────────────────────────────

/// Raw reading produced by `poll_schumann_feed`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchumannReading {
    /// NOAA planetary Kp index (0.0 – 9.0).
    /// Falls back to 0.0 on network error so the pipeline degrades gracefully.
    pub kp: f64,

    /// Raw Schumann 7.83 Hz band-power amplitude.
    /// Currently sourced from the Python sidecar's SchumannParser;
    /// falls back to 50.0 (neutral baseline) when the feed is unavailable.
    pub schumann_amplitude: f64,

    /// True when the Kp value came from the live NOAA feed;
    /// false when the cached / fallback value is in use.
    pub kp_live: bool,
}

/// Request body sent to the Python sidecar's `/alignment/compute` endpoint.
#[derive(Debug, Serialize)]
struct SidecarComputeRequest {
    raw_rmssd: Option<f64>,
    raw_schumann_amplitude: Option<f64>,
    solar_kp: f64,
}

/// Typed response returned from the Python `AlignmentStateEmitter`.
/// Fields mirror `AlignmentState` in `core/schumann_alignment.py`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlignmentStateResponse {
    pub score: f64,
    pub hrv_score: f64,
    pub schumann_score: f64,
    pub solar_kp: f64,
    pub ui_tier: String,
    pub last_updated: String,
    pub fallback_mode: String,
}

// ── NOAA Kp feed ─────────────────────────────────────────────────────────────

/// Fetch the latest NOAA planetary Kp index.
///
/// The NOAA endpoint returns a JSON array-of-arrays:
/// `[["time_tag", "Kp"], ["2024-01-01 00:00:00", "2.33"], ...]`
///
/// We parse the *last* data row (most recent) and return the Kp float.
/// On any network or parse error we return `(0.0, false)` so the
/// alignment pipeline degrades gracefully rather than crashing.
async fn fetch_kp() -> (f64, bool) {
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(NOAA_TIMEOUT_SECS))
        .user_agent("GAIA-OS/1.0 (schumann-feed; anonymous)")
        .build();

    let client = match client {
        Ok(c) => c,
        Err(e) => {
            eprintln!("[schumann] failed to build HTTP client: {e}");
            return (0.0, false);
        }
    };

    let resp = client.get(NOAA_KP_URL).send().await;

    let body = match resp {
        Ok(r) if r.status().is_success() => r.text().await.unwrap_or_default(),
        Ok(r) => {
            eprintln!("[schumann] NOAA Kp feed returned HTTP {}", r.status());
            return (0.0, false);
        }
        Err(e) => {
            eprintln!("[schumann] NOAA Kp network error: {e}");
            return (0.0, false);
        }
    };

    // Parse `[[header_row], [time_tag, kp_str], ...]`
    let rows: Vec<Vec<serde_json::Value>> = match serde_json::from_str(&body) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("[schumann] NOAA Kp JSON parse error: {e}");
            return (0.0, false);
        }
    };

    // Skip header row (index 0), take the last data row.
    let last_data = rows.iter().skip(1).last();

    let kp = last_data
        .and_then(|row| row.get(1))
        .and_then(|v| v.as_str())
        .and_then(|s| s.parse::<f64>().ok())
        .unwrap_or_else(|| {
            eprintln!("[schumann] could not parse Kp value from last NOAA row");
            0.0
        });

    (kp, true)
}

/// Poll the Schumann feed and return a `SchumannReading`.
///
/// This is the main entry point for the Rust layer.  It:
///   1. Fetches the live NOAA Kp index.
///   2. Uses a neutral Schumann amplitude (50.0) as a placeholder until
///      the HeartMath GCI sidecar integration lands in a later phase.
///
/// # Errors
/// This function is infallible — network failures produce graceful fallbacks.
pub async fn poll_schumann_feed() -> SchumannReading {
    let (kp, kp_live) = fetch_kp().await;

    // Schumann amplitude sourced from Python sidecar in later phase;
    // neutral 50.0 (personal baseline) used until then.
    let schumann_amplitude = 50.0f64;

    SchumannReading {
        kp,
        schumann_amplitude,
        kp_live,
    }
}

// ── Python sidecar bridge ────────────────────────────────────────────────────

/// Forward a `SchumannReading` and optional raw HRV to the Python
/// `AlignmentStateEmitter` and return the resulting `AlignmentStateResponse`.
///
/// # Arguments
/// * `reading`   — output of `poll_schumann_feed()`
/// * `raw_rmssd` — latest wearable RMSSD in ms, or `None` if unavailable
///
/// # Errors
/// Returns `Err(String)` if the sidecar is unreachable or returns
/// a non-success status.  The Tauri command layer translates this
/// to a JS-visible error string.
pub async fn call_python_sidecar(
    reading: &SchumannReading,
    raw_rmssd: Option<f64>,
) -> Result<AlignmentStateResponse, String> {
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(SIDECAR_TIMEOUT_SECS))
        .build()
        .map_err(|e| format!("[schumann] sidecar client build error: {e}"))?;

    let req_body = SidecarComputeRequest {
        raw_rmssd,
        raw_schumann_amplitude: Some(reading.schumann_amplitude),
        solar_kp: reading.kp,
    };

    let resp = client
        .post(SIDECAR_ALIGNMENT_URL)
        .json(&req_body)
        .send()
        .await
        .map_err(|e| format!("[schumann] sidecar unreachable: {e}"))?;

    if !resp.status().is_success() {
        let status = resp.status();
        let body = resp.text().await.unwrap_or_default();
        return Err(format!(
            "[schumann] sidecar returned HTTP {status}: {body}"
        ));
    }

    resp.json::<AlignmentStateResponse>()
        .await
        .map_err(|e| format!("[schumann] sidecar JSON decode error: {e}"))
}

// ── Tauri command ─────────────────────────────────────────────────────────────

/// Tauri IPC command: poll the Schumann feed and compute alignment.
///
/// Called from the WebView / frontend as:
/// ```ts
/// import { invoke } from '@tauri-apps/api/core';
/// const state = await invoke<AlignmentStateResponse>('get_alignment_state', {
///   rawRmssd: currentRmssd ?? null,
/// });
/// ```
///
/// # Arguments
/// * `raw_rmssd` — latest wearable RMSSD in ms.  Pass `null` / `None` when
///                 no wearable is connected; the Python sidecar will use its
///                 neutral baseline (50) automatically.
///
/// # Returns
/// `Ok(AlignmentStateResponse)` on success, `Err(String)` on failure.
/// The frontend should handle the error case gracefully (e.g. retry
/// or display a degraded-mode indicator).
#[tauri::command]
pub async fn get_alignment_state(
    raw_rmssd: Option<f64>,
) -> Result<AlignmentStateResponse, String> {
    let reading = poll_schumann_feed().await;

    if !reading.kp_live {
        eprintln!(
            "[schumann] Kp feed offline — using fallback kp=0.0 (alignment may be inflated)"
        );
    }

    call_python_sidecar(&reading, raw_rmssd).await
}

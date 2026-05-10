//! GAIA-OS — Tauri ↔ Python sidecar bridge for Soul Mirror engines
//!
//! This module exposes the SovereignMemory, AffectEngine, and StageEngine
//! HTTP surfaces as Tauri `invoke`-able commands.  Every command is a thin
//! async proxy: it serialises the frontend payload, POSTs/GETs the sidecar
//! on 127.0.0.1:52000, and returns the JSON response verbatim.
//!
//! No business logic lives here — this is pure transport.
//!
//! # Commands
//!
//! | Command              | Method | Sidecar endpoint            |
//! |----------------------|--------|-----------------------------|
//! | `memory_remember`    | POST   | /memory/remember            |
//! | `memory_recall`      | POST   | /memory/recall              |
//! | `memory_semantic`    | POST   | /memory/semantic            |
//! | `memory_key_status`  | GET    | /memory/key-status          |
//! | `memory_key_rotate`  | POST   | /memory/key-rotate          |
//! | `affect_analyze`     | POST   | /affect/analyze             |
//! | `affect_history`     | GET    | /affect/history/{principal} |
//! | `affect_trend`       | GET    | /affect/trend/{principal}   |
//! | `stage_evaluate`     | POST   | /stage/evaluate             |

use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::Value;

/// Base URL of the Python sidecar.  Matches the port set in main.py and
/// GAIA_SIDECAR_PORT env var (default 52000).
const SIDECAR_BASE: &str = "http://127.0.0.1:52000";

// ── Managed state ──────────────────────────────────────────────────────────────

/// Shared HTTP client stored in Tauri's managed state.
/// Keeps the connection pool alive across all command calls.
pub struct SidecarClient(pub Client);

impl SidecarClient {
    pub fn new() -> Self {
        let client = Client::builder()
            .timeout(std::time::Duration::from_secs(30))
            .build()
            .expect("failed to build reqwest client");
        SidecarClient(client)
    }
}

// ── Shared error helper ────────────────────────────────────────────────────────

async fn sidecar_err(resp: reqwest::Response) -> String {
    let status = resp.status();
    let body = resp.text().await.unwrap_or_default();
    format!("sidecar returned {status}: {body}")
}

// ── /memory commands ───────────────────────────────────────────────────────────

/// Request body for `POST /memory/remember`
#[derive(Serialize)]
struct RememberRequest<'a> {
    principal_id: &'a str,
    content:      &'a str,
    role:         &'a str,  // "user" | "assistant" | "system"
}

/// Request body for `POST /memory/recall`
#[derive(Serialize)]
struct RecallRequest<'a> {
    principal_id: &'a str,
    query:        &'a str,
    limit:        u32,
}

/// Request body for `POST /memory/semantic`
#[derive(Serialize)]
struct SemanticRequest<'a> {
    principal_id: &'a str,
    pattern:      &'a str,
    evidence:     Vec<&'a str>,
}

/// Store a single chat turn in episodic memory.
///
/// Called after every message exchange in the GAIA chat loop.
#[tauri::command]
pub async fn memory_remember(
    state: tauri::State<'_, SidecarClient>,
    principal_id: String,
    content:      String,
    role:         String,
) -> Result<Value, String> {
    let body = RememberRequest {
        principal_id: &principal_id,
        content:      &content,
        role:         &role,
    };
    let resp = state
        .0
        .post(format!("{SIDECAR_BASE}/memory/remember"))
        .json(&body)
        .send()
        .await
        .map_err(|e| format!("memory_remember request failed: {e}"))?;

    if resp.status().is_success() {
        resp.json::<Value>().await.map_err(|e| e.to_string())
    } else {
        Err(sidecar_err(resp).await)
    }
}

/// Retrieve relevant memories to inject into GAIA's context window.
///
/// Called before building the prompt for each inference turn.
#[tauri::command]
pub async fn memory_recall(
    state:        tauri::State<'_, SidecarClient>,
    principal_id: String,
    query:        String,
    limit:        Option<u32>,
) -> Result<Value, String> {
    let body = RecallRequest {
        principal_id: &principal_id,
        query:        &query,
        limit:        limit.unwrap_or(5),
    };
    let resp = state
        .0
        .post(format!("{SIDECAR_BASE}/memory/recall"))
        .json(&body)
        .send()
        .await
        .map_err(|e| format!("memory_recall request failed: {e}"))?;

    if resp.status().is_success() {
        resp.json::<Value>().await.map_err(|e| e.to_string())
    } else {
        Err(sidecar_err(resp).await)
    }
}

/// Distil a semantic pattern from episodic evidence.
#[tauri::command]
pub async fn memory_semantic(
    state:        tauri::State<'_, SidecarClient>,
    principal_id: String,
    pattern:      String,
    evidence:     Vec<String>,
) -> Result<Value, String> {
    let evidence_refs: Vec<&str> = evidence.iter().map(String::as_str).collect();
    let body = SemanticRequest {
        principal_id: &principal_id,
        pattern:      &pattern,
        evidence:     evidence_refs,
    };
    let resp = state
        .0
        .post(format!("{SIDECAR_BASE}/memory/semantic"))
        .json(&body)
        .send()
        .await
        .map_err(|e| format!("memory_semantic request failed: {e}"))?;

    if resp.status().is_success() {
        resp.json::<Value>().await.map_err(|e| e.to_string())
    } else {
        Err(sidecar_err(resp).await)
    }
}

/// Return the current DEK ring + master key health status.
#[tauri::command]
pub async fn memory_key_status(
    state: tauri::State<'_, SidecarClient>,
) -> Result<Value, String> {
    let resp = state
        .0
        .get(format!("{SIDECAR_BASE}/memory/key-status"))
        .send()
        .await
        .map_err(|e| format!("memory_key_status request failed: {e}"))?;

    if resp.status().is_success() {
        resp.json::<Value>().await.map_err(|e| e.to_string())
    } else {
        Err(sidecar_err(resp).await)
    }
}

/// Trigger a forward DEK rotation.
#[tauri::command]
pub async fn memory_key_rotate(
    state: tauri::State<'_, SidecarClient>,
) -> Result<Value, String> {
    let resp = state
        .0
        .post(format!("{SIDECAR_BASE}/memory/key-rotate"))
        .send()
        .await
        .map_err(|e| format!("memory_key_rotate request failed: {e}"))?;

    if resp.status().is_success() {
        resp.json::<Value>().await.map_err(|e| e.to_string())
    } else {
        Err(sidecar_err(resp).await)
    }
}

// ── /affect commands ───────────────────────────────────────────────────────────

/// Request body for `POST /affect/analyze`
#[derive(Serialize)]
struct AffectAnalyzeRequest<'a> {
    principal_id: &'a str,
    text:         &'a str,
    source:       &'a str,  // "gaia_chat" | "journal" | "system"
    persist:      bool,
}

/// Run affect inference on a text block and optionally persist the snapshot.
#[tauri::command]
pub async fn affect_analyze(
    state:        tauri::State<'_, SidecarClient>,
    principal_id: String,
    text:         String,
    source:       Option<String>,
    persist:      Option<bool>,
) -> Result<Value, String> {
    let body = AffectAnalyzeRequest {
        principal_id: &principal_id,
        text:         &text,
        source:       source.as_deref().unwrap_or("gaia_chat"),
        persist:      persist.unwrap_or(true),
    };
    let resp = state
        .0
        .post(format!("{SIDECAR_BASE}/affect/analyze"))
        .json(&body)
        .send()
        .await
        .map_err(|e| format!("affect_analyze request failed: {e}"))?;

    if resp.status().is_success() {
        resp.json::<Value>().await.map_err(|e| e.to_string())
    } else {
        Err(sidecar_err(resp).await)
    }
}

/// Retrieve AffectSnapshot history for a principal (last N days).
#[tauri::command]
pub async fn affect_history(
    state:        tauri::State<'_, SidecarClient>,
    principal_id: String,
    days:         Option<u32>,
) -> Result<Value, String> {
    let days = days.unwrap_or(30);
    let resp = state
        .0
        .get(format!("{SIDECAR_BASE}/affect/history/{principal_id}"))
        .query(&[("days", days)])
        .send()
        .await
        .map_err(|e| format!("affect_history request failed: {e}"))?;

    if resp.status().is_success() {
        resp.json::<Value>().await.map_err(|e| e.to_string())
    } else {
        Err(sidecar_err(resp).await)
    }
}

/// Return the ArcTrend (valence momentum, volatility, direction) for a principal.
#[tauri::command]
pub async fn affect_trend(
    state:        tauri::State<'_, SidecarClient>,
    principal_id: String,
    days:         Option<u32>,
) -> Result<Value, String> {
    let days = days.unwrap_or(30);
    let resp = state
        .0
        .get(format!("{SIDECAR_BASE}/affect/trend/{principal_id}"))
        .query(&[("days", days)])
        .send()
        .await
        .map_err(|e| format!("affect_trend request failed: {e}"))?;

    if resp.status().is_success() {
        resp.json::<Value>().await.map_err(|e| e.to_string())
    } else {
        Err(sidecar_err(resp).await)
    }
}

// ── /stage commands ────────────────────────────────────────────────────────────

/// Run a full Magnum Opus stage evaluation tick for a principal.
///
/// All signal fields are optional — pass only what is available.
/// The sidecar fills defaults for missing fields.
#[tauri::command]
pub async fn stage_evaluate(
    state:                   tauri::State<'_, SidecarClient>,
    principal_id:            String,
    goal_states:             Option<Vec<String>>,
    hrv_rmssd_history:       Option<Vec<f64>>,
    alignment_score_history: Option<Vec<f64>>,
    journal_entries:         Option<Vec<Value>>,
    focus_session_minutes:   Option<Vec<f64>>,
    goals_completed:         Option<u32>,
    goals_abandoned:         Option<u32>,
    valence_history:         Option<Vec<f64>>,
    schumann_state:          Option<Value>,
) -> Result<Value, String> {
    // Build a serde_json::Value payload — all optional fields
    let mut body = serde_json::json!({
        "principal_id": principal_id,
        "goal_states":              goal_states.unwrap_or_default(),
        "hrv_rmssd_history":        hrv_rmssd_history.unwrap_or_default(),
        "alignment_score_history":  alignment_score_history.unwrap_or_default(),
        "journal_entries":          journal_entries.unwrap_or_default(),
        "focus_session_minutes":    focus_session_minutes.unwrap_or_default(),
        "goals_completed":          goals_completed.unwrap_or(0),
        "goals_abandoned":          goals_abandoned.unwrap_or(0),
        "valence_history":          valence_history.unwrap_or_default(),
    });

    if let Some(ss) = schumann_state {
        body["schumann_state"] = ss;
    }

    let resp = state
        .0
        .post(format!("{SIDECAR_BASE}/stage/evaluate"))
        .json(&body)
        .send()
        .await
        .map_err(|e| format!("stage_evaluate request failed: {e}"))?;

    if resp.status().is_success() {
        resp.json::<Value>().await.map_err(|e| e.to_string())
    } else {
        Err(sidecar_err(resp).await)
    }
}

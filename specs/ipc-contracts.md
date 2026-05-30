# GAIA-OS IPC Contract Specification

> **Canonical reference** for all inter-process data contracts across the Rust ↔ Python ↔ TypeScript boundary.
> Generated from live source audit — `src-tauri/src/lib.rs`, `src-tauri/src/memory.rs`,
> `src-tauri/src/schumann.rs`, and all files in `core/routers/`.
>
> **Last audited:** 2026-05-30
> **Auditor:** GAIA-OS automated contract pass (Issue #101)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  TypeScript Frontend  (src/)                                        │
│  Tauri invoke() ──────────────────────────────────────────────────► │
│                          Rust / Tauri (src-tauri/)                  │
│  ◄── Tauri events ────────────────────────────────────────────────  │
│                                    │                                │
│                   HTTP proxy       │      Direct HTTP               │
│                   :52000           ▼      :8009 (IPC bridge)        │
│                  Python FastAPI sidecar (core/)                     │
│                  POST :8009/emit ──────────────────► Tauri events   │
└─────────────────────────────────────────────────────────────────────┘
```

**Three runtimes. Four communication channels:**

| Channel | Direction | Transport | Port |
|---|---|---|---|
| Tauri `invoke()` | TS → Rust | IPC | — |
| Tauri events | Rust → TS | IPC | — |
| Sidecar HTTP proxy | Rust → Python | HTTP/JSON | 52000 |
| IPC bridge | Python → Rust → TS | HTTP → event | 8009 |

---

## Part 1 — Tauri Commands (Rust ↔ TypeScript)

All commands are exposed via `tauri::generate_handler![]` in `src-tauri/src/lib.rs`.

### 1.1 Core App Commands

#### `greet`
```
Args:    name: string
Returns: string  ("Hello, {name}! You've been greeted from GAIA!")
Source:  lib.rs
```

#### `get_backend_status`
```
Args:    —
Returns: string  ("online")
Source:  lib.rs
```

#### `restart_backend`
```
Args:    —
Returns: Result<string, string>  ("restarted" | error message)
Source:  lib.rs
Effect:  kills sidecar, relaunches gaia-backend binary
```

#### `open_log_dir`
```
Args:    —
Returns: Result<void, string>
Source:  lib.rs
Effect:  opens app_data_dir/logs in OS file manager
```

#### `load_ambient_position`
```
Args:    —
Returns: Result<string, string>  (JSON string from ambient-position.json, or "" if absent)
Source:  lib.rs
```

#### `navigate_main`
```
Args:    section: string
Returns: Result<void, string>
Source:  lib.rs
Effect:  emits "navigate" event with { section } to main window, shows + focuses window
```

#### `quit_app`
```
Args:    —
Returns: void
Source:  lib.rs
Effect:  kills sidecar, calls app.exit(0)
```

---

### 1.2 Schumann Commands (`src-tauri/src/schumann.rs`)

#### `get_alignment_state`
```
Args:    —
Returns: Result<Value, String>  (JSON — Schumann resonance alignment snapshot)
Source:  schumann.rs → GET :52000/schumann/state (or local computation)
```

---

### 1.3 Soul Mirror Bridge Commands (`src-tauri/src/memory.rs`)

All commands are thin async proxies to `http://127.0.0.1:52000`. No business logic.

#### `memory_remember`
```
Args:
  principal_id: string
  content:      string
  role:         "user" | "assistant" | "system"

Returns: Result<Value, String>

Sidecar:  POST /memory/remember
Body:     { principal_id, content, role }
```

#### `memory_recall`
```
Args:
  principal_id: string
  query:        string
  limit?:       number  (default: 5)

Returns: Result<Value, String>  (array of memory entries)

Sidecar:  POST /memory/recall
Body:     { principal_id, query, limit }
```

#### `memory_semantic`
```
Args:
  principal_id: string
  pattern:      string
  evidence:     string[]

Returns: Result<Value, String>

Sidecar:  POST /memory/semantic
Body:     { principal_id, pattern, evidence }
```

#### `memory_key_status`
```
Args:    —
Returns: Result<Value, String>  (DEK ring + master key health)

Sidecar:  GET /memory/key-status
```

#### `memory_key_rotate`
```
Args:    —
Returns: Result<Value, String>

Sidecar:  POST /memory/key-rotate
```

#### `affect_analyze`
```
Args:
  principal_id: string
  text:         string
  source?:      "gaia_chat" | "journal" | "system"  (default: "gaia_chat")
  persist?:     boolean  (default: true)

Returns: Result<Value, String>  (AffectSnapshot)

Sidecar:  POST /affect/analyze
Body:     { principal_id, text, source, persist }
```

#### `affect_history`
```
Args:
  principal_id: string
  days?:        number  (default: 30)

Returns: Result<Value, String>  (array of AffectSnapshot)

Sidecar:  GET /affect/history/{principal_id}?days={days}
```

#### `affect_trend`
```
Args:
  principal_id: string
  days?:        number  (default: 30)

Returns: Result<Value, String>  (ArcTrend: valence_momentum, volatility, direction)

Sidecar:  GET /affect/trend/{principal_id}?days={days}
```

#### `stage_evaluate`
```
Args:
  principal_id:             string
  goal_states?:             string[]
  hrv_rmssd_history?:       number[]
  alignment_score_history?: number[]
  journal_entries?:         object[]
  focus_session_minutes?:   number[]
  goals_completed?:         number
  goals_abandoned?:         number
  valence_history?:         number[]
  schumann_state?:          object

Returns: Result<Value, String>  (Magnum Opus stage evaluation result)

Sidecar:  POST /stage/evaluate
Body:     all fields as JSON, missing fields default to [] / 0
```

---

## Part 2 — Tauri Events (Rust → TypeScript)

Events emitted by Rust to the `main` WebView window. TypeScript frontend listens via `listen()`.

| Event | Payload | Trigger |
|---|---|---|
| `sidecar:ready` | `()` | Python health check passes after boot |
| `sidecar:error` | `{ reason: string }` | Sidecar binary not found, spawn fail, health timeout |
| `navigate` | `{ section: string }` | `navigate_main` command or tray menu |

---

## Part 3 — IPC Bridge (Python → Rust → TypeScript)

**Python backend → Rust bridge → Tauri event → TypeScript frontend**

The IPC bridge listens on `127.0.0.1:8009` (loopback only). Python POSTs to it to push events to the WebView without polling.

#### `POST :8009/emit`
```
Body:    { event: string, payload: any }
Returns: 200 "ok" | 500 "emit failed"

Python calls this to emit any Tauri event to the frontend.
Common events pushed via this channel:
  - "mood:update"       — affect engine pushed a new mood snapshot
  - "memory:stored"     — episodic memory write confirmed
  - "canon:reload"      — canon document set changed
  - "gaian:state"       — Gaian identity state broadcast
```

**Notification flow:**
```
Python core/routers/* ──► POST :8009/emit ──► Rust axum handler
                                               ──► app_handle.emit(event, payload)
                                                   ──► TypeScript listen(event, cb)
```

---

## Part 4 — Python API Endpoints (core/routers/)

All Python endpoints are served on `http://127.0.0.1:52000` (GAIA_SIDECAR_PORT).
The external CORS-accessible server runs on port 8008.

### Router Index

| Router file | Prefix | Description |
|---|---|---|
| `auth_users.py` | `/auth` | Register, login, me |
| `auth.py` (legacy) | `/auth` | Token bootstrap for dev/admin |
| `health.py` | `/health` | Liveness + readiness probes |
| `internal_router.py` | `/internal` | Rust → Python signals (loopback) |
| `system.py` | `/system` | System info, version, config |
| `gaians.py` | `/gaians` | Gaian CRUD |
| `chat.py` | `/chat` | Chat turns, streaming inference |
| `memory.py` | `/memory` | SovereignMemory CRUD |
| `zodiac.py` | `/zodiac` | Zodiac / planetary data |
| `query.py` | `/query` | Direct LLM query (no session) |
| `admin.py` | `/admin` | Admin operations |
| `mood_ws.py` | `/mood` | WebSocket mood stream |
| `room.py` | `/room` | Conversation rooms |
| `goals_router.py` | `/goals` | Goals CRUD + Spiritus birth-stamping |
| `action_gate_router.py` | `/action-gate` | Risk-tier veto (GREEN/YELLOW/RED) |

### 4.1 Auth

#### `POST /auth/register`
```
Body:    { username: string, password: string, email?: string }
Returns: { id: string, username: string, token: string }
```

#### `POST /auth/login`
```
Body:    { username: string, password: string }
Returns: { token: string, token_type: "bearer" }
```

#### `GET /auth/me`
```
Headers: Authorization: Bearer <token>
Returns: { id: string, username: string, email?: string, created_at: string }
```

#### `POST /auth/token` (legacy dev bootstrap)
```
Body:    form-encoded { username, password }
Returns: { access_token: string, token_type: "bearer" }
```

---

### 4.2 Health

#### `GET /health`
```
Returns: { status: "ok", version: string, uptime_s: number }
```

#### `GET /health/ready`
```
Returns: { ready: boolean, checks: { [subsystem: string]: boolean } }
```

---

### 4.3 Internal (Rust → Python, loopback only)

#### `POST /internal/ipc-ready`
```
Body:    {}
Returns: { ok: true }
Effect:  Python registers the IPC bridge URL for push notifications
```

---

### 4.4 Chat

#### `POST /chat`
```
Headers: Authorization: Bearer <token>
Body:
  {
    gaian_id:    string,
    room_id?:    string,
    message:     string,
    stream?:     boolean  (default: false)
  }
Returns (non-stream):
  {
    reply:       string,
    gaian_id:    string,
    room_id:     string,
    tokens_used: number,
    affect?:     AffectSnapshot
  }
Returns (stream): text/event-stream SSE chunks
```

---

### 4.5 Memory

#### `POST /memory/remember`
```
Body:    { principal_id: string, content: string, role: string }
Returns: { id: string, stored_at: string }
```

#### `POST /memory/recall`
```
Body:    { principal_id: string, query: string, limit: number }
Returns: { memories: MemoryEntry[], count: number }
```

#### `POST /memory/semantic`
```
Body:    { principal_id: string, pattern: string, evidence: string[] }
Returns: { pattern_id: string, distilled_at: string }
```

#### `GET /memory/key-status`
```
Returns: { dek_ring_size: number, master_key_healthy: boolean, last_rotation: string }
```

#### `POST /memory/key-rotate`
```
Returns: { rotated: true, new_dek_id: string }
```

---

### 4.6 Goals (`/goals`)

Full CRUD with Spiritus birth-stamping. Prefix: `/goals`.

#### `POST /goals`
```
Body:    { title: string, description?: string, gaian_id?: string }
Returns: GoalObject (see schema below)
```

#### `GET /goals`
```
Query:   ?gaian_id=<id>&status=open|closed|all
Returns: { goals: GoalObject[], total: number }
```

#### `GET /goals/{id}`
```
Returns: GoalObject
```

#### `PATCH /goals/{id}`
```
Body:    Partial<GoalObject>
Returns: GoalObject
```

#### `DELETE /goals/{id}`
```
Returns: { deleted: true, id: string }
```

**GoalObject schema:**
```json
{
  "id":           "string (uuid)",
  "title":        "string",
  "description":  "string | null",
  "status":       "open | in_progress | closed | abandoned",
  "gaian_id":     "string | null",
  "spiritus_id":  "string | null",
  "created_at":   "ISO 8601",
  "updated_at":   "ISO 8601"
}
```

---

### 4.7 Action Gate (`/action-gate`)

#### `POST /action-gate/evaluate`
```
Body:
  {
    action:      string,
    context:     object,
    principal?:  string
  }
Returns:
  {
    tier:        "GREEN" | "YELLOW" | "RED",
    verdict:     "allow" | "hold" | "veto",
    reason:      string,
    audit_id:    string
  }
```

---

### 4.8 Mood WebSocket (`/mood`)

#### `WS /mood/stream`
```
On connect:  { type: "connected", gaian_id: string }
Server push: { type: "snapshot", affect: AffectSnapshot, timestamp: string }
Client msg:  { type: "ping" }
Server:      { type: "pong" }
```

---

## Part 5 — Validation Status

Current enforcement state per boundary:

| Boundary | Contract Defined | Runtime Validation | Schema File |
|---|---|---|---|
| TS → Rust `invoke()` | ✅ This doc | ⚠️ Tauri type inference only | — |
| Rust → Python HTTP | ✅ This doc | ⚠️ `serde_json::Value` (untyped) | — |
| Python response shapes | ✅ Partially (Pydantic in some routers) | ⚠️ Incomplete across all routers | — |
| Python → Rust IPC bridge | ✅ This doc | ❌ No validation on emit payload | — |
| `schema/body_matrix.json` | ✅ Existing | ✅ Validated | `schema/body_matrix.json` |

---

## Part 6 — Open Enforcement Tasks

These tasks remain from Issue #101 and should be tracked as sub-issues or follow-on work:

1. **`schema/api/`** — Add JSON Schema files for every Python endpoint response (`GoalObject`, `AffectSnapshot`, `MemoryEntry`, `ChatReply`, `AlignmentState`).
2. **Pydantic response models** — Ensure every router returns a typed Pydantic model, not a bare `dict`. Routers requiring audit: `chat.py` (25 KB), `gaians.py`, `room.py`.
3. **TypeScript type guards** — Generate TS interfaces from the schemas above; add runtime guards in `src/` for all `invoke()` return values and IPC bridge events.
4. **Rust assertion tests** — Add `#[tokio::test]` fixtures in `memory.rs` and `schumann.rs` that verify sidecar response shapes against expected JSON structure.
5. **IPC bridge payload validation** — Add a schema registry to the bridge so unknown `event` names or malformed payloads return 400 instead of silently failing.

---

## Appendix — Type Glossary

| Type | Definition |
|---|---|
| `AffectSnapshot` | `{ valence: float, arousal: float, dominance: float, label: string, source: string, timestamp: ISO8601 }` |
| `ArcTrend` | `{ valence_momentum: float, volatility: float, direction: "rising" / "falling" / "stable" }` |
| `MemoryEntry` | `{ id: string, content: string, role: string, principal_id: string, created_at: ISO8601, relevance?: float }` |
| `AlignmentState` | `{ frequency_hz: float, amplitude: float, coherence: float, timestamp: ISO8601 }` |
| `GoalObject` | See §4.6 |
| `SidecarHandle` | Rust internal — `Arc<Mutex<Option<CommandChild>>>` |
| `SidecarClient` | Rust internal — managed `reqwest::Client` with 30 s timeout |

# AGENT_TELEMETRY_HUB_SPEC.md

> **Issue:** [#188 — Agent Telemetry Hub](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/188)  
> **Status:** Implemented — `sidecar/telemetry/`  
> **Canon refs:** C05 (Transparency), C30 (No silent failures), C01 (Sovereignty)  
> **Receives events from:** #155, #154, #150, #52, #187, #152, #153  
> **Feeds into:** #162 (Crystal audit nodes), Glass Room (#103), Dev Suite dashboards

---

## 1. Purpose

The Agent Telemetry Hub is GAIA-OS's unified observability plane. It creates a local, append-only, user-inspectable audit trail for every meaningful agentic action, fallback, and context change.

Its goals are:

1. **Transparency** — every agentic step can be inspected later.
2. **Trust** — users can see what happened, why it happened, and what fallback paths fired.
3. **Optimization** — DQ and OE trends become measurable across time.
4. **Sovereignty** — telemetry never leaves the device unless the user explicitly exports it.

---

## 2. Core Data Model

### `TelemetryEvent`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID |
| `timestamp` | `datetime` | UTC event time |
| `session_id` | `str` | GAIA session identifier |
| `source` | `str` | `synergy_orchestrator` \| `sandbox` \| `skill` \| `healing` \| `biometric` \| `planetary` |
| `event_type` | `str` | `job_started` \| `job_completed` \| `job_failed` \| `fallback_used` \| `circuit_broken` \| `action_gate_triggered` \| `skill_invoked` \| `context_change` |
| `skill_id` | `str \| None` | Engine or skill identity |
| `trust_tier` | `str \| None` | Skill Trust label |
| `intent_class` | `str \| None` | Synergy intent class |
| `risk_tier` | `str \| None` | Action Gate risk tier |
| `input_summary` | `str` | Non-sensitive input summary |
| `output_summary` | `str` | Non-sensitive output summary |
| `duration_ms` | `int` | Duration in milliseconds |
| `dq_score` | `float \| None` | DecisionQuality score |
| `degraded` | `bool` | Whether fallback was used |
| `fallback_mode` | `str \| None` | Fallback mode if degraded |
| `biometric_context` | `str \| None` | Current coherence label |
| `planetary_context` | `str \| None` | Current planetary label |
| `canon_refs` | `list[str]` | Governing canon references |
| `tags` | `list[str]` | Extra indexing tags |

---

## 3. Collector Responsibilities

`TelemetryCollector` does four things for every event:

1. Inserts the event into a local append-only SQLite store.
2. Streams the event to the Glass Room UI callback, if configured.
3. Routes high-value events to Crystal indexing, if configured.
4. Exposes query APIs for traces, skill health, DQ history, OE windows, export, and deletion.

### Append-only store

The table schema is intentionally insert-only at runtime. Events are never mutated after insertion. User deletion is performed only through explicit right-to-erasure workflows.

### Crystal indexing policy

An event is considered high-value if:
- `risk_tier in ("YELLOW", "RED")`, or
- `degraded == True`

---

## 4. Query Surfaces

### `get_session_trace(session_id)`
Returns the full time-ordered list of telemetry events for a session.

### `get_skill_health(skill_id, window_min=60)`
Returns:
- error rate,
- average latency,
- degraded count,
- inferred circuit state,
- last failure timestamp.

### `get_dq_history(limit=100)`
Returns recent events with `dq_score != None` for longitudinal trending.

### `get_oe_window(window)`
Supported windows:
- `24h`
- `7d`
- `30d`

The OE metric is currently computed as:

`oe_score = success_rate / avg_task_duration_s`

where success is defined as a completed orchestration task that did **not** degrade.

---

## 5. Orchestration Efficiency

### `OrchestrationEfficiency`

| Field | Meaning |
|-------|---------|
| `successful_tasks` | Completed non-degraded orchestration tasks |
| `total_tasks` | All completed orchestration tasks |
| `avg_task_duration_s` | Mean duration across completed orchestration tasks |
| `avg_dq_score` | Mean DQ score where available |
| `degraded_task_fraction` | Fraction of tasks using fallbacks |
| `oe_score` | `success_rate / avg_task_duration_s` |

This keeps OE complementary to DQ:
- DQ measures quality,
- OE measures throughput efficiency under real system conditions.

---

## 6. Privacy Model

The Telemetry Hub follows strict privacy rules:

- Only summaries are stored — never raw conversation text, raw files, or raw biometric data.
- Biometric labels may be stored, but raw sensor values remain inside the Biometric Engine.
- Telemetry is local-only.
- User can export session traces as JSON.
- User can delete telemetry by time range.

---

## 7. Test Coverage

### Files

| File | Coverage |
|------|----------|
| `tests/test_telemetry_collector.py` | emit, traces, skill health, DQ history, OE windows, export/delete |
| `tests/test_orchestration_efficiency.py` | OE score computation |

### Minimum guarantees

- Event insertions succeed for all valid `TelemetryEvent`s.
- Session traces return events in chronological order.
- Skill health windows calculate error rate and circuit-state inference correctly.
- OE windows compute task totals, degraded fraction, and composite score correctly.
- Export returns valid JSON.
- Delete range removes matching rows only.

---

## 8. Remaining Work

- [ ] Wire emit points into #155, #154, #150, #52, #152, #153.
- [ ] Add real-time Glass Room panel in TypeScript.
- [ ] Add Crystal index callback implementation once audit node schema is finalized in #162.
- [ ] Add DQ/OE chart rendering in Glass Room / Dev Suite.
- [ ] Expand OE formula with explicit energy-cost weighting once system metrics exist.

---

## 9. Changelog

| Date | Change |
|------|--------|
| 2026-06-03 | Initial implementation of `sidecar/telemetry/`, tests, and telemetry spec |

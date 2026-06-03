# Self-Healing Workflow Engine — Specification

**Issue:** #187  
**Status:** Implementation Complete  
**Canon:** C30 (No Silent Failures) · C01 (Sovereignty) · C34 (Presence)  
**Sprint:** 2 · Tier 1 — Orchestration Core  

---

## Overview

The Self-Healing Workflow Engine provides a three-layer resilience wrapper around every Synergy Orchestrator job:

1. **RetryPolicy** — per-skill retry configuration with exponential, fixed, or jitter backoff
2. **CircuitBreaker** — CLOSED → OPEN → HALF_OPEN state machine that auto-isolates failing skills
3. **SelfHealingEngine** — orchestrates both layers, applies `DegradedFallback` when all retries are exhausted, and emits telemetry events to the Agent Telemetry Hub (Issue #188)

Without this layer, any transient failure in a single engine (e.g., a network timeout in Research Desk) can abort an entire Deep Work session — a violation of Canon C30 and a direct degradation of user trust.

---

## Architecture

### RetryPolicy

```
src-python/resilience/retry_policy.py
```

- `max_attempts: int` — default 3
- `backoff_strategy: BackoffStrategy` — `FIXED | EXPONENTIAL | JITTER`
- `base_delay_ms / max_delay_ms` — delay bounds
- `retryable_errors` — TimeoutError, ConnectionError, ServiceUnavailable
- `non_retryable_errors` — AuthError, PolicyViolation, SandboxEscape (never retried)
- Per-skill overrides in `SKILL_RETRY_POLICIES` dict

### CircuitBreaker

```
src-python/resilience/circuit_breaker.py
```

State transitions:

```
CLOSED ──(failure_rate ≥ threshold)──► OPEN ──(open_duration elapsed)──► HALF_OPEN
                                                                              │
                                                              success ──► CLOSED
                                                              failure ──► OPEN
```

- Rolling `window_seconds` (default 60s) tracks call and failure times
- `min_calls_in_window` (default 4) prevents premature tripping on sparse traffic
- `.health` property exposes circuit state for Agent Telemetry Hub dashboard

### DegradedFallbacks

```
src-python/resilience/degraded_fallbacks.py
```

| Skill | Mode | DQ Multiplier |
|-------|------|---------------|
| `planetary_signal_hub` | CACHED (15 min) | 0.85 |
| `article_loader` | MANUAL_INPUT | 0.90 |
| `crystal_graphrag` | DOWNGRADE (vector only) | 0.70 |
| `biometric_coherence` | AFFECTIVE_ONLY | 0.80 |
| `soul_mirror` | SKIP | 0.75 |
| `dev_suite_executor` | STATIC_RESPONSE | 0.00 |
| `dream_weaver` | SKIP | 0.90 |

Every fallback carries a `user_message` — Canon C30 compliance is enforced in tests.

### SelfHealingEngine

```
src-python/resilience/self_healing_engine.py
```

Execution path for `execute_with_healing(skill_id, fn, *args, fallback=None)`:

```
1. Lookup RetryPolicy + CircuitBreaker for skill_id
2. For attempt in 1..max_attempts:
   a. CircuitBreaker.call(fn)
   b. On success → return HealingResult(degraded=False)
   c. On CircuitOpenError → break to fallback
   d. On retryable error + attempts remaining → sleep(backoff) + continue
   e. On non-retryable error → raise NonRetryableError immediately
3. Apply DegradedFallback if available → return HealingResult(degraded=True)
4. No fallback → raise WorkflowFailure
```

`HealingResult` carries:
- `degraded: bool`
- `fallback_used: str | None`
- `dq_confidence_multiplier: float` — applied to DecisionQuality in OrchestratorV2
- `user_message: str | None` — surfaced in degradation indicator UI

---

## Integration with OrchestratorV2 (Issue #155)

```python
# In OrchestratorV2.orchestrate():
results = await asyncio.gather(*[
    self.healing_engine.execute_with_healing(
        skill_id=job.engine,
        fn=self._run_job_fn(job),
    )
    for job in parallel_jobs
])

for r in results:
    if r.degraded:
        dq.confidence *= r.dq_confidence_multiplier
        dq.degradation_reason = r.fallback_used
```

---

## Integration with Agent Telemetry Hub (Issue #188)

Every call to `_emit()` sends a structured event:

```json
{
  "source": "self_healing_engine",
  "skill_id": "crystal_graphrag",
  "event_type": "fallback_used",
  "attempt": 3,
  "fallback_mode": "downgrade_to_vector",
  "duration_ms": 2341.5,
  "degraded": true
}
```

Telemetry is best-effort — a failure in `_emit()` never propagates to the healing engine.

---

## User-Facing Degradation UI

When `HealingResult.degraded == True` and `user_message` is set, the frontend renders:

```
┌─ GAIA Response ──────────────────────────────────────┐
│  Here are the memories related to your query...      │
│                                                      │
│  ⚠ Graph search unavailable (Crystal DB degraded).  │
│  Results use semantic similarity only — relationship │
│  context excluded.                                   │
│  [Retry with full graph →]                           │
└──────────────────────────────────────────────────────┘
```

GAIA never silently degrades. Every fallback is surfaced with context and a retry option (Canon C30 + C01).

---

## Testing

```
src-python/tests/test_resilience.py
```

Suite covers:
- RetryPolicy backoff (fixed, exponential, jitter, max_delay cap)
- CircuitBreaker all state transitions
- SelfHealingEngine: success, retry-then-success, exhausted+fallback, no-fallback WorkflowFailure
- NonRetryableError propagation
- DQ confidence multiplier correctness
- Canon C30: all DEGRADED_FALLBACKS have `user_message`

Run: `pytest src-python/tests/test_resilience.py -v`

---

## Canon Compliance

| Canon | Requirement | Implementation |
|-------|-------------|----------------|
| C30 | No silent failures | Every fallback carries `user_message`; all telemetry events emitted |
| C01 | Sovereignty | `[Retry →]` always available; non-retryable errors surface immediately |
| C34 | Presence | GAIA remains functional in degraded state; degradation is acknowledged, not hidden |

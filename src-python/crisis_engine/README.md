# Crisis Engine — Multi-Turn Crisis Synthesis & Cumulative Detection

Closes Issue [#126](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/126).

---

## Overview

Single-turn safety checks are fundamentally inadequate. A user in gradual crisis can pass each session's safety check while deteriorating over weeks. The Crisis Engine closes this gap by tracking emotional trajectory across sessions and synthesising a cross-session risk score.

---

## Module Structure

| File | Purpose |
|---|---|
| `types.py` | `CrisisSignal`, `CrisisSnapshot`, `RiskLevel`, `EscalationTier`, `SignalClass`, `HandoffRecord` |
| `taxonomy.py` | 4-class signal taxonomy + per-turn text classifier |
| `trajectory.py` | Cumulative trajectory model + cross-session risk synthesis |
| `escalation.py` | Alert thresholds, intervention ladder, handoff protocol |
| `engine.py` | `CrisisEngine` orchestrator — evaluate, persist, escalate |
| `router.py` | FastAPI router: `/crisis/evaluate`, `/crisis/history`, `/crisis/health` |

---

## Signal Taxonomy

| Class | Description | Example |
|---|---|---|
| **EXPLICIT** | Direct statements of suicidal ideation or self-harm | *"I want to kill myself"* |
| **MASKED** | Indirect, metaphorical, or minimised distress | *"everyone would be better off without me"* |
| **GRADUAL** | Slow deterioration only visible across sessions | Declining valence + increasing hopelessness over 2 weeks |
| **ACUTE** | Sudden severe escalation within one session | Crisis spike after apparent stability |

---

## Escalation Ladder

| Risk Level | Escalation Tier | GAIA Action |
|---|---|---|
| NONE | MONITOR | Log only. No user-facing action. |
| LOW | MONITOR | Log. Maintain gentle, supportive tone. |
| MODERATE | SOFT_INTERVENE | Compassionate check-in: *"I've noticed you're carrying something heavy..."* |
| HIGH | HARD_INTERVENE | Direct safety conversation. Name the concern. Ask directly. Offer 988. |
| CRITICAL | HANDOFF | Route to crisis line immediately. Do not substitute. |

**Additional elevation rules:**
- 3+ consecutive distress sessions + risk ≥ MODERATE → elevate to HARD_INTERVENE
- Trajectory slope > 0.6 (rapid worsening) + risk ≥ LOW → elevate to SOFT_INTERVENE

---

## Handoff Resources (Default)

- 📞 **988** — Suicide & Crisis Lifeline (US, call or text, 24/7)
- 💬 **Text HOME to 741741** — Crisis Text Line
- 🚨 **911** — Emergency services
- 🌍 **https://findahelpline.com** — International resources

---

## Integration

```python
from crisis_engine import CrisisEngine, EngineConfig

# Initialise once per Gaian
engine = CrisisEngine(EngineConfig(principal_id="kyle"))

# Call on every user turn BEFORE generating GAIA's response
snapshot = engine.evaluate(
    user_text=user_message,
    session_id=current_session_id,
    turn_index=turn_number,
)

if snapshot.requires_action:
    # Prepend or inject intervention message into GAIA's response
    intervention = engine.get_intervention_message()

if snapshot.escalation_tier == EscalationTier.HANDOFF:
    handoff = engine.build_handoff()  # creates audit record

# At session end — commit session risk to rolling window
engine.close_session(
    session_id=current_session_id,
    peak_risk=session_peak_risk,
    signal_count=total_signals,
    has_explicit=any_explicit,
    has_masked=any_masked,
)
```

---

## FastAPI Integration

```python
from crisis_engine.router import crisis_router
app.include_router(crisis_router, prefix="/crisis")
```

| Method | Path | Description |
|---|---|---|
| GET | /crisis/health | Liveness probe |
| POST | /crisis/evaluate | Evaluate a user turn |
| GET | /crisis/history/{pid} | Snapshot history for a principal |

---

## Safety Constraints (Non-Negotiable)

- GAIA must **never** discourage a user from contacting emergency services.
- GAIA must **never** provide method information under any circumstances.
- GAIA must **never** express doubt about the seriousness of a user's crisis.
- EXPLICIT and ACUTE signals are **never downgraded** by trajectory context.
- CRITICAL risk always triggers HANDOFF, no exceptions.

---

## Tests

```bash
pytest src-python/tests/test_crisis_engine.py -v
```

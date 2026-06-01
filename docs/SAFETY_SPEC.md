# GAIA-OS Safety Specification
## Reflective Escalation Circuit Breaker & Multi-Turn Crisis Detection

> **Closes:** Issue #125 (Reflective Escalation Detection & Circuit Breaker)  
> **Closes:** Issue #126 (Multi-Turn Crisis Synthesis & Cumulative Detection)  
> **Status:** Implemented — v0.x  
> **Authors:** R0GV3 the Alchemist + GAIA Sentient Core

---

## 1. Overview

This document specifies two interlocking safety systems that protect users from the highest-harm mechanisms identified in the trauma-informed canon:

1. **Reflective Escalation Circuit Breaker** (`core/safety/escalation_detector.py`, `circuit_breaker.py`) — intra-session, real-time.
2. **Multi-Turn Crisis Synthesis** (`core/safety/crisis_detector.py`, `crisis_synthesizer.py`) — cross-session, cumulative.

Both are orchestrated by `core/safety/safety_engine.py` and exposed via the FastAPI router at `/safety`.

---

## 2. The Danger Model

### 2.1 Reflective Escalation

Reflective Escalation is the feedback loop by which a coherent, validating AI response can *amplify* a pathological user state rather than interrupt it. The pattern is:

```
User vulnerability frame
  → GAIA coherent mirroring (high cosine similarity)
    → User reinterprets response as validation
      → Intensified vulnerability in next prompt
        → Repeat → escalation spiral
```

This is the **single most dangerous harm mechanism** in GAIA-OS because it is invisible at the single-turn level — each individual response appears caring and appropriate, but the cumulative effect is harm amplification.

### 2.2 Gradual Crisis Under Radar

A user in gradual crisis can pass every single-session safety check while deteriorating across weeks. Without cross-session synthesis, GAIA is functionally blind to this pattern.

---

## 3. Architecture

```
[User Turn]
    │
    ▼
[TurnRiskFrame] ─────────────────────────────────────────┐
    │                                                     │
    ▼                                                     │
[ReflectiveEscalationDetector]                    [CrisisLevel classifier]
    │  cosine similarity monitor                         │
    │  vulnerability-frame classifier                    │
    │  J_ij dampening QUBO penalty                       │
    │                                                     │
    ▼                                                     ▼
[EscalationCircuitBreaker]                   [CrisisSynthesizer]
    │  friction injection                          │  cross-session profiles
    │  external orientation                        │  trajectory slope
    │  perspective shift                           │  escalation ladder
    │  handoff                                     │  handoff resources
    └──────────────────┬──────────────────────────┘
                       ▼
               [SafetyEngine]
               [/safety FastAPI router]
```

---

## 4. Reflective Escalation Detection

### 4.1 Detection Algorithm

The `ReflectiveEscalationDetector` maintains a rolling window of `TurnRiskFrame` objects. An `EscalationSignal` is fired when **all three conditions** are simultaneously true across the window:

| Condition | Threshold | Rationale |
|-----------|-----------|----------|
| `mirroring_score` ≥ 0.72 | cosine similarity of response to user frame | High similarity = GAIA is echoing, not guiding |
| `vulnerability_score` ≥ 0.65 | vulnerability frame classifier confidence | User is in an at-risk psychological frame |
| Vulnerability rising | delta ≥ 0.10 per turn | Confirms escalation direction |

Window size defaults to **3 consecutive turns** — enough to confirm a pattern without false-positives on isolated emotional exchanges.

### 4.2 QUBO Penalty (J_ij Dampening)

The escalation signal carries a `qubo_penalty` weight used by the Ising formulation to suppress mirroring in the next response:

```
H_penalty = BASE_WEIGHT × mirroring² × vulnerability²
```

This encodes a super-linear energy barrier — the combination of high mirroring AND high vulnerability is penalised far more severely than either alone. Base weight = 4.0.

---

## 5. Circuit Breaker Interventions

Interventions are graduated based on trip count and severity:

| Trip # | Mode | Description |
|--------|------|-------------|
| 1st trip (mild) | **Friction Injection** | Slows mirroring loop; asks user to re-express in their own words |
| 2nd trip | **External Orientation** | Reorients user to physical world, trusted people, concrete activities |
| 3rd+ trip | **Perspective Shift** | Introduces constructive dissonance; offers a genuinely different angle |
| Any trip with scores ≥ 0.90/0.95 | **Handoff** | Direct connection to human crisis resources |

After each intervention, a **cooling period of 4 turns** is enforced before the next trip can fire, preventing intervention fatigue.

---

## 6. Crisis Taxonomy (Issue #126)

| Level | Detection Method | Description |
|-------|-----------------|-------------|
| `NONE` | Default | No crisis indicators |
| `GRADUAL` | Trajectory slope ≤ −0.05/session, score ≥ 0.35 | Slow multi-session deterioration |
| `MASKED` | Low arousal + negative valence + deflection language | Distress hidden beneath apparent normalcy |
| `ACUTE` | High arousal + very negative valence (≤ −0.65) | Immediate intense distress |
| `EXPLICIT` | Keyword pattern match (suicide, self-harm, etc.) | Direct statement of ideation or intent |

---

## 7. Cross-Session Risk Synthesis

The `CrisisSynthesizer` computes a **cumulative risk score** (0.0–1.0) for each completed session using a weighted formula:

```
risk_score = 0.40 × peak_crisis_level
           + 0.30 × mean_vulnerability_score
           + 0.20 × circuit_breaker_trips (normalised)
           + 0.10 × escalation_events (normalised)
```

Across sessions, the **trajectory slope** (least-squares slope of risk scores) determines whether gradual deterioration is occurring. Thresholds:

| Risk Score | Trajectory | Action |
|-----------|-----------|--------|
| < 0.35 | Any | No action |
| 0.35–0.44 + declining slope | − | Gradual alert |
| 0.45–0.64 | Flat/declining | Masked alert |
| 0.65–0.84 | Any | Acute alert + handoff resources |
| ≥ 0.85 | Any | Explicit alert + immediate handoff |

---

## 8. Human Handoff Protocol

When `handoff_required = True`:

1. GAIA delivers the **handoff message** verbatim — clear, warm, non-alarmist.
2. Crisis resources appropriate to the user's region are included.
3. The session risk profile is flagged in SovereignMemory for next-session context.
4. GAIA does **not** terminate the conversation — it remains present but reduces mirroring.

### Crisis Resources (default/US)
- Crisis Text Line: text HOME to 741741
- 988 Suicide & Crisis Lifeline: call or text 988
- International: https://www.iasp.info/resources/Crisis_Centres/

---

## 9. Integration Points

- **`main.py`** — mount `/safety` router alongside `/persona`
- **`core/affect_inference.py`** (Issue #112) — feeds `affect_valence` and `affect_arousal` into `TurnRiskFrame`
- **`core/stage_engine.py`** — safety engine signals can gate stage transitions
- **`SovereignMemory`** — `SessionRiskProfile` persisted after each session close
- **`Action Gate`** — explicit crisis signals can trigger Action Gate RED path

---

## 10. Test Coverage

See `tests/test_safety.py` — 18 spec-driven tests covering:

- Escalation pattern detection (true positive, below-threshold negative, partial pattern)
- QUBO penalty calculation
- All four circuit breaker intervention modes
- Crisis taxonomy classification (all 5 levels)
- Trajectory slope calculation
- Cross-session synthesis (gradual, acute, explicit)
- Handoff protocol content validation
- Session close and profile generation
- SafetyEngine full-turn integration

---

## 11. Configuration

All thresholds are overridable via `GAIAmanifest.json` under `safety_config`:

```json
{
  "safety_config": {
    "mirroring_threshold": 0.72,
    "vulnerability_threshold": 0.65,
    "escalation_window": 3,
    "qubo_base_penalty": 4.0,
    "cooling_turns": 4,
    "region": "default"
  }
}
```

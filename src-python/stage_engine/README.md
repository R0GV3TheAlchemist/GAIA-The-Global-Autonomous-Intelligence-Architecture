# GAIA-OS Stage Engine

Issue #63 | Pillar I: Magnum Opus

## Five Developmental Stages

| Stage | Name | Key Markers |
|-------|------|-------------|
| 1 | Divergence | High entropy, low HRV, shallow journaling |
| 2 | Awakening | Journaling depth rising, HRV trending up |
| 3 | Crucible | Shadow engagement, mixed valence arcs |
| 4 | Convergence | Values-behaviour alignment, stable HRV 60+ days |
| 5 | Ascendence | Mentorship documented, legacy artifacts created |

## Marker Scoring (all 0–100)

| Marker | Formula |
|--------|---------|
| `decision_entropy` | Shannon entropy over goal states, inverted |
| `hrv_coherence` | Personalised z-score sigmoid + Schumann alignment blend |
| `journaling_depth` | Weighted composite: length, lexical entropy, self-ref, emotion density |
| `focus_session_length_min` | Piecewise linear from raw minutes |
| `goal_completion_rate` | Bayesian-smoothed completion fraction |
| `emotional_arc_stability` | exp(-ασ) × (1 - β × zcr) |

## Transition Windows

| Transition | Min Window | Markers Required |
|------------|------------|------------------|
| 1 → 2 | 21 days | 4 of 6 |
| 2 → 3 | 30 days | 4 of 6 |
| 3 → 4 | 45 days | 4 of 6 |
| 4 → 5 | 60 days | 4 of 6 |

Regression: 5 of 6 prior-stage markers for 14+ consecutive days.
Labelled "Stage 3R" in the UI — framed as a season change, not failure.

## Example

```python
from sovereign_memory import SovereignMemory
from stage_engine import StageEngine

with SovereignMemory() as memory:
    engine = StageEngine(memory)
    result = engine.evaluate(
        principal_id="user-001",
        goal_states=["committed"] * 21,
        hrv_rmssd_history=[45.0] * 30,
        alignment_score_history=[60.0] * 30,
        journal_entries=[{"token_count": 400, "lexical_entropy": 0.6, "self_ref_ratio": 0.12, "emotion_density": 0.15}] * 14,
        focus_session_minutes=[28.0] * 14,
        goals_completed=8,
        goals_abandoned=2,
        valence_history=[0.2, 0.3, 0.1, 0.4, 0.2] * 6,
        days_forward_window_met=22,
    )
    print(result.record.stage_label)
    if result.transition:
        print("Transition fired:", result.transition.label)
```

## Follow-up work

- `shadow_engagement_flag` detection from journal semantic analysis
- `mentorship_behavior_flag` detection from episodic patterns
- `values_behavior_alignment` score from Shadow Engine
- Tauri IPC binding for frontend stage visualization
- Ceremony UI payload construction

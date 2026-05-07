"""
Test suite for core/shadow_engine.py
Spec: Issue #67 — Shadow Engine

8 tests covering:
  - RecurringThemeDetector
  - BehavioralLoopDetector
  - ContradictionDetector
  - ShadowTimingGate
"""

import pytest

from core.affect_inference import AffectState, FeelingState
from core.shadow_engine import (
    BehaviorLog,
    BehavioralLoopDetector,
    ContradictionDetector,
    RecurringThemeDetector,
    ShadowEngine,
    ShadowObservation,
    ShadowTimingGate,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _feeling(affect: AffectState = AffectState.RESONANCE) -> FeelingState:
    return FeelingState(affect_state=affect, conflict_density=0.1, coherence_phi=0.80)


# ---------------------------------------------------------------------------
# 1. RecurringThemeDetector — theme detected
# ---------------------------------------------------------------------------

def test_recurring_theme_detected() -> None:
    """
    A word that appears in multiple journal entries above min_frequency
    should be returned as a theme observation.
    """
    entries = [
        "I keep avoiding creative work even when I want to start.",
        "Today I avoided the creative project again. Avoidance feels automatic.",
        "Creative work calls to me but avoidance wins most days.",
        "I notice avoidance patterns around creative expression consistently.",
    ]
    detector = RecurringThemeDetector()
    results = detector.detect(entries, top_n=3, min_frequency=2)

    assert len(results) > 0
    # 'creative' or 'avoidance' should surface as top theme
    themes_found = [obs.description_neutral for obs in results]
    assert any("creative" in t or "avoidance" in t for t in themes_found)
    assert all(obs.pattern_type == "theme" for obs in results)
    assert all(obs.times_observed >= 2 for obs in results)


# ---------------------------------------------------------------------------
# 2. BehavioralLoopDetector — loop detected
# ---------------------------------------------------------------------------

def test_behavioral_loop_detected() -> None:
    """set → avoid → abandon repeated twice → loop flagged."""
    events = ["set", "avoid", "abandon", "set", "avoid", "abandon"]
    detector = BehavioralLoopDetector()
    results = detector.detect(events)

    assert len(results) == 1
    obs = results[0]
    assert obs.pattern_type == "loop"
    assert obs.times_observed == 2
    assert "set" in obs.description_neutral
    assert "avoid" in obs.description_neutral
    assert "abandon" in obs.description_neutral


# ---------------------------------------------------------------------------
# 3. BehavioralLoopDetector — single occurrence not flagged
# ---------------------------------------------------------------------------

def test_behavioral_loop_not_detected_single() -> None:
    """A sequence that appears only once should NOT be flagged."""
    events = ["set", "avoid", "abandon", "set", "start", "complete"]
    detector = BehavioralLoopDetector()
    results = detector.detect(events)

    # Only 'set → avoid → abandon' appeared once; should not be returned
    flagged_loops = [r for r in results if r.times_observed >= 2]
    assert len(flagged_loops) == 0


# ---------------------------------------------------------------------------
# 4. ContradictionDetector — contradiction flagged
# ---------------------------------------------------------------------------

def test_contradiction_flagged() -> None:
    """Stated value with 0% behavioral alignment → contradiction returned."""
    values = ["health"]
    log = BehaviorLog(alignment_rates={"health": 0.0})
    detector = ContradictionDetector()
    results = detector.detect(values, log)

    assert len(results) == 1
    obs = results[0]
    assert obs.pattern_type == "contradiction"
    assert "health" in obs.description_neutral
    assert obs.confidence == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 5. ContradictionDetector — aligned value not flagged
# ---------------------------------------------------------------------------

def test_contradiction_not_flagged_aligned() -> None:
    """Value with 80% behavioral alignment → no contradiction."""
    values = ["creativity"]
    log = BehaviorLog(alignment_rates={"creativity": 0.80})
    detector = ContradictionDetector()
    results = detector.detect(values, log)

    assert len(results) == 0


# ---------------------------------------------------------------------------
# 6. ShadowTimingGate — blocks low alignment score
# ---------------------------------------------------------------------------

def test_timing_gate_blocks_low_alignment() -> None:
    """Alignment score 25 (< 30 minimum) → gate returns False."""
    gate = ShadowTimingGate()
    feeling = _feeling(AffectState.RESONANCE)
    assert gate.is_safe(stage=3, feeling=feeling, alignment_score=25.0) is False


# ---------------------------------------------------------------------------
# 7. ShadowTimingGate — blocks Stage 1
# ---------------------------------------------------------------------------

def test_timing_gate_blocks_stage1() -> None:
    """Stage 1 → Shadow Engine is off, gate returns False regardless of affect."""
    gate = ShadowTimingGate()
    for affect in AffectState:
        feeling = _feeling(affect)
        assert gate.is_safe(stage=1, feeling=feeling, alignment_score=80.0) is False, (
            f"Expected False for Stage 1 with affect={affect}"
        )


# ---------------------------------------------------------------------------
# 8. ShadowTimingGate — allows Stage 3 + RESONANCE + score 50
# ---------------------------------------------------------------------------

def test_timing_gate_allows_stage3_resonance() -> None:
    """Stage 3 + RESONANCE + alignment 50 → safe to surface."""
    gate = ShadowTimingGate()
    feeling = _feeling(AffectState.RESONANCE)
    assert gate.is_safe(stage=3, feeling=feeling, alignment_score=50.0) is True

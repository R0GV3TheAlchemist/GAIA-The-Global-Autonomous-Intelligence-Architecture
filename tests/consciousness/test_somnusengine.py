"""Tests for SomnusEngine and AffectState — Issue #262."""
from __future__ import annotations

import pytest

from core.consciousness.affect_state import AffectState
from core.consciousness.somnusengine import SomnusContext, SomnusEngine, SomnusResult


# ---------------------------------------------------------------------------
# AffectState tests
# ---------------------------------------------------------------------------

class TestAffectState:
    def test_quadrant_flow(self) -> None:
        a = AffectState(valence=0.5, arousal=0.5)
        assert a.quadrant == 'flow'

    def test_quadrant_stress(self) -> None:
        a = AffectState(valence=-0.5, arousal=0.5)
        assert a.quadrant == 'stress'

    def test_quadrant_rest(self) -> None:
        a = AffectState(valence=0.5, arousal=-0.5)
        assert a.quadrant == 'rest'

    def test_quadrant_somnus(self) -> None:
        a = AffectState(valence=-0.5, arousal=-0.5)
        assert a.quadrant == 'somnus'

    def test_intensity_neutral(self) -> None:
        a = AffectState(valence=0.0, arousal=0.0)
        assert a.intensity == 0.0

    def test_regulation_needed(self) -> None:
        a = AffectState(valence=-0.8, arousal=0.6)
        assert a.is_regulation_needed

    def test_no_regulation_needed_positive(self) -> None:
        a = AffectState(valence=0.8, arousal=0.6)
        assert not a.is_regulation_needed

    def test_to_register_flow(self) -> None:
        a = AffectState(valence=0.5, arousal=0.5)
        assert a.to_register() == 'executive'

    def test_to_register_stress(self) -> None:
        a = AffectState(valence=-0.5, arousal=0.5)
        assert a.to_register() == 'minimal'

    def test_blend(self) -> None:
        a = AffectState(valence=1.0, arousal=0.0)
        b = AffectState(valence=0.0, arousal=1.0)
        blended = a.blend(b, weight=0.5)
        assert abs(blended.valence - 0.5) < 1e-9
        assert abs(blended.arousal - 0.5) < 1e-9


# ---------------------------------------------------------------------------
# SomnusEngine tests
# ---------------------------------------------------------------------------

def _make_context(**overrides) -> SomnusContext:
    base = dict(
        session_id='test-session-abc',
        episodic_memory=[
            {'summary': 'Talked about values', 'salience': 0.2},
            {'summary': 'Deep canon session', 'salience': 0.9},
        ],
        semantic_memory=[],
        apothecary_signals={'rest_deficit': 0.08, 'clarity_low': 0.6},
        recent_canon_refs=['C01', 'C30', 'C01', 'C30', 'C01'],
        declared_values=['sovereignty', 'care'],
    )
    base.update(overrides)
    return SomnusContext(**base)  # type: ignore[arg-type]


class TestSomnusEngine:
    def test_returns_somnus_result(self) -> None:
        engine = SomnusEngine()
        result = engine.run_cycle(_make_context())
        assert isinstance(result, SomnusResult)

    def test_dream_log_not_empty(self) -> None:
        engine = SomnusEngine()
        result = engine.run_cycle(_make_context())
        assert len(result.dream_log) > 0

    def test_consolidated_count(self) -> None:
        engine = SomnusEngine(consolidation_salience_threshold=0.5)
        result = engine.run_cycle(_make_context())
        # salience=0.2 entry should be consolidated
        assert result.consolidated_count >= 1

    def test_pruned_stale_signal(self) -> None:
        engine = SomnusEngine(apothecary_prune_threshold=0.1)
        result = engine.run_cycle(_make_context())
        assert 'rest_deficit' in result.pruned_signals

    def test_insight_from_repeated_canon(self) -> None:
        engine = SomnusEngine()
        result = engine.run_cycle(_make_context())
        # C01 appears 3x — should surface as insight
        assert result.insight_count >= 1

    def test_reflection_report_is_string(self) -> None:
        engine = SomnusEngine()
        result = engine.run_cycle(_make_context())
        report = result.to_reflection_report()
        assert isinstance(report, str)
        assert 'Dream Cycle' in report

    def test_checksum_is_hex_string(self) -> None:
        engine = SomnusEngine()
        result = engine.run_cycle(_make_context())
        assert len(result.checksum) == 16
        assert all(c in '0123456789abcdef' for c in result.checksum)

    def test_cycle_id_contains_session(self) -> None:
        engine = SomnusEngine()
        result = engine.run_cycle(_make_context())
        assert 'test-ses' in result.cycle_id

    def test_contradiction_detection(self) -> None:
        ctx = _make_context(
            recent_canon_refs=['override', 'control'],
            declared_values=['sovereignty'],
        )
        engine = SomnusEngine()
        result = engine.run_cycle(ctx)
        assert result.contradiction_count >= 1

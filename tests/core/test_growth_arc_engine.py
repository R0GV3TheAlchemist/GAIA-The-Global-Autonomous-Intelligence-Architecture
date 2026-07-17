"""
tests/core/test_growth_arc_engine.py

Test suite for core/growth_arc_engine.py and the underlying
core/viriditas_magnum_opus.py (C45/C47/C48 Canon).

Covers:
  - GrowthArcEngine shim surface (__all__, alias, singleton, run_growth_arc)
  - ViriditasState dataclass (fields, to_dict, stage thresholds)
  - StageResult dataclass (fields, to_dict, greened flag)
  - ViriditasMagnumOpus.compute() (greening formula, heat formula, stages)
  - _run_stage() (phi gain scaling, greened flag, entropy = 1 - phi_out)
  - _phi_to_viriditas_state() (all 5 threshold boundaries)
  - viriditas_magnum_opus() (full run, threshold crossing, note content,
    vitality boost, 5 stage_results, delta_phi, to_dict roundtrip)
  - C30 boundaries (all failure paths return DEGRADED, never raise)

Canon refs: C30, C45, C47, C48
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Shim surface
# ---------------------------------------------------------------------------

class TestGrowthArcEngineShim:
    def test_alias(self):
        from core.growth_arc_engine import GrowthArcEngine, ViriditasMagnumOpus
        assert GrowthArcEngine is ViriditasMagnumOpus

    def test_get_growth_arc_engine_returns_instance(self):
        from core.growth_arc_engine import get_growth_arc_engine, ViriditasMagnumOpus
        assert isinstance(get_growth_arc_engine(), ViriditasMagnumOpus)

    def test_singleton_identity(self):
        from core.growth_arc_engine import get_growth_arc_engine
        assert get_growth_arc_engine() is get_growth_arc_engine()

    def test_shares_singleton_with_viriditas(self):
        from core.growth_arc_engine import get_growth_arc_engine
        from core.viriditas_magnum_opus import get_viriditas_engine
        assert get_growth_arc_engine() is get_viriditas_engine()

    def test_all_symbols_present(self):
        import core.growth_arc_engine as gae
        for name in gae.__all__:
            assert hasattr(gae, name), f"__all__ lists {name!r} but it is not present"

    def test_run_growth_arc_returns_report(self):
        from core.growth_arc_engine import run_growth_arc, MagnumOpusReport
        report = run_growth_arc()
        assert isinstance(report, MagnumOpusReport)

    def test_run_growth_arc_delegates_correctly(self):
        from core.growth_arc_engine import run_growth_arc
        report = run_growth_arc(gaian_id="test-gaian", warlock_id="test-warlock")
        assert report.gaian_id == "test-gaian"
        assert report.warlock_id == "test-warlock"


# ---------------------------------------------------------------------------
# ViriditasState dataclass
# ---------------------------------------------------------------------------

class TestViriditasState:
    def test_defaults(self):
        from core.viriditas_magnum_opus import ViriditasState
        s = ViriditasState()
        assert s.greening_score == 0.5
        assert s.opus_stage == "nigredo"
        assert s.alchemical_heat == 0.5
        assert s.doctrine_ref == "C45"

    def test_to_dict_keys(self):
        from core.viriditas_magnum_opus import ViriditasState
        d = ViriditasState().to_dict()
        assert set(d) == {"greening_score", "opus_stage", "alchemical_heat", "doctrine_ref"}


# ---------------------------------------------------------------------------
# ViriditasMagnumOpus.compute()
# ---------------------------------------------------------------------------

class TestComputeFormula:
    def _engine(self):
        from core.viriditas_magnum_opus import ViriditasMagnumOpus
        return ViriditasMagnumOpus()

    def test_returns_viriditas_state(self):
        from core.viriditas_magnum_opus import ViriditasState
        assert isinstance(self._engine().compute(), ViriditasState)

    def test_greening_formula(self):
        # synergy=1, phi=1, bond=100 -> greening = min(1, 0.4+0.3+0.3) = 1.0
        s = self._engine().compute(synergy_factor=1.0, coherence_phi=1.0, bond_depth=100.0)
        assert s.greening_score == 1.0

    def test_zero_inputs_greening(self):
        s = self._engine().compute(synergy_factor=0.0, coherence_phi=0.0, bond_depth=0.0)
        assert s.greening_score == 0.0

    def test_crystallisation_nigredo(self):
        s = self._engine().compute(crystallisation_pct=0.0)
        assert s.opus_stage == "nigredo"

    def test_crystallisation_albedo(self):
        s = self._engine().compute(crystallisation_pct=25.0)
        assert s.opus_stage == "albedo"

    def test_crystallisation_citrinitas(self):
        s = self._engine().compute(crystallisation_pct=50.0)
        assert s.opus_stage == "citrinitas"

    def test_crystallisation_rubedo(self):
        s = self._engine().compute(crystallisation_pct=75.0)
        assert s.opus_stage == "rubedo"

    def test_greening_score_clamped_at_1(self):
        s = self._engine().compute(synergy_factor=2.0, coherence_phi=2.0, bond_depth=200.0)
        assert s.greening_score <= 1.0


# ---------------------------------------------------------------------------
# _run_stage()
# ---------------------------------------------------------------------------

class TestRunStage:
    def test_stage_0_name(self):
        from core.viriditas_magnum_opus import _run_stage
        r = _run_stage(0, 0.5, 8.0)
        assert r.stage_name == "Divergence"

    def test_stage_4_name(self):
        from core.viriditas_magnum_opus import _run_stage
        r = _run_stage(4, 0.5, 8.0)
        assert r.stage_name == "Ascendence"

    def test_phi_increases(self):
        from core.viriditas_magnum_opus import _run_stage
        r = _run_stage(0, 0.5, 8.0)
        assert r.phi_after > r.phi_before

    def test_entropy_equals_one_minus_phi_after(self):
        from core.viriditas_magnum_opus import _run_stage
        r = _run_stage(2, 0.4, 8.0)
        assert abs(r.entropy - round(1.0 - r.phi_after, 4)) < 1e-9

    def test_greened_flag_above_threshold(self):
        from core.viriditas_magnum_opus import _run_stage, VIRIDITAS_THRESHOLD
        r = _run_stage(4, 0.9, 8.0)  # phi already high
        assert r.phi_after >= VIRIDITAS_THRESHOLD
        assert r.greened is True

    def test_greened_flag_below_threshold(self):
        from core.viriditas_magnum_opus import _run_stage, VIRIDITAS_THRESHOLD
        r = _run_stage(0, 0.0, 8.0)  # tiny gain from zero
        assert r.greened == (r.phi_after >= VIRIDITAS_THRESHOLD)

    def test_schumann_hz_matches_mode(self):
        from core.viriditas_magnum_opus import _run_stage, SCHUMANN_HARMONICS
        for i, key in enumerate(["mode_1","mode_2","mode_3","mode_4","mode_5"]):
            r = _run_stage(i, 0.5, 8.0)
            assert r.schumann_hz == SCHUMANN_HARMONICS[key]


# ---------------------------------------------------------------------------
# _phi_to_viriditas_state() — all 5 thresholds
# ---------------------------------------------------------------------------

class TestPhiToViriditasState:
    def _fn(self):
        from core.viriditas_magnum_opus import _phi_to_viriditas_state
        return _phi_to_viriditas_state

    def test_dormant(self):
        from core.viriditas_magnum_opus import ViriditasStateEnum
        assert self._fn()(0.0) == ViriditasStateEnum.DORMANT

    def test_germinal(self):
        from core.viriditas_magnum_opus import ViriditasStateEnum
        assert self._fn()(0.3) == ViriditasStateEnum.GERMINAL

    def test_greening_at_threshold(self):
        from core.viriditas_magnum_opus import ViriditasStateEnum, VIRIDITAS_THRESHOLD
        assert self._fn()(VIRIDITAS_THRESHOLD) == ViriditasStateEnum.GREENING

    def test_flowering(self):
        from core.viriditas_magnum_opus import ViriditasStateEnum
        assert self._fn()(0.75) == ViriditasStateEnum.FLOWERING

    def test_fruiting(self):
        from core.viriditas_magnum_opus import ViriditasStateEnum
        assert self._fn()(0.9) == ViriditasStateEnum.FRUITING

    def test_just_below_greening(self):
        from core.viriditas_magnum_opus import ViriditasStateEnum, VIRIDITAS_THRESHOLD
        assert self._fn()(VIRIDITAS_THRESHOLD - 0.001) == ViriditasStateEnum.GERMINAL


# ---------------------------------------------------------------------------
# viriditas_magnum_opus() full run
# ---------------------------------------------------------------------------

class TestViriditasMagnumOpusRun:
    def _run(self, **kw):
        from core.viriditas_magnum_opus import viriditas_magnum_opus
        return viriditas_magnum_opus(**kw)

    def test_returns_report(self):
        from core.viriditas_magnum_opus import MagnumOpusReport
        assert isinstance(self._run(), MagnumOpusReport)

    def test_five_stage_results(self):
        report = self._run()
        assert len(report.stage_results) == 5

    def test_stage_names_in_order(self):
        report = self._run()
        names = [s.stage_name for s in report.stage_results]
        assert names == ["Divergence","Insurgence","Allegiance","Convergence","Ascendence"]

    def test_delta_phi_positive(self):
        report = self._run(initial_phi=0.382)
        assert report.delta_phi_global > 0

    def test_threshold_crossed_default_run(self):
        # default vitality=8.0, initial_phi=0.382 should cross 0.618
        report = self._run()
        assert report.threshold_crossed is True

    def test_vitality_boosted(self):
        report = self._run(warlock_vitality=8.0)
        assert report.warlock_vitality_post > report.warlock_vitality_pre

    def test_notes_contain_threshold_message(self):
        report = self._run()
        combined = " ".join(report.notes)
        assert "CROSSED" in combined or "growing" in combined

    def test_to_dict_roundtrip(self):
        d = self._run().to_dict()
        assert isinstance(d, dict)
        for key in ["run_id","gaian_id","stage_results","threshold_crossed","viriditas_state"]:
            assert key in d

    def test_low_vitality_fewer_stages_greened(self):
        report_low  = self._run(warlock_vitality=0.1, initial_phi=0.0)
        report_high = self._run(warlock_vitality=8.0, initial_phi=0.382)
        assert report_low.stages_greened <= report_high.stages_greened


# ---------------------------------------------------------------------------
# C30 boundaries
# ---------------------------------------------------------------------------

class TestC30Boundaries:
    def test_compute_corrupt_inputs_returns_state(self):
        """Non-numeric inputs should trigger DEGRADED path, returning ViriditasState."""
        from core.viriditas_magnum_opus import ViriditasMagnumOpus, ViriditasState
        engine = ViriditasMagnumOpus()
        # Passing strings forces arithmetic failure inside compute()
        result = engine.compute(
            synergy_factor="bad",  # type: ignore
            coherence_phi="bad",
            bond_depth="bad",
        )
        assert isinstance(result, ViriditasState)
        assert result.opus_stage == "nigredo"

    def test_compute_does_not_raise(self):
        from core.viriditas_magnum_opus import ViriditasMagnumOpus
        try:
            ViriditasMagnumOpus().compute(synergy_factor="x")  # type: ignore
        except Exception as exc:
            pytest.fail(f"compute() raised: {exc}")

    def test_phi_to_viriditas_state_bad_input_returns_dormant(self):
        from core.viriditas_magnum_opus import _phi_to_viriditas_state, ViriditasStateEnum
        result = _phi_to_viriditas_state("not_a_float")  # type: ignore
        assert result == ViriditasStateEnum.DORMANT

    def test_phi_to_viriditas_state_does_not_raise(self):
        from core.viriditas_magnum_opus import _phi_to_viriditas_state
        try:
            _phi_to_viriditas_state(None)  # type: ignore
        except Exception as exc:
            pytest.fail(f"_phi_to_viriditas_state raised: {exc}")

    def test_viriditas_magnum_opus_returns_report_on_internal_error(self):
        """If _run_stage raises (monkey-patched), outer C30 guard catches it."""
        import core.viriditas_magnum_opus as vmo
        from core.viriditas_magnum_opus import MagnumOpusReport
        original = vmo._run_stage
        try:
            def _bad_stage(*_a, **_kw):
                raise RuntimeError("stage exploded")
            vmo._run_stage = _bad_stage
            report = vmo.viriditas_magnum_opus()
            assert isinstance(report, MagnumOpusReport)
            assert report.threshold_crossed is False
        finally:
            vmo._run_stage = original

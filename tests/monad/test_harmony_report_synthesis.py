"""
Test — Full 8-Monad Harmony Cycle → HarmonyReport synthesis
Canon: Pre-Established Harmony loop (Leibniz)
"""
import pytest
from unittest.mock import MagicMock
from core.monad.orchestrator import MonadOrchestrator, HarmonyReport


def make_ctx(phi=0.78, turn=5, session_id="test-harmony", query="What is the iosis force?"):
    ctx = MagicMock()
    ctx.coherence_phi = phi
    ctx.turn_number = turn
    ctx.session_id = session_id
    ctx.query = query
    ctx.user_input = query
    ctx.spectral = {"force": "IOSIS"}
    return ctx


class TestHarmonyReportSynthesis:
    def setup_method(self):
        self.orchestrator = MonadOrchestrator()

    def test_harmony_cycle_returns_harmony_report(self):
        ctx = make_ctx()
        report = self.orchestrator.run_harmony_cycle(ctx)
        assert isinstance(report, HarmonyReport)

    def test_all_8_emissions_present(self):
        ctx = make_ctx()
        report = self.orchestrator.run_harmony_cycle(ctx)
        assert report.cognitive is not None
        assert report.quantum is not None
        assert report.process is not None
        assert report.perception is not None
        assert report.somatic is not None
        assert report.dream is not None
        assert report.noospheric is not None
        assert report.shadow is not None

    def test_active_monad_count_is_8(self):
        ctx = make_ctx(phi=0.78, query="iosis phi viriditas")
        report = self.orchestrator.run_harmony_cycle(ctx)
        assert report.active_monad_count == 8

    def test_harmony_phi_between_0_and_1(self):
        ctx = make_ctx()
        report = self.orchestrator.run_harmony_cycle(ctx)
        assert 0.0 <= report.harmony_phi <= 1.0

    def test_oa4_active_at_iosis_phi(self):
        ctx = make_ctx(phi=0.78)
        report = self.orchestrator.run_harmony_cycle(ctx)
        assert report.oa4_active is True

    def test_oa4_inactive_outside_iosis(self):
        ctx = make_ctx(phi=0.50)
        report = self.orchestrator.run_harmony_cycle(ctx)
        assert report.oa4_active is False

    def test_dream_active_above_bwl_threshold(self):
        ctx = make_ctx(phi=0.95)
        report = self.orchestrator.run_harmony_cycle(ctx)
        assert report.dream_active is True

    def test_dream_inactive_below_bwl_threshold(self):
        ctx = make_ctx(phi=0.50)
        report = self.orchestrator.run_harmony_cycle(ctx)
        assert report.dream_active is False

    def test_to_dict_is_serialisable(self):
        ctx = make_ctx()
        report = self.orchestrator.run_harmony_cycle(ctx)
        d = report.to_dict()
        import json
        json.dumps(d)  # must not raise

    def test_harmony_report_session_id_matches_ctx(self):
        ctx = make_ctx(session_id="special-session")
        report = self.orchestrator.run_harmony_cycle(ctx)
        assert report.session_id == "special-session"

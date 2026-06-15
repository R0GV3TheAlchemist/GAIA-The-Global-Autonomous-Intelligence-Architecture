"""
Tests — ShadowMonad
Canon: SHADOW_INTERROGATOR.md — always active, speaks when not asked.
"""
from unittest.mock import MagicMock
from core.monad.shadow import ShadowMonad


def make_ctx(phi=0.5, turn=1):
    ctx = MagicMock()
    ctx.coherence_phi = phi
    ctx.turn_number = turn
    ctx.session_id = "test-session"
    ctx.spectral = {}
    return ctx


class TestShadowMonad:
    def setup_method(self):
        self.monad = ShadowMonad(monad_id="test.shadow")

    def test_always_returns_dict(self):
        result = self.monad.harmonize(make_ctx())
        assert isinstance(result, dict)

    def test_interrogator_question_present(self):
        result = self.monad.harmonize(make_ctx(phi=0.50))
        assert len(result["interrogator_questions"]) > 0

    def test_oa4_flag_set_in_iosis_range(self):
        result = self.monad.harmonize(make_ctx(phi=0.78))
        assert "IOSIS_CORRIDOR_UNRESOLVED" in result["oa4_open"]

    def test_dark_line_detected_on_phi_collapse(self):
        # Drive phi down for 3 turns
        self.monad.harmonize(make_ctx(phi=0.80))
        self.monad.harmonize(make_ctx(phi=0.70))
        result = self.monad.harmonize(make_ctx(phi=0.60))
        assert result["dark_line_detected"] is True

    def test_no_dark_line_on_ascending_phi(self):
        self.monad.harmonize(make_ctx(phi=0.60))
        self.monad.harmonize(make_ctx(phi=0.70))
        result = self.monad.harmonize(make_ctx(phi=0.80))
        assert result["dark_line_detected"] is False

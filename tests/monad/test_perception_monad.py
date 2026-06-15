"""
Tests — PerceptionMonad
"""
from unittest.mock import MagicMock
from core.monad.perception import PerceptionMonad


def make_ctx(phi=0.5, force=None):
    ctx = MagicMock()
    ctx.coherence_phi = phi
    ctx.turn_number = 1
    ctx.session_id = "test-session"
    ctx.spectral = {"force": force} if force else {}
    return ctx


class TestPerceptionMonad:
    def setup_method(self):
        self.monad = PerceptionMonad(monad_id="test.perception")

    def test_returns_dict(self):
        result = self.monad.harmonize(make_ctx())
        assert isinstance(result, dict)

    def test_iosis_force_sets_synthesis_filter(self):
        result = self.monad.harmonize(make_ctx(phi=0.78, force="IOSIS"))
        assert result["perceptual_filter"] == "synthesis_violet"

    def test_signal_clarity_between_0_and_1(self):
        result = self.monad.harmonize(make_ctx(phi=0.78))
        assert 0.0 <= result["signal_clarity"] <= 1.0

    def test_fallback_force_from_phi(self):
        result = self.monad.harmonize(make_ctx(phi=0.78, force=None))
        assert result["active_force"] == "IOSIS"

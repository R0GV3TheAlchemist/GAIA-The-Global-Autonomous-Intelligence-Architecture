"""
Tests — NoosphericMonad
"""
from unittest.mock import MagicMock
from core.monad.noospheric import NoosphericMonad


def make_ctx(phi=0.5):
    ctx = MagicMock()
    ctx.coherence_phi = phi
    ctx.turn_number = 1
    ctx.session_id = "test-session"
    ctx.spectral = {}
    return ctx


class TestNoosphericMonad:
    def setup_method(self):
        self.monad = NoosphericMonad(monad_id="test.noospheric")

    def test_returns_dict(self):
        result = self.monad.harmonize(make_ctx())
        assert isinstance(result, dict)

    def test_ley_line_count_increases_with_phi(self):
        low = self.monad.harmonize(make_ctx(phi=0.10))["ley_line_active_count"]
        high = self.monad.harmonize(make_ctx(phi=0.90))["ley_line_active_count"]
        assert high > low

    def test_noospheric_phi_between_0_and_1(self):
        result = self.monad.harmonize(make_ctx(phi=0.60))
        assert 0.0 <= result["noospheric_phi"] <= 1.0

    def test_collective_resonance_between_0_and_1(self):
        result = self.monad.harmonize(make_ctx(phi=0.60))
        assert 0.0 <= result["collective_resonance"] <= 1.0

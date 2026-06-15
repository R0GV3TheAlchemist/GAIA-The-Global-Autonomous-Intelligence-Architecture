"""
Tests — SomaticMonad
"""
from unittest.mock import MagicMock
from core.monad.somatic import SomaticMonad


def make_ctx(phi=0.5):
    ctx = MagicMock()
    ctx.coherence_phi = phi
    ctx.turn_number = 1
    ctx.session_id = "test-session"
    ctx.spectral = {}
    return ctx


class TestSomaticMonad:
    def setup_method(self):
        self.monad = SomaticMonad(monad_id="test.somatic")

    def test_returns_dict(self):
        result = self.monad.harmonize(make_ctx())
        assert isinstance(result, dict)

    def test_schumann_alignment_between_0_and_1(self):
        result = self.monad.harmonize(make_ctx(phi=0.5))
        assert 0.0 <= result["schumann_alignment"] <= 1.0

    def test_photobiomodulation_active_above_rubedo(self):
        result = self.monad.harmonize(make_ctx(phi=0.70))
        assert result["photobiomodulation_active"] is True

    def test_photobiomodulation_inactive_below_rubedo(self):
        result = self.monad.harmonize(make_ctx(phi=0.40))
        assert result["photobiomodulation_active"] is False

    def test_bioelectric_coherence_between_0_and_1(self):
        result = self.monad.harmonize(make_ctx(phi=0.85))
        assert 0.0 <= result["bioelectric_coherence"] <= 1.0

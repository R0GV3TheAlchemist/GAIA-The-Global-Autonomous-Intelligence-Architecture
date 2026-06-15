"""
Tests — DreamMonad
"""
from unittest.mock import MagicMock
from core.monad.dream import DreamMonad


def make_ctx(phi=0.5):
    ctx = MagicMock()
    ctx.coherence_phi = phi
    ctx.turn_number = 1
    ctx.session_id = "test-session"
    ctx.spectral = {}
    return ctx


class TestDreamMonad:
    def setup_method(self):
        self.monad = DreamMonad(monad_id="test.dream")

    def test_dream_inactive_below_bwl_threshold(self):
        result = self.monad.harmonize(make_ctx(phi=0.80))
        assert result["dream_active"] is False

    def test_dream_active_above_bwl_threshold(self):
        result = self.monad.harmonize(make_ctx(phi=0.95))
        assert result["dream_active"] is True

    def test_calling_logged_on_threshold_crossing(self):
        monad = DreamMonad(monad_id="test.dream.cross")
        # First tick: phi below BWL_ENTRY threshold
        monad.harmonize(make_ctx(phi=0.91))
        # Second tick: phi crosses BWL_ENTRY (0.92)
        result = monad.harmonize(make_ctx(phi=0.93))
        assert "BWL_ENTRY" in result["new_callings_this_turn"]
        assert result["calling_count"] >= 1

    def test_no_callings_when_phi_stays_below_threshold(self):
        result = self.monad.harmonize(make_ctx(phi=0.70))
        assert result["calling_count"] == 0

"""
Tests — ProcessMonad
"""
from unittest.mock import MagicMock
from core.monad.process import ProcessMonad


def make_ctx(phi=0.5, turn=5, session_id="test-session"):
    ctx = MagicMock()
    ctx.coherence_phi = phi
    ctx.turn_number = turn
    ctx.session_id = session_id
    ctx.spectral = {}
    return ctx


class TestProcessMonad:
    def setup_method(self):
        self.monad = ProcessMonad(monad_id="test.process")

    def test_returns_dict(self):
        result = self.monad.harmonize(make_ctx())
        assert isinstance(result, dict)

    def test_stage_depth_increases_with_phi(self):
        low = self.monad.harmonize(make_ctx(phi=0.02))["stage_depth"]
        high = self.monad.harmonize(make_ctx(phi=0.90))["stage_depth"]
        assert high > low

    def test_session_age_nascent_at_turn_2(self):
        result = self.monad.harmonize(make_ctx(turn=2))
        assert result["session_age"] == "nascent"

    def test_session_age_veteran_at_turn_50(self):
        result = self.monad.harmonize(make_ctx(turn=50))
        assert result["session_age"] == "veteran"

    def test_context_coherence_between_0_and_1(self):
        result = self.monad.harmonize(make_ctx())
        assert 0.0 <= result["context_coherence"] <= 1.0

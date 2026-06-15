"""
Tests — CognitiveMonad
Canon law C30: epistemic integrity — no silent failures.
"""
import pytest
from unittest.mock import MagicMock
from core.monad.cognitive import CognitiveMonad


def make_ctx(query="", phi=0.5, turn=1):
    ctx = MagicMock()
    ctx.query = query
    ctx.user_input = query
    ctx.coherence_phi = phi
    ctx.turn_number = turn
    ctx.session_id = "test-session"
    ctx.spectral = {}
    return ctx


class TestCognitiveMonad:
    def setup_method(self):
        self.monad = CognitiveMonad(monad_id="test.cognitive")

    def test_returns_dict_for_valid_query(self):
        result = self.monad.harmonize(make_ctx(query="What is the viriditas force?"))
        assert isinstance(result, dict)
        assert "concept_density" in result
        assert "canon_alignment_score" in result

    def test_returns_none_for_empty_query(self):
        result = self.monad.harmonize(make_ctx(query=""))
        assert result is None

    def test_canon_query_scores_high_alignment(self):
        result = self.monad.harmonize(
            make_ctx(query="phi viriditas iosis rubedo monad harmony coherence spectral")
        )
        assert result["canon_alignment_score"] > 0.5

    def test_concept_density_between_0_and_1(self):
        result = self.monad.harmonize(make_ctx(query="The quick brown fox"))
        assert 0.0 <= result["concept_density"] <= 1.0

    def test_tick_never_raises(self):
        ctx = make_ctx(query="test")
        result = self.monad.tick(ctx)
        assert result is not None

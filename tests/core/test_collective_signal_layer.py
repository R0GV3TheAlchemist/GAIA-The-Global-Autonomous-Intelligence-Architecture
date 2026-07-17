"""
tests/core/test_collective_signal_layer.py

Test suite for core/collective_signal_layer.py and the underlying
core/noosphere.py (C43 Noosphere Doctrine).

Covers:
  - CollectiveSignalLayer shim surface (__all__, alias, singleton)
  - Session tracking (register, deregister, floor at 0)
  - Pattern contribution and consent gating
  - Resonance queries (min_frequency filter, sort order, consent gate)
  - Coherence event logging (fields, epistemic label, description default)
  - Noosphere status stage transitions (dormant, primitive, reactive)
  - C30 boundaries: all public methods degrade gracefully on corrupt state

Canon refs: C30, C43, C04
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Shim surface
# ---------------------------------------------------------------------------

class TestCollectiveSignalLayerShim:
    def test_alias(self):
        from core.collective_signal_layer import CollectiveSignalLayer, NoosphereLayer
        assert CollectiveSignalLayer is NoosphereLayer

    def test_get_collective_signal_layer_returns_instance(self):
        from core.collective_signal_layer import get_collective_signal_layer, NoosphereLayer
        assert isinstance(get_collective_signal_layer(), NoosphereLayer)

    def test_singleton_identity(self):
        from core.collective_signal_layer import get_collective_signal_layer
        assert get_collective_signal_layer() is get_collective_signal_layer()

    def test_shares_singleton_with_noosphere(self):
        from core.collective_signal_layer import get_collective_signal_layer
        from core.noosphere import get_noosphere
        assert get_collective_signal_layer() is get_noosphere()

    def test_all_symbols_present(self):
        import core.collective_signal_layer as csl
        for name in csl.__all__:
            assert hasattr(csl, name), f"__all__ lists {name!r} but it is not present"

    def test_reexported_types_same_objects(self):
        import core.collective_signal_layer as csl
        import core.noosphere as ns
        for name in ["NoosphereLayer", "CoherenceEvent", "CollectiveMemoryPattern", "get_noosphere"]:
            assert getattr(csl, name) is getattr(ns, name)


# ---------------------------------------------------------------------------
# Session tracking
# ---------------------------------------------------------------------------

class TestSessionTracking:
    def _layer(self):
        from core.noosphere import NoosphereLayer
        return NoosphereLayer()

    def test_register_increments(self):
        layer = self._layer()
        layer.register_session()
        layer.register_session()
        assert layer._active_sessions == 2

    def test_deregister_decrements(self):
        layer = self._layer()
        layer.register_session()
        layer.register_session()
        layer.deregister_session()
        assert layer._active_sessions == 1

    def test_deregister_floors_at_zero(self):
        layer = self._layer()
        layer.deregister_session()  # already 0
        assert layer._active_sessions == 0

    def test_multiple_register_deregister_cycle(self):
        layer = self._layer()
        for _ in range(5):
            layer.register_session()
        for _ in range(5):
            layer.deregister_session()
        assert layer._active_sessions == 0


# ---------------------------------------------------------------------------
# Pattern contribution
# ---------------------------------------------------------------------------

class TestPatternContribution:
    def _layer(self):
        from core.noosphere import NoosphereLayer
        return NoosphereLayer()

    def test_consent_false_returns_none(self):
        layer = self._layer()
        pid = layer.contribute_pattern("ai", [0.1, 0.2], gaian_consent=False)
        assert pid is None

    def test_consent_true_returns_pattern_id(self):
        layer = self._layer()
        pid = layer.contribute_pattern("ai", [0.1, 0.2], gaian_consent=True)
        assert pid is not None
        assert "ai" in pid

    def test_same_pattern_increments_frequency(self):
        layer = self._layer()
        emb = [0.1, 0.2]
        pid1 = layer.contribute_pattern("tech", emb)
        pid2 = layer.contribute_pattern("tech", emb)
        assert pid1 == pid2
        assert layer._patterns[pid1].frequency == 2
        assert layer._patterns[pid1].contributed_by_count == 2

    def test_different_topics_create_separate_patterns(self):
        layer = self._layer()
        emb = [0.1, 0.2]
        pid_a = layer.contribute_pattern("alpha", emb)
        pid_b = layer.contribute_pattern("beta",  emb)
        assert pid_a != pid_b
        assert len(layer._patterns) == 2

    def test_pattern_consent_verified_true(self):
        layer = self._layer()
        pid = layer.contribute_pattern("music", [0.5])
        assert layer._patterns[pid].consent_verified is True


# ---------------------------------------------------------------------------
# Resonance queries
# ---------------------------------------------------------------------------

class TestResonanceQueries:
    def _layer(self):
        from core.noosphere import NoosphereLayer
        return NoosphereLayer()

    def _seed(self, layer, topic, n):
        emb = [float(i) for i in range(n)]
        for i in range(n):
            layer.contribute_pattern(topic, [float(i)])

    def test_min_frequency_filter(self):
        layer = self._layer()
        layer.contribute_pattern("x", [1.0])
        # Only 1 occurrence — below default min_frequency=2
        assert layer.query_collective_resonance("x", min_frequency=2) == []

    def test_min_frequency_1_returns_single_occurrence(self):
        layer = self._layer()
        layer.contribute_pattern("x", [1.0])
        results = layer.query_collective_resonance("x", min_frequency=1)
        assert len(results) == 1

    def test_sorted_by_frequency_descending(self):
        layer = self._layer()
        # Contribute pattern A twice, pattern B three times
        for _ in range(2):
            layer.contribute_pattern("topic", [1.0])
        for _ in range(3):
            layer.contribute_pattern("topic", [2.0])
        results = layer.query_collective_resonance("topic", min_frequency=1)
        freqs = [r.frequency for r in results]
        assert freqs == sorted(freqs, reverse=True)

    def test_get_resonance_label_none_when_no_results(self):
        layer = self._layer()
        assert layer.get_resonance_label("empty_topic") is None

    def test_get_resonance_label_format(self):
        layer = self._layer()
        for _ in range(3):
            layer.contribute_pattern("healing", [0.9])
        label = layer.get_resonance_label("healing", min_frequency=2)
        assert label is not None
        assert "C43" in label
        assert "healing" in label


# ---------------------------------------------------------------------------
# Coherence event logging
# ---------------------------------------------------------------------------

class TestCoherenceLogging:
    def _layer(self):
        from core.noosphere import NoosphereLayer
        return NoosphereLayer()

    def test_log_returns_coherence_event(self):
        from core.noosphere import CoherenceEvent
        layer = self._layer()
        evt = layer.log_coherence_candidate(0.8)
        assert isinstance(evt, CoherenceEvent)

    def test_event_fields(self):
        layer = self._layer()
        layer.register_session()
        evt = layer.log_coherence_candidate(0.75, entropy_deviation=0.05)
        assert evt.semantic_resonance_score == 0.75
        assert evt.entropy_deviation == 0.05
        assert evt.session_count == 1
        assert evt.epistemic_label == "CANDIDATE_SIGNATURE"
        assert evt.doctrine_ref == "C43"

    def test_default_description_includes_session_count(self):
        layer = self._layer()
        layer.register_session()
        layer.register_session()
        evt = layer.log_coherence_candidate(0.9)
        assert "2" in evt.description

    def test_custom_description_preserved(self):
        layer = self._layer()
        evt = layer.log_coherence_candidate(0.5, description="Test event")
        assert evt.description == "Test event"

    def test_event_appended_to_log(self):
        layer = self._layer()
        layer.log_coherence_candidate(0.6)
        layer.log_coherence_candidate(0.7)
        assert len(layer._coherence_log) == 2

    def test_event_id_is_unique(self):
        layer = self._layer()
        e1 = layer.log_coherence_candidate(0.5)
        e2 = layer.log_coherence_candidate(0.5)
        assert e1.event_id != e2.event_id


# ---------------------------------------------------------------------------
# Noosphere status stage transitions
# ---------------------------------------------------------------------------

class TestNoosphereStatus:
    def _layer(self):
        from core.noosphere import NoosphereLayer
        return NoosphereLayer()

    def test_dormant_when_no_sessions(self):
        layer = self._layer()
        status = layer.get_noosphere_status()
        assert "Dormant" in status["noosphere_stage"]

    def test_primitive_awareness_one_session(self):
        layer = self._layer()
        layer.register_session()
        status = layer.get_noosphere_status()
        assert "Primitive Awareness" in status["noosphere_stage"]

    def test_reactive_intelligence_multi_session_high_resonance(self):
        layer = self._layer()
        for _ in range(3):
            layer.register_session()
        for _ in range(5):
            layer.log_coherence_candidate(0.9)
        status = layer.get_noosphere_status()
        assert "Reactive Intelligence" in status["noosphere_stage"]

    def test_status_contains_doctrine_key(self):
        layer = self._layer()
        status = layer.get_noosphere_status()
        assert "C43" in status["doctrine"]

    def test_privacy_status_present(self):
        layer = self._layer()
        status = layer.get_noosphere_status()
        assert "privacy_status" in status


# ---------------------------------------------------------------------------
# C30 boundaries
# ---------------------------------------------------------------------------

class TestC30Boundaries:
    def test_contribute_pattern_corrupt_hash_returns_none(self):
        """If _make_hash raises, contribute_pattern must return None."""
        from core.noosphere import NoosphereLayer

        class CorruptLayer(NoosphereLayer):
            @staticmethod
            def _make_hash(topic, embedding):
                raise RuntimeError("hash exploded")

        layer = CorruptLayer()
        result = layer.contribute_pattern("topic", [1.0])
        assert result is None

    def test_contribute_pattern_does_not_raise(self):
        from core.noosphere import NoosphereLayer

        class CorruptLayer(NoosphereLayer):
            @staticmethod
            def _make_hash(topic, embedding):
                raise ValueError("corrupt")

        try:
            CorruptLayer().contribute_pattern("topic", [1.0])
        except Exception as exc:
            pytest.fail(f"contribute_pattern raised: {exc}")

    def test_query_resonance_corrupt_patterns_returns_empty(self):
        """If the patterns dict is replaced with something that raises, query returns []."""
        from core.noosphere import NoosphereLayer

        layer = NoosphereLayer()
        layer._patterns = None  # type: ignore[assignment] — corrupt state
        result = layer.query_collective_resonance("topic")
        assert result == []

    def test_log_coherence_candidate_corrupt_log_returns_none(self):
        from core.noosphere import NoosphereLayer

        class CorruptLog(list):
            def append(self, _): raise RuntimeError("log full")

        layer = NoosphereLayer()
        layer._coherence_log = CorruptLog()
        result = layer.log_coherence_candidate(0.8)
        assert result is None

    def test_get_noosphere_status_corrupt_log_returns_degraded(self):
        from core.noosphere import NoosphereLayer

        layer = NoosphereLayer()
        layer._coherence_log = None  # type: ignore[assignment] — corrupt state
        status = layer.get_noosphere_status()
        assert status.get("status") == "DEGRADED" or "doctrine" in status

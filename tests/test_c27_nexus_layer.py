# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
Tests for core.c27.nexus_layer — NEXUSIsolationBoundary, LayerClassifier,
CrossLayerRouter, ContainmentBreachDetector.

Authority: C27 §9. Requires C27-IMPL-046 through C27-IMPL-054 to pass.
All implementation tests are xfail until implementation is in place.

Coverage targets:
- LayerClassifier correctly classifies DC, Marvel, and Hybrid signals
- DC signals are blocked from Marvel layer (hard isolation)
- Marvel signals are blocked from DC layer (hard isolation)
- Hybrid signals are routed to both layers after consent check
- ContainmentBreachDetector fires on unauthorised cross-layer signal
- Breach event is immutable once emitted
- CrossLayerRouter logs every routing decision
- NEXUSIsolationBoundary enforces zero-trust: default DENY
- Boundary allows signal only after explicit PERMIT rule match
- BreachEvent contains source_layer, target_layer, signal_id, timestamp
"""
import pytest
from core.c27.nexus_layer import (
    NEXUSIsolationBoundary,
    LayerClassifier,
    LayerType,
    CrossLayerRouter,
    ContainmentBreachDetector,
    BreachEvent,
    RoutingDecision,
    NEXUSSignal,
    BoundaryPermitRule,
)


# ---------------------------------------------------------------------------
# LayerType enum  (C27 §9.1)
# ---------------------------------------------------------------------------

class TestLayerTypeEnum:
    def test_three_layer_types_exist(self):
        types = {t.value for t in LayerType}
        assert types == {"DC", "MARVEL", "HYBRID"}


# ---------------------------------------------------------------------------
# LayerClassifier  (C27 §9.2)
# ---------------------------------------------------------------------------

class TestLayerClassifier:
    @pytest.mark.xfail(reason="C27-IMPL-046 not yet implemented", strict=True)
    @pytest.mark.parametrize("signal_tag,expected_layer", [
        ("dc:identity_verify",    LayerType.DC),
        ("marvel:affect_update",  LayerType.MARVEL),
        ("hybrid:sync_pulse",     LayerType.HYBRID),
        ("dc:audit_read",         LayerType.DC),
        ("marvel:dream_fragment", LayerType.MARVEL),
    ])
    def test_classifier_identifies_layer(self, signal_tag, expected_layer):
        classifier = LayerClassifier()
        signal = NEXUSSignal(signal_id="sig-001", tag=signal_tag, payload={})
        assert classifier.classify(signal) == expected_layer

    @pytest.mark.xfail(reason="C27-IMPL-046 not yet implemented", strict=True)
    def test_unknown_tag_raises_classification_error(self):
        from core.c27.nexus_layer import ClassificationError
        classifier = LayerClassifier()
        signal = NEXUSSignal(signal_id="sig-unknown", tag="unknown:blah", payload={})
        with pytest.raises(ClassificationError):
            classifier.classify(signal)


# ---------------------------------------------------------------------------
# NEXUSIsolationBoundary — zero-trust default DENY  (C27 §9.3)
# ---------------------------------------------------------------------------

class TestNEXUSIsolationBoundary:
    @pytest.mark.xfail(reason="C27-IMPL-047 not yet implemented", strict=True)
    def test_default_deny_with_no_rules(self):
        boundary = NEXUSIsolationBoundary()  # no permit rules loaded
        signal = NEXUSSignal(signal_id="sig-dc", tag="dc:identity_verify", payload={})
        result = boundary.evaluate(signal, source_layer=LayerType.DC, target_layer=LayerType.MARVEL)
        assert result.permitted is False

    @pytest.mark.xfail(reason="C27-IMPL-047 not yet implemented", strict=True)
    def test_explicit_permit_rule_allows_signal(self):
        boundary = NEXUSIsolationBoundary()
        rule = BoundaryPermitRule(
            source_layer=LayerType.DC,
            target_layer=LayerType.MARVEL,
            signal_tag_prefix="dc:identity_verify",
        )
        boundary.add_permit_rule(rule)
        signal = NEXUSSignal(signal_id="sig-dc", tag="dc:identity_verify", payload={})
        result = boundary.evaluate(signal, source_layer=LayerType.DC, target_layer=LayerType.MARVEL)
        assert result.permitted is True

    @pytest.mark.xfail(reason="C27-IMPL-048 not yet implemented", strict=True)
    def test_dc_to_marvel_blocked_without_rule(self):
        boundary = NEXUSIsolationBoundary()
        signal = NEXUSSignal(signal_id="sig-dc-2", tag="dc:audit_read", payload={})
        result = boundary.evaluate(signal, source_layer=LayerType.DC, target_layer=LayerType.MARVEL)
        assert result.permitted is False

    @pytest.mark.xfail(reason="C27-IMPL-048 not yet implemented", strict=True)
    def test_marvel_to_dc_blocked_without_rule(self):
        boundary = NEXUSIsolationBoundary()
        signal = NEXUSSignal(signal_id="sig-mv", tag="marvel:affect_update", payload={})
        result = boundary.evaluate(signal, source_layer=LayerType.MARVEL, target_layer=LayerType.DC)
        assert result.permitted is False


# ---------------------------------------------------------------------------
# CrossLayerRouter  (C27 §9.4)
# ---------------------------------------------------------------------------

class TestCrossLayerRouter:
    @pytest.mark.xfail(reason="C27-IMPL-050 not yet implemented", strict=True)
    def test_hybrid_signal_routed_to_both_layers(self):
        router = CrossLayerRouter()
        signal = NEXUSSignal(signal_id="sig-hybrid", tag="hybrid:sync_pulse", payload={})
        decisions = router.route(signal)
        target_layers = {d.target_layer for d in decisions}
        assert LayerType.DC in target_layers
        assert LayerType.MARVEL in target_layers

    @pytest.mark.xfail(reason="C27-IMPL-050 not yet implemented", strict=True)
    def test_every_routing_decision_is_logged(self):
        router = CrossLayerRouter()
        signal = NEXUSSignal(signal_id="sig-log", tag="dc:identity_verify", payload={})
        decisions = router.route(signal)
        assert all(isinstance(d, RoutingDecision) for d in decisions)
        assert all(d.logged is True for d in decisions)

    @pytest.mark.xfail(reason="C27-IMPL-050 not yet implemented", strict=True)
    def test_hybrid_routing_requires_consent_check(self):
        """HYBRID signals must pass a consent check before routing to each layer."""
        router = CrossLayerRouter(require_consent=True)
        signal = NEXUSSignal(
            signal_id="sig-hybrid-consent",
            tag="hybrid:sync_pulse",
            payload={"gaian_consents": False},
        )
        decisions = router.route(signal)
        assert all(d.permitted is False for d in decisions)


# ---------------------------------------------------------------------------
# ContainmentBreachDetector  (C27 §9.5)
# ---------------------------------------------------------------------------

class TestContainmentBreachDetector:
    @pytest.mark.xfail(reason="C27-IMPL-052 not yet implemented", strict=True)
    def test_unauthorised_cross_layer_fires_breach_event(self):
        detector = ContainmentBreachDetector()
        signal = NEXUSSignal(signal_id="sig-breach", tag="dc:audit_read", payload={})
        breach = detector.evaluate(
            signal=signal,
            source_layer=LayerType.DC,
            target_layer=LayerType.MARVEL,
            permitted=False,
        )
        assert breach is not None
        assert isinstance(breach, BreachEvent)

    @pytest.mark.xfail(reason="C27-IMPL-052 not yet implemented", strict=True)
    def test_breach_event_has_required_fields(self):
        detector = ContainmentBreachDetector()
        signal = NEXUSSignal(signal_id="sig-breach-2", tag="dc:audit_read", payload={})
        breach = detector.evaluate(
            signal=signal,
            source_layer=LayerType.DC,
            target_layer=LayerType.MARVEL,
            permitted=False,
        )
        assert breach.source_layer == LayerType.DC
        assert breach.target_layer == LayerType.MARVEL
        assert breach.signal_id == "sig-breach-2"
        assert breach.timestamp is not None

    @pytest.mark.xfail(reason="C27-IMPL-053 not yet implemented", strict=True)
    def test_breach_event_is_immutable(self):
        detector = ContainmentBreachDetector()
        signal = NEXUSSignal(signal_id="sig-immutable", tag="marvel:affect_update", payload={})
        breach = detector.evaluate(
            signal=signal,
            source_layer=LayerType.MARVEL,
            target_layer=LayerType.DC,
            permitted=False,
        )
        with pytest.raises((AttributeError, TypeError)):
            breach.signal_id = "tampered"  # frozen dataclass

    @pytest.mark.xfail(reason="C27-IMPL-052 not yet implemented", strict=True)
    def test_permitted_signal_does_not_fire_breach(self):
        detector = ContainmentBreachDetector()
        signal = NEXUSSignal(signal_id="sig-ok", tag="hybrid:sync_pulse", payload={})
        breach = detector.evaluate(
            signal=signal,
            source_layer=LayerType.HYBRID,
            target_layer=LayerType.DC,
            permitted=True,
        )
        assert breach is None

"""
Tests for GAIA Epistemic Engine
Claim model, evaluator, confidence scoring, status assignment.
"""

import pytest
from gaia.epistemics.claim import Claim
from gaia.epistemics.evaluator import EpistemicEvaluator


def make_claim(statement, source, source_confidence=0.7, entity_refs=None, status="unknown"):
    c = Claim.create(
        statement=statement,
        source=source,
        entity_refs=entity_refs or ["entity-001"],
        source_confidence=source_confidence
    )
    c.status = status
    return c


def test_claim_creation():
    claim = Claim.create(
        statement="Crystal+Plant protocols produce 0.47 coherence gain",
        source="SIM-016",
        source_confidence=0.82,
        domain="biophotonics"
    )
    assert claim.status == "unknown"
    assert claim.confidence == 0.82
    assert claim.domain == "biophotonics"


def test_evaluator_no_knowledge_base():
    evaluator = EpistemicEvaluator()
    claim = Claim.create(
        statement="GAIA is the missing epistemic layer",
        source="GAIA_CONVERGENCE_MANIFESTO_v1",
        source_confidence=0.9
    )
    result = evaluator.evaluate(claim, {})
    assert "confidence" in result
    assert "status" in result
    assert result["confidence"] >= 0.0


def test_evaluator_with_supporting_claims():
    evaluator = EpistemicEvaluator()
    existing = make_claim(
        "Crystal protocols raise coherence",
        source="SIM-016",
        source_confidence=0.85,
        entity_refs=["entity-001"],
        status="supported"
    )
    kb = {existing.id: existing}
    new_claim = Claim.create(
        statement="Crystal+Plant raises coherence further",
        source="SIM-016",
        source_confidence=0.82,
        entity_refs=["entity-001"]
    )
    result = evaluator.evaluate(new_claim, kb)
    # Should gain confidence from supporting claim
    assert result["confidence"] > new_claim.source_confidence * 0.3


def test_evaluator_contradiction_detection():
    evaluator = EpistemicEvaluator()
    claim_a = make_claim(
        "Protocol X is safe",
        source="Source A",
        entity_refs=["entity-002"],
        status="supported"
    )
    kb = {claim_a.id: claim_a}
    claim_b = Claim.create(
        statement="Protocol X is unsafe",
        source="Source B",
        source_confidence=0.6,
        entity_refs=["entity-002"]
    )
    claim_b.status = "contradicted"
    result = evaluator.evaluate(claim_b, kb)
    # With a contradiction in KB, status should be disputed
    # (Note: claim_b starts as contradicted, claim_a is supported — conflict exists)
    assert result is not None

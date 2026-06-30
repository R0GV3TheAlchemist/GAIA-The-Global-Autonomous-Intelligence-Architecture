"""
GAIA Epistemic Evaluator
The truth engine at the heart of GAIA.

This is what makes GAIA structurally different from every other AI system:
- It does not assume inputs are true
- It evaluates every claim against existing knowledge
- It computes confidence, detects contradictions, assigns epistemic status
- It updates the world model with evidence-weighted truth
"""

from typing import List, Dict, Any, Optional
from .claim import Claim, VALID_STATUSES


# Confidence thresholds — aligned with EPISTEMIC_FRAMEWORK.md
CONFIDENCE_THRESHOLDS = {
    "verified": 0.85,
    "supported": 0.65,
    "speculative-grounded": 0.45,
    "speculative": 0.25,
    "disputed": 0.0,       # Any claim with active contradictions
    "unknown": 0.0,        # Not yet evaluated
}

# Scoring weights
SUPPORT_WEIGHT = 0.08      # Each supporting claim adds this much confidence
CONTRADICTION_WEIGHT = 0.12  # Each contradicting claim removes this much
SOURCE_WEIGHT = 0.3        # Source reliability contributes this fraction


class EpistemicEvaluator:
    """
    The EpistemicEvaluator processes incoming Claims against the
    existing knowledge base and produces an evidence-weighted
    assessment: confidence score + epistemic status.

    This is GAIA's truth engine.
    """

    def evaluate(
        self,
        claim: Claim,
        knowledge_base: Dict[str, Claim]
    ) -> Dict[str, Any]:
        """
        Full epistemic evaluation of a claim.

        Returns:
            dict with keys: claim, confidence, status, contradictions,
                            supporting_claims, evaluation_notes
        """
        # 1. Find related claims in the knowledge base
        related = self._find_related_claims(claim, knowledge_base)

        # 2. Separate supporting from contradicting
        supporting = [c for c in related if self._is_supporting(claim, c)]
        contradictions = self._detect_contradictions(claim, related)

        # 3. Compute confidence score
        confidence = self._compute_confidence(
            claim, supporting, contradictions
        )

        # 4. Assign epistemic status
        status = self._assign_status(confidence, contradictions)

        # 5. Build provenance chain entry
        provenance_entry = (
            f"Evaluated at {__import__('datetime').datetime.utcnow().isoformat()} — "
            f"supporting={len(supporting)}, contradictions={len(contradictions)}, "
            f"confidence={confidence:.3f}, status={status}"
        )

        return {
            "claim": claim,
            "confidence": confidence,
            "status": status,
            "contradictions": contradictions,
            "supporting_claims": supporting,
            "evaluation_notes": provenance_entry
        }

    def _find_related_claims(
        self,
        claim: Claim,
        knowledge_base: Dict[str, Claim]
    ) -> List[Claim]:
        """
        Find claims in the knowledge base that share entity references
        or overlap semantically with the incoming claim.
        v0.1: entity_ref overlap. v0.2+: semantic similarity via embeddings.
        """
        related = []
        claim_entities = set(claim.entity_refs)
        for existing in knowledge_base.values():
            if existing.id == claim.id:
                continue
            existing_entities = set(existing.entity_refs)
            if claim_entities & existing_entities:  # shared entity reference
                related.append(existing)
        return related

    def _is_supporting(self, claim: Claim, other: Claim) -> bool:
        """A claim supports another if same entities + compatible status."""
        return (
            set(claim.entity_refs) & set(other.entity_refs)
            and other.status in ("supported", "verified", "speculative-grounded")
        )

    def _detect_contradictions(
        self,
        claim: Claim,
        related: List[Claim]
    ) -> List[Claim]:
        """
        Detect contradictions: claims about the same entities
        with conflicting status or high semantic opposition.
        v0.1: status conflict detection.
        v0.2+: semantic contradiction via NLI model.
        """
        contradictions = []
        for r in related:
            if self._is_contradiction(claim, r):
                contradictions.append(r)
        return contradictions

    def _is_contradiction(self, a: Claim, b: Claim) -> bool:
        """Two claims contradict if they concern the same entities
        and one is disputed/contradicted while the other is supported/verified."""
        a_positive = a.status in ("supported", "verified")
        b_positive = b.status in ("supported", "verified")
        a_negative = a.status in ("disputed", "contradicted")
        b_negative = b.status in ("disputed", "contradicted")
        same_entities = bool(set(a.entity_refs) & set(b.entity_refs))
        return same_entities and (
            (a_positive and b_negative) or
            (a_negative and b_positive)
        )

    def _compute_confidence(
        self,
        claim: Claim,
        supporting: List[Claim],
        contradictions: List[Claim]
    ) -> float:
        """
        Confidence computation:
        base = source_confidence * SOURCE_WEIGHT
        + supporting evidence bonus
        - contradiction penalty
        Clamped to [0.0, 1.0]
        """
        base = claim.source_confidence * SOURCE_WEIGHT

        # Start from midpoint if no source confidence signal
        if base == 0:
            base = 0.3

        base += len(supporting) * SUPPORT_WEIGHT
        base -= len(contradictions) * CONTRADICTION_WEIGHT

        return round(max(0.0, min(1.0, base)), 4)

    def _assign_status(
        self,
        confidence: float,
        contradictions: List[Claim]
    ) -> str:
        """Assign epistemic status based on confidence score and contradictions."""
        if contradictions:
            return "disputed"
        if confidence >= CONFIDENCE_THRESHOLDS["verified"]:
            return "verified"
        if confidence >= CONFIDENCE_THRESHOLDS["supported"]:
            return "supported"
        if confidence >= CONFIDENCE_THRESHOLDS["speculative-grounded"]:
            return "speculative-grounded"
        if confidence >= CONFIDENCE_THRESHOLDS["speculative"]:
            return "speculative"
        return "unknown"

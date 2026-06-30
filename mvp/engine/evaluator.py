"""
GAIA MVP — Epistemic Evaluator
The truth engine. Scores every claim. Assigns epistemic status.
This is what makes GAIA different from every other system.
"""

from typing import Dict, Any, List

# Confidence scoring weights
SUPPORT_BOOST  = 0.08   # each supporting claim adds this
CONTRA_PENALTY = 0.12   # each contradiction removes this
SOURCE_BONUS   = 0.05   # each named source adds this

# Status thresholds
THRESHOLDS = {
    "verified":            0.85,
    "supported":           0.65,
    "speculative-grounded": 0.45,
    "speculative":         0.25,
}


class EpistemicEvaluator:

    def evaluate(self, claim, world_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Full epistemic evaluation.
        Returns: claim, confidence, status, contradictions, supporting
        """
        related       = self._find_related(claim, world_state)
        contradictions = self._detect_contradictions(claim, related)
        supporting    = [c for c in related if c.get("status") in ("supported", "verified")]

        confidence = self._compute_confidence(claim, supporting, contradictions)
        status     = self._assign_status(confidence, contradictions)

        return {
            "claim":         claim,
            "confidence":    confidence,
            "status":        status,
            "contradictions": contradictions,
            "supporting":    supporting,
        }

    # ——— internal ———

    def _find_related(self, claim, world_state: Dict) -> List[Dict]:
        """v0.1: keyword overlap. v0.2+: semantic similarity."""
        words = set(claim.statement.lower().split())
        related = []
        for entry in world_state.values():
            entry_words = set(entry.get("statement", "").lower().split())
            if len(words & entry_words) >= 3:   # 3+ shared words = related
                related.append(entry)
        return related

    def _detect_contradictions(self, claim, related: List[Dict]) -> List[Dict]:
        return [
            r for r in related
            if self._is_conflict(claim.status, r.get("status", "unknown"))
        ]

    @staticmethod
    def _is_conflict(status_a: str, status_b: str) -> bool:
        positive = {"supported", "verified"}
        negative = {"disputed", "contradicted"}
        return (
            (status_a in positive and status_b in negative) or
            (status_a in negative and status_b in positive)
        )

    def _compute_confidence(self, claim, supporting, contradictions) -> float:
        base = 0.30                                       # floor
        base += len(claim.sources) * SOURCE_BONUS         # named sources
        base += len(supporting)    * SUPPORT_BOOST        # corroborating evidence
        base -= len(contradictions) * CONTRA_PENALTY      # contradictions
        return round(max(0.0, min(1.0, base)), 4)

    def _assign_status(self, confidence: float, contradictions: List) -> str:
        if contradictions:
            return "disputed"
        for status, threshold in THRESHOLDS.items():
            if confidence >= threshold:
                return status
        return "speculative"

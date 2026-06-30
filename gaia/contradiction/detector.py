"""
GAIA Contradiction Detector
Scans the knowledge base for conflicting claims and flags them for resolution.
"""

from typing import List, Dict, Tuple
from ..epistemics.claim import Claim


class ContradictionDetector:
    """
    Scans all claims in the knowledge base and identifies conflicting pairs.
    In v0.1: entity-overlap + status conflict detection.
    In v0.2+: semantic NLI-based contradiction detection.
    """

    def scan(
        self,
        knowledge_base: Dict[str, Claim]
    ) -> List[Tuple[Claim, Claim]]:
        """
        Full scan of the knowledge base for contradictions.
        Returns list of (claim_a, claim_b) conflict pairs.
        """
        claims = list(knowledge_base.values())
        conflicts = []
        seen = set()

        for i, a in enumerate(claims):
            for b in claims[i+1:]:
                pair_key = tuple(sorted([a.id, b.id]))
                if pair_key in seen:
                    continue
                if self._conflicts(a, b):
                    conflicts.append((a, b))
                    seen.add(pair_key)

        return conflicts

    def detect_for_claim(
        self,
        claim: Claim,
        knowledge_base: Dict[str, Claim]
    ) -> List[Claim]:
        """Detect contradictions for a single incoming claim against the knowledge base."""
        return [
            existing for existing in knowledge_base.values()
            if existing.id != claim.id and self._conflicts(claim, existing)
        ]

    def _conflicts(self, a: Claim, b: Claim) -> bool:
        """
        Two claims conflict when:
        1. They share at least one entity reference (they're about the same thing)
        2. Their epistemic statuses are incompatible
        """
        shared_entities = bool(set(a.entity_refs) & set(b.entity_refs))
        if not shared_entities:
            return False

        positive_statuses = {"supported", "verified"}
        negative_statuses = {"contradicted", "disputed"}

        a_pos = a.status in positive_statuses
        b_neg = b.status in negative_statuses
        a_neg = a.status in negative_statuses
        b_pos = b.status in positive_statuses

        return (a_pos and b_neg) or (a_neg and b_pos)

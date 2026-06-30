"""
GAIA MVP — Contradiction Engine
Scans the world state for claims that conflict with an incoming claim.
Conflicts are explicit, never hidden. — GAIAN_LAW L4
"""

from typing import Dict, Any, List


class ContradictionEngine:

    def detect(self, claim, world_state: Dict[str, Any]) -> List[Dict]:
        """
        Find all existing world-state entries that conflict with `claim`.
        """
        conflicts = []
        for entry in world_state.values():
            if entry.get("id") == claim.id:
                continue
            if self._is_conflict(claim, entry):
                conflicts.append(entry)
        return conflicts

    def _is_conflict(self, claim, entry: Dict) -> bool:
        """
        Two entries conflict when they share significant keyword overlap
        AND carry incompatible epistemic statuses.
        """
        words_a = set(claim.statement.lower().split())
        words_b = set(entry.get("statement", "").lower().split())
        semantic_overlap = len(words_a & words_b) >= 3

        positive = {"supported", "verified"}
        negative = {"disputed", "contradicted"}
        status_conflict = (
            (claim.status in positive and entry.get("status") in negative) or
            (claim.status in negative and entry.get("status") in positive)
        )

        return semantic_overlap and status_conflict

    def full_scan(self, world_state: Dict[str, Any]) -> List[Dict]:
        """
        Full contradiction scan across all entries.
        Returns list of {entry_a, entry_b} conflict pairs.
        """
        entries  = list(world_state.values())
        conflicts = []
        seen = set()
        for i, a in enumerate(entries):
            for b in entries[i+1:]:
                pair = tuple(sorted([a.get("id",""), b.get("id","")]))
                if pair in seen:
                    continue
                words_a = set(a.get("statement","").lower().split())
                words_b = set(b.get("statement","").lower().split())
                if len(words_a & words_b) >= 3:
                    pos = {"supported", "verified"}
                    neg = {"disputed", "contradicted"}
                    if (
                        (a.get("status") in pos and b.get("status") in neg) or
                        (a.get("status") in neg and b.get("status") in pos)
                    ):
                        conflicts.append({"entry_a": a, "entry_b": b})
                        seen.add(pair)
        return conflicts

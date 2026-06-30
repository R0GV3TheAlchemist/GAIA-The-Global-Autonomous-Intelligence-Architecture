"""
GAIA Consensus Engine
The system that forms shared truth from multiple node perspectives.

v0.4: Confidence + trust-weighted consensus (deterministic)
v0.5: Probabilistic Bayesian consensus
v0.6: Adversarial reasoning + trust graph weighting
"""

from typing import Dict, Any, List
from .global_state import GlobalWorldState


class ConsensusEngine:
    """
    Given merged node perspectives on the same claim,
    the ConsensusEngine determines the global consensus view.

    Resolution strategy (v0.4):
      1. For each claim, collect all node perspectives
      2. Weight each perspective by (confidence * node_trust_score)
      3. Highest weighted perspective wins
      4. Log conflicts where spread is above CONFLICT_THRESHOLD

    This is deterministic consensus — correct foundation,
    not yet full probabilistic democracy.
    """

    CONFLICT_THRESHOLD = 0.20  # flag if top-2 perspectives are within this range

    def resolve(
        self,
        merged_states: Dict[str, List[Dict]],
        global_state: GlobalWorldState
    ) -> Dict[str, Any]:
        """
        Resolve merged node perspectives into a single consensus world state.
        Returns: {claim_id: consensus_entry}
        """
        consensus: Dict[str, Any] = {}

        for claim_id, perspectives in merged_states.items():
            if len(perspectives) == 1:
                # Single source — no conflict possible
                p = perspectives[0]
                consensus[claim_id] = {
                    **p["value"],
                    "consensus_source": p["node"],
                    "consensus_method": "single_source",
                    "consensus_score":  p["value"].get("confidence", 0.5)
                }
                continue

            # Multi-source: compute weighted scores
            scored = self._score_perspectives(perspectives)
            scored_sorted = sorted(scored, key=lambda x: x["weight"], reverse=True)

            winner = scored_sorted[0]

            # Check if this needs conflict logging
            if len(scored_sorted) >= 2:
                top_gap = scored_sorted[0]["weight"] - scored_sorted[1]["weight"]
                if top_gap < self.CONFLICT_THRESHOLD:
                    global_state.log_conflict(claim_id, [
                        {
                            "node":       p["node"],
                            "weight":     p["weight"],
                            "confidence": p["value"].get("confidence", 0),
                            "status":     p["value"].get("status", "unknown")
                        }
                        for p in scored_sorted
                    ])

            consensus[claim_id] = {
                **winner["value"],
                "consensus_source": winner["node"],
                "consensus_method": "weighted_trust_confidence",
                "consensus_score":  winner["weight"],
                "perspective_count": len(perspectives)
            }

        return consensus

    def _score_perspectives(self, perspectives: List[Dict]) -> List[Dict]:
        """
        Score each perspective by: weight = confidence * trust_score
        """
        scored = []
        for p in perspectives:
            confidence = p["value"].get("confidence", 0.5)
            trust      = p.get("trust", 1.0)
            scored.append({
                **p,
                "weight": round(confidence * trust, 4)
            })
        return scored

    def agreement_level(
        self,
        merged_states: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """
        Compute network-wide agreement level:
        what fraction of claims have unanimous status across nodes?
        """
        total = 0
        unanimous = 0
        contested = []

        for claim_id, perspectives in merged_states.items():
            if len(perspectives) < 2:
                continue
            total += 1
            statuses = {p["value"].get("status", "unknown") for p in perspectives}
            if len(statuses) == 1:
                unanimous += 1
            else:
                contested.append({
                    "claim_id":  claim_id,
                    "statuses":  list(statuses),
                    "node_count": len(perspectives)
                })

        agreement_pct = round(unanimous / total, 4) if total > 0 else 1.0
        return {
            "total_shared_claims": total,
            "unanimous":           unanimous,
            "contested":           len(contested),
            "agreement_level":     agreement_pct,
            "contested_claims":    contested
        }

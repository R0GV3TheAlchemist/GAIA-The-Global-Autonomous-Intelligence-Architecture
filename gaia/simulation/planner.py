"""
GAIA Simulation Planner
Goal-driven candidate plan generation and simulation-based ranking.

Planning comes after simulation.
The planner:
  1. Takes a goal
  2. Generates candidate plans (sequences of events)
  3. Runs each as a simulation
  4. Compares outcomes
  5. Ranks and recommends

Critical: the planner never acts directly on reality.
It produces ranked recommendations for human or agent decision.

Goal
  ↓
Generate Candidate Plans
  ↓
Simulate each
  ↓
Compare outcomes
  ↓
Rank by confidence + metrics
  ↓
Recommend → Human / Agent Decision
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .engine import SimulationEngine, Simulation


class PlanningGoal:
    """A goal to be achieved through candidate plan simulation."""

    def __init__(
        self,
        description: str,
        target_metrics: Optional[Dict[str, float]] = None,
        constraints: Optional[List[str]] = None
    ):
        self.description    = description
        self.target_metrics = target_metrics or {}  # metric → desired value
        self.constraints    = constraints or []

    def __repr__(self) -> str:
        return f"PlanningGoal('{self.description[:60]}')"


class Planner:
    """
    Generates, simulates, and ranks candidate plans toward a goal.
    """

    def __init__(self, engine: "SimulationEngine"):
        self.engine = engine
        self._planning_runs: List[Dict] = []

    def plan(
        self,
        goal: PlanningGoal,
        candidate_simulations: List["Simulation"],
        world_snapshot: Any
    ) -> Dict[str, Any]:
        """
        Run all candidate simulations and rank them toward the goal.
        Returns ranked recommendations.
        """
        results = []

        for sim in candidate_simulations:
            result = self.engine.run(sim, world_snapshot)
            score  = self._score_against_goal(result, goal)
            results.append({
                "simulation_id":  sim.id,
                "title":          sim.title,
                "goal_score":     score,
                "outcome_status": result.get("outcome", {}).get("outcome_status", "unknown"),
                "confidence":     result.get("outcome", {}).get("aggregate_confidence", 0),
                "result":         result
            })

        # Rank by goal_score descending
        ranked = sorted(results, key=lambda x: x["goal_score"], reverse=True)

        planning_run = {
            "goal":             goal.description,
            "candidates_run":   len(candidate_simulations),
            "ranked_plans":     ranked,
            "recommendation":   ranked[0] if ranked else None,
            "note": (
                "Ranking based on simulation outcomes under stated assumptions. "
                "Human or agent decision required before any action on reality."
            )
        }
        self._planning_runs.append(planning_run)
        return planning_run

    def _score_against_goal(
        self,
        result: Dict[str, Any],
        goal: PlanningGoal
    ) -> float:
        """
        Score a simulation result against a planning goal.
        Score = assumption confidence × metric alignment.
        """
        base_conf = result.get("outcome", {}).get("aggregate_confidence", 0.5)
        if not goal.target_metrics:
            return base_conf

        final_metrics = result.get("outcome", {}).get("final_metrics", {})
        alignment_scores = []
        for metric, target in goal.target_metrics.items():
            actual = final_metrics.get(metric)
            if actual is None:
                alignment_scores.append(0.5)  # unknown → neutral
            else:
                # Normalised closeness score
                diff = abs(actual - target)
                closeness = max(0.0, 1.0 - diff)
                alignment_scores.append(closeness)

        avg_alignment = sum(alignment_scores) / len(alignment_scores)
        return round(base_conf * avg_alignment, 4)

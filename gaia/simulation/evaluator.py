"""
GAIA Simulation Evaluator
Scores completed simulations and compares candidate futures.

Every simulation outcome records:
  - Confidence (how reliable are the assumptions?)
  - Conflicts (assumptions that contradict known world state)
  - Unknowns (critical factors that could invalidate the outcome)
  - Metrics delta (how did key measures change?)
  - Epistemic status (is this speculative, plausible, or grounded?)

Not simply: True / False.
Always: 'Under these assumptions, with these unknowns, here is what follows.'
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import Simulation


class SimulationEvaluator:

    def evaluate(self, sim: "Simulation") -> Dict[str, Any]:
        """
        Score a completed simulation.
        """
        asm_summary = sim.assumptions.summary()
        agg_conf    = asm_summary["aggregate_confidence"]
        critical_u  = asm_summary["critical_unknowns"]
        contested   = asm_summary["contested_assumptions"]

        # Epistemic status of the outcome
        status = self._assign_status(agg_conf, critical_u, contested)

        # Final sandbox metrics
        final_metrics = dict(sim.sandbox.get_state().metrics)

        return {
            "outcome_status":        status,
            "aggregate_confidence":  agg_conf,
            "critical_unknowns":     critical_u,
            "contested_assumptions": contested,
            "final_metrics":         final_metrics,
            "events_applied":        len(sim.events_plan),
            "claim_count":           len(sim.sandbox.get_state().claims),
            "interpretation": (
                f"Under {asm_summary['assumption_count']} assumption(s) with "
                f"aggregate confidence {agg_conf:.2f}, "
                f"and {critical_u} critical unknown(s): "
                f"outcome is {status}. "
                f"This is a candidate future, not a truth claim."
            )
        }

    def compare(
        self,
        sim_a: "Simulation",
        sim_b: "Simulation"
    ) -> Dict[str, Any]:
        """
        Compare two completed simulations.
        Returns a structured comparison for human or agent decision-making.
        """
        oc_a = sim_a.outcome or {}
        oc_b = sim_b.outcome or {}

        metrics_a = oc_a.get("final_metrics", {})
        metrics_b = oc_b.get("final_metrics", {})

        all_metrics = set(metrics_a) | set(metrics_b)
        metric_deltas = {}
        for m in all_metrics:
            va = metrics_a.get(m, 0)
            vb = metrics_b.get(m, 0)
            metric_deltas[m] = {
                sim_a.id: va,
                sim_b.id: vb,
                "delta":  round(vb - va, 4)
            }

        # Which simulation has higher assumption confidence?
        conf_a = oc_a.get("aggregate_confidence", 0)
        conf_b = oc_b.get("aggregate_confidence", 0)
        preferred = sim_a.id if conf_a >= conf_b else sim_b.id

        return {
            "sim_a":          sim_a.id,
            "sim_b":          sim_b.id,
            "metric_deltas":  metric_deltas,
            "confidence_a":   conf_a,
            "confidence_b":   conf_b,
            "preferred":      preferred,
            "note": (
                "Comparison based on assumption confidence and metric outcomes. "
                "Human or agent decision required before any action."
            )
        }

    def _assign_status(
        self,
        agg_confidence: float,
        critical_unknowns: int,
        contested_assumptions: int
    ) -> str:
        if critical_unknowns >= 3 or contested_assumptions >= 2:
            return "highly_speculative"
        if critical_unknowns >= 1 or agg_confidence < 0.30:
            return "speculative"
        if agg_confidence >= 0.60 and critical_unknowns == 0:
            return "plausible_grounded"
        if agg_confidence >= 0.40:
            return "plausible"
        return "speculative"

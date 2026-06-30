"""
GAIA Simulation Branching
Fork multiple simulations from a single snapshot to explore divergent futures.

Branching model:

  Reality Snapshot
       │
       ├─── Simulation A (optimistic assumptions)
       ├─── Simulation B (pessimistic assumptions)
       └─── Simulation C (baseline assumptions)
              │
        Comparison Engine
              │
     Human / Agent Decision

The snapshot never changes.
Only the branches diverge.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .engine import SimulationEngine, Simulation


class BranchManager:
    """
    Creates and manages divergent simulation branches
    from a single real-world snapshot.
    """

    def __init__(self, engine: "SimulationEngine"):
        self.engine   = engine
        self._branches: Dict[str, List["Simulation"]] = {}  # snapshot_id → [sims]

    def branch(
        self,
        snapshot: Any,
        configurations: List[Dict[str, Any]]
    ) -> List["Simulation"]:
        """
        Create multiple simulation branches from a single snapshot.
        Each configuration defines a distinct 'what if' scenario.

        configuration keys:
          title        — human-readable branch name
          assumptions  — list of {statement, confidence} dicts
          unknowns     — list of {description, impact_level} dicts
          events       — list of {description, parameters} dicts

        Returns list of ready-to-run Simulation objects.
        """
        from .event import Event
        snapshot_id = getattr(snapshot, "id", "manual")
        branches = []

        for cfg in configurations:
            sim = self.engine.create(cfg.get("title", "branch"))

            for asm in cfg.get("assumptions", []):
                sim.assumptions.add_assumption(**asm)

            for unk in cfg.get("unknowns", []):
                sim.assumptions.add_unknown(**unk)

            for evt in cfg.get("events", []):
                sim.add_event(Event(
                    description=evt["description"],
                    parameters=evt.get("parameters", {})
                ))

            branches.append(sim)

        self._branches.setdefault(snapshot_id, []).extend(branches)
        return branches

    def run_all(
        self,
        branches: List["Simulation"],
        snapshot: Any,
        steps: int = 1
    ) -> List[Dict[str, Any]]:
        """Run all branches against the same snapshot and return results."""
        return [
            self.engine.run(sim, snapshot, steps=steps)
            for sim in branches
        ]

    def compare_all(
        self,
        branches: List["Simulation"]
    ) -> Dict[str, Any]:
        """Compare all completed branches side by side."""
        completed = [b for b in branches if b.completed]
        if len(completed) < 2:
            return {"error": "Need at least 2 completed branches to compare."}

        return {
            "branch_count": len(completed),
            "branches": [
                {
                    "id":              b.id,
                    "title":           b.title,
                    "outcome_status":  b.outcome.get("outcome_status", "unknown"),
                    "confidence":      b.outcome.get("aggregate_confidence", 0),
                    "critical_unknowns": b.outcome.get("critical_unknowns", 0),
                    "final_metrics":   b.outcome.get("final_metrics", {})
                }
                for b in completed
            ],
            "note": "All branches forked from same snapshot. Reality unchanged."
        }

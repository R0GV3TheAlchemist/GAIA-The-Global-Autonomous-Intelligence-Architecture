"""
GAIA Simulation Engine — v0.7
Orchestrates the full simulation lifecycle:
  create → configure assumptions → inject events → run steps → evaluate

Core principle enforced here:
  Reality is read-only.
  Simulations branch from snapshots and run in isolated sandboxes.
  No simulation result is written back to the real world state
  without explicit human or agent decision.
"""

import uuid
from copy import deepcopy
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

from .sandbox import Sandbox
from .event import Event
from .assumptions import AssumptionSet
from .evaluator import SimulationEvaluator

if TYPE_CHECKING:
    from gaia.world.temporal import WorldSnapshot


class Simulation:
    """
    A single simulation run.
    Tracks the full lifecycle: snapshot fork → events → steps → outcome.
    """

    def __init__(self, title: str = ""):
        self.id              = f"sim_{str(uuid.uuid4())[:8]}"
        self.title           = title
        self.parent_snapshot = None   # snapshot ID this sim forked from
        self.sandbox         = Sandbox(self.id)
        self.assumptions     = AssumptionSet(self.id, title)
        self.events_plan:    List[Event] = []
        self.causal_rules:   List[Any]   = []
        self.completed       = False
        self.outcome         = None
        self.created_at      = datetime.utcnow().isoformat()

    def add_event(self, event: Event) -> None:
        self.events_plan.append(event)

    def __repr__(self) -> str:
        return (
            f"Simulation(id={self.id}, title='{self.title}', "
            f"events={len(self.events_plan)}, completed={self.completed})"
        )


class SimulationEngine:
    """
    The orchestrator for GAIA simulation runs.

    Usage:
        engine = SimulationEngine()

        sim = engine.create("Renewable Expansion 2035")

        sim.assumptions.add_assumption(
            "Battery costs continue declining", confidence=0.80
        )
        sim.assumptions.add_unknown("Fusion breakthrough", impact_level="critical")

        sim.add_event(Event(
            "Increase renewable capacity",
            parameters={"renewable_share": 0.60, "energy_cost": -0.15}
        ))

        result = engine.run(sim, world_snapshot)
    """

    def __init__(self):
        self._simulations: Dict[str, Simulation] = {}
        self._evaluator   = SimulationEvaluator()
        self._run_count   = 0

    def create(self, title: str = "") -> Simulation:
        """Create a new simulation (not yet run)."""
        sim = Simulation(title=title)
        self._simulations[sim.id] = sim
        return sim

    def run(
        self,
        sim: Simulation,
        snapshot,                         # WorldSnapshot or Dict
        steps: int = 1,
        require_assumptions: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a simulation:
        1. Validate assumptions (required by default)
        2. Fork sandbox from snapshot
        3. Inject events
        4. Run causal steps
        5. Evaluate outcomes
        Returns complete simulation result.
        """
        # Step 1: Validate assumptions
        if require_assumptions and not sim.assumptions.is_valid():
            return {
                "simulation_id": sim.id,
                "error": (
                    "Simulation rejected: no assumptions defined. "
                    "Every simulation must explicitly state its assumptions "
                    "to prevent hypothetical outcomes being mistaken for truth claims."
                )
            }

        # Step 2: Fork sandbox from snapshot
        if hasattr(snapshot, "state"):
            sim.sandbox.fork_from_snapshot(snapshot)
            sim.parent_snapshot = getattr(snapshot, "id", None)
        else:
            sim.sandbox.fork_from(snapshot)

        # Step 3: Inject events
        for event in sim.events_plan:
            sim.sandbox.inject(event)

        # Step 4: Run causal steps
        step_results = []
        for _ in range(steps):
            step_result = sim.sandbox.step(sim.causal_rules)
            step_results.append(step_result)

        # Step 5: Evaluate
        sim.sandbox.complete()
        sim.completed = True
        sim.outcome   = self._evaluator.evaluate(sim)
        self._run_count += 1

        return {
            "simulation_id":   sim.id,
            "title":           sim.title,
            "parent_snapshot": sim.parent_snapshot,
            "steps_run":       steps,
            "events_applied":  len(sim.events_plan),
            "assumptions":     sim.assumptions.summary(),
            "outcome":         sim.outcome,
            "sandbox_export":  sim.sandbox.export(),
            "completed_at":    datetime.utcnow().isoformat()
        }

    def compare(
        self,
        sim_a: Simulation,
        sim_b: Simulation
    ) -> Dict[str, Any]:
        """
        Compare two completed simulations.
        Foundation for the planning layer (rank candidate futures).
        """
        if not sim_a.completed or not sim_b.completed:
            return {"error": "Both simulations must be completed before comparison."}
        return self._evaluator.compare(sim_a, sim_b)

    def get(self, sim_id: str) -> Optional[Simulation]:
        return self._simulations.get(sim_id)

    def all_simulations(self) -> List[Simulation]:
        return list(self._simulations.values())

    def stats(self) -> Dict[str, Any]:
        completed = sum(1 for s in self._simulations.values() if s.completed)
        return {
            "total_simulations": len(self._simulations),
            "completed":         completed,
            "pending":           len(self._simulations) - completed,
            "total_runs":        self._run_count
        }

    def __repr__(self) -> str:
        return f"SimulationEngine(sims={len(self._simulations)}, runs={self._run_count})"

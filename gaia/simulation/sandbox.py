"""
GAIA Simulation Sandbox
The isolated execution environment for a single simulation run.

A sandbox:
  - begins from a deep copy of a real-world snapshot
  - accepts event injections
  - tracks all state mutations
  - never touches the real world state
  - produces a complete, auditable simulation record
"""

import copy
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SimulationState(BaseModel):
    """The mutable world state inside a sandbox."""
    claims: Dict[str, Any] = {}
    entities: Dict[str, Any] = {}
    causal_links: List[Dict] = []
    metrics: Dict[str, float] = {}


class Sandbox:
    """
    Isolated simulation execution environment.
    Forked from a real temporal snapshot.
    State mutations are local only — no writes to real world.

    Lifecycle:
      1. fork_from(snapshot)   — clone real state into sandbox
      2. inject(event)         — apply hypothetical changes
      3. step()                — advance one time unit
      4. get_state()           — read current sandbox state
      5. export()              — produce final simulation record
    """

    def __init__(self, simulation_id: Optional[str] = None):
        self.id          = simulation_id or f"sim_{str(uuid.uuid4())[:8]}"
        self._state      = SimulationState()
        self._events_applied: List[Dict] = []
        self._step_count = 0
        self._forked_from: Optional[str] = None
        self._forked_at: Optional[str] = None
        self._completed  = False
        self._notes: List[str] = []

    def fork_from(self, snapshot_state: Dict[str, Any]) -> "Sandbox":
        """
        Clone a real world snapshot into this sandbox.
        After this call, sandbox state is fully isolated from reality.
        """
        self._state.claims  = copy.deepcopy(snapshot_state.get("claims",  snapshot_state))
        self._state.entities = copy.deepcopy(snapshot_state.get("entities", {}))
        self._forked_at      = datetime.utcnow().isoformat()
        return self

    def fork_from_snapshot(self, snapshot) -> "Sandbox":
        """Fork from a WorldSnapshot object."""
        self._forked_from = getattr(snapshot, "id", None)
        return self.fork_from(getattr(snapshot, "state", {}))

    def inject(self, event: "Event") -> None:  # type: ignore
        """
        Apply a hypothetical event to the sandbox state.
        Records the event for audit trail.
        Reality is not touched.
        """
        mutations = event.apply(self._state)
        self._events_applied.append({
            "event_id":    event.id,
            "description": event.description,
            "parameters":  event.parameters,
            "mutations":   mutations,
            "step":        self._step_count,
            "timestamp":   datetime.utcnow().isoformat()
        })

    def step(self, causal_rules: Optional[List] = None) -> Dict[str, Any]:
        """
        Advance the simulation one time step.
        Optionally apply causal rules to propagate effects.
        Returns a diff summary of what changed.
        """
        self._step_count += 1
        changes = {"step": self._step_count, "mutations": []}

        if causal_rules:
            for rule in causal_rules:
                result = rule.apply(self._state)
                if result:
                    changes["mutations"].append(result)
                    self._notes.append(
                        f"Step {self._step_count}: causal rule '{rule.name}' triggered"
                    )
        return changes

    def complete(self) -> None:
        self._completed = True

    def get_state(self) -> SimulationState:
        return self._state

    def export(self) -> Dict[str, Any]:
        """Export the full simulation record for evaluation."""
        return {
            "simulation_id":   self.id,
            "forked_from":     self._forked_from,
            "forked_at":       self._forked_at,
            "steps_run":       self._step_count,
            "events_applied":  len(self._events_applied),
            "events":          self._events_applied,
            "completed":       self._completed,
            "notes":           self._notes,
            "final_state":     {
                "claim_count":  len(self._state.claims),
                "entity_count": len(self._state.entities),
                "metrics":      dict(self._state.metrics)
            }
        }

    def __repr__(self) -> str:
        return (
            f"Sandbox(id={self.id}, "
            f"steps={self._step_count}, "
            f"events={len(self._events_applied)}, "
            f"completed={self._completed})"
        )

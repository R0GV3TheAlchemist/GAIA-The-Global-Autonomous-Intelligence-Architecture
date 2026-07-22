"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NEXUS — The Universal Autonomous Intelligence Architecture
  GAIA  — The Global Autonomous Intelligence Architecture

  Author   : Kyle Steen
  GitHub   : R0GV3TheAlchemist (https://github.com/R0GV3TheAlchemist)
  Email    : xxkylesteenxx@outlook.com
  Project  : NEXUS / GAIA
  License  : All Rights Reserved © 2026 Kyle Steen
             Unauthorized use, reproduction, or distribution
             of this file or its contents is strictly prohibited.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

simulation.py — NEXUS Digital Twin Simulation Engine.

TwinSimulation bootstraps a sandboxed simulation from a TwinRegistry
snapshot, runs counterfactual scenarios, and reports divergence from
the live registry state.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4
import copy, time

from twins.entity import DigitalTwin, TwinState, TwinType
from twins.registry import TwinRegistry, TwinEvent, TwinEventType


@dataclass
class SimulationScenario:
    """A named set of state mutations to apply in a sandboxed simulation."""
    scenario_id:  UUID               = field(default_factory=uuid4)
    name:         str                = ""
    description:  str                = ""
    mutations:    List[Dict[str, Any]] = field(default_factory=list)

    def add_mutation(self, twin_name: str,
                     properties: Dict[str, Any],
                     health: Optional[float] = None) -> None:
        self.mutations.append({
            "twin_name":  twin_name,
            "properties": properties,
            "health":     health,
        })


@dataclass
class SimulationResult:
    """Result of running a SimulationScenario against a sandboxed registry."""
    result_id:      UUID               = field(default_factory=uuid4)
    scenario_id:    UUID               = field(default_factory=uuid4)
    scenario_name:  str                = ""
    ran_at:         float              = field(default_factory=time.time)
    divergence:     List[Dict[str, Any]] = field(default_factory=list)
    events_emitted: int                = 0
    success:        bool               = True
    error:          str                = ""


class TwinSimulation:
    """
    Bootstraps a sandboxed TwinRegistry from a live registry snapshot,
    applies SimulationScenario mutations, and computes divergence.
    No writes are made to the live registry.
    """

    def __init__(self, live_registry: TwinRegistry) -> None:
        self._live = live_registry

    def run(self, scenario: SimulationScenario) -> SimulationResult:
        result = SimulationResult(
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
        )
        sandbox = TwinRegistry()
        event_counter = [0]

        def count_events(e: TwinEvent) -> None:
            event_counter[0] += 1

        for et in TwinEventType:
            sandbox.subscribe(et, count_events)

        for twin_dict in self._live.snapshot():
            twin = DigitalTwin(
                name=twin_dict["name"],
                twin_type=TwinType[twin_dict["twin_type"]],
                metadata=twin_dict.get("metadata", {}),
            )
            twin._state.properties    = copy.deepcopy(twin_dict.get("properties", {}))
            twin._state.health        = twin_dict.get("health", 1.0)
            twin._state.anomaly_flags = list(twin_dict.get("anomaly_flags", []))
            sandbox.register(twin)

        try:
            for mutation in scenario.mutations:
                twin = sandbox.get_by_name(mutation["twin_name"])
                if twin is None:
                    result.success = False
                    result.error   = f"Twin '{mutation['twin_name']}' not found in sandbox."
                    return result
                sandbox.update(twin.twin_id, mutation["properties"],
                               mutation.get("health"))
        except Exception as exc:
            result.success = False
            result.error   = str(exc)
            return result

        live_snap    = {t["name"]: t for t in self._live.snapshot()}
        sandbox_snap = {t["name"]: t for t in sandbox.snapshot()}

        for name, live_twin in live_snap.items():
            sim_twin   = sandbox_snap.get(name, {})
            live_props = live_twin.get("properties", {})
            sim_props  = sim_twin.get("properties", {})
            for key in set(live_props) | set(sim_props):
                lv, sv = live_props.get(key), sim_props.get(key)
                if lv != sv:
                    result.divergence.append({
                        "twin_name":  name,
                        "property":   key,
                        "live_value": lv,
                        "sim_value":  sv,
                    })

        result.events_emitted = event_counter[0]
        return result

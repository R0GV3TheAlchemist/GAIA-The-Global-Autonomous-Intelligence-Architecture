"""
GAIA Tests — Simulation Layer
Tests the full simulation lifecycle:
  sandbox isolation, event injection, assumptions, evaluation, branching.
Pure in-process — no network required.
"""

import pytest
from gaia.simulation.engine import SimulationEngine, Simulation
from gaia.simulation.sandbox import Sandbox
from gaia.simulation.event import Event
from gaia.simulation.assumptions import AssumptionSet
from gaia.simulation.evaluator import SimulationEvaluator
from gaia.simulation.scenario import ScenarioLibrary
from gaia.simulation.branching import BranchManager


# --- Assumptions tests ---

def test_assumption_set_requires_assumptions():
    asm = AssumptionSet("sim-test")
    assert not asm.is_valid()
    asm.add_assumption("Battery costs decline", confidence=0.8)
    assert asm.is_valid()

def test_aggregate_confidence_product():
    asm = AssumptionSet("sim-test")
    asm.add_assumption("A", confidence=0.8)
    asm.add_assumption("B", confidence=0.5)
    # 0.8 * 0.5 = 0.4
    assert asm.aggregate_confidence() == 0.4

def test_critical_unknowns_filtered():
    asm = AssumptionSet("sim-test")
    asm.add_unknown("Fusion",   impact_level="critical")
    asm.add_unknown("Politics", impact_level="medium")
    assert len(asm.critical_unknowns()) == 1


# --- Sandbox isolation tests ---

REAL_STATE = {
    "claim-1": {"statement": "Energy costs are high", "confidence": 0.8, "status": "supported"}
}

def test_sandbox_isolation():
    sandbox = Sandbox()
    sandbox.fork_from(REAL_STATE)
    # Modify sandbox
    sandbox.get_state().claims["claim-1"]["confidence"] = 0.1
    # Real state must be unchanged
    assert REAL_STATE["claim-1"]["confidence"] == 0.8

def test_event_injection():
    sandbox = Sandbox()
    sandbox.fork_from(REAL_STATE)
    event = Event(
        "Reduce energy cost",
        parameters={"energy_cost": 0.3},
        target_claim="claim-1",
    )
    sandbox.inject(event)
    # Metric should be set
    assert sandbox.get_state().metrics.get("energy_cost") == 0.3


# --- Engine tests ---

def test_engine_rejects_simulation_without_assumptions():
    engine = SimulationEngine()
    sim = engine.create("No assumptions sim")
    result = engine.run(sim, REAL_STATE, require_assumptions=True)
    assert "error" in result

def test_engine_runs_valid_simulation():
    engine = SimulationEngine()
    sim = engine.create("Valid sim")
    sim.assumptions.add_assumption("Energy costs are stable", confidence=0.75)
    sim.add_event(Event("Energy cost shock", parameters={"energy_cost": 0.9}))
    result = engine.run(sim, REAL_STATE)
    assert result["completed_at"]
    assert result["outcome"]["outcome_status"] in {
        "plausible_grounded", "plausible", "speculative", "highly_speculative"
    }


# --- Scenario library tests ---

def test_scenario_library_lists_scenarios():
    scenarios = ScenarioLibrary.list()
    assert "pandemic" in scenarios
    assert "cyber_attack" in scenarios
    assert "renewable_expansion" in scenarios

def test_scenario_instantiation():
    engine = SimulationEngine()
    template = ScenarioLibrary.get("renewable_expansion")
    sim = template.instantiate(engine, title="Test Renewable")
    assert sim.assumptions.is_valid()
    assert len(sim.events_plan) >= 1


# --- Branching tests ---

def test_branching_produces_isolated_sims():
    engine  = SimulationEngine()
    manager = BranchManager(engine)
    branches = manager.branch(
        snapshot={"state": REAL_STATE},
        configurations=[
            {
                "title": "optimistic",
                "assumptions": [{"statement": "Costs drop fast", "confidence": 0.9}],
                "events": [{"description": "Cut energy cost", "parameters": {"energy_cost": 0.2}}]
            },
            {
                "title": "pessimistic",
                "assumptions": [{"statement": "Costs stay high", "confidence": 0.6}],
                "events": [{"description": "Raise energy cost", "parameters": {"energy_cost": 0.9}}]
            }
        ]
    )
    assert len(branches) == 2
    # Real state is unchanged
    assert REAL_STATE["claim-1"]["confidence"] == 0.8

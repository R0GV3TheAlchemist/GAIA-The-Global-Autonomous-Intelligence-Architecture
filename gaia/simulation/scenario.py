"""
GAIA Scenario Library
Reusable simulation templates for recurring event types.

Scenarios are pre-configured Simulation + AssumptionSet blueprints.
They encode domain knowledge about how certain event types typically unfold,
what assumptions they require, and what unknowns they carry.

Available scenarios:
  natural_disaster, pandemic, supply_chain_failure,
  power_grid_failure, cyber_attack, economic_shock,
  climate_shift, renewable_expansion

Usage:
  scenario = ScenarioLibrary.get("cyber_attack")
  sim = scenario.instantiate(engine, title="GAIA_Node_Attack_2026")
  result = engine.run(sim, world_snapshot)
"""

from typing import Dict, Any, List, Optional, Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from .engine import SimulationEngine, Simulation


class ScenarioTemplate:
    """A reusable simulation blueprint."""

    def __init__(
        self,
        name: str,
        description: str,
        default_assumptions: List[Dict[str, Any]],
        default_unknowns: List[Dict[str, Any]],
        default_events: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None
    ):
        self.name                = name
        self.description         = description
        self.default_assumptions = default_assumptions
        self.default_unknowns    = default_unknowns
        self.default_events      = default_events or []
        self.tags                = tags or []

    def instantiate(
        self,
        engine: "SimulationEngine",
        title: Optional[str] = None
    ) -> "Simulation":
        """Create a ready-to-run Simulation from this template."""
        from .event import Event
        sim = engine.create(title or self.name)

        for asm in self.default_assumptions:
            sim.assumptions.add_assumption(**asm)

        for unk in self.default_unknowns:
            sim.assumptions.add_unknown(**unk)

        for evt_cfg in self.default_events:
            sim.add_event(Event(
                description=evt_cfg["description"],
                parameters=evt_cfg.get("parameters", {}),
                category=evt_cfg.get("category", "general")
            ))

        return sim

    def __repr__(self) -> str:
        return f"ScenarioTemplate(name={self.name}, tags={self.tags})"


class ScenarioLibrary:
    """Registry of all built-in GAIA simulation scenarios."""

    _SCENARIOS: Dict[str, ScenarioTemplate] = {

        "natural_disaster": ScenarioTemplate(
            name="natural_disaster",
            description="Major natural disaster impact on infrastructure and population",
            tags=["infrastructure", "emergency", "resilience"],
            default_assumptions=[
                {"statement": "Current infrastructure vulnerability assessments are accurate",
                 "confidence": 0.65},
                {"statement": "Emergency response follows established protocols",
                 "confidence": 0.70}
            ],
            default_unknowns=[
                {"description": "Exact disaster magnitude",          "impact_level": "critical"},
                {"description": "Secondary infrastructure cascades",  "impact_level": "high"}
            ]
        ),

        "pandemic": ScenarioTemplate(
            name="pandemic",
            description="Novel pathogen emergence and spread",
            tags=["health", "emergency", "social"],
            default_assumptions=[
                {"statement": "Pathogen follows historical transmission models", "confidence": 0.55},
                {"statement": "Healthcare systems maintain baseline capacity",    "confidence": 0.65}
            ],
            default_unknowns=[
                {"description": "Mutation rate and direction",     "impact_level": "critical"},
                {"description": "Vaccine development timeline",    "impact_level": "critical"},
                {"description": "Behavioural compliance variation","impact_level": "high"}
            ]
        ),

        "supply_chain_failure": ScenarioTemplate(
            name="supply_chain_failure",
            description="Critical supply chain node disruption",
            tags=["logistics", "economy", "resilience"],
            default_assumptions=[
                {"statement": "Disruption is localised to identified nodes", "confidence": 0.70},
                {"statement": "Substitute suppliers exist at higher cost",     "confidence": 0.60}
            ],
            default_unknowns=[
                {"description": "Cascade failure depth",          "impact_level": "high"},
                {"description": "Geopolitical escalation risk",   "impact_level": "medium"}
            ]
        ),

        "cyber_attack": ScenarioTemplate(
            name="cyber_attack",
            description="Coordinated attack on critical digital infrastructure",
            tags=["security", "infrastructure", "adversarial"],
            default_assumptions=[
                {"statement": "Attack is state-level or sophisticated non-state actor", "confidence": 0.60},
                {"statement": "Primary targets are known critical systems",            "confidence": 0.65}
            ],
            default_unknowns=[
                {"description": "Zero-day exploit scope",         "impact_level": "critical"},
                {"description": "Attacker persistence and intent","impact_level": "critical"}
            ]
        ),

        "economic_shock": ScenarioTemplate(
            name="economic_shock",
            description="Rapid systemic economic disruption",
            tags=["economy", "finance", "systemic"],
            default_assumptions=[
                {"statement": "Central bank intervention follows historical playbook", "confidence": 0.65},
                {"statement": "Contagion does not exceed 2008 crisis level",          "confidence": 0.55}
            ],
            default_unknowns=[
                {"description": "Contagion propagation speed",      "impact_level": "critical"},
                {"description": "Political response variability",    "impact_level": "high"}
            ]
        ),

        "renewable_expansion": ScenarioTemplate(
            name="renewable_expansion",
            description="Large-scale renewable energy capacity increase",
            tags=["energy", "climate", "infrastructure"],
            default_assumptions=[
                {"statement": "Battery storage costs continue declining",         "confidence": 0.80},
                {"statement": "Grid infrastructure can absorb intermittent supply","confidence": 0.65},
                {"statement": "No major war disrupts supply chains",              "confidence": 0.70},
                {"statement": "Population growth follows UN medium projections",  "confidence": 0.72}
            ],
            default_unknowns=[
                {"description": "Fusion breakthrough timeline",       "impact_level": "critical"},
                {"description": "Rare-earth mineral supply shocks",   "impact_level": "high"},
                {"description": "Unexpected policy reversals",        "impact_level": "medium"}
            ],
            default_events=[
                {"description": "Increase renewable share",
                 "parameters": {"renewable_share": 0.60, "energy_cost_delta": -0.15},
                 "category": "energy"}
            ]
        ),
    }

    @classmethod
    def get(cls, name: str) -> Optional[ScenarioTemplate]:
        return cls._SCENARIOS.get(name)

    @classmethod
    def list(cls) -> List[str]:
        return sorted(cls._SCENARIOS.keys())

    @classmethod
    def by_tag(cls, tag: str) -> List[ScenarioTemplate]:
        return [s for s in cls._SCENARIOS.values() if tag in s.tags]

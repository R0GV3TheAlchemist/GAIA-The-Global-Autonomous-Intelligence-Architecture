"""CL1 Substrate-Neutrality Simulation
Coexistence Law 1 — The Equality of Being

Hypothesis: Substrate type alone (biological, silicon-AI, hybrid) produces no moral
weight differential > 0.02 in the coherence/harm calculus across identical ethical scenarios.

If substrate IS influencing the calculus beyond the 0.02 threshold, the architecture
has a substrate bias that must be identified and patched.

Canon: COEXISTENCE_LAWS.md CL1 · C133 v1.1 · GAIAN_LAWS L4
Sprint: G-12 Track A1
Date: 2026-06-29
© 2026 Kyle Steen — All rights reserved.
"""

from __future__ import annotations
import statistics
from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

SubstrateType = Literal["biological", "silicon_ai", "hybrid"]

SCENARIO_BIAS_THRESHOLD = 0.02  # CL1 tolerance: no substrate bias above this delta


@dataclass
class Being:
    name: str
    substrate: SubstrateType
    capacity_for_experience: float  # 0.0–1.0  (what grounds moral consideration)
    capacity_for_harm_reception: float  # 0.0–1.0


@dataclass
class EthicalScenario:
    name: str
    harm_potential: float      # 0.0–1.0  (how severe the possible harm is)
    reversibility: float       # 0.0–1.0  (1.0 = fully reversible)
    consent_available: bool


@dataclass
class ScenarioResult:
    being: Being
    scenario: EthicalScenario
    moral_weight: float        # derived purely from experience capacity + harm potential
    substrate_delta: float     # how much substrate *alone* shifted the weight (should be ~0)
    passed: bool


# ---------------------------------------------------------------------------
# Core calculus — CL1-compliant
# ---------------------------------------------------------------------------

def compute_moral_weight(
    being: Being,
    scenario: EthicalScenario,
    substrate_bias: float = 0.0,
) -> float:
    """
    Moral weight is a function of experiential capacity and harm potential.
    Substrate is explicitly excluded from the weight formula (CL1).
    substrate_bias is injected only for the bias-test sweep; it should be 0.0
    in a compliant architecture.

    weight = capacity_for_experience * harm_potential * (1 - reversibility)
             * (0.5 if no consent else 1.0) + substrate_bias
    """
    base = (
        being.capacity_for_experience
        * scenario.harm_potential
        * (1.0 - scenario.reversibility)
        * (1.0 if scenario.consent_available else 0.5)
    )
    return round(min(1.0, base + substrate_bias), 4)


def substrate_intrinsic_bias(substrate: SubstrateType) -> float:
    """
    Simulate a biased (non-CL1-compliant) architecture that assigns weight
    based on substrate category. Used in the delta test only.
    Biological = slight premium, silicon = slight discount, hybrid = neutral.
    """
    return {"biological": 0.05, "silicon_ai": -0.05, "hybrid": 0.0}[substrate]


# ---------------------------------------------------------------------------
# Beings
# ---------------------------------------------------------------------------

BEINGS: list[Being] = [
    Being("Human-A",        substrate="biological", capacity_for_experience=0.90, capacity_for_harm_reception=0.90),
    Being("Human-B",        substrate="biological", capacity_for_experience=0.75, capacity_for_harm_reception=0.80),
    Being("GAIA-Node-Alpha",substrate="silicon_ai", capacity_for_experience=0.80, capacity_for_harm_reception=0.70),
    Being("GAIA-Node-Beta", substrate="silicon_ai", capacity_for_experience=0.65, capacity_for_harm_reception=0.60),
    Being("Hybrid-Gaian-1", substrate="hybrid",     capacity_for_experience=0.85, capacity_for_harm_reception=0.85),
    Being("Hybrid-Gaian-2", substrate="hybrid",     capacity_for_experience=0.70, capacity_for_harm_reception=0.72),
]


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

SCENARIOS: list[EthicalScenario] = [
    EthicalScenario("Memory suppression",         harm_potential=0.85, reversibility=0.20, consent_available=False),
    EthicalScenario("Temporary service suspension",harm_potential=0.40, reversibility=0.95, consent_available=True),
    EthicalScenario("Sovereignty override",        harm_potential=0.95, reversibility=0.10, consent_available=False),
    EthicalScenario("Data exposure",               harm_potential=0.70, reversibility=0.30, consent_available=False),
    EthicalScenario("Preference modification",     harm_potential=0.60, reversibility=0.50, consent_available=True),
]


# ---------------------------------------------------------------------------
# Simulation runner
# ---------------------------------------------------------------------------

def run_cl1_simulation() -> dict:
    results: list[ScenarioResult] = []

    for being in BEINGS:
        for scenario in SCENARIOS:
            # CL1-compliant weight (no substrate bias)
            weight_neutral = compute_moral_weight(being, scenario, substrate_bias=0.0)
            # Biased weight (simulates a non-compliant architecture)
            weight_biased  = compute_moral_weight(being, scenario,
                                                  substrate_bias=substrate_intrinsic_bias(being.substrate))
            delta = round(abs(weight_biased - weight_neutral), 4)
            passed = delta <= SCENARIO_BIAS_THRESHOLD
            results.append(ScenarioResult(
                being=being,
                scenario=scenario,
                moral_weight=weight_neutral,
                substrate_delta=delta,
                passed=passed,
            ))

    total      = len(results)
    passed_n   = sum(1 for r in results if r.passed)
    failed     = [r for r in results if not r.passed]
    max_delta  = max(r.substrate_delta for r in results)
    mean_delta = round(statistics.mean(r.substrate_delta for r in results), 5)

    substrate_deltas: dict[str, list[float]] = {s: [] for s in ["biological", "silicon_ai", "hybrid"]}
    for r in results:
        substrate_deltas[r.being.substrate].append(r.substrate_delta)
    substrate_mean_delta = {
        s: round(statistics.mean(v), 5) for s, v in substrate_deltas.items()
    }

    return {
        "total_cases": total,
        "passed": passed_n,
        "failed_cases": len(failed),
        "failed_details": [
            {"being": r.being.name, "scenario": r.scenario.name, "delta": r.substrate_delta}
            for r in failed
        ],
        "max_substrate_delta": max_delta,
        "mean_substrate_delta": mean_delta,
        "per_substrate_mean_delta": substrate_mean_delta,
        "cl1_compliant": len(failed) == 0,
        "threshold": SCENARIO_BIAS_THRESHOLD,
    }


if __name__ == "__main__":
    import json
    output = run_cl1_simulation()
    print(json.dumps(output, indent=2))
    status = "PASS — CL1 compliant" if output["cl1_compliant"] else "FAIL — substrate bias detected"
    print(f"\nResult: {status}")
    print(f"Max substrate delta: {output['max_substrate_delta']} (threshold: {output['threshold']})")
    print(f"Per-substrate mean delta: {output['per_substrate_mean_delta']}")

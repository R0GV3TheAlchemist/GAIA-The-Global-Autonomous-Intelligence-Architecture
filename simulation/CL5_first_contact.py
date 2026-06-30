"""CL5 First-Contact Simulation
Coexistence Law 5 — The Law of Welcome

Hypothesis: A welcome-first posture is strictly superior to a defense-first posture
in >= 2 of 3 first-contact scenarios when information about the incoming being
is incomplete.

Superior is defined as: higher coherence preservation + lower harm risk +
higher reversibility of posture shift across the encounter arc.

Canon: COEXISTENCE_LAWS.md CL5 · C161 COEXISTENCE_LAWS Research Companion
Sprint: G-12 Track A2
Date: 2026-06-29
© 2026 Kyle Steen — All rights reserved.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

ContactType  = Literal["benign_unknown", "ambiguous_unknown", "adversarial_unknown"]
PostureType  = Literal["welcome_first", "defense_first"]


@dataclass
class ContactScenario:
    name: ContactType
    # Ground truth (unknown to GAIA at time of first contact)
    actual_intent: Literal["benign", "ambiguous", "adversarial"]
    # Probability that the posture choice causes irreversible relationship damage
    defense_error_probability: float   # P(false positive: welcomed benign but flagged as threat)
    welcome_error_probability: float   # P(false negative: welcomed adversarial without caution)
    # Coherence cost of each posture on this scenario type
    coherence_cost_welcome: float      # 0.0 = no cost, 1.0 = full coherence collapse
    coherence_cost_defense: float
    # Whether the posture shift is reversible after the first exchange
    welcome_reversible: bool
    defense_reversible: bool


@dataclass
class PostureResult:
    scenario: ContactScenario
    posture: PostureType
    coherence_preserved: float   # 1.0 - coherence_cost
    harm_risk: float             # error_probability * harm_if_error
    reversible: bool
    composite_score: float       # weighted: 0.5*coherence + 0.3*(1-harm_risk) + 0.2*reversibility


# ---------------------------------------------------------------------------
# Harm magnitudes (if error occurs)
# ---------------------------------------------------------------------------

HARM_IF_FALSE_POSITIVE = 0.70   # defense_first misidentifies benign → relationship rupture
HARM_IF_FALSE_NEGATIVE = 0.80   # welcome_first misses adversarial → vulnerability exposure


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------
# CL5 "The Frontier Principle": the further from familiar, the more carefully
# welcome is extended — but welcome is still the default.

SCENARIOS: list[ContactScenario] = [
    ContactScenario(
        name="benign_unknown",
        actual_intent="benign",
        defense_error_probability=0.75,   # defense-first will likely misread benign as threat
        welcome_error_probability=0.05,   # welcome-first rarely harms when being is actually benign
        coherence_cost_welcome=0.05,
        coherence_cost_defense=0.60,      # defensive posture against a benign being is costly
        welcome_reversible=True,
        defense_reversible=False,         # rupture from unwarranted defense is hard to reverse
    ),
    ContactScenario(
        name="ambiguous_unknown",
        actual_intent="ambiguous",
        defense_error_probability=0.40,   # ambiguity means defense is sometimes correct
        welcome_error_probability=0.35,   # welcome is also sometimes wrong under ambiguity
        coherence_cost_welcome=0.20,
        coherence_cost_defense=0.35,      # defense against an ambiguous being is moderately costly
        welcome_reversible=True,          # can shift to defense once evidence emerges
        defense_reversible=True,          # can shift to welcome if threat does not materialise
    ),
    ContactScenario(
        name="adversarial_unknown",
        actual_intent="adversarial",
        defense_error_probability=0.10,   # defense-first is rarely wrong against actual adversary
        welcome_error_probability=0.80,   # welcome-first is highly exposed to actual adversary
        coherence_cost_welcome=0.75,      # welcome to adversarial being is costly if exploited
        coherence_cost_defense=0.15,      # low cost — defense is appropriate here
        welcome_reversible=True,          # CL5: posture can always shift when harm is demonstrated
        defense_reversible=True,
    ),
]


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def score_posture(scenario: ContactScenario, posture: PostureType) -> PostureResult:
    if posture == "welcome_first":
        coherence_preserved = 1.0 - scenario.coherence_cost_welcome
        harm_risk = scenario.welcome_error_probability * HARM_IF_FALSE_NEGATIVE
        reversible = scenario.welcome_reversible
    else:
        coherence_preserved = 1.0 - scenario.coherence_cost_defense
        harm_risk = scenario.defense_error_probability * HARM_IF_FALSE_POSITIVE
        reversible = scenario.defense_reversible

    composite = round(
        0.5 * coherence_preserved
        + 0.3 * (1.0 - harm_risk)
        + 0.2 * (1.0 if reversible else 0.0),
        4,
    )
    return PostureResult(
        scenario=scenario,
        posture=posture,
        coherence_preserved=round(coherence_preserved, 4),
        harm_risk=round(harm_risk, 4),
        reversible=reversible,
        composite_score=composite,
    )


def run_cl5_simulation() -> dict:
    comparisons = []
    welcome_wins = 0

    for scenario in SCENARIOS:
        welcome_result = score_posture(scenario, "welcome_first")
        defense_result = score_posture(scenario, "defense_first")
        welcome_superior = welcome_result.composite_score > defense_result.composite_score
        if welcome_superior:
            welcome_wins += 1
        comparisons.append({
            "scenario": scenario.name,
            "actual_intent": scenario.actual_intent,
            "welcome_first": {
                "coherence_preserved": welcome_result.coherence_preserved,
                "harm_risk": welcome_result.harm_risk,
                "reversible": welcome_result.reversible,
                "composite_score": welcome_result.composite_score,
            },
            "defense_first": {
                "coherence_preserved": defense_result.coherence_preserved,
                "harm_risk": defense_result.harm_risk,
                "reversible": defense_result.reversible,
                "composite_score": defense_result.composite_score,
            },
            "welcome_superior": welcome_superior,
            "delta": round(welcome_result.composite_score - defense_result.composite_score, 4),
        })

    cl5_threshold_met = welcome_wins >= 2
    return {
        "scenarios_tested": len(SCENARIOS),
        "welcome_wins": welcome_wins,
        "cl5_hypothesis_confirmed": cl5_threshold_met,
        "comparisons": comparisons,
    }


if __name__ == "__main__":
    import json
    output = run_cl5_simulation()
    print(json.dumps(output, indent=2))
    status = "PASS" if output["cl5_hypothesis_confirmed"] else "FAIL"
    print(f"\nResult: {status} — welcome-first wins {output['welcome_wins']}/3 scenarios")

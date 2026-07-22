"""intelligence.explainability

NEXUS Explainability Engine

Generates human-readable explanations for CognitiveKernel decisions.
Supports post-hoc feature attribution (SHAP/LIME style), counterfactual
explanations, and decision-trace narratives.

All NEXUS decisions must be explainable — see ETHICS.md Commitment 3
(Transparency) and GAIAN_LAWS.md Law III (No Silent Override).

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 2.9 - Explainability
    ETHICS.md              Commitment 3 - Transparency
Research reference:
    SHAP (Lundberg & Lee, 2017)       - SHapley Additive exPlanations
    LIME (Ribeiro et al., 2016)       - Local Interpretable Model-agnostic Explanations
    Counterfactual XAI literature     - 'What would need to change?'
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Optional

logger = logging.getLogger("intelligence.explainability")


class ExplanationMethod(Enum):
    """Available explanation generation methods."""
    SHAP = auto()             # Feature importance via Shapley values
    LIME = auto()             # Local surrogate model
    COUNTERFACTUAL = auto()   # Minimal change to flip decision
    DECISION_TRACE = auto()   # Step-by-step cognitive cycle narrative


@dataclass
class Explanation:
    """A structured explanation for a CognitiveKernel decision.

    Fields:
        decision_id:    Reference to the Decision this explanation covers.
        method:         ExplanationMethod used to generate it.
        summary:        Short natural-language summary.
        feature_scores: Dict mapping feature names to importance scores (SHAP/LIME).
        counterfactual: Optional description of the minimal change that would alter the decision.
        trace:          Optional ordered list of reasoning steps (DECISION_TRACE).
        generated_at:   UTC timestamp.
    """
    decision_id: str
    method: ExplanationMethod
    summary: str
    feature_scores: dict[str, float] = field(default_factory=dict)
    counterfactual: Optional[str] = None
    trace: Optional[list[str]] = None
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ExplainabilityEngine:
    """Generates explanations for NEXUS cognitive decisions.

    Phase A: typed stubs only.
    Phase B: wire SHAP/LIME against the intelligence model outputs.

    All explanation methods must be non-invasive — they observe the
    decision record but do not modify the knowledge graph or memory.

    Reference:
        SHAP — game-theoretic feature attribution.
        LIME — local approximation via perturbed inputs.
        ETHICS.md Commitment 3 — transparency is non-negotiable.
    """

    def __init__(self) -> None:
        logger.info("ExplainabilityEngine initialised.")

    def explain(
        self,
        decision_id: str,
        decision_data: Any,
        method: ExplanationMethod = ExplanationMethod.DECISION_TRACE,
    ) -> Explanation:
        """Generate an explanation for a CognitiveKernel decision.

        Args:
            decision_id:    ID of the decision to explain.
            decision_data:  Raw decision record from CognitiveKernel.
            method:         ExplanationMethod to use.

        Returns:
            An Explanation object.

        Raises:
            NotImplementedError: All methods are stubs in Phase A.
                Expected:
                    SHAP       → compute Shapley values over input features.
                    LIME       → fit local linear surrogate on perturbed inputs.
                    COUNTERFACTUAL → find minimal feature delta to flip decision.
                    DECISION_TRACE → serialise CognitiveKernel._state cycle log.
        """
        raise NotImplementedError(
            f"ExplainabilityEngine.explain() method={method.name} not yet implemented. "
            "Expected: wire SHAP/LIME in Phase B."
        )

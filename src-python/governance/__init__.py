"""governance — Governance engine and policy evaluator

Provides:
  - GovernanceEngine: the central policy enforcement point for NEXUS.
  - PolicyEvaluator: evaluates actions against governance rules.
  - GovernanceConfig: configuration for policy sources and enforcement mode.

Phase C — all methods are stubbed.

Design references
-----------------
- NEXUS GOVERNANCE.md + GOVERNANCESPEC.md: policy taxonomy.
- EU AI Act (2024): transparency, human oversight, risk classification.
- NIST AI RMF: Govern, Map, Measure, Manage lifecycle.
- IEEE Ethically Aligned Design: value-sensitive policy encoding.
- GAIAN Coexistence Laws: no silent override, consent-first principles.
"""
from __future__ import annotations
from governance.engine import GovernanceEngine, PolicyEvaluator, GovernanceConfig, PolicyDecision

__all__ = ["GovernanceEngine", "PolicyEvaluator", "GovernanceConfig", "PolicyDecision"]

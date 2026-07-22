"""
intelligence — NEXUS Intelligence Layer

Root package for the NEXUS cognitive intelligence layer. Provides the
high-level abstractions for goal-directed reasoning, agent lifecycle
management, sensor fusion, episodic/semantic/procedural memory, and
explainable AI decision tracing.

Architecture reference: NEXUS_UNIVERSAL_OS.md Domain 2 — Intelligence
Ethics reference:       ETHICS.md Commitment 6 — Explainability by Default
GAIAN law reference:    GAIAN_LAWS.md Law V — Transparent Cognition
"""
from __future__ import annotations

__version__ = "0.1.0"
__author__  = "R0GV3TheAlchemist"
__license__ = "See LICENSE"

from intelligence.cognitive_kernel import GoalStack, ReasoningEngine, AuditLog
from intelligence.agent            import BaseAgent, AgentLifecycle, AgentCoalition
from intelligence.perception       import SensorFusion, WorldModel, UncertaintyQuantifier
from intelligence.knowledge_graph  import EpisodicMemory, SemanticMemory, ProceduralMemory
from intelligence.explainability   import DecisionTrace, ExplanationSummary

__all__ = [
    "GoalStack", "ReasoningEngine", "AuditLog",
    "BaseAgent", "AgentLifecycle", "AgentCoalition",
    "SensorFusion", "WorldModel", "UncertaintyQuantifier",
    "EpisodicMemory", "SemanticMemory", "ProceduralMemory",
    "DecisionTrace", "ExplanationSummary",
]

"""intelligence

NEXUS Cognitive Intelligence Layer

The intelligence package provides the higher-order cognitive capabilities
of NEXUS: perception, reasoning, memory-backed knowledge graphs, agent
orchestration, and explainability.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 2 - Intelligence Layer
    ARCHITECTURE.md        Cognitive stack

Research reference:
    Zep/Graphiti (arXiv:2501.13956)  - bi-temporal knowledge graph memory
    neo4j-agent-memory (PyPI)         - graph-native agent memory
    MemGPT (arXiv:2310.08560)         - tiered memory paging
    SHAP / LIME                        - explainability methods for XAI
"""
from __future__ import annotations

from intelligence.cognitive_kernel import CognitiveKernel, CognitiveState
from intelligence.agent import Agent, AgentConfig, AgentStatus
from intelligence.perception import PerceptionEngine, Percept
from intelligence.knowledge_graph import KnowledgeGraph, MemoryType, GraphNode, GraphEdge
from intelligence.explainability import ExplainabilityEngine, Explanation

__all__ = [
    "CognitiveKernel",
    "CognitiveState",
    "Agent",
    "AgentConfig",
    "AgentStatus",
    "PerceptionEngine",
    "Percept",
    "KnowledgeGraph",
    "MemoryType",
    "GraphNode",
    "GraphEdge",
    "ExplainabilityEngine",
    "Explanation",
]

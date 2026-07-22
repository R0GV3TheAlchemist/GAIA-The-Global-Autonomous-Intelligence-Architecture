"""intelligence.knowledge_graph

NEXUS Knowledge Graph

Provides a three-tier memory model (Episodic / Semantic / Procedural)
backed by a graph store. Designed to be compatible with Zep/Graphiti's
bi-temporal model and neo4j-agent-memory as the production backing store.

Memory taxonomy (cognitive science + Zep mapping):
    Episodic   → specific past events with temporal context (Zep episodic subgraph)
    Semantic   → general facts, concepts, entity relationships (Zep semantic subgraph)
    Procedural → skills, how-to patterns, learned routines

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 2.4 - Knowledge Graph
Research reference:
    Zep/Graphiti arXiv:2501.13956   - bi-temporal graph memory (18.5× accuracy)
    neo4j-agent-memory PyPI         - graph-native agent memory backing store
    Portable Agent Memory arXiv:2605.11032 - Merkle-DAG provenance
    MemGPT arXiv:2310.08560         - tiered episodic/semantic paging
    Zylos AI May 2026               - 36-46% accuracy gains with KG world models
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Optional

logger = logging.getLogger("intelligence.knowledge_graph")


class MemoryType(Enum):
    """Three-tier memory taxonomy."""
    EPISODIC = auto()
    SEMANTIC = auto()
    PROCEDURAL = auto()


@dataclass
class GraphNode:
    """A node in the NEXUS knowledge graph.

    Fields:
        node_id:     Unique UUID4 identifier.
        memory_type: MemoryType classification.
        label:       Short human-readable label.
        data:        Node payload (fact, event summary, skill descriptor).
        created_at:  UTC creation timestamp.
        valid_from:  Bi-temporal 'fact time' — when this fact became true in the world.
        valid_to:    Bi-temporal end of fact validity (None = still valid).
    """
    label: str
    memory_type: MemoryType
    data: Any = None
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


@dataclass
class GraphEdge:
    """A directed relationship between two GraphNodes.

    Fields:
        edge_id:     Unique UUID4.
        source_id:   node_id of the source node.
        target_id:   node_id of the target node.
        relation:    Relationship type label (e.g. 'causes', 'related_to').
        weight:      Optional edge weight for graph algorithms.
        created_at:  UTC creation timestamp.
    """
    source_id: str
    target_id: str
    relation: str
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    weight: float = 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeGraph:
    """Three-tier in-process knowledge graph for NEXUS intelligence.

    Phase A: in-memory dict-based implementation.
    Phase B: swap backing store to neo4j-agent-memory or Zep/Graphiti.

    Reference:
        Zep bi-temporal model — every edge carries two timestamps.
        Portable Agent Memory — provenance chain for tamper-evidence.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []
        logger.info("KnowledgeGraph initialised (in-memory).")

    def add_node(self, node: GraphNode) -> None:
        """Add a GraphNode to the knowledge graph."""
        self._nodes[node.node_id] = node
        logger.debug("KnowledgeGraph: added node '%s' (%s).", node.label, node.memory_type)

    def add_edge(self, edge: GraphEdge) -> None:
        """Add a directed GraphEdge to the knowledge graph.

        Raises:
            KeyError: If source_id or target_id do not exist as nodes.
        """
        if edge.source_id not in self._nodes:
            raise KeyError(f"Source node not found: {edge.source_id}")
        if edge.target_id not in self._nodes:
            raise KeyError(f"Target node not found: {edge.target_id}")
        self._edges.append(edge)
        logger.debug(
            "KnowledgeGraph: edge %s --[%s]--> %s.",
            edge.source_id, edge.relation, edge.target_id,
        )

    def query(self, memory_type: Optional[MemoryType] = None, label_contains: str = "") -> list[GraphNode]:
        """Query nodes by memory type and/or label substring.

        Args:
            memory_type:    Filter by MemoryType (None = all types).
            label_contains: Case-insensitive substring filter on node.label.

        Returns:
            List of matching GraphNode instances.
        """
        results = list(self._nodes.values())
        if memory_type is not None:
            results = [n for n in results if n.memory_type == memory_type]
        if label_contains:
            lc = label_contains.lower()
            results = [n for n in results if lc in n.label.lower()]
        return results

    def neighbors(self, node_id: str) -> list[GraphNode]:
        """Return all direct neighbour nodes of the given node.

        Args:
            node_id: UUID4 of the source node.

        Returns:
            List of GraphNode instances reachable via outbound edges.

        Raises:
            NotImplementedError: Graph traversal not yet optimised.
                Expected: in Phase B use neo4j MATCH (n)-[:*]->(m) pattern.
        """
        raise NotImplementedError(
            "KnowledgeGraph.neighbors() not yet implemented. "
            "Expected: filter self._edges by source_id, resolve target nodes."
        )

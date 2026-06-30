"""
GAIA World Graph
NetworkX-backed knowledge graph for entity-level world modelling.
The runtime graph of what GAIA believes exists and how it connects.
"""

try:
    import networkx as nx
    _NX_AVAILABLE = True
except ImportError:
    _NX_AVAILABLE = False

from typing import Dict, Any, List, Optional


class WorldGraph:
    """
    NetworkX-backed directed graph of entities and relationships.
    Falls back to dict-based adjacency if NetworkX is not installed.

    Upgrade path:
      v0.2: NetworkX in-memory graph  ← THIS VERSION
      v0.3: Neo4j persistent graph
    """

    def __init__(self):
        if _NX_AVAILABLE:
            self._graph = nx.DiGraph()
            self._backend = "networkx"
        else:
            self._graph = {"nodes": {}, "edges": []}
            self._backend = "dict"
        print(f"  WorldGraph initialised (backend: {self._backend})")

    def add_entity_node(self, entity) -> None:
        """Add an entity as a graph node."""
        if _NX_AVAILABLE:
            self._graph.add_node(entity.id, **entity.to_node_attrs())
        else:
            self._graph["nodes"][entity.id] = entity.to_node_attrs()

    def add_relationship_edge(self, rel) -> None:
        """Add a relationship as a directed edge."""
        if _NX_AVAILABLE:
            self._graph.add_edge(
                rel.from_entity,
                rel.to_entity,
                **rel.to_edge_attrs()
            )
        else:
            self._graph["edges"].append(rel.to_edge_attrs())

    def get_neighbours(self, entity_id: str) -> List[str]:
        """Return all directly connected entity IDs."""
        if _NX_AVAILABLE:
            successors   = list(self._graph.successors(entity_id))
            predecessors = list(self._graph.predecessors(entity_id))
            return list(set(successors + predecessors))
        return []

    def shortest_path(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """Find shortest path between two entities (multi-hop reasoning)."""
        if not _NX_AVAILABLE:
            return None
        try:
            return nx.shortest_path(self._graph, from_id, to_id)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def stats(self) -> Dict[str, Any]:
        if _NX_AVAILABLE:
            return {
                "nodes":   self._graph.number_of_nodes(),
                "edges":   self._graph.number_of_edges(),
                "backend": self._backend
            }
        return {
            "nodes":   len(self._graph["nodes"]),
            "edges":   len(self._graph["edges"]),
            "backend": self._backend
        }

    def __repr__(self) -> str:
        s = self.stats()
        return f"WorldGraph(nodes={s['nodes']}, edges={s['edges']}, backend={s['backend']})"

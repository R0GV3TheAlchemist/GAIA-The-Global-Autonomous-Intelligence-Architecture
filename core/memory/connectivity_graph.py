from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from math import log1p
from typing import DefaultDict, Dict, Iterable, List, Sequence, Set, Tuple


@dataclass(slots=True)
class ConnectivityNode:
    """Represents structural connectivity for a memory node."""

    memory_id: str
    neighbors: Set[str] = field(default_factory=set)
    inbound: int = 0
    outbound: int = 0

    @property
    def degree(self) -> int:
        return len(self.neighbors)


class ConnectivityGraph:
    """Lightweight graph used to weight memories by structural linkage.

    The graph is intentionally simple so it can be layered over the existing
    GAIA memory store without forcing a new persistence model. Nodes are memory
    identifiers; edges are typed relationships such as follow-up, refinement,
    contradiction, or co-reference.
    """

    def __init__(self) -> None:
        self._adjacency: DefaultDict[str, Set[str]] = defaultdict(set)
        self._reverse: DefaultDict[str, Set[str]] = defaultdict(set)

    def add_memory(self, memory_id: str) -> None:
        self._adjacency.setdefault(memory_id, set())
        self._reverse.setdefault(memory_id, set())

    def add_edge(self, source_id: str, target_id: str) -> None:
        if not source_id or not target_id or source_id == target_id:
            return
        self.add_memory(source_id)
        self.add_memory(target_id)
        self._adjacency[source_id].add(target_id)
        self._reverse[target_id].add(source_id)

    def add_edges(self, source_id: str, related_ids: Iterable[str]) -> None:
        for target_id in related_ids:
            self.add_edge(source_id, target_id)

    def neighbors(self, memory_id: str) -> Set[str]:
        return set(self._adjacency.get(memory_id, set())) | set(self._reverse.get(memory_id, set()))

    def connectivity(self, memory_id: str) -> ConnectivityNode:
        outbound = len(self._adjacency.get(memory_id, set()))
        inbound = len(self._reverse.get(memory_id, set()))
        return ConnectivityNode(
            memory_id=memory_id,
            neighbors=self.neighbors(memory_id),
            inbound=inbound,
            outbound=outbound,
        )

    def weight(self, memory_id: str) -> float:
        node = self.connectivity(memory_id)
        if node.degree == 0:
            return 1.0
        return 1.0 + log1p(node.degree) + 0.25 * log1p(node.inbound + node.outbound)

    def rank(self, memory_ids: Sequence[str]) -> List[Tuple[str, float]]:
        ranked = [(memory_id, self.weight(memory_id)) for memory_id in memory_ids]
        return sorted(ranked, key=lambda item: item[1], reverse=True)

    def snapshot(self) -> Dict[str, Dict[str, List[str]]]:
        return {
            memory_id: {
                "outbound": sorted(self._adjacency.get(memory_id, set())),
                "inbound": sorted(self._reverse.get(memory_id, set())),
            }
            for memory_id in sorted(set(self._adjacency) | set(self._reverse))
        }

    @classmethod
    def from_relationship_map(cls, relationships: Dict[str, Iterable[str]]) -> "ConnectivityGraph":
        graph = cls()
        for source_id, related_ids in relationships.items():
            graph.add_memory(source_id)
            graph.add_edges(source_id, related_ids)
        return graph

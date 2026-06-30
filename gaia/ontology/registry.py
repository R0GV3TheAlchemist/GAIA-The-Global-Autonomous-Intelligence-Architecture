"""
GAIA Ontology Registry
The central store for all entities and relationships in the GAIA world model.
This is the runtime ontology — everything GAIA knows about what exists.
"""

from typing import Dict, List, Optional
from .entity import Entity
from .relationship import Relationship


class OntologyRegistry:
    """
    The Ontology Registry is GAIA's in-memory world model kernel.

    It holds:
    - All entities (typed objects in GAIA's reality)
    - All relationships (typed, confidence-weighted connections)

    In production this will be backed by a graph database (Neo4j or equivalent).
    In v0.1 it operates as an in-memory store with dict-based indexing.
    """

    def __init__(self):
        self._entities: Dict[str, Entity] = {}
        self._relationships: Dict[str, Relationship] = {}
        self._entity_type_index: Dict[str, List[str]] = {}   # type → [entity_ids]
        self._relationship_index: Dict[str, List[str]] = {}  # entity_id → [rel_ids]

    # ——— Entity operations ———

    def add_entity(self, entity: Entity) -> None:
        self._entities[entity.id] = entity
        self._entity_type_index.setdefault(entity.type, []).append(entity.id)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self._entities.get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        ids = self._entity_type_index.get(entity_type, [])
        return [self._entities[eid] for eid in ids if eid in self._entities]

    def all_entities(self) -> List[Entity]:
        return list(self._entities.values())

    # ——— Relationship operations ———

    def add_relationship(self, rel: Relationship) -> None:
        self._relationships[rel.id] = rel
        self._relationship_index.setdefault(rel.from_entity_id, []).append(rel.id)
        self._relationship_index.setdefault(rel.to_entity_id, []).append(rel.id)

    def get_relationship(self, rel_id: str) -> Optional[Relationship]:
        return self._relationships.get(rel_id)

    def get_relationships_for_entity(self, entity_id: str) -> List[Relationship]:
        rel_ids = self._relationship_index.get(entity_id, [])
        return [self._relationships[rid] for rid in rel_ids if rid in self._relationships]

    def get_outgoing_relationships(self, entity_id: str) -> List[Relationship]:
        return [
            r for r in self.get_relationships_for_entity(entity_id)
            if r.from_entity_id == entity_id
        ]

    def get_incoming_relationships(self, entity_id: str) -> List[Relationship]:
        return [
            r for r in self.get_relationships_for_entity(entity_id)
            if r.to_entity_id == entity_id
        ]

    # ——— Stats ———

    def stats(self) -> Dict:
        return {
            "total_entities": len(self._entities),
            "total_relationships": len(self._relationships),
            "entity_types": {k: len(v) for k, v in self._entity_type_index.items()}
        }

    def __repr__(self) -> str:
        return (f"OntologyRegistry("
                f"entities={len(self._entities)}, "
                f"relationships={len(self._relationships)})")

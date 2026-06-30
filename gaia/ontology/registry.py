"""
GAIA Ontology Registry
The structured model of what exists in the GAIA world.
This is the heart of the ontology layer —
the runtime store for all entities, relationships, and ontology-bound claims.
"""

from typing import Dict, List, Optional, Any
from .entity import Entity
from .relationship import Relationship
from .claim import Claim


class OntologyRegistry:
    """
    Holds the full GAIA ontology at runtime:
    - Entities (typed objects in GAIA's world)
    - Relationships (typed, confidence-weighted connections)
    - Claims (assertions bound to entities)

    Before ontology: GAIA was a graph of text claims.
    After ontology: GAIA is a structured model of reality
    with claims layered on top.

    This enables:
    - Entity-level reasoning
    - Contradiction across concepts (not just text)
    - Multi-domain structured truth evaluation
    - Causal graph construction
    """

    def __init__(self):
        self._entities: Dict[str, Entity] = {}
        self._relationships: Dict[str, Relationship] = {}
        self._claims: Dict[str, Claim] = {}
        # Indices
        self._entity_type_idx: Dict[str, List[str]] = {}
        self._entity_claims_idx: Dict[str, List[str]] = {}  # entity_id → [claim_ids]
        self._entity_rel_idx: Dict[str, List[str]] = {}     # entity_id → [rel_ids]

    # ——— Entity CRUD ———

    def add_entity(self, entity: Entity) -> None:
        self._entities[entity.id] = entity
        self._entity_type_idx.setdefault(entity.type, []).append(entity.id)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self._entities.get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        return [
            self._entities[eid]
            for eid in self._entity_type_idx.get(entity_type, [])
            if eid in self._entities
        ]

    def find_entity_by_name(self, name: str) -> Optional[Entity]:
        name_lower = name.lower()
        for e in self._entities.values():
            if e.name.lower() == name_lower:
                return e
        return None

    def all_entities(self) -> List[Entity]:
        return list(self._entities.values())

    # ——— Relationship CRUD ———

    def add_relationship(self, rel: Relationship) -> None:
        self._relationships[rel.id] = rel
        self._entity_rel_idx.setdefault(rel.from_entity, []).append(rel.id)
        self._entity_rel_idx.setdefault(rel.to_entity, []).append(rel.id)

    def get_related(self, entity_id: str) -> List[Relationship]:
        """All relationships connected to an entity (in or out)."""
        rel_ids = self._entity_rel_idx.get(entity_id, [])
        return [self._relationships[rid] for rid in rel_ids if rid in self._relationships]

    def get_outgoing(self, entity_id: str) -> List[Relationship]:
        return [r for r in self.get_related(entity_id) if r.from_entity == entity_id]

    def get_incoming(self, entity_id: str) -> List[Relationship]:
        return [r for r in self.get_related(entity_id) if r.to_entity == entity_id]

    def get_relationships_by_type(self, rel_type: str) -> List[Relationship]:
        return [r for r in self._relationships.values() if r.type == rel_type]

    # ——— Claim CRUD ———

    def add_claim(self, claim: Claim) -> None:
        self._claims[claim.id] = claim
        for eid in claim.entities:
            self._entity_claims_idx.setdefault(eid, []).append(claim.id)

    def get_claims_for_entity(self, entity_id: str) -> List[Claim]:
        claim_ids = self._entity_claims_idx.get(entity_id, [])
        return [self._claims[cid] for cid in claim_ids if cid in self._claims]

    def all_claims(self) -> List[Claim]:
        return list(self._claims.values())

    # ——— Cross-entity reasoning ———

    def get_entity_neighbourhood(
        self,
        entity_id: str,
        depth: int = 1
    ) -> Dict[str, Any]:
        """
        Return the immediate neighbourhood of an entity:
        its relationships + connected entities + all claims about it.
        Foundation for multi-hop reasoning in v0.3+.
        """
        entity = self.get_entity(entity_id)
        if not entity:
            return {"error": f"Entity {entity_id} not found"}

        rels = self.get_related(entity_id)
        connected_ids = set()
        for r in rels:
            connected_ids.add(r.from_entity)
            connected_ids.add(r.to_entity)
        connected_ids.discard(entity_id)

        return {
            "entity": entity,
            "relationships": rels,
            "connected_entities": [
                self._entities[eid] for eid in connected_ids
                if eid in self._entities
            ],
            "claims": self.get_claims_for_entity(entity_id)
        }

    # ——— Stats ———

    def stats(self) -> Dict[str, Any]:
        return {
            "total_entities":      len(self._entities),
            "total_relationships": len(self._relationships),
            "total_claims":        len(self._claims),
            "entity_types":        {k: len(v) for k, v in self._entity_type_idx.items()},
        }

    def __repr__(self) -> str:
        return (
            f"OntologyRegistry("
            f"entities={len(self._entities)}, "
            f"relationships={len(self._relationships)}, "
            f"claims={len(self._claims)})"
        )

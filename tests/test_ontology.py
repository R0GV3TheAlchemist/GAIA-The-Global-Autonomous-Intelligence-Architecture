"""
Tests for GAIA Ontology System
Entity model, relationship model, and registry.
"""

import pytest
from gaia.ontology.entity import Entity
from gaia.ontology.relationship import Relationship, RELATIONSHIP_TYPES
from gaia.ontology.registry import OntologyRegistry


def test_entity_creation():
    entity = Entity.create(
        type="KnowledgeNode",
        name="Biophotonic Coherence",
        attributes={"domain": "biophotonics"},
        epistemic_status="speculative-grounded"
    )
    assert entity.id is not None
    assert entity.type == "KnowledgeNode"
    assert entity.name == "Biophotonic Coherence"
    assert entity.epistemic_status == "speculative-grounded"


def test_relationship_creation():
    e1 = Entity.create(type="Concept", name="Crystal Alchemy")
    e2 = Entity.create(type="Concept", name="Biophotonic Coherence")
    rel = Relationship.create(
        from_entity_id=e1.id,
        to_entity_id=e2.id,
        rel_type="ENABLES",
        confidence=0.71
    )
    assert rel.type == "ENABLES"
    assert rel.confidence == 0.71


def test_invalid_relationship_type():
    with pytest.raises(ValueError):
        Relationship.create(
            from_entity_id="a",
            to_entity_id="b",
            rel_type="INVENTED_TYPE"
        )


def test_registry_add_and_retrieve():
    registry = OntologyRegistry()
    entity = Entity.create(type="Agent", name="GAIA Core")
    registry.add_entity(entity)
    retrieved = registry.get_entity(entity.id)
    assert retrieved is not None
    assert retrieved.name == "GAIA Core"


def test_registry_type_index():
    registry = OntologyRegistry()
    for name in ["Water Stage", "Fire Stage", "Air Stage"]:
        registry.add_entity(Entity.create(type="ElementalStage", name=name))
    stages = registry.get_entities_by_type("ElementalStage")
    assert len(stages) == 3

"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NEXUS — The Universal Autonomous Intelligence Architecture
  GAIA  — The Global Autonomous Intelligence Architecture

  Author   : Kyle Steen
  GitHub   : R0GV3TheAlchemist (https://github.com/R0GV3TheAlchemist)
  Email    : xxkylesteenxx@outlook.com
  Project  : NEXUS / GAIA
  License  : All Rights Reserved © 2026 Kyle Steen
             Unauthorized use, reproduction, or distribution
             of this file or its contents is strictly prohibited.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

knowledge_graph.py — NEXUS Knowledge Graph.

Three memory subsystems mirroring cognitive science:
  - EpisodicMemory  : event sequences with timestamps
  - SemanticMemory  : typed concept graph (RDF-compatible)
  - ProceduralMemory: executable skill routines
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import UUID, uuid4
import time


# ─── Episodic Memory ─────────────────────────────────────────────────────────

@dataclass
class Episode:
    """A single timestamped event in episodic memory."""
    episode_id: UUID = field(default_factory=uuid4)
    timestamp: float = field(default_factory=time.time)
    description: str = ""
    entities: List[str] = field(default_factory=list)
    payload: Any = None
    tags: List[str] = field(default_factory=list)


class EpisodicMemory:
    """
    Ordered log of episodic events. Supports temporal range queries
    and tag-based filtering.
    """

    def __init__(self) -> None:
        self._episodes: List[Episode] = []

    def record(self, description: str, entities: List[str] = None,
               payload: Any = None, tags: List[str] = None) -> Episode:
        ep = Episode(
            description=description,
            entities=entities or [],
            payload=payload,
            tags=tags or [],
        )
        self._episodes.append(ep)
        return ep

    def query_by_tag(self, tag: str) -> List[Episode]:
        return [e for e in self._episodes if tag in e.tags]

    def query_by_time_range(self, start: float, end: float) -> List[Episode]:
        return [e for e in self._episodes if start <= e.timestamp <= end]

    def recent(self, n: int = 10) -> List[Episode]:
        return self._episodes[-n:]

    def __len__(self) -> int:
        return len(self._episodes)


# ─── Semantic Memory ──────────────────────────────────────────────────────────

@dataclass
class Concept:
    """A node in the semantic concept graph."""
    concept_id: UUID = field(default_factory=uuid4)
    label: str = ""
    concept_type: str = "Entity"
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Relation:
    """A typed directed edge between two Concepts."""
    relation_id: UUID = field(default_factory=uuid4)
    subject_id: UUID = field(default_factory=uuid4)
    predicate: str = ""
    object_id: UUID = field(default_factory=uuid4)
    weight: float = 1.0


class SemanticMemory:
    """
    RDF-compatible typed concept graph.

    Nodes are Concepts; edges are typed Relations.
    Supports SPARQL-style triple queries: (subject, predicate, object).
    """

    def __init__(self) -> None:
        self._concepts: Dict[UUID, Concept] = {}
        self._relations: List[Relation] = []

    def add_concept(self, label: str, concept_type: str = "Entity",
                    attributes: Dict[str, Any] = None) -> Concept:
        c = Concept(label=label, concept_type=concept_type,
                    attributes=attributes or {})
        self._concepts[c.concept_id] = c
        return c

    def add_relation(self, subject: Concept, predicate: str,
                     obj: Concept, weight: float = 1.0) -> Relation:
        r = Relation(subject_id=subject.concept_id, predicate=predicate,
                     object_id=obj.concept_id, weight=weight)
        self._relations.append(r)
        return r

    def query(self, subject_id: Optional[UUID] = None,
              predicate: Optional[str] = None,
              object_id: Optional[UUID] = None) -> List[Relation]:
        results = self._relations
        if subject_id:
            results = [r for r in results if r.subject_id == subject_id]
        if predicate:
            results = [r for r in results if r.predicate == predicate]
        if object_id:
            results = [r for r in results if r.object_id == object_id]
        return results

    def get_concept(self, concept_id: UUID) -> Optional[Concept]:
        return self._concepts.get(concept_id)


# ─── Procedural Memory ───────────────────────────────────────────────────────

@dataclass
class Skill:
    """An executable procedural skill routine."""
    skill_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    routine: Optional[Callable] = None
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)

    def execute(self, *args, **kwargs) -> Any:
        if self.routine is None:
            raise NotImplementedError(f"Skill '{self.name}' has no routine attached.")
        return self.routine(*args, **kwargs)


class ProceduralMemory:
    """
    Registry of executable skill routines.

    Skills are indexed by name for fast lookup. Each skill carries
    pre/postcondition contracts for runtime verification.
    """

    def __init__(self) -> None:
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)

    def execute(self, name: str, *args, **kwargs) -> Any:
        skill = self.get(name)
        if skill is None:
            raise KeyError(f"No skill named '{name}' in procedural memory.")
        return skill.execute(*args, **kwargs)

    def list_skills(self) -> List[str]:
        return list(self._skills.keys())

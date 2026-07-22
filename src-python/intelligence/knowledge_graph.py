"""
intelligence.knowledge_graph — Episodic, Semantic & Procedural Memory

Provides three distinct memory stores used by NEXUS agents:
  - EpisodicMemory:   Time-indexed records of past events (what happened, when).
  - SemanticMemory:   Concept/fact store (what things are, relationships).
  - ProceduralMemory: Action schemas / skills (how to do things).

Design references:
  - Tulving 1972 episodic/semantic memory distinction
  - Zep / MemGPT memory architecture for LLM agents
  - Neo4j Python bindings for graph-backed semantic memory
  - NEXUS_UNIVERSAL_OS.md Domain 2.4 — Memory Architecture
GAIAN law: GAIAN_LAWS.md Law II — Memory Sovereignty
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("intelligence.knowledge_graph")


@dataclass
class Episode:
    """A single episodic memory record."""
    description: str
    occurred_at: datetime        = field(default_factory=lambda: datetime.now(timezone.utc))
    tags:        list[str]       = field(default_factory=list)
    payload:     dict[str, Any]  = field(default_factory=dict)
    episode_id:  str             = field(default_factory=lambda: str(uuid.uuid4()))


class EpisodicMemory:
    """Append-only log of agent experience episodes.

    Reference: NEXUS_UNIVERSAL_OS.md Domain 2.4; Tulving 1972.
    """

    def __init__(self) -> None:
        self._episodes: list[Episode] = []

    def record(self, episode: Episode) -> None:
        """Record a new episode."""
        self._episodes.append(episode)
        logger.debug("EpisodicMemory: recorded episode %s", episode.episode_id)

    def recall(self, tag: Optional[str] = None) -> list[Episode]:
        """Retrieve episodes, optionally filtered by tag."""
        if tag is None:
            return list(self._episodes)
        return [e for e in self._episodes if tag in e.tags]

    def __len__(self) -> int:
        return len(self._episodes)


@dataclass
class Concept:
    """A node in the semantic memory graph."""
    name:       str
    attributes: dict[str, Any] = field(default_factory=dict)
    concept_id: str            = field(default_factory=lambda: str(uuid.uuid4()))


class SemanticMemory:
    """Concept/fact store for declarative world knowledge.

    In Phase C this will be backed by a Neo4j graph or NetworkX.
    In v0.1.0 it uses an in-memory dict.
    Reference: NEXUS_UNIVERSAL_OS.md Domain 2.4; Zep memory architecture.
    """

    def __init__(self) -> None:
        self._concepts:      dict[str, Concept]         = {}
        self._relationships: list[tuple[str, str, str]] = []  # (src_id, rel, dst_id)

    def add_concept(self, concept: Concept) -> None:
        """Add a concept node to the semantic graph."""
        self._concepts[concept.concept_id] = concept
        logger.debug("SemanticMemory: added concept '%s'", concept.name)

    def relate(self, src_id: str, relationship: str, dst_id: str) -> None:
        """Add a directed relationship edge between two concepts."""
        self._relationships.append((src_id, relationship, dst_id))

    def query(self, name: str) -> Optional[Concept]:
        """Find a concept by name (linear scan — use graph DB in production)."""
        return next((c for c in self._concepts.values() if c.name == name), None)


@dataclass
class ActionSchema:
    """A procedural memory entry describing how to perform an action."""
    action_name:  str
    preconditions: list[str]      = field(default_factory=list)
    effects:       list[str]      = field(default_factory=list)
    steps:         list[str]      = field(default_factory=list)
    schema_id:     str            = field(default_factory=lambda: str(uuid.uuid4()))


class ProceduralMemory:
    """Registry of ActionSchemas (skills / procedures).

    Reference: NEXUS_UNIVERSAL_OS.md Domain 2.4.
    """

    def __init__(self) -> None:
        self._schemas: dict[str, ActionSchema] = {}

    def register(self, schema: ActionSchema) -> None:
        """Register an action schema."""
        self._schemas[schema.action_name] = schema
        logger.debug("ProceduralMemory: registered schema '%s'", schema.action_name)

    def lookup(self, action_name: str) -> Optional[ActionSchema]:
        """Retrieve a schema by action name."""
        return self._schemas.get(action_name)

    def all_actions(self) -> list[str]:
        """Return a list of all registered action names."""
        return list(self._schemas.keys())

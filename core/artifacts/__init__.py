"""
GAIA Artifacts — durable, versioned outputs produced by agents, workflows,
skills, or human operators.

Artifacts are immutable payload snapshots with explicit lineage. They are
meant to represent outputs such as reports, plans, code bundles, charts,
insights, prompts, transcripts, or any other generated deliverable that
needs to be stored, versioned, retrieved, and linked back to origin.

Artifacts differ from Memory (facts about a principal), Sessions (ephemeral
conversation state), and Spaces (shared persistent environments). An
Artifact is a durable output object with metadata, provenance, and content.
"""
from __future__ import annotations

from core.artifacts.model import (
    Artifact,
    ArtifactKind,
    ArtifactVersion,
    ArtifactStatus,
    ArtifactLineage,
)
from core.artifacts.repository import ArtifactRepository
from core.artifacts.manager import ArtifactManager

__all__ = [
    "Artifact",
    "ArtifactKind",
    "ArtifactVersion",
    "ArtifactStatus",
    "ArtifactLineage",
    "ArtifactRepository",
    "ArtifactManager",
]

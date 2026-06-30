"""Core domain types for GAIA Artifacts."""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ArtifactKind(str, Enum):
    REPORT = "report"
    PLAN = "plan"
    CODE = "code"
    CHART = "chart"
    DATA = "data"
    PROMPT = "prompt"
    TRANSCRIPT = "transcript"
    NOTE = "note"
    CUSTOM = "custom"


class ArtifactStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


@dataclass
class ArtifactLineage:
    """Structured provenance for an artifact.

    The lineage object makes it possible to trace an artifact back to the
    session, workflow, space, skill, principal, or parent artifact that
    produced it.
    """
    source_session_id: str = ""
    source_space_id: str = ""
    source_workflow_id: str = ""
    source_skill_id: str = ""
    source_principal_id: str = ""
    parent_artifact_id: str = ""
    parent_version: int = 0


@dataclass
class ArtifactVersion:
    """Immutable snapshot of artifact content at a point in time."""
    version: int
    content: str
    content_hash: str
    mime_type: str = "text/plain"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utcnow)
    created_by: str = ""

    @classmethod
    def from_content(
        cls,
        version: int,
        content: str,
        created_by: str = "",
        mime_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "ArtifactVersion":
        return cls(
            version=version,
            content=content,
            content_hash=_sha256_text(content),
            mime_type=mime_type,
            metadata=metadata or {},
            created_by=created_by,
        )


@dataclass
class Artifact:
    """A durable output object with versions and provenance."""
    name: str
    kind: ArtifactKind
    owner_id: str
    artifact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: ArtifactStatus = ArtifactStatus.DRAFT
    tags: List[str] = field(default_factory=list)
    lineage: ArtifactLineage = field(default_factory=ArtifactLineage)
    versions: List[ArtifactVersion] = field(default_factory=list)
    created_at: str = field(default_factory=_utcnow)
    updated_at: str = field(default_factory=_utcnow)

    def _touch(self) -> None:
        self.updated_at = _utcnow()

    @property
    def latest(self) -> Optional[ArtifactVersion]:
        return self.versions[-1] if self.versions else None

    @property
    def version_count(self) -> int:
        return len(self.versions)

    def add_version(
        self,
        content: str,
        created_by: str = "",
        mime_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ArtifactVersion:
        next_version = len(self.versions) + 1
        version = ArtifactVersion.from_content(
            version=next_version,
            content=content,
            created_by=created_by,
            mime_type=mime_type,
            metadata=metadata,
        )
        self.versions.append(version)
        self._touch()
        return version

    def get_version(self, version: int) -> Optional[ArtifactVersion]:
        for item in self.versions:
            if item.version == version:
                return item
        return None

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def summary(self) -> Dict[str, Any]:
        latest = self.latest
        return {
            "artifact_id": self.artifact_id,
            "name": self.name,
            "kind": self.kind.value,
            "status": self.status.value,
            "owner_id": self.owner_id,
            "version_count": self.version_count,
            "latest_version": latest.version if latest else 0,
            "latest_hash": latest.content_hash if latest else "",
            "tags": list(self.tags),
            "lineage": self.lineage.__dict__.copy(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

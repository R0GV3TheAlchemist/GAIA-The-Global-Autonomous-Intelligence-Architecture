"""High-level artifact lifecycle and version orchestration."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.artifacts.model import (
    Artifact,
    ArtifactKind,
    ArtifactLineage,
    ArtifactStatus,
    ArtifactVersion,
)
from core.artifacts.repository import ArtifactRepository


class ArtifactPermissionError(Exception):
    """Raised when an actor attempts an unauthorized artifact mutation."""


class ArtifactManager:
    def __init__(self, repository: ArtifactRepository) -> None:
        self.repository = repository

    def create(
        self,
        name: str,
        kind: ArtifactKind,
        owner_id: str,
        content: str,
        *,
        description: str = "",
        tags: Optional[List[str]] = None,
        mime_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None,
        lineage: Optional[ArtifactLineage] = None,
    ) -> Artifact:
        artifact = Artifact(
            name=name,
            kind=kind,
            owner_id=owner_id,
            description=description,
            tags=tags or [],
            lineage=lineage or ArtifactLineage(source_principal_id=owner_id),
        )
        artifact.add_version(
            content=content,
            created_by=owner_id,
            mime_type=mime_type,
            metadata=metadata,
        )
        self.repository.save(artifact)
        return artifact

    def publish(self, artifact_id: str, actor_id: str) -> Artifact:
        artifact = self._require_owner(artifact_id, actor_id)
        artifact.status = ArtifactStatus.PUBLISHED
        artifact._touch()
        self.repository.save(artifact)
        return artifact

    def archive(self, artifact_id: str, actor_id: str) -> Artifact:
        artifact = self._require_owner(artifact_id, actor_id)
        artifact.status = ArtifactStatus.ARCHIVED
        artifact._touch()
        self.repository.save(artifact)
        return artifact

    def deprecate(self, artifact_id: str, actor_id: str) -> Artifact:
        artifact = self._require_owner(artifact_id, actor_id)
        artifact.status = ArtifactStatus.DEPRECATED
        artifact._touch()
        self.repository.save(artifact)
        return artifact

    def add_version(
        self,
        artifact_id: str,
        actor_id: str,
        content: str,
        *,
        mime_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ArtifactVersion:
        artifact = self._require_owner(artifact_id, actor_id)
        version = artifact.add_version(
            content=content,
            created_by=actor_id,
            mime_type=mime_type,
            metadata=metadata,
        )
        self.repository.save(artifact)
        return version

    def fork(
        self,
        artifact_id: str,
        actor_id: str,
        *,
        new_name: str,
        new_owner_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Artifact:
        source = self.repository.require(artifact_id)
        latest = source.latest
        if latest is None:
            raise ValueError("Cannot fork an artifact with no versions.")
        lineage = ArtifactLineage(
            source_session_id=source.lineage.source_session_id,
            source_space_id=source.lineage.source_space_id,
            source_workflow_id=source.lineage.source_workflow_id,
            source_skill_id=source.lineage.source_skill_id,
            source_principal_id=actor_id,
            parent_artifact_id=source.artifact_id,
            parent_version=latest.version,
        )
        child = self.create(
            name=new_name,
            kind=source.kind,
            owner_id=new_owner_id or actor_id,
            content=latest.content,
            description=description or source.description,
            tags=list(source.tags),
            mime_type=latest.mime_type,
            metadata=dict(latest.metadata),
            lineage=lineage,
        )
        return child

    def tag(self, artifact_id: str, actor_id: str, tag: str) -> Artifact:
        artifact = self._require_owner(artifact_id, actor_id)
        if tag not in artifact.tags:
            artifact.tags.append(tag)
            artifact._touch()
            self.repository.save(artifact)
        return artifact

    def untag(self, artifact_id: str, actor_id: str, tag: str) -> Artifact:
        artifact = self._require_owner(artifact_id, actor_id)
        if tag in artifact.tags:
            artifact.tags.remove(tag)
            artifact._touch()
            self.repository.save(artifact)
        return artifact

    def get(self, artifact_id: str) -> Artifact:
        return self.repository.require(artifact_id)

    def get_version(self, artifact_id: str, version: int) -> Optional[ArtifactVersion]:
        return self.repository.require(artifact_id).get_version(version)

    def latest_content(self, artifact_id: str) -> str:
        artifact = self.repository.require(artifact_id)
        latest = artifact.latest
        return latest.content if latest else ""

    def search(self, query: str) -> List[Artifact]:
        return self.repository.search(query)

    def list_by_owner(self, owner_id: str) -> List[Artifact]:
        return self.repository.list_by_owner(owner_id)

    def list_by_kind(self, kind: ArtifactKind) -> List[Artifact]:
        return self.repository.list_by_kind(kind)

    def _require_owner(self, artifact_id: str, actor_id: str) -> Artifact:
        artifact = self.repository.require(artifact_id)
        if artifact.owner_id != actor_id:
            raise ArtifactPermissionError(
                f"Actor '{actor_id}' is not owner of artifact '{artifact_id}'."
            )
        return artifact

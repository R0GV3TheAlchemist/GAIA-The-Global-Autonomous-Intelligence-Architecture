"""In-memory repository for GAIA Artifacts.

The repository keeps two indices:
- artifact_id -> Artifact
- name -> set[artifact_id]

Names are intentionally not unique because multiple artifacts may share a
label while differing by owner, lineage, or kind.
"""
from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional

from core.artifacts.model import Artifact, ArtifactKind, ArtifactStatus


class ArtifactRepository:
    def __init__(self) -> None:
        self._by_id: Dict[str, Artifact] = {}
        self._ids_by_name: DefaultDict[str, set[str]] = defaultdict(set)

    def save(self, artifact: Artifact) -> None:
        existing = self._by_id.get(artifact.artifact_id)
        if existing is not None and existing.name != artifact.name:
            self._ids_by_name[existing.name].discard(existing.artifact_id)
            if not self._ids_by_name[existing.name]:
                del self._ids_by_name[existing.name]
        self._by_id[artifact.artifact_id] = artifact
        self._ids_by_name[artifact.name].add(artifact.artifact_id)

    def get(self, artifact_id: str) -> Optional[Artifact]:
        return self._by_id.get(artifact_id)

    def require(self, artifact_id: str) -> Artifact:
        artifact = self.get(artifact_id)
        if artifact is None:
            raise KeyError(f"Artifact '{artifact_id}' not found.")
        return artifact

    def delete(self, artifact_id: str) -> None:
        artifact = self._by_id.pop(artifact_id, None)
        if artifact is None:
            return
        self._ids_by_name[artifact.name].discard(artifact_id)
        if not self._ids_by_name[artifact.name]:
            del self._ids_by_name[artifact.name]

    def list_all(self) -> List[Artifact]:
        return list(self._by_id.values())

    def list_by_owner(self, owner_id: str) -> List[Artifact]:
        return [a for a in self._by_id.values() if a.owner_id == owner_id]

    def list_by_kind(self, kind: ArtifactKind) -> List[Artifact]:
        return [a for a in self._by_id.values() if a.kind == kind]

    def list_by_status(self, status: ArtifactStatus) -> List[Artifact]:
        return [a for a in self._by_id.values() if a.status == status]

    def get_by_name(self, name: str) -> List[Artifact]:
        return [self._by_id[aid] for aid in self._ids_by_name.get(name, set())]

    def search(self, query: str) -> List[Artifact]:
        q = query.lower()
        results: List[Artifact] = []
        for artifact in self._by_id.values():
            if (
                q in artifact.name.lower()
                or q in artifact.description.lower()
                or any(q in tag.lower() for tag in artifact.tags)
                or q in artifact.kind.value.lower()
            ):
                results.append(artifact)
        return results

    def __contains__(self, artifact_id: str) -> bool:
        return artifact_id in self._by_id

    def __len__(self) -> int:
        return len(self._by_id)

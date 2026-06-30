from __future__ import annotations

import pytest

from core.artifacts.manager import ArtifactManager, ArtifactPermissionError
from core.artifacts.model import ArtifactKind, ArtifactLineage, ArtifactStatus
from core.artifacts.repository import ArtifactRepository


class TestArtifactModelAndFlow:
    def test_create_artifact_with_initial_version(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create(
            name="alignment-report",
            kind=ArtifactKind.REPORT,
            owner_id="gaia",
            content="v1",
        )
        assert artifact.version_count == 1
        assert artifact.latest is not None
        assert artifact.latest.content == "v1"

    def test_latest_hash_present(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("x", ArtifactKind.NOTE, "gaia", "hello")
        assert artifact.latest is not None
        assert len(artifact.latest.content_hash) == 64

    def test_add_version(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("plan", ArtifactKind.PLAN, "gaia", "step 1")
        version = manager.add_version(artifact.artifact_id, "gaia", "step 2")
        assert version.version == 2
        assert artifact.version_count == 2
        assert artifact.latest.content == "step 2"

    def test_get_specific_version(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("plan", ArtifactKind.PLAN, "gaia", "v1")
        manager.add_version(artifact.artifact_id, "gaia", "v2")
        v1 = manager.get_version(artifact.artifact_id, 1)
        assert v1 is not None
        assert v1.content == "v1"

    def test_publish_archive_deprecate(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("plan", ArtifactKind.PLAN, "gaia", "v1")
        manager.publish(artifact.artifact_id, "gaia")
        assert artifact.status == ArtifactStatus.PUBLISHED
        manager.archive(artifact.artifact_id, "gaia")
        assert artifact.status == ArtifactStatus.ARCHIVED
        manager.deprecate(artifact.artifact_id, "gaia")
        assert artifact.status == ArtifactStatus.DEPRECATED

    def test_only_owner_can_add_version(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("plan", ArtifactKind.PLAN, "gaia", "v1")
        with pytest.raises(ArtifactPermissionError):
            manager.add_version(artifact.artifact_id, "intruder", "v2")

    def test_only_owner_can_change_status(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("note", ArtifactKind.NOTE, "gaia", "x")
        with pytest.raises(ArtifactPermissionError):
            manager.publish(artifact.artifact_id, "other")

    def test_repository_get_and_delete(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("n", ArtifactKind.NOTE, "gaia", "x")
        assert repo.get(artifact.artifact_id) is artifact
        repo.delete(artifact.artifact_id)
        assert repo.get(artifact.artifact_id) is None

    def test_repository_get_by_name(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        manager.create("shared", ArtifactKind.NOTE, "gaia", "x")
        manager.create("shared", ArtifactKind.NOTE, "other", "y")
        results = repo.get_by_name("shared")
        assert len(results) == 2

    def test_repository_list_by_owner(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        manager.create("a", ArtifactKind.NOTE, "gaia", "x")
        manager.create("b", ArtifactKind.REPORT, "gaia", "y")
        manager.create("c", ArtifactKind.CODE, "other", "z")
        assert len(repo.list_by_owner("gaia")) == 2

    def test_repository_list_by_kind(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        manager.create("a", ArtifactKind.REPORT, "gaia", "x")
        manager.create("b", ArtifactKind.REPORT, "gaia", "y")
        manager.create("c", ArtifactKind.CODE, "gaia", "z")
        assert len(repo.list_by_kind(ArtifactKind.REPORT)) == 2

    def test_search_by_name_description_tag_kind(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        manager.create(
            "atlas-report",
            ArtifactKind.REPORT,
            "gaia",
            "body",
            description="mapping layer",
            tags=["geo", "criticality"],
        )
        assert len(manager.search("atlas")) == 1
        assert len(manager.search("mapping")) == 1
        assert len(manager.search("geo")) == 1
        assert len(manager.search("report")) == 1

    def test_tag_and_untag(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("plan", ArtifactKind.PLAN, "gaia", "x")
        manager.tag(artifact.artifact_id, "gaia", "priority")
        assert "priority" in artifact.tags
        manager.untag(artifact.artifact_id, "gaia", "priority")
        assert "priority" not in artifact.tags

    def test_fork_creates_lineage(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        parent = manager.create(
            "parent-plan",
            ArtifactKind.PLAN,
            "gaia",
            "base",
            lineage=ArtifactLineage(source_space_id="space-1", source_workflow_id="wf-1"),
        )
        child = manager.fork(parent.artifact_id, "gaia", new_name="child-plan")
        assert child.lineage.parent_artifact_id == parent.artifact_id
        assert child.lineage.parent_version == 1
        assert child.latest is not None
        assert child.latest.content == "base"

    def test_fork_can_change_owner(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        parent = manager.create("parent", ArtifactKind.NOTE, "gaia", "x")
        child = manager.fork(parent.artifact_id, "gaia", new_name="child", new_owner_id="alice")
        assert child.owner_id == "alice"

    def test_latest_content(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("note", ArtifactKind.NOTE, "gaia", "x")
        manager.add_version(artifact.artifact_id, "gaia", "y")
        assert manager.latest_content(artifact.artifact_id) == "y"

    def test_summary_contains_lineage_and_hash(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("note", ArtifactKind.NOTE, "gaia", "x")
        summary = artifact.summary()
        assert summary["latest_hash"]
        assert "lineage" in summary

    def test_missing_artifact_raises(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        with pytest.raises(KeyError):
            manager.get("missing")

    def test_permission_error_on_tag(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("note", ArtifactKind.NOTE, "gaia", "x")
        with pytest.raises(ArtifactPermissionError):
            manager.tag(artifact.artifact_id, "other", "t")

    def test_permission_error_on_untag(self) -> None:
        repo = ArtifactRepository()
        manager = ArtifactManager(repo)
        artifact = manager.create("note", ArtifactKind.NOTE, "gaia", "x")
        with pytest.raises(ArtifactPermissionError):
            manager.untag(artifact.artifact_id, "other", "t")

"""
tests/test_canon_store.py

Test suite for CanonStore and CanonDiff.
Issue #249.
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from core.canon_store import CanonStore, CanonEntry, _hash_body
from core.canon_diff import CanonDiff, CanonDiffResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def store(tmp_path: Path) -> CanonStore:
    """Fresh CanonStore backed by a temp directory."""
    return CanonStore(store_path=tmp_path / "canon")


def _seed_entry(store: CanonStore, entry_id: str = "C01", body: str = "GAIA values life.") -> None:
    """Helper: propose + approve a single add amendment."""
    amd = store.propose_amendment(
        action="add",
        entry_id=entry_id,
        proposed_by="gaian_test",
        justification="Seed entry for tests.",
        new_body=body,
        new_title=f"Entry {entry_id}",
    )
    store.approve_amendment(amd.amendment_id, reviewed_by="gaian_test", new_title=f"Entry {entry_id}")


# ---------------------------------------------------------------------------
# CanonEntry
# ---------------------------------------------------------------------------

class TestCanonEntry:
    def test_hash_auto_computed(self) -> None:
        e = CanonEntry(id="C01", title="T", body="hello")
        assert e.hash == _hash_body("hello")

    def test_to_dict_round_trip(self) -> None:
        e = CanonEntry(id="C01", title="T", body="hello", tags=["governance"])
        d = e.to_dict()
        e2 = CanonEntry(**d)
        assert e2.body == e.body
        assert e2.tags == ["governance"]


# ---------------------------------------------------------------------------
# CanonStore — basic CRUD
# ---------------------------------------------------------------------------

class TestCanonStoreCRUD:
    def test_initial_state(self, store: CanonStore) -> None:
        assert store.version == "0.1.0"
        assert store.all_entries() == []

    def test_propose_add(self, store: CanonStore) -> None:
        amd = store.propose_amendment(
            action="add",
            entry_id="C01",
            proposed_by="gaian",
            justification="First principle.",
            new_body="GAIA serves life.",
        )
        assert amd.status == "pending"
        assert len(store.pending_amendments()) == 1

    def test_approve_add_creates_entry(self, store: CanonStore) -> None:
        amd = store.propose_amendment(
            action="add", entry_id="C01", proposed_by="gaian",
            justification=".", new_body="GAIA serves life.",
        )
        store.approve_amendment(amd.amendment_id, reviewed_by="admin", new_title="Principle C01")
        entry = store.get("C01")
        assert entry is not None
        assert entry.body == "GAIA serves life."
        assert entry.title == "Principle C01"

    def test_version_bumps_on_approval(self, store: CanonStore) -> None:
        assert store.version == "0.1.0"
        _seed_entry(store)
        assert store.version == "0.1.1"

    def test_propose_update(self, store: CanonStore) -> None:
        _seed_entry(store)
        amd = store.propose_amendment(
            action="update", entry_id="C01", proposed_by="gaian",
            justification="Clarification.", new_body="GAIA values all life.",
        )
        store.approve_amendment(amd.amendment_id, reviewed_by="admin")
        assert store.get("C01").body == "GAIA values all life."

    def test_propose_remove(self, store: CanonStore) -> None:
        _seed_entry(store)
        amd = store.propose_amendment(
            action="remove", entry_id="C01", proposed_by="gaian",
            justification="Superseded.",
        )
        store.approve_amendment(amd.amendment_id, reviewed_by="admin")
        assert store.get("C01") is None

    def test_reject_amendment(self, store: CanonStore) -> None:
        amd = store.propose_amendment(
            action="add", entry_id="C01", proposed_by="gaian",
            justification=".", new_body="body",
        )
        store.reject_amendment(amd.amendment_id, reviewed_by="admin")
        assert amd.status == "rejected"
        assert store.get("C01") is None

    def test_duplicate_add_raises(self, store: CanonStore) -> None:
        _seed_entry(store)
        with pytest.raises(ValueError, match="already exists"):
            store.propose_amendment(
                action="add", entry_id="C01", proposed_by="gaian",
                justification=".", new_body="body",
            )

    def test_update_nonexistent_raises(self, store: CanonStore) -> None:
        with pytest.raises(ValueError, match="not found"):
            store.propose_amendment(
                action="update", entry_id="MISSING", proposed_by="gaian",
                justification=".", new_body="body",
            )

    def test_search(self, store: CanonStore) -> None:
        _seed_entry(store, "C01", "GAIA values life and sovereignty.")
        _seed_entry(store, "C02", "All decisions must be transparent.")
        results = store.search("sovereignty")
        assert len(results) == 1
        assert results[0].id == "C01"


# ---------------------------------------------------------------------------
# CanonStore — persistence
# ---------------------------------------------------------------------------

class TestCanonStorePersistence:
    def test_entries_persist_across_reload(self, tmp_path: Path) -> None:
        store = CanonStore(store_path=tmp_path / "canon")
        _seed_entry(store)
        store2 = CanonStore(store_path=tmp_path / "canon")
        assert store2.get("C01") is not None
        assert store2.version == "0.1.1"

    def test_snapshot_created_on_approval(self, store: CanonStore) -> None:
        _seed_entry(store)
        snaps = store.list_snapshots()
        assert "0.1.1" in snaps

    def test_load_snapshot(self, store: CanonStore) -> None:
        _seed_entry(store)
        snap = store.load_snapshot("0.1.1")
        assert "C01" in snap["entries"]


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class TestConflictDetection:
    def test_no_conflicts_clean_canon(self, store: CanonStore) -> None:
        _seed_entry(store, "C01", "GAIA always supports life.")
        conflicts = store.detect_conflicts()
        assert conflicts == []

    def test_duplicate_body_flagged(self, store: CanonStore) -> None:
        body = "GAIA values life."
        _seed_entry(store, "C01", body)
        # Manually add a duplicate-bodied entry without going through amendment
        from core.canon_store import CanonEntry
        store._entries["C02"] = CanonEntry(id="C02", title="Dup", body=body)
        conflicts = store.detect_conflicts()
        ids = {(c.entry_a, c.entry_b) for c in conflicts}
        assert ("C01", "C02") in ids or ("C02", "C01") in ids


# ---------------------------------------------------------------------------
# Regulatory export
# ---------------------------------------------------------------------------

class TestRegulatoryExport:
    def test_export_structure(self, store: CanonStore) -> None:
        _seed_entry(store)
        export = store.regulatory_export()
        assert export["gaia_canon_export"] is True
        assert export["version"] == store.version
        assert len(export["entries"]) == 1
        assert isinstance(export["amendment_log"], list)

    def test_export_writes_file(self, store: CanonStore, tmp_path: Path) -> None:
        _seed_entry(store)
        out = tmp_path / "export.json"
        store.regulatory_export(output_path=out)
        assert out.exists()
        data = json.loads(out.read_text())
        assert data["gaia_canon_export"] is True


# ---------------------------------------------------------------------------
# CanonDiff
# ---------------------------------------------------------------------------

class TestCanonDiff:
    def test_diff_added(self, store: CanonStore) -> None:
        before = {}
        after = {"C01": {"id": "C01", "title": "T", "body": "hello", "hash": "abc", "tags": [], "source_file": "", "added_in": ""}}
        result = CanonDiff.compare_dicts(before, after, "0.1.0", "0.1.1")
        assert len(result.added) == 1
        assert result.added[0].entry_id == "C01"
        assert result.total_changes == 1

    def test_diff_removed(self, store: CanonStore) -> None:
        before = {"C01": {"id": "C01", "title": "T", "body": "hello", "hash": "abc", "tags": [], "source_file": "", "added_in": ""}}
        after = {}
        result = CanonDiff.compare_dicts(before, after, "0.1.0", "0.1.1")
        assert len(result.removed) == 1

    def test_diff_modified(self, store: CanonStore) -> None:
        before = {"C01": {"id": "C01", "title": "T", "body": "old", "hash": "aaa", "tags": [], "source_file": "", "added_in": ""}}
        after  = {"C01": {"id": "C01", "title": "T", "body": "new", "hash": "bbb", "tags": [], "source_file": "", "added_in": ""}}
        result = CanonDiff.compare_dicts(before, after, "0.1.0", "0.1.1")
        assert len(result.modified) == 1
        assert result.modified[0].before_body == "old"
        assert result.modified[0].after_body == "new"

    def test_diff_no_changes(self, store: CanonStore) -> None:
        entry = {"C01": {"id": "C01", "title": "T", "body": "same", "hash": "xyz", "tags": [], "source_file": "", "added_in": ""}}
        result = CanonDiff.compare_dicts(entry, entry, "0.1.0", "0.1.0")
        assert result.total_changes == 0

    def test_summary_string(self) -> None:
        before = {}
        after = {"C01": {"id": "C01", "title": "T", "body": "hello", "hash": "abc", "tags": [], "source_file": "", "added_in": ""}}
        result = CanonDiff.compare_dicts(before, after, "0.1.0", "0.1.1")
        assert "0.1.0" in result.summary()
        assert "+1 added" in result.summary()

    def test_compare_snapshots(self, store: CanonStore) -> None:
        _seed_entry(store, "C01", "First version.")
        v1 = store.version  # 0.1.1
        amd = store.propose_amendment(
            action="update", entry_id="C01", proposed_by="gaian",
            justification=".", new_body="Updated version.",
        )
        store.approve_amendment(amd.amendment_id, reviewed_by="admin")
        differ = CanonDiff(store)
        result = differ.compare_versions(v1, store.version)
        assert len(result.modified) == 1

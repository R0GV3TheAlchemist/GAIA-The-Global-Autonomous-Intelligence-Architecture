"""
tests/memory/test_memory_console.py

Full test suite for the Visible Memory & State Console.
Covers read, update, delete, archive, explain, export, and session state flows.

Canon Reference: C01 (Gaian Sovereignty), C-SENTINEL Article 4 (Memory Sovereignty)
Issue:           #213
"""

import pytest
from datetime import datetime, timezone

from core.memory.memory_store import (
    MemoryCategory,
    MemoryEntry,
    MemoryProvenance,
    MemoryTier,
    ProvenanceSource,
    SessionState,
)
from core.memory.memory_console import (
    ConsoleStatus,
    MemoryConsole,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def console() -> MemoryConsole:
    return MemoryConsole(gaian_id="test-gaian-001")


@pytest.fixture
def durable_entry() -> MemoryEntry:
    return MemoryEntry(
        key="preferred_name",
        value="Alchemist",
        category=MemoryCategory.PREFERENCE,
        tier=MemoryTier.DURABLE,
        provenance=MemoryProvenance(
            source=ProvenanceSource.GAIAN_EXPLICIT,
            confidence=1.0,
            origin_context="User said: call me Alchemist",
        ),
    )


@pytest.fixture
def session_entry() -> MemoryEntry:
    return MemoryEntry(
        key="current_goal",
        value="Build issue #213",
        category=MemoryCategory.SESSION_GOAL,
        tier=MemoryTier.SESSION,
        provenance=MemoryProvenance(
            source=ProvenanceSource.GAIAN_EXPLICIT,
            confidence=0.95,
        ),
    )


@pytest.fixture
def stored_console(console, durable_entry) -> MemoryConsole:
    console.store(durable_entry)
    return console


# ---------------------------------------------------------------------------
# MemoryProvenance validation
# ---------------------------------------------------------------------------

class TestMemoryProvenance:

    def test_valid_confidence_accepted(self):
        p = MemoryProvenance(source=ProvenanceSource.GAIAN_EXPLICIT, confidence=0.85)
        assert p.confidence == 0.85

    def test_confidence_above_one_rejected(self):
        with pytest.raises(ValueError):
            MemoryProvenance(source=ProvenanceSource.GAIAN_EXPLICIT, confidence=1.1)

    def test_confidence_below_zero_rejected(self):
        with pytest.raises(ValueError):
            MemoryProvenance(source=ProvenanceSource.GAIAN_EXPLICIT, confidence=-0.1)

    def test_confidence_at_boundaries_accepted(self):
        MemoryProvenance(source=ProvenanceSource.GAIAN_EXPLICIT, confidence=0.0)
        MemoryProvenance(source=ProvenanceSource.GAIAN_EXPLICIT, confidence=1.0)


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------

class TestStore:

    def test_store_new_entry(self, console, durable_entry):
        result = console.store(durable_entry)
        assert result.status == ConsoleStatus.OK
        assert result.entry.id == durable_entry.id

    def test_store_updates_existing_key(self, stored_console, durable_entry):
        updated = MemoryEntry(
            key="preferred_name",
            value="The Alchemist",
            category=MemoryCategory.PREFERENCE,
            tier=MemoryTier.DURABLE,
            provenance=MemoryProvenance(
                source=ProvenanceSource.GAIAN_EXPLICIT,
                confidence=1.0,
            ),
        )
        result = stored_console.store(updated)
        assert result.status == ConsoleStatus.OK
        assert result.entry.value == "The Alchemist"
        # Should still be the original entry ID
        assert result.entry.id == durable_entry.id


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

class TestRead:

    def test_read_existing_entry(self, stored_console, durable_entry):
        result = stored_console.read(durable_entry.id)
        assert result.status == ConsoleStatus.OK
        assert result.entry.key == "preferred_name"

    def test_read_includes_dict_export(self, stored_console, durable_entry):
        result = stored_console.read(durable_entry.id)
        assert result.data is not None
        assert "id" in result.data
        assert "confidence" in result.data
        assert "source" in result.data

    def test_read_nonexistent_returns_not_found(self, console):
        result = console.read("nonexistent-id")
        assert result.status == ConsoleStatus.NOT_FOUND


# ---------------------------------------------------------------------------
# Browse
# ---------------------------------------------------------------------------

class TestBrowse:

    def test_browse_returns_stored_entries(self, stored_console):
        entries = stored_console.browse()
        assert len(entries) == 1

    def test_browse_excludes_archived_by_default(self, stored_console, durable_entry):
        stored_console.archive(durable_entry.id)
        entries = stored_console.browse()
        assert len(entries) == 0

    def test_browse_by_tier(self, console, durable_entry, session_entry):
        console.store(durable_entry)
        console.store(session_entry)
        durable = console.browse(tier=MemoryTier.DURABLE)
        session = console.browse(tier=MemoryTier.SESSION)
        assert all(e.tier == MemoryTier.DURABLE for e in durable)
        assert all(e.tier == MemoryTier.SESSION for e in session)

    def test_browse_by_category(self, console, durable_entry, session_entry):
        console.store(durable_entry)
        console.store(session_entry)
        prefs = console.browse(category=MemoryCategory.PREFERENCE)
        assert all(e.category == MemoryCategory.PREFERENCE for e in prefs)

    def test_browse_by_tag(self, console):
        entry = MemoryEntry(
            key="theme",
            value="alchemy",
            category=MemoryCategory.PREFERENCE,
            tier=MemoryTier.DURABLE,
            provenance=MemoryProvenance(source=ProvenanceSource.GAIAN_EXPLICIT, confidence=1.0),
            tags=["aesthetic", "identity"],
        )
        console.store(entry)
        tagged = console.browse(tag="aesthetic")
        assert len(tagged) == 1
        assert tagged[0].key == "theme"


# ---------------------------------------------------------------------------
# Edit
# ---------------------------------------------------------------------------

class TestEdit:

    def test_edit_updates_value(self, stored_console, durable_entry):
        result = stored_console.edit(durable_entry.id, "Master Alchemist")
        assert result.status == ConsoleStatus.OK
        assert result.entry.value == "Master Alchemist"

    def test_edit_upgrades_provenance_to_gaian_explicit(self, stored_console, durable_entry):
        stored_console.edit(durable_entry.id, "Master Alchemist")
        entry = stored_console.read(durable_entry.id).entry
        assert entry.provenance.source == ProvenanceSource.GAIAN_EXPLICIT
        assert entry.provenance.confidence == 1.0

    def test_edit_returns_old_and_new_value(self, stored_console, durable_entry):
        result = stored_console.edit(durable_entry.id, "Master Alchemist")
        assert result.data["old_value"] == "Alchemist"
        assert result.data["new_value"] == "Master Alchemist"

    def test_edit_nonexistent_returns_not_found(self, console):
        result = console.edit("nonexistent", "value")
        assert result.status == ConsoleStatus.NOT_FOUND

    def test_edit_archived_entry_forbidden(self, stored_console, durable_entry):
        stored_console.archive(durable_entry.id)
        result = stored_console.edit(durable_entry.id, "new value")
        assert result.status == ConsoleStatus.FORBIDDEN


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

class TestDelete:

    def test_delete_removes_entry(self, stored_console, durable_entry):
        result = stored_console.delete(durable_entry.id)
        assert result.status == ConsoleStatus.OK
        assert stored_console.read(durable_entry.id).status == ConsoleStatus.NOT_FOUND

    def test_delete_is_permanent(self, stored_console, durable_entry):
        stored_console.delete(durable_entry.id)
        entries = stored_console.browse()
        assert len(entries) == 0

    def test_delete_nonexistent_returns_not_found(self, console):
        result = console.delete("nonexistent")
        assert result.status == ConsoleStatus.NOT_FOUND

    def test_delete_returns_deleted_entry(self, stored_console, durable_entry):
        result = stored_console.delete(durable_entry.id)
        assert result.entry.key == "preferred_name"


# ---------------------------------------------------------------------------
# Archive
# ---------------------------------------------------------------------------

class TestArchive:

    def test_archive_sets_tier(self, stored_console, durable_entry):
        result = stored_console.archive(durable_entry.id)
        assert result.status == ConsoleStatus.OK
        assert result.entry.tier == MemoryTier.ARCHIVED

    def test_archived_entry_not_in_browse(self, stored_console, durable_entry):
        stored_console.archive(durable_entry.id)
        assert len(stored_console.browse()) == 0

    def test_archive_already_archived_is_ok(self, stored_console, durable_entry):
        stored_console.archive(durable_entry.id)
        result = stored_console.archive(durable_entry.id)
        assert result.status == ConsoleStatus.OK

    def test_archive_nonexistent_returns_not_found(self, console):
        result = console.archive("nonexistent")
        assert result.status == ConsoleStatus.NOT_FOUND

    def test_archived_entry_visible_when_browsing_archived_tier(self, stored_console, durable_entry):
        stored_console.archive(durable_entry.id)
        archived = stored_console.browse(tier=MemoryTier.ARCHIVED)
        assert len(archived) == 1


# ---------------------------------------------------------------------------
# Explain
# ---------------------------------------------------------------------------

class TestExplain:

    def test_explain_returns_ok(self, stored_console, durable_entry):
        result = stored_console.explain(durable_entry.id)
        assert result.status == ConsoleStatus.OK

    def test_explain_contains_key_and_value(self, stored_console, durable_entry):
        result = stored_console.explain(durable_entry.id)
        assert "preferred_name" in result.data["explanation"]
        assert "Alchemist" in result.data["explanation"]

    def test_explain_contains_confidence(self, stored_console, durable_entry):
        result = stored_console.explain(durable_entry.id)
        assert "100%" in result.data["explanation"]

    def test_explain_contains_provenance_source(self, stored_console, durable_entry):
        result = stored_console.explain(durable_entry.id)
        assert "told me" in result.data["explanation"]

    def test_explain_contains_origin_context(self, stored_console, durable_entry):
        result = stored_console.explain(durable_entry.id)
        assert "call me Alchemist" in result.data["explanation"]

    def test_explain_with_active_response(self, stored_console, durable_entry):
        result = stored_console.explain(
            durable_entry.id,
            active_response="Good morning, Alchemist!"
        )
        assert "relevant to the current context" in result.data["explanation"]

    def test_explain_updates_last_used_at(self, stored_console, durable_entry):
        stored_console.explain(durable_entry.id, active_response="Hello!")
        entry = stored_console.read(durable_entry.id).entry
        assert entry.last_used_at is not None

    def test_explain_updates_last_used_context(self, stored_console, durable_entry):
        stored_console.explain(durable_entry.id, active_response="Hello, Alchemist!")
        entry = stored_console.read(durable_entry.id).entry
        assert entry.last_used_context == "Hello, Alchemist!"

    def test_explain_nonexistent_returns_not_found(self, console):
        result = console.explain("nonexistent")
        assert result.status == ConsoleStatus.NOT_FOUND


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

class TestExport:

    def test_export_all_returns_list(self, stored_console):
        export = stored_console.export_all()
        assert isinstance(export, list)
        assert len(export) == 1

    def test_export_entry_is_human_readable(self, stored_console):
        export = stored_console.export_all()
        entry = export[0]
        assert "key" in entry
        assert "value" in entry
        assert "confidence" in entry
        assert "source" in entry
        assert "created_at" in entry

    def test_export_empty_store(self, console):
        assert console.export_all() == []


# ---------------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------------

class TestSessionState:

    def test_set_and_get_session_state(self, console):
        session = SessionState(session_id="sess-001", gaian_id="test-gaian-001")
        console.set_session_state(session)
        retrieved = console.get_session_state()
        assert retrieved.session_id == "sess-001"

    def test_clear_session_state(self, console):
        session = SessionState(session_id="sess-001", gaian_id="test-gaian-001")
        console.set_session_state(session)
        console.clear_session_state()
        assert console.get_session_state() is None

    def test_session_and_durable_are_separate(self, console, durable_entry, session_entry):
        console.store(durable_entry)
        console.store(session_entry)
        durable_entries = console.browse(tier=MemoryTier.DURABLE)
        session_entries = console.browse(tier=MemoryTier.SESSION)
        assert len(durable_entries) == 1
        assert len(session_entries) == 1
        assert durable_entries[0].tier == MemoryTier.DURABLE
        assert session_entries[0].tier == MemoryTier.SESSION

    def test_promote_session_to_durable(self, console, session_entry):
        console.store(session_entry)
        session = SessionState(session_id="sess-001", gaian_id="test-gaian-001")
        promoted = session.promote_to_durable(session_entry)
        assert promoted.tier == MemoryTier.DURABLE

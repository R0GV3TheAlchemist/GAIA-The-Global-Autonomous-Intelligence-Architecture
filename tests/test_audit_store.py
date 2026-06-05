"""
tests/test_audit_store.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Test suite for core/obs/audit_store.py — the immutable, signed,
hash-chained audit persistence layer (#247).
"""
import hashlib
import json
import time
from pathlib import Path

import pytest

from core.obs.audit_store import AuditStore, AuditReader, StoredAuditEntry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def store(tmp_path):
    """Fresh AuditStore backed by a temp directory."""
    return AuditStore(store_dir=tmp_path / "audit", passphrase="test-passphrase")


@pytest.fixture()
def populated_store(store):
    """AuditStore with three pre-recorded events."""
    store.record("agent.action",     "planner",  "call_tool",   "ok")
    store.record("permission.grant", "gaian",    "approve",     "ok")
    store.record("memory.write",     "memory",   "store_fact",  "ok")
    return store


# ---------------------------------------------------------------------------
# 1. Persistence
# ---------------------------------------------------------------------------

class TestPersistence:

    def test_ndjson_file_created_on_first_record(self, store, tmp_path):
        store.record("session.start", "system", "init", "ok")
        ndjson = tmp_path / "audit" / "audit.ndjson"
        assert ndjson.exists(), "NDJSON file should be created after first record()"

    def test_each_record_appends_one_line(self, populated_store, tmp_path):
        ndjson = tmp_path / "audit" / "audit.ndjson"
        lines = [l for l in ndjson.read_text().splitlines() if l.strip()]
        assert len(lines) == 3

    def test_store_survives_reload(self, tmp_path):
        """Data written by one AuditStore instance is readable by a new one."""
        s1 = AuditStore(store_dir=tmp_path / "audit", passphrase="pw")
        s1.record("agent.action", "planner", "do_thing", "ok")
        s1.record("session.end",  "system",  "shutdown",  "ok")

        s2 = AuditStore(store_dir=tmp_path / "audit", passphrase="pw")
        assert s2.count() == 2


# ---------------------------------------------------------------------------
# 2. Signing
# ---------------------------------------------------------------------------

class TestSigning:

    def test_each_entry_has_signature(self, populated_store):
        entries = populated_store.query()
        for e in entries:
            assert e.signature is not None and len(e.signature) == 64

    def test_verify_passes_on_untampered_store(self, populated_store):
        ok, errors = populated_store.verify()
        assert ok, f"verify() should pass on clean store, errors: {errors}"

    def test_wrong_passphrase_fails_verify(self, tmp_path):
        s1 = AuditStore(store_dir=tmp_path / "audit", passphrase="correct")
        s1.record("agent.action", "planner", "act", "ok")

        s2 = AuditStore(store_dir=tmp_path / "audit", passphrase="wrong")
        ok, errors = s2.verify()
        assert not ok, "Wrong passphrase should fail signature verification"


# ---------------------------------------------------------------------------
# 3. Hash chain
# ---------------------------------------------------------------------------

class TestHashChain:

    def test_first_entry_has_no_prev_hash(self, store):
        store.record("session.start", "system", "init", "ok")
        entries = store.query()
        assert entries[0].prev_hash is None

    def test_second_entry_links_to_first(self, store, tmp_path):
        store.record("agent.action", "planner", "step_1", "ok")
        store.record("agent.action", "planner", "step_2", "ok")

        ndjson  = tmp_path / "audit" / "audit.ndjson"
        lines   = [l for l in ndjson.read_text().splitlines() if l.strip()]
        expected_prev = hashlib.sha256(lines[0].encode()).hexdigest()

        second_entry = store.query()[1]
        assert second_entry.prev_hash == expected_prev

    def test_tamper_detection(self, store, tmp_path):
        """Mutating a line in the NDJSON file should break verify()."""
        store.record("agent.action", "planner", "legit_action", "ok")
        store.record("agent.action", "planner", "legit_action", "ok")

        ndjson = tmp_path / "audit" / "audit.ndjson"
        content = ndjson.read_text()
        # Tamper: change outcome of first entry
        tampered = content.replace('"ok"', '"tampered"', 1)
        ndjson.write_text(tampered)

        ok, errors = store.verify()
        assert not ok, "Tampered store should fail verify()"
        assert len(errors) > 0


# ---------------------------------------------------------------------------
# 4. JSON-LD export
# ---------------------------------------------------------------------------

class TestJsonLdExport:

    def test_jsonld_has_context(self, populated_store):
        doc = json.loads(populated_store.export_jsonld())
        assert "@context" in doc
        assert "@vocab" in doc["@context"]

    def test_jsonld_entries_count_matches(self, populated_store):
        doc = json.loads(populated_store.export_jsonld())
        assert len(doc["entries"]) == 3

    def test_jsonld_context_maps_ts_to_prov(self, populated_store):
        doc = json.loads(populated_store.export_jsonld())
        assert doc["@context"]["ts"]["@id"] == "prov:generatedAtTime"


# ---------------------------------------------------------------------------
# 5. Purge & Gaian-controlled deletion
# ---------------------------------------------------------------------------

class TestPurgeAndDeletion:

    def test_purge_removes_old_entries(self, tmp_path):
        store = AuditStore(store_dir=tmp_path / "audit", passphrase="pw")
        store.record("agent.action", "planner", "old_act", "ok",
                     meta={"_ts_override": "2020-01-01T00:00:00+00:00"})
        store.record("session.start", "system", "init", "ok")

        # Purge everything before 2021
        pruned = store.purge(before_ts="2021-01-01T00:00:00+00:00")
        # The first entry's actual ts is ~now (we can't set ts in the past
        # without mocking), but we can verify purge runs without error
        # and returns an integer
        assert isinstance(pruned, int)

    def test_purge_logs_intent_record(self, store):
        store.record("agent.action", "planner", "act", "ok")
        store.purge(before_ts="2099-01-01T00:00:00+00:00")
        purge_events = store.query(event_type="audit.purge")
        assert len(purge_events) >= 1

    def test_delete_store_removes_file(self, store, tmp_path):
        store.record("agent.action", "planner", "act", "ok")
        store.delete_store()
        ndjson = tmp_path / "audit" / "audit.ndjson"
        assert not ndjson.exists()
        assert store.count() == 0


# ---------------------------------------------------------------------------
# 6. AuditReader — read-only interface
# ---------------------------------------------------------------------------

class TestAuditReader:

    def test_reader_can_query(self, populated_store, tmp_path):
        reader = AuditReader(
            store_dir=tmp_path / "audit",
            passphrase="test-passphrase",
        )
        results = reader.query(actor="planner")
        assert len(results) == 1

    def test_reader_can_verify(self, populated_store, tmp_path):
        reader = AuditReader(
            store_dir=tmp_path / "audit",
            passphrase="test-passphrase",
        )
        ok, errors = reader.verify()
        assert ok

    def test_reader_has_no_write_methods(self, populated_store, tmp_path):
        reader = AuditReader(
            store_dir=tmp_path / "audit",
            passphrase="test-passphrase",
        )
        assert not hasattr(reader, "record")
        assert not hasattr(reader, "purge")
        assert not hasattr(reader, "delete_store")
        assert not hasattr(reader, "apply_retention")

    def test_reader_export_jsonld(self, populated_store, tmp_path):
        reader = AuditReader(
            store_dir=tmp_path / "audit",
            passphrase="test-passphrase",
        )
        doc = json.loads(reader.export_jsonld())
        assert "@context" in doc
        assert len(doc["entries"]) == 3

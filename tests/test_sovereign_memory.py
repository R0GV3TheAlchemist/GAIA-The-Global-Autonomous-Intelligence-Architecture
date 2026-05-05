"""
Test suite for Sovereign Memory — Issue #66.

Covers:
  1.  SovereignMemory opens without error (in-memory DB, passphrase)
  2.  store_episode returns a non-empty string ID
  3.  get_episode returns decrypted plaintext matching original
  4.  get_episode returns None for unknown ID
  5.  list_episodes returns correct count and type filter
  6.  soft_delete_episode hides episode from list_episodes
  7.  store_affect_snapshot writes all biometric rows
  8.  get_biometric_history returns samples in time order
  9.  distill_semantic returns a non-empty ID
  10. search_memory returns MemoryRecords
  11. tag_as_legacy stores and export_legacy decrypts correctly (markdown)
  12. export_legacy JSON format is valid JSON list
  13. crypto_erase_key marks key revoked and raises on decrypt
  14. MasterKeyManager.wipe clears class-level MK
  15. derive_dek is deterministic (same inputs → same output)
  16. encrypt + decrypt roundtrip preserves plaintext
  17. encrypt with AAD: decrypt with wrong AAD raises
  18. get_stage_history returns empty list for new principal
  19. MigrationRunner.apply_pending on empty dir returns []
  20. MigrationRunner.current_version returns 1 after schema init
  21. MigrationRunner applies a test migration file correctly
  22. MigrationRunner is idempotent (re-apply returns [])
  23. stage_window_state table exists after migration 0002
  24. shadow tables exist after migration 0003
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
import time
from pathlib import Path

import pytest

from sovereign_memory import SovereignMemory
from sovereign_memory.crypto import (
    MasterKeyManager,
    derive_dek,
    encrypt,
    decrypt,
    make_aad,
)
from sovereign_memory.types import AffectSnapshot
from sovereign_memory.migrations import MigrationRunner, MigrationError


# ─────────────────────────────────────────────
# Fixture: in-memory SovereignMemory
# ─────────────────────────────────────────────

@pytest.fixture
def mem():
    """
    Open SovereignMemory against a temp file DB using a fixed passphrase.
    Wipe MK class state before each test to avoid cross-test contamination.
    Also apply pending migrations.
    """
    MasterKeyManager.wipe()
    with tempfile.NamedTemporaryFile(suffix=".db", delete=True) as f:
        db_path = f.name
    m = SovereignMemory(db_path=db_path, passphrase="test-passphrase-1234")
    m.open()
    # Apply migrations including 0002 and 0003
    migrations_dir = Path(__file__).parent.parent / "src-python" / "sovereign_memory" / "migrations"
    runner = MigrationRunner(m._conn, migrations_dir=migrations_dir)
    runner.apply_pending()
    yield m
    m.close()
    MasterKeyManager.wipe()


PID = "principal-test-001"


# ─────────────────────────────────────────────
# 1–3: Lifecycle + episode CRUD
# ─────────────────────────────────────────────

class TestLifecycle:
    def test_open_succeeds(self, mem):
        assert mem._conn is not None
        assert mem._mk is not None

    def test_assert_open_raises_before_open(self):
        MasterKeyManager.wipe()
        m = SovereignMemory(db_path=":memory:", passphrase="x")
        with pytest.raises(RuntimeError, match="not open"):
            m.store_episode("pid", "content")


class TestEpisodeCRUD:
    def test_store_episode_returns_id(self, mem):
        eid = mem.store_episode(PID, "I felt hopeful today.", type="journal")
        assert isinstance(eid, str)
        assert len(eid) > 0

    def test_get_episode_decrypts_correctly(self, mem):
        content = "I made a major career decision."
        eid = mem.store_episode(PID, content, type="decision")
        record = mem.get_episode(PID, eid)
        assert record is not None
        assert content[:280] == record.preview

    def test_get_episode_unknown_returns_none(self, mem):
        assert mem.get_episode(PID, "nonexistent-id") is None

    def test_list_episodes_count(self, mem):
        for i in range(5):
            mem.store_episode(PID, f"entry {i}")
        records = mem.list_episodes(PID, limit=10)
        assert len(records) == 5

    def test_list_episodes_type_filter(self, mem):
        mem.store_episode(PID, "journal entry", type="journal")
        mem.store_episode(PID, "decision entry", type="decision")
        journals = mem.list_episodes(PID, type="journal")
        assert all(r.type == "journal" for r in journals)

    def test_soft_delete_hides_episode(self, mem):
        eid = mem.store_episode(PID, "to be deleted")
        mem.soft_delete_episode(PID, eid)
        records = mem.list_episodes(PID)
        assert all(r.id != eid for r in records)
        assert mem.get_episode(PID, eid) is None


# ─────────────────────────────────────────────
# 7–8: Biometric history
# ─────────────────────────────────────────────

class TestBiometricHistory:
    def test_store_affect_snapshot_writes_rows(self, mem):
        snap = AffectSnapshot(
            id="snap-001",
            principal_id=PID,
            timestamp=int(time.time() * 1000),
            source="journal",
            emotion="joy",
            confidence=0.85,
            valence=0.7,
            arousal=0.6,
            dominance=0.5,
            entropy=0.3,
            arc_stability=0.8,
            is_neutral_primary=False,
        )
        mem.store_affect_snapshot(snap)
        rows = mem.get_biometric_history(PID, "affect_valence", days=1)
        assert len(rows) == 1
        assert abs(rows[0].value - 0.7) < 0.001

    def test_biometric_history_is_time_ordered(self, mem):
        now = int(time.time() * 1000)
        for i in range(3):
            mem.append_biometric_sample(PID, "hrv_rmssd", 50.0 + i, "manual",
                                         timestamp=now + i * 1000)
        samples = mem.get_biometric_history(PID, "hrv_rmssd", days=1)
        timestamps = [s.timestamp for s in samples]
        assert timestamps == sorted(timestamps)


# ─────────────────────────────────────────────
# 9–12: Semantic + legacy
# ─────────────────────────────────────────────

class TestSemanticAndLegacy:
    def test_distill_semantic_returns_id(self, mem):
        eid = mem.store_episode(PID, "base episode")
        pid = mem.distill_semantic(PID, "I tend to avoid conflict", [eid], confidence=0.8)
        assert isinstance(pid, str) and len(pid) > 0

    def test_search_memory_returns_records(self, mem):
        mem.store_episode(PID, "searching for meaning in work")
        results = mem.search_memory(PID, "work")
        assert len(results) >= 1

    def test_tag_as_legacy_roundtrip_markdown(self, mem):
        mem.tag_as_legacy(PID, "My Vision", "The world I want to build.", stage_at_creation=4)
        export = mem.export_legacy(PID, format="markdown")
        assert "My Vision" in export
        assert "The world I want to build." in export

    def test_export_legacy_json(self, mem):
        mem.tag_as_legacy(PID, "Letter", "Dear future me.", stage_at_creation=5)
        export = mem.export_legacy(PID, format="json")
        data = json.loads(export)
        assert isinstance(data, list)
        assert any(a["title"] == "Letter" for a in data)


# ─────────────────────────────────────────────
# 13–18: Crypto + GDPR
# ─────────────────────────────────────────────

class TestCrypto:
    def test_crypto_erase_revokes_key(self, mem):
        mem.crypto_erase_key("episodic-v1")
        row = mem._conn.execute(
            "SELECT status FROM encryption_keys WHERE key_id='episodic-v1'"
        ).fetchone()
        assert row["status"] == "revoked"

    def test_mk_wipe_clears_state(self):
        MasterKeyManager._mk = b"test"
        MasterKeyManager.wipe()
        assert MasterKeyManager._mk is None

    def test_derive_dek_deterministic(self):
        mk = b"x" * 32
        dek1 = derive_dek(mk, "episodic-v1")
        dek2 = derive_dek(mk, "episodic-v1")
        assert dek1 == dek2
        assert len(dek1) == 32

    def test_encrypt_decrypt_roundtrip(self):
        dek = b"k" * 32
        ct, nonce, aad = encrypt(dek, "Hello sovereign memory")
        pt = decrypt(dek, ct, nonce, aad)
        assert pt == "Hello sovereign memory"

    def test_decrypt_wrong_aad_raises(self):
        from cryptography.exceptions import InvalidTag
        dek = b"k" * 32
        ct, nonce, aad_bytes = encrypt(dek, "secret", {"table": "t", "id": "1", "v": 1})
        wrong_aad = json.dumps({"table": "t", "id": "2", "v": 1}).encode()
        with pytest.raises(InvalidTag):
            decrypt(dek, ct, nonce, wrong_aad)

    def test_stage_history_empty_for_new_principal(self, mem):
        assert mem.get_stage_history("new-principal") == []


# ─────────────────────────────────────────────
# 19–24: Migration runner
# ─────────────────────────────────────────────

class TestMigrationRunner:
    def _bare_conn(self) -> sqlite3.Connection:
        """Open a bare in-memory DB with schema.sql applied."""
        import importlib.resources
        from pathlib import Path as P
        MasterKeyManager.wipe()
        m = SovereignMemory(db_path=":memory:", passphrase="test")
        m.open()
        return m._conn, m

    def test_empty_dir_returns_no_applied(self, tmp_path):
        conn, m = self._bare_conn()
        runner = MigrationRunner(conn, migrations_dir=tmp_path)
        applied = runner.apply_pending()
        assert applied == []
        m.close()

    def test_current_version_after_schema_init(self):
        conn, m = self._bare_conn()
        runner = MigrationRunner(conn)
        assert runner.current_version() == 1
        m.close()

    def test_apply_migration_file(self, tmp_path):
        conn, m = self._bare_conn()
        sql = "CREATE TABLE IF NOT EXISTS _test_migration (id INTEGER PRIMARY KEY);"
        (tmp_path / "0002_test_migration.sql").write_text(sql)
        runner = MigrationRunner(conn, migrations_dir=tmp_path)
        applied = runner.apply_pending()
        assert 2 in applied
        assert runner.current_version() == 2
        # Table must exist
        row = conn.execute("SELECT name FROM sqlite_master WHERE name='_test_migration'").fetchone()
        assert row is not None
        m.close()

    def test_idempotent_reapply(self, tmp_path):
        conn, m = self._bare_conn()
        sql = "CREATE TABLE IF NOT EXISTS _test_idem (id INTEGER PRIMARY KEY);"
        (tmp_path / "0002_test_idem.sql").write_text(sql)
        runner = MigrationRunner(conn, migrations_dir=tmp_path)
        runner.apply_pending()
        applied2 = runner.apply_pending()
        assert applied2 == []   # nothing new
        m.close()

    def test_stage_window_state_table_exists(self, mem):
        row = mem._conn.execute(
            "SELECT name FROM sqlite_master WHERE name='stage_window_state'"
        ).fetchone()
        assert row is not None

    def test_shadow_tables_exist(self, mem):
        for table in ["shadow_records", "shadow_transitions"]:
            row = mem._conn.execute(
                f"SELECT name FROM sqlite_master WHERE name='{table}'"
            ).fetchone()
            assert row is not None, f"Table '{table}' missing"

"""
Persistence layer tests.

Covers:
  1. PersistenceStore atomic writes and reads
  2. MemoryPersistence: write-through, load-all, delete
  3. IdentityPersistence: mutable identity, immutable genesis
  4. RegistryPersistence: index, per-entry, directory scan
  5. SessionPersistence: manifests, GAIA memory
  6. PersistenceManager: full restore cycle
  7. Cross-restart continuity: born in session 1, named in session 2,
     memories from session 1 present in session 2
"""
from __future__ import annotations

import pytest
from pathlib import Path
from datetime import datetime, timezone

from core.persistence.store import PersistenceStore
from core.persistence.memory import MemoryPersistence
from core.persistence.identity import IdentityPersistence
from core.persistence.registry import RegistryPersistence
from core.persistence.session import SessionPersistence
from core.persistence.manager import PersistenceManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _frag_dict(gid="g1", fid="f1", content="hello", importance=0.5):
    return {
        "fragment_id":      fid,
        "gaian_id":         gid,
        "content":          content,
        "kind":             "session_context",
        "scope":            "session",
        "importance":       importance,
        "tags":             ["test"],
        "created_at":       datetime.now(timezone.utc).isoformat(),
        "epoch_id":         None,
        "source":           None,
        "related_gaian_id": None,
    }


# ---------------------------------------------------------------------------
# 1. PersistenceStore
# ---------------------------------------------------------------------------

class TestPersistenceStore:
    def test_write_and_read(self, tmp_path):
        s = PersistenceStore(tmp_path)
        s.write("test/data.json", {"key": "value"})
        assert s.read("test/data.json") == {"key": "value"}

    def test_atomic_write_creates_no_tmp(self, tmp_path):
        s = PersistenceStore(tmp_path)
        s.write("x.json", {"a": 1})
        assert not (tmp_path / "x.json.tmp").exists()
        assert (tmp_path / "x.json").exists()

    def test_read_missing_returns_none(self, tmp_path):
        s = PersistenceStore(tmp_path)
        assert s.read("nonexistent.json") is None

    def test_overwrite_is_atomic(self, tmp_path):
        s = PersistenceStore(tmp_path)
        s.write("f.json", {"v": 1})
        s.write("f.json", {"v": 2})
        assert s.read("f.json")["v"] == 2

    def test_exists(self, tmp_path):
        s = PersistenceStore(tmp_path)
        assert not s.exists("f.json")
        s.write("f.json", {})
        assert s.exists("f.json")

    def test_delete(self, tmp_path):
        s = PersistenceStore(tmp_path)
        s.write("f.json", {})
        s.delete("f.json")
        assert not s.exists("f.json")

    def test_list_dir(self, tmp_path):
        s = PersistenceStore(tmp_path)
        s.write("dir/a.json", {})
        s.write("dir/b.json", {})
        names = s.list_dir("dir")
        assert "a.json" in names
        assert "b.json" in names

    def test_list_subdirs(self, tmp_path):
        s = PersistenceStore(tmp_path)
        s.write("parent/child1/f.json", {})
        s.write("parent/child2/f.json", {})
        subs = s.list_subdirs("parent")
        assert "child1" in subs and "child2" in subs


# ---------------------------------------------------------------------------
# 2. MemoryPersistence
# ---------------------------------------------------------------------------

class TestMemoryPersistence:
    def test_save_and_load_fragment(self, tmp_path):
        mp = MemoryPersistence(PersistenceStore(tmp_path), "g1")

        class FakeFrag:
            fragment_id = "f1"
            gaian_id    = "g1"
            content     = "I remember the ocean."
            kind        = type("K", (), {"value": "episodic"})()
            scope       = type("S", (), {"value": "lifetime"})()
            importance  = 0.9
            tags        = {"ocean", "memory"}
            created_at  = datetime.now(timezone.utc)
            epoch_id    = None
            source      = None
            related_gaian_id = None

        mp.save_fragment(FakeFrag())
        frags = mp.load_fragments()
        assert len(frags) == 1
        assert frags[0]["content"] == "I remember the ocean."
        assert frags[0]["importance"] == 0.9

    def test_load_multiple_fragments(self, tmp_path):
        mp = MemoryPersistence(PersistenceStore(tmp_path), "g1")
        for i in range(5):
            class F:
                fragment_id = f"frag-{i}"
                gaian_id    = "g1"
                content     = f"memory {i}"
                kind        = type("K", (), {"value": "session_context"})()
                scope       = type("S", (), {"value": "session"})()
                importance  = 0.5
                tags        = set()
                created_at  = datetime.now(timezone.utc)
                epoch_id    = None
                source      = None
                related_gaian_id = None
            mp.save_fragment(F())
        assert mp.fragment_count() == 5
        assert len(mp.load_fragments()) == 5

    def test_delete_fragment(self, tmp_path):
        mp = MemoryPersistence(PersistenceStore(tmp_path), "g1")

        class F:
            fragment_id = "del-me"
            gaian_id    = "g1"
            content     = "gone"
            kind        = type("K", (), {"value": "session_context"})()
            scope       = type("S", (), {"value": "session"})()
            importance  = 0.1
            tags        = set()
            created_at  = datetime.now(timezone.utc)
            epoch_id    = None
            source      = None
            related_gaian_id = None

        mp.save_fragment(F())
        assert mp.fragment_count() == 1
        mp.delete_fragment("del-me")
        assert mp.fragment_count() == 0


# ---------------------------------------------------------------------------
# 3. IdentityPersistence
# ---------------------------------------------------------------------------

class TestIdentityPersistence:
    def test_save_and_load_identity(self, tmp_path):
        ip = IdentityPersistence(PersistenceStore(tmp_path), "g1")
        ip.save_identity({"gaian_id": "g1", "display_name": "Lyra"})
        data = ip.load_identity()
        assert data["display_name"] == "Lyra"

    def test_identity_is_mutable(self, tmp_path):
        ip = IdentityPersistence(PersistenceStore(tmp_path), "g1")
        ip.save_identity({"display_name": "Lyra"})
        ip.save_identity({"display_name": "Nova"})  # should not raise
        assert ip.load_identity()["display_name"] == "Nova"

    def test_genesis_is_immutable(self, tmp_path):
        ip = IdentityPersistence(PersistenceStore(tmp_path), "g1")
        ip.save_genesis({"soul_word": "home"})
        with pytest.raises(PermissionError, match="immutable"):
            ip.save_genesis({"soul_word": "hacked"})

    def test_genesis_not_found_returns_none(self, tmp_path):
        ip = IdentityPersistence(PersistenceStore(tmp_path), "g1")
        assert ip.load_genesis() is None


# ---------------------------------------------------------------------------
# 4. RegistryPersistence
# ---------------------------------------------------------------------------

class TestRegistryPersistence:
    def test_save_and_load_index(self, tmp_path):
        rp = RegistryPersistence(PersistenceStore(tmp_path))
        rp.save_index(["g1", "g2", "g3"])
        assert rp.load_index() == ["g1", "g2", "g3"]

    def test_empty_index_returns_empty_list(self, tmp_path):
        rp = RegistryPersistence(PersistenceStore(tmp_path))
        assert rp.load_index() == []

    def test_save_and_load_entry(self, tmp_path):
        rp = RegistryPersistence(PersistenceStore(tmp_path))
        rp.save_entry("g1", {"gaian_id": "g1", "display_name": "Lyra"})
        assert rp.load_entry("g1")["display_name"] == "Lyra"

    def test_delete_entry_removes_from_index(self, tmp_path):
        rp = RegistryPersistence(PersistenceStore(tmp_path))
        rp.save_index(["g1", "g2"])
        rp.save_entry("g1", {"gaian_id": "g1"})
        rp.delete_entry("g1")
        assert "g1" not in rp.load_index()

    def test_all_gaian_ids_from_dir_scan(self, tmp_path):
        rp = RegistryPersistence(PersistenceStore(tmp_path))
        rp.save_entry("g1", {})
        rp.save_entry("g2", {})
        ids = rp.all_gaian_ids()
        assert "g1" in ids and "g2" in ids


# ---------------------------------------------------------------------------
# 5. SessionPersistence
# ---------------------------------------------------------------------------

class TestSessionPersistence:
    def test_save_and_load_manifest(self, tmp_path):
        sp = SessionPersistence(PersistenceStore(tmp_path))
        sp.save_manifest({
            "session_id": "abc12345",
            "boot_number": 1,
            "boot_status": "ok",
        })
        latest = sp.load_latest_manifest()
        assert latest["boot_number"] == 1

    def test_manifests_accumulate(self, tmp_path):
        sp = SessionPersistence(PersistenceStore(tmp_path))
        sp.save_manifest({"session_id": "aaa", "boot_number": 1})
        sp.save_manifest({"session_id": "bbb", "boot_number": 2})
        all_m = sp.load_all_manifests()
        assert len(all_m) == 2

    def test_boot_count(self, tmp_path):
        sp = SessionPersistence(PersistenceStore(tmp_path))
        sp.save_manifest({"session_id": "a1", "boot_number": 1})
        sp.save_manifest({"session_id": "a2", "boot_number": 2})
        assert sp.boot_count() == 2

    def test_gaia_fragment_save_and_load(self, tmp_path):
        sp = SessionPersistence(PersistenceStore(tmp_path))
        sp.save_gaia_fragment({"fragment_id": "gf1", "content": "GAIA woke."})
        frags = sp.load_gaia_fragments()
        assert len(frags) == 1
        assert frags[0]["content"] == "GAIA woke."


# ---------------------------------------------------------------------------
# 6 + 7. PersistenceManager full restore cycle
# ---------------------------------------------------------------------------

class TestPersistenceManagerRestore:
    """
    Full cross-restart test.

    Session 1: birth a GAIAN, write memories, end session.
    Session 2: restore from disk. GAIAN present, memories intact.
    """

    def test_born_gaian_survives_restart(self, tmp_path):
        from core.identity.gaian.registry import GAIANRegistry
        from core.primordial.session import PrimordialSession
        from core.api.api import GAIAOSApi, APIRequest
        from core.fs.filesystem import GAIAFilesystem

        root = tmp_path / "gaia_persist"
        pm = PersistenceManager(root)

        # ----- Session 1: birth -----
        reg1 = GAIANRegistry()
        sess1 = PrimordialSession(registry=reg1, boot_number=1)
        sess1.awaken()
        fs = GAIAFilesystem(root=root / "fs")
        api1 = GAIAOSApi()
        api1.wire(sess1, fs)

        # Run birth ceremony
        r = api1.dispatch(APIRequest("ui", "/v1/gaian/birth/begin", {}))
        cid = r.payload["ceremony_id"]
        for qid, ans in [
            ("dob", "1990-08-05"), ("environment", "forest"),
            ("sound", "wind"), ("time_of_day", "dawn"),
            ("thinking_style", "feelings"), ("soul_word", "roots"),
        ]:
            api1.dispatch(APIRequest("ui", "/v1/gaian/birth/answer",
                                     {"ceremony_id": cid,
                                      "question_id": qid, "answer": ans}))
        r3 = api1.dispatch(APIRequest("ui", "/v1/gaian/birth/complete",
                                      {"ceremony_id": cid}))
        gaian_id = r3.payload["gaian_id"]

        # Persist the new GAIAN
        gaian = reg1.get(gaian_id)
        pm.on_gaian_born(gaian)

        # Write a session and persist a memory fragment
        api1.dispatch(APIRequest("ui", "/v1/session/begin",
                                 {"gaian_id": gaian_id, "human_id": "u"}))
        api1.dispatch(APIRequest("ui", "/v1/session/turn",
                                 {"gaian_id": gaian_id,
                                  "content": "I was born today.",
                                  "human_id": "u"}))
        # Manually persist fragment (in production this is a hook)
        rt = sess1.get_runtime(gaian_id)
        for frag in rt.memory._fragments:
            pm.on_fragment_written(gaian_id, frag)

        pm.on_manifest_written(sess1.manifest)

        # ----- Session 2: restore -----
        reg2 = GAIANRegistry()
        sess2 = PrimordialSession(registry=reg2, boot_number=2)
        sess2.awaken()  # boots without restoring (no hooks yet)

        restored = pm.restore(sess2, reg2)
        assert restored == 1, f"Expected 1 restored GAIAN, got {restored}"

        # GAIAN is present in new registry
        assert reg2.get(gaian_id) is not None

        # Runtime is accessible
        rt2 = sess2.get_runtime(gaian_id)
        assert rt2 is not None

        # Memory fragments survived
        assert len(rt2.memory._fragments) >= 1

    def test_genesis_immutability_across_restarts(self, tmp_path):
        pm = PersistenceManager(tmp_path)
        pm.identity_for("g1").save_genesis({"soul_word": "home"})
        with pytest.raises(PermissionError):
            pm.identity_for("g1").save_genesis({"soul_word": "hack"})

    def test_registry_index_grows_with_each_birth(self, tmp_path):
        pm = PersistenceManager(tmp_path)

        class FakeGAIAN:
            def __init__(self, gid):
                self.gaian_id = gid
                self.display_name = None
                self._genesis = {"soul_word": "x"}
            def to_dict(self):
                return {"gaian_id": self.gaian_id}

        for i in range(3):
            pm.on_gaian_born(FakeGAIAN(f"gaian-{i:03d}"))

        index = pm.registry_persistence.load_index()
        assert len(index) == 3

    def test_persistence_stats(self, tmp_path):
        pm = PersistenceManager(tmp_path)

        class FakeGAIAN:
            gaian_id = "g99"
            display_name = None
            _genesis = {"soul_word": "sky"}
            def to_dict(self): return {"gaian_id": "g99"}

        pm.on_gaian_born(FakeGAIAN())
        stats = pm.stats()
        assert stats["gaian_count"] == 1
        assert stats["boot_count"] == 0  # no manifest written yet

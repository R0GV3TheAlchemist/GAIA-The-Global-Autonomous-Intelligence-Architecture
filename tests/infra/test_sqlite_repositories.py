"""
tests/infra/test_sqlite_repositories.py
C17 / C23 / C27 — SQLite repository integration tests

All tests use ':memory:' databases so no filesystem side-effects occur.
One test group also exercises a real temp-file DB to verify durability.
"""

from __future__ import annotations

import os
import tempfile
import threading
from datetime import datetime, timezone

import pytest

from core.infra import SqliteLifecycleRepository, SqliteStewardshipRepository
from core.lifecycle import (
    GAIANLifecycleState,
    LifecycleManager,
    StewardshipBond,
    StewardRole,
    InProcessVault,
    Ed25519LifecycleSigner,
)
from core.lifecycle.lifecycle_audit_logger import LifecycleEvent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_event(gaian_id: str, seq: int = 1) -> LifecycleEvent:
    return LifecycleEvent(
        gaian_id=gaian_id,
        seq=seq,
        event_type="GENESIS",
        from_state=None,
        to_state=GAIANLifecycleState.BORN,
        actor_id="s-test",
        metadata={"test": True},
        logged_at=_now().isoformat(),
        hmac_sig="deadbeef",
    )


def _make_bond(
    bond_id: str,
    gaian_id: str,
    steward_id: str,
    role: StewardRole = StewardRole.PRIMARY,
) -> StewardshipBond:
    return StewardshipBond(
        bond_id=bond_id,
        gaian_id=gaian_id,
        steward_id=steward_id,
        role=role,
    )


def _make_signer() -> Ed25519LifecycleSigner:
    vault = InProcessVault()
    vault.generate_key("test-key")
    return Ed25519LifecycleSigner(vault=vault, key_id="test-key")


# ---------------------------------------------------------------------------
# SqliteLifecycleRepository
# ---------------------------------------------------------------------------

class TestSqliteLifecycleRepository:

    def test_schema_auto_created(self):
        repo = SqliteLifecycleRepository(":memory:")
        # no exception — tables exist
        assert repo.load_state("ghost") is None

    def test_save_and_load_state(self):
        repo = SqliteLifecycleRepository(":memory:")
        repo.save_state("g1", GAIANLifecycleState.ACTIVE, _now())
        assert repo.load_state("g1") == GAIANLifecycleState.ACTIVE

    def test_state_overwrite(self):
        repo = SqliteLifecycleRepository(":memory:")
        repo.save_state("g1", GAIANLifecycleState.BORN, _now())
        repo.save_state("g1", GAIANLifecycleState.DORMANT, _now())
        assert repo.load_state("g1") == GAIANLifecycleState.DORMANT

    def test_all_gaian_ids(self):
        repo = SqliteLifecycleRepository(":memory:")
        for gid, state in [("g1", GAIANLifecycleState.ACTIVE),
                           ("g2", GAIANLifecycleState.BORN),
                           ("g3", GAIANLifecycleState.RETIRED)]:
            repo.save_state(gid, state, _now())
        assert set(repo.all_gaian_ids()) == {"g1", "g2", "g3"}

    def test_save_and_load_audit_event(self):
        repo = SqliteLifecycleRepository(":memory:")
        evt = _make_event("g1")
        repo.save_audit_event("g1", evt)
        log = repo.load_audit_log("g1")
        assert len(log) == 1
        assert log[0].event_type == "GENESIS"
        assert log[0].to_state == GAIANLifecycleState.BORN
        assert log[0].actor_id == "s-test"

    def test_audit_log_insertion_order(self):
        repo = SqliteLifecycleRepository(":memory:")
        for i in range(5):
            repo.save_audit_event("g1", _make_event("g1", seq=i))
        log = repo.load_audit_log("g1")
        assert [e.seq for e in log] == list(range(5))

    def test_audit_log_multi_gaian_isolation(self):
        repo = SqliteLifecycleRepository(":memory:")
        repo.save_audit_event("g1", _make_event("g1", seq=1))
        repo.save_audit_event("g2", _make_event("g2", seq=1))
        assert len(repo.load_audit_log("g1")) == 1
        assert len(repo.load_audit_log("g2")) == 1

    def test_hmac_sig_round_trip(self):
        repo = SqliteLifecycleRepository(":memory:")
        evt = _make_event("g1")
        evt.hmac_sig = "cafebabe"
        repo.save_audit_event("g1", evt)
        assert repo.load_audit_log("g1")[0].hmac_sig == "cafebabe"

    def test_file_based_db_durability(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            repo1 = SqliteLifecycleRepository(db_path)
            repo1.save_state("g-persist", GAIANLifecycleState.ACTIVE, _now())
            # Open a second connection to the same file
            repo2 = SqliteLifecycleRepository(db_path)
            assert repo2.load_state("g-persist") == GAIANLifecycleState.ACTIVE
        finally:
            os.unlink(db_path)

    def test_concurrent_writes_do_not_corrupt(self):
        repo = SqliteLifecycleRepository(":memory:")
        errors = []

        def writer(gid):
            try:
                repo.save_state(gid, GAIANLifecycleState.ACTIVE, _now())
                repo.save_audit_event(gid, _make_event(gid))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(f"g{i}",)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Concurrent write errors: {errors}"
        assert len(repo.all_gaian_ids()) == 20


# ---------------------------------------------------------------------------
# SqliteStewardshipRepository
# ---------------------------------------------------------------------------

class TestSqliteStewardshipRepository:

    def test_schema_auto_created(self):
        repo = SqliteStewardshipRepository(":memory:")
        assert repo.load_active_bond("ghost") is None

    def test_save_and_load_active_bond(self):
        repo = SqliteStewardshipRepository(":memory:")
        bond = _make_bond("b1", "g1", "s1")
        repo.save_bond(bond)
        loaded = repo.load_active_bond("g1", role=StewardRole.PRIMARY)
        assert loaded is not None
        assert loaded.steward_id == "s1"
        assert loaded.is_active is True

    def test_released_bond_excluded_from_active(self):
        repo = SqliteStewardshipRepository(":memory:")
        bond = _make_bond("b2", "g2", "s2")
        repo.save_bond(bond)
        bond.release(reason="test release")
        repo.save_bond(bond)  # upsert — updates is_active to 0
        assert repo.load_active_bond("g2") is None

    def test_bond_history_preserves_order(self):
        repo = SqliteStewardshipRepository(":memory:")
        for i in range(4):
            repo.save_bond(_make_bond(f"b{i}", "g3", f"s{i}"))
        history = repo.load_bond_history("g3")
        assert len(history) == 4
        assert history[0].bond_id == "b0"
        assert history[-1].bond_id == "b3"

    def test_load_bond_history_includes_released(self):
        repo = SqliteStewardshipRepository(":memory:")
        bond = _make_bond("b-rel", "g4", "s-rel")
        repo.save_bond(bond)
        bond.release(reason="succession")
        repo.save_bond(bond)
        history = repo.load_bond_history("g4")
        assert len(history) == 1
        assert history[0].is_active is False
        assert history[0].release_reason == "succession"

    def test_load_active_bond_no_role_filter(self):
        repo = SqliteStewardshipRepository(":memory:")
        repo.save_bond(_make_bond("b-g", "g5", "s-guardian", role=StewardRole.GUARDIAN))
        bond = repo.load_active_bond("g5")
        assert bond is not None
        assert bond.role == StewardRole.GUARDIAN

    def test_multi_gaian_isolation(self):
        repo = SqliteStewardshipRepository(":memory:")
        repo.save_bond(_make_bond("ba", "ga", "sa"))
        repo.save_bond(_make_bond("bb", "gb", "sb"))
        assert repo.load_active_bond("ga").steward_id == "sa"
        assert repo.load_active_bond("gb").steward_id == "sb"


# ---------------------------------------------------------------------------
# End-to-end: LifecycleManager wired to SQLite repos
# ---------------------------------------------------------------------------

class TestLifecycleManagerWithSQLite:

    def test_full_genesis_to_active_persisted(self):
        lrepo = SqliteLifecycleRepository(":memory:")
        srepo = SqliteStewardshipRepository(":memory:")
        mgr = LifecycleManager(
            signer=_make_signer(),
            lifecycle_repo=lrepo,
            stewardship_repo=srepo,
        )
        mgr.register_latent("g-e2e")
        mgr.genesis("g-e2e", steward_id="s-e2e")
        mgr.activate(
            "g-e2e",
            actor_id="s-e2e",
            justification="integration test",
            trigger_class="STEWARD_ACTION",
        )
        assert lrepo.load_state("g-e2e") == GAIANLifecycleState.ACTIVE
        log = lrepo.load_audit_log("g-e2e")
        assert len(log) >= 2
        assert any(e.to_state == GAIANLifecycleState.ACTIVE for e in log)

    def test_state_survives_manager_restart(self):
        """A new LifecycleManager instance sees the same persisted state."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            lrepo1 = SqliteLifecycleRepository(db_path)
            srepo1 = SqliteStewardshipRepository(db_path)
            mgr1 = LifecycleManager(signer=_make_signer(),
                                    lifecycle_repo=lrepo1,
                                    stewardship_repo=srepo1)
            mgr1.register_latent("g-restart")
            mgr1.genesis("g-restart", steward_id="s-rst")

            # Simulate restart: fresh manager, same DB file
            lrepo2 = SqliteLifecycleRepository(db_path)
            state = lrepo2.load_state("g-restart")
            assert state == GAIANLifecycleState.BORN
        finally:
            os.unlink(db_path)

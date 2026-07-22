# Copyright (c) 2026 Kyle Alexander Steen (R0GV3 The Alchemist). All Rights Reserved.
# NEXUS Planetary Ledger — Phase E test suite
# Tests: append, DAG chaining, signature verification, SQLite persistence,
#        replay-on-restart, query filtering, chain traversal.

from __future__ import annotations

import json
from pathlib import Path

import pytest

from planetary_ledger import EventType, PlanetaryLedger
from planetary_ledger.dag import MerkleDAG
from planetary_ledger.event import LedgerEvent
from planetary_ledger.signer import Ed25519Signer, HMACSigner


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ledger(tmp_path: Path) -> PlanetaryLedger:
    return PlanetaryLedger(
        db_path=tmp_path / "test_ledger.db",
        node_id="aaaaaaaa-0000-0000-0000-000000000001",
        signer=HMACSigner(b"test-secret"),
        session_id="session-test-001",
    )


# ---------------------------------------------------------------------------
# LedgerEvent unit tests
# ---------------------------------------------------------------------------

class TestLedgerEvent:
    def test_to_dict_required_fields(self):
        e = LedgerEvent(
            event_type=EventType.SESSION_INIT,
            source_node="aaaaaaaa-0000-0000-0000-000000000001",
            payload={"key": "value"},
        )
        d = e.to_dict()
        assert "event_id" in d
        assert d["event_type"] == "session_init"
        assert d["signature"]["algorithm"] == "HMAC-SHA256"

    def test_roundtrip_from_dict(self):
        e = LedgerEvent(
            event_type=EventType.GOVERNANCE_AUDIT,
            source_node="bbbbbbbb-0000-0000-0000-000000000002",
            payload={"audit": True},
            tags=["phase-e"],
        )
        d = e.to_dict()
        e2 = LedgerEvent.from_dict(d)
        assert e2.event_id == e.event_id
        assert e2.event_type == EventType.GOVERNANCE_AUDIT
        assert e2.tags == ["phase-e"]

    def test_all_event_types_valid(self):
        for et in EventType:
            e = LedgerEvent(
                event_type=et,
                source_node="cccccccc-0000-0000-0000-000000000003",
                payload={},
            )
            assert e.to_dict()["event_type"] == et.value


# ---------------------------------------------------------------------------
# MerkleDAG unit tests
# ---------------------------------------------------------------------------

class TestMerkleDAG:
    def test_add_root_node(self):
        dag = MerkleDAG()
        e = LedgerEvent(
            event_type=EventType.SESSION_INIT,
            source_node="node-1",
            payload={},
        )
        node = dag.add(e.to_dict())
        assert node.content_hash
        assert node.parent_event_id is None
        assert dag.roots == [node.event_id]

    def test_parent_child_link(self):
        dag = MerkleDAG()
        e1 = LedgerEvent(event_type=EventType.SESSION_INIT, source_node="n", payload={})
        e2 = LedgerEvent(
            event_type=EventType.SESSION_CLOSE,
            source_node="n",
            payload={},
            parent_event_id=e1.event_id,
        )
        dag.add(e1.to_dict())
        dag.add(e2.to_dict())
        parent_node = dag.get(e1.event_id)
        assert e2.event_id in parent_node.children

    def test_verify_chain_passes(self):
        dag = MerkleDAG()
        e = LedgerEvent(event_type=EventType.CUSTOM, source_node="n", payload={"x": 1})
        d = e.to_dict()
        dag.add(d)
        assert dag.verify_chain(e.event_id, d) is True

    def test_verify_chain_fails_tampered(self):
        dag = MerkleDAG()
        e = LedgerEvent(event_type=EventType.CUSTOM, source_node="n", payload={"x": 1})
        d = e.to_dict()
        dag.add(d)
        tampered = dict(d)
        tampered["payload"] = {"x": 999}
        assert dag.verify_chain(e.event_id, tampered) is False

    def test_ancestors_chain(self):
        dag = MerkleDAG()
        ids = []
        prev = None
        for i in range(5):
            e = LedgerEvent(
                event_type=EventType.CUSTOM,
                source_node="n",
                payload={"i": i},
                parent_event_id=prev,
            )
            dag.add(e.to_dict())
            ids.append(e.event_id)
            prev = e.event_id
        chain = dag.ancestors(ids[-1])
        assert chain == ids[:-1]


# ---------------------------------------------------------------------------
# HMACSigner unit tests
# ---------------------------------------------------------------------------

class TestHMACSigner:
    def test_sign_and_verify(self):
        signer = HMACSigner(b"secret")
        e = LedgerEvent(event_type=EventType.CUSTOM, source_node="n", payload={})
        d = e.to_dict()
        sig = signer.sign(d)
        assert signer.verify(d, sig) is True

    def test_verify_fails_wrong_secret(self):
        s1 = HMACSigner(b"secret-a")
        s2 = HMACSigner(b"secret-b")
        e = LedgerEvent(event_type=EventType.CUSTOM, source_node="n", payload={})
        d = e.to_dict()
        sig = s1.sign(d)
        assert s2.verify(d, sig) is False

    def test_verify_fails_tampered_payload(self):
        signer = HMACSigner(b"secret")
        e = LedgerEvent(event_type=EventType.CUSTOM, source_node="n", payload={"x": 1})
        d = e.to_dict()
        sig = signer.sign(d)
        d["payload"] = {"x": 999}
        assert signer.verify(d, sig) is False


# ---------------------------------------------------------------------------
# Ed25519Signer unit tests
# ---------------------------------------------------------------------------

class TestEd25519Signer:
    def test_ephemeral_sign_verify(self):
        signer = Ed25519Signer()  # generates ephemeral key pair
        e = LedgerEvent(event_type=EventType.GOVERNANCE_AUDIT, source_node="n", payload={})
        d = e.to_dict()
        sig = signer.sign(d)
        assert signer.verify(d, sig) is True

    def test_algorithm_reported(self):
        signer = Ed25519Signer()
        assert signer.algorithm in ("Ed25519", "HMAC-SHA256")


# ---------------------------------------------------------------------------
# PlanetaryLedger integration tests
# ---------------------------------------------------------------------------

class TestPlanetaryLedger:
    def test_append_single_event(self, ledger):
        e = ledger.append(EventType.SESSION_INIT, {"start": True})
        assert e.event_id
        assert e.source_node == "aaaaaaaa-0000-0000-0000-000000000001"
        assert ledger.size == 1

    def test_chain_links_automatically(self, ledger):
        e1 = ledger.append(EventType.SESSION_INIT, {})
        e2 = ledger.append(EventType.MEMORY_COMMIT, {"data": "abc"})
        assert e2.parent_event_id == e1.event_id

    def test_verify_event_passes(self, ledger):
        e = ledger.append(EventType.GOVERNANCE_AUDIT, {"audit": "ok"})
        assert ledger.verify_event(e.event_id) is True

    def test_verify_nonexistent_event(self, ledger):
        assert ledger.verify_event("nonexistent-id") is False

    def test_query_by_event_type(self, ledger):
        ledger.append(EventType.SESSION_INIT, {})
        ledger.append(EventType.SCHUMANN_SYNC, {"freq": 7.83})
        ledger.append(EventType.SESSION_CLOSE, {})
        results = ledger.query(event_type=EventType.SCHUMANN_SYNC)
        assert len(results) == 1
        assert results[0]["event_type"] == "schumann_sync"

    def test_query_by_session_id(self, ledger):
        ledger.append(EventType.CAPABILITY_GRANTED, {"cap": "read"})
        results = ledger.query(session_id="session-test-001")
        assert len(results) >= 1

    def test_get_chain(self, ledger):
        e1 = ledger.append(EventType.SESSION_INIT, {})
        e2 = ledger.append(EventType.MEMORY_COMMIT, {})
        e3 = ledger.append(EventType.SESSION_CLOSE, {})
        chain = ledger.get_chain(e3.event_id)
        assert e1.event_id in chain
        assert e2.event_id in chain

    def test_replay_on_restart(self, tmp_path):
        db = tmp_path / "replay.db"
        l1 = PlanetaryLedger(db_path=db, signer=HMACSigner(b"secret"))
        e = l1.append(EventType.SESSION_INIT, {"boot": True})
        original_id = e.event_id

        # Simulate restart
        l2 = PlanetaryLedger(db_path=db, signer=HMACSigner(b"secret"))
        assert l2.size == 1
        assert l2.dag.get(original_id) is not None

    def test_tags_persisted(self, ledger):
        e = ledger.append(EventType.CUSTOM, {}, tags=["phase-e", "test"])
        results = ledger.query(event_type=EventType.CUSTOM)
        assert "phase-e" in results[0]["tags"]

    def test_multiple_event_types(self, ledger):
        for et in [EventType.CAPABILITY_GRANTED, EventType.TWIN_SYNC, EventType.CRISIS_TRIGGERED]:
            ledger.append(et, {"et": et.value})
        assert ledger.size == 3

    def test_dag_size_matches_ledger(self, ledger):
        for i in range(10):
            ledger.append(EventType.CUSTOM, {"i": i})
        assert ledger.dag.size == 10
        assert ledger.size == 10

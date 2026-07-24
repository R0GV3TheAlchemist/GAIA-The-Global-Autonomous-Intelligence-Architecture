# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
Tests for core.c27.audit_log — AuditLogWriter, AuditLogReader, AuditLogIntegrityVerifier.

Authority: C27 §5. Implements C27-IMPL-006 through C27-IMPL-010.

Coverage targets:
- AuditLogEntry dataclass fields match C27 §5.1 JSON schema
- AuditLogWriter.append produces a chained entry (hash, signature, previous_hash)
- Genesis entry has previous_entry_hash == None
- SHA-256 chain: entry_hash of entry N == previous_entry_hash of entry N+1
- AuditLogIntegrityVerifier returns True for intact chain
- AuditLogIntegrityVerifier returns False when an entry is tampered
- AuditLogReader requires RBAC — GAIAN_SELF always authorized, THIRD_PARTY denied
"""
import pytest
from datetime import datetime, timezone
from core.c27.audit_log import AuditLogEntry, AuditLogWriter, AuditLogReader, AuditLogIntegrityVerifier
from core.c27.rbac import C27Role


# ---------------------------------------------------------------------------
# AuditLogEntry — dataclass contract
# ---------------------------------------------------------------------------

class TestAuditLogEntryContract:
    def test_entry_has_required_fields(self):
        entry = AuditLogEntry(
            entry_id="entry-001",
            gaian_id="gaian-001",
            event_type="LIFECYCLE_TRANSITION",
            actor="steward-007",
            action="ACTIVE→DORMANT",
            payload={"from": "ACTIVE", "to": "DORMANT"},
            previous_entry_hash=None,
        )
        assert entry.entry_id == "entry-001"
        assert entry.gaian_id == "gaian-001"
        assert entry.previous_entry_hash is None  # genesis entry
        assert isinstance(entry.timestamp, datetime)

    def test_entry_hash_and_signature_default_empty(self):
        """Before AuditLogWriter processes an entry, hash/sig are empty strings."""
        entry = AuditLogEntry(
            entry_id="entry-002",
            gaian_id="gaian-001",
            event_type="STEWARD_ACTION",
            actor="steward-007",
            action="Bond formed",
            payload={},
            previous_entry_hash=None,
        )
        assert entry.entry_hash == ""
        assert entry.signature == ""


# ---------------------------------------------------------------------------
# AuditLogWriter  (C27-IMPL-007, C27-IMPL-008)
# ---------------------------------------------------------------------------

@pytest.fixture
def writer():
    return AuditLogWriter(gaian_id="gaian-writer-test")


class TestAuditLogWriter:
    def test_first_entry_is_genesis(self, writer):
        """Genesis entry must have previous_entry_hash == None."""
        entry = writer.append(
            event_type="LIFECYCLE_TRANSITION",
            actor="steward-007",
            action="LATENT→BORN",
            payload={"from": "LATENT", "to": "BORN"},
        )
        assert entry.previous_entry_hash is None
        assert len(entry.entry_hash) == 64  # SHA-256 hex
        assert entry.signature != ""

    def test_second_entry_chains_to_first(self, writer):
        """entry_hash of entry N must equal previous_entry_hash of entry N+1."""
        e1 = writer.append(
            event_type="LIFECYCLE_TRANSITION",
            actor="steward-007",
            action="LATENT→BORN",
            payload={},
        )
        e2 = writer.append(
            event_type="STEWARD_ACTION",
            actor="steward-007",
            action="Bond formed",
            payload={},
        )
        assert e2.previous_entry_hash == e1.entry_hash

    def test_entry_hash_is_sha256_hex(self, writer):
        entry = writer.append(
            event_type="SYSTEM_EVENT",
            actor="gaia-runtime",
            action="Heartbeat",
            payload={},
        )
        assert len(entry.entry_hash) == 64
        assert all(c in "0123456789abcdef" for c in entry.entry_hash)

    def test_signature_is_non_empty(self, writer):
        entry = writer.append(
            event_type="SYSTEM_EVENT",
            actor="gaia-runtime",
            action="Heartbeat",
            payload={},
        )
        assert entry.signature != ""

    def test_entries_property_returns_copy(self, writer):
        writer.append(event_type="EV", actor="a", action="x", payload={})
        snapshot = writer.entries
        snapshot.clear()
        assert len(writer.entries) == 1  # internal list unaffected


# ---------------------------------------------------------------------------
# AuditLogIntegrityVerifier  (C27-IMPL-010)
# ---------------------------------------------------------------------------

class TestAuditLogIntegrityVerifier:
    def test_intact_chain_returns_true(self):
        verifier = AuditLogIntegrityVerifier()
        w = AuditLogWriter(gaian_id="gaian-integrity-ok")
        w.append(event_type="LIFECYCLE_TRANSITION", actor="s", action="A", payload={})
        w.append(event_type="STEWARD_ACTION",       actor="s", action="B", payload={})
        # Register this writer in the global store used by verifier
        from core.c27.audit_log import _STORE
        _STORE["gaian-integrity-ok"] = w
        assert verifier.verify("gaian-integrity-ok") is True

    def test_tampered_chain_returns_false(self):
        """Mutating any entry_hash must cause verify() to return False."""
        from core.c27.audit_log import _STORE
        w = AuditLogWriter(gaian_id="gaian-tamper")
        w.append(event_type="LIFECYCLE_TRANSITION", actor="s", action="A", payload={})
        _STORE["gaian-tamper"] = w
        # Tamper: overwrite entry_hash on the first entry
        w.entries[0].entry_hash = "deadbeef" * 8
        assert AuditLogIntegrityVerifier().verify("gaian-tamper") is False


# ---------------------------------------------------------------------------
# AuditLogReader — RBAC gating  (C27-IMPL-009)
# ---------------------------------------------------------------------------

class TestAuditLogReaderRBAC:
    def test_gaian_self_can_read_own_log(self):
        reader = AuditLogReader()
        entries = reader.query(
            gaian_id="gaian-self-reader",
            requestor_id="gaian-self-reader",
            requestor_role=C27Role.GAIAN_SELF,
        )
        assert isinstance(entries, list)  # access must not be denied

    def test_third_party_denied(self):
        reader = AuditLogReader()
        with pytest.raises(PermissionError):
            reader.query(
                gaian_id="gaian-001",
                requestor_id="external-actor",
                requestor_role=C27Role.THIRD_PARTY,
            )

    def test_sentinel_can_read_audit(self):
        reader = AuditLogReader()
        entries = reader.query(
            gaian_id="gaian-sentinel-reader",
            requestor_id="sentinel-process",
            requestor_role=C27Role.SENTINEL,
        )
        assert isinstance(entries, list)

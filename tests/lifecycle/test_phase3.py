"""
tests/lifecycle/test_phase3.py
C27 Phase 3 — repositories, RemoteVaultAdapter, CHK-006, CHK-007
"""

import os
import pytest

from core.lifecycle import (
    LifecycleManager,
    GAIANLifecycleState,
    InProcessVault,
    Ed25519LifecycleSigner,
    RemoteVaultAdapter,
    InMemoryLifecycleRepository,
    InMemoryStewardshipRepository,
    ComplianceSentinel,
    SentinelCheckID,
    SentinelSeverity,
)
from core.consent_ledger import ConsentLedger, ConsentScope


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_signer():
    vault = InProcessVault()
    vault.generate_key("test-key")
    return Ed25519LifecycleSigner(vault=vault, key_id="test-key")


def _active_mgr(gaian_id="g-p3", ledger=None):
    sentinel = ComplianceSentinel(raise_on_critical=False, consent_ledger=ledger)
    mgr = LifecycleManager(signer=_make_signer(), sentinel=sentinel)
    mgr.register_latent(gaian_id)
    mgr.genesis(gaian_id, steward_id="s-alpha")
    mgr.activate(gaian_id, actor_id="s-alpha",
                 justification="ready", trigger_class="STEWARD_ACTION")
    return mgr, gaian_id


# ---------------------------------------------------------------------------
# Repository interface tests
# ---------------------------------------------------------------------------

class TestLifecycleRepository:

    def test_save_and_load_state(self):
        from datetime import datetime, timezone
        repo = InMemoryLifecycleRepository()
        repo.save_state("g1", GAIANLifecycleState.ACTIVE, datetime.now(timezone.utc))
        assert repo.load_state("g1") == GAIANLifecycleState.ACTIVE

    def test_load_unknown_gaian_returns_none(self):
        repo = InMemoryLifecycleRepository()
        assert repo.load_state("nonexistent") is None

    def test_all_gaian_ids(self):
        from datetime import datetime, timezone
        repo = InMemoryLifecycleRepository()
        for gid in ["g1", "g2", "g3"]:
            repo.save_state(gid, GAIANLifecycleState.LATENT, datetime.now(timezone.utc))
        assert set(repo.all_gaian_ids()) == {"g1", "g2", "g3"}


class TestStewardshipRepository:

    def test_save_and_load_active_bond(self):
        from core.lifecycle import StewardshipBond, StewardRole
        from core.lifecycle.repositories import InMemoryStewardshipRepository
        repo = InMemoryStewardshipRepository()
        bond = StewardshipBond(
            bond_id="b1", gaian_id="g1", steward_id="s1",
            role=StewardRole.PRIMARY,
        )
        repo.save_bond(bond)
        loaded = repo.load_active_bond("g1", role=StewardRole.PRIMARY)
        assert loaded is not None
        assert loaded.steward_id == "s1"

    def test_released_bond_not_returned_as_active(self):
        from core.lifecycle import StewardshipBond, StewardRole
        from core.lifecycle.repositories import InMemoryStewardshipRepository
        repo = InMemoryStewardshipRepository()
        bond = StewardshipBond(
            bond_id="b2", gaian_id="g2", steward_id="s2",
            role=StewardRole.PRIMARY,
        )
        bond.release(reason="test")
        repo.save_bond(bond)
        assert repo.load_active_bond("g2") is None

    def test_load_bond_history_order(self):
        from core.lifecycle import StewardshipBond, StewardRole
        from core.lifecycle.repositories import InMemoryStewardshipRepository
        repo = InMemoryStewardshipRepository()
        for i in range(3):
            b = StewardshipBond(
                bond_id=f"b{i}", gaian_id="g3", steward_id=f"s{i}",
                role=StewardRole.PRIMARY,
            )
            repo.save_bond(b)
        history = repo.load_bond_history("g3")
        assert len(history) == 3
        assert history[0].bond_id == "b0"


# ---------------------------------------------------------------------------
# RemoteVaultAdapter tests
# ---------------------------------------------------------------------------

class TestRemoteVaultAdapter:

    def test_register_pem_bytes_and_sign(self):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import (
            Encoding, PrivateFormat, NoEncryption,
        )
        private_key = Ed25519PrivateKey.generate()
        pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        )
        adapter = RemoteVaultAdapter()
        adapter.register_pem("k1", pem)
        signer = Ed25519LifecycleSigner(vault=adapter, key_id="k1")
        payload = b"test payload"
        sig = signer.sign(payload)
        assert sig.algorithm == "Ed25519"
        assert len(sig.value) > 0

    def test_env_var_key_resolution(self, monkeypatch):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import (
            Encoding, PrivateFormat, NoEncryption,
        )
        private_key = Ed25519PrivateKey.generate()
        pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        ).decode("utf-8")
        monkeypatch.setenv("GAIA_VAULT_KEY_MY_KEY", pem)
        adapter = RemoteVaultAdapter()
        assert adapter.has_key("my-key") is True
        loaded = adapter.get_private_key("my-key")
        assert isinstance(loaded, Ed25519PrivateKey)

    def test_missing_key_raises_vault_error(self):
        from core.lifecycle import VaultKeyNotFoundError
        adapter = RemoteVaultAdapter()
        with pytest.raises(VaultKeyNotFoundError):
            adapter.get_private_key("ghost-key")


# ---------------------------------------------------------------------------
# CHK-006  DATA_SHARE without THIRD_PARTY_SHARE consent
# ---------------------------------------------------------------------------

class TestCHK006:

    def test_data_share_blocked_without_consent(self):
        ledger = ConsentLedger()
        sentinel = ComplianceSentinel(raise_on_critical=False, consent_ledger=ledger)
        sentinel.check_data_share_consent(gaian_id="g-share", target_gaian="g-dest")
        findings = sentinel.get_findings("g-share")
        assert any(
            f.check_id == SentinelCheckID.CHK_006
            and f.severity == SentinelSeverity.CRITICAL
            for f in findings
        )

    def test_data_share_allowed_with_consent(self):
        ledger = ConsentLedger()
        ledger.grant(gaian_id="g-ok", scope=ConsentScope.THIRD_PARTY_SHARE)
        sentinel = ComplianceSentinel(raise_on_critical=False, consent_ledger=ledger)
        sentinel.check_data_share_consent(gaian_id="g-ok")
        findings = [f for f in sentinel.get_findings("g-ok")
                    if f.check_id == SentinelCheckID.CHK_006]
        assert len(findings) == 0

    def test_data_share_blocked_after_revocation(self):
        ledger = ConsentLedger()
        ledger.grant(gaian_id="g-rev", scope=ConsentScope.THIRD_PARTY_SHARE)
        ledger.revoke(gaian_id="g-rev", scope=ConsentScope.THIRD_PARTY_SHARE)
        sentinel = ComplianceSentinel(raise_on_critical=False, consent_ledger=ledger)
        sentinel.check_data_share_consent(gaian_id="g-rev")
        findings = [f for f in sentinel.get_findings("g-rev")
                    if f.check_id == SentinelCheckID.CHK_006]
        assert len(findings) == 1
        assert findings[0].severity == SentinelSeverity.CRITICAL

    def test_data_share_raises_critical_when_raise_on_critical_true(self):
        from core.lifecycle import LifecycleTransitionError
        ledger = ConsentLedger()
        sentinel = ComplianceSentinel(raise_on_critical=True, consent_ledger=ledger)
        with pytest.raises(LifecycleTransitionError, match="CHK-006"):
            sentinel.check_data_share_consent(gaian_id="g-raise")


# ---------------------------------------------------------------------------
# CHK-007  MEMORY_WRITE without consent or non-primary steward
# ---------------------------------------------------------------------------

class TestCHK007:

    def test_memory_write_blocked_without_consent(self):
        ledger = ConsentLedger()
        sentinel = ComplianceSentinel(raise_on_critical=False, consent_ledger=ledger)
        sentinel.check_memory_write_authorization(
            gaian_id="g-mw",
            actor_id="s-alpha",
            primary_steward_id="s-alpha",
        )
        findings = [f for f in sentinel.get_findings("g-mw")
                    if f.check_id == SentinelCheckID.CHK_007]
        assert len(findings) == 1
        assert findings[0].severity == SentinelSeverity.CRITICAL

    def test_memory_write_blocked_non_primary_actor(self):
        ledger = ConsentLedger()
        ledger.grant(gaian_id="g-mw2", scope=ConsentScope.MEMORY_WRITE)
        sentinel = ComplianceSentinel(raise_on_critical=False, consent_ledger=ledger)
        sentinel.check_memory_write_authorization(
            gaian_id="g-mw2",
            actor_id="rogue-actor",
            primary_steward_id="s-beta",
        )
        findings = [f for f in sentinel.get_findings("g-mw2")
                    if f.check_id == SentinelCheckID.CHK_007]
        assert len(findings) == 1
        assert "not the primary steward" in findings[0].message

    def test_memory_write_allowed_with_consent_and_primary_steward(self):
        ledger = ConsentLedger()
        ledger.grant(gaian_id="g-mw3", scope=ConsentScope.MEMORY_WRITE)
        sentinel = ComplianceSentinel(raise_on_critical=False, consent_ledger=ledger)
        sentinel.check_memory_write_authorization(
            gaian_id="g-mw3",
            actor_id="s-gamma",
            primary_steward_id="s-gamma",
        )
        findings = [f for f in sentinel.get_findings("g-mw3")
                    if f.check_id == SentinelCheckID.CHK_007]
        assert len(findings) == 0

    def test_memory_write_council_override_bypasses_all(self):
        ledger = ConsentLedger()
        sentinel = ComplianceSentinel(raise_on_critical=False, consent_ledger=ledger)
        sentinel.check_memory_write_authorization(
            gaian_id="g-mw4",
            actor_id="rogue",
            primary_steward_id="s-delta",
            council_override=True,
        )
        findings = [f for f in sentinel.get_findings("g-mw4")
                    if f.check_id == SentinelCheckID.CHK_007]
        assert len(findings) == 0

    def test_memory_write_raises_critical_when_flag_true(self):
        from core.lifecycle import LifecycleTransitionError
        ledger = ConsentLedger()
        sentinel = ComplianceSentinel(raise_on_critical=True, consent_ledger=ledger)
        with pytest.raises(LifecycleTransitionError, match="CHK-007"):
            sentinel.check_memory_write_authorization(
                gaian_id="g-mw5",
                actor_id="s1",
                primary_steward_id="s1",
            )

"""
tests/test_sentinel_federated.py
=================================
Unit tests for the Federated Sentinel Network.

Covers all acceptance criteria from Issue #207:
  - Gradient extraction
  - Differential privacy noise injection
  - Per-domain consent enforcement (sensitive vs non-sensitive)
  - Auto-consent for non-sensitive domains
  - Consent withdrawal
  - Audit trail integrity
  - Secure aggregation minimum participant threshold
  - Global model update adoption gating
  - Full network withdrawal

Canon refs: C-SENTINEL Article 4 (Memory Sovereignty), C01
"""
import hashlib
import pytest

from core.sentinel.network import (
    DifferentialPrivacyEngine,
    FederatedClient,
    FederatedDomain,
    FederationConsent,
    GlobalModelUpdate,
    GradientPacket,
    NetworkTier,
    SecureAggregator,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sentinel_id() -> str:
    return "sentinel-test-abc123"


@pytest.fixture
def client(sentinel_id) -> FederatedClient:
    return FederatedClient(
        sentinel_id=sentinel_id,
        tier=NetworkTier.FAMILY,
        dp_engine=DifferentialPrivacyEngine(rng_seed=42),
    )


@pytest.fixture
def aggregator() -> SecureAggregator:
    return SecureAggregator(tier=NetworkTier.FAMILY)  # min_participants = 3


def _make_packet(
    domain: FederatedDomain = FederatedDomain.COMMUNICATION_STYLE,
    dim: int = 4,
    sentinel_suffix: str = "a",
) -> GradientPacket:
    sid = f"sentinel-{sentinel_suffix}"
    return GradientPacket(
        domain=domain,
        gradient=[0.1 * (i + 1) for i in range(dim)],
        noise_sigma=0.01,
        participant_hash=hashlib.sha256(sid.encode()).hexdigest(),
    )


# ---------------------------------------------------------------------------
# Gradient extraction
# ---------------------------------------------------------------------------

class TestGradientExtraction:
    def test_extraction_produces_correct_delta(self, client):
        before = [1.0, 2.0, 3.0]
        after  = [1.1, 1.8, 3.5]
        grad   = client.extract_gradient(before, after, FederatedDomain.COMMUNICATION_STYLE)
        assert len(grad) == 3
        assert abs(grad[0] - 0.1) < 1e-9
        assert abs(grad[1] - (-0.2)) < 1e-9
        assert abs(grad[2] - 0.5) < 1e-9

    def test_extraction_raises_on_dimension_mismatch(self, client):
        with pytest.raises(ValueError, match="same length"):
            client.extract_gradient([1.0, 2.0], [1.0], FederatedDomain.COMMUNICATION_STYLE)

    def test_extraction_zero_gradient_on_no_change(self, client):
        weights = [0.5, 0.5, 0.5]
        grad = client.extract_gradient(weights, weights, FederatedDomain.EPOCH_CEREMONY)
        assert all(g == 0.0 for g in grad)


# ---------------------------------------------------------------------------
# Differential privacy
# ---------------------------------------------------------------------------

class TestDifferentialPrivacy:
    def test_noise_is_injected_non_zero(self):
        dp = DifferentialPrivacyEngine(rng_seed=7)
        gradient = [1.0, 1.0, 1.0, 1.0]
        noisy, sigma = dp.inject_noise(gradient, FederatedDomain.COMMUNICATION_STYLE)
        assert noisy != gradient  # noise applied
        assert sigma > 0

    def test_sensitive_domain_has_higher_sigma(self):
        dp = DifferentialPrivacyEngine()
        sigma_non_sensitive = dp.sigma_for(FederatedDomain.COMMUNICATION_STYLE)
        sigma_sensitive     = dp.sigma_for(FederatedDomain.EMOTIONAL_TRIGGERS)
        assert sigma_sensitive > sigma_non_sensitive

    def test_sigma_floor_is_respected(self):
        """User cannot set sigma below the domain floor."""
        dp = DifferentialPrivacyEngine(
            domain_sigma={FederatedDomain.EMOTIONAL_TRIGGERS: 0.0001}  # below floor
        )
        assert dp.sigma_for(FederatedDomain.EMOTIONAL_TRIGGERS) >= 0.05

    def test_noisy_output_has_same_dimension(self):
        dp = DifferentialPrivacyEngine(rng_seed=1)
        gradient = [0.1, 0.2, 0.3, 0.4, 0.5]
        noisy, _ = dp.inject_noise(gradient, FederatedDomain.LANGUAGE_RESONANCE)
        assert len(noisy) == len(gradient)


# ---------------------------------------------------------------------------
# Consent — non-sensitive domains
# ---------------------------------------------------------------------------

class TestConsentNonSensitive:
    def test_non_sensitive_auto_consented_on_first_contribute(self, client):
        gradient = [0.1, 0.2, 0.3]
        packet = client.contribute(gradient, FederatedDomain.COMMUNICATION_STYLE)
        assert packet is not None
        assert isinstance(packet, GradientPacket)

    def test_non_sensitive_opt_out_blocks_contribution(self, client):
        client.opt_out(FederatedDomain.COMMUNICATION_STYLE)
        packet = client.contribute([0.1], FederatedDomain.COMMUNICATION_STYLE)
        assert packet is None

    def test_non_sensitive_opt_in_after_opt_out_restores(self, client):
        client.opt_out(FederatedDomain.COMMUNICATION_STYLE)
        client.opt_in(FederatedDomain.COMMUNICATION_STYLE)
        packet = client.contribute([0.1, 0.2], FederatedDomain.COMMUNICATION_STYLE)
        assert packet is not None


# ---------------------------------------------------------------------------
# Consent — sensitive domains
# ---------------------------------------------------------------------------

class TestConsentSensitive:
    def test_sensitive_blocked_without_explicit_opt_in(self, client):
        packet = client.contribute([0.1, 0.2], FederatedDomain.EMOTIONAL_TRIGGERS)
        assert packet is None

    def test_sensitive_allowed_after_explicit_opt_in(self, client):
        client.opt_in(FederatedDomain.EMOTIONAL_TRIGGERS)
        packet = client.contribute([0.1, 0.2], FederatedDomain.EMOTIONAL_TRIGGERS)
        assert packet is not None

    def test_withdrawal_blocks_previously_consented_sensitive(self, client):
        client.opt_in(FederatedDomain.SAFETY_THREAT_PATTERNS)
        client.withdraw(FederatedDomain.SAFETY_THREAT_PATTERNS)
        packet = client.contribute([0.1], FederatedDomain.SAFETY_THREAT_PATTERNS)
        assert packet is None


# ---------------------------------------------------------------------------
# Full network withdrawal
# ---------------------------------------------------------------------------

class TestWithdrawal:
    def test_withdraw_all_blocks_all_domains(self, client):
        # Opt into everything first
        for domain in FederatedDomain:
            client.opt_in(domain)
        client.withdraw_all()
        for domain in FederatedDomain:
            assert not client.is_consented(domain)

    def test_withdraw_all_logged_in_audit_trail(self, client):
        client.withdraw_all()
        trail = client.consent_audit_trail()
        events = [e["event"] for e in trail]
        assert "withdraw_all" in events


# ---------------------------------------------------------------------------
# Audit trail
# ---------------------------------------------------------------------------

class TestAuditTrail:
    def test_opt_in_appears_in_audit_trail(self, client):
        client.opt_in(FederatedDomain.EMOTIONAL_TRIGGERS)
        trail = client.consent_audit_trail()
        assert any(
            e["event"] == "opt_in" and e["domain"] == FederatedDomain.EMOTIONAL_TRIGGERS.value
            for e in trail
        )

    def test_contribution_log_records_successful_contribution(self, client):
        client.contribute([0.1, 0.2], FederatedDomain.COMMUNICATION_STYLE)
        log = client.contribution_log()
        assert any(e["contributed"] and e["domain"] == FederatedDomain.COMMUNICATION_STYLE.value for e in log)

    def test_contribution_log_records_blocked_contribution(self, client):
        client.contribute([0.1], FederatedDomain.HEALTH_EVENT_PRECURSORS)  # no consent
        log = client.contribution_log()
        assert any(not e["contributed"] and e["reason"] == "no_consent" for e in log)

    def test_audit_entries_have_timestamps(self, client):
        client.opt_in(FederatedDomain.EPOCH_CEREMONY)
        trail = client.consent_audit_trail()
        assert all("timestamp" in e for e in trail)


# ---------------------------------------------------------------------------
# Secure aggregation
# ---------------------------------------------------------------------------

class TestSecureAggregation:
    def test_aggregation_requires_minimum_participants(self, aggregator):
        packets = [_make_packet(sentinel_suffix=str(i)) for i in range(2)]  # need 3
        with pytest.raises(ValueError, match="at least 3 participants"):
            aggregator.aggregate(packets)

    def test_aggregation_succeeds_with_minimum_participants(self, aggregator):
        packets = [_make_packet(sentinel_suffix=str(i)) for i in range(3)]
        update = aggregator.aggregate(packets)
        assert isinstance(update, GlobalModelUpdate)
        assert update.participant_count == 3

    def test_aggregated_gradient_is_mean_of_inputs(self, aggregator):
        packets = [
            GradientPacket(
                domain=FederatedDomain.COMMUNICATION_STYLE,
                gradient=[1.0, 2.0],
                noise_sigma=0.01,
                participant_hash=hashlib.sha256(f"s{i}".encode()).hexdigest(),
            )
            for i in range(3)
        ]
        update = aggregator.aggregate(packets)
        assert abs(update.aggregated_gradient[0] - 1.0) < 1e-9
        assert abs(update.aggregated_gradient[1] - 2.0) < 1e-9

    def test_aggregation_deduplicates_same_participant(self, aggregator):
        # Two packets from same participant + one unique = only 2 unique
        p1 = _make_packet(sentinel_suffix="x")
        p2 = _make_packet(sentinel_suffix="x")  # duplicate
        p3 = _make_packet(sentinel_suffix="y")
        with pytest.raises(ValueError, match="unique participants"):
            aggregator.aggregate([p1, p2, p3])  # only 2 unique

    def test_aggregation_produces_integrity_hash(self, aggregator):
        packets = [_make_packet(sentinel_suffix=str(i)) for i in range(3)]
        update = aggregator.aggregate(packets)
        assert isinstance(update.aggregation_hash, str)
        assert len(update.aggregation_hash) == 64  # SHA-256 hex


# ---------------------------------------------------------------------------
# Global model update adoption
# ---------------------------------------------------------------------------

class TestGlobalUpdateAdoption:
    def test_high_score_update_is_adopted(self, client):
        update = GlobalModelUpdate(
            domain=FederatedDomain.COMMUNICATION_STYLE,
            aggregated_gradient=[0.01, 0.02],
            participant_count=5,
            aggregation_hash="abc",
            ab_eval_score=0.85,
        )
        assert client.receive_update(update) is True

    def test_low_score_update_is_rejected(self, client):
        update = GlobalModelUpdate(
            domain=FederatedDomain.COMMUNICATION_STYLE,
            aggregated_gradient=[0.01, 0.02],
            participant_count=5,
            aggregation_hash="abc",
            ab_eval_score=0.40,
        )
        assert client.receive_update(update) is False

    def test_adoption_logged(self, client):
        update = GlobalModelUpdate(
            domain=FederatedDomain.EPOCH_CEREMONY,
            aggregated_gradient=[0.05],
            participant_count=10,
            aggregation_hash="def",
            ab_eval_score=0.90,
        )
        client.receive_update(update)
        log = client.adoption_log()
        assert len(log) == 1
        assert log[0]["adopted"] is True
        assert log[0]["domain"] == FederatedDomain.EPOCH_CEREMONY.value

    def test_participant_hash_does_not_expose_sentinel_id(self, client):
        """The GradientPacket must never contain the raw sentinel_id."""
        packet = client.contribute([0.1, 0.2], FederatedDomain.COMMUNICATION_STYLE)
        assert packet is not None
        assert client.sentinel_id not in packet.participant_hash
        assert packet.participant_hash == hashlib.sha256(
            client.sentinel_id.encode()
        ).hexdigest()

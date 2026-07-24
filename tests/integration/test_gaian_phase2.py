"""
tests/integration/test_gaian_phase2.py

Phase 2 integration tests for the full GAIAN profile pipeline:
  Spotify session → LCI ingest → GaianProfileManager.update_lci
  → Tauri IPC response shape

All tests use in-memory fakes (no real Spotify API, no disk I/O).
The GaianProfileManager is monkey-patched with a dict-backed store
so these tests run offline and in CI.

Issue: #825
Canon: docs/canon/GAIAN_IDENTITY.md
"""

from __future__ import annotations

import dataclasses
import pytest

from src.gaian.runtimetypes import GAIANProfileModel, LCIHistoryEntry
from src.gaian.profile_manager import GaianProfileManager, ProfileNotFoundError
from src.connectors.spotify_lci_connector import SpotifyLCIConnector
import src.gaian.tauri_ipc as ipc


# ---------------------------------------------------------------------------
# In-memory store fixture
# ---------------------------------------------------------------------------

class InMemoryProfileStore:
    """Dict-backed store used to replace GaianProfileManager in tests."""

    def __init__(self):
        self._store: dict[str, GAIANProfileModel] = {}

    def load_profile(self, architect_id: str) -> GAIANProfileModel:
        if architect_id not in self._store:
            raise ProfileNotFoundError(f"No profile: {architect_id!r}")
        return self._store[architect_id]

    def save_profile(self, profile: GAIANProfileModel) -> None:
        self._store[profile.architect_id] = profile

    def update_lci(
        self,
        profile: GAIANProfileModel,
        new_phi: float,
        session_id: str,
        timestamp=None,
    ) -> GAIANProfileModel:
        return GaianProfileManager().update_lci(profile, new_phi, session_id, timestamp)

    def reset_to_baseline(self, profile: GAIANProfileModel) -> GAIANProfileModel:
        return GaianProfileManager().reset_to_baseline(profile)


@pytest.fixture(autouse=True)
def patch_ipc_manager(monkeypatch):
    """Replace the module-level IPC manager with an in-memory store."""
    store = InMemoryProfileStore()
    monkeypatch.setattr(ipc, "_manager", store)
    return store


@pytest.fixture
def seeded_store(patch_ipc_manager):
    """A store pre-populated with one profile."""
    profile = GAIANProfileModel(
        architect_id="architect-phase2-001",
        name="Nexus",
        slug="nexus",
        lci_baseline=0.5,
    )
    patch_ipc_manager.save_profile(profile)
    return patch_ipc_manager


# ---------------------------------------------------------------------------
# GaianProfileManager — unit stubs (pre-implementation guards)
# ---------------------------------------------------------------------------

class TestProfileManagerStubs:

    def test_load_raises_for_unknown_id(self):
        mgr = GaianProfileManager()
        with pytest.raises(ProfileNotFoundError):
            mgr.load_profile("nonexistent-000")

    def test_save_raises_not_implemented(self):
        mgr = GaianProfileManager()
        profile = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.5
        )
        with pytest.raises(NotImplementedError):
            mgr.save_profile(profile)

    def test_migrate_to_same_version_returns_unchanged(self):
        mgr = GaianProfileManager()
        profile = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.5, profile_version=1
        )
        result = mgr.migrate_profile(profile, target_version=1)
        assert result is profile

    def test_migrate_to_unsupported_version_raises(self):
        mgr = GaianProfileManager()
        profile = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.5
        )
        with pytest.raises(Exception):
            mgr.migrate_profile(profile, target_version=99)

    def test_update_lci_appends_entry(self):
        mgr = GaianProfileManager()
        profile = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.5
        )
        updated = mgr.update_lci(profile, new_phi=0.7, session_id="s1")
        assert len(updated.lci_history) == 1
        assert updated.lci_history[0].phi == pytest.approx(0.7)

    def test_update_lci_increments_total_sessions(self):
        mgr = GaianProfileManager()
        profile = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.5
        )
        updated = mgr.update_lci(profile, new_phi=0.6, session_id="s1")
        assert updated.total_sessions == 1

    def test_update_lci_does_not_mutate_original(self):
        mgr = GaianProfileManager()
        profile = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.5
        )
        mgr.update_lci(profile, new_phi=0.8, session_id="s1")
        assert len(profile.lci_history) == 0

    def test_reset_to_baseline_clears_history(self):
        mgr = GaianProfileManager()
        history = [LCIHistoryEntry(phi=0.7, timestamp="2026-07-24T12:00:00Z", session_id="s1")]
        profile = GAIANProfileModel(
            architect_id="x", name="x", slug="x",
            lci_baseline=0.5, lci_history=history, lci_trend="volatile"
        )
        reset = mgr.reset_to_baseline(profile)
        assert reset.lci_history == []
        assert reset.lci_trend == "stable"

    def test_reset_preserves_baseline(self):
        mgr = GaianProfileManager()
        profile = GAIANProfileModel(
            architect_id="x", name="x", slug="x", lci_baseline=0.72
        )
        reset = mgr.reset_to_baseline(profile)
        assert reset.lci_baseline == pytest.approx(0.72)


# ---------------------------------------------------------------------------
# SpotifyLCIConnector
# ---------------------------------------------------------------------------

class TestSpotifyLCIConnector:

    def test_ingest_valid_session_returns_entry(self):
        conn = SpotifyLCIConnector(baseline=0.5)
        session = {
            "session_id": "sp-001",
            "played_at": "2026-07-24T12:00:00Z",
            "track": {
                "duration_ms": 240000,
                "audio_features": {"valence": 0.8, "energy": 0.7},
            },
            "progress_ms": 240000,
        }
        entry = conn.ingest_session(session)
        assert isinstance(entry, LCIHistoryEntry)
        assert 0.0 <= entry.phi <= 1.0
        assert entry.session_id == "sp-001"

    def test_ingest_malformed_returns_baseline_phi(self):
        conn = SpotifyLCIConnector(baseline=0.5)
        entry = conn.ingest_session({})  # completely empty
        assert entry.phi == pytest.approx(0.5, abs=0.2)  # near baseline

    def test_ingest_never_raises(self):
        conn = SpotifyLCIConnector(baseline=0.5)
        # Pathological input
        try:
            conn.ingest_session({"track": {"audio_features": {"valence": "INVALID"}}})
        except Exception as exc:
            pytest.fail(f"ingest_session raised unexpectedly: {exc}")

    def test_batch_ingest_returns_correct_count(self):
        conn = SpotifyLCIConnector()
        sessions = [{"session_id": f"s{i}"} for i in range(5)]
        entries = conn.batch_ingest(sessions)
        assert len(entries) == 5

    def test_batch_ingest_partial_failure_does_not_abort(self):
        conn = SpotifyLCIConnector()
        sessions = [
            {"session_id": "good", "track": {"audio_features": {"valence": 0.8, "energy": 0.6}}},
            {},  # malformed
            {"session_id": "also-good", "track": {"audio_features": {"valence": 0.4, "energy": 0.3}}},
        ]
        entries = conn.batch_ingest(sessions)
        assert len(entries) == 3

    def test_phi_within_bounds_for_extreme_inputs(self):
        conn = SpotifyLCIConnector()
        # Max everything
        session = {
            "track": {"duration_ms": 1, "audio_features": {"valence": 1.0, "energy": 1.0}},
            "progress_ms": 1,
        }
        entry = conn.ingest_session(session)
        assert 0.0 <= entry.phi <= 1.0


# ---------------------------------------------------------------------------
# Tauri IPC handlers
# ---------------------------------------------------------------------------

class TestTauriIPCHandlers:

    def test_cmd_get_profile_success(self, seeded_store):
        resp = ipc.cmd_get_profile("architect-phase2-001")
        assert resp["ok"] is True
        assert resp["data"]["architect_id"] == "architect-phase2-001"

    def test_cmd_get_profile_not_found(self, patch_ipc_manager):
        resp = ipc.cmd_get_profile("ghost-000")
        assert resp["ok"] is False
        assert "error" in resp

    def test_cmd_update_lci_success(self, seeded_store):
        resp = ipc.cmd_update_lci("architect-phase2-001", phi=0.65, session_id="s1")
        assert resp["ok"] is True
        assert resp["data"]["total_sessions"] == 1

    def test_cmd_update_lci_invalid_phi_returns_error(self, seeded_store):
        resp = ipc.cmd_update_lci("architect-phase2-001", phi=1.5, session_id="s1")
        assert resp["ok"] is False
        assert "phi" in resp["error"]

    def test_cmd_update_lci_unknown_architect(self, patch_ipc_manager):
        resp = ipc.cmd_update_lci("nobody", phi=0.5, session_id="s1")
        assert resp["ok"] is False

    def test_cmd_reset_profile_success(self, seeded_store):
        # First make it volatile
        ipc.cmd_update_lci("architect-phase2-001", phi=0.1, session_id="s1")
        resp = ipc.cmd_reset_profile("architect-phase2-001")
        assert resp["ok"] is True
        assert resp["data"]["lci_trend"] == "stable"

    def test_cmd_reset_profile_not_found(self, patch_ipc_manager):
        resp = ipc.cmd_reset_profile("nobody")
        assert resp["ok"] is False

    def test_ipc_never_exposes_ethical_guardrail_false(self, seeded_store):
        """ADR-FE-006: no IPC path may produce a profile with guardrail=False."""
        resp = ipc.cmd_get_profile("architect-phase2-001")
        assert resp["data"]["constitutional"]["ethical_guardrail_active"] is True


# ---------------------------------------------------------------------------
# Full pipeline: Spotify → LCI → profile update → IPC
# ---------------------------------------------------------------------------

class TestFullPipeline:

    def test_spotify_session_flows_into_profile_via_ipc(self, seeded_store):
        conn = SpotifyLCIConnector(baseline=0.5)
        session = {
            "session_id": "sp-pipeline-01",
            "played_at": "2026-07-24T13:00:00Z",
            "track": {
                "duration_ms": 300000,
                "audio_features": {"valence": 0.75, "energy": 0.65},
            },
            "progress_ms": 300000,
        }
        entry = conn.ingest_session(session)

        resp = ipc.cmd_update_lci(
            "architect-phase2-001",
            phi=entry.phi,
            session_id=entry.session_id,
            timestamp=entry.timestamp,
        )

        assert resp["ok"] is True
        history = resp["data"]["lci_history"]
        assert len(history) == 1
        assert history[0]["session_id"] == "sp-pipeline-01"
        assert abs(history[0]["phi"] - entry.phi) < 1e-4

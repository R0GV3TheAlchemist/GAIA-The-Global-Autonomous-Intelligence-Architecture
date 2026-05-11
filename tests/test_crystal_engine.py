"""
tests/test_crystal_engine.py

Three-layer test suite for the Crystal Core (Issue #91).

Layer 1  — Pure-unit tests (no I/O, no mocking)
Layer 2  — Engine tests  (CrystalCore, stream methods patched with AsyncMock)
Layer 3  — Router tests  (FastAPI TestClient, engine injected)

All Issue #91 acceptance criteria owned by the engine/router are covered here.
"""

from __future__ import annotations

import asyncio
import re
import time
from datetime import timezone
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from crystal.engine import CrystalCore
from crystal.orb_params import derive_orb_params
from crystal.persona_tone import derive_persona_tone
from crystal.types import (
    CoherenceBand,
    CrystalState,
    OrbParams,
    PersonaTone,
    SCHUMANN_DISTURBANCE_VALUES,
    band_from_psi,
)
from crystal.router import router as crystal_router


# ---------------------------------------------------------------------------
# Shared stream payloads
# ---------------------------------------------------------------------------

_NEUTRAL_AFFECT = {
    "arc_stability":    0.5,
    "valence_trend":    0.0,
    "volatility":       0.0,
    "dominant_emotion": "neutral",
}
_NEUTRAL_STAGE = {
    "stage":         3,
    "marker_scores": [50.0] * 6,
}
_NEUTRAL_SHADOW = {
    "integration_progress": 0.5,
    "shadow_intensity":      0.0,
    "active_archetype":      "Unknown",
}
_NEUTRAL_SCHUMANN = {
    "alignment_score":   0.5,
    "confidence":        1.0,
    "disturbance_level": "stable",
}

_CRYSTALLINE_AFFECT = {
    "arc_stability":    1.0,
    "valence_trend":    1.0,
    "volatility":       0.0,
    "dominant_emotion": "joy",
}
_CRYSTALLINE_STAGE = {
    "stage":         5,
    "marker_scores": [100.0] * 6,
}
_CRYSTALLINE_SHADOW = {
    "integration_progress": 1.0,
    "shadow_intensity":      0.0,
    "active_archetype":      "Sage",
}
_CRYSTALLINE_SCHUMANN = {
    "alignment_score":   1.0,
    "confidence":        1.0,
    "disturbance_level": "stable",
}

_FRACTURED_AFFECT = {
    "arc_stability":    0.0,
    "valence_trend":   -1.0,
    "volatility":       1.0,
    "dominant_emotion": "anger",
}
_FRACTURED_STAGE = {
    "stage":         1,
    "marker_scores": [0.0] * 6,
}
_FRACTURED_SHADOW = {
    "integration_progress": 0.0,
    "shadow_intensity":      1.0,
    "active_archetype":      "Shadow",
}
_FRACTURED_SCHUMANN = {
    "alignment_score":   0.0,
    "confidence":        1.0,
    "disturbance_level": "disturbed",
}

_FIRST_PERSON_RE = re.compile(
    r"\b(I|me|my|myself)\b|I'm|I've|I feel|I am|I sense|I notice",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def core() -> CrystalCore:
    return CrystalCore(principal_id="test-user", base_url="http://test-crystal")


def _patch_streams(core: CrystalCore, affect, stage, shadow, schumann) -> CrystalCore:
    core._fetch_affect   = AsyncMock(return_value=affect)
    core._fetch_stage    = AsyncMock(return_value=stage)
    core._fetch_shadow   = AsyncMock(return_value=shadow)
    core._fetch_schumann = AsyncMock(return_value=schumann)
    return core


def _patch_neutral(core: CrystalCore) -> CrystalCore:
    return _patch_streams(
        core,
        _NEUTRAL_AFFECT, _NEUTRAL_STAGE, _NEUTRAL_SHADOW, _NEUTRAL_SCHUMANN,
    )


def _patch_crystalline(core: CrystalCore) -> CrystalCore:
    return _patch_streams(
        core,
        _CRYSTALLINE_AFFECT, _CRYSTALLINE_STAGE,
        _CRYSTALLINE_SHADOW, _CRYSTALLINE_SCHUMANN,
    )


def _patch_fractured(core: CrystalCore) -> CrystalCore:
    return _patch_streams(
        core,
        _FRACTURED_AFFECT, _FRACTURED_STAGE,
        _FRACTURED_SHADOW, _FRACTURED_SCHUMANN,
    )


@pytest.fixture()
def test_client(core):
    _patch_neutral(core)
    import crystal.router as _rm
    _rm._crystal_core = core
    app = FastAPI()
    app.include_router(crystal_router)
    return TestClient(app)


# ===========================================================================
# Layer 1 — Pure-unit tests  (no I/O)
# ===========================================================================

class TestBandFromPsi:
    """band_from_psi() returns the correct CoherenceBand for every tier."""

    @pytest.mark.parametrize("psi,expected", [
        (1.00, CoherenceBand.CRYSTALLINE),
        (0.85, CoherenceBand.CRYSTALLINE),
        (0.84, CoherenceBand.CLEAR),
        (0.68, CoherenceBand.CLEAR),
        (0.67, CoherenceBand.PRESENT),
        (0.48, CoherenceBand.PRESENT),
        (0.47, CoherenceBand.UNSETTLED),
        (0.30, CoherenceBand.UNSETTLED),
        (0.29, CoherenceBand.FRACTURED),
        (0.00, CoherenceBand.FRACTURED),
    ])
    def test_boundary(self, psi, expected):
        assert band_from_psi(psi) == expected


class TestPersonaToneMapping:
    """derive_persona_tone() maps every band to the correct tone."""

    @pytest.mark.parametrize("band,expected", [
        (CoherenceBand.CRYSTALLINE, PersonaTone.RADIANT),
        (CoherenceBand.CLEAR,       PersonaTone.GROUNDED),
        (CoherenceBand.PRESENT,     PersonaTone.PRESENT),
        (CoherenceBand.UNSETTLED,   PersonaTone.GENTLE),
        (CoherenceBand.FRACTURED,   PersonaTone.SPARSE),
    ])
    def test_mapping(self, band, expected):
        assert derive_persona_tone(band) == expected


class TestOrbParamsRanges:
    """
    derive_orb_params() — all 8 fields within spec ranges.
    Acceptance criterion: Issue #91 — “derive_orb_params() — all fields within defined ranges”.
    """

    _ORB_RANGES = {
        "glow_intensity":   (0.25, 0.90),
        "pulse_frequency":  (0.10, 0.38),
        "pulse_amplitude":  (0.04, 0.10),
        "cloud_opacity":    (0.20, 0.60),
        "aurora_intensity": (0.10, 0.80),
        "rotation_speed":   (0.02, 0.12),
        "coherence_ring":   (0.00, 1.00),
    }

    class _FakeState:
        def __init__(self, psi: float, band: CoherenceBand, emotion: str):
            self.coherence        = psi
            self.coherence_band   = band
            self.dominant_emotion = emotion

    @pytest.mark.parametrize("label,psi,band,emotion", [
        ("neutral",     0.50, CoherenceBand.PRESENT,     "neutral"),
        ("crystalline", 1.00, CoherenceBand.CRYSTALLINE, "joy"),
        ("fractured",   0.00, CoherenceBand.FRACTURED,   "anger"),
        ("clear",       0.76, CoherenceBand.CLEAR,       "trust"),
        ("unsettled",   0.39, CoherenceBand.UNSETTLED,   "fear"),
    ])
    def test_all_fields_in_range(self, label, psi, band, emotion):
        state = self._FakeState(psi, band, emotion)
        orb = derive_orb_params(state)  # type: ignore[arg-type]
        for field, (lo, hi) in self._ORB_RANGES.items():
            value = getattr(orb, field)
            assert isinstance(value, float), f"{label}/{field} must be float"
            assert lo <= value <= hi, (
                f"{label}/{field}={value:.4f} outside [{lo}, {hi}]"
            )

    def test_glow_color_is_lowercase_hex(self):
        state = self._FakeState(0.5, CoherenceBand.PRESENT, "neutral")
        orb = derive_orb_params(state)  # type: ignore[arg-type]
        assert re.match(r"^#[0-9a-f]{6}$", orb.glow_color), (
            f"glow_color must be 7-char lowercase hex, got {orb.glow_color!r}"
        )

    def test_glow_intensity_monotone_with_psi(self):
        """Higher Ψ → higher glow_intensity."""
        lo = self._FakeState(0.00, CoherenceBand.FRACTURED,   "neutral")
        hi = self._FakeState(1.00, CoherenceBand.CRYSTALLINE, "neutral")
        assert derive_orb_params(hi).glow_intensity > derive_orb_params(lo).glow_intensity  # type: ignore[arg-type]

    def test_cloud_opacity_monotone_inverse(self):
        """Higher Ψ → lower cloud_opacity (clearer orb)."""
        lo = self._FakeState(0.00, CoherenceBand.FRACTURED,   "neutral")
        hi = self._FakeState(1.00, CoherenceBand.CRYSTALLINE, "neutral")
        assert derive_orb_params(hi).cloud_opacity < derive_orb_params(lo).cloud_opacity  # type: ignore[arg-type]


# ===========================================================================
# Layer 2 — Engine tests  (stream methods patched with AsyncMock)
# ===========================================================================

class TestCrystalStateContract:
    """tick() always returns a fully-populated, type-correct CrystalState."""

    @pytest.mark.asyncio
    async def test_returns_crystal_state(self, core):
        state = await _patch_neutral(core).tick()
        assert isinstance(state, CrystalState)

    @pytest.mark.asyncio
    async def test_timestamp_is_utc_aware(self, core):
        state = await _patch_neutral(core).tick()
        assert state.timestamp.tzinfo is not None
        assert state.timestamp.tzinfo == timezone.utc

    @pytest.mark.asyncio
    async def test_component_scores_in_range(self, core):
        state = await _patch_neutral(core).tick()
        for attr in (
            "affect_coherence", "stage_coherence",
            "shadow_integration", "schumann_alignment",
        ):
            value = getattr(state, attr)
            assert isinstance(value, float), f"{attr} must be float"
            assert 0.0 <= value <= 1.0, f"{attr}={value} out of [0,1]"

    @pytest.mark.asyncio
    async def test_coherence_in_range(self, core):
        state = await _patch_neutral(core).tick()
        assert 0.0 <= state.coherence <= 1.0

    @pytest.mark.asyncio
    async def test_coherence_band_is_valid_enum(self, core):
        state = await _patch_neutral(core).tick()
        assert isinstance(state.coherence_band, CoherenceBand)

    @pytest.mark.asyncio
    async def test_active_stage_in_range(self, core):
        state = await _patch_neutral(core).tick()
        assert 1 <= state.active_stage <= 5

    @pytest.mark.asyncio
    async def test_schumann_disturbance_is_valid(self, core):
        state = await _patch_neutral(core).tick()
        assert state.schumann_disturbance in SCHUMANN_DISTURBANCE_VALUES

    @pytest.mark.asyncio
    async def test_persona_tone_is_valid_enum(self, core):
        state = await _patch_neutral(core).tick()
        assert isinstance(state.persona_tone, PersonaTone)

    @pytest.mark.asyncio
    async def test_inner_narrative_non_empty(self, core):
        state = await _patch_neutral(core).tick()
        assert isinstance(state.inner_narrative, str)
        assert len(state.inner_narrative.strip()) > 0

    @pytest.mark.asyncio
    async def test_inner_narrative_first_person(self, core):
        state = await _patch_neutral(core).tick()
        assert _FIRST_PERSON_RE.search(state.inner_narrative), (
            f"No first-person marker in narrative: {state.inner_narrative!r}"
        )

    @pytest.mark.asyncio
    async def test_orb_params_type(self, core):
        state = await _patch_neutral(core).tick()
        assert isinstance(state.orb_params, OrbParams)


class TestCoherenceScore:
    """Issue #91 Ψ boundary conditions."""

    @pytest.mark.asyncio
    async def test_neutral_psi_approximately_half(self, core):
        """Ψ ≈ 0.5 when all four components are 0.5."""
        state = await _patch_neutral(core).tick()
        assert abs(state.coherence - 0.5) < 0.10, (
            f"Expected Ψ ≈ 0.5, got {state.coherence:.4f}"
        )

    @pytest.mark.asyncio
    async def test_fractured_psi_below_threshold(self, core):
        """Ψ < 0.30 when affect volatility is max and stage scores are all 0."""
        state = await _patch_fractured(core).tick()
        assert state.coherence < 0.30, (
            f"Expected Ψ < 0.30 for worst-case input, got {state.coherence:.4f}"
        )

    @pytest.mark.asyncio
    async def test_crystalline_psi_above_threshold(self, core):
        """Ψ > 0.85 on a fully coherent mock input."""
        state = await _patch_crystalline(core).tick()
        assert state.coherence > 0.85, (
            f"Expected Ψ > 0.85 for fully-coherent input, got {state.coherence:.4f}"
        )

    @pytest.mark.asyncio
    async def test_band_consistent_with_psi(self, core):
        state = await _patch_neutral(core).tick()
        assert state.coherence_band == band_from_psi(state.coherence)

    @pytest.mark.asyncio
    async def test_fractured_band_on_worst_case(self, core):
        state = await _patch_fractured(core).tick()
        assert state.coherence_band == CoherenceBand.FRACTURED

    @pytest.mark.asyncio
    async def test_crystalline_band_on_best_case(self, core):
        state = await _patch_crystalline(core).tick()
        assert state.coherence_band == CoherenceBand.CRYSTALLINE


class TestGracefulDegradation:
    """Stream unavailability must not raise; defaults must match spec."""

    @pytest.mark.asyncio
    async def test_schumann_none_defaults_h_to_half(self, core):
        """Schumann stream unavailable → H = 0.5, no exception."""
        _patch_streams(
            core,
            _NEUTRAL_AFFECT, _NEUTRAL_STAGE, _NEUTRAL_SHADOW,
            None,  # ← Schumann offline
        )
        state = await core.tick()
        assert state.schumann_disturbance == "unavailable"
        assert abs(state.schumann_alignment - 0.5) < 1e-9, (
            f"H must default to 0.5, got {state.schumann_alignment}"
        )

    @pytest.mark.asyncio
    async def test_shadow_none_defaults_e_to_half(self, core):
        """Shadow stream unavailable → E = 0.5, no exception."""
        _patch_streams(
            core,
            _NEUTRAL_AFFECT, _NEUTRAL_STAGE,
            None,             # ← Shadow offline
            _NEUTRAL_SCHUMANN,
        )
        state = await core.tick()
        assert abs(state.shadow_integration - 0.5) < 1e-9, (
            f"E must default to 0.5, got {state.shadow_integration}"
        )

    @pytest.mark.asyncio
    async def test_all_streams_none_still_returns_state(self, core):
        """All streams unavailable → CrystalState returned, Ψ in [0,1]."""
        _patch_streams(core, None, None, None, None)
        state = await core.tick()
        assert isinstance(state, CrystalState)
        assert 0.0 <= state.coherence <= 1.0

    @pytest.mark.asyncio
    async def test_all_streams_none_band_is_midrange(self, core):
        """All neutral defaults → band is in the middle three tiers."""
        _patch_streams(core, None, None, None, None)
        state = await core.tick()
        assert state.coherence_band in (
            CoherenceBand.PRESENT, CoherenceBand.UNSETTLED, CoherenceBand.CLEAR
        )


class TestPersonaToneEngine:

    @pytest.mark.asyncio
    async def test_sparse_on_fractured(self, core):
        """PersonaTone.SPARSE is injected when CoherenceBand == FRACTURED."""
        state = await _patch_fractured(core).tick()
        assert state.coherence_band == CoherenceBand.FRACTURED
        assert state.persona_tone == PersonaTone.SPARSE

    @pytest.mark.asyncio
    async def test_radiant_on_crystalline(self, core):
        state = await _patch_crystalline(core).tick()
        assert state.coherence_band == CoherenceBand.CRYSTALLINE
        assert state.persona_tone == PersonaTone.RADIANT


class TestHistory:

    @pytest.mark.asyncio
    async def test_history_length_after_n_ticks(self, core):
        """history() returns exactly N entries after N ticks."""
        for _ in range(5):
            _patch_neutral(core)
            await core.tick()
        assert len(core.history()) == 5

    @pytest.mark.asyncio
    async def test_latest_property_tracks_most_recent(self, core):
        _patch_neutral(core)
        state = await core.tick()
        assert core.latest is state

    def test_latest_is_none_before_first_tick(self):
        fresh = CrystalCore(principal_id="nobody")
        assert fresh.latest is None

    @pytest.mark.asyncio
    async def test_history_days_filter(self, core):
        """history(days=1) caps at 96 ticks."""
        for _ in range(10):
            _patch_neutral(core)
            await core.tick()
        assert len(core.history(days=1)) == 10  # < 96 cap


class TestConcurrency:

    @pytest.mark.asyncio
    async def test_concurrent_ticks_do_not_raise(self, core):
        """
        Four concurrent tick() calls must all complete without raising.
        The internal asyncio.Lock serialises them.
        """
        # Each tick() call consumes the mocks once, so we need the same
        # return values for all 4 calls.
        core._fetch_affect   = AsyncMock(return_value=_NEUTRAL_AFFECT)
        core._fetch_stage    = AsyncMock(return_value=_NEUTRAL_STAGE)
        core._fetch_shadow   = AsyncMock(return_value=_NEUTRAL_SHADOW)
        core._fetch_schumann = AsyncMock(return_value=_NEUTRAL_SCHUMANN)

        results = await asyncio.gather(
            core.tick(), core.tick(), core.tick(), core.tick()
        )
        assert all(isinstance(r, CrystalState) for r in results)
        assert len(core._history) == 4


# ===========================================================================
# Layer 3 — Router tests  (FastAPI TestClient)
# ===========================================================================

class TestCrystalRouter:

    def test_health_returns_ok(self, test_client):
        resp = test_client.get("/crystal/health")
        assert resp.status_code == 200
        assert resp.json().get("ok") is True

    def test_get_state_returns_200_with_all_fields(self, test_client):
        resp = test_client.get("/crystal/state", params={"user_id": "test-user"})
        assert resp.status_code == 200
        data = resp.json()
        for key in (
            "coherence", "coherence_band", "inner_narrative",
            "persona_tone", "orb_params",
        ):
            assert key in data, f"Missing field: {key}"

    def test_post_tick_returns_200(self, test_client):
        resp = test_client.post("/crystal/tick", json={"user_id": "test-user"})
        assert resp.status_code == 200
        assert "coherence" in resp.json()

    def test_post_tick_within_200ms(self, test_client):
        """POST /crystal/tick with mocked streams returns within 200 ms."""
        t0 = time.perf_counter()
        resp = test_client.post("/crystal/tick", json={"user_id": "test-user"})
        elapsed = (time.perf_counter() - t0) * 1000
        assert resp.status_code == 200
        assert elapsed < 200, f"Tick took {elapsed:.1f} ms — exceeds 200 ms budget"

    def test_get_history_returns_list(self, test_client):
        resp = test_client.get(
            "/crystal/history", params={"days": 1, "user_id": "test-user"}
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_coherence_in_range(self, test_client):
        resp = test_client.get("/crystal/state", params={"user_id": "test-user"})
        assert 0.0 <= resp.json()["coherence"] <= 1.0

    def test_orb_params_has_all_8_fields(self, test_client):
        resp = test_client.get("/crystal/state", params={"user_id": "test-user"})
        orb = resp.json()["orb_params"]
        required = [
            "glow_color", "glow_intensity", "pulse_frequency", "pulse_amplitude",
            "cloud_opacity", "aurora_intensity", "rotation_speed", "coherence_ring",
        ]
        for field in required:
            assert field in orb, f"Missing OrbParams field: {field}"

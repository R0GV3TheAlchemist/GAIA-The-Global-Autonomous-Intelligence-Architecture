"""
tests/numerology/test_route.py
HTTP integration tests for the Numerology API routes.

Uses FastAPI's TestClient (sync) against a minimal app that mounts
only the numerology router with a mocked NumerologyService dep.

This keeps the route tests hermetic: no real DB, no SQLAlchemy engine,
no Alembic migrations required.
"""
from __future__ import annotations

import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes.numerology import get_numerology_service, router
from gaia.numerology.engine import NumerologyEngine
from gaia.numerology.models import NumerologyChart, NumerologyInput

# ---------------------------------------------------------------------------
# Minimal app + mock service
# ---------------------------------------------------------------------------

_engine = NumerologyEngine()
_CHART_ID = uuid.uuid4()
_PROFILE_ID = uuid.uuid4()
_USER_ID = uuid.uuid4()


def _make_mock_orm_chart(
    life_path: int = 1,
    personal_year: int = 7,
) -> MagicMock:
    """Build a MagicMock that looks like a NumerologyChart ORM row."""
    computed = _engine.compute("Nikola Tesla", date(1856, 7, 10))
    raw = computed.as_dict()

    mock = MagicMock()
    mock.id = _CHART_ID
    mock.profile_id = _PROFILE_ID
    mock.life_path = life_path
    mock.expression = computed.expression.reduced_value
    mock.soul_urge = computed.soul_urge.reduced_value
    mock.personality = computed.personality.reduced_value
    mock.birthday = computed.birthday.reduced_value
    mock.personal_year = personal_year
    mock.computed_for_year = 2026
    mock.life_path_is_master = computed.life_path.is_master_number
    mock.expression_is_master = computed.expression.is_master_number
    mock.soul_urge_is_master = computed.soul_urge.is_master_number
    mock.raw_chart = raw
    mock.numbers = []
    mock.profile = MagicMock()
    mock.profile.full_name = "Nikola Tesla"
    mock.profile.birth_date = date(1856, 7, 10)
    mock.profile.system = "pythagorean"
    mock.profile.user_id = _USER_ID
    mock.get_number = MagicMock(return_value=None)
    return mock


def _make_mock_service(orm_chart=None) -> AsyncMock:
    svc = AsyncMock()
    chart = orm_chart or _make_mock_orm_chart()
    svc.get_or_create_chart.return_value = chart
    svc.get_chart_by_id.return_value = chart
    svc.get_charts_for_user.return_value = [chart]
    svc.delete_profile.return_value = True
    return svc


def _build_app(mock_svc=None) -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    if mock_svc:
        app.dependency_overrides[get_numerology_service] = lambda: mock_svc
    return app


# ---------------------------------------------------------------------------
# POST /api/v1/numerology/chart — ephemeral (no user_id)
# ---------------------------------------------------------------------------

class TestPostChartEphemeral:
    def setup_method(self):
        self.app = _build_app()  # no override — uses real engine, no DB
        self.client = TestClient(self.app, raise_server_exceptions=True)

    def test_returns_200(self):
        resp = self.client.post("/api/v1/numerology/chart", json={
            "full_name": "Nikola Tesla",
            "birth_date": "1856-07-10",
        })
        assert resp.status_code == 200

    def test_response_has_life_path(self):
        resp = self.client.post("/api/v1/numerology/chart", json={
            "full_name": "Nikola Tesla",
            "birth_date": "1856-07-10",
        })
        data = resp.json()
        assert "life_path" in data
        assert data["life_path"]["reduced_value"] == 1

    def test_response_has_all_five_core_numbers(self):
        resp = self.client.post("/api/v1/numerology/chart", json={
            "full_name": "Ada Lovelace",
            "birth_date": "1815-12-10",
        })
        data = resp.json()
        for key in ("life_path", "expression", "soul_urge", "personality", "birthday"):
            assert key in data, f"Missing: {key}"

    def test_chart_id_is_null_for_ephemeral(self):
        resp = self.client.post("/api/v1/numerology/chart", json={
            "full_name": "Test User",
            "birth_date": "1990-06-15",
        })
        assert resp.json()["chart_id"] is None

    def test_challenges_list_present(self):
        resp = self.client.post("/api/v1/numerology/chart", json={
            "full_name": "Test User",
            "birth_date": "1990-06-15",
        })
        assert isinstance(resp.json()["challenges"], list)
        assert len(resp.json()["challenges"]) == 4

    def test_future_birth_date_returns_422(self):
        resp = self.client.post("/api/v1/numerology/chart", json={
            "full_name": "Future Person",
            "birth_date": "2099-01-01",
        })
        assert resp.status_code == 422

    def test_empty_name_returns_422(self):
        resp = self.client.post("/api/v1/numerology/chart", json={
            "full_name": "",
            "birth_date": "1990-01-01",
        })
        assert resp.status_code == 422

    def test_unsupported_system_returns_400(self):
        resp = self.client.post("/api/v1/numerology/chart", json={
            "full_name": "Test User",
            "birth_date": "1990-01-01",
            "system": "chaldean",
        })
        assert resp.status_code == 422  # Pydantic validator fires before route


# ---------------------------------------------------------------------------
# POST /api/v1/numerology/chart — persistent (with user_id)
# ---------------------------------------------------------------------------

class TestPostChartPersistent:
    def setup_method(self):
        self.mock_svc = _make_mock_service()
        self.app = _build_app(self.mock_svc)
        self.client = TestClient(self.app, raise_server_exceptions=True)

    def test_returns_200(self):
        resp = self.client.post("/api/v1/numerology/chart", json={
            "full_name": "Nikola Tesla",
            "birth_date": "1856-07-10",
            "user_id": str(_USER_ID),
        })
        assert resp.status_code == 200

    def test_chart_id_is_present(self):
        resp = self.client.post("/api/v1/numerology/chart", json={
            "full_name": "Nikola Tesla",
            "birth_date": "1856-07-10",
            "user_id": str(_USER_ID),
        })
        data = resp.json()
        assert data["chart_id"] == str(_CHART_ID)

    def test_service_get_or_create_called(self):
        self.client.post("/api/v1/numerology/chart", json={
            "full_name": "Nikola Tesla",
            "birth_date": "1856-07-10",
            "user_id": str(_USER_ID),
        })
        self.mock_svc.get_or_create_chart.assert_called_once()


# ---------------------------------------------------------------------------
# GET /api/v1/numerology/chart/{chart_id}
# ---------------------------------------------------------------------------

class TestGetChartById:
    def setup_method(self):
        self.mock_svc = _make_mock_service()
        self.app = _build_app(self.mock_svc)
        self.client = TestClient(self.app, raise_server_exceptions=True)

    def test_returns_200_for_known_id(self):
        resp = self.client.get(f"/api/v1/numerology/chart/{_CHART_ID}")
        assert resp.status_code == 200

    def test_returns_404_for_unknown_id(self):
        self.mock_svc.get_chart_by_id.return_value = None
        resp = self.client.get(f"/api/v1/numerology/chart/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_response_contains_chart_id(self):
        resp = self.client.get(f"/api/v1/numerology/chart/{_CHART_ID}")
        assert resp.json()["chart_id"] == str(_CHART_ID)


# ---------------------------------------------------------------------------
# GET /api/v1/numerology/user/{user_id}
# ---------------------------------------------------------------------------

class TestGetUserCharts:
    def setup_method(self):
        self.mock_svc = _make_mock_service()
        self.app = _build_app(self.mock_svc)
        self.client = TestClient(self.app, raise_server_exceptions=True)

    def test_returns_200(self):
        resp = self.client.get(f"/api/v1/numerology/user/{_USER_ID}")
        assert resp.status_code == 200

    def test_response_has_charts_list(self):
        resp = self.client.get(f"/api/v1/numerology/user/{_USER_ID}")
        data = resp.json()
        assert "charts" in data
        assert isinstance(data["charts"], list)

    def test_empty_list_for_unknown_user(self):
        self.mock_svc.get_charts_for_user.return_value = []
        resp = self.client.get(f"/api/v1/numerology/user/{uuid.uuid4()}")
        assert resp.json()["charts"] == []


# ---------------------------------------------------------------------------
# DELETE /api/v1/numerology/profile/{id}
# ---------------------------------------------------------------------------

class TestDeleteProfile:
    def setup_method(self):
        self.mock_svc = _make_mock_service()
        self.app = _build_app(self.mock_svc)
        self.client = TestClient(self.app, raise_server_exceptions=True)

    def test_soft_delete_returns_200(self):
        resp = self.client.delete(f"/api/v1/numerology/profile/{_PROFILE_ID}")
        assert resp.status_code == 200

    def test_soft_delete_response_payload(self):
        resp = self.client.delete(f"/api/v1/numerology/profile/{_PROFILE_ID}")
        data = resp.json()
        assert data["ok"] is True
        assert data["deletion_type"] == "soft"

    def test_hard_delete_flag(self):
        resp = self.client.delete(
            f"/api/v1/numerology/profile/{_PROFILE_ID}?hard=true"
        )
        data = resp.json()
        assert data["deletion_type"] == "hard"

    def test_returns_404_for_unknown_profile(self):
        self.mock_svc.delete_profile.return_value = False
        resp = self.client.delete(f"/api/v1/numerology/profile/{uuid.uuid4()}")
        assert resp.status_code == 404

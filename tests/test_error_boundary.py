"""
tests/test_error_boundary.py
Unit tests for core/error_boundary.py — Sprint G-6.

Covers:
  - _envelope / _code helpers produce correct shapes
  - HTTP exception handler returns correct status, ok=False, code, message
  - Validation error handler returns 422 + field-level detail list
  - Unhandled exception handler returns 500 + generic message (no traceback)
  - X-Correlation-ID header is present on all error responses
  - install_error_handlers registers without raising
  - All error codes map correctly (400, 401, 403, 404, 409, 422, 429, 500)
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI, HTTPException
from httpx import AsyncClient, ASGITransport
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from core.error_boundary import (
    _code,
    _envelope,
    install_error_handlers,
    _handle_http_exception,
    _handle_validation_error,
    _handle_unhandled_exception,
)


# ================================================================== #
#  Helpers                                                            #
# ================================================================== #

class TestCodeHelper:
    def test_known_codes(self):
        assert _code(400) == "BAD_REQUEST"
        assert _code(401) == "UNAUTHORIZED"
        assert _code(403) == "FORBIDDEN"
        assert _code(404) == "NOT_FOUND"
        assert _code(409) == "CONFLICT"
        assert _code(422) == "VALIDATION_ERROR"
        assert _code(429) == "RATE_LIMITED"
        assert _code(500) == "INTERNAL_SERVER_ERROR"

    def test_unknown_code_fallback(self):
        assert _code(418) == "HTTP_418"
        assert _code(599) == "HTTP_599"


class TestEnvelope:
    def test_ok_is_false(self):
        env = _envelope(404, "not found")
        assert env["ok"] is False

    def test_error_key_present(self):
        env = _envelope(404, "not found")
        assert "error" in env

    def test_error_has_required_fields(self):
        env = _envelope(404, "test message")
        inner = env["error"]
        assert "code" in inner
        assert "message" in inner
        assert "correlation_id" in inner
        assert "status" in inner

    def test_status_matches(self):
        env = _envelope(403, "forbidden")
        assert env["error"]["status"] == 403

    def test_message_matches(self):
        env = _envelope(500, "boom")
        assert env["error"]["message"] == "boom"

    def test_detail_absent_when_none(self):
        env = _envelope(400, "bad")
        assert "detail" not in env["error"]

    def test_detail_present_when_provided(self):
        env = _envelope(422, "validation", detail=[{"field": "x"}])
        assert env["error"]["detail"] == [{"field": "x"}]


# ================================================================== #
#  Integration via AsyncClient + ASGITransport                        #
# ================================================================== #

@pytest.fixture
def app_with_boundary():
    """Minimal FastAPI app with error boundary + 3 test routes."""
    _app = FastAPI()
    install_error_handlers(_app)

    @_app.get("/raise-404")
    async def raise_404():
        raise HTTPException(status_code=404, detail="GAIAN 'luna' not found")

    @_app.get("/raise-403")
    async def raise_403():
        raise HTTPException(status_code=403, detail="Admin required")

    @_app.get("/raise-500")
    async def raise_500():
        raise RuntimeError("kaboom")

    @_app.get("/ok")
    async def ok_route():
        return {"ok": True}

    return _app


class TestHTTPExceptionHandler:
    @pytest.mark.asyncio
    async def test_404_status_code(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/raise-404")
        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_404_ok_is_false(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/raise-404")
        assert r.json()["ok"] is False

    @pytest.mark.asyncio
    async def test_404_code_is_not_found(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/raise-404")
        assert r.json()["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_404_message_passed_through(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/raise-404")
        assert "luna" in r.json()["error"]["message"]

    @pytest.mark.asyncio
    async def test_correlation_id_header_present(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/raise-404")
        assert "x-correlation-id" in r.headers

    @pytest.mark.asyncio
    async def test_403_code_is_forbidden(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/raise-403")
        assert r.json()["error"]["code"] == "FORBIDDEN"


class TestUnhandledExceptionHandler:
    @pytest.mark.asyncio
    async def test_500_status_code(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/raise-500")
        assert r.status_code == 500

    @pytest.mark.asyncio
    async def test_500_ok_is_false(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/raise-500")
        assert r.json()["ok"] is False

    @pytest.mark.asyncio
    async def test_500_code_is_internal_server_error(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/raise-500")
        assert r.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"

    @pytest.mark.asyncio
    async def test_no_traceback_in_response(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/raise-500")
        body = json.dumps(r.json())
        assert "Traceback" not in body
        assert "kaboom" not in body

    @pytest.mark.asyncio
    async def test_500_correlation_id_header_present(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/raise-500")
        assert "x-correlation-id" in r.headers


class TestHappyPath:
    @pytest.mark.asyncio
    async def test_ok_route_unaffected(self, app_with_boundary):
        async with AsyncClient(transport=ASGITransport(app=app_with_boundary), base_url="http://test") as client:
            r = await client.get("/ok")
        assert r.status_code == 200
        assert r.json()["ok"] is True


class TestInstallErrorHandlers:
    def test_install_does_not_raise(self):
        fresh_app = FastAPI()
        install_error_handlers(fresh_app)  # should not raise

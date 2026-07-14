"""
Tests for RepositoryFactory.

Covers:
  1. from_env() returns None when GAIA_DB_DSN is absent
  2. from_env() returns None when GAIA_DB_DSN is empty / whitespace
  3. from_env() delegates to from_dsn() when GAIA_DB_DSN is set
  4. from_dsn() builds Repositories with correct types
  5. from_dsn() passes minconn / maxconn to the pool
  6. close() closes the pool
  7. close() is a no-op when passed None
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from core.persistence.repository_factory import (
    GAIA_DB_DSN_ENV,
    Repositories,
    RepositoryFactory,
)
from core.persistence.postgres_repositories import (
    PostgresMemoryRepository,
    PostgresPool,
    PostgresSearchRepository,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_pool():
    """Return a MagicMock that stands in for PostgresPool."""
    mock = MagicMock(spec=PostgresPool)
    return mock


@pytest.fixture()
def clean_env(monkeypatch):
    """Ensure GAIA_DB_DSN is unset for the duration of a test."""
    monkeypatch.delenv(GAIA_DB_DSN_ENV, raising=False)
    yield


# ---------------------------------------------------------------------------
# 1-2. from_env() with no / empty DSN
# ---------------------------------------------------------------------------

class TestRepositoryFactoryFromEnvNoDSN:
    def test_returns_none_when_env_var_absent(self, clean_env):
        result = RepositoryFactory.from_env()
        assert result is None

    def test_returns_none_when_env_var_empty(self, monkeypatch):
        monkeypatch.setenv(GAIA_DB_DSN_ENV, "")
        result = RepositoryFactory.from_env()
        assert result is None

    def test_returns_none_when_env_var_whitespace(self, monkeypatch):
        monkeypatch.setenv(GAIA_DB_DSN_ENV, "   ")
        result = RepositoryFactory.from_env()
        assert result is None


# ---------------------------------------------------------------------------
# 3-5. from_env() / from_dsn() with DSN set
# ---------------------------------------------------------------------------

class TestRepositoryFactoryFromDSN:
    def test_from_env_delegates_to_from_dsn(self, monkeypatch):
        monkeypatch.setenv(GAIA_DB_DSN_ENV, "postgresql://localhost/gaia_test")
        with patch.object(
            RepositoryFactory,
            "from_dsn",
            return_value=MagicMock(spec=Repositories),
        ) as mock_from_dsn:
            result = RepositoryFactory.from_env(minconn=2, maxconn=5)
        mock_from_dsn.assert_called_once_with(
            "postgresql://localhost/gaia_test", minconn=2, maxconn=5
        )
        assert result is not None

    def test_from_dsn_returns_repositories_instance(self, monkeypatch):
        mock_pool = _make_mock_pool()
        with patch(
            "core.persistence.repository_factory.PostgresPool",
            return_value=mock_pool,
        ):
            repos = RepositoryFactory.from_dsn("postgresql://localhost/test")

        assert isinstance(repos, Repositories)
        assert isinstance(repos.memory, PostgresMemoryRepository)
        assert isinstance(repos.search, PostgresSearchRepository)
        assert repos.pool is mock_pool

    def test_from_dsn_passes_pool_params(self, monkeypatch):
        mock_pool = _make_mock_pool()
        with patch(
            "core.persistence.repository_factory.PostgresPool",
            return_value=mock_pool,
        ) as MockPool:
            RepositoryFactory.from_dsn(
                "postgresql://localhost/test", minconn=3, maxconn=20
            )
        MockPool.assert_called_once_with(
            dsn="postgresql://localhost/test", minconn=3, maxconn=20
        )

    def test_repositories_dataclass_is_frozen(self, monkeypatch):
        mock_pool = _make_mock_pool()
        with patch(
            "core.persistence.repository_factory.PostgresPool",
            return_value=mock_pool,
        ):
            repos = RepositoryFactory.from_dsn("postgresql://localhost/test")

        with pytest.raises((AttributeError, TypeError)):
            repos.memory = None  # type: ignore[misc]  # frozen dataclass


# ---------------------------------------------------------------------------
# 6-7. close()
# ---------------------------------------------------------------------------

class TestRepositoryFactoryClose:
    def test_close_calls_pool_close(self, monkeypatch):
        mock_pool = _make_mock_pool()
        with patch(
            "core.persistence.repository_factory.PostgresPool",
            return_value=mock_pool,
        ):
            repos = RepositoryFactory.from_dsn("postgresql://localhost/test")

        RepositoryFactory.close(repos)
        mock_pool.close.assert_called_once()

    def test_close_is_noop_with_none(self):
        # Should not raise
        RepositoryFactory.close(None)

    def test_close_idempotent_to_caller(self, monkeypatch):
        """close() twice should not raise even if the pool already closed."""
        mock_pool = _make_mock_pool()
        with patch(
            "core.persistence.repository_factory.PostgresPool",
            return_value=mock_pool,
        ):
            repos = RepositoryFactory.from_dsn("postgresql://localhost/test")

        RepositoryFactory.close(repos)
        RepositoryFactory.close(repos)  # second call — should not raise
        assert mock_pool.close.call_count == 2

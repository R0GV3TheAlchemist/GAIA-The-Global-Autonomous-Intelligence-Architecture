"""
Tests for the Postgres integration wiring in PersistenceManager.

Covers:
  1. PersistenceManager without repos: postgres_enabled is False,
     memory_repo and search_repo are None, all existing behaviour unchanged.
  2. PersistenceManager with repos: postgres_enabled is True,
     memory_repo and search_repo delegate to the injected Repositories.
  3. stats() includes postgres_enabled key in both modes.
  4. PersistenceManager accepts repos=None explicitly (same as default).
  5. __init__.py public API: all expected symbols importable from package root.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from core.persistence.manager import PersistenceManager
from core.persistence.repository_factory import Repositories, RepositoryFactory
from core.persistence.postgres_repositories import (
    PostgresMemoryRepository,
    PostgresPool,
    PostgresSearchRepository,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_repos() -> Repositories:
    """Build a Repositories with fully mocked internals."""
    pool   = MagicMock(spec=PostgresPool)
    memory = MagicMock(spec=PostgresMemoryRepository)
    search = MagicMock(spec=PostgresSearchRepository)
    return Repositories(memory=memory, search=search, pool=pool)


# ---------------------------------------------------------------------------
# 1. PersistenceManager without repos
# ---------------------------------------------------------------------------

class TestManagerWithoutRepos:
    def test_postgres_enabled_is_false(self, tmp_path):
        pm = PersistenceManager(tmp_path)
        assert pm.postgres_enabled is False

    def test_memory_repo_is_none(self, tmp_path):
        pm = PersistenceManager(tmp_path)
        assert pm.memory_repo is None

    def test_search_repo_is_none(self, tmp_path):
        pm = PersistenceManager(tmp_path)
        assert pm.search_repo is None

    def test_repos_property_is_none(self, tmp_path):
        pm = PersistenceManager(tmp_path)
        assert pm.repos is None

    def test_file_stores_still_constructed(self, tmp_path):
        pm = PersistenceManager(tmp_path)
        assert pm.registry_persistence is not None
        assert pm.session_persistence  is not None

    def test_explicit_repos_none_same_as_default(self, tmp_path):
        pm = PersistenceManager(tmp_path, repos=None)
        assert pm.postgres_enabled is False


# ---------------------------------------------------------------------------
# 2. PersistenceManager with repos
# ---------------------------------------------------------------------------

class TestManagerWithRepos:
    def test_postgres_enabled_is_true(self, tmp_path):
        pm = PersistenceManager(tmp_path, repos=_make_repos())
        assert pm.postgres_enabled is True

    def test_memory_repo_returns_injected_instance(self, tmp_path):
        repos = _make_repos()
        pm = PersistenceManager(tmp_path, repos=repos)
        assert pm.memory_repo is repos.memory

    def test_search_repo_returns_injected_instance(self, tmp_path):
        repos = _make_repos()
        pm = PersistenceManager(tmp_path, repos=repos)
        assert pm.search_repo is repos.search

    def test_repos_property_returns_full_container(self, tmp_path):
        repos = _make_repos()
        pm = PersistenceManager(tmp_path, repos=repos)
        assert pm.repos is repos

    def test_file_stores_still_constructed_alongside_repos(self, tmp_path):
        pm = PersistenceManager(tmp_path, repos=_make_repos())
        assert pm.registry_persistence is not None
        assert pm.session_persistence  is not None

    def test_memory_for_still_works_with_repos(self, tmp_path):
        """memory_for() (file-based) should still function when repos active."""
        pm = PersistenceManager(tmp_path, repos=_make_repos())
        store = pm.memory_for("gaian-001")
        assert store is not None
        # Second call returns same cached instance
        assert pm.memory_for("gaian-001") is store


# ---------------------------------------------------------------------------
# 3. stats() includes postgres_enabled
# ---------------------------------------------------------------------------

class TestManagerStats:
    def test_stats_postgres_enabled_false_without_repos(self, tmp_path):
        pm = PersistenceManager(tmp_path)
        assert pm.stats()["postgres_enabled"] is False

    def test_stats_postgres_enabled_true_with_repos(self, tmp_path):
        pm = PersistenceManager(tmp_path, repos=_make_repos())
        assert pm.stats()["postgres_enabled"] is True

    def test_stats_contains_expected_keys(self, tmp_path):
        pm = PersistenceManager(tmp_path)
        keys = pm.stats().keys()
        for expected in (
            "root", "postgres_enabled", "gaian_count",
            "boot_count", "fragment_counts", "gaia_fragments",
        ):
            assert expected in keys, f"Missing stats key: {expected}"


# ---------------------------------------------------------------------------
# 4. Factory-to-manager wiring (integration)
# ---------------------------------------------------------------------------

class TestFactoryToManagerWiring:
    def test_from_env_none_wires_to_manager_cleanly(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GAIA_DB_DSN", raising=False)
        repos = RepositoryFactory.from_env()
        pm = PersistenceManager(tmp_path, repos=repos)
        assert pm.postgres_enabled is False

    def test_close_noop_when_manager_has_no_repos(self, tmp_path):
        pm = PersistenceManager(tmp_path)
        RepositoryFactory.close(pm.repos)  # must not raise

    def test_close_calls_pool_when_repos_present(self, tmp_path):
        repos = _make_repos()
        pm = PersistenceManager(tmp_path, repos=repos)
        RepositoryFactory.close(pm.repos)
        repos.pool.close.assert_called_once()


# ---------------------------------------------------------------------------
# 5. Package-level __init__.py public API
# ---------------------------------------------------------------------------

class TestPersistencePackageExports:
    def test_persistence_manager_importable(self):
        from core.persistence import PersistenceManager
        assert PersistenceManager is not None

    def test_repository_factory_importable(self):
        from core.persistence import RepositoryFactory
        assert RepositoryFactory is not None

    def test_repositories_importable(self):
        from core.persistence import Repositories
        assert Repositories is not None

    def test_postgres_pool_importable(self):
        from core.persistence import PostgresPool
        assert PostgresPool is not None

    def test_postgres_memory_repo_importable(self):
        from core.persistence import PostgresMemoryRepository
        assert PostgresMemoryRepository is not None

    def test_postgres_search_repo_importable(self):
        from core.persistence import PostgresSearchRepository
        assert PostgresSearchRepository is not None

    def test_all_exports_in_dunder_all(self):
        import core.persistence as pkg
        for name in [
            "PersistenceManager", "RepositoryFactory", "Repositories",
            "PostgresPool", "PostgresMemoryRepository", "PostgresSearchRepository",
            "PersistenceStore", "MemoryPersistence", "IdentityPersistence",
            "RegistryPersistence", "SessionPersistence",
        ]:
            assert name in pkg.__all__, f"{name!r} missing from __all__"

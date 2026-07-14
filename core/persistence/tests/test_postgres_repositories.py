"""
Tests for PostgresMemoryRepository and PostgresSearchRepository.

Covers:
  1. PostgresPool context manager: commit on success, rollback on error
  2. PostgresMemoryRepository: create, get, update, delete, list
  3. PostgresSearchRepository: save, get_history, delete_history
  4. _row_to_memory / _row_to_search_result static converters

All tests are fully offline — psycopg2 is patched at the connection-pool
level so no real Postgres instance is required.
"""
from __future__ import annotations

import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch, call

import pytest

from core.persistence.postgres_repositories import (
    PostgresMemoryRepository,
    PostgresPool,
    PostgresSearchRepository,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pool(fetchone=None, fetchall=None, rowcount=1):
    """Build a PostgresPool whose internal psycopg2 pool is fully mocked.

    Returns (pool, mock_conn, mock_cur) for assertion convenience.
    """
    mock_cur = MagicMock()
    mock_cur.__enter__ = lambda s: mock_cur
    mock_cur.__exit__ = MagicMock(return_value=False)
    mock_cur.fetchone.return_value = fetchone
    mock_cur.fetchall.return_value = fetchall or []
    mock_cur.rowcount = rowcount

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cur

    mock_pool = MagicMock()
    mock_pool.getconn.return_value = mock_conn

    pool = PostgresPool.__new__(PostgresPool)
    pool._pool = mock_pool
    return pool, mock_conn, mock_cur


NOW = datetime(2026, 7, 14, 12, 0, 0, tzinfo=UTC)


def _memory_row(memory_id="mem-001", user_id="user-A") -> dict[str, Any]:
    return {
        "id": memory_id,
        "user_id": user_id,
        "content": "I remember the stars.",
        "memory_type": "episodic",
        "metadata": {"mood": "calm"},
        "tags": ["stars", "night"],
        "confidence": 0.95,
        "source": "session",
        "status": "active",
        "created_at": NOW,
        "updated_at": NOW,
    }


def _search_row(result_id="sr-001", user_id="user-A") -> dict[str, Any]:
    return {
        "id": result_id,
        "user_id": user_id,
        "query": "stars night",
        "results": [{"memory_id": "m1", "score": 0.9}],
        "total_found": 1,
        "search_time_ms": 42,
        "created_at": NOW,
    }


# ---------------------------------------------------------------------------
# Fake models (stand-ins for core.persistence.models.*)
# ---------------------------------------------------------------------------

class FakeMemoryType:
    def __init__(self, value): self.value = value
    @classmethod
    def __call__(cls, v): return cls(v)

class FakeMemoryStatus:
    def __init__(self, value): self.value = value
    @classmethod
    def __call__(cls, v): return cls(v)


def _patch_models(monkeypatch):
    """Patch MemoryType / MemoryStatus inside the module under test."""
    import core.persistence.postgres_repositories as mod
    monkeypatch.setattr(mod, "MemoryType",   FakeMemoryType,   raising=False)
    monkeypatch.setattr(mod, "MemoryStatus", FakeMemoryStatus, raising=False)


class FakeMemory:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)
        self.id = kw.get("id", None)
        self.user_id = kw.get("user_id", "user-A")
        self.content = kw.get("content", "default content")
        self.memory_type = FakeMemoryType(kw.get("memory_type", "episodic"))
        self.metadata = kw.get("metadata", {})
        self.tags = kw.get("tags", [])
        self.confidence = kw.get("confidence", 0.8)
        self.source = kw.get("source", "test")
        self.status = FakeMemoryStatus(kw.get("status", "active"))
        self.created_at = kw.get("created_at", None)
        self.updated_at = kw.get("updated_at", None)


class FakeSearchResult:
    def __init__(self, **kw):
        self.id = kw.get("id", None)
        self.user_id = kw.get("user_id", "user-A")
        self.query = kw.get("query", "test query")
        self.results = kw.get("results", [])
        self.total_found = kw.get("total_found", 0)
        self.search_time_ms = kw.get("search_time_ms", 10)
        self.created_at = kw.get("created_at", None)


# ---------------------------------------------------------------------------
# 1. PostgresPool
# ---------------------------------------------------------------------------

class TestPostgresPool:
    def test_commit_on_success(self):
        pool, mock_conn, _ = _make_pool()
        with pool.connection() as conn:
            assert conn is mock_conn
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

    def test_rollback_on_exception(self):
        pool, mock_conn, _ = _make_pool()
        with pytest.raises(ValueError):
            with pool.connection():
                raise ValueError("boom")
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()

    def test_connection_returned_to_pool_after_success(self):
        pool, mock_conn, _ = _make_pool()
        with pool.connection():
            pass
        pool._pool.putconn.assert_called_once_with(mock_conn)

    def test_connection_returned_to_pool_after_error(self):
        pool, mock_conn, _ = _make_pool()
        with pytest.raises(RuntimeError):
            with pool.connection():
                raise RuntimeError("fail")
        pool._pool.putconn.assert_called_once_with(mock_conn)

    def test_close_calls_closeall(self):
        pool, _, _ = _make_pool()
        pool.close()
        pool._pool.closeall.assert_called_once()


# ---------------------------------------------------------------------------
# 2. PostgresMemoryRepository
# ---------------------------------------------------------------------------

class TestPostgresMemoryRepositoryCreate:
    def test_create_returns_memory_with_row_data(self, monkeypatch):
        row = _memory_row()
        pool, _, cur = _make_pool(fetchone=row)
        _patch_models(monkeypatch)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "Memory", FakeMemory, raising=False)

        repo = PostgresMemoryRepository(pool)
        mem = FakeMemory(user_id="user-A", content="I remember the stars.")
        result = repo.create_memory(mem)

        assert result.content == "I remember the stars."
        assert cur.execute.called

    def test_create_uses_returning_clause(self, monkeypatch):
        row = _memory_row()
        pool, _, cur = _make_pool(fetchone=row)
        _patch_models(monkeypatch)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "Memory", FakeMemory, raising=False)

        repo = PostgresMemoryRepository(pool)
        repo.create_memory(FakeMemory())

        sql = cur.execute.call_args[0][0]
        assert "RETURNING" in sql.upper()


class TestPostgresMemoryRepositoryGet:
    def test_get_returns_memory_when_found(self, monkeypatch):
        row = _memory_row(memory_id="mem-001")
        pool, _, cur = _make_pool(fetchone=row)
        _patch_models(monkeypatch)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "Memory", FakeMemory, raising=False)

        repo = PostgresMemoryRepository(pool)
        result = repo.get_memory("mem-001")

        assert result is not None
        assert result.content == "I remember the stars."

    def test_get_returns_none_when_not_found(self, monkeypatch):
        pool, _, cur = _make_pool(fetchone=None)
        _patch_models(monkeypatch)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "Memory", FakeMemory, raising=False)

        repo = PostgresMemoryRepository(pool)
        result = repo.get_memory("does-not-exist")
        assert result is None


class TestPostgresMemoryRepositoryUpdate:
    def test_update_returns_updated_memory(self, monkeypatch):
        row = _memory_row(memory_id="mem-001")
        pool, _, cur = _make_pool(fetchone=row)
        _patch_models(monkeypatch)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "Memory", FakeMemory, raising=False)

        repo = PostgresMemoryRepository(pool)
        mem = FakeMemory(id="mem-001", content="updated")
        result = repo.update_memory(mem)
        assert result.content == "I remember the stars."  # from RETURNING row

    def test_update_raises_if_no_id(self, monkeypatch):
        pool, _, _ = _make_pool()
        repo = PostgresMemoryRepository(pool)
        mem = FakeMemory(id=None)
        with pytest.raises(ValueError, match="memory.id"):
            repo.update_memory(mem)

    def test_update_raises_key_error_when_not_found(self, monkeypatch):
        pool, _, cur = _make_pool(fetchone=None)
        _patch_models(monkeypatch)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "Memory", FakeMemory, raising=False)

        repo = PostgresMemoryRepository(pool)
        mem = FakeMemory(id="ghost")
        with pytest.raises(KeyError):
            repo.update_memory(mem)


class TestPostgresMemoryRepositoryDelete:
    def test_delete_returns_true_when_row_deleted(self, monkeypatch):
        pool, _, cur = _make_pool(rowcount=1)
        repo = PostgresMemoryRepository(pool)
        assert repo.delete_memory("mem-001") is True

    def test_delete_returns_false_when_not_found(self, monkeypatch):
        pool, _, cur = _make_pool(rowcount=0)
        repo = PostgresMemoryRepository(pool)
        assert repo.delete_memory("ghost") is False


class TestPostgresMemoryRepositoryList:
    def test_list_returns_all_rows(self, monkeypatch):
        rows = [_memory_row("m1"), _memory_row("m2")]
        pool, _, cur = _make_pool(fetchall=rows)
        _patch_models(monkeypatch)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "Memory", FakeMemory, raising=False)

        repo = PostgresMemoryRepository(pool)
        results = repo.list_memories(user_id="user-A")
        assert len(results) == 2

    def test_list_adds_tag_filter_clause(self, monkeypatch):
        pool, _, cur = _make_pool(fetchall=[])
        _patch_models(monkeypatch)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "Memory", FakeMemory, raising=False)

        repo = PostgresMemoryRepository(pool)
        repo.list_memories(user_id="user-A", tags=["stars"])

        sql = cur.execute.call_args[0][0]
        assert "@>" in sql  # array containment operator

    def test_list_adds_type_filter_clause(self, monkeypatch):
        pool, _, cur = _make_pool(fetchall=[])
        _patch_models(monkeypatch)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "Memory", FakeMemory, raising=False)

        repo = PostgresMemoryRepository(pool)
        repo.list_memories(user_id="user-A", memory_type=FakeMemoryType("episodic"))

        sql = cur.execute.call_args[0][0]
        assert "memory_type" in sql


# ---------------------------------------------------------------------------
# 3. PostgresSearchRepository
# ---------------------------------------------------------------------------

class TestPostgresSearchRepository:
    def test_save_returns_result_with_row_data(self, monkeypatch):
        row = _search_row()
        pool, _, cur = _make_pool(fetchone=row)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "SearchResult", FakeSearchResult, raising=False)

        repo = PostgresSearchRepository(pool)
        result = repo.save_search_result(FakeSearchResult(query="stars night"))
        assert result.query == "stars night"

    def test_save_uses_returning_clause(self, monkeypatch):
        row = _search_row()
        pool, _, cur = _make_pool(fetchone=row)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "SearchResult", FakeSearchResult, raising=False)

        repo = PostgresSearchRepository(pool)
        repo.save_search_result(FakeSearchResult())

        sql = cur.execute.call_args[0][0]
        assert "RETURNING" in sql.upper()

    def test_get_history_returns_list(self, monkeypatch):
        rows = [_search_row("sr-1"), _search_row("sr-2")]
        pool, _, cur = _make_pool(fetchall=rows)

        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "SearchResult", FakeSearchResult, raising=False)

        repo = PostgresSearchRepository(pool)
        results = repo.get_search_history(user_id="user-A")
        assert len(results) == 2

    def test_delete_history_returns_count(self, monkeypatch):
        pool, _, cur = _make_pool(rowcount=7)
        repo = PostgresSearchRepository(pool)
        deleted = repo.delete_search_history("user-A")
        assert deleted == 7

    def test_delete_history_issues_correct_query(self, monkeypatch):
        pool, _, cur = _make_pool(rowcount=0)
        repo = PostgresSearchRepository(pool)
        repo.delete_search_history("user-A")
        sql = cur.execute.call_args[0][0]
        assert "search_results" in sql
        assert "user_id" in sql


# ---------------------------------------------------------------------------
# 4. Static row converters
# ---------------------------------------------------------------------------

class TestRowConverters:
    def test_row_to_memory_maps_all_fields(self, monkeypatch):
        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "MemoryType",   FakeMemoryType,   raising=False)
        monkeypatch.setattr(mod, "MemoryStatus", FakeMemoryStatus, raising=False)
        monkeypatch.setattr(mod, "Memory",       FakeMemory,       raising=False)

        row = _memory_row("m1", "u1")
        result = PostgresMemoryRepository._row_to_memory(row)

        assert result.id       == "m1"
        assert result.user_id  == "u1"
        assert result.content  == "I remember the stars."
        assert result.confidence == 0.95
        assert "stars" in result.tags

    def test_row_to_search_result_maps_all_fields(self, monkeypatch):
        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "SearchResult", FakeSearchResult, raising=False)

        row = _search_row("sr-1", "u1")
        result = PostgresSearchRepository._row_to_search_result(row)

        assert result.id            == "sr-1"
        assert result.user_id       == "u1"
        assert result.query         == "stars night"
        assert result.total_found   == 1
        assert result.search_time_ms == 42

    def test_row_to_memory_defaults_empty_metadata(self, monkeypatch):
        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "MemoryType",   FakeMemoryType,   raising=False)
        monkeypatch.setattr(mod, "MemoryStatus", FakeMemoryStatus, raising=False)
        monkeypatch.setattr(mod, "Memory",       FakeMemory,       raising=False)

        row = _memory_row()
        row["metadata"] = None
        row["tags"] = None
        result = PostgresMemoryRepository._row_to_memory(row)
        assert result.metadata == {}
        assert result.tags == []

    def test_row_to_search_result_defaults_empty_results(self, monkeypatch):
        import core.persistence.postgres_repositories as mod
        monkeypatch.setattr(mod, "SearchResult", FakeSearchResult, raising=False)

        row = _search_row()
        row["results"] = None
        result = PostgresSearchRepository._row_to_search_result(row)
        assert result.results == []

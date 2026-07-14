"""Abstract repository interfaces for the GAIA OS persistence layer.

Every storage backend (Postgres, SQLite, in-memory) must implement these
interfaces. Callers depend only on the abstractions here, never on a
specific implementation, keeping the core free of infrastructure concerns.

C17 / C23 persistence contract.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from .models import Memory, MemoryStatus, MemoryType, SearchResult


# ---------------------------------------------------------------------------
# Memory repository
# ---------------------------------------------------------------------------

class MemoryRepository(ABC):
    """CRUD interface for :class:`Memory` records."""

    @abstractmethod
    def create_memory(self, memory: Memory) -> Memory:
        """Persist a new memory and return it with ``id`` and timestamps set."""

    @abstractmethod
    def get_memory(self, memory_id: str) -> Memory | None:
        """Return the memory with the given id, or ``None`` if not found."""

    @abstractmethod
    def update_memory(self, memory: Memory) -> Memory:
        """Overwrite an existing memory record. Raises ``KeyError`` if missing."""

    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """Hard-delete a memory. Returns ``True`` if a row was removed."""

    @abstractmethod
    def list_memories(
        self,
        user_id: str,
        memory_type: MemoryType | None = None,
        status: MemoryStatus | None = None,
        tags: Sequence[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Memory]:
        """Return memories for *user_id*, with optional filters."""


# ---------------------------------------------------------------------------
# Search-history repository
# ---------------------------------------------------------------------------

class SearchRepository(ABC):
    """Interface for recording and retrieving search interactions."""

    @abstractmethod
    def save_search_result(self, result: SearchResult) -> SearchResult:
        """Persist a search result record and return it with ``id`` set."""

    @abstractmethod
    def get_search_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SearchResult]:
        """Return the most-recent search records for *user_id*."""

    @abstractmethod
    def delete_search_history(self, user_id: str) -> int:
        """Delete all search history for *user_id*. Returns count removed."""


# ---------------------------------------------------------------------------
# In-memory fallback implementations (no external deps, used as defaults)
# ---------------------------------------------------------------------------

class InMemoryMemoryRepository(MemoryRepository):
    """Ephemeral in-process implementation — suitable for tests and dev."""

    def __init__(self) -> None:
        self._store: dict[str, Memory] = {}

    def create_memory(self, memory: Memory) -> Memory:
        import uuid
        from datetime import UTC, datetime
        now = datetime.now(UTC)
        memory.id = memory.id or str(uuid.uuid4())
        memory.created_at = memory.created_at or now
        memory.updated_at = memory.updated_at or now
        self._store[memory.id] = memory
        return memory

    def get_memory(self, memory_id: str) -> Memory | None:
        return self._store.get(memory_id)

    def update_memory(self, memory: Memory) -> Memory:
        from datetime import UTC, datetime
        if not memory.id or memory.id not in self._store:
            raise KeyError(f"memory not found: {memory.id}")
        memory.updated_at = datetime.now(UTC)
        self._store[memory.id] = memory
        return memory

    def delete_memory(self, memory_id: str) -> bool:
        return self._store.pop(memory_id, None) is not None

    def list_memories(
        self,
        user_id: str,
        memory_type: MemoryType | None = None,
        status: MemoryStatus | None = None,
        tags: Sequence[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Memory]:
        results = [
            m for m in self._store.values()
            if m.user_id == user_id
            and (memory_type is None or m.memory_type == memory_type)
            and (status is None or m.status == status)
            and (tags is None or all(t in m.tags for t in tags))
        ]
        results.sort(key=lambda m: m.created_at or 0, reverse=True)
        return results[offset: offset + limit]


class InMemorySearchRepository(SearchRepository):
    """Ephemeral in-process implementation — suitable for tests and dev."""

    def __init__(self) -> None:
        self._store: list[SearchResult] = []

    def save_search_result(self, result: SearchResult) -> SearchResult:
        import uuid
        from datetime import UTC, datetime
        result.id = result.id or str(uuid.uuid4())
        result.created_at = result.created_at or datetime.now(UTC)
        self._store.append(result)
        return result

    def get_search_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SearchResult]:
        results = [r for r in self._store if r.user_id == user_id]
        results.sort(key=lambda r: r.created_at or 0, reverse=True)
        return results[offset: offset + limit]

    def delete_search_history(self, user_id: str) -> int:
        before = len(self._store)
        self._store = [r for r in self._store if r.user_id != user_id]
        return before - len(self._store)


__all__ = [
    "MemoryRepository",
    "SearchRepository",
    "InMemoryMemoryRepository",
    "InMemorySearchRepository",
]

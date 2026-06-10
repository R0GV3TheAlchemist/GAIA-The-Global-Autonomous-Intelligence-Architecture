"""
core/storage
============
Pluggable persistence layer for GAIA-OS.

Public API
----------
    from core.storage import StorageBackend, SQLiteBackend, get_backend

    # Get the configured backend (reads GAIA_STORAGE_BACKEND env var)
    backend = get_backend()

    # Or instantiate directly:
    backend = SQLiteBackend(db_path="~/.gaia/state.db")

    # All operations are async:
    await backend.put("key", b"value")
    value = await backend.get("key")
    rows  = await backend.query(prefix="mesh:")
    await backend.delete("key")

Canon Ref:
    C04  — Sovereign privacy: Gaian memories encrypted at rest
    C47  — Sovereign Matrix Code: data portability

Issue: #281 — Distributed State Store
"""

from .backend import (
    StorageBackend,
    StorageError,
    StorageKeyError,
    StorageWriteError,
    SovereignStorageBackend,
)
from .sqlite_backend import SQLiteBackend
from .memory_backend import MemoryBackend
from .factory import get_backend, configure_backend

__all__ = [
    # Protocol
    "StorageBackend",
    # Errors
    "StorageError",
    "StorageKeyError",
    "StorageWriteError",
    # Backends
    "SQLiteBackend",
    "MemoryBackend",
    # Sovereign wrapper
    "SovereignStorageBackend",
    # Factory
    "get_backend",
    "configure_backend",
]

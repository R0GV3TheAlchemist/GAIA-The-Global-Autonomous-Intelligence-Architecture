"""
core/storage/factory.py
=======================
get_backend() — Factory that returns the configured StorageBackend.

Configuration is read from the environment variable GAIA_STORAGE_BACKEND.
The default is "sqlite" which preserves all existing behaviour.

Environment variable
--------------------
    GAIA_STORAGE_BACKEND=sqlite          (default)
    GAIA_STORAGE_BACKEND=memory          (tests / ephemeral nodes)
    GAIA_STORAGE_BACKEND=cockroachdb     (Phase 2 — not yet implemented)
    GAIA_STORAGE_BACKEND=scylladb        (Phase 2 — not yet implemented)
    GAIA_STORAGE_BACKEND=ipfs            (Phase 2 / 3 — not yet implemented)

Additional config
-----------------
    GAIA_STORAGE_PATH     Path for SQLite db (default: ~/.gaia/storage.db)
    GAIA_STORAGE_DSN      Connection string for remote backends (Phase 2)

Phase 2 backend stubs
---------------------
When GAIA_STORAGE_BACKEND is set to a Phase 2 value, get_backend() raises
a clear NotImplementedError explaining how to implement the adapter.
This keeps the factory as the single integration point — swapping to
CockroachDB in Phase 2 requires only:
  1. pip install asyncpg
  2. Implement CockroachDBBackend in core/storage/cockroachdb_backend.py
  3. Uncomment the import in this file

Phase 3: Store-and-forward adapter for interplanetary links wraps any
existing backend.  Writes queue locally and flush when the link is up.

Issue: #281
"""

from __future__ import annotations

import logging
import os
from typing import Any

from .backend import StorageBackend
from .sqlite_backend import SQLiteBackend
from .memory_backend import MemoryBackend

logger = logging.getLogger("gaia.storage.factory")

# Module-level singleton — one backend per process unless configure_backend()
# is called explicitly.
_DEFAULT_BACKEND: StorageBackend | None = None


def get_backend(
    backend_type: str | None = None,
    **kwargs: Any,
) -> StorageBackend:
    """
    Return the configured StorageBackend singleton.

    The backend is constructed once per process and cached.  Subsequent
    calls return the same instance unless configure_backend() has been
    called to replace it.

    Args:
        backend_type: Override the GAIA_STORAGE_BACKEND env var.
                      One of: "sqlite", "memory", "cockroachdb",
                              "scylladb", "ipfs".
                      Defaults to GAIA_STORAGE_BACKEND or "sqlite".
        **kwargs:     Passed directly to the backend constructor.
                      e.g. get_backend("sqlite", db_path="/data/gaia.db")

    Returns:
        A ready-to-use StorageBackend instance.

    Raises:
        NotImplementedError: For Phase 2 / 3 backends not yet implemented.
        ValueError: For unknown backend type strings.
    """
    global _DEFAULT_BACKEND

    if _DEFAULT_BACKEND is not None and backend_type is None and not kwargs:
        return _DEFAULT_BACKEND

    btype = (
        backend_type
        or os.environ.get("GAIA_STORAGE_BACKEND", "sqlite")
    ).lower().strip()

    backend: StorageBackend

    if btype == "sqlite":
        db_path = kwargs.pop(
            "db_path",
            os.environ.get("GAIA_STORAGE_PATH", "~/.gaia/storage.db"),
        )
        backend = SQLiteBackend(db_path=db_path, **kwargs)
        logger.info(f"[StorageFactory] SQLiteBackend → {db_path}")

    elif btype == "memory":
        backend = MemoryBackend(**kwargs)
        logger.info("[StorageFactory] MemoryBackend (ephemeral)")

    elif btype == "cockroachdb":
        # ─────────────────────────────────────────────────────────────────
        # Phase 2: CockroachDB — globally distributed SQL
        # ─────────────────────────────────────────────────────────────────
        # To implement:
        #   pip install asyncpg
        #   Create core/storage/cockroachdb_backend.py implementing StorageBackend
        #   Uncomment: from .cockroachdb_backend import CockroachDBBackend
        #   Set GAIA_STORAGE_DSN=postgresql://user:pw@host:26257/gaia
        raise NotImplementedError(
            "CockroachDB backend is not yet implemented (Phase 2).\n"
            "To implement:\n"
            "  1. pip install asyncpg\n"
            "  2. Create core/storage/cockroachdb_backend.py\n"
            "  3. Set GAIA_STORAGE_BACKEND=cockroachdb\n"
            "  4. Set GAIA_STORAGE_DSN=postgresql://user:pw@host:26257/gaia"
        )

    elif btype == "scylladb":
        # ─────────────────────────────────────────────────────────────────
        # Phase 2: ScyllaDB — high-throughput time-series (telemetry)
        # ─────────────────────────────────────────────────────────────────
        # To implement:
        #   pip install cassandra-driver
        #   Create core/storage/scylla_backend.py implementing StorageBackend
        #   Uncomment: from .scylla_backend import ScyllaBackend
        #   Set GAIA_STORAGE_DSN=scylla://host:9042/gaia
        raise NotImplementedError(
            "ScyllaDB backend is not yet implemented (Phase 2).\n"
            "To implement:\n"
            "  1. pip install cassandra-driver\n"
            "  2. Create core/storage/scylla_backend.py\n"
            "  3. Set GAIA_STORAGE_BACKEND=scylladb\n"
            "  4. Set GAIA_STORAGE_DSN=scylla://host:9042/gaia"
        )

    elif btype == "ipfs":
        # ─────────────────────────────────────────────────────────────────
        # Phase 3: IPFS / OrbitDB — content-addressed sovereign memory
        # ─────────────────────────────────────────────────────────────────
        # To implement:
        #   pip install ipfshttpclient
        #   Create core/storage/ipfs_backend.py implementing StorageBackend
        #   Requires a running IPFS daemon (or Kubo RPC endpoint)
        raise NotImplementedError(
            "IPFS/OrbitDB backend is not yet implemented (Phase 3).\n"
            "To implement:\n"
            "  1. pip install ipfshttpclient\n"
            "  2. Run an IPFS daemon (or configure Kubo RPC endpoint)\n"
            "  3. Create core/storage/ipfs_backend.py\n"
            "  4. Set GAIA_STORAGE_BACKEND=ipfs\n"
            "  5. Set GAIA_STORAGE_DSN=http://127.0.0.1:5001"
        )

    else:
        raise ValueError(
            f"Unknown storage backend: {btype!r}. "
            f"Valid options: sqlite, memory, cockroachdb, scylladb, ipfs"
        )

    if backend_type is None and not kwargs:
        _DEFAULT_BACKEND = backend

    return backend


def configure_backend(backend: StorageBackend) -> None:
    """
    Replace the module-level singleton with a pre-constructed backend.

    Use this in tests or when you need fine-grained control:

        from core.storage import configure_backend, MemoryBackend
        configure_backend(MemoryBackend())

    Or to use the SovereignStorageBackend for a specific Gaian:

        from core.storage import configure_backend, SQLiteBackend, SovereignStorageBackend
        key = derive_key_from_passphrase(gaian_passphrase)
        base = SQLiteBackend(db_path=f"~/.gaia/{gaian_id}/memories.db")
        sovereign = SovereignStorageBackend(base, encryption_key=key)
        configure_backend(sovereign)
    """
    global _DEFAULT_BACKEND
    _DEFAULT_BACKEND = backend
    logger.info(f"[StorageFactory] Backend configured: {backend!r}")

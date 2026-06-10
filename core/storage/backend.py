"""
core/storage/backend.py
=======================
StorageBackend — Abstract protocol that all GAIA-OS persistence layers
must implement.  Decouples engine code from any specific database.

Design principles
-----------------
1. All methods are async.  Backends that wrap sync libraries (SQLite,
   LevelDB) run their I/O in a thread-pool executor so the event loop
   is never blocked.

2. Keys are plain strings.  Values are raw bytes.  Serialisation
   (JSON, msgpack, protobuf) is the responsibility of the caller.

3. Prefix queries enable namespace-scoped scans (e.g. "mesh:", "affect:",
   "audit:") without a secondary index.

4. Optional TTL lets callers express expiry intent.  Backends that do
   not support TTL natively MUST still accept the parameter and log a
   warning rather than raising.

Sovereign Memory
----------------
SovereignStorageBackend wraps any backend with AES-GCM encryption so
a Gaian's memories are encrypted at rest with their own key.  No other
node, process, or human can read the data without the key. (Canon C04)

Phase roadmap
-------------
    Phase 1  SQLiteBackend       — this file + sqlite_backend.py
    Phase 2  CockroachDBBackend  — globally distributed SQL
             ScyllaBackend       — high-throughput time-series
             IPFSBackend         — content-addressed sovereign memory
    Phase 3  StoreForwardBackend — interplanetary queue + vector clocks

Issue: #281
"""

from __future__ import annotations

import logging
import os
from typing import Protocol, runtime_checkable

logger = logging.getLogger("gaia.storage")


# ─────────────────────────────────────────────────────────────────────────────
# Errors
# ─────────────────────────────────────────────────────────────────────────────

class StorageError(Exception):
    """Base class for all storage layer errors."""


class StorageKeyError(StorageError):
    """Raised when a requested key does not exist."""


class StorageWriteError(StorageError):
    """Raised when a write operation fails."""


class StorageConnectionError(StorageError):
    """Raised when the backend cannot establish a connection."""


# ─────────────────────────────────────────────────────────────────────────────
# StorageBackend Protocol
# ─────────────────────────────────────────────────────────────────────────────

@runtime_checkable
class StorageBackend(Protocol):
    """
    Abstract storage backend protocol.

    All GAIA-OS persistence (telemetry, sovereign memory, mesh state,
    audit ledger, crisis records) routes through this interface.
    Implementations MUST be async-safe.  Sync-only libraries (SQLite)
    MUST wrap blocking I/O in asyncio.get_event_loop().run_in_executor().

    Key format conventions (enforced by callers, not the backend)
    --------------------------------------------------------------
        mesh:<key>              collective field entries
        affect:<node_id>        per-node affect vectors
        coherence:<node_id>     per-node coherence scores
        audit:<user_id>:<ts>    audit ledger events
        memory:<user_id>:<id>   sovereign Gaian memories
        telemetry:<ts>:<event>  telemetry events
        crisis:<id>             crisis engine records
    """

    async def put(
        self,
        key: str,
        value: bytes,
        ttl: int | None = None,
    ) -> None:
        """
        Write a value under key.

        Args:
            key:   Unique string key.
            value: Raw bytes value.  Callers handle serialisation.
            ttl:   Optional time-to-live in seconds.  Backends that do
                   not support TTL MUST accept and ignore this parameter
                   (they may log a debug warning).

        Raises:
            StorageWriteError: If the write fails.
        """
        ...

    async def get(self, key: str) -> bytes | None:
        """
        Retrieve a value by key.

        Returns:
            Raw bytes if the key exists, None otherwise.
            Never raises StorageKeyError — callers check for None.
        """
        ...

    async def query(
        self,
        prefix: str,
        limit: int = 100,
    ) -> list[tuple[str, bytes]]:
        """
        Return all (key, value) pairs whose key starts with prefix.

        Results are ordered by key ascending.
        Returns an empty list if no keys match.

        Args:
            prefix: Key prefix to scan (e.g. "mesh:", "audit:user_1:").
            limit:  Maximum number of rows to return.
        """
        ...

    async def delete(self, key: str) -> None:
        """
        Delete a key.  No-op if the key does not exist.

        Raises:
            StorageWriteError: If the delete fails for a non-absence reason.
        """
        ...

    async def close(self) -> None:
        """
        Release any held resources (connections, file handles, threads).
        Safe to call multiple times.
        """
        ...

    async def ping(self) -> bool:
        """
        Health check.  Returns True if the backend is reachable.
        Used by the mesh server status endpoint.
        """
        ...


# ─────────────────────────────────────────────────────────────────────────────
# SovereignStorageBackend — encryption wrapper (Canon C04)
# ─────────────────────────────────────────────────────────────────────────────

class SovereignStorageBackend:
    """
    Encrypts all values with AES-256-GCM before delegating to the
    wrapped backend.  Decrypts transparently on read.

    This ensures a Gaian's memories are encrypted at rest with their own
    key.  The key never leaves the device.  No other node or process can
    read the data without it. (Canon C04 — Sovereign Privacy)

    Usage
    -----
        key = os.urandom(32)  # or derive from Gaian's passphrase
        base = SQLiteBackend(db_path="~/.gaia/memories.db")
        sovereign = SovereignStorageBackend(base, encryption_key=key)
        await sovereign.put("memory:luna:001", b"{...}")

    Requires: cryptography package (pip install cryptography)
    Graceful degradation: if cryptography is unavailable, operates as a
    passthrough (logs a warning) so the rest of GAIA-OS keeps running.
    """

    _NONCE_LEN = 12   # AES-GCM standard nonce length
    _TAG_LEN   = 16   # AES-GCM authentication tag length

    def __init__(
        self,
        backend: StorageBackend,
        encryption_key: bytes,
    ) -> None:
        self._backend = backend
        self._key = encryption_key
        self._crypto_available = False

        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            self._aesgcm = AESGCM(encryption_key)
            self._crypto_available = True
        except ImportError:
            logger.warning(
                "[SovereignStorage] cryptography package not installed. "
                "Data stored UNENCRYPTED. Install: pip install cryptography"
            )

    def _encrypt(self, plaintext: bytes) -> bytes:
        if not self._crypto_available:
            return plaintext
        nonce = os.urandom(self._NONCE_LEN)
        ct = self._aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ct  # prepend nonce for storage

    def _decrypt(self, ciphertext: bytes) -> bytes:
        if not self._crypto_available:
            return ciphertext
        if len(ciphertext) < self._NONCE_LEN:
            raise StorageError("Ciphertext too short — corrupt or unencrypted data.")
        nonce = ciphertext[:self._NONCE_LEN]
        ct    = ciphertext[self._NONCE_LEN:]
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            return AESGCM(self._key).decrypt(nonce, ct, None)
        except Exception as exc:
            raise StorageError(f"Decryption failed: {exc}") from exc

    async def put(
        self, key: str, value: bytes, ttl: int | None = None
    ) -> None:
        await self._backend.put(key, self._encrypt(value), ttl=ttl)

    async def get(self, key: str) -> bytes | None:
        raw = await self._backend.get(key)
        if raw is None:
            return None
        return self._decrypt(raw)

    async def query(
        self, prefix: str, limit: int = 100
    ) -> list[tuple[str, bytes]]:
        rows = await self._backend.query(prefix, limit=limit)
        return [(k, self._decrypt(v)) for k, v in rows]

    async def delete(self, key: str) -> None:
        await self._backend.delete(key)

    async def close(self) -> None:
        await self._backend.close()

    async def ping(self) -> bool:
        return await self._backend.ping()

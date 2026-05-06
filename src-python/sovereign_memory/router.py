"""
FastAPI router for Sovereign Memory  (Issue #66)

Mount in main.py::

    from sovereign_memory.router import memory_router, init_memory
    app.include_router(memory_router, prefix="/memory")

Endpoints
---------
GET  /memory/health                            — liveness probe + vec status
POST /memory/episode                           — store an episodic memory
GET  /memory/episode/{principal_id}/{ep_id}    — retrieve one episode (decrypted)
GET  /memory/episodes/{principal_id}           — list recent episodes
POST /memory/semantic                          — distil a semantic pattern
GET  /memory/search/{principal_id}             — semantic vector search
GET  /memory/biometric/{principal_id}          — get biometric history
DELETE /memory/episode/{principal_id}/{ep_id}  — soft-delete an episode
GET  /memory/schema-version                    — return current schema version
POST /memory/crypto-erase/{key_id}             — GDPR Art.17 crypto-erasure
POST /memory/remember                          — convenience: store a chat turn
POST /memory/recall                            — convenience: retrieve context for query
POST /memory/prune                             — remove orphaned vector rows

Key management (NEW)
--------------------
GET  /memory/key-status                        — MK source, key ring state
POST /memory/key-backup                        — export encrypted MK blob
POST /memory/key-restore                       — import MK from backup blob
POST /memory/key-rotate                        — retire current DEK, activate next version
"""

from __future__ import annotations

import logging
import time
from typing import List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

memory_router = APIRouter(tags=["sovereign_memory"])
_memory = None   # SovereignMemory singleton


def init_memory(memory) -> None:
    """Call from app lifespan after SovereignMemory.open()."""
    global _memory
    _memory = memory
    logger.info("SovereignMemory router initialised")


def _assert_ready():
    if _memory is None:
        raise HTTPException(503, "Sovereign Memory not initialised")


# ─────────────────────────────────────────────
# Request / response models
# ─────────────────────────────────────────────

class StoreEpisodeRequest(BaseModel):
    principal_id : str
    content      : str
    type         : str = "journal"
    tags         : List[str] = Field(default_factory=list)
    created_at   : Optional[int] = None


class StoreSemanticRequest(BaseModel):
    principal_id : str
    pattern      : str
    episode_ids  : List[str]
    confidence   : float = 0.7
    tags         : List[str] = Field(default_factory=list)


class RememberRequest(BaseModel):
    """Convenience model: store a single chat turn as an episodic memory."""
    principal_id : str
    text         : str
    role         : Literal["user", "gaia", "system"] = "user"
    type         : str = "conversation"
    tags         : List[str] = Field(default_factory=list)


class RecallRequest(BaseModel):
    """Convenience model: retrieve relevant memories for a query."""
    principal_id : str
    query        : str
    limit        : int = Field(10, ge=1, le=100)


# — Key management request models —

class KeyBackupRequest(BaseModel):
    """
    passphrase: The backup password chosen by the user.
    The MK will be wrapped under an Argon2id-derived key; the returned
    blob is safe to write to disk or cloud.
    """
    passphrase : str = Field(..., min_length=1)


class KeyRestoreRequest(BaseModel):
    """
    backup_blob: Raw JSON string from gaia-sovereign-backup.json
    passphrase:  The password used when the backup was created
    """
    backup_blob : str = Field(..., min_length=10)
    passphrase  : str = Field(..., min_length=1)


class KeyRotateRequest(BaseModel):
    """
    domain: Which key family to rotate.
      - 'episodic'  → episodic-vN  → episodic-v(N+1)
      - 'semantic'  → semantic-vN  → semantic-v(N+1)
      - 'legacy'    → legacy-vN    → legacy-v(N+1)
    """
    domain : Literal["episodic", "semantic", "legacy"]


# ─────────────────────────────────────────────
# Core endpoints (unchanged)
# ─────────────────────────────────────────────

@memory_router.get("/health")
async def health() -> JSONResponse:
    from . import vec_search
    ok = _memory is not None
    return JSONResponse(status_code=200 if ok else 503, content={
        "ok": ok,
        "vec_search": vec_search.is_vec_available(),
    })


@memory_router.post("/episode")
async def store_episode(req: StoreEpisodeRequest) -> JSONResponse:
    _assert_ready()
    episode_id = _memory.store_episode(
        principal_id=req.principal_id,
        content=req.content,
        type=req.type,
        tags=req.tags,
        created_at=req.created_at,
    )
    return JSONResponse(status_code=201, content={"episode_id": episode_id})


@memory_router.get("/episode/{principal_id}/{episode_id}")
async def get_episode(principal_id: str, episode_id: str) -> JSONResponse:
    _assert_ready()
    record = _memory.get_episode(principal_id, episode_id)
    if record is None:
        raise HTTPException(404, f"Episode '{episode_id}' not found")
    return JSONResponse(content=record.__dict__)


@memory_router.get("/episodes/{principal_id}")
async def list_episodes(
    principal_id: str,
    type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> JSONResponse:
    _assert_ready()
    records = _memory.list_episodes(principal_id, type=type, limit=limit)
    return JSONResponse(content={"episodes": [r.__dict__ for r in records]})


@memory_router.post("/semantic")
async def store_semantic(req: StoreSemanticRequest) -> JSONResponse:
    _assert_ready()
    pattern_id = _memory.distill_semantic(
        principal_id=req.principal_id,
        pattern=req.pattern,
        episode_ids=req.episode_ids,
        confidence=req.confidence,
        tags=req.tags,
    )
    return JSONResponse(status_code=201, content={"pattern_id": pattern_id})


@memory_router.get("/search/{principal_id}")
async def search_memory(
    principal_id: str,
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100),
) -> JSONResponse:
    _assert_ready()
    results = _memory.search_memory(principal_id, q, limit=limit)
    return JSONResponse(content={
        "results": [r.__dict__ for r in results],
        "vec_search": True,
    })


@memory_router.get("/biometric/{principal_id}")
async def get_biometric_history(
    principal_id: str,
    signal_type: str = Query(...),
    days: int = Query(30, ge=1, le=365),
) -> JSONResponse:
    _assert_ready()
    samples = _memory.get_biometric_history(principal_id, signal_type, days)
    return JSONResponse(content={
        "signal_type": signal_type,
        "samples": [{"timestamp": s.timestamp, "value": s.value, "source": s.source} for s in samples]
    })


@memory_router.delete("/episode/{principal_id}/{episode_id}")
async def soft_delete_episode(principal_id: str, episode_id: str) -> JSONResponse:
    _assert_ready()
    _memory.soft_delete_episode(principal_id, episode_id)
    return JSONResponse(content={"deleted": True, "episode_id": episode_id})


@memory_router.get("/schema-version")
async def schema_version() -> JSONResponse:
    _assert_ready()
    from .migrations import MigrationRunner
    runner = MigrationRunner(_memory._conn)
    return JSONResponse(content={
        "current_version": runner.current_version(),
        "history": runner.list_applied(),
    })


@memory_router.post("/crypto-erase/{key_id}")
async def crypto_erase(key_id: str) -> JSONResponse:
    """
    GDPR Art. 17 crypto-erasure: revoke a DEK.
    All rows encrypted under key_id become permanently unrecoverable.
    IRREVERSIBLE.
    """
    _assert_ready()
    _memory.crypto_erase_key(key_id)
    return JSONResponse(content={
        "erased": True,
        "key_id": key_id,
        "warning": "All data encrypted under this key is permanently unrecoverable."
    })


# ─────────────────────────────────────────────
# Convenience endpoints (vec memory)
# ─────────────────────────────────────────────

@memory_router.post("/remember")
async def remember(req: RememberRequest) -> JSONResponse:
    _assert_ready()
    episode_id = _memory.remember(
        principal_id=req.principal_id,
        text=req.text,
        role=req.role,
        type=req.type,
        tags=req.tags,
    )
    return JSONResponse(status_code=201, content={"episode_id": episode_id})


@memory_router.post("/recall")
async def recall(req: RecallRequest) -> JSONResponse:
    _assert_ready()
    results = _memory.recall(
        principal_id=req.principal_id,
        query=req.query,
        limit=req.limit,
    )
    return JSONResponse(content={
        "results": [r.__dict__ for r in results],
        "count": len(results),
    })


@memory_router.post("/prune")
async def prune_vectors() -> JSONResponse:
    _assert_ready()
    removed = _memory.prune_vectors()
    return JSONResponse(content={"removed": removed})


# ─────────────────────────────────────────────
# Key management endpoints (NEW)
# ─────────────────────────────────────────────

@memory_router.get("/key-status")
async def key_status() -> JSONResponse:
    """
    Return the current state of the key ring.

    Response fields:
      mk_loaded   : bool   — is the Master Key in memory?
      mk_source   : str    — where MK lives: macos_keychain | windows_credential_manager
                                             | secret_service | passphrase_derived | not_loaded
      keys        : list   — rows from encryption_keys (id, status, created_at, rotated_at)
      schema_ver  : int    — current schema_version
    """
    _assert_ready()
    from .crypto import MasterKeyManager
    from .migrations import MigrationRunner

    mk_source = MasterKeyManager.mk_source()
    mk_loaded = mk_source != "not_loaded"

    keys = _memory._conn.execute(
        """
        SELECT key_id, status, created_at, rotated_at
        FROM encryption_keys
        ORDER BY created_at ASC
        """
    ).fetchall()

    runner = MigrationRunner(_memory._conn)
    schema_ver = runner.current_version()

    return JSONResponse(content={
        "mk_loaded": mk_loaded,
        "mk_source": mk_source,
        "schema_ver": schema_ver,
        "keys": [
            {
                "key_id":     row["key_id"],
                "status":     row["status"],
                "created_at": row["created_at"],
                "rotated_at": row["rotated_at"],
            }
            for row in keys
        ],
    })


@memory_router.post("/key-backup")
async def key_backup(req: KeyBackupRequest) -> JSONResponse:
    """
    Export an AES-256-GCM encrypted backup of the Master Key.

    The returned 'blob' is a JSON string the frontend should write to
    disk as gaia-sovereign-backup.json.  The passphrase is not stored
    anywhere; the user is responsible for remembering it.

    IMPORTANT: The backup is only as secure as the passphrase.  Use a
    strong, unique passphrase and store the file + passphrase separately.
    """
    _assert_ready()
    from .crypto import MasterKeyManager

    try:
        blob_bytes = MasterKeyManager.export_encrypted(req.passphrase)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    return JSONResponse(
        status_code=200,
        content={
            "blob": blob_bytes.decode("utf-8"),
            "filename": "gaia-sovereign-backup.json",
            "warning": (
                "Store this file and your passphrase in separate, secure locations. "
                "Without both, your encrypted memories cannot be recovered."
            ),
        },
    )


@memory_router.post("/key-restore")
async def key_restore(req: KeyRestoreRequest) -> JSONResponse:
    """
    Import a Master Key from a backup blob.

    On success:
      - MK is saved to the OS keychain (if available).
      - MK is set in process memory immediately.
      - GAIA-OS does NOT need to restart for the current session, but the
        user should restart to ensure all components re-open with the new MK.

    On failure (wrong passphrase, corrupt file):
      - HTTP 400 with a human-readable error message.
      - The existing MK is NOT modified.
    """
    _assert_ready()
    from .crypto import MasterKeyManager

    try:
        MasterKeyManager.import_encrypted(
            blob=req.backup_blob.encode("utf-8"),
            passphrase=req.passphrase,
        )
    except ValueError as exc:
        raise HTTPException(400, f"Restore failed: {exc}")
    except RuntimeError as exc:
        raise HTTPException(500, f"Restore error: {exc}")

    return JSONResponse(
        status_code=200,
        content={
            "restored": True,
            "mk_source": MasterKeyManager.mk_source(),
            "note": "Master Key restored. Please restart GAIA-OS to apply fully.",
        },
    )


@memory_router.post("/key-rotate")
async def key_rotate(req: KeyRotateRequest) -> JSONResponse:
    """
    Retire the current active DEK for a domain and create the next version.

    This is a NON-DESTRUCTIVE forward rotation:
      - Old rows remain readable under the retired key.
      - New writes use the new key immediately.
      - To permanently destroy old data, follow with /crypto-erase/{old_key_id}.

    Domain → key_id naming: episodic → episodic-vN, semantic → semantic-vN, etc.
    """
    _assert_ready()
    import re

    domain = req.domain  # 'episodic' | 'semantic' | 'legacy'
    now = int(time.time() * 1000)

    # Find the currently active key for this domain
    rows = _memory._conn.execute(
        """
        SELECT key_id, status FROM encryption_keys
        WHERE key_id LIKE ? AND status = 'active'
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (f"{domain}-%",),
    ).fetchall()

    if not rows:
        raise HTTPException(
            404,
            f"No active key found for domain '{domain}'. "
            "Has it been crypto-erased?"
        )

    current_key_id: str = rows[0]["key_id"]  # e.g. 'episodic-v1'

    # Parse version number and increment
    m = re.search(r"-v(\d+)$", current_key_id)
    if not m:
        raise HTTPException(
            500,
            f"Key ID '{current_key_id}' does not follow the expected vN naming convention."
        )
    next_version = int(m.group(1)) + 1
    new_key_id = f"{domain}-v{next_version}"  # e.g. 'episodic-v2'

    # Guard: don't create a duplicate
    existing = _memory._conn.execute(
        "SELECT key_id FROM encryption_keys WHERE key_id=?", (new_key_id,)
    ).fetchone()
    if existing:
        raise HTTPException(
            409,
            f"Key '{new_key_id}' already exists. Rotation may have already been run."
        )

    # Retire old key + create new key in one transaction
    _memory._conn.execute("BEGIN")
    try:
        _memory._conn.execute(
            "UPDATE encryption_keys SET status='retired', rotated_at=? WHERE key_id=?",
            (now, current_key_id),
        )
        _memory._conn.execute(
            """
            INSERT INTO encryption_keys (key_id, wrapped_key, algorithm, created_at, status)
            VALUES (?, ?, 'aes-256-gcm', ?, 'active')
            """,
            (new_key_id, b"local-kdf", now),
        )
        _memory._conn.execute("COMMIT")
    except Exception as exc:
        _memory._conn.execute("ROLLBACK")
        raise HTTPException(500, f"Key rotation failed: {exc}")

    # Bust the DEK cache so next encrypt() uses the new key
    _memory._dek_cache.pop(current_key_id, None)
    _memory._dek_cache.pop(new_key_id, None)

    return JSONResponse(
        status_code=200,
        content={
            "rotated": True,
            "retired_key_id": current_key_id,
            "new_key_id": new_key_id,
            "note": (
                f"New writes to '{domain}' will use '{new_key_id}'. "
                f"Old data under '{current_key_id}' remains readable. "
                f"To permanently erase old data, call POST /memory/crypto-erase/{current_key_id}."
            ),
        },
    )

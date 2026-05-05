"""
FastAPI router for Sovereign Memory  (Issue #66)

Mount in main.py::

    from sovereign_memory.router import memory_router, init_memory
    app.include_router(memory_router, prefix="/memory")

Endpoints
---------
GET  /memory/health                            — liveness probe
POST /memory/episode                           — store an episodic memory
GET  /memory/episode/{principal_id}/{ep_id}    — retrieve one episode (decrypted)
GET  /memory/episodes/{principal_id}           — list recent episodes
POST /memory/semantic                          — distil a semantic pattern
GET  /memory/search/{principal_id}             — search memory
GET  /memory/biometric/{principal_id}          — get biometric history
DELETE /memory/episode/{principal_id}/{ep_id}  — soft-delete an episode
GET  /memory/schema-version                    — return current schema version
POST /memory/crypto-erase/{key_id}             — GDPR Art.17 crypto-erasure
"""

from __future__ import annotations

import logging
from typing import List, Optional

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
# Request models
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


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@memory_router.get("/health")
async def health() -> JSONResponse:
    ok = _memory is not None
    return JSONResponse(status_code=200 if ok else 503, content={"ok": ok})


@memory_router.post("/episode")
async def store_episode(req: StoreEpisodeRequest) -> JSONResponse:
    """Encrypt and store a new episodic memory."""
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
    """Retrieve and decrypt a single episodic memory."""
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
    """List recent episodes for a principal (decrypted previews)."""
    _assert_ready()
    records = _memory.list_episodes(principal_id, type=type, limit=limit)
    return JSONResponse(content={"episodes": [r.__dict__ for r in records]})


@memory_router.post("/semantic")
async def store_semantic(req: StoreSemanticRequest) -> JSONResponse:
    """Distil and store a semantic pattern."""
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
    """Search episodic + semantic memory."""
    _assert_ready()
    results = _memory.search_memory(principal_id, q, limit=limit)
    return JSONResponse(content={"results": [r.__dict__ for r in results]})


@memory_router.get("/biometric/{principal_id}")
async def get_biometric_history(
    principal_id: str,
    signal_type: str = Query(...),
    days: int = Query(30, ge=1, le=365),
) -> JSONResponse:
    """Return N-day biometric history for a signal type."""
    _assert_ready()
    samples = _memory.get_biometric_history(principal_id, signal_type, days)
    return JSONResponse(content={
        "signal_type": signal_type,
        "samples": [{"timestamp": s.timestamp, "value": s.value, "source": s.source} for s in samples]
    })


@memory_router.delete("/episode/{principal_id}/{episode_id}")
async def soft_delete_episode(principal_id: str, episode_id: str) -> JSONResponse:
    """Soft-delete an episode (ciphertext retained until key rotation)."""
    _assert_ready()
    _memory.soft_delete_episode(principal_id, episode_id)
    return JSONResponse(content={"deleted": True, "episode_id": episode_id})


@memory_router.get("/schema-version")
async def schema_version() -> JSONResponse:
    """Return current schema version and applied migration history."""
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
    This action is IRREVERSIBLE.
    """
    _assert_ready()
    _memory.crypto_erase_key(key_id)
    return JSONResponse(content={
        "erased": True,
        "key_id": key_id,
        "warning": "All data encrypted under this key is permanently unrecoverable."
    })

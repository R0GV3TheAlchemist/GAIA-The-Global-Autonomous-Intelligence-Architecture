"""
GAIA API — Memory Router

Exposes GAIA's semantic memory layer over HTTP so the Tauri frontend
and any other client can:
  - Store memories explicitly (POST /api/memory/remember)
  - Retrieve relevant memories for a query (POST /api/memory/retrieve)
  - Forget a specific item (DELETE /api/memory/forget/{item_id})
  - Check memory health (GET /api/memory/health)

All endpoints delegate to the GAIAOrchestrator singleton which holds
the live MemoryStore instance.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

log = logging.getLogger("gaia.api.memory")

router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


# ── Request / Response models ──────────────────────────────────────────────────

class RememberRequest(BaseModel):
    user_id:    str   = Field(..., description="User who owns this memory.")
    text:       str   = Field(..., description="Text content to remember.")
    kind:       str   = Field("note", description="Memory kind (note, fact, preference, goal, …).")
    importance: float = Field(0.5,   ge=0.0, le=1.0, description="Importance score 0–1.")
    session_id: Optional[str] = None


class RememberResponse(BaseModel):
    id:      int
    status:  str = "remembered"


class RetrieveRequest(BaseModel):
    user_id: str  = Field(..., description="User whose memories to search.")
    query:   str  = Field(..., description="Natural language query for semantic search.")
    top_k:   int  = Field(10,  ge=1, le=50, description="Max results to return.")


class MemoryHitOut(BaseModel):
    id:         int
    text:       str
    kind:       str
    role:       str
    importance: float
    score:      float
    created_at: float


class RetrieveResponse(BaseModel):
    hits:   List[MemoryHitOut]
    count:  int


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/remember", response_model=RememberResponse)
async def remember(req: RememberRequest) -> RememberResponse:
    """Store a new memory item for a user."""
    try:
        from core.runtime import get_orchestrator
        orch = get_orchestrator()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Orchestrator not ready.")

    item_id = await orch.remember(
        user_id=req.user_id,
        text=req.text,
        kind_str=req.kind,
        importance=req.importance,
        session_id=req.session_id,
    )
    if item_id is None:
        raise HTTPException(status_code=503, detail="Memory store unavailable.")
    return RememberResponse(id=item_id)


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(req: RetrieveRequest) -> RetrieveResponse:
    """Retrieve semantically relevant memories for a query."""
    try:
        from core.runtime import get_orchestrator
        orch = get_orchestrator()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Orchestrator not ready.")

    hits = await orch.retrieve(user_id=req.user_id, query=req.query, top_k=req.top_k)
    out = []
    for h in hits:
        try:
            out.append(MemoryHitOut(
                id=h.item.id or 0,
                text=h.item.text,
                kind=h.item.kind.value if hasattr(h.item.kind, 'value') else str(h.item.kind),
                role=h.item.role,
                importance=h.item.importance,
                score=round(getattr(h, 'score', 0.0), 4),
                created_at=h.item.created_at,
            ))
        except Exception as exc:
            log.warning("[memory.retrieve] Skipping malformed hit: %s", exc)
    return RetrieveResponse(hits=out, count=len(out))


@router.delete("/forget/{item_id}")
async def forget(item_id: int, user_id: str) -> dict:
    """Soft-delete a specific memory item by id."""
    try:
        from core.runtime import get_orchestrator
        orch = get_orchestrator()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Orchestrator not ready.")

    if not orch.memory:
        raise HTTPException(status_code=503, detail="Memory store unavailable.")
    try:
        orch.memory.forget(user_id=user_id, item_id=item_id)
        return {"status": "forgotten", "item_id": item_id}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/health")
async def memory_health() -> dict:
    """Return memory subsystem health and orchestrator status."""
    try:
        from core.runtime import get_orchestrator
        orch = get_orchestrator()
        return {"status": "ok", **orch.status()}
    except RuntimeError:
        return {"status": "not_ready", "ready": False}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}

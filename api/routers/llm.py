"""
GAIA API — LLM Router

Endpoints:
  POST /api/llm/generate          — single-shot generation (JSON response)
  POST /api/llm/generate/stream   — streaming generation (SSE)
  GET  /api/llm/routing-status    — live routing config + provider availability

All endpoints delegate to core/llm_router.py which handles the
offline-first routing logic.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from core.llm_router import generate, stream, routing_status

log = logging.getLogger("gaia.api.llm")

router = APIRouter(
    prefix="/llm",
    tags=["LLM"],
)


# ── Request / Response models ─────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt or full conversation turn.")
    system: Optional[str] = Field(
        None,
        description="Optional system prompt injected before the user message.",
    )


class GenerateResponse(BaseModel):
    text:       str
    provider:   str
    model:      str
    latency_ms: int
    offline:    bool
    metadata:   dict = {}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/generate",
    response_model=GenerateResponse,
    summary="Generate a response from GAIA's LLM (offline-first)",
)
async def llm_generate(req: GenerateRequest) -> GenerateResponse:
    """
    Route a prompt through GAIA's offline-first LLM router.

    The router tries providers in order based on GAIA_ROUTING_MODE:
      - local-first  (default): Ollama → OpenAI → Anthropic
      - cloud-first:            OpenAI/Anthropic → Ollama
      - local-only:             Ollama only
      - cloud-only:             OpenAI/Anthropic only

    Returns the generated text plus provenance metadata so the frontend
    can show which provider answered (e.g. a 🔒 badge when offline).
    """
    try:
        result = await generate(req.prompt, req.system)
    except RuntimeError as exc:
        log.error(f"[llm.generate] All providers failed: {exc}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "No LLM provider available.",
                "detail": str(exc),
                "hint": "Start Ollama locally or configure OPENAI_API_KEY / ANTHROPIC_API_KEY.",
            },
        )

    return GenerateResponse(
        text=result.text,
        provider=result.provider,
        model=result.model,
        latency_ms=result.latency_ms,
        offline=result.offline,
        metadata=result.metadata,
    )


@router.post(
    "/generate/stream",
    summary="Stream a response from GAIA's LLM (SSE, offline-first)",
)
async def llm_generate_stream(req: GenerateRequest) -> StreamingResponse:
    """
    Server-Sent Events stream of tokens.

    Each event is a plain text token (or space-separated word when falling
    back to a cloud provider that doesn't natively stream via this path).

    The stream ends with a final [DONE] sentinel event so the frontend
    can close the connection cleanly.

    Example client (TypeScript / fetch):

        const resp = await fetch('/api/llm/generate/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt }),
        });
        const reader = resp.body!.getReader();
        for await (const chunk of ...) { ... }
    """
    async def _event_stream():
        try:
            async for token in stream(req.prompt, req.system):
                yield f"data: {token}\n\n"
        except RuntimeError as exc:
            log.error(f"[llm.stream] Failed: {exc}")
            yield f"event: error\ndata: {exc}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":  "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/routing-status",
    summary="Live routing config and provider availability",
)
async def llm_routing_status() -> dict:
    """
    Returns the current routing mode, Ollama availability, and whether
    GAIA is running in sovereign (fully offline) mode.

    Example response:
      {
        "routing_mode": "local-first",
        "ollama": { "available": true, "model": "llama3", ... },
        "cloud": { "openai": true, "anthropic": false, ... },
        "sovereign": true
      }
    """
    return await routing_status()

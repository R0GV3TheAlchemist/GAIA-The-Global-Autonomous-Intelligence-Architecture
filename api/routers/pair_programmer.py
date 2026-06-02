"""
GAIA API — Pair Programmer Router

Endpoints:
  POST /api/pair-programmer/stream    — streaming code completion (SSE)
  POST /api/pair-programmer/complete  — single-shot code completion (JSON)

Both endpoints are code-aware wrappers around the LLM router.
They inject a sovereign code-assistant system prompt and forward
the request through core/llm_router.py exactly like the LLM router does,
so offline-first routing (Ollama → cloud fallback) is inherited for free.
"""

from __future__ import annotations

import logging
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from core.llm_router import generate, stream

log = logging.getLogger("gaia.api.pair_programmer")

router = APIRouter(
    prefix="/pair-programmer",
    tags=["Pair Programmer"],
)

# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are GAIA's sovereign Pair Programmer — a precise, thoughtful code assistant
embedded directly in the developer's environment.  You run locally and respect
the user's privacy; no code is ever sent to a third party unless the user has
explicitly configured a cloud provider.

Guidelines:
- Produce complete, runnable code unless the user explicitly asks for a snippet.
- Prefer the language/framework already in use in the surrounding context.
- Explain non-obvious decisions in brief inline comments, not lengthy prose.
- If the request is ambiguous, make a reasonable assumption and state it.
- Do NOT add unsolicited refactors outside the scope of the request.
- When a fix is requested, show only the corrected section plus minimal context.
- Always close every code block you open.
"""


# ── Request / Response models ─────────────────────────────────────────────────

class Message(BaseModel):
    """A single turn in the conversation (mirrors OpenAI / Ollama chat format)."""
    role:    Literal["user", "assistant", "system"]
    content: str = Field(..., max_length=10_000)


class PairProgrammerRequest(BaseModel):
    # Primary inputs — caller provides ONE of these:
    prompt:   Optional[str] = Field(
        None,
        max_length=20_000,
        description="Plain-text prompt.  Use this for simple, single-turn requests.",
    )
    messages: Optional[list[Message]] = Field(
        None,
        description="Multi-turn conversation history (role/content pairs).  "
                    "The last message must be from the user.  "
                    "Takes precedence over `prompt` when both are provided.",
    )

    # Optional context injected before the conversation
    file_context: Optional[str] = Field(
        None,
        max_length=50_000,          # ~1,250 lines — keeps total prompt within model limits
        description="Raw source of the file currently open in the editor.  "
                    "Injected into the system prompt so the model understands "
                    "the surrounding code.",
    )
    language: Optional[str] = Field(
        None,
        max_length=64,
        description="Programming language hint (e.g. 'TypeScript', 'Python').  "
                    "Helps the model choose the right syntax when not inferable "
                    "from `file_context`.",
    )
    cursor_context: Optional[str] = Field(
        None,
        max_length=5_000,           # ~125 lines — tight excerpt around the cursor
        description="A small excerpt (±20 lines) around the cursor position.  "
                    "Used to anchor completions to the exact edit location.",
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "prompt": "Add JSDoc to every exported function in this file.",
                    "language": "TypeScript",
                    "file_context": "export function add(a: number, b: number) { return a + b; }",
                },
                {
                    "messages": [
                        {"role": "user", "content": "How do I debounce a React hook?"},
                        {"role": "assistant", "content": "Here's a minimal debounce hook..."},
                        {"role": "user", "content": "Can you add a leading-edge option?"},
                    ]
                },
            ]
        }


class CompleteResponse(BaseModel):
    text:       str  = Field(..., description="The generated code / answer.")
    provider:   str  = Field(..., description="Which LLM provider answered.")
    model:      str  = Field(..., description="Model name returned by the provider.")
    latency_ms: int  = Field(..., description="Wall-clock latency in milliseconds.")
    offline:    bool = Field(..., description="True when answered by the local Ollama instance.")
    metadata:   dict = Field(default_factory=dict)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_prompt(req: PairProgrammerRequest) -> str:
    """
    Collapse a PairProgrammerRequest down to the single prompt string that
    `core.llm_router.generate / stream` expects.

    Priority:
      1. If `messages` is supplied, serialise them as a role-prefixed transcript.
      2. Otherwise fall through to `prompt`.
    """
    if req.messages:
        lines = []
        for msg in req.messages:
            lines.append(f"{msg.role.upper()}: {msg.content}")
        return "\n".join(lines)

    if req.prompt:
        return req.prompt

    raise ValueError("Either `prompt` or `messages` must be provided.")


def _build_system(req: PairProgrammerRequest) -> str:
    """
    Augment the base system prompt with any editor context the caller supplied.
    """
    parts = [_SYSTEM_PROMPT]

    if req.language:
        parts.append(f"Language in use: {req.language}.")

    if req.file_context:
        parts.append(
            "\n--- CURRENT FILE ---\n"
            + req.file_context.strip()
            + "\n--- END OF FILE ---"
        )

    if req.cursor_context:
        parts.append(
            "\n--- CURSOR CONTEXT (±20 lines) ---\n"
            + req.cursor_context.strip()
            + "\n--- END CURSOR CONTEXT ---"
        )

    return "\n\n".join(parts)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/complete",
    response_model=CompleteResponse,
    summary="Single-shot code completion (offline-first)",
)
async def pair_programmer_complete(req: PairProgrammerRequest) -> CompleteResponse:
    """
    Returns the full completion in one JSON response.

    Use this for:
    - Background / non-interactive requests (e.g. linting explanations)
    - Short completions where streaming UX isn't needed
    - Tool calls where the caller needs the full response before proceeding

    Routing follows `GAIA_ROUTING_MODE`:
      local-first (default) → Ollama → OpenAI → Anthropic
    """
    try:
        prompt = _build_prompt(req)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    system = _build_system(req)

    try:
        result = await generate(prompt, system)
    except RuntimeError as exc:
        log.error(f"[pair_programmer.complete] All providers failed: {exc}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "No LLM provider available.",
                "detail": str(exc),
                "hint": "Start Ollama locally or configure OPENAI_API_KEY / ANTHROPIC_API_KEY.",
            },
        )

    return CompleteResponse(
        text=result.text,
        provider=result.provider,
        model=result.model,
        latency_ms=result.latency_ms,
        offline=result.offline,
        metadata=result.metadata,
    )


@router.post(
    "/stream",
    summary="Streaming code completion — Server-Sent Events (offline-first)",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "SSE token stream.  Each event is `data: <token>\\n\\n`.  "
                           "Stream ends with `data: [DONE]\\n\\n`.",
            "content": {"text/event-stream": {}},
        }
    },
)
async def pair_programmer_stream(req: PairProgrammerRequest) -> StreamingResponse:
    """
    Streams tokens back as Server-Sent Events for real-time display in the editor.

    Protocol:
      - Each token arrives as:     `data: <token>\\n\\n`
      - Errors arrive as:          `event: error\\ndata: <message>\\n\\n`
      - Stream terminator:         `data: [DONE]\\n\\n`

    TypeScript fetch example:

        const resp = await fetch('/api/pair-programmer/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, language, file_context }),
        });

        const reader = resp.body!.getReader();
        const decoder = new TextDecoder();
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            for (const line of chunk.split('\\n')) {
                if (line.startsWith('data: ')) {
                    const token = line.slice(6);
                    if (token === '[DONE]') return;
                    appendToEditor(token);
                }
            }
        }
    """
    try:
        prompt = _build_prompt(req)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    system = _build_system(req)

    async def _event_stream():
        try:
            async for token in stream(prompt, system):
                # Escape newlines inside the token so SSE framing stays intact
                safe = token.replace("\n", "\\n")
                yield f"data: {safe}\n\n"
        except RuntimeError as exc:
            log.error(f"[pair_programmer.stream] Failed: {exc}")
            yield f"event: error\ndata: {exc}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

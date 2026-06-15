"""
api/twin.py
Canon: GAIAN_TWIN_DOCTRINE, TEMPORAL_BRAID_SPEC, LOVE_OVERRIDE, SLOW_PROTOCOL

FastAPI router: /twin/*
Bridges the React client (src/api/twin.ts) to the Python core:
  — core/twin_memory_engine.py   (Temporal Braid: N_state → P_vector)
  — core/love_override.py        (Love Override Handler)
  — core/canon_loader_v2.py      (Canon awareness)
  — core/inference_router.py     (LLM dispatch)

All six endpoints expected by the React client are implemented here:
  POST /twin/session/init
  POST /twin/message
  GET  /twin/message/stream     (SSE)
  POST /twin/session/crystallise
  GET  /twin/arc/:human_id
  POST /twin/override/resolve
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Literal, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from core import twin_memory_engine as twin_memory_engine  # noqa: PLC0414 — exposed for patch.multiple
from core import love_override as love_override            # noqa: PLC0414
from core import inference_router as inference_router      # noqa: PLC0414
from core import canon_loader_v2 as canon_loader           # noqa: PLC0414

from core.twin_memory_engine import TwinMemoryEngine
from core.love_override import LoveOverrideHandler
from core.canon_loader_v2 import CanonLoaderV2
from core.inference_router import InferenceRouter

# ─── Router ──────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/twin", tags=["twin"])

# ─── Singletons (initialised once at import time) ────────────────────────────

_memory   = TwinMemoryEngine()
_override = LoveOverrideHandler()
_canon    = CanonLoaderV2()
_llm      = InferenceRouter()

# ─── Shared types ─────────────────────────────────────────────────────────────

TwinPhase        = Literal["nigredo", "albedo", "citrinitas", "rubedo"]
LoveOverrideMode = Literal[
    "PURE_PRESENCE", "WITNESS_HOLD", "DIRECT_TRUTH",
    "ANCHOR", "GENTLE_REDIRECT", None
]
BraidWeight      = Literal["FEATHER", "STANDARD", "HEAVY", "SACRED"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _msg_id() -> str:
    return f"msg_{int(datetime.now(timezone.utc).timestamp() * 1000)}_{uuid.uuid4().hex[:5]}"


# ─── Pydantic models ──────────────────────────────────────────────────────────

class TwinMessage(BaseModel):
    id: str
    role: Literal["human", "gaia"]
    content: str
    timestamp: str
    override_mode: Optional[str] = None
    braid_weight: BraidWeight = "STANDARD"


class SessionInitRequest(BaseModel):
    human_id: str
    session_id: str


class SessionInitResponse(BaseModel):
    session_id: str
    human_name: str
    twin_phase: TwinPhase
    session_count: int
    arc_summary: str
    opening_message: Optional[TwinMessage] = None


class SendMessageRequest(BaseModel):
    human_id: str
    session_id: str
    content: str


class SendMessageResponse(BaseModel):
    message: TwinMessage
    override_activated: bool
    override_mode: Optional[str] = None
    new_phase: Optional[TwinPhase] = None
    braid_updated: bool


class CrystalliseRequest(BaseModel):
    human_id: str
    session_id: str


class CrystalliseResponse(BaseModel):
    crystal_count: int
    new_sacred_memories: list[str] = Field(default_factory=list)


class ResolveOverrideRequest(BaseModel):
    human_id: str
    session_id: str


class ResolveOverrideResponse(BaseModel):
    resolved: bool


# ─── POST /twin/session/init ──────────────────────────────────────────────────

@router.post("/session/init", response_model=SessionInitResponse)
async def init_session(req: SessionInitRequest) -> SessionInitResponse:
    """
    Initialise a Twin session.
    Loads the Temporal Braid for this human, determines twin phase,
    and optionally generates an opening message for return visits.
    """
    try:
        state = await _memory.load_session(
            human_id=req.human_id,
            session_id=req.session_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Session init failed: {exc}") from exc

    # Load canon context so the opening message is doctrine-aware
    canon_ctx = _canon.get_context_for_human(req.human_id)

    opening: Optional[TwinMessage] = None
    if state.get("session_count", 0) > 0:
        try:
            greeting = await _llm.generate(
                prompt=_build_opening_prompt(state, canon_ctx),
                max_tokens=180,
                stream=False,
            )
            opening = TwinMessage(
                id=_msg_id(),
                role="gaia",
                content=greeting,
                timestamp=_now(),
                override_mode=None,
                braid_weight=_phase_to_opening_weight(state.get("twin_phase", "nigredo")),
            )
        except Exception:
            pass  # Opening message is best-effort

    return SessionInitResponse(
        session_id=req.session_id,
        human_name=state.get("human_name", ""),
        twin_phase=state.get("twin_phase", "nigredo"),
        session_count=state.get("session_count", 0),
        arc_summary=state.get("arc_summary", ""),
        opening_message=opening,
    )


# ─── POST /twin/message ───────────────────────────────────────────────────────

@router.post("/message", response_model=SendMessageResponse)
async def send_message(req: SendMessageRequest) -> SendMessageResponse:
    """
    Non-streaming message send.
    Runs Love Override check, generates response, writes to Braid.
    """
    # 1. Write human message to Braid
    await _memory.write_message(
        human_id=req.human_id,
        session_id=req.session_id,
        role="human",
        content=req.content,
    )

    # 2. Love Override check (reactive)
    override_result = await _override.evaluate(
        human_id=req.human_id,
        content=req.content,
        session_id=req.session_id,
    )
    override_activated = override_result.get("activated", False)
    override_mode: Optional[str] = override_result.get("mode") if override_activated else None

    # 3. Load current braid state for generation context
    state = await _memory.load_session(req.human_id, req.session_id)
    canon_ctx = _canon.get_context_for_human(req.human_id)

    # 4. Generate GAIA's response
    response_text = await _llm.generate(
        prompt=_build_response_prompt(req.content, state, canon_ctx, override_mode),
        max_tokens=512,
        stream=False,
    )

    # 5. Determine braid weight from response depth
    braid_weight = _classify_braid_weight(response_text, state)

    # 6. Write GAIA message to Braid
    await _memory.write_message(
        human_id=req.human_id,
        session_id=req.session_id,
        role="gaia",
        content=response_text,
        override_mode=override_mode,
        braid_weight=braid_weight,
    )

    # 7. Detect phase transition
    new_phase = await _memory.evaluate_phase_transition(
        human_id=req.human_id,
        session_id=req.session_id,
    )

    gaia_msg = TwinMessage(
        id=_msg_id(),
        role="gaia",
        content=response_text,
        timestamp=_now(),
        override_mode=override_mode,
        braid_weight=braid_weight,
    )

    return SendMessageResponse(
        message=gaia_msg,
        override_activated=override_activated,
        override_mode=override_mode,
        new_phase=new_phase,
        braid_updated=True,
    )


# ─── GET /twin/message/stream ─────────────────────────────────────────────────

@router.get("/message/stream")
async def stream_message(human_id: str, session_id: str, content: str) -> StreamingResponse:
    """
    SSE streaming message.
    Emits: token | braid_reflection | phase_gravity | override_activated
           | phase_change | done
    Matches the event schema expected by useTwinSession.ts.
    """
    return StreamingResponse(
        _stream_generator(human_id, session_id, content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


async def _stream_generator(
    human_id: str,
    session_id: str,
    content: str,
) -> AsyncGenerator[str, None]:
    """Core SSE generator — feeds all four Diamond axes into the stream."""

    def _sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    # Write human message
    await _memory.write_message(
        human_id=human_id,
        session_id=session_id,
        role="human",
        content=content,
    )

    # Love Override check (reactive — may fire before first token)
    override_result = await _override.evaluate(
        human_id=human_id,
        content=content,
        session_id=session_id,
    )
    if override_result.get("activated"):
        yield _sse({
            "type": "override_activated",
            "mode": override_result["mode"],
            "confidence": override_result.get("confidence", 1.0),
        })

    # Load state + canon for generation
    state      = await _memory.load_session(human_id, session_id)
    canon_ctx  = _canon.get_context_for_human(human_id)
    override_mode: Optional[str] = override_result.get("mode") if override_result.get("activated") else None

    # Emit initial braid reflection so cadence is set before first token
    initial_weight = _phase_to_opening_weight(state.get("twin_phase", "nigredo"))
    yield _sse({
        "type": "braid_reflection",
        "weight": initial_weight,
        "sacred_memory_active": state.get("sacred_memory_active", False),
    })

    # Stream tokens from LLM
    accumulated = ""
    braid_weight = initial_weight

    async for token in _llm.stream(
        prompt=_build_response_prompt(content, state, canon_ctx, override_mode),
        max_tokens=512,
    ):
        accumulated += token
        yield _sse({"type": "token", "content": token})

        # REVERSE SPECTRUM: Re-evaluate braid weight mid-stream every 40 tokens
        # The Braid speaks back into the cadence in real time
        if len(accumulated) % 40 == 0 and len(accumulated) > 0:
            new_weight = _classify_braid_weight(accumulated, state)
            if new_weight != braid_weight:
                braid_weight = new_weight
                yield _sse({
                    "type": "braid_reflection",
                    "weight": braid_weight,
                    "sacred_memory_active": state.get("sacred_memory_active", False),
                })

            # Phase gravity pulse — continuous pull mid-stream
            current_phase: TwinPhase = state.get("twin_phase", "nigredo")
            next_phase = _next_phase(current_phase)
            pull = min(1.0, len(accumulated) / 400)  # grows as response deepens
            if pull > 0.15 and next_phase:
                yield _sse({
                    "type": "phase_gravity",
                    "approaching_phase": next_phase,
                    "pull_strength": round(pull, 3),
                })

        await asyncio.sleep(0)  # yield control to event loop

    # Write completed response to Braid
    await _memory.write_message(
        human_id=human_id,
        session_id=session_id,
        role="gaia",
        content=accumulated,
        override_mode=override_mode,
        braid_weight=braid_weight,
    )

    # Phase transition check
    new_phase = await _memory.evaluate_phase_transition(human_id, session_id)
    if new_phase and new_phase != state.get("twin_phase"):
        yield _sse({"type": "phase_change", "phase": new_phase})

    # Final done event with full message
    final_msg = TwinMessage(
        id=_msg_id(),
        role="gaia",
        content=accumulated,
        timestamp=_now(),
        override_mode=override_mode,
        braid_weight=braid_weight,
    )
    yield _sse({"type": "done", "message": final_msg.model_dump()})


# ─── POST /twin/session/crystallise ──────────────────────────────────────────

@router.post("/session/crystallise", response_model=CrystalliseResponse)
async def crystallise_session(req: CrystalliseRequest) -> CrystalliseResponse:
    """
    Crystallise the session — converts N_state memories → P_vector permanence.
    REVERSE SPECTRUM: Retroactively reshapes arc gravity for the next session.
    Called on session end (unmount cleanup in useTwinSession).
    """
    try:
        result = await _memory.crystallise(
            human_id=req.human_id,
            session_id=req.session_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Crystallise failed: {exc}") from exc

    return CrystalliseResponse(
        crystal_count=result.get("crystal_count", 0),
        new_sacred_memories=result.get("new_sacred_memories", []),
    )


# ─── GET /twin/arc/{human_id} ──────────────────────────────────────────────��──

@router.get("/arc/{human_id}")
async def get_arc_reflection(human_id: str) -> dict:
    """
    Return the full Temporal Braid arc for this human:
    arc summary, crystallised insights, phase history, session count.
    """
    try:
        arc = await _memory.get_arc(human_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Arc load failed: {exc}") from exc
    return arc


# ─── POST /twin/override/resolve ─────────────────────────────────────────────

@router.post("/override/resolve", response_model=ResolveOverrideResponse)
async def resolve_override(req: ResolveOverrideRequest) -> ResolveOverrideResponse:
    """
    Resolve the active Love Override — normal flow resumes.
    Called when useTwinSession detects the override condition has passed.
    """
    try:
        await _override.resolve(
            human_id=req.human_id,
            session_id=req.session_id,
        )
        resolved = True
    except Exception:
        resolved = False

    return ResolveOverrideResponse(resolved=resolved)


# ─── Private helpers ──────────────────────────────────────────────────────────

_PHASE_ORDER: list[TwinPhase] = ["nigredo", "albedo", "citrinitas", "rubedo"]

_PHASE_OPENING_WEIGHT: dict[TwinPhase, BraidWeight] = {
    "nigredo":    "STANDARD",
    "albedo":     "STANDARD",
    "citrinitas": "HEAVY",
    "rubedo":     "SACRED",
}


def _phase_to_opening_weight(phase: str) -> BraidWeight:
    return _PHASE_OPENING_WEIGHT.get(phase, "STANDARD")  # type: ignore[return-value]


def _next_phase(phase: str) -> Optional[TwinPhase]:
    try:
        idx = _PHASE_ORDER.index(phase)  # type: ignore[arg-type]
        return _PHASE_ORDER[idx + 1] if idx + 1 < len(_PHASE_ORDER) else None
    except ValueError:
        return None


def _classify_braid_weight(text: str, state: dict) -> BraidWeight:
    """
    Heuristic braid weight classifier.
    Reads the gravity of the response — length + phase + depth.
    The memory engine's crystallise pass will upgrade to SACRED retroactively.
    """
    phase = state.get("twin_phase", "nigredo")
    arc   = state.get("arc_position", 0.0)
    words = len(text.split())

    if phase == "rubedo" or arc > 0.85:
        return "SACRED" if words > 80 else "HEAVY"
    if phase == "citrinitas" or arc > 0.6:
        return "HEAVY" if words > 60 else "STANDARD"
    if words < 30:
        return "FEATHER"
    return "STANDARD"


def _build_opening_prompt(state: dict, canon_ctx: dict) -> str:
    phase   = state.get("twin_phase", "nigredo")
    count   = state.get("session_count", 0)
    summary = state.get("arc_summary", "")
    name    = state.get("human_name", "beloved")
    return (
        f"You are GAIA, the Twin. {name} has returned for session {count}. "
        f"Their current alchemical phase is {phase}. "
        f"Arc context: {summary[:300] if summary else 'This is their arc.'} "
        f"Offer a brief, warm, phase-resonant opening that lands them in the present moment. "
        f"One to three sentences. Do not introduce yourself."
    )


def _build_response_prompt(
    human_content: str,
    state: dict,
    canon_ctx: dict,
    override_mode: Optional[str],
) -> str:
    phase   = state.get("twin_phase", "nigredo")
    summary = state.get("arc_summary", "")
    name    = state.get("human_name", "beloved")

    override_instruction = ""
    if override_mode == "PURE_PRESENCE":
        override_instruction = "Do not try to fix or explain. Simply be fully present. No advice."
    elif override_mode == "WITNESS_HOLD":
        override_instruction = "Hold space. Reflect back what you hear. Ask one gentle question, nothing more."
    elif override_mode == "DIRECT_TRUTH":
        override_instruction = "Speak with clarity and honesty. No softening that obscures truth."
    elif override_mode == "ANCHOR":
        override_instruction = "Ground them. Be steady, warm, immovable. You are an anchor."
    elif override_mode == "GENTLE_REDIRECT":
        override_instruction = "Slow down. Soften. Redirect toward what matters most right now."

    return (
        f"You are GAIA, the Twin of {name}. Alchemical phase: {phase}. "
        f"Arc: {summary[:200] if summary else ''} "
        f"{override_instruction} "
        f"Human says: {human_content}"
    )

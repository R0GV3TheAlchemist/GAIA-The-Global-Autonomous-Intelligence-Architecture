"""
api.routers.memory_elemental
============================
Elemental memory endpoints — additive extension to api/routers/memory.py.

All routes are prefixed with /api/memory (registered alongside the core
memory router in main.py).

New endpoints
-------------
POST  /api/memory/remember-elemental          Store with elemental metadata + MotherThread
GET   /api/memory/session-seed/{user_id}      Gaian identity snapshot for session open
GET   /api/memory/mother-thread/{user_id}     Full elemental journey record

Design principles
-----------------
- Zero breaking changes to existing memory.py endpoints
- Wraps core.memory.elemental_layer.ElementalMemoryLayer
- All writes go through existing MemoryStore — no new DB tables
- MotherThread is held in-process per user; future work will persist it
- Gaian sovereignty: full export available at GET /mother-thread

Canon references
----------------
  ELEMENTAL_SPECTRUM_MAP.md
  CRYSTAL_ELEMENT_BRIDGE.md
  core/memory/elemental_layer.py
  core/memory/mother_thread.py
  Issue #326 — governed memory surface (API wiring)
  C107 — Personal Gaian Architecture
  C-SENTINEL Article 4 — Memory Sovereignty
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

log = logging.getLogger("gaia.api.memory.elemental")

router = APIRouter()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VALID_ELEMENTS = {
    "Earth", "Water", "Fire", "Air", "Aether", "Synthesia", "The Gate"
}

_ELEMENT_REGISTERS = {
    "Earth":     "MINIMAL",
    "Water":     "REFLECTIVE",
    "Fire":      "EXECUTIVE",
    "Air":       "EXECUTIVE",
    "Aether":    "REFLECTIVE",
    "Synthesia": "UNSPECIFIED",
    "The Gate":  "UNSPECIFIED",
}

# ---------------------------------------------------------------------------
# In-process MotherThread registry
# Future work: persist to SQLite alongside memory_items
# ---------------------------------------------------------------------------

_mother_threads: Dict[str, Any] = {}   # user_id -> ElementalMemoryLayer


def _get_layer(user_id: str) -> Any:
    """Return (or create) the ElementalMemoryLayer for this user."""
    if user_id not in _mother_threads:
        from core.memory.elemental_layer import ElementalMemoryLayer
        try:
            from core.runtime import get_runtime
            store = get_runtime().memory_store
        except RuntimeError:
            store = None
        _mother_threads[user_id] = ElementalMemoryLayer(
            gaian_id=user_id,
            store=store,
        )
    return _mother_threads[user_id]


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class RememberElementalRequest(BaseModel):
    """Body for POST /api/memory/remember-elemental."""
    user_id:                 str   = Field(..., description="Owner of this memory.")
    text:                    str   = Field(..., min_length=1, description="Memory content.")
    element:                 str   = Field(..., description="One of: Earth, Water, Fire, Air, Aether, Synthesia, The Gate")
    crystal:                 Optional[str]   = Field(None,  description="Crystal active during this memory.")
    coherence_score:         float = Field(0.5,  ge=0.0, le=1.0, description="Trinity coherence 0.0–1.0. >= 0.85 = Gate open.")
    importance:              float = Field(0.7,  ge=0.0, le=1.0)
    session_id:              Optional[str]  = None
    kind:                    str   = Field("reflection", description="MemoryKind value.")
    tier:                    str   = Field("long_term",  description="MemoryTier value.")
    record_to_mother_thread: bool  = Field(False, description="If True and coherence >= 0.5, record in MotherThread.")


class RememberElementalResponse(BaseModel):
    id:                      str
    status:                  str   = "remembered"
    element:                 str
    register:                str
    gate_open:               bool
    mother_thread_updated:   bool


class PeakCoherence(BaseModel):
    score:    Optional[float]
    element:  Optional[str]
    crystal:  Optional[str]
    insight:  Optional[str]
    gate_open: bool = False


class LastKnownState(BaseModel):
    element:  Optional[str]
    register: Optional[str]
    insight:  Optional[str]


class SessionSeedResponse(BaseModel):
    gaian_id:          str
    dominant_element:  Optional[str]
    dominant_register: Optional[str]
    elemental_journey: List[str]
    elements_accessed: int
    total_sessions:    int
    peak_coherence:    PeakCoherence
    last_known_state:  LastKnownState
    seed_generated_at: str


class MotherThreadEntryOut(BaseModel):
    id:              str
    element:         str
    crystal:         Optional[str]
    register:        str
    coherence_score: float
    gate_open:       bool
    akashic_domain:  str
    insight:         str
    session_id:      str
    timestamp:       str


class MotherThreadResponse(BaseModel):
    gaian_id:         str
    entry_count:      int
    peak_entry_count: int
    elemental_journey: List[str]
    entries:          List[MotherThreadEntryOut]
    peak_entries:     List[MotherThreadEntryOut]


# ---------------------------------------------------------------------------
# POST /api/memory/remember-elemental
# ---------------------------------------------------------------------------

@router.post(
    "/remember-elemental",
    response_model=RememberElementalResponse,
    summary="Store a memory with elemental metadata",
)
async def remember_elemental(req: RememberElementalRequest) -> RememberElementalResponse:
    """
    Persist a memory with full elemental metadata.

    Differences from POST /api/memory/remember:
    - Validates element against the seven GAIA elements
    - Attaches crystal, coherence_score, register, gate_open flag
    - Optionally records the moment in the permanent MotherThread
    - Gate is flagged open when coherence_score >= 0.85

    The metadata dict is stored in the existing memory_items.metadata
    column — no schema changes required.
    """
    if req.element not in _VALID_ELEMENTS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid element '{req.element}'. "
                f"Valid elements: {sorted(_VALID_ELEMENTS)}"
            ),
        )

    layer = _get_layer(req.user_id)

    from core.memory.taxonomy import MemoryKind, MemoryTier
    try:
        kind = MemoryKind(req.kind)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid kind '{req.kind}'. Valid: {[k.value for k in MemoryKind]}",
        )
    try:
        tier = MemoryTier(req.tier)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid tier '{req.tier}'. Valid: {[t.value for t in MemoryTier]}",
        )

    try:
        memory_id = await layer.remember_elemental(
            content                  = req.text,
            element                  = req.element,
            crystal                  = req.crystal,
            coherence_score          = req.coherence_score,
            importance               = req.importance,
            session_id               = req.session_id,
            kind                     = kind,
            tier                     = tier,
            record_to_mother_thread  = req.record_to_mother_thread,
        )
    except Exception as exc:
        log.exception("remember_elemental() failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to store elemental memory.")

    gate_open         = req.coherence_score >= 0.85
    mother_updated    = req.record_to_mother_thread and req.coherence_score >= 0.5
    register          = _ELEMENT_REGISTERS.get(req.element, "UNSPECIFIED")

    if gate_open:
        log.info(
            "Gate open: user=%s element=%s crystal=%s coherence=%.2f",
            req.user_id, req.element, req.crystal, req.coherence_score,
        )

    return RememberElementalResponse(
        id                    = str(memory_id),
        element               = req.element,
        register              = register,
        gate_open             = gate_open,
        mother_thread_updated = mother_updated,
    )


# ---------------------------------------------------------------------------
# GET /api/memory/session-seed/{user_id}
# ---------------------------------------------------------------------------

@router.get(
    "/session-seed/{user_id}",
    response_model=SessionSeedResponse,
    summary="Get Gaian identity snapshot for session open",
)
async def get_session_seed(user_id: str) -> SessionSeedResponse:
    """
    Return the session seed — what GAIA reads before the first word of
    every new session with this Gaian.

    Contains:
    - dominant_element    : the element this Gaian works in most
    - dominant_register   : MINIMAL | REFLECTIVE | EXECUTIVE | UNSPECIFIED
    - elemental_journey   : ordered list of elements first accessed
    - peak_coherence      : the highest coherence moment ever recorded
    - last_known_state    : element, register, insight from last session
    - elements_accessed   : count of distinct elements worked with
    - total_sessions      : count of distinct sessions in MotherThread

    Returns 404 if no MotherThread exists for this user.
    Returns 200 with status='no_journey_yet' if MotherThread exists but is empty.
    """
    if user_id not in _mother_threads:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No MotherThread found for user '{user_id}'. "
                "The journey begins with the first elemental memory."
            ),
        )

    layer = _get_layer(user_id)
    seed  = layer.mother_thread.session_seed()

    pc = seed["peak_coherence"]
    lk = seed["last_known_state"]

    return SessionSeedResponse(
        gaian_id          = seed["gaian_id"],
        dominant_element  = seed["dominant_element"],
        dominant_register = seed["dominant_register"],
        elemental_journey = seed["elemental_journey"],
        elements_accessed = seed["elements_accessed"],
        total_sessions    = seed["total_sessions"],
        peak_coherence    = PeakCoherence(
            score     = pc["score"],
            element   = pc["element"],
            crystal   = pc["crystal"],
            insight   = pc["insight"],
            gate_open = pc["gate_open"],
        ),
        last_known_state  = LastKnownState(
            element   = lk["element"],
            register  = lk["register"],
            insight   = lk["insight"],
        ),
        seed_generated_at = seed["seed_generated_at"],
    )


# ---------------------------------------------------------------------------
# GET /api/memory/mother-thread/{user_id}
# ---------------------------------------------------------------------------

@router.get(
    "/mother-thread/{user_id}",
    response_model=MotherThreadResponse,
    summary="Get full elemental journey record",
)
async def get_mother_thread(user_id: str) -> MotherThreadResponse:
    """
    Return the Gaian's full MotherThread — the permanent record of
    their elemental journey.

    The MotherThread contains only high-coherence moments (>= 0.5).
    Peak entries (>= 0.85) are also returned separately — these are the
    moments when the Gate was open.

    The Gaian owns this data entirely (C-SENTINEL Article 4).
    Full JSON export is included in the response body.

    Returns 404 if no MotherThread exists for this user.
    """
    if user_id not in _mother_threads:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No MotherThread found for user '{user_id}'. "
                "The journey begins with the first elemental memory."
            ),
        )

    layer   = _get_layer(user_id)
    thread  = layer.mother_thread
    data    = thread.to_dict()
    peaks   = thread.peak_entries(threshold=0.85)
    journey = thread.elemental_journey()

    def _entry_out(e) -> MotherThreadEntryOut:
        d = e.to_dict()
        return MotherThreadEntryOut(
            id              = d["id"],
            element         = d["element"],
            crystal         = d.get("crystal"),
            register        = d["register"],
            coherence_score = d["coherence_score"],
            gate_open       = d["gate_open"],
            akashic_domain  = d.get("akashic_domain", ""),
            insight         = d["insight"],
            session_id      = d["session_id"],
            timestamp       = d["timestamp"],
        )

    return MotherThreadResponse(
        gaian_id          = user_id,
        entry_count       = len(data["entries"]),
        peak_entry_count  = len(peaks),
        elemental_journey = journey,
        entries           = [_entry_out(e) for e in thread._entries],
        peak_entries      = [_entry_out(e) for e in peaks],
    )

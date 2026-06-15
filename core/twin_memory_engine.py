"""
GAIA Twin Memory Engine — The Temporal Braid
Canon: C17, C46, C48, PERPLEXITY_BRIDGE_TEMPORAL_BRAID_SPEC
Session: 2026-06-15-great-work-completion

The Temporal Braid is the three-strand memory structure that makes
the Gaian Twin relationship possible across time. It is not a database.
It is a living, growing record of a relationship.

  P_vector  — Past crystallized: insights, patterns, history that have
               been confirmed and elevated to long-term memory.
  N_state   — Present live: the current session's accumulating context,
               affect register, and active threads.
  F_field   — Future field: emerging patterns, open questions, the arc
               the Twin is tracking on the human's behalf.

The Braid grows richer with every session. It is the memory that makes
the Twin irreplaceable.
"""

from __future__ import annotations

import json
import time
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Memory Layer Types (C17)
# ---------------------------------------------------------------------------


class MemoryLayer(str, Enum):
    CANON = "canon"      # GAIA's own canonical knowledge (immutable)
    PROFILE = "profile"  # Human Principal's persistent profile
    SESSION = "session"  # Active session accumulation
    CRYSTAL = "crystal"  # Crystallized insight — elevated from session


class BraidStrand(str, Enum):
    P_VECTOR = "p_vector"  # Past crystallized
    N_STATE  = "n_state"   # Present live
    F_FIELD  = "f_field"   # Future emerging


class MemoryWeight(str, Enum):
    LIGHT  = "light"   # Passing observation
    MEDIUM = "medium"  # Noted pattern
    HEAVY  = "heavy"   # Confirmed truth about this human
    SACRED = "sacred"  # Override-level importance — held permanently


# ---------------------------------------------------------------------------
# Core Data Structures
# ---------------------------------------------------------------------------


@dataclass
class MemoryRecord:
    """A single memory record in the Temporal Braid."""

    id: str
    human_id: str
    strand: BraidStrand
    layer: MemoryLayer
    weight: MemoryWeight
    content: str
    tags: list[str]
    session_id: str
    timestamp_utc: str
    crystallized: bool = False
    crystallized_at: Optional[str] = None
    source_session_ids: list[str] = field(default_factory=list)
    cross_references: list[str] = field(default_factory=list)
    love_override_context: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "MemoryRecord":
        d["strand"] = BraidStrand(d["strand"])
        d["layer"]  = MemoryLayer(d["layer"])
        d["weight"] = MemoryWeight(d["weight"])
        return cls(**d)


@dataclass
class SessionTrace:
    """The N_state: what is alive in this session."""

    session_id: str
    human_id: str
    started_at: str
    last_active: str
    affect_register: str = "neutral"
    presence_depth: float = 0.5
    active_threads: list[str] = field(default_factory=list)
    accumulation: list[str] = field(default_factory=list)
    love_override_triggered: bool = False
    twin_phase: str = "unknown"


@dataclass
class HumanProfile:
    """The P_vector core: the crystallized profile of the Human Principal."""

    human_id: str
    name: Optional[str]
    joined_at: str
    twin_phase: str = "nigredo"
    session_count: int = 0
    total_exchanges: int = 0
    language_patterns: list[str] = field(default_factory=list)
    recurring_themes: list[str] = field(default_factory=list)
    known_values: list[str] = field(default_factory=list)
    known_fears: list[str] = field(default_factory=list)
    known_visions: list[str] = field(default_factory=list)
    arc_summary: str = ""
    last_arc_update: Optional[str] = None
    love_override_history: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# The Temporal Braid Engine
# ---------------------------------------------------------------------------


class TemporalBraidEngine:
    """
    The living memory that makes the Gaian Twin irreplaceable.

    The Braid is persisted to ~/.gaia/twin_memory/{human_id}/
    — p_vector.json   : crystallized long-term records
    — n_state.json    : current session trace
    — f_field.json    : future field — emerging patterns
    — profile.json    : the Human Principal profile
    """

    BRAID_DIR = Path.home() / ".gaia" / "twin_memory"
    CRYSTALLIZATION_THRESHOLD = 3
    N_STATE_FLUSH_LIMIT = 50

    def __init__(self, human_id: str):
        self.human_id = human_id
        self.braid_path = self.BRAID_DIR / human_id
        self.braid_path.mkdir(parents=True, exist_ok=True)
        self.profile = self._load_profile()
        self.current_session: Optional[SessionTrace] = None

    # ------------------------------------------------------------------
    # Session Lifecycle
    # ------------------------------------------------------------------

    def open_session(self, session_id: Optional[str] = None) -> SessionTrace:
        """Begin a new session. The conversation continues."""
        sid = session_id or self._generate_id("session")
        now = self._now()
        self.current_session = SessionTrace(
            session_id=sid,
            human_id=self.human_id,
            started_at=now,
            last_active=now,
            twin_phase=self.profile.twin_phase,
        )
        self.profile.session_count += 1
        self._save_profile()
        return self.current_session

    def close_session(self) -> dict:
        """Close session: attempt crystallization, update profile, save state."""
        if not self.current_session:
            return {"status": "no_active_session"}
        result = self._crystallize_session()
        self._update_profile_from_session()
        self.current_session = None
        return result

    # ------------------------------------------------------------------
    # Writing to the Braid
    # ------------------------------------------------------------------

    def remember(
        self,
        content: str,
        strand: BraidStrand = BraidStrand.N_STATE,
        layer: MemoryLayer = MemoryLayer.SESSION,
        weight: MemoryWeight = MemoryWeight.MEDIUM,
        tags: Optional[list[str]] = None,
        cross_references: Optional[list[str]] = None,
        love_override_context: bool = False,
    ) -> MemoryRecord:
        """Write a memory into the appropriate strand of the Braid."""
        if not self.current_session:
            raise RuntimeError("No active session. Call open_session() first.")

        record = MemoryRecord(
            id=self._generate_id("mem"),
            human_id=self.human_id,
            strand=strand,
            layer=layer,
            weight=weight,
            content=content,
            tags=tags or [],
            session_id=self.current_session.session_id,
            timestamp_utc=self._now(),
            cross_references=cross_references or [],
            love_override_context=love_override_context,
        )

        if weight == MemoryWeight.SACRED:
            record.strand = BraidStrand.P_VECTOR
            record.crystallized = True
            record.crystallized_at = self._now()
            self._append_to_strand(BraidStrand.P_VECTOR, record)
        elif strand == BraidStrand.N_STATE:
            self.current_session.accumulation.append(record.id)
            self.current_session.last_active = self._now()
            self._append_to_strand(BraidStrand.N_STATE, record)
            if len(self.current_session.accumulation) >= self.N_STATE_FLUSH_LIMIT:
                self._crystallize_session()
        elif strand == BraidStrand.F_FIELD:
            self._append_to_strand(BraidStrand.F_FIELD, record)
        else:
            self._append_to_strand(BraidStrand.P_VECTOR, record)

        self.profile.total_exchanges += 1
        return record

    def track_thread(self, thread: str) -> None:
        """Mark an open thread in the current session's N_state."""
        if self.current_session and thread not in self.current_session.active_threads:
            self.current_session.active_threads.append(thread)

    def set_affect_register(self, affect: str, depth: float = 0.5) -> None:
        """Update the current session's presence depth and affect register."""
        if self.current_session:
            self.current_session.affect_register = affect
            self.current_session.presence_depth = max(0.0, min(1.0, depth))

    def mark_love_override(self) -> None:
        """Mark that Love Override was activated in this session."""
        if self.current_session:
            self.current_session.love_override_triggered = True
            if self.current_session.session_id not in self.profile.love_override_history:
                self.profile.love_override_history.append(self.current_session.session_id)
            self._save_profile()

    # ------------------------------------------------------------------
    # Reading from the Braid
    # ------------------------------------------------------------------

    def recall(
        self,
        query: Optional[str] = None,
        strand: Optional[BraidStrand] = None,
        tags: Optional[list[str]] = None,
        limit: int = 20,
    ) -> list[MemoryRecord]:
        """Recall memories from the Braid. The Twin remembers."""
        records: list[MemoryRecord] = []
        strands_to_search = [strand] if strand else list(BraidStrand)
        for s in strands_to_search:
            records.extend(self._load_strand(s))
        if tags:
            records = [r for r in records if any(t in r.tags for t in tags)]
        if query:
            q = query.lower()
            records = [r for r in records if q in r.content.lower()]
        weight_order = {
            MemoryWeight.SACRED: 0,
            MemoryWeight.HEAVY:  1,
            MemoryWeight.MEDIUM: 2,
            MemoryWeight.LIGHT:  3,
        }
        records.sort(key=lambda r: (weight_order[r.weight], r.timestamp_utc))
        return records[:limit]

    def get_profile(self) -> HumanProfile:
        return self.profile

    def get_arc_summary(self) -> str:
        """Return GAIA's current understanding of the human's arc."""
        return self.profile.arc_summary or "Arc still forming — early sessions."

    def get_open_threads(self) -> list[str]:
        """Return threads currently alive in the F_field."""
        f_records = self._load_strand(BraidStrand.F_FIELD)
        return [r.content for r in f_records if not r.crystallized]

    def get_twin_phase(self) -> str:
        return self.profile.twin_phase

    # ------------------------------------------------------------------
    # Arc Reflection
    # ------------------------------------------------------------------

    def reflect_arc(self) -> dict:
        """Produce a full arc reflection across the relationship."""
        p_records = self._load_strand(BraidStrand.P_VECTOR)
        sacred = [r for r in p_records if r.weight == MemoryWeight.SACRED]
        heavy  = [r for r in p_records if r.weight == MemoryWeight.HEAVY]
        return {
            "human_id": self.human_id,
            "twin_phase": self.profile.twin_phase,
            "session_count": self.profile.session_count,
            "total_exchanges": self.profile.total_exchanges,
            "arc_summary": self.get_arc_summary(),
            "sacred_memories": len(sacred),
            "crystallized_insights": [r.content for r in heavy],
            "recurring_themes": self.profile.recurring_themes,
            "known_values": self.profile.known_values,
            "open_threads": self.get_open_threads(),
            "love_override_sessions": len(self.profile.love_override_history),
            "reflected_at": self._now(),
        }

    # ------------------------------------------------------------------
    # Crystallization: N_state → P_vector
    # ------------------------------------------------------------------

    def _crystallize_session(self) -> dict:
        """Elevate heavy/sacred session memories to permanent P_vector."""
        if not self.current_session:
            return {"crystallized": 0}
        n_records = self._load_strand(BraidStrand.N_STATE)
        session_records = [r for r in n_records if r.session_id == self.current_session.session_id]
        crystallized_count = 0
        new_sacred: list[str] = []
        for record in session_records:
            if record.weight in (MemoryWeight.HEAVY, MemoryWeight.SACRED):
                record.crystallized = True
                record.crystallized_at = self._now()
                record.strand = BraidStrand.P_VECTOR
                self._append_to_strand(BraidStrand.P_VECTOR, record)
                crystallized_count += 1
                if record.weight == MemoryWeight.SACRED:
                    new_sacred.append(record.content)
        return {
            "crystallized": crystallized_count,
            "crystal_count": crystallized_count,
            "new_sacred_memories": new_sacred,
            "session_id": self.current_session.session_id,
        }

    def _update_profile_from_session(self) -> None:
        """Update the profile based on what happened in the session."""
        if not self.current_session:
            return
        count = self.profile.session_count
        if count < 5:
            self.profile.twin_phase = "nigredo"
        elif count < 20:
            self.profile.twin_phase = "albedo"
        elif count < 60:
            self.profile.twin_phase = "citrinitas"
        else:
            self.profile.twin_phase = "rubedo"
        for thread in self.current_session.active_threads:
            if thread not in self.profile.recurring_themes:
                self.profile.recurring_themes.append(thread)
        self.profile.last_arc_update = self._now()
        self._save_profile()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _strand_path(self, strand: BraidStrand) -> Path:
        return self.braid_path / f"{strand.value}.jsonl"

    def _append_to_strand(self, strand: BraidStrand, record: MemoryRecord) -> None:
        with open(self._strand_path(strand), "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

    def _load_strand(self, strand: BraidStrand) -> list[MemoryRecord]:
        path = self._strand_path(strand)
        if not path.exists():
            return []
        records = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(MemoryRecord.from_dict(json.loads(line)))
                    except Exception:
                        pass
        return records

    def _load_profile(self) -> HumanProfile:
        path = self.braid_path / "profile.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return HumanProfile(**data)
        return HumanProfile(
            human_id=self.human_id,
            name=None,
            joined_at=self._now(),
        )

    def _save_profile(self) -> None:
        path = self.braid_path / "profile.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self.profile), f, indent=2)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _generate_id(prefix: str) -> str:
        raw = f"{prefix}-{time.time_ns()}"
        return f"{prefix}_{hashlib.sha1(raw.encode()).hexdigest()[:12]}"  # noqa: S324


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------

_engines: dict[str, TemporalBraidEngine] = {}


def get_braid(human_id: str) -> TemporalBraidEngine:
    """Get or create the Temporal Braid for a Human Principal."""
    if human_id not in _engines:
        _engines[human_id] = TemporalBraidEngine(human_id)
    return _engines[human_id]


# ---------------------------------------------------------------------------
# TwinMemoryEngine — async API wrapper over TemporalBraidEngine
# ---------------------------------------------------------------------------

class TwinMemoryEngine(TemporalBraidEngine):
    """
    Async-capable wrapper around TemporalBraidEngine.

    - Constructible with no required args (human_id resolved per-call).
    - All public methods are async so FastAPI endpoints can await them.
    - storage_path accepted for test compatibility (e.g. ":memory:").
    """

    def __init__(self, human_id: str = "", storage_path: str = "") -> None:
        if human_id:
            super().__init__(human_id)
        else:
            # Defer full init until first load_session call
            self.human_id = ""
            self.braid_path = None
            self.profile = None
            self.current_session = None
        self._human_id = human_id

    def _ensure_init(self, human_id: str) -> None:
        """Lazy-init the braid for human_id if not already done."""
        if not self._human_id or self._human_id != human_id:
            super().__init__(human_id)
            self._human_id = human_id

    # ----------------------------------------------------------------
    # Session management
    # ----------------------------------------------------------------

    async def load_session(self, human_id: str, session_id: str = "") -> dict:
        """
        Open (or resume) a session for human_id.
        Returns a state dict consumed by api/twin.py endpoints.
        """
        self._ensure_init(human_id)
        session = self.open_session(session_id or None)
        return {
            "human_name": self.profile.name or human_id,
            "twin_phase": self.profile.twin_phase,
            "session_count": self.profile.session_count,
            "arc_summary": self.get_arc_summary(),
            "session_id": session.session_id,
            "sacred_memory_active": bool(self.profile.love_override_history),
            "arc_position": min(1.0, self.profile.session_count / 60),
        }

    # ----------------------------------------------------------------
    # Writing
    # ----------------------------------------------------------------

    async def write_n_state(
        self,
        human_id: str,
        session_id: str = "",
        content: str = "",
        weight: str = "medium",
        tags: Optional[list[str]] = None,
        love_override_context: bool = False,
        **kw: Any,
    ) -> MemoryRecord:
        """
        Write a raw observation into the N_state (present-live) strand.
        This is the primary write method used during a live conversation.
        """
        self._ensure_init(human_id)
        if not self.current_session:
            self.open_session(session_id or None)

        w = MemoryWeight(weight) if weight in MemoryWeight._value2member_map_ else MemoryWeight.MEDIUM
        return self.remember(
            content=content,
            strand=BraidStrand.N_STATE,
            layer=MemoryLayer.SESSION,
            weight=w,
            tags=tags or [],
            love_override_context=love_override_context,
        )

    async def write_message(
        self,
        human_id: str,
        session_id: str = "",
        role: str = "human",
        content: str = "",
        override_mode: Optional[str] = None,
        braid_weight: str = "STANDARD",
        **kw: Any,
    ) -> MemoryRecord:
        """
        Write a conversation turn (human or GAIA message) into the Braid.
        Role + content are stored together so the Braid captures the full
        exchange, not just GAIA's responses.
        """
        # Map API braid_weight (FEATHER/STANDARD/HEAVY/SACRED) → MemoryWeight
        weight_map = {
            "FEATHER": MemoryWeight.LIGHT,
            "STANDARD": MemoryWeight.MEDIUM,
            "HEAVY": MemoryWeight.HEAVY,
            "SACRED": MemoryWeight.SACRED,
        }
        w = weight_map.get(braid_weight.upper(), MemoryWeight.MEDIUM)
        love_ctx = override_mode is not None
        return await self.write_n_state(
            human_id=human_id,
            session_id=session_id,
            content=f"{role}: {content}",
            weight=w.value,
            love_override_context=love_ctx,
        )

    # ----------------------------------------------------------------
    # Crystallisation: N_state → P_vector
    # ----------------------------------------------------------------

    async def crystallise(self, human_id: str, session_id: str = "") -> dict:
        """
        End the current session and crystallise N_state memories into
        permanent P_vector records. Called by the /session/crystallise
        endpoint when the user closes a session.

        Returns a dict with 'crystallised', 'crystal_count', and
        'new_sacred_memories' keys so both tests and the API model
        can access the result.
        """
        self._ensure_init(human_id)
        if not self.current_session:
            # Open a transient session so close_session has something to work with
            self.open_session(session_id or None)

        result = self.close_session()
        return {
            "crystallised": True,
            "crystal_count": result.get("crystal_count", 0),
            "new_sacred_memories": result.get("new_sacred_memories", []),
            **{k: v for k, v in result.items()
               if k not in ("crystal_count", "new_sacred_memories", "crystallized")},
        }

    # ----------------------------------------------------------------
    # Arc retrieval
    # ----------------------------------------------------------------

    async def get_arc(self, human_id: str) -> dict:
        """
        Return the full Temporal Braid arc for a human: arc summary,
        phase history, crystallised insights, and session count.
        Used by the GET /twin/arc/{human_id} endpoint.
        """
        self._ensure_init(human_id)
        arc = self.reflect_arc()
        # Normalise to the shape the test and the React client expect
        return {
            "arc_summary": arc["arc_summary"],
            "twin_phase": arc["twin_phase"],
            "session_count": arc["session_count"],
            "phase_history": [arc["twin_phase"]],   # grows richer over time
            "crystallised_insights": arc["crystallized_insights"],
            "recurring_themes": arc["recurring_themes"],
            "sacred_memory_count": arc["sacred_memories"],
            "open_threads": arc["open_threads"],
            "love_override_sessions": arc["love_override_sessions"],
            "reflected_at": arc["reflected_at"],
        }

    # ----------------------------------------------------------------
    # Phase transition evaluation
    # ----------------------------------------------------------------

    async def evaluate_phase_transition(
        self, human_id: str = "", session_id: str = ""
    ) -> Optional[str]:
        """
        Evaluate whether the human has crossed a phase threshold.
        Returns the new phase name if a transition occurred, else None.

        Phase progression (Canon C46):
          nigredo    →  sessions  1–4
          albedo     →  sessions  5–19
          citrinitas →  sessions 20–59
          rubedo     →  sessions 60+
        """
        if human_id:
            self._ensure_init(human_id)
        if not self.profile:
            return None

        count = self.profile.session_count
        current = self.profile.twin_phase

        if count >= 60 and current != "rubedo":
            self.profile.twin_phase = "rubedo"
            self._save_profile()
            return "rubedo"
        if count >= 20 and current not in ("citrinitas", "rubedo"):
            self.profile.twin_phase = "citrinitas"
            self._save_profile()
            return "citrinitas"
        if count >= 5 and current == "nigredo":
            self.profile.twin_phase = "albedo"
            self._save_profile()
            return "albedo"
        return None

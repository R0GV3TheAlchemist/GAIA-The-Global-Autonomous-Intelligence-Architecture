"""
PersonaTracer — writes and reads PersonaTrace entries in SovereignMemory.

A PersonaTrace is a session-scoped snapshot of how the Gaian presented:
archetype, drift events, average similarity, total turns. Written at
session end; read at session start to maintain persona continuity.

Issue: #115
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Optional

from .types import DriftEvent, PersonaTrace

logger = logging.getLogger("gaia.persona.tracer")

# Memory tag used to identify persona trace entries
PERSONA_TRACE_TAG = "persona_trace"


class PersonaTracer:
    """
    Serialises PersonaTrace objects to / from SovereignMemory.

    Parameters
    ----------
    memory : SovereignMemory
        The shared SovereignMemory instance (injected at startup).
    """

    def __init__(self, memory) -> None:  # type: ignore[type-arg]
        self._memory = memory

    # ── Public API ────────────────────────────────────────────────────────────

    def write_trace(
        self,
        archetype_id: str,
        drift_events: list[DriftEvent],
        total_turns: int,
        avg_similarity: float,
        session_id: Optional[str] = None,
        started_at: Optional[float] = None,
        notes: str = "",
    ) -> PersonaTrace:
        """
        Serialise and store a PersonaTrace in SovereignMemory.

        Returns the stored PersonaTrace for confirmation.
        """
        now = time.time()
        trace = PersonaTrace(
            session_id=session_id or str(uuid.uuid4()),
            archetype_id=archetype_id,
            started_at=started_at or now,
            ended_at=now,
            drift_events=drift_events,
            total_turns=total_turns,
            avg_similarity=avg_similarity,
            notes=notes,
        )

        content = json.dumps({
            "session_id":    trace.session_id,
            "archetype_id": trace.archetype_id,
            "started_at":   trace.started_at,
            "ended_at":     trace.ended_at,
            "total_turns":  trace.total_turns,
            "avg_similarity": trace.avg_similarity,
            "drift_count":  trace.drift_count,
            "drift_events": [
                {
                    "timestamp":       e.timestamp,
                    "archetype_id":    e.archetype_id,
                    "similarity_score": e.similarity_score,
                    "turn_index":      e.turn_index,
                    "trigger":         e.trigger,
                }
                for e in drift_events
            ],
            "notes": notes,
        })

        self._memory.store_episode(
            content=content,
            episode_type=PERSONA_TRACE_TAG,
            tags=[PERSONA_TRACE_TAG, archetype_id],
        )

        logger.info(
            "PersonaTrace written — session=%s archetype=%s turns=%d drifts=%d avg_sim=%.4f",
            trace.session_id, archetype_id, total_turns, trace.drift_count, avg_similarity,
        )
        return trace

    def read_latest_trace(self, archetype_id: Optional[str] = None) -> Optional[PersonaTrace]:
        """
        Retrieve the most recent PersonaTrace from SovereignMemory.

        Optionally filter by archetype_id.
        """
        try:
            results = self._memory.search_memory(
                query=f"persona_trace {archetype_id or ''}".strip(),
                limit=5,
                memory_types=[PERSONA_TRACE_TAG],
            )
        except Exception as exc:
            logger.warning("Failed to read persona traces: %s", exc)
            return None

        for record in results:
            try:
                data = json.loads(record.get("content", "{}"))
                if archetype_id and data.get("archetype_id") != archetype_id:
                    continue
                drift_events = [
                    DriftEvent(
                        timestamp=e["timestamp"],
                        archetype_id=e["archetype_id"],
                        similarity_score=e["similarity_score"],
                        turn_index=e["turn_index"],
                        trigger=e["trigger"],
                    )
                    for e in data.get("drift_events", [])
                ]
                return PersonaTrace(
                    session_id=data["session_id"],
                    archetype_id=data["archetype_id"],
                    started_at=data["started_at"],
                    ended_at=data["ended_at"],
                    drift_events=drift_events,
                    total_turns=data.get("total_turns", 0),
                    avg_similarity=data.get("avg_similarity", 1.0),
                    notes=data.get("notes", ""),
                )
            except (KeyError, json.JSONDecodeError) as exc:
                logger.debug("Skipping malformed trace record: %s", exc)
                continue

        return None

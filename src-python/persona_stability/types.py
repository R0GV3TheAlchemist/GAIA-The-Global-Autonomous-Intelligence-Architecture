"""
Persona Stability — core types.

All dataclasses are JSON-serialisable (use dataclasses.asdict for storage).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class PersonaAnchor:
    """
    Compressed 3-5 sentence essence of a Gaian archetype.
    Injected into the LLM context window every N turns to prevent drift.
    """
    archetype_id: str          # e.g. "sage", "lover", "warrior"
    essence: str               # compressed anchor text (3-5 sentences)
    voice_baseline: list[float] = field(default_factory=list)  # embedding vector


@dataclass
class DriftEvent:
    """
    Logged when cosine similarity between a response and the voice baseline
    drops below the drift threshold.
    """
    timestamp: float
    archetype_id: str
    similarity_score: float    # 0.0 – 1.0; below threshold = drift
    turn_index: int
    trigger: str               # "similarity_drop" | "affect_intensity"


@dataclass
class AnchorInjectionResult:
    """
    Returned by AnchorInjector.should_inject() to describe the injection decision.
    """
    should_inject: bool
    reason: str                # "scheduled" | "drift_detected" | "affect_intensity" | "none"
    anchor_text: Optional[str] = None
    turn_index: int = 0


@dataclass
class PersonaTrace:
    """
    Snapshot of how the Gaian presented during a session.
    Written to SovereignMemory at session end; read at session start
    to maintain persona continuity across sessions.
    """
    session_id: str
    archetype_id: str
    started_at: float
    ended_at: float
    drift_events: list[DriftEvent] = field(default_factory=list)
    total_turns: int = 0
    avg_similarity: float = 1.0
    notes: str = ""

    @property
    def drift_count(self) -> int:
        return len(self.drift_events)

    @property
    def duration_minutes(self) -> float:
        return (self.ended_at - self.started_at) / 60.0

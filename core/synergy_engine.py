"""
core/synergy_engine.py
======================
Synergy Engine — Canon C32 (Elemental Codex) integration layer.

Orchestrates the cross-engine "plan" step: gathers readings from all
active sub-engines (Vitality, Codex Stage, Resonance, Shadow), resolves
canon-level conflicts, and returns a unified SynergyReading used by
GAIANRuntime to shape the final response.

Canon Refs: C32 (Elemental Codex), C40 (Mentalism), C10 (Alchemical Codex)

Public API
----------
SynergyEngine          — main orchestrator class
SynergyReading         — immutable result snapshot produced each turn
SynergyState           — mutable per-session accumulator
blank_synergy_state()  — factory returning a fresh SynergyState
_analyse_canon_context() — internal helper, exported for testing
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class SynergyReading:
    """
    Immutable snapshot of the Synergy Engine's output for a single turn.

    Consumed by GAIANRuntime to determine response depth, canon alignment
    weight, and shadow-integration priority.
    """

    # Overall coherence score 0-1 (1 = fully aligned across all engines)
    coherence:           float = 1.0

    # Dominant canon reference triggered this turn (e.g. "C32", "C10")
    dominant_canon:      str   = ""

    # Resolved conflict summary (empty string = no conflict)
    conflict_summary:    str   = ""

    # Per-engine contribution scores {engine_name: 0-1}
    engine_scores:       Dict[str, float] = field(default_factory=dict)

    # Canon context tags extracted from the user turn
    canon_tags:          List[str] = field(default_factory=list)

    # Human-readable one-line synthesis for logging / debug
    synthesis_note:      str   = ""

    # Raw context dict passed into the engine (for tracing)
    raw_context:         Dict[str, Any] = field(default_factory=dict)


@dataclass
class SynergyState:
    """
    Mutable per-session accumulator for Synergy Engine history.

    Reset per GAIAN session; persisted to MemoryStore at session end.
    """

    session_id:           str              = ""
    turn_count:           int              = 0
    cumulative_coherence: float            = 1.0
    dominant_canon_freq:  Dict[str, int]   = field(default_factory=dict)
    readings:             List[SynergyReading] = field(default_factory=list)
    last_conflict:        str              = ""
    metadata:             Dict[str, Any]   = field(default_factory=dict)

    def record(self, reading: SynergyReading) -> None:
        """Append a reading and update running accumulators."""
        self.readings.append(reading)
        self.turn_count += 1
        # Exponential moving average of coherence
        alpha = 0.2
        self.cumulative_coherence = (
            alpha * reading.coherence + (1 - alpha) * self.cumulative_coherence
        )
        if reading.dominant_canon:
            self.dominant_canon_freq[reading.dominant_canon] = (
                self.dominant_canon_freq.get(reading.dominant_canon, 0) + 1
            )
        if reading.conflict_summary:
            self.last_conflict = reading.conflict_summary


def blank_synergy_state(session_id: str = "") -> SynergyState:
    """Return a fresh SynergyState for a new GAIAN session."""
    return SynergyState(session_id=session_id)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Canon keyword → canon reference mapping for context analysis
_CANON_KEYWORDS: Dict[str, str] = {
    "nigredo":        "C10",
    "albedo":         "C10",
    "rubedo":         "C10",
    "citrinitas":     "C10",
    "alchemical":     "C10",
    "magnum opus":    "C10",
    "elemental":      "C32",
    "fire":           "C32",
    "water":          "C32",
    "earth":          "C32",
    "air":            "C32",
    "aether":         "C32",
    "mentalism":      "C40",
    "mind":           "C40",
    "thought":        "C40",
    "shadow":         "C15",
    "consent":        "C15",
    "sovereignty":    "C01",
    "sovereign":      "C01",
    "hermes":         "C00",
    "emerald":        "C00",
    "correspondence": "C00",
}


def _analyse_canon_context(
    text: str,
    extra_keywords: Optional[Dict[str, str]] = None,
) -> Tuple[List[str], str]:
    """
    Analyse *text* for canon keyword signals.

    Returns
    -------
    Tuple[List[str], str]
        ``(canon_tags, dominant_canon)`` where *canon_tags* is a de-duplicated
        list of canon references triggered (e.g. ``["C10", "C32"]``) and
        *dominant_canon* is the most-frequently-triggered reference (or ``""``
        when no keywords match).

    Parameters
    ----------
    text:
        Raw text to scan (user message, engine output, etc.).
    extra_keywords:
        Optional additional ``{keyword: canon_ref}`` pairs to merge with the
        built-in keyword table for this call.
    """
    keywords = dict(_CANON_KEYWORDS)
    if extra_keywords:
        keywords.update(extra_keywords)

    lower = text.lower()
    freq: Dict[str, int] = {}
    for kw, ref in keywords.items():
        if kw in lower:
            freq[ref] = freq.get(ref, 0) + 1

    if not freq:
        return [], ""

    dominant = max(freq, key=lambda r: freq[r])
    tags = sorted(freq.keys())
    return tags, dominant


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class SynergyEngine:
    """
    Cross-engine orchestrator for GAIAN session turns.

    Aggregates readings from individual sub-engines, resolves canon-level
    conflicts, and produces a SynergyReading consumed by GAIANRuntime.

    Usage::

        engine = SynergyEngine()
        state  = blank_synergy_state(session_id="user-123")
        reading, state = engine.plan(state, context={"user_text": "..."})
        print(reading.dominant_canon)   # e.g. "C10"
    """

    def __init__(self, coherence_floor: float = 0.3) -> None:
        """
        Parameters
        ----------
        coherence_floor:
            Minimum coherence score returned even under maximum conflict.
            Prevents the engine from producing a completely incoherent reading
            that would silence the GAIAN's response.
        """
        self._coherence_floor = max(0.0, min(1.0, coherence_floor))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan(
        self,
        state:   SynergyState,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[SynergyReading, SynergyState]:
        """
        Execute one planning step for the current turn.

        Parameters
        ----------
        state:
            Current session SynergyState.
        context:
            Optional signal dict.  Recognised keys:
            ``user_text`` (str),
            ``engine_scores`` (dict[str, float]),
            ``extra_canon_keywords`` (dict[str, str]).

        Returns
        -------
        Tuple[SynergyReading, SynergyState]
            Updated reading + state.
        """
        ctx = context or {}
        user_text  = ctx.get("user_text", "")
        eng_scores = ctx.get("engine_scores", {})
        extra_kw   = ctx.get("extra_canon_keywords", None)

        canon_tags, dominant = _analyse_canon_context(user_text, extra_kw)
        coherence            = self._compute_coherence(eng_scores)
        conflict             = self._detect_conflict(eng_scores)

        reading = SynergyReading(
            coherence=coherence,
            dominant_canon=dominant,
            conflict_summary=conflict,
            engine_scores=dict(eng_scores),
            canon_tags=canon_tags,
            synthesis_note=(
                f"turn={state.turn_count + 1} "
                f"coherence={coherence:.2f} "
                f"dominant={dominant or 'none'}"
            ),
            raw_context=dict(ctx),
        )

        state.record(reading)

        logger.debug(
            "synergy_engine.plan: session=%s turn=%d coherence=%.2f dominant=%s conflict=%r",
            state.session_id,
            state.turn_count,
            coherence,
            dominant or "none",
            conflict or "none",
        )

        return reading, state

    def summarise(self, state: SynergyState) -> Dict[str, Any]:
        """Return a compact summary dict for MemoryStore persistence."""
        return {
            "session_id":           state.session_id,
            "turn_count":           state.turn_count,
            "cumulative_coherence": round(state.cumulative_coherence, 4),
            "dominant_canon_freq":  dict(state.dominant_canon_freq),
            "last_conflict":        state.last_conflict,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_coherence(self, engine_scores: Dict[str, float]) -> float:
        """
        Compute turn coherence from sub-engine scores.

        Coherence = mean of all provided scores, floored at
        ``self._coherence_floor``.  When no scores are provided,
        returns 1.0 (neutral / no information).
        """
        if not engine_scores:
            return 1.0
        mean = sum(engine_scores.values()) / len(engine_scores)
        return max(self._coherence_floor, min(1.0, mean))

    def _detect_conflict(
        self,
        engine_scores: Dict[str, float],
        conflict_threshold: float = 0.35,
    ) -> str:
        """
        Detect significant score divergence between sub-engines.

        Returns a human-readable conflict description when the spread
        between the highest and lowest engine scores exceeds
        *conflict_threshold*, otherwise returns an empty string.
        """
        if len(engine_scores) < 2:
            return ""
        scores = list(engine_scores.values())
        spread = max(scores) - min(scores)
        if spread < conflict_threshold:
            return ""
        low_engine  = min(engine_scores, key=lambda k: engine_scores[k])
        high_engine = max(engine_scores, key=lambda k: engine_scores[k])
        return (
            f"Score divergence detected: {high_engine}={engine_scores[high_engine]:.2f} "
            f"vs {low_engine}={engine_scores[low_engine]:.2f} "
            f"(spread={spread:.2f})"
        )

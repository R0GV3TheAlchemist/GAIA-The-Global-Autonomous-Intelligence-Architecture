"""
shadow_engine/engine.py
ShadowEngine — orchestrates detection, intensity, integration, and transitions.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing   import Optional

import httpx

from .archetypes  import ArchetypeDetector, ShadowInputs
from .intensity   import compute_shadow_intensity
from .integration import IntegrationTracker, IntegrationState
from .types       import (
    ShadowRecord, ShadowTransition,
    ACTIVATION_THRESHOLD, CO_ACTIVE_DELTA,
    INTENSITY_THRESHOLDS, INTEGRATION_MILESTONES,
)

try:
    from ..config import API_BASE
except ImportError:
    import os
    API_BASE = os.environ.get("GAIA_API_BASE", "http://localhost:8000")

_AFFECT_TREND_URL  = f"{API_BASE}/affect/trend"
_STAGE_RECORD_URL  = f"{API_BASE}/stage/record"
_HTTP_TIMEOUT      = 4.0


class ShadowEngine:
    """
    Full shadow evaluation pipeline.

    Usage:
        engine = ShadowEngine()
        record = await engine.evaluate(principal_id)
    """

    def __init__(self) -> None:
        self._detector    = ArchetypeDetector()
        # In-memory cache: principal_id → (ShadowRecord, IntegrationTracker)
        self._cache: dict[str, tuple[ShadowRecord, IntegrationTracker]] = {}

    # ------------------------------------------------------------------ public

    async def evaluate(
        self,
        principal_id: str,
        *,
        source: str = "scheduled",
        override_inputs: Optional[ShadowInputs] = None,
    ) -> ShadowRecord:
        """Run a full evaluation tick and return the updated ShadowRecord."""
        inputs = override_inputs or await self._fetch_inputs(principal_id)
        scores = self._detector.score_all(inputs)

        active, co_active = self._resolve_active(scores)
        prev = self._cache.get(principal_id)
        prev_record = prev[0] if prev else None
        tracker      = prev[1] if prev else None

        days_active = self._compute_days_active(active, prev_record)
        intensity   = compute_shadow_intensity(
            scores.get(active, 0.0) if active else 0.0,
            days_active,
        )

        if tracker is None or (active and tracker._s.archetype != active):
            tracker = IntegrationTracker.new(
                principal_id, active or "Unknown"
            ) if active else IntegrationTracker.new(principal_id, "Unknown")

        record = ShadowRecord(
            principal_id=principal_id,
            active_archetype=active,
            co_active=co_active,
            archetype_scores=scores,
            shadow_intensity=intensity,
            integration_progress=tracker.progress,
            days_active=days_active,
            last_evaluated=datetime.now(timezone.utc),
            evaluation_source=source,
        )

        transitions = self._detect_transitions(record, prev_record)
        self._cache[principal_id] = (record, tracker)
        return record

    async def get_current(self, principal_id: str) -> Optional[ShadowRecord]:
        """Return cached record without re-evaluating."""
        cached = self._cache.get(principal_id)
        return cached[0] if cached else None

    def record_reflection_session(self, principal_id: str) -> float:
        """Add +0.05 integration for a reflection session."""
        cached = self._cache.get(principal_id)
        if not cached:
            return 0.0
        record, tracker = cached
        gain = tracker.accrue_reflection_session()
        updated = ShadowRecord(
            **{**record.__dict__, "integration_progress": tracker.progress}
        )
        self._cache[principal_id] = (updated, tracker)
        return gain

    # ------------------------------------------------------------------ private

    async def _fetch_inputs(self, principal_id: str) -> ShadowInputs:
        """Fetch ArcTrend + StageRecord and assemble ShadowInputs."""
        inputs: ShadowInputs = {}
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            # Affect trend
            try:
                r = await client.get(f"{_AFFECT_TREND_URL}/{principal_id}")
                if r.status_code == 200:
                    at = r.json()
                    inputs.update({
                        "dominant_emotion": at.get("dominant_emotion", "neutral"),
                        "valence_trend":    float(at.get("valence_trend", 0.0)),
                        "mood_momentum":    float(at.get("mood_momentum", 0.0)),
                        "volatility":       min(1.0, float(at.get("volatility", 0.0))),
                        "is_volatile":      bool(at.get("is_volatile", False)),
                        "arc_stability":    float(at.get("arc_stability", 0.5)),
                        "low_energy_flag":  bool(at.get("low_energy_flag", False)),
                        "arousal":          min(1.0, float(at.get("mean_arousal", 0.5))),
                    })
            except Exception:
                self._apply_affect_defaults(inputs)

            # Stage record
            try:
                r = await client.get(f"{_STAGE_RECORD_URL}/{principal_id}")
                if r.status_code == 200:
                    sr = r.json()
                    m  = sr.get("marker_scores", {})
                    inputs.update({
                        "decision_entropy":        float(m.get("decision_entropy", 50.0)),
                        "hrv_coherence":           float(m.get("hrv_coherence", 50.0)),
                        "journaling_depth":        float(m.get("journaling_depth", 50.0)),
                        "focus_session_length":    float(m.get("focus_session_length", 50.0)),
                        "goal_completion_rate":    float(m.get("goal_completion_rate", 50.0)),
                        "emotional_arc_stability": float(m.get("emotional_arc_stability", 50.0)),
                        "days_in_stage":           int(sr.get("days_in_stage", 0)),
                        "regression_active":       bool(sr.get("regression_active", False)),
                    })
            except Exception:
                self._apply_stage_defaults(inputs)

        return inputs

    @staticmethod
    def _apply_affect_defaults(inp: ShadowInputs) -> None:
        inp.setdefault("dominant_emotion", "neutral")
        inp.setdefault("valence_trend",    0.0)
        inp.setdefault("mood_momentum",    0.0)
        inp.setdefault("volatility",       0.0)
        inp.setdefault("is_volatile",      False)
        inp.setdefault("arc_stability",    0.5)
        inp.setdefault("low_energy_flag",  False)
        inp.setdefault("arousal",          0.5)

    @staticmethod
    def _apply_stage_defaults(inp: ShadowInputs) -> None:
        for key in ("decision_entropy", "hrv_coherence", "journaling_depth",
                    "focus_session_length", "goal_completion_rate",
                    "emotional_arc_stability"):
            inp.setdefault(key, 50.0)
        inp.setdefault("days_in_stage",     0)
        inp.setdefault("regression_active", False)

    @staticmethod
    def _resolve_active(
        scores: dict[str, float]
    ) -> tuple[Optional[str], list[str]]:
        if not scores:
            return None, []
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_name, top_score = ranked[0]
        if top_score < ACTIVATION_THRESHOLD:
            return None, []
        co_active = [
            name for name, score in ranked[1:]
            if top_score - score <= CO_ACTIVE_DELTA
        ]
        return top_name, co_active

    @staticmethod
    def _compute_days_active(
        active: Optional[str],
        prev: Optional[ShadowRecord],
    ) -> int:
        if prev is None or prev.active_archetype != active:
            return 0
        return prev.days_active + 1

    @staticmethod
    def _detect_transitions(
        current: ShadowRecord,
        prev:    Optional[ShadowRecord],
    ) -> list[ShadowTransition]:
        transitions: list[ShadowTransition] = []
        now = datetime.now(timezone.utc)
        pid = current.principal_id

        # Archetype shift
        if prev and prev.active_archetype != current.active_archetype:
            transitions.append(ShadowTransition(
                principal_id=pid,
                timestamp=now,
                from_archetype=prev.active_archetype,
                to_archetype=current.active_archetype,
                trigger="archetype_shift",
                intensity_at=current.shadow_intensity,
                integration_at=current.integration_progress,
                note=(
                    f"Archetype shifted from {prev.active_archetype!r} "
                    f"to {current.active_archetype!r}."
                ),
            ))

        # Intensity threshold crossings
        if prev:
            for t in INTENSITY_THRESHOLDS:
                prev_above = prev.shadow_intensity >= t
                curr_above = current.shadow_intensity >= t
                if prev_above != curr_above:
                    direction = "crossed above" if curr_above else "dropped below"
                    transitions.append(ShadowTransition(
                        principal_id=pid,
                        timestamp=now,
                        from_archetype=prev.active_archetype,
                        to_archetype=current.active_archetype,
                        trigger="intensity_threshold",
                        intensity_at=current.shadow_intensity,
                        integration_at=current.integration_progress,
                        note=f"Intensity {direction} {t:.2f}.",
                    ))

        # Integration milestones
        if prev:
            for m in INTEGRATION_MILESTONES:
                if prev.integration_progress < m <= current.integration_progress:
                    transitions.append(ShadowTransition(
                        principal_id=pid,
                        timestamp=now,
                        from_archetype=current.active_archetype,
                        to_archetype=current.active_archetype,
                        trigger="integration_milestone",
                        intensity_at=current.shadow_intensity,
                        integration_at=current.integration_progress,
                        note=(
                            f"Integration milestone reached: "
                            f"{int(m*100)}% for {current.active_archetype!r}."
                        ),
                    ))

        return transitions

"""
crystal/engine.py
CrystalCore — the tick loop that assembles CrystalState from the four streams.

Tick schedule (from spec C-CC01 §2):
  - On app launch (once)
  - Every 15 minutes while the app is active
  - Immediately when GAIA completes a conversation turn (lightweight)

All stream fetching is async over localhost HTTP.
Graceful degradation: any stream failure → neutral default; no exception raised.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing   import Optional

import httpx

from .coherence     import compute_coherence
from .narrative     import build_narrative
from .orb_params    import derive_orb_params
from .persona_tone  import derive_persona_tone
from .types         import (
    CoherenceBand, CrystalState, OrbParams, PersonaTone,
    band_from_psi,
)

try:
    from ..config import API_BASE
except ImportError:
    import os
    API_BASE = os.environ.get("GAIA_API_BASE", "http://localhost:8000")

logger = logging.getLogger("gaia.crystal")

_HTTP_TIMEOUT = 4.0

# Canonical marker key order — matches the positional list the stage stream may return
_MARKER_KEYS = [
    "decision_entropy",
    "hrv_coherence",
    "journaling_depth",
    "focus_session_length",
    "goal_completion_rate",
    "emotional_arc_stability",
]

# Defaults when streams are unavailable
_NEUTRAL_MARKERS: dict[str, float] = {
    "decision_entropy":        50.0,
    "hrv_coherence":           50.0,
    "journaling_depth":        50.0,
    "focus_session_length":    50.0,
    "goal_completion_rate":    50.0,
    "emotional_arc_stability": 50.0,
}


def _normalise_marker_scores(raw) -> dict[str, float]:
    """
    Accept either:
      - a dict  {"decision_entropy": 60.0, ...}  (live stream / unit tests)
      - a list  [60.0, 55.0, 70.0, 50.0, 65.0, 58.0]  (test fixtures)
      - None / anything else  → neutral defaults
    """
    if isinstance(raw, dict):
        return {k: float(raw.get(k, 50.0)) for k in _MARKER_KEYS}
    if isinstance(raw, (list, tuple)):
        pairs = zip(_MARKER_KEYS, raw)
        return {k: float(v) for k, v in pairs}
    return dict(_NEUTRAL_MARKERS)


class CrystalCore:
    """
    Assembles a CrystalState from the four live streams on each tick.

    Maintains an in-memory cache of the latest state.
    History (list of CrystalState) is kept for up to 7 × 96 = 672 ticks.
    """

    MAX_HISTORY = 672  # 7 days × 96 ticks/day (15-min cadence)

    def __init__(
        self,
        principal_id: str = "default",
        *,
        base_url: Optional[str] = None,
    ) -> None:
        self.principal_id = principal_id
        self.base_url = base_url or API_BASE
        self._latest: Optional[CrystalState] = None
        self._history: list[CrystalState] = []
        self._tick_lock = asyncio.Lock()

    # ------------------------------------------------------------------ public

    async def tick(self, *, user_id: Optional[str] = None) -> CrystalState:
        """
        Run a full evaluation tick and return the updated CrystalState.

        Args:
            user_id: Optional override for the principal identifier to use
                     during this tick.  When omitted, ``self.principal_id``
                     is used.
        """
        effective_id = user_id or self.principal_id
        async with self._tick_lock:
            state = await self._build_state(effective_id)
            self._latest = state
            self._history.append(state)
            if len(self._history) > self.MAX_HISTORY:
                self._history = self._history[-self.MAX_HISTORY:]
            logger.debug(
                "Crystal tick complete — Ψ=%.3f band=%s tone=%s",
                state.coherence,
                state.coherence_band.value,
                state.persona_tone.value,
            )
            return state

    @property
    def latest(self) -> Optional[CrystalState]:
        """Return the most recent CrystalState without triggering a new tick."""
        return self._latest

    def history(self, days: int = 7) -> list[CrystalState]:
        """Return history ticks from the last N days (approximate by tick count)."""
        ticks_per_day = 96  # one tick per 15 minutes
        max_ticks = days * ticks_per_day
        return self._history[-max_ticks:]

    # ----------------------------------------------------------------- private

    async def _build_state(self, principal_id: str) -> CrystalState:
        """Fetch all streams, compute Ψ, and assemble a CrystalState."""
        affect, stage, shadow, schumann = await asyncio.gather(
            self._fetch_affect(),
            self._fetch_stage(),
            self._fetch_shadow(),
            self._fetch_schumann(),
            return_exceptions=True,
        )

        # If a gather element is an exception, replace with empty dict / defaults
        affect   = affect   if isinstance(affect,   dict) else {}
        stage    = stage    if isinstance(stage,    dict) else {}
        shadow   = shadow   if isinstance(shadow,   dict) else {}
        schumann = schumann if isinstance(schumann, dict) else {}

        # ── Extract affect fields ──────────────────────────────────────────
        arc_stability    = float(affect.get("arc_stability",    0.5))
        valence_trend    = float(affect.get("valence_trend",    0.0))
        volatility       = float(affect.get("volatility",       0.0))
        dominant_emotion = str(affect.get("dominant_emotion",   "neutral"))

        # ── Extract stage fields ───────────────────────────────────────────
        # marker_scores may arrive as a dict (live) or a list (tests)
        marker_scores = _normalise_marker_scores(stage.get("marker_scores"))
        active_stage  = int(stage.get("stage", 3))

        # ── Extract shadow fields ──────────────────────────────────────────
        shadow_available     = bool(shadow)
        integration_progress = float(shadow.get("integration_progress", 0.5))
        shadow_intensity     = float(shadow.get("shadow_intensity",     0.0))
        active_archetype     = str(shadow.get("active_archetype") or "Unknown")

        # ── Extract schumann fields ────────────────────────────────────────
        schumann_available  = bool(schumann)
        alignment_score     = float(schumann.get("alignment_score", 0.5))
        schumann_confidence = float(schumann.get("confidence",      0.0))
        disturbance_raw     = str(schumann.get("disturbance_level", "unavailable"))
        disturbance = disturbance_raw if disturbance_raw in (
            "stable", "elevated", "disturbed"
        ) else "unavailable"

        # ── Compute coherence ──────────────────────────────────────────────
        psi, A, S, E, H = compute_coherence(
            arc_stability=arc_stability,
            valence_trend=valence_trend,
            volatility=volatility,
            marker_scores=marker_scores,
            integration_progress=integration_progress,
            shadow_intensity=shadow_intensity,
            shadow_available=shadow_available,
            schumann_alignment=alignment_score,
            schumann_confidence=schumann_confidence,
            schumann_available=schumann_available,
        )

        band      = band_from_psi(psi)
        tone      = derive_persona_tone(band)
        narrative = build_narrative(band, dominant_emotion, disturbance)

        partial = _PartialState(
            coherence=psi,
            coherence_band=band,
            dominant_emotion=dominant_emotion,
        )
        orb = derive_orb_params(partial)  # type: ignore[arg-type]

        return CrystalState(
            timestamp=datetime.now(timezone.utc),
            affect_coherence=A,
            stage_coherence=S,
            shadow_integration=E,
            schumann_alignment=H,
            coherence=psi,
            coherence_band=band,
            dominant_emotion=dominant_emotion,
            active_stage=active_stage,
            active_archetype=active_archetype,
            schumann_disturbance=disturbance,
            inner_narrative=narrative,
            persona_tone=tone,
            orb_params=orb,
        )

    # ── Stream fetchers ────────────────────────────────────────────────────

    async def _fetch_affect(self) -> dict:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/affect/trend/{self.principal_id}")
            r.raise_for_status()
            return r.json()

    async def _fetch_stage(self) -> dict:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/stage/record/{self.principal_id}")
            r.raise_for_status()
            return r.json()

    async def _fetch_shadow(self) -> dict:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/shadow/state/{self.principal_id}")
            r.raise_for_status()
            return r.json()

    async def _fetch_schumann(self) -> dict:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            r = await client.get(f"{self.base_url}/schumann/state")
            r.raise_for_status()
            return r.json()


# ---------------------------------------------------------------------------
# Lightweight proxy for orb param derivation (avoids circular import)
# ---------------------------------------------------------------------------

class _PartialState:
    def __init__(
        self,
        coherence:        float,
        coherence_band:   CoherenceBand,
        dominant_emotion: str,
    ) -> None:
        self.coherence        = coherence
        self.coherence_band   = coherence_band
        self.dominant_emotion = dominant_emotion

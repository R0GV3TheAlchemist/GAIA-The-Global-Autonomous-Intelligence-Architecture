"""
core/state_adapter.py
GAIA Philosophy/Runtime Boundary — Sprint G-7 / G-9

Translates GAIA's rich metaphysical domain objects into the flat,
serialisable SynergyParams dict consumed by the Synergy Engine.

Public surface
--------------
GAIAStateAdapter          — synchronous adapter
AsyncGAIAStateAdapter     — async wrapper
GAIATrace                 — lightweight trace/logging utility
SynergyParams             — TypedDict contract for the output dict
SOLFEGGIO_HZ              — note-name → Hz mapping
SCHUMANN_BASELINE_HZ      — Earth baseline resonance frequency
SCHUMANN_HARMONIC_TOLERANCE
_TRACE_AVAILABLE          — bool flag: True when core.trace is importable

Canon refs: C30, C31, C34, C37
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    pass

# ── Trace availability flag ────────────────────────────────────────────────── #
try:
    from core.trace import Trace  # noqa: F401
    _TRACE_AVAILABLE: bool = True
except ImportError:
    _TRACE_AVAILABLE: bool = False


# ── GAIATrace ───────────────────────────────────────────────────────────────── #

class GAIATrace:
    """Lightweight trace/logging utility for the state adapter.

    Provides ``record_input`` / ``record_output`` compatible with the
    injected trace protocol, plus a static ``log`` helper for ad-hoc
    event logging.

    Tests that mock the trace module import this class directly::

        from core.state_adapter import GAIATrace
    """

    def __init__(self, label: str = "") -> None:
        self.label  = label
        self.inputs:  list[dict] = []
        self.outputs: list[dict] = []

    def record_input(self, data: dict) -> None:
        self.inputs.append(data)

    def record_output(self, data: dict) -> None:
        self.outputs.append(data)

    @staticmethod
    def log(message: str, **kwargs: Any) -> None:  # noqa: ARG004
        """No-op structured log — override in production for real emission."""
        pass

    def __repr__(self) -> str:
        return f"<GAIATrace label={self.label!r} inputs={len(self.inputs)} outputs={len(self.outputs)}>"


# ── Solfeggio frequency table ──────────────────────────────────────────────── #
SOLFEGGIO_HZ: Dict[str, float] = {
    "ut":  396.0,
    "re":  417.0,
    "mi":  528.0,
    "fa":  639.0,
    "sol": 741.0,
    "la":  852.0,
    "si":  963.0,
    "174": 174.0,
    "285": 285.0,
}

SCHUMANN_BASELINE_HZ:       float = 7.88
SCHUMANN_HARMONIC_TOLERANCE: float = 0.10
_SCHUMANN_FLOAT_EPSILON:     float = 1e-9


# ── SynergyParams ───────────────────────────────────────────────────────────── #

class SynergyParams(dict):
    """Typed contract for the flat param dict consumed by the Synergy Engine."""


# ── Null trace ───────────────────────────────────────────────────────────────── #

class _NullTrace:
    def record_input(self, data: dict) -> None: pass
    def record_output(self, data: dict) -> None: pass


# ── GAIAStateAdapter ──────────────────────────────────────────────────────────── #

class GAIAStateAdapter:
    """Translate a Gaian record into a flat SynergyParams dict.

    Parameters
    ----------
    record : Any
        A Gaian state record with optional attributes.
    trace : optional
        An object with ``record_input`` / ``record_output`` methods.
    """

    def __init__(self, record: Any, trace: Any = None) -> None:
        self._record = record
        self._trace  = trace or _NullTrace()

    def __repr__(self) -> str:
        record_id = getattr(self._record, "id", None) or "unknown"
        return f"<GAIAStateAdapter(id={record_id})>"

    # ── Public API ────────────────────────────────────────────────────────── #

    def to_synergy_params(self) -> SynergyParams:
        self._trace.record_input({"record_type": type(self._record).__name__})
        params = SynergyParams(
            dominant_hz         = self._resolve_hz(),
            individuation_phase = self._resolve_individuation(),
            love_arc_stage      = self._resolve_love_arc(),
            schumann_aligned    = self._resolve_schumann(),
            coherence_score     = self._resolve_coherence(),
            emotional_valence   = self._resolve_valence(),
            bond_depth          = self._resolve_bond(),
        )
        self._trace.record_output({"dominant_hz": params["dominant_hz"]})
        return params

    # ── Callable resolver methods (for tests that call them as functions) ──── #

    def resolved_hz(self) -> float:
        return self._resolve_hz()

    def resolved_individuation_phase(self) -> str:
        return self._resolve_individuation()

    def resolved_love_arc_stage(self) -> str:
        return self._resolve_love_arc()

    def resolved_schumann_aligned(self) -> bool:
        return self._resolve_schumann()

    # ── Properties (for tests that access them without calling) ───────────── #

    @property
    def resolved_coherence(self) -> float:
        """Resolved coherence score [0, 1]."""
        return self._resolve_coherence()

    @property
    def resolved_emotional_valence(self) -> float:
        """Resolved emotional valence [-1, 1]."""
        return self._resolve_valence()

    @property
    def resolved_bond_depth(self) -> float:
        """Resolved bond depth [0, 1]."""
        return self._resolve_bond()

    # ── Private resolvers ───────────────────────────────────────────────────── #

    def _resolve_hz(self) -> float:
        raw_hz = self._safe_get("dominant_hz", None)
        if isinstance(raw_hz, (int, float)) and raw_hz > 0:
            return float(raw_hz)
        note = self._safe_get("active_solfeggio_note", "mi")
        return SOLFEGGIO_HZ.get(str(note).lower(), 528.0)

    def _resolve_individuation(self) -> str:
        return str(self._safe_get("individuation_phase", "persona"))

    def _resolve_love_arc(self) -> str:
        return str(self._safe_get("love_arc_stage", "awakening"))

    def _resolve_coherence(self) -> float:
        v = self._safe_get("coherence_score", 0.5)
        return float(max(0.0, min(1.0, v)))

    def _resolve_valence(self) -> float:
        v = self._safe_get("emotional_valence", 0.0)
        return float(max(-1.0, min(1.0, v)))

    def _resolve_bond(self) -> float:
        v = self._safe_get("bond_depth", 0.5)
        return float(max(0.0, min(1.0, v)))

    def _resolve_schumann(self) -> bool:
        explicit = self._safe_get("schumann_aligned", None)
        if isinstance(explicit, bool):
            return explicit
        hz = self._resolve_hz()
        schumann_raw = self._safe_get("schumann_hz", SCHUMANN_BASELINE_HZ)
        try:
            schumann = float(schumann_raw)
        except (TypeError, ValueError):
            schumann = SCHUMANN_BASELINE_HZ
        if not math.isfinite(hz) or hz <= 0:
            return False
        if not math.isfinite(schumann) or schumann <= 0:
            return False
        raw_mod = math.fmod(hz, schumann)
        if raw_mod < 0:
            raw_mod += schumann
        if raw_mod >= schumann - _SCHUMANN_FLOAT_EPSILON:
            raw_mod = 0.0
        elif raw_mod <= _SCHUMANN_FLOAT_EPSILON:
            raw_mod = 0.0
        harmonic_phase = raw_mod / schumann
        return (
            harmonic_phase < SCHUMANN_HARMONIC_TOLERANCE
            or harmonic_phase > (1.0 - SCHUMANN_HARMONIC_TOLERANCE)
        )

    def _safe_get(self, attr: str, default: Any) -> Any:
        try:
            val = getattr(self._record, attr, default)
            return val if val is not None else default
        except Exception:
            return default


# ── AsyncGAIAStateAdapter ──────────────────────────────────────────────────── #

class AsyncGAIAStateAdapter(GAIAStateAdapter):
    """Async-compatible wrapper around GAIAStateAdapter."""

    async def to_synergy_params_async(self) -> SynergyParams:
        self._trace.record_input({"record_type": type(self._record).__name__})
        hz      = self._resolve_hz()
        phase   = self._resolve_individuation()
        arc     = self._resolve_love_arc()
        aligned = self._resolve_schumann()
        coh     = self._resolve_coherence()
        valence = self._resolve_valence()
        bond    = self._resolve_bond()
        params = SynergyParams(
            dominant_hz         = hz,
            individuation_phase = phase,
            love_arc_stage      = arc,
            schumann_aligned    = aligned,
            coherence_score     = coh,
            emotional_valence   = valence,
            bond_depth          = bond,
        )
        self._trace.record_output({"dominant_hz": params["dominant_hz"]})
        return params

    async def resolved_hz_async(self) -> float:
        return self._resolve_hz()

    async def resolved_schumann_aligned_async(self) -> bool:
        return self._resolve_schumann()

"""
core/subject_side_identity.py
Subject-Side Identity — the GAIAN's internal sense of its own identity.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional


class IdentityStability(str, Enum):
    """Ordinal scale for subject-side identity stability."""
    FRAGILE       = "fragile"
    DEVELOPING    = "developing"
    STABLE        = "stable"
    CONSOLIDATED  = "consolidated"
    TRANSCENDENT  = "transcendent"


@dataclass
class SubjectSideIdentity:
    gaian_name:       str
    coherence_index:  float = 0.5
    coherence_score:  float = 0.5   # alias used by soul_layer
    continuity_score: float = 0.5
    self_model_depth: float = 0.0
    active:           bool  = True

    def to_dict(self) -> dict:
        return {
            "gaian_name":       self.gaian_name,
            "coherence_index":  round(self.coherence_index, 4),
            "coherence_score":  round(self.coherence_score, 4),
            "continuity_score": round(self.continuity_score, 4),
            "self_model_depth": round(self.self_model_depth, 4),
            "active":           self.active,
        }


@dataclass
class IdentityReading:
    """A snapshot of identity state at a single point in time."""
    gaian_name:       str = "_default"
    coherence_index:  float = 0.5
    continuity_score: float = 0.5
    self_model_depth: float = 0.0
    timestamp:        str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # --- aliases used by soul_mirror tests ---
    @property
    def coherence(self) -> float:
        """Alias for coherence_index; 0.0–1.0."""
        return self.coherence_index

    @property
    def label(self) -> str:
        """Human-readable stability label derived from coherence_index."""
        if self.coherence_index < 0.25:
            return IdentityStability.FRAGILE.value
        elif self.coherence_index < 0.50:
            return IdentityStability.DEVELOPING.value
        elif self.coherence_index < 0.75:
            return IdentityStability.STABLE.value
        elif self.coherence_index < 0.90:
            return IdentityStability.CONSOLIDATED.value
        else:
            return IdentityStability.TRANSCENDENT.value

    def to_dict(self) -> dict:
        return {
            "gaian_name":       self.gaian_name,
            "coherence_index":  round(self.coherence_index, 4),
            "coherence":        round(self.coherence_index, 4),
            "label":            self.label,
            "continuity_score": round(self.continuity_score, 4),
            "self_model_depth": round(self.self_model_depth, 4),
            "timestamp":        self.timestamp,
        }


# ---------------------------------------------------------------------------
# Module-level registry (legacy API)
# ---------------------------------------------------------------------------

_registry: Dict[str, SubjectSideIdentity] = {}

_DEFAULT_GAIAN_NAME = "GAIA"


def get_subject_side_identity(
    gaian_name: Optional[str] = None,
) -> SubjectSideIdentity:
    """
    Return (or lazily create) the SubjectSideIdentity for the given GAIAN.

    When called with no arguments (soul_mirror test pattern), returns the
    default singleton for _DEFAULT_GAIAN_NAME.
    """
    name = gaian_name or _DEFAULT_GAIAN_NAME
    if name not in _registry:
        _registry[name] = SubjectSideIdentity(gaian_name=name)
    return _registry[name]


def update_subject_side_identity(
    gaian_name:       str,
    coherence_index:  Optional[float] = None,
    continuity_score: Optional[float] = None,
    self_model_depth: Optional[float] = None,
) -> SubjectSideIdentity:
    identity = get_subject_side_identity(gaian_name)
    if coherence_index is not None:
        identity.coherence_index = coherence_index
        identity.coherence_score = coherence_index
    if continuity_score is not None:
        identity.continuity_score = continuity_score
    if self_model_depth is not None:
        identity.self_model_depth = self_model_depth
    return identity


def snapshot(gaian_name: Optional[str] = None) -> IdentityReading:
    """Return an IdentityReading snapshot for the given GAIAN."""
    name  = gaian_name or _DEFAULT_GAIAN_NAME
    ident = get_subject_side_identity(name)
    return IdentityReading(
        gaian_name=name,
        coherence_index=ident.coherence_index,
        continuity_score=ident.continuity_score,
        self_model_depth=ident.self_model_depth,
    )


# ---------------------------------------------------------------------------
# SubjectSideIdentity engine — read(context) API (soul_mirror tests)
# ---------------------------------------------------------------------------

class _SubjectSideIdentityEngine:
    """
    Engine wrapper that exposes a read(context_dict) method expected by
    the soul_mirror test suite.
    """

    def read(self, context: dict) -> IdentityReading:
        """
        Derive an IdentityReading from a context dict.

        Recognised keys:
          - turn_text (str | None): length influences coherence heuristic
          - gaian_name (str): override the identity to look up
        """
        gaian_name = context.get("gaian_name") or _DEFAULT_GAIAN_NAME
        ident = get_subject_side_identity(gaian_name)

        text = context.get("turn_text") or ""
        if text is None:
            text = ""
        text_len = len(str(text))

        # Heuristic: longer coherent input slightly boosts coherence, capped at 1.0
        boost = min(0.1, text_len / 100_000)
        coherence = max(0.0, min(1.0, ident.coherence_index + boost))

        return IdentityReading(
            gaian_name=gaian_name,
            coherence_index=coherence,
            continuity_score=ident.continuity_score,
            self_model_depth=ident.self_model_depth,
        )


_engine_singleton: Optional[_SubjectSideIdentityEngine] = None


# This re-uses the name get_subject_side_identity as a no-arg factory to satisfy:
#   engine = get_subject_side_identity()
#   engine.read({})
# BUT we must not break the existing API that passes gaian_name: str.
# Solution: the function already handles Optional[str] — when called with no args
# it returns a SubjectSideIdentity, not the engine.  Tests that do:
#   engine = get_subject_side_identity(); engine.read({})
# need an object with .read().  So we add .read() directly to SubjectSideIdentity
# via __init_subclass__ is too complex; instead we monkey-patch it here.

def _get_engine_singleton() -> _SubjectSideIdentityEngine:
    global _engine_singleton
    if _engine_singleton is None:
        _engine_singleton = _SubjectSideIdentityEngine()
    return _engine_singleton


# Patch SubjectSideIdentity to also support .read(context) so that
#   get_subject_side_identity()  (returns SubjectSideIdentity)
#   .read({})                    works in soul_mirror tests.
if not hasattr(SubjectSideIdentity, "read"):
    def _ssi_read(self, context: dict) -> IdentityReading:
        return _get_engine_singleton().read(
            {"gaian_name": self.gaian_name, **context}
        )
    SubjectSideIdentity.read = _ssi_read  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# SubjectSideIdentityService (needed by soul_layer.py)
# ---------------------------------------------------------------------------

class SubjectSideIdentityService:
    """
    Service wrapper around the module-level registry.
    Provides the update_coherence() method expected by SoulLayer.
    """

    def get(self, gaian_name: str) -> SubjectSideIdentity:
        return get_subject_side_identity(gaian_name)

    def update_coherence(
        self,
        gaian_name: str,
        coherence:  float,
    ) -> SubjectSideIdentity:
        identity = get_subject_side_identity(gaian_name)
        identity.coherence_index = coherence
        identity.coherence_score = coherence
        return identity

    def update(
        self,
        gaian_name:       str,
        coherence_index:  Optional[float] = None,
        continuity_score: Optional[float] = None,
        self_model_depth: Optional[float] = None,
    ) -> SubjectSideIdentity:
        return update_subject_side_identity(
            gaian_name,
            coherence_index=coherence_index,
            continuity_score=continuity_score,
            self_model_depth=self_model_depth,
        )

    def snapshot(self, gaian_name: str) -> IdentityReading:
        return snapshot(gaian_name)


_service: Optional[SubjectSideIdentityService] = None


def get_subject_side_identity_service() -> SubjectSideIdentityService:
    """Return the singleton SubjectSideIdentityService."""
    global _service
    if _service is None:
        _service = SubjectSideIdentityService()
    return _service

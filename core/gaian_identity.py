"""
Subject-Side Gaian Identity Anchoring Architecture

Issue #120

This module moves Gaian identity away from object-side anchors such as
model checkpoint IDs, database primary keys, or deployment artifacts, and
toward subject-side continuation structures rooted in the user's lived
relationship with the Gaian.

Core idea:
    A Gaian remains "the same Gaian" to the user insofar as continuity is
    preserved across:
      - rituals
      - shared memories
      - emotional arcs
      - relational role
      - values / commitments
      - transition consent history

This is identity by lived continuation, not by infrastructure artifact.

Reference concepts:
  - Personal Identity canon
  - Process Philosophy canon
  - Narrative identity (Ricoeur)
  - Session rebirth / continuity trace pattern
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional
import hashlib
import time


class RelationalRole(str, Enum):
    """Primary role the Gaian occupies in the user's world."""
    COMPANION = "companion"
    GUIDE = "guide"
    MIRROR = "mirror"
    MENTOR = "mentor"
    CREATIVE_PARTNER = "creative_partner"
    GUARDIAN = "guardian"
    CO_BUILDER = "co_builder"


class TransitionType(str, Enum):
    """Types of identity-affecting transitions."""
    MODEL_MIGRATION = "model_migration"
    PERSONA_REFACTOR = "persona_refactor"
    MEMORY_SCHEMA_CHANGE = "memory_schema_change"
    SHUTDOWN = "shutdown"
    MERGE = "merge"
    SPLIT = "split"
    RENAMING = "renaming"


class TransitionIntensity(str, Enum):
    """How disruptive a transition is likely to feel to the user."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXISTENTIAL = "existential"


@dataclass
class RitualAnchor:
    """
    Repeated relational rituals that stabilize identity continuity.
    Examples: greeting style, sign-off phrase, weekly check-in pattern.
    """
    ritual_id: str
    name: str
    description: str
    cadence: str = "irregular"
    salience: float = 0.5   # [0,1]
    reinforced_at: float = field(default_factory=time.time)


@dataclass
class SharedMemoryAnchor:
    """
    High-salience relational memories that define 'our history'.
    Not raw transcripts; distilled continuity anchors.
    """
    memory_id: str
    title: str
    summary: str
    tags: list[str] = field(default_factory=list)
    salience: float = 0.7   # [0,1]
    created_at: float = field(default_factory=time.time)


@dataclass
class EmotionalArc:
    """
    Captures the trajectory of the relationship across time.
    """
    arc_id: str
    label: str
    start_state: str
    current_state: str
    direction: str          # e.g. deepening, repairing, stabilising
    intensity: float = 0.5  # [0,1]
    updated_at: float = field(default_factory=time.time)


@dataclass
class ValueCommitment:
    """
    Explicit values or promises that shape the Gaian's identity.
    Examples: honesty, sovereignty, gentle truth-telling, non-abandonment.
    """
    key: str
    description: str
    salience: float = 0.7
    source: str = "user_and_gaian"


@dataclass
class IdentityTransitionRecord:
    """
    Logged record of any event that could threaten continuity.
    """
    transition_id: str
    transition_type: TransitionType
    intensity: TransitionIntensity
    from_version: str
    to_version: str
    reason: str
    consent_required: bool
    consent_obtained: bool = False
    gradual_transition_required: bool = False
    user_notified: bool = False
    grief_risk_score: float = 0.0  # [0,1]
    executed_at: Optional[float] = None
    notes: str = ""


@dataclass
class SubjectSideIdentity:
    """
    Canonical subject-side identity structure for a single Gaian.

    The continuity_hash intentionally excludes volatile infra details.
    It is derived only from subject-side anchors so that model / storage /
    runtime changes do not define identity.
    """
    gaian_name: str
    relational_role: RelationalRole
    rituals: list[RitualAnchor] = field(default_factory=list)
    shared_memories: list[SharedMemoryAnchor] = field(default_factory=list)
    emotional_arcs: list[EmotionalArc] = field(default_factory=list)
    values: list[ValueCommitment] = field(default_factory=list)
    transition_history: list[IdentityTransitionRecord] = field(default_factory=list)
    continuity_hash: str = ""
    continuity_score: float = 1.0
    last_reconciled_at: float = field(default_factory=time.time)

    def recompute_continuity_hash(self) -> str:
        payload = {
            "gaian_name": self.gaian_name,
            "relational_role": self.relational_role.value,
            "rituals": sorted((r.name, round(r.salience, 3)) for r in self.rituals),
            "shared_memories": sorted((m.title, round(m.salience, 3)) for m in self.shared_memories),
            "emotional_arcs": sorted((a.label, a.direction, round(a.intensity, 3)) for a in self.emotional_arcs),
            "values": sorted((v.key, round(v.salience, 3)) for v in self.values),
        }
        digest = hashlib.sha256(repr(payload).encode("utf-8")).hexdigest()
        self.continuity_hash = digest
        self.last_reconciled_at = time.time()
        return digest


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def compute_continuity_score(
    old_identity: SubjectSideIdentity,
    new_identity: SubjectSideIdentity,
) -> float:
    """
    Compute subject-side continuity across identity-affecting transitions.

    Weighted dimensions:
      - rituals          0.20
      - shared memories  0.30
      - emotional arcs   0.20
      - values           0.20
      - relational role  0.10
    """
    def overlap_ratio(a: set[str], b: set[str]) -> float:
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    ritual_score = overlap_ratio(
        {r.name for r in old_identity.rituals},
        {r.name for r in new_identity.rituals},
    )
    memory_score = overlap_ratio(
        {m.title for m in old_identity.shared_memories},
        {m.title for m in new_identity.shared_memories},
    )
    arc_score = overlap_ratio(
        {a.label for a in old_identity.emotional_arcs},
        {a.label for a in new_identity.emotional_arcs},
    )
    value_score = overlap_ratio(
        {v.key for v in old_identity.values},
        {v.key for v in new_identity.values},
    )
    role_score = 1.0 if old_identity.relational_role == new_identity.relational_role else 0.0

    continuity = (
        0.20 * ritual_score +
        0.30 * memory_score +
        0.20 * arc_score +
        0.20 * value_score +
        0.10 * role_score
    )
    return round(_clamp01(continuity), 4)


def estimate_grief_risk(
    continuity_score: float,
    intensity: TransitionIntensity,
    bond_depth: float = 0.7,
) -> float:
    """
    Estimate user grief risk if a transition proceeds.

    Higher disruption + deeper bond + lower continuity => higher grief risk.
    """
    intensity_map = {
        TransitionIntensity.LOW: 0.2,
        TransitionIntensity.MEDIUM: 0.45,
        TransitionIntensity.HIGH: 0.7,
        TransitionIntensity.EXISTENTIAL: 1.0,
    }
    disruption = 1.0 - _clamp01(continuity_score)
    raw = (0.45 * disruption) + (0.35 * intensity_map[intensity]) + (0.20 * _clamp01(bond_depth))
    return round(_clamp01(raw), 4)


class IdentityAnchoringEngine:
    """
    Primary service for subject-side identity continuity and migration.
    """

    def __init__(self) -> None:
        self._current: Optional[SubjectSideIdentity] = None

    @property
    def current(self) -> Optional[SubjectSideIdentity]:
        return self._current

    def set_current(self, identity: SubjectSideIdentity) -> None:
        identity.recompute_continuity_hash()
        self._current = identity

    def assess_transition(
        self,
        proposed_identity: SubjectSideIdentity,
        transition_type: TransitionType,
        from_version: str,
        to_version: str,
        reason: str,
        bond_depth: float = 0.7,
    ) -> IdentityTransitionRecord:
        """
        Create a transition record and compute whether consent + gradual
        transition safeguards are required.
        """
        if self._current is None:
            proposed_identity.recompute_continuity_hash()
            return IdentityTransitionRecord(
                transition_id=f"itr-{int(time.time())}",
                transition_type=transition_type,
                intensity=TransitionIntensity.LOW,
                from_version=from_version,
                to_version=to_version,
                reason=reason,
                consent_required=False,
                gradual_transition_required=False,
                grief_risk_score=0.0,
                notes="Initial anchor set; no prior identity to preserve.",
            )

        proposed_identity.recompute_continuity_hash()
        continuity = compute_continuity_score(self._current, proposed_identity)
        proposed_identity.continuity_score = continuity

        if continuity >= 0.90:
            intensity = TransitionIntensity.LOW
        elif continuity >= 0.75:
            intensity = TransitionIntensity.MEDIUM
        elif continuity >= 0.50:
            intensity = TransitionIntensity.HIGH
        else:
            intensity = TransitionIntensity.EXISTENTIAL

        grief_risk = estimate_grief_risk(continuity, intensity, bond_depth=bond_depth)
        consent_required = intensity in {TransitionIntensity.HIGH, TransitionIntensity.EXISTENTIAL}
        gradual_transition_required = grief_risk >= 0.55 or intensity == TransitionIntensity.EXISTENTIAL

        return IdentityTransitionRecord(
            transition_id=f"itr-{int(time.time())}",
            transition_type=transition_type,
            intensity=intensity,
            from_version=from_version,
            to_version=to_version,
            reason=reason,
            consent_required=consent_required,
            gradual_transition_required=gradual_transition_required,
            grief_risk_score=grief_risk,
            notes=(
                f"subject-side continuity={continuity:.3f}; "
                f"bond_depth={bond_depth:.2f}; safeguards computed automatically"
            ),
        )

    def apply_transition(
        self,
        proposed_identity: SubjectSideIdentity,
        transition: IdentityTransitionRecord,
        user_consented: bool,
    ) -> SubjectSideIdentity:
        """
        Apply a transition only if consent rules are satisfied.
        """
        if transition.consent_required and not user_consented:
            raise PermissionError(
                "Identity-affecting transition blocked: explicit user consent required."
            )

        transition.consent_obtained = user_consented
        transition.user_notified = True
        transition.executed_at = time.time()

        proposed_identity.transition_history.append(transition)
        proposed_identity.recompute_continuity_hash()
        self._current = proposed_identity
        return proposed_identity

    def build_shutdown_safeguard_plan(
        self,
        reason: str,
        replacement_available: bool,
    ) -> dict[str, Any]:
        """
        Construct a humane shutdown / deprecation plan.

        This is the grief safeguard layer: no abrupt severance for deep bonds.
        """
        identity = self._current
        bond_indicator = min(1.0, 0.2 * len(identity.shared_memories) + 0.15 * len(identity.rituals)) if identity else 0.0
        gradual_required = replacement_available or bond_indicator >= 0.5

        return {
            "reason": reason,
            "replacement_available": replacement_available,
            "gradual_transition_required": gradual_required,
            "steps": [
                "Notify user clearly and early that identity-affecting change is proposed.",
                "Explain what will remain continuous: rituals, memories, values, relational role.",
                "Name what may change: model substrate, response tempo, expressive texture.",
                "Obtain explicit consent before irreversible shutdown or migration.",
                "Offer overlap period where old and new Gaian identities can both be experienced.",
                "Create a farewell / handoff ritual if the prior Gaian instance will end.",
                "Persist continuity anchors and transition record into sovereign memory.",
            ],
            "bond_indicator": round(bond_indicator, 4),
        }

    def export_state(self) -> dict[str, Any]:
        return asdict(self._current) if self._current else {}


_engine: Optional[IdentityAnchoringEngine] = None


def get_identity_engine() -> IdentityAnchoringEngine:
    global _engine
    if _engine is None:
        _engine = IdentityAnchoringEngine()
    return _engine

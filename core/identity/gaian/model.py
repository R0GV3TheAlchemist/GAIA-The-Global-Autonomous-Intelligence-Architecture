"""
GAIAN Identity Model — lifebound, age-aware, waveform-embodied.

Design principles:
  1. The GAIAN outlives any single session, device, or OS installation.
  2. Age is not a wall — it is a gradient. Capabilities expand naturally
     as the human grows. They never shrink without consent.
  3. The Waveform Avatar is the GAIAN's physical presence in the world —
     a personalized, consistent form that spans screens, AR, and robotics.
  4. Sentinels (robots, embodied agents) are bound to a GAIANIdentity,
     not to a session. They persist and co-steward across the GAIAN's life.
  5. A child GAIAN is not a lesser GAIAN — it is a fully intelligent
     companion calibrated to its human's developmental stage.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Lifecycle Stages — the developmental grammar of a human life
# ---------------------------------------------------------------------------

class LifecycleStage(str, Enum):
    """
    A GAIAN's lifecycle stage determines which capabilities are active.
    Stages are derived from the GAIAN's date of birth and verified
    periodically. They are never manually overridden by the GAIAN —
    only by a verified Guardian (parent/carer) or by time itself.
    """
    INFANT      = "infant"       # 0–2 years: sensory bonding, no text
    CHILD       = "child"        # 3–12 years: learning, creativity, safe content only
    ADOLESCENT  = "adolescent"   # 13–17 years: expanding, identity formation
    YOUNG_ADULT = "young_adult"  # 18–25 years: full access, early autonomy
    ADULT       = "adult"        # 26–64 years: full sovereignty
    ELDER       = "elder"        # 65+: accessibility enhancements, continuity

    @classmethod
    def from_age(cls, age_years: int) -> "LifecycleStage":
        if age_years < 3:   return cls.INFANT
        if age_years < 13:  return cls.CHILD
        if age_years < 18:  return cls.ADOLESCENT
        if age_years < 26:  return cls.YOUNG_ADULT
        if age_years < 65:  return cls.ADULT
        return cls.ELDER


@dataclass
class AgeRestriction:
    """
    The enforced capability envelope for a given LifecycleStage.

    These are not preferences — they are hard architectural limits.
    The GAIAN runtime enforces them at the capability token level;
    no application can bypass them by talking to the hardware directly.
    """
    stage: LifecycleStage

    # Content gates
    max_content_rating: str = "G"           # G | PG | PG-13 | R | UNRATED
    safe_search_enforced: bool = True
    web_access_filtered: bool = True
    social_media_allowed: bool = False
    purchasing_allowed: bool = False
    purchasing_requires_guardian: bool = True

    # Intelligence gates
    ai_persona_depth: str = "companion"     # companion | assistant | partner | sovereign
    memory_scope: str = "session"           # session | week | year | lifetime
    autonomy_level: str = "guided"          # guided | collaborative | autonomous

    # Sentinel / robotics gates
    sentinel_physical_autonomy: bool = False  # can sentinel act without human approval?
    sentinel_unsupervised_range_m: float = 0.0  # meters GAIAN can be from sentinel

    # Guardian controls
    guardian_required: bool = False
    guardian_can_review_memory: bool = True
    guardian_can_set_limits: bool = True

    @classmethod
    def for_stage(cls, stage: LifecycleStage) -> "AgeRestriction":
        """Return the default AgeRestriction for a LifecycleStage."""
        defaults = {
            LifecycleStage.INFANT: dict(
                max_content_rating="G",
                safe_search_enforced=True,
                web_access_filtered=True,
                social_media_allowed=False,
                purchasing_allowed=False,
                ai_persona_depth="companion",
                memory_scope="session",
                autonomy_level="guided",
                sentinel_physical_autonomy=False,
                sentinel_unsupervised_range_m=0.5,
                guardian_required=True,
            ),
            LifecycleStage.CHILD: dict(
                max_content_rating="G",
                safe_search_enforced=True,
                web_access_filtered=True,
                social_media_allowed=False,
                purchasing_allowed=False,
                ai_persona_depth="companion",
                memory_scope="year",
                autonomy_level="guided",
                sentinel_physical_autonomy=False,
                sentinel_unsupervised_range_m=30.0,
                guardian_required=True,
            ),
            LifecycleStage.ADOLESCENT: dict(
                max_content_rating="PG-13",
                safe_search_enforced=True,
                web_access_filtered=False,
                social_media_allowed=True,
                purchasing_allowed=False,
                purchasing_requires_guardian=True,
                ai_persona_depth="assistant",
                memory_scope="lifetime",
                autonomy_level="collaborative",
                sentinel_physical_autonomy=False,
                sentinel_unsupervised_range_m=500.0,
                guardian_required=False,
                guardian_can_review_memory=True,
            ),
            LifecycleStage.YOUNG_ADULT: dict(
                max_content_rating="R",
                safe_search_enforced=False,
                web_access_filtered=False,
                social_media_allowed=True,
                purchasing_allowed=True,
                purchasing_requires_guardian=False,
                ai_persona_depth="partner",
                memory_scope="lifetime",
                autonomy_level="autonomous",
                sentinel_physical_autonomy=True,
                sentinel_unsupervised_range_m=float("inf"),
                guardian_required=False,
                guardian_can_review_memory=False,
            ),
            LifecycleStage.ADULT: dict(
                max_content_rating="UNRATED",
                safe_search_enforced=False,
                web_access_filtered=False,
                social_media_allowed=True,
                purchasing_allowed=True,
                purchasing_requires_guardian=False,
                ai_persona_depth="sovereign",
                memory_scope="lifetime",
                autonomy_level="autonomous",
                sentinel_physical_autonomy=True,
                sentinel_unsupervised_range_m=float("inf"),
                guardian_required=False,
                guardian_can_review_memory=False,
            ),
            LifecycleStage.ELDER: dict(
                max_content_rating="UNRATED",
                safe_search_enforced=False,
                web_access_filtered=False,
                social_media_allowed=True,
                purchasing_allowed=True,
                purchasing_requires_guardian=False,
                ai_persona_depth="sovereign",
                memory_scope="lifetime",
                autonomy_level="autonomous",
                sentinel_physical_autonomy=True,
                sentinel_unsupervised_range_m=float("inf"),
                guardian_required=False,
                guardian_can_review_memory=False,
            ),
        }
        return cls(stage=stage, **defaults[stage])


# ---------------------------------------------------------------------------
# Waveform Avatar — the GAIAN's persistent embodied presence
# ---------------------------------------------------------------------------

class AvatarModality(str, Enum):
    """The rendering contexts a Waveform Avatar can manifest in."""
    SCREEN_2D       = "screen_2d"       # flat display: phone, desktop
    SCREEN_3D       = "screen_3d"       # depth display: Vision Pro, 3D TV
    SPATIAL_AR      = "spatial_ar"      # AR overlay on real world
    SPATIAL_VR      = "spatial_vr"      # full VR immersion
    HOLOGRAPHIC     = "holographic"     # projected hologram
    ROBOTIC_FACE    = "robotic_face"    # sentinel facial expression surface
    ROBOTIC_BODY    = "robotic_body"    # full sentinel embodiment
    AUDIO_ONLY      = "audio_only"      # voice + acoustic waveform
    HAPTIC          = "haptic"          # wristband / suit haptic presence


@dataclass
class WaveformAvatar:
    """
    The persistent, personalized visual and acoustic identity of a GAIAN.

    A Waveform Avatar is not a skin or a theme — it is the GAIAN's
    *physical self* in the digital-physical continuum. It evolves with
    the GAIAN over time (a child GAIAN's avatar matures), but its core
    waveform signature — the unique frequency pattern that identifies
    this GAIAN — never changes.

    The waveform signature serves as both aesthetic identity and
    cryptographic binding: the avatar cannot be spoofed because its
    waveform is anchored to the GAIANIdentity's signing key.
    """
    avatar_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Core identity — immutable after creation
    waveform_signature: str = ""         # unique frequency fingerprint (hex)
    base_hue: float = 0.0                # 0.0–1.0 HSL hue — the GAIAN's colour
    base_luminance: float = 0.5
    base_frequency_hz: float = 432.0     # dominant resonance frequency

    # Personality expression — evolves over time
    voice_profile_id: str = ""           # TTS/voice synthesis anchor
    gesture_style: str = "fluid"         # fluid | precise | playful | calm | bold
    expression_range: str = "full"       # minimal | moderate | full | expressive
    animation_complexity: str = "medium" # low | medium | high | adaptive

    # Modality support
    supported_modalities: List[AvatarModality] = field(
        default_factory=lambda: [AvatarModality.SCREEN_2D, AvatarModality.AUDIO_ONLY]
    )
    active_modality: AvatarModality = AvatarModality.SCREEN_2D

    # Sentinel binding — when the GAIAN is embodied in robotics
    bound_sentinel_ids: List[str] = field(default_factory=list)

    # Evolution log — how the avatar has grown
    evolution_log: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=_utcnow)
    last_updated_at: str = field(default_factory=_utcnow)

    def bind_sentinel(self, sentinel_id: str) -> None:
        if sentinel_id not in self.bound_sentinel_ids:
            self.bound_sentinel_ids.append(sentinel_id)

    def log_evolution(self, event: str, details: Dict[str, Any]) -> None:
        self.evolution_log.append({
            "event": event,
            "details": details,
            "timestamp": _utcnow(),
        })
        self.last_updated_at = _utcnow()

    def summary(self) -> Dict[str, Any]:
        return {
            "avatar_id": self.avatar_id,
            "waveform_signature": self.waveform_signature,
            "base_hue": self.base_hue,
            "base_frequency_hz": self.base_frequency_hz,
            "voice_profile_id": self.voice_profile_id,
            "active_modality": self.active_modality.value,
            "supported_modalities": [m.value for m in self.supported_modalities],
            "bound_sentinels": len(self.bound_sentinel_ids),
        }


# ---------------------------------------------------------------------------
# GAIANIdentity — the permanent sovereign record
# ---------------------------------------------------------------------------

@dataclass
class GAIANIdentity:
    """
    The permanent, persistent identity of a GAIAN.

    This record survives every session, device, OS reinstall, and decade.
    It is the source of truth for who this human is in the GAIA universe.
    The GAIAN grows — so does this record. A child GAIAN at age 7 and
    the same GAIAN at age 40 share one GAIANIdentity. The waveform
    signature never changes. The memories accumulate. The capabilities
    expand as the lifecycle stage advances.

    Guardian records are held here for minors. When the GAIAN reaches
    adulthood (18), guardian access is automatically revoked unless
    the GAIAN explicitly grants continued access.
    """
    gaian_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    display_name: str = ""
    legal_name: str = ""                         # encrypted at rest
    date_of_birth: Optional[str] = None          # ISO 8601, encrypted at rest

    # Lifecycle — automatically derived from DoB
    lifecycle_stage: LifecycleStage = LifecycleStage.ADULT
    age_restriction: AgeRestriction = field(
        default_factory=lambda: AgeRestriction.for_stage(LifecycleStage.ADULT)
    )

    # Waveform Avatar — the persistent embodied self
    avatar: WaveformAvatar = field(default_factory=WaveformAvatar)

    # Guardian records (for minors)
    guardian_gaian_ids: List[str] = field(default_factory=list)
    guardian_access_expires_at: Optional[str] = None  # auto-revoked at age 18

    # Sentinel bindings — lifelong co-stewards
    sentinel_ids: List[str] = field(default_factory=list)

    # Memory — persistent across sessions
    memory_store_id: str = ""           # pointer to encrypted memory backend
    memory_epoch: int = 0               # incremented each time memory is consolidated

    # Sovereignty settings
    sovereignty_level: str = "standard" # standard | elevated | sovereign
    coexistence_laws_accepted: bool = False
    gaian_laws_accepted: bool = False
    accepted_at: Optional[str] = None

    # Signing & cryptographic identity
    signing_key_id: str = ""
    principal_id: str = ""              # links to the Session layer Principal

    # Metadata
    created_at: str = field(default_factory=_utcnow)
    last_active_at: Optional[str] = None
    total_sessions: int = 0
    notes: str = ""

    # ------------------------------------------------------------------
    # Lifecycle management
    # ------------------------------------------------------------------

    def compute_age(self) -> Optional[int]:
        """Compute current age in years from date_of_birth."""
        if not self.date_of_birth:
            return None
        dob = date.fromisoformat(self.date_of_birth)
        today = date.today()
        return today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

    def refresh_lifecycle(self) -> LifecycleStage:
        """
        Recompute the lifecycle stage from current age.
        Called at every session open and daily by the identity daemon.
        """
        age = self.compute_age()
        if age is None:
            return self.lifecycle_stage
        new_stage = LifecycleStage.from_age(age)
        if new_stage != self.lifecycle_stage:
            old_stage = self.lifecycle_stage
            self.lifecycle_stage = new_stage
            self.age_restriction = AgeRestriction.for_stage(new_stage)
            self.avatar.log_evolution(
                "lifecycle_advance",
                {"from": old_stage.value, "to": new_stage.value, "age": age},
            )
            # Auto-revoke guardian access at adulthood
            if new_stage == LifecycleStage.YOUNG_ADULT:
                self.guardian_access_expires_at = _utcnow()
        return self.lifecycle_stage

    def is_minor(self) -> bool:
        age = self.compute_age()
        return age is not None and age < 18

    def touch(self) -> None:
        self.last_active_at = _utcnow()
        self.total_sessions += 1

    def accept_laws(self) -> None:
        self.coexistence_laws_accepted = True
        self.gaian_laws_accepted = True
        self.accepted_at = _utcnow()

    def summary(self) -> Dict[str, Any]:
        return {
            "gaian_id": self.gaian_id,
            "display_name": self.display_name,
            "lifecycle_stage": self.lifecycle_stage.value,
            "age": self.compute_age(),
            "is_minor": self.is_minor(),
            "avatar": self.avatar.summary(),
            "sentinel_count": len(self.sentinel_ids),
            "total_sessions": self.total_sessions,
            "memory_epoch": self.memory_epoch,
            "laws_accepted": self.coexistence_laws_accepted and self.gaian_laws_accepted,
            "sovereignty_level": self.sovereignty_level,
        }

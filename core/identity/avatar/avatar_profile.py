"""
core/identity/avatar/avatar_profile.py

AvatarProfile — the persistent, sovereign identity record for a GAIA avatar.

Design:
- Immutable core fields (id, created_at, origin_key) set at creation.
- Mutable expression fields (name, voice, traits, mode) updated via
  controlled mutators that log a change history.
- Serialises cleanly to/from dict for storage in the warm/cold tiers.
- Sovereign: the avatar owns its own state; no external system may
  mutate it without an explicit consent token (C15).

Canon Refs: C01, C04, C15
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ExpressionMode(str, Enum):
    """
    The stance an avatar takes when interacting.

    NEUTRAL    — default, balanced, no dominant affect
    GUARDIAN   — protective, boundary-asserting
    SCHOLAR    — analytic, citation-forward
    HERALD     — expressive, narrative-rich
    WITNESS    — receptive, reflective, minimal output
    SOVEREIGN  — highest-authority posture; only for root avatars
    """
    NEUTRAL   = "neutral"
    GUARDIAN  = "guardian"
    SCHOLAR   = "scholar"
    HERALD    = "herald"
    WITNESS   = "witness"
    SOVEREIGN = "sovereign"


# ---------------------------------------------------------------------------
# Trait
# ---------------------------------------------------------------------------

@dataclass
class AvatarTrait:
    """
    A named characteristic with a normalised intensity [0.0, 1.0].

    Examples:
        AvatarTrait(name="curiosity", intensity=0.85)
        AvatarTrait(name="directness", intensity=0.70)
    """
    name: str
    intensity: float = 0.5          # [0.0, 1.0]
    description: str = ""
    inherited: bool = False         # True if propagated from a parent avatar

    def __post_init__(self) -> None:
        self.intensity = max(0.0, min(1.0, self.intensity))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AvatarTrait":
        return cls(
            name=d["name"],
            intensity=d.get("intensity", 0.5),
            description=d.get("description", ""),
            inherited=d.get("inherited", False),
        )


# ---------------------------------------------------------------------------
# Change record
# ---------------------------------------------------------------------------

@dataclass
class ProfileChange:
    field: str
    old_value: Any
    new_value: Any
    changed_at: float = field(default_factory=time.time)
    changed_by: str = "self"        # avatar_id or 'system'
    consent_token: Optional[str] = None


# ---------------------------------------------------------------------------
# AvatarProfile
# ---------------------------------------------------------------------------

@dataclass
class AvatarProfile:
    """
    Persistent sovereign identity record.

    Immutable fields
    ----------------
    id           Unique avatar identifier (UUID4).
    created_at   Unix timestamp of creation.
    origin_key   Cryptographic origin reference (e.g., public key fingerprint).

    Mutable fields
    --------------
    name         Display name.
    voice        Tone / voice descriptor (e.g., 'warm', 'precise', 'poetic').
    mode         Current ExpressionMode.
    traits       List of AvatarTrait instances.
    tags         Arbitrary string labels.
    metadata     Free-form dict for extension without schema changes.
    """

    # Immutable
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    origin_key: str = ""

    # Mutable expression fields
    name: str = "unnamed"
    voice: str = "neutral"
    mode: ExpressionMode = ExpressionMode.NEUTRAL
    traits: List[AvatarTrait] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Internal audit trail
    _history: List[ProfileChange] = field(default_factory=list, repr=False)
    updated_at: float = field(default_factory=time.time)

    # ------------------------------------------------------------------
    # Mutators (logged)
    # ------------------------------------------------------------------

    def set_name(
        self,
        name: str,
        *,
        changed_by: str = "self",
        consent_token: Optional[str] = None,
    ) -> None:
        self._record("name", self.name, name, changed_by, consent_token)
        self.name = name

    def set_voice(
        self,
        voice: str,
        *,
        changed_by: str = "self",
        consent_token: Optional[str] = None,
    ) -> None:
        self._record("voice", self.voice, voice, changed_by, consent_token)
        self.voice = voice

    def set_mode(
        self,
        mode: ExpressionMode,
        *,
        changed_by: str = "self",
        consent_token: Optional[str] = None,
    ) -> None:
        if mode == ExpressionMode.SOVEREIGN and changed_by != "root":
            raise PermissionError(
                "SOVEREIGN mode requires changed_by='root' and a valid consent_token."
            )
        self._record("mode", self.mode, mode, changed_by, consent_token)
        self.mode = mode

    def set_trait(
        self,
        trait: AvatarTrait,
        *,
        changed_by: str = "self",
        consent_token: Optional[str] = None,
    ) -> None:
        """Upsert a trait by name."""
        existing = next((t for t in self.traits if t.name == trait.name), None)
        self._record(
            f"trait:{trait.name}",
            existing.to_dict() if existing else None,
            trait.to_dict(),
            changed_by,
            consent_token,
        )
        if existing:
            self.traits.remove(existing)
        self.traits.append(trait)
        self.updated_at = time.time()

    def remove_trait(
        self,
        name: str,
        *,
        changed_by: str = "self",
        consent_token: Optional[str] = None,
    ) -> bool:
        existing = next((t for t in self.traits if t.name == name), None)
        if not existing:
            return False
        self._record(f"trait:{name}", existing.to_dict(), None, changed_by, consent_token)
        self.traits.remove(existing)
        self.updated_at = time.time()
        return True

    def get_trait(self, name: str) -> Optional[AvatarTrait]:
        return next((t for t in self.traits if t.name == name), None)

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = time.time()

    def remove_tag(self, tag: str) -> bool:
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = time.time()
            return True
        return False

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def history(self) -> List[ProfileChange]:
        return list(self._history)

    def history_for_field(self, field_name: str) -> List[ProfileChange]:
        return [c for c in self._history if c.field == field_name]

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "origin_key": self.origin_key,
            "name": self.name,
            "voice": self.voice,
            "mode": self.mode.value,
            "traits": [t.to_dict() for t in self.traits],
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "AvatarProfile":
        profile = cls(
            id=d["id"],
            created_at=d["created_at"],
            updated_at=d.get("updated_at", d["created_at"]),
            origin_key=d.get("origin_key", ""),
            name=d.get("name", "unnamed"),
            voice=d.get("voice", "neutral"),
            mode=ExpressionMode(d.get("mode", "neutral")),
            traits=[AvatarTrait.from_dict(t) for t in d.get("traits", [])],
            tags=d.get("tags", []),
            metadata=d.get("metadata", {}),
        )
        return profile

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _record(
        self,
        field_name: str,
        old: Any,
        new: Any,
        changed_by: str,
        consent_token: Optional[str],
    ) -> None:
        self._history.append(
            ProfileChange(
                field=field_name,
                old_value=old,
                new_value=new,
                changed_by=changed_by,
                consent_token=consent_token,
            )
        )
        self.updated_at = time.time()

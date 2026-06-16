"""Architect Repository — Human Principal profile store.

The Architect is GAIA's term for the Human Principal as the sovereign
builder and partner — the one who holds vision and will.

The ArchitectRepository stores and retrieves Architect profiles.
Profiles persist across sessions — they are M3 Identity anchors.

C04 §2: A valid Human Principal must be a living human being,
explicitly enrolled with informed consent.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ArchitectProfile:
    """The Architect (Human Principal) profile — stored across all sessions.

    C04 §2.3: The Human Principal controls session continuity, permission tier,
    memory retention, audit review, suspension, termination, and scope.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    foundation_statement: str = ""          # Their declared purpose / intention for GAIA
    elemental_signature: Optional[str] = None  # FIRE / EARTH / WATER / AIR / AETHER
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_count: int = 0
    current_stage: str = "NIGREDO"           # Alchemical stage at last session
    last_session_id: Optional[str] = None
    last_seen_at: Optional[datetime] = None
    autonomy_tier: int = 4                   # C04 §4: T0–T4; default T4 SOVEREIGN
    is_active: bool = True
    metadata: dict = field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)

    def record_session_open(self, session_id: str) -> None:
        self.session_count += 1
        self.last_session_id = session_id
        self.last_seen_at = datetime.now(timezone.utc)
        self.touch()

    def update_stage(self, stage: str) -> None:
        self.current_stage = stage
        self.touch()

    def __repr__(self) -> str:
        return (
            f"<ArchitectProfile id={self.id[:8]} name={self.name!r} "
            f"stage={self.current_stage} sessions={self.session_count}>"
        )


class ArchitectRepository:
    """In-memory store for Architect profiles.

    Production deployment would back this with a database.
    The interface is backend-agnostic — swap the backend without changing callers.
    """

    def __init__(self) -> None:
        self._profiles: dict[str, ArchitectProfile] = {}   # id -> profile
        self._name_index: dict[str, str] = {}              # name -> id

    def create(self, name: str, foundation_statement: str = "",
               elemental_signature: Optional[str] = None) -> ArchitectProfile:
        """Register a new Architect. Raises if name already exists."""
        if name in self._name_index:
            raise ValueError(
                f"Architect '{name}' already exists. "
                f"Use get_or_create() or get_by_name()."
            )
        profile = ArchitectProfile(
            name=name,
            foundation_statement=foundation_statement,
            elemental_signature=elemental_signature,
        )
        self._profiles[profile.id] = profile
        self._name_index[name] = profile.id
        return profile

    def get(self, architect_id: str) -> Optional[ArchitectProfile]:
        return self._profiles.get(architect_id)

    def get_by_name(self, name: str) -> Optional[ArchitectProfile]:
        profile_id = self._name_index.get(name)
        if not profile_id:
            return None
        return self._profiles.get(profile_id)

    def get_or_create(
        self,
        name: str,
        foundation_statement: str = "",
        elemental_signature: Optional[str] = None,
    ) -> tuple[ArchitectProfile, bool]:
        """Return (profile, created). created=True if new profile was registered."""
        existing = self.get_by_name(name)
        if existing:
            return existing, False
        new_profile = self.create(name, foundation_statement, elemental_signature)
        return new_profile, True

    def update(self, profile: ArchitectProfile) -> None:
        """Persist updates to an existing profile."""
        if profile.id not in self._profiles:
            raise KeyError(f"Architect {profile.id[:8]} not found.")
        profile.touch()
        self._profiles[profile.id] = profile

    def list_all(self) -> list[ArchitectProfile]:
        return list(self._profiles.values())

    def count(self) -> int:
        return len(self._profiles)

    def __repr__(self) -> str:
        return f"<ArchitectRepository profiles={self.count()}>"

"""
core/identity/avatar/avatar_registry.py

AvatarRegistry — multi-avatar lifecycle manager.

Design:
- In-memory store keyed by avatar_id, with optional persistence via
  a supplied storage adapter (any object with put/get/delete methods
  matching the WarmTier interface).
- Supports lookup by id, by name, and by tag.
- Enforces a single root avatar (SOVEREIGN mode) per registry instance.
- Thread-safe via a reentrant lock.

Canon Refs: C01, C04, C15
"""

from __future__ import annotations

import threading
from typing import Any, Dict, Iterator, List, Optional

from .avatar_profile import AvatarProfile, ExpressionMode
from .avatar_renderer import AvatarRenderer, RenderedState


# Storage adapter protocol (duck-typed)
class _StorageAdapter:
    def put(self, key: str, value: Any, **kwargs: Any) -> None: ...
    def get(self, key: str) -> Optional[Any]: ...
    def delete(self, key: str) -> bool: ...


class AvatarRegistry:
    """
    Lifecycle registry for GAIA avatars.

    Parameters
    ----------
    storage : optional storage adapter (WarmTier-compatible)
        When provided, profiles are persisted on every write.
    renderer : AvatarRenderer | None
        Renderer used by render_avatar().  A default is created if omitted.
    """

    def __init__(
        self,
        storage: Optional[Any] = None,
        renderer: Optional[AvatarRenderer] = None,
    ) -> None:
        self._profiles: Dict[str, AvatarProfile] = {}
        self._lock = threading.RLock()
        self._storage = storage
        self._renderer = renderer or AvatarRenderer()
        self._root_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        profile: AvatarProfile,
        *,
        persist: bool = True,
    ) -> AvatarProfile:
        """
        Register a new avatar profile.
        Raises ValueError if a profile with the same id already exists.
        Raises PermissionError if trying to register a second SOVEREIGN.
        """
        with self._lock:
            if profile.id in self._profiles:
                raise ValueError(f"Avatar '{profile.id}' is already registered.")
            if profile.mode == ExpressionMode.SOVEREIGN:
                if self._root_id is not None:
                    raise PermissionError(
                        f"A SOVEREIGN avatar already exists: {self._root_id}. "
                        "Only one root avatar is allowed per registry."
                    )
                self._root_id = profile.id
            self._profiles[profile.id] = profile
            if persist and self._storage:
                self._storage.put(
                    f"avatar:{profile.id}",
                    profile.to_dict(),
                    tags=["avatar"] + profile.tags,
                )
        return profile

    def deregister(
        self,
        avatar_id: str,
        *,
        consent_token: Optional[str] = None,
    ) -> bool:
        """Remove an avatar from the registry.  Returns True if found."""
        with self._lock:
            if avatar_id not in self._profiles:
                return False
            profile = self._profiles[avatar_id]
            if profile.mode == ExpressionMode.SOVEREIGN and consent_token is None:
                raise PermissionError(
                    "Deregistering a SOVEREIGN avatar requires a consent_token."
                )
            del self._profiles[avatar_id]
            if avatar_id == self._root_id:
                self._root_id = None
            if self._storage:
                self._storage.delete(f"avatar:{avatar_id}")
        return True

    def update(
        self,
        profile: AvatarProfile,
        *,
        persist: bool = True,
    ) -> AvatarProfile:
        """Replace an existing profile with a mutated version."""
        with self._lock:
            if profile.id not in self._profiles:
                raise KeyError(f"Avatar '{profile.id}' not found. Use register() to add it.")
            self._profiles[profile.id] = profile
            if persist and self._storage:
                self._storage.put(
                    f"avatar:{profile.id}",
                    profile.to_dict(),
                    tags=["avatar"] + profile.tags,
                )
        return profile

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, avatar_id: str) -> Optional[AvatarProfile]:
        with self._lock:
            return self._profiles.get(avatar_id)

    def get_by_name(self, name: str) -> List[AvatarProfile]:
        with self._lock:
            return [p for p in self._profiles.values() if p.name == name]

    def get_by_tag(self, tag: str) -> List[AvatarProfile]:
        with self._lock:
            return [p for p in self._profiles.values() if tag in p.tags]

    def root(self) -> Optional[AvatarProfile]:
        """Return the SOVEREIGN root avatar, if one exists."""
        with self._lock:
            return self._profiles.get(self._root_id) if self._root_id else None

    def all(self) -> List[AvatarProfile]:
        with self._lock:
            return list(self._profiles.values())

    def __len__(self) -> int:
        with self._lock:
            return len(self._profiles)

    def __iter__(self) -> Iterator[AvatarProfile]:
        return iter(self.all())

    def __contains__(self, avatar_id: str) -> bool:
        with self._lock:
            return avatar_id in self._profiles

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render_avatar(self, avatar_id: str) -> Optional[RenderedState]:
        """Render the current expression state for an avatar."""
        profile = self.get(avatar_id)
        if profile is None:
            return None
        return self._renderer.render(profile)

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def load_from_storage(self, avatar_id: str) -> Optional[AvatarProfile]:
        """Pull a profile from storage into the in-memory registry."""
        if self._storage is None:
            return None
        data = self._storage.get(f"avatar:{avatar_id}")
        if data is None:
            return None
        profile = AvatarProfile.from_dict(data)
        with self._lock:
            self._profiles[profile.id] = profile
        return profile

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "total": len(self._profiles),
                "root_id": self._root_id,
                "modes": {
                    mode.value: sum(
                        1 for p in self._profiles.values() if p.mode == mode
                    )
                    for mode in ExpressionMode
                },
            }

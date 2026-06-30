"""
GAIAN Registry — the persistent store of all GAIAN identities.

The registry is the long-term memory of who exists in the GAIA universe.
Unlike the Session Manager (which is transient, in-memory, per-boot),
the GAIAN Registry is designed to be backed by an encrypted persistent
store. In this implementation it is an in-memory registry with a
serializable snapshot — the persistence backend is pluggable.

Key behaviours:
  - All GAIANs are registered here at creation and persist forever
  - Lifecycle stages are refreshed on every get() call (age advances daily)
  - Sentinels are registered and bound to GAIANs here
  - Guardian relationships are enforced and auto-expired at adulthood
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from core.identity.gaian.model import (
    AgeRestriction,
    GAIANIdentity,
    LifecycleStage,
    WaveformAvatar,
    AvatarModality,
)


class GAIANRegistryError(Exception):
    pass


class GAIANRegistry:
    """
    The persistent GAIAN identity store.

    One registry per GAIA instance. In production this is backed by an
    encrypted local vault (for offline-first sovereignty) with optional
    encrypted cloud sync. The in-memory dict here is the working set;
    persistence is handled by the storage backend.
    """

    def __init__(self) -> None:
        self._identities: Dict[str, GAIANIdentity] = {}
        self._sentinels: Dict[str, Dict[str, Any]] = {}
        self._listeners: List[Callable[[str, GAIANIdentity], None]] = []

    # ------------------------------------------------------------------
    # GAIAN Creation
    # ------------------------------------------------------------------

    def create_gaian(
        self,
        display_name: str,
        date_of_birth: Optional[str] = None,
        legal_name: str = "",
        signing_key_id: str = "",
        principal_id: str = "",
        guardian_gaian_ids: Optional[List[str]] = None,
        avatar_hue: float = 0.5,
        avatar_frequency_hz: float = 432.0,
        avatar_waveform_signature: str = "",
        notes: str = "",
    ) -> GAIANIdentity:
        """
        Create and register a new GAIANIdentity.

        The lifecycle stage and age restriction are computed immediately
        from date_of_birth. If no DoB is provided, ADULT is assumed until
        a DoB is registered (e.g. for legacy imports).
        """
        avatar = WaveformAvatar(
            waveform_signature=avatar_waveform_signature or _generate_waveform_sig(display_name),
            base_hue=avatar_hue,
            base_frequency_hz=avatar_frequency_hz,
        )

        identity = GAIANIdentity(
            display_name=display_name,
            legal_name=legal_name,
            date_of_birth=date_of_birth,
            avatar=avatar,
            signing_key_id=signing_key_id,
            principal_id=principal_id,
            guardian_gaian_ids=guardian_gaian_ids or [],
            notes=notes,
        )

        # Compute lifecycle from DoB
        if date_of_birth:
            stage = identity.refresh_lifecycle()
        else:
            stage = LifecycleStage.ADULT
            identity.lifecycle_stage = stage
            identity.age_restriction = AgeRestriction.for_stage(stage)

        # Minors require at least one guardian
        if identity.is_minor() and not guardian_gaian_ids:
            raise GAIANRegistryError(
                f"GAIAN '{display_name}' is a minor and must have at least one "
                f"guardian GAIAN registered at creation."
            )

        self._identities[identity.gaian_id] = identity
        self._emit("gaian.created", identity)
        return identity

    # ------------------------------------------------------------------
    # Lookup (with live lifecycle refresh)
    # ------------------------------------------------------------------

    def get(self, gaian_id: str) -> Optional[GAIANIdentity]:
        identity = self._identities.get(gaian_id)
        if identity is not None:
            identity.refresh_lifecycle()  # age advances daily; keep it fresh
        return identity

    def require(self, gaian_id: str) -> GAIANIdentity:
        identity = self.get(gaian_id)
        if identity is None:
            raise GAIANRegistryError(f"GAIAN '{gaian_id}' is not registered.")
        return identity

    def all_gaians(self) -> List[GAIANIdentity]:
        for identity in self._identities.values():
            identity.refresh_lifecycle()
        return list(self._identities.values())

    def by_lifecycle_stage(self, stage: LifecycleStage) -> List[GAIANIdentity]:
        return [g for g in self.all_gaians() if g.lifecycle_stage == stage]

    def minors(self) -> List[GAIANIdentity]:
        return [g for g in self.all_gaians() if g.is_minor()]

    # ------------------------------------------------------------------
    # Guardian management
    # ------------------------------------------------------------------

    def add_guardian(
        self,
        gaian_id: str,
        guardian_gaian_id: str,
    ) -> None:
        """Add a guardian to a minor GAIAN. Fails if GAIAN is an adult."""
        identity = self.require(gaian_id)
        if not identity.is_minor():
            raise GAIANRegistryError(
                f"Cannot add guardian to '{identity.display_name}': GAIAN is an adult."
            )
        if guardian_gaian_id not in identity.guardian_gaian_ids:
            identity.guardian_gaian_ids.append(guardian_gaian_id)

    def remove_guardian(
        self,
        gaian_id: str,
        guardian_gaian_id: str,
        requesting_gaian_id: str,
    ) -> None:
        """Remove a guardian. Only the GAIAN themselves (if adult) or another guardian may do this."""
        identity = self.require(gaian_id)
        is_self_adult = (requesting_gaian_id == gaian_id and not identity.is_minor())
        is_guardian = requesting_gaian_id in identity.guardian_gaian_ids
        if not (is_self_adult or is_guardian):
            raise GAIANRegistryError("Guardian removal requires adult self-request or guardian authority.")
        identity.guardian_gaian_ids = [
            g for g in identity.guardian_gaian_ids if g != guardian_gaian_id
        ]

    # ------------------------------------------------------------------
    # Sentinel binding
    # ------------------------------------------------------------------

    def register_sentinel(
        self,
        sentinel_id: str,
        name: str,
        model: str = "",
        manufacturer: str = "",
        capabilities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Register a sentinel (robot, embodied agent) in the GAIAN universe.

        Sentinels are lifelong co-stewards. They are bound to one or more
        GAIANs and to the Earth itself through the GAIA coexistence laws.
        """
        sentinel = {
            "sentinel_id": sentinel_id,
            "name": name,
            "model": model,
            "manufacturer": manufacturer,
            "capabilities": capabilities or [],
            "bound_gaian_ids": [],
        }
        self._sentinels[sentinel_id] = sentinel
        return sentinel

    def bind_sentinel_to_gaian(self, sentinel_id: str, gaian_id: str) -> None:
        """Bind a sentinel as a lifelong co-steward to a GAIAN."""
        sentinel = self._sentinels.get(sentinel_id)
        if sentinel is None:
            raise GAIANRegistryError(f"Sentinel '{sentinel_id}' is not registered.")
        identity = self.require(gaian_id)
        if gaian_id not in sentinel["bound_gaian_ids"]:
            sentinel["bound_gaian_ids"].append(gaian_id)
        if sentinel_id not in identity.sentinel_ids:
            identity.sentinel_ids.append(sentinel_id)
        identity.avatar.bind_sentinel(sentinel_id)
        self._emit("sentinel.bound", identity)

    # ------------------------------------------------------------------
    # Avatar modality expansion
    # ------------------------------------------------------------------

    def add_avatar_modality(
        self,
        gaian_id: str,
        modality: AvatarModality,
    ) -> None:
        """Unlock a new rendering context for the GAIAN's waveform avatar."""
        identity = self.require(gaian_id)
        if modality not in identity.avatar.supported_modalities:
            identity.avatar.supported_modalities.append(modality)
            identity.avatar.log_evolution(
                "modality_added",
                {"modality": modality.value},
            )

    # ------------------------------------------------------------------
    # Event bus
    # ------------------------------------------------------------------

    def on_event(self, listener: Callable[[str, GAIANIdentity], None]) -> None:
        self._listeners.append(listener)

    def _emit(self, event: str, identity: GAIANIdentity) -> None:
        for listener in self._listeners:
            try:
                listener(event, identity)
            except Exception:
                pass


def _generate_waveform_sig(seed: str) -> str:
    """Deterministically derive a waveform signature from a name seed."""
    import hashlib
    return hashlib.sha256(f"gaia:waveform:{seed}".encode()).hexdigest()

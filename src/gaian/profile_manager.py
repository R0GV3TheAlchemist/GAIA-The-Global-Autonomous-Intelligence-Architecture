"""
src/gaian/profile_manager.py

GaianProfileManager — load, save, migrate, and update GAIAN profiles.

Phase 2 scaffold: method signatures and docstrings are complete;
core logic is marked with TODO stubs ready for implementation.

Issue: #825
Canon: docs/canon/GAIAN_IDENTITY.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.gaian.runtimetypes import GAIANProfileModel, LCIHistoryEntry


class ProfileNotFoundError(Exception):
    """Raised when a requested architect_id has no persisted profile."""


class ProfileMigrationError(Exception):
    """Raised when a profile cannot be migrated to the target version."""


class GaianProfileManager:
    """
    Operational service layer for GAIANProfileModel.

    Responsibilities:
      - Persist profiles to/from storage (default: JSON on disk)
      - Migrate profiles between schema versions
      - Apply LCI updates and recompute trend
      - Provide a recovery reset path
    """

    SUPPORTED_VERSIONS = (1, 2)

    def __init__(self, storage_dir: Optional[Path] = None) -> None:
        self.storage_dir = storage_dir or Path.home() / ".nexus" / "profiles"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load_profile(self, architect_id: str) -> GAIANProfileModel:
        """
        Load and return the persisted profile for *architect_id*.

        Raises:
            ProfileNotFoundError: if no profile exists for this ID.
        """
        # TODO: deserialise from self.storage_dir / f"{architect_id}.json"
        raise ProfileNotFoundError(f"No profile found for architect_id={architect_id!r}")

    def save_profile(self, profile: GAIANProfileModel) -> None:
        """
        Persist *profile* to storage, bumping profile_version by 1.

        The profile is written atomically (write-then-rename).
        """
        # TODO: serialise to self.storage_dir / f"{profile.architect_id}.json"
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Migration
    # ------------------------------------------------------------------

    def migrate_profile(
        self,
        profile: GAIANProfileModel,
        target_version: int,
    ) -> GAIANProfileModel:
        """
        Migrate *profile* to *target_version*.

        Currently supports v1 → v2 only.

        Raises:
            ProfileMigrationError: if the migration path is unsupported.
        """
        if target_version not in self.SUPPORTED_VERSIONS:
            raise ProfileMigrationError(
                f"Unsupported target version: {target_version}. "
                f"Supported: {self.SUPPORTED_VERSIONS}"
            )
        if profile.profile_version == target_version:
            return profile
        # TODO: implement v1 → v2 field mapping
        raise NotImplementedError

    # ------------------------------------------------------------------
    # LCI updates
    # ------------------------------------------------------------------

    def update_lci(
        self,
        profile: GAIANProfileModel,
        new_phi: float,
        session_id: str,
        timestamp: Optional[str] = None,
    ) -> GAIANProfileModel:
        """
        Append a new LCI reading to *profile*, recompute `lci_trend`,
        apply baseline drift, and return the updated profile.

        The original profile is not mutated; a new instance is returned.
        """
        import dataclasses
        from datetime import datetime, timezone

        ts = timestamp or datetime.now(timezone.utc).isoformat()
        entry = LCIHistoryEntry(phi=new_phi, timestamp=ts, session_id=session_id)

        new_history = list(profile.lci_history) + [entry]
        new_trend = profile.compute_lci_trend(current_phi=new_phi)

        # TODO: baseline drift logic (e.g. exponential moving average)
        return dataclasses.replace(
            profile,
            lci_history=new_history,
            lci_trend=new_trend,
            total_sessions=profile.total_sessions + 1,
        )

    # ------------------------------------------------------------------
    # Recovery reset
    # ------------------------------------------------------------------

    def reset_to_baseline(self, profile: GAIANProfileModel) -> GAIANProfileModel:
        """
        Return a copy of *profile* with LCI history cleared and trend
        reset to 'stable'. Does NOT alter lci_baseline.

        Used during recovery from a volatile state.
        """
        import dataclasses

        return dataclasses.replace(
            profile,
            lci_history=[],
            lci_trend="stable",
        )

"""
IdentityPersistence — persist GAIAN identity and genesis records.

Directory layout under GAIA_ROOT:

  gaians/<gaian_id>/
    identity.json    — mutable: name, lifecycle stage, cognitive defaults
    genesis.json     — IMMUTABLE after first write (birth answers)
    avatar.json      — element waveform snapshot

Genesis immutability:
  Once genesis.json exists, save_genesis() raises PermissionError.
  This mirrors the write-once guarantee in GAIAFilesystem.GAIANHome.
  The persistence layer enforces it independently so it holds
  even when the filesystem layer is bypassed.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from core.persistence.store import PersistenceStore


class IdentityPersistence:
    """
    Disk-backed persistence for a single GAIAN\'s identity.
    """

    IDENTITY_FILE = "identity.json"
    GENESIS_FILE  = "genesis.json"
    AVATAR_FILE   = "avatar.json"

    def __init__(self, store: PersistenceStore, gaian_id: str) -> None:
        self._store    = store
        self._gaian_id = gaian_id
        self._base     = f"gaians/{gaian_id}"

    # ------------------------------------------------------------------
    # Identity (mutable)
    # ------------------------------------------------------------------

    def save_identity(self, data: Dict[str, Any]) -> None:
        self._store.write(f"{self._base}/{self.IDENTITY_FILE}", data)

    def load_identity(self) -> Optional[Dict[str, Any]]:
        return self._store.read(f"{self._base}/{self.IDENTITY_FILE}")

    # ------------------------------------------------------------------
    # Genesis (immutable)
    # ------------------------------------------------------------------

    def save_genesis(self, data: Dict[str, Any]) -> None:
        path = f"{self._base}/{self.GENESIS_FILE}"
        if self._store.exists(path):
            raise PermissionError(
                f"genesis.json for GAIAN {self._gaian_id} is immutable "
                f"and cannot be overwritten."
            )
        self._store.write(path, data)

    def load_genesis(self) -> Optional[Dict[str, Any]]:
        return self._store.read(f"{self._base}/{self.GENESIS_FILE}")

    def genesis_exists(self) -> bool:
        return self._store.exists(f"{self._base}/{self.GENESIS_FILE}")

    # ------------------------------------------------------------------
    # Avatar waveform snapshot
    # ------------------------------------------------------------------

    def save_avatar(self, data: Dict[str, Any]) -> None:
        self._store.write(f"{self._base}/{self.AVATAR_FILE}", data)

    def load_avatar(self) -> Optional[Dict[str, Any]]:
        return self._store.read(f"{self._base}/{self.AVATAR_FILE}")

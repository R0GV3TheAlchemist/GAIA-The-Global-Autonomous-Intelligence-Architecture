"""
RegistryPersistence — persist the GAIANRegistry index.

File layout under GAIA_ROOT:

  registry/
    index.json       — list of all registered gaian_ids + minimal metadata
    <gaian_id>.json  — per-GAIAN registry entry (full serialised GAIANIdentity)

The registry index is a fast lookup table: on boot it tells the
PrimordialSession which GAIAN IDs exist so it can restore each one's
full IdentityPersistence and MemoryPersistence in turn.

Concurrency note:
  The registry is written by a single process (the OS server).
  No locking is needed for single-worker deployments.
  Multi-worker support requires an external registry backend
  (flagged in GAIA_WORKERS note in .env.example).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.persistence.store import PersistenceStore


class RegistryPersistence:

    INDEX_FILE = "registry/index.json"
    ENTRY_DIR  = "registry"

    def __init__(self, store: PersistenceStore) -> None:
        self._store = store

    def _entry_path(self, gaian_id: str) -> str:
        return f"{self.ENTRY_DIR}/{gaian_id}.json"

    # ------------------------------------------------------------------
    # Index
    # ------------------------------------------------------------------

    def save_index(self, gaian_ids: List[str],
                   metadata: Optional[Dict[str, Any]] = None) -> None:
        """Persist the registry index (list of gaian_ids + optional meta)."""
        self._store.write(self.INDEX_FILE, {
            "gaian_ids": gaian_ids,
            "count":     len(gaian_ids),
            "metadata":  metadata or {},
        })

    def load_index(self) -> List[str]:
        """Returns the list of known gaian_ids, or [] if not found."""
        data = self._store.read(self.INDEX_FILE)
        if not data:
            return []
        return data.get("gaian_ids", [])

    # ------------------------------------------------------------------
    # Per-GAIAN entry
    # ------------------------------------------------------------------

    def save_entry(self, gaian_id: str, data: Dict[str, Any]) -> None:
        self._store.write(self._entry_path(gaian_id), data)

    def load_entry(self, gaian_id: str) -> Optional[Dict[str, Any]]:
        return self._store.read(self._entry_path(gaian_id))

    def delete_entry(self, gaian_id: str) -> None:
        self._store.delete(self._entry_path(gaian_id))
        # Reload and rewrite index without this ID
        ids = self.load_index()
        ids = [i for i in ids if i != gaian_id]
        self.save_index(ids)

    def all_gaian_ids(self) -> List[str]:
        """Scan the registry dir for .json files as a fallback index."""
        names = self._store.list_dir(self.ENTRY_DIR)
        return [
            n[:-5] for n in names
            if n.endswith(".json") and n != "index.json"
        ]

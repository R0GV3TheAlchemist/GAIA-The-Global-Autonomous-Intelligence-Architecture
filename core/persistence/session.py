"""
SessionPersistence — persist boot manifests and GAIA sovereign memory.

File layout under GAIA_ROOT:

  session/
    manifests/
      boot_<N>_<session_id[:8]>.json   — one manifest per boot
    latest_manifest.json               — symlink-equivalent: latest boot
  gaia_memory/
    fragments/
      <fragment_id>.json               — GAIA\'s own sovereign memory
    stats.json

Boot manifests accumulate over the life of the OS. A developer
can inspect them to see every boot\'s status, Schumann reading,
GAIAN count, and any degraded phases.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.persistence.store import PersistenceStore


class SessionPersistence:

    MANIFESTS_DIR    = "session/manifests"
    LATEST_MANIFEST  = "session/latest_manifest.json"
    GAIA_MEM_DIR     = "gaia_memory/fragments"
    GAIA_STATS       = "gaia_memory/stats.json"

    def __init__(self, store: PersistenceStore) -> None:
        self._store = store

    # ------------------------------------------------------------------
    # Boot manifests
    # ------------------------------------------------------------------

    def save_manifest(self, manifest_data: Dict[str, Any]) -> None:
        boot_n  = manifest_data.get("boot_number", 0)
        sid     = manifest_data.get("session_id", "unknown")[:8]
        fname   = f"boot_{boot_n:06d}_{sid}.json"
        self._store.write(f"{self.MANIFESTS_DIR}/{fname}", manifest_data)
        self._store.write(self.LATEST_MANIFEST, manifest_data)

    def load_latest_manifest(self) -> Optional[Dict[str, Any]]:
        return self._store.read(self.LATEST_MANIFEST)

    def load_all_manifests(self) -> List[Dict[str, Any]]:
        names = self._store.list_dir(self.MANIFESTS_DIR)
        result = []
        for name in sorted(names):
            if name.endswith(".json"):
                data = self._store.read(f"{self.MANIFESTS_DIR}/{name}")
                if data:
                    result.append(data)
        return result

    def boot_count(self) -> int:
        return len(self._store.list_dir(self.MANIFESTS_DIR))

    # ------------------------------------------------------------------
    # GAIA sovereign memory
    # ------------------------------------------------------------------

    def save_gaia_fragment(self, fragment_data: Dict[str, Any]) -> None:
        fid = fragment_data.get("fragment_id", "unknown")
        self._store.write(f"{self.GAIA_MEM_DIR}/{fid}.json", fragment_data)

    def load_gaia_fragments(self) -> List[Dict[str, Any]]:
        names = self._store.list_dir(self.GAIA_MEM_DIR)
        result = []
        for name in names:
            if name.endswith(".json"):
                fid = name[:-5]
                data = self._store.read(f"{self.GAIA_MEM_DIR}/{fid}.json")
                if data:
                    result.append(data)
        return result

    def save_gaia_stats(self, stats: Dict[str, Any]) -> None:
        self._store.write(self.GAIA_STATS, stats)

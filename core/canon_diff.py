"""
core/canon_diff.py

Canon diff tooling — compare two Canon versions and surface
added, removed, and modified entries.
Issue #249.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from core.canon_store import CanonStore, CanonEntry


@dataclass
class DiffEntry:
    """A single change between two Canon versions."""
    change: str          # "added" | "removed" | "modified"
    entry_id: str
    title: str
    before_body: str | None
    after_body: str | None
    before_hash: str | None
    after_hash: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CanonDiffResult:
    """Full diff between two Canon versions."""
    version_before: str
    version_after: str
    added: list[DiffEntry]
    removed: list[DiffEntry]
    modified: list[DiffEntry]

    @property
    def total_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.modified)

    def summary(self) -> str:
        return (
            f"Canon diff {self.version_before} → {self.version_after}: "
            f"+{len(self.added)} added, "
            f"-{len(self.removed)} removed, "
            f"~{len(self.modified)} modified "
            f"({self.total_changes} total changes)"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "version_before": self.version_before,
            "version_after": self.version_after,
            "summary": self.summary(),
            "added": [d.to_dict() for d in self.added],
            "removed": [d.to_dict() for d in self.removed],
            "modified": [d.to_dict() for d in self.modified],
        }


class CanonDiff:
    """
    Compares two Canon snapshots or live CanonStore states.

    Usage:
        diff = CanonDiff(store)
        result = diff.compare_versions("0.1.0", "0.1.3")
        print(result.summary())

        # Or compare two raw entry dicts directly:
        result = CanonDiff.compare_dicts(entries_before, entries_after, "v1", "v2")
    """

    def __init__(self, store: CanonStore) -> None:
        self._store = store

    def compare_versions(
        self, version_before: str, version_after: str
    ) -> CanonDiffResult:
        """
        Compare two snapshot versions already stored in the CanonStore.
        Pass version_after="live" to compare against the current live state.
        """
        snap_before = self._store.load_snapshot(version_before)
        entries_before: dict[str, dict] = snap_before.get("entries", {})

        if version_after == "live":
            entries_after = {
                k: v.to_dict() for k, v in
                {e.id: e for e in self._store.all_entries()}.items()
            }
            ver_after = self._store.version
        else:
            snap_after = self._store.load_snapshot(version_after)
            entries_after = snap_after.get("entries", {})
            ver_after = version_after

        return self.compare_dicts(
            entries_before, entries_after, version_before, ver_after
        )

    @staticmethod
    def compare_dicts(
        before: dict[str, dict],
        after: dict[str, dict],
        version_before: str,
        version_after: str,
    ) -> CanonDiffResult:
        """Core diff logic on plain entry dicts."""
        added: list[DiffEntry] = []
        removed: list[DiffEntry] = []
        modified: list[DiffEntry] = []

        all_ids = set(before) | set(after)

        for eid in sorted(all_ids):
            b = before.get(eid)
            a = after.get(eid)

            if b is None and a is not None:
                added.append(DiffEntry(
                    change="added",
                    entry_id=eid,
                    title=a.get("title", ""),
                    before_body=None,
                    after_body=a.get("body"),
                    before_hash=None,
                    after_hash=a.get("hash"),
                ))
            elif a is None and b is not None:
                removed.append(DiffEntry(
                    change="removed",
                    entry_id=eid,
                    title=b.get("title", ""),
                    before_body=b.get("body"),
                    after_body=None,
                    before_hash=b.get("hash"),
                    after_hash=None,
                ))
            elif b is not None and a is not None:
                if b.get("hash") != a.get("hash"):
                    modified.append(DiffEntry(
                        change="modified",
                        entry_id=eid,
                        title=a.get("title", b.get("title", "")),
                        before_body=b.get("body"),
                        after_body=a.get("body"),
                        before_hash=b.get("hash"),
                        after_hash=a.get("hash"),
                    ))

        return CanonDiffResult(
            version_before=version_before,
            version_after=version_after,
            added=added,
            removed=removed,
            modified=modified,
        )

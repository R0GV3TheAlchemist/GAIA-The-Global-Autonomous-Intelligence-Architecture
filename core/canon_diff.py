"""
core/canon_diff.py
Canon Diff — computes structural diffs between CanonEntry versions.

Public API
----------
CanonDiffEntry  : single-entry change record (added / removed / modified)
CanonDiffReport : collection result from compare_dicts() / compare_versions()
CanonDiff       : static compare_dicts() + instance compare_versions()

Legacy (backward compat)
------------------------
CanonDiffResult : original per-entry diff result (still exported)
CanonDiff.diff()  / CanonDiff.apply() : unchanged field-level helpers
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.canon_store import CanonStore


# ---------------------------------------------------------------------------
# New rich diff types (Issue #249)
# ---------------------------------------------------------------------------

@dataclass
class CanonDiffEntry:
    """
    Records a single entry-level change between two Canon snapshots.

    Fields
    ------
    entry_id      : stable Canon slug (e.g. "C01")
    action        : "added" | "removed" | "modified"
    before_body   : body text before the change (empty string for added)
    after_body    : body text after the change (empty string for removed)
    changed_fields: list of field names whose values differ (for modified)
    """
    entry_id:      str       = ""
    action:        str       = ""          # "added" | "removed" | "modified"
    before_body:   str       = ""
    after_body:    str       = ""
    changed_fields: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "entry_id":       self.entry_id,
            "action":         self.action,
            "before_body":    self.before_body,
            "after_body":     self.after_body,
            "changed_fields": self.changed_fields,
        }


@dataclass
class CanonDiffReport:
    """
    Aggregated diff result produced by CanonDiff.compare_dicts().

    Fields
    ------
    version_from : semver string of the older snapshot
    version_to   : semver string of the newer snapshot
    added        : entries present in *after* but not in *before*
    removed      : entries present in *before* but not in *after*
    modified     : entries present in both but with changed fields
    """
    version_from: str                  = ""
    version_to:   str                  = ""
    added:        List[CanonDiffEntry] = field(default_factory=list)
    removed:      List[CanonDiffEntry] = field(default_factory=list)
    modified:     List[CanonDiffEntry] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        """Total number of changed entries (added + removed + modified)."""
        return len(self.added) + len(self.removed) + len(self.modified)

    def summary(self) -> str:
        """
        Return a one-line human-readable summary.

        Example: "Canon diff 0.1.0 → 0.1.1: +1 added, -0 removed, ~0 modified"
        """
        return (
            f"Canon diff {self.version_from} → {self.version_to}: "
            f"+{len(self.added)} added, "
            f"-{len(self.removed)} removed, "
            f"~{len(self.modified)} modified"
        )

    def to_dict(self) -> dict:
        return {
            "version_from": self.version_from,
            "version_to":   self.version_to,
            "added":        [e.to_dict() for e in self.added],
            "removed":      [e.to_dict() for e in self.removed],
            "modified":     [e.to_dict() for e in self.modified],
            "total_changes": self.total_changes,
        }


# ---------------------------------------------------------------------------
# Legacy per-entry diff types (kept for backward compat)
# ---------------------------------------------------------------------------

@dataclass
class CanonDiffResult:
    """Legacy result of diffing two CanonEntry field dicts (CanonDiff.diff)."""

    entry_id:   str              = ""
    added:      Dict[str, Any]   = field(default_factory=dict)
    removed:    Dict[str, Any]   = field(default_factory=dict)
    changed:    Dict[str, Any]   = field(default_factory=dict)
    unchanged:  List[str]        = field(default_factory=list)
    is_identical: bool           = False

    def to_dict(self) -> dict:
        return {
            "entry_id":    self.entry_id,
            "added":       self.added,
            "removed":     self.removed,
            "changed":     self.changed,
            "unchanged":   self.unchanged,
            "is_identical": self.is_identical,
        }


# ---------------------------------------------------------------------------
# CanonDiff
# ---------------------------------------------------------------------------

class CanonDiff:
    """
    Computes structural diffs between two Canon snapshots.

    Static usage (no store needed)
    ------------------------------
    report = CanonDiff.compare_dicts(before_dict, after_dict, "0.1.0", "0.1.1")

    Instance usage (with a CanonStore)
    -----------------------------------
    differ = CanonDiff(store)
    report = differ.compare_versions("0.1.1", "0.1.2")
    """

    def __init__(self, store: Optional["CanonStore"] = None) -> None:
        self._store = store

    # ------------------------------------------------------------------
    # Public static API
    # ------------------------------------------------------------------

    @staticmethod
    def compare_dicts(
        before: Dict[str, Any],
        after:  Dict[str, Any],
        version_from: str = "",
        version_to:   str = "",
    ) -> CanonDiffReport:
        """
        Compare two entry-keyed dicts (as produced by snapshot["entries"])
        and return a CanonDiffReport.

        Each dict maps entry_id -> entry_dict (with at least an "id"
        and "body" key; all other keys are compared for modified tracking).
        """
        added:    List[CanonDiffEntry] = []
        removed:  List[CanonDiffEntry] = []
        modified: List[CanonDiffEntry] = []

        all_ids = set(before) | set(after)

        for eid in sorted(all_ids):
            if eid not in before:
                # New entry
                added.append(CanonDiffEntry(
                    entry_id=eid,
                    action="added",
                    before_body="",
                    after_body=after[eid].get("body", ""),
                ))
            elif eid not in after:
                # Removed entry
                removed.append(CanonDiffEntry(
                    entry_id=eid,
                    action="removed",
                    before_body=before[eid].get("body", ""),
                    after_body="",
                ))
            else:
                b = before[eid]
                a = after[eid]
                changed_fields = [
                    k for k in (set(b) | set(a))
                    if b.get(k) != a.get(k)
                ]
                if changed_fields:
                    modified.append(CanonDiffEntry(
                        entry_id=eid,
                        action="modified",
                        before_body=b.get("body", ""),
                        after_body=a.get("body", ""),
                        changed_fields=sorted(changed_fields),
                    ))

        return CanonDiffReport(
            version_from=version_from,
            version_to=version_to,
            added=added,
            removed=removed,
            modified=modified,
        )

    def compare_versions(
        self,
        version_from: str,
        version_to:   str,
    ) -> CanonDiffReport:
        """
        Compare two persisted snapshots from the attached CanonStore.

        Raises
        ------
        RuntimeError  : if no CanonStore was provided at construction time.
        FileNotFoundError : if either snapshot does not exist.
        """
        if self._store is None:
            raise RuntimeError(
                "CanonDiff must be constructed with a CanonStore to use compare_versions()."
            )
        before_snap = self._store.load_snapshot(version_from)
        after_snap  = self._store.load_snapshot(version_to)
        return CanonDiff.compare_dicts(
            before=before_snap.get("entries", {}),
            after=after_snap.get("entries", {}),
            version_from=version_from,
            version_to=version_to,
        )

    # ------------------------------------------------------------------
    # Legacy field-level diff helpers (unchanged)
    # ------------------------------------------------------------------

    @staticmethod
    def diff(
        entry_id: str,
        old: Dict[str, Any],
        new: Dict[str, Any],
    ) -> CanonDiffResult:
        """Field-level diff of two entry dicts. Returns a legacy CanonDiffResult."""
        all_keys = set(old) | set(new)
        added: Dict[str, Any]   = {}
        removed: Dict[str, Any] = {}
        changed: Dict[str, Any] = {}
        unchanged: List[str]    = []

        for key in all_keys:
            if key not in old:
                added[key] = new[key]
            elif key not in new:
                removed[key] = old[key]
            elif old[key] != new[key]:
                changed[key] = {"old": old[key], "new": new[key]}
            else:
                unchanged.append(key)

        return CanonDiffResult(
            entry_id=entry_id,
            added=added,
            removed=removed,
            changed=changed,
            unchanged=unchanged,
            is_identical=(not added and not removed and not changed),
        )

    @staticmethod
    def apply(
        base: Dict[str, Any],
        diff_result: CanonDiffResult,
    ) -> Dict[str, Any]:
        """Apply a legacy CanonDiffResult to a base dict, returning the patched dict."""
        result = dict(base)
        for key in diff_result.removed:
            result.pop(key, None)
        for key, value in diff_result.added.items():
            result[key] = value
        for key, values in diff_result.changed.items():
            result[key] = values["new"]
        return result

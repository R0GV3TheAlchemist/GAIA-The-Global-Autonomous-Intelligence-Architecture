"""
core/canon_store.py

Canon as an explicit, versioned, inspectable value system.
Issue #249 — Governance: Canon versioning, amendment workflow,
conflict detection, and regulatory export.
"""

from __future__ import annotations

import json
import hashlib
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CanonEntry:
    """A single versioned Canon passage."""
    id: str                          # stable slug, e.g. "C01"
    title: str
    body: str
    tags: list[str] = field(default_factory=list)
    source_file: str = ""           # originating .md file
    added_in: str = ""              # semver that introduced this entry
    hash: str = ""                  # SHA-256 of body for change detection

    def __post_init__(self) -> None:
        if not self.hash:
            self.hash = _hash_body(self.body)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Amendment:
    """A single Canon amendment record."""
    amendment_id: str
    proposed_by: str                 # Gaian username or system
    proposed_at: str                 # ISO-8601 timestamp
    action: str                      # "add" | "update" | "remove"
    entry_id: str
    previous_body: str | None
    new_body: str | None
    justification: str
    status: str = "pending"          # "pending" | "approved" | "rejected"
    reviewed_by: str | None = None
    reviewed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ConflictReport:
    """Describes a detected conflict between two Canon entries."""
    entry_a: str
    entry_b: str
    reason: str
    severity: str = "warning"        # "warning" | "critical"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash_body(body: str) -> str:
    return hashlib.sha256(body.encode()).hexdigest()[:16]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bump_patch(version: str) -> str:
    """Increment patch component: '1.2.3' -> '1.2.4'."""
    parts = version.lstrip("v").split(".")
    if len(parts) != 3:
        return version
    parts[2] = str(int(parts[2]) + 1)
    return ".".join(parts)


# ---------------------------------------------------------------------------
# CanonStore
# ---------------------------------------------------------------------------

class CanonStore:
    """
    Manages the versioned, inspectable Canon for a GAIA instance.

    Storage layout (all under `store_path`):
        entries.json       — active Canon entries keyed by id
        amendments.json    — ordered amendment ledger
        version.txt        — current semantic version string
        snapshots/         — frozen per-version snapshots
    """

    def __init__(self, store_path: str | Path = "data/canon_store") -> None:
        self.store_path = Path(store_path)
        self._entries_file = self.store_path / "entries.json"
        self._amendments_file = self.store_path / "amendments.json"
        self._version_file = self.store_path / "version.txt"
        self._snapshots_dir = self.store_path / "snapshots"
        self._entries: dict[str, CanonEntry] = {}
        self._amendments: list[Amendment] = []
        self._version: str = "0.1.0"
        self._load()

    # ------------------------------------------------------------------
    # Public API — read
    # ------------------------------------------------------------------

    @property
    def version(self) -> str:
        return self._version

    def get(self, entry_id: str) -> CanonEntry | None:
        return self._entries.get(entry_id)

    def all_entries(self) -> list[CanonEntry]:
        return list(self._entries.values())

    def search(self, query: str) -> list[CanonEntry]:
        """Simple case-insensitive full-text search over title + body."""
        q = query.lower()
        return [
            e for e in self._entries.values()
            if q in e.title.lower() or q in e.body.lower()
        ]

    def pending_amendments(self) -> list[Amendment]:
        return [a for a in self._amendments if a.status == "pending"]

    # ------------------------------------------------------------------
    # Public API — write (amendment workflow)
    # ------------------------------------------------------------------

    def propose_amendment(
        self,
        action: str,
        entry_id: str,
        proposed_by: str,
        justification: str,
        new_body: str | None = None,
        new_title: str | None = None,
        tags: list[str] | None = None,
    ) -> Amendment:
        """
        Propose an amendment.  Returns the pending Amendment record.
        action: "add" | "update" | "remove"
        """
        if action not in ("add", "update", "remove"):
            raise ValueError(f"Invalid action: {action!r}")
        if action == "add" and entry_id in self._entries:
            raise ValueError(f"Entry {entry_id!r} already exists — use 'update'.")
        if action in ("update", "remove") and entry_id not in self._entries:
            raise ValueError(f"Entry {entry_id!r} not found — cannot {action}.")

        existing = self._entries.get(entry_id)
        amendment = Amendment(
            amendment_id=f"AMD-{len(self._amendments) + 1:04d}",
            proposed_by=proposed_by,
            proposed_at=_now_iso(),
            action=action,
            entry_id=entry_id,
            previous_body=existing.body if existing else None,
            new_body=new_body,
            justification=justification,
            status="pending",
        )
        self._amendments.append(amendment)
        self._save_amendments()
        return amendment

    def approve_amendment(
        self,
        amendment_id: str,
        reviewed_by: str,
        new_title: str | None = None,
        tags: list[str] | None = None,
    ) -> CanonEntry | None:
        """
        Approve a pending amendment, apply it, bump the version, and
        snapshot the current state.  Returns the affected CanonEntry.
        """
        amd = self._find_amendment(amendment_id)
        if amd.status != "pending":
            raise ValueError(f"Amendment {amendment_id} is already {amd.status}.")

        entry: CanonEntry | None = None

        if amd.action == "add":
            if amd.new_body is None:
                raise ValueError("new_body is required for 'add' amendments.")
            entry = CanonEntry(
                id=amd.entry_id,
                title=new_title or amd.entry_id,
                body=amd.new_body,
                tags=tags or [],
                added_in=_bump_patch(self._version),
            )
            self._entries[amd.entry_id] = entry

        elif amd.action == "update":
            existing = self._entries[amd.entry_id]
            existing.body = amd.new_body or existing.body
            existing.hash = _hash_body(existing.body)
            if new_title:
                existing.title = new_title
            if tags is not None:
                existing.tags = tags
            entry = existing

        elif amd.action == "remove":
            entry = self._entries.pop(amd.entry_id, None)

        amd.status = "approved"
        amd.reviewed_by = reviewed_by
        amd.reviewed_at = _now_iso()

        self._version = _bump_patch(self._version)
        self._save_all()
        self._snapshot()
        return entry

    def reject_amendment(self, amendment_id: str, reviewed_by: str) -> Amendment:
        amd = self._find_amendment(amendment_id)
        if amd.status != "pending":
            raise ValueError(f"Amendment {amendment_id} is already {amd.status}.")
        amd.status = "rejected"
        amd.reviewed_by = reviewed_by
        amd.reviewed_at = _now_iso()
        self._save_amendments()
        return amd

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self) -> list[ConflictReport]:
        """
        Scan all active entries for potential contradictions.
        Currently detects:
          - Duplicate entry IDs (structural)
          - Entries whose bodies contain direct negations of another entry's key terms
          - Entries with identical body hashes (duplicate content)
        """
        reports: list[ConflictReport] = []
        entries = list(self._entries.values())
        seen_hashes: dict[str, str] = {}

        negation_patterns = [
            (r"\bnever\b", r"\balways\b"),
            (r"\bmust not\b", r"\bmust\b"),
            (r"\bforbidden\b", r"\brequired\b"),
            (r"\bdisallow\b", r"\ballow\b"),
        ]

        for entry in entries:
            # Duplicate hash check
            if entry.hash in seen_hashes:
                reports.append(ConflictReport(
                    entry_a=seen_hashes[entry.hash],
                    entry_b=entry.id,
                    reason="Identical body content (duplicate).",
                    severity="warning",
                ))
            else:
                seen_hashes[entry.hash] = entry.id

        # Cross-entry negation scan
        for i, a in enumerate(entries):
            for b in entries[i + 1:]:
                shared_tags = set(a.tags) & set(b.tags)
                if not shared_tags:
                    continue
                for neg, pos in negation_patterns:
                    a_has_neg = bool(re.search(neg, a.body, re.I))
                    b_has_pos = bool(re.search(pos, b.body, re.I))
                    a_has_pos = bool(re.search(pos, a.body, re.I))
                    b_has_neg = bool(re.search(neg, b.body, re.I))
                    if (a_has_neg and b_has_pos) or (a_has_pos and b_has_neg):
                        reports.append(ConflictReport(
                            entry_a=a.id,
                            entry_b=b.id,
                            reason=(
                                f"Potential negation conflict on shared tags "
                                f"{shared_tags} (pattern: {neg!r} vs {pos!r})."
                            ),
                            severity="warning",
                        ))
                        break
        return reports

    # ------------------------------------------------------------------
    # Regulatory export
    # ------------------------------------------------------------------

    def regulatory_export(self, output_path: str | Path | None = None) -> dict[str, Any]:
        """
        Produce a machine-readable summary of the active Canon for
        external regulatory review.  Writes to output_path if given.
        """
        export: dict[str, Any] = {
            "gaia_canon_export": True,
            "version": self._version,
            "exported_at": _now_iso(),
            "total_entries": len(self._entries),
            "entries": [e.to_dict() for e in self._entries.values()],
            "amendment_log": [
                a.to_dict() for a in self._amendments if a.status == "approved"
            ],
            "conflicts_at_export": [c.to_dict() for c in self.detect_conflicts()],
        }
        if output_path:
            Path(output_path).write_text(json.dumps(export, indent=2))
        return export

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def list_snapshots(self) -> list[str]:
        """Return all available snapshot version strings."""
        if not self._snapshots_dir.exists():
            return []
        return sorted(
            p.stem for p in self._snapshots_dir.glob("*.json")
        )

    def load_snapshot(self, version: str) -> dict[str, Any]:
        """Load a frozen snapshot by version string."""
        snap_file = self._snapshots_dir / f"{version}.json"
        if not snap_file.exists():
            raise FileNotFoundError(f"No snapshot for version {version!r}.")
        return json.loads(snap_file.read_text())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_amendment(self, amendment_id: str) -> Amendment:
        for a in self._amendments:
            if a.amendment_id == amendment_id:
                return a
        raise KeyError(f"Amendment {amendment_id!r} not found.")

    def _snapshot(self) -> None:
        self._snapshots_dir.mkdir(parents=True, exist_ok=True)
        snap: dict[str, Any] = {
            "version": self._version,
            "snapshotted_at": _now_iso(),
            "entries": {k: v.to_dict() for k, v in self._entries.items()},
        }
        snap_file = self._snapshots_dir / f"{self._version}.json"
        snap_file.write_text(json.dumps(snap, indent=2))

    def _load(self) -> None:
        self.store_path.mkdir(parents=True, exist_ok=True)
        if self._version_file.exists():
            self._version = self._version_file.read_text().strip()
        if self._entries_file.exists():
            raw = json.loads(self._entries_file.read_text())
            self._entries = {k: CanonEntry(**v) for k, v in raw.items()}
        if self._amendments_file.exists():
            raw_amds = json.loads(self._amendments_file.read_text())
            self._amendments = [Amendment(**a) for a in raw_amds]

    def _save_all(self) -> None:
        self._entries_file.write_text(
            json.dumps({k: v.to_dict() for k, v in self._entries.items()}, indent=2)
        )
        self._version_file.write_text(self._version)
        self._save_amendments()

    def _save_amendments(self) -> None:
        self._amendments_file.write_text(
            json.dumps([a.to_dict() for a in self._amendments], indent=2)
        )

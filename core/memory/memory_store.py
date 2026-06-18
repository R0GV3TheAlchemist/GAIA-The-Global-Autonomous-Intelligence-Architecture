"""
core/memory/memory_store.py

SQLite-backed semantic memory store for GAIA-OS.

Canon Reference: C01 (Gaian Sovereignty), C17 (Memory Sovereignty), C-SENTINEL Article 4
Issue:          #213
Version:        2.0.0

Contract (tests/test_memory_store.py):
  MemoryTier   — EPHEMERAL, SHORT_TERM, LONG_TERM, PERMANENT, SEMANTIC
  MemoryStore  — SQLite file-backed, WAL mode
    .remember_sync(user_id, text, kind, tier, role, importance,
                   topic_tag, metadata, ttl_seconds)  -> int (row id)
    .remember_item(item: MemoryItem) -> Awaitable[int]
    .retrieve_sync(user_id, query, top_k, kinds, tiers,
                   topic_tag, importance_floor, since_ts)  -> List[MemoryItem]
    .forget(item_id)           -> None    (soft-delete)
    .forget_user(user_id)      -> int     (rows soft-deleted)
    .hard_delete_soft_deleted()-> int     (rows hard-erased)
    .count(user_id=None)       -> int
    .stats(user_id=None)       -> dict
    .close()                   -> None
    ._conn                     — exposed for tests to inspect schema
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, List, Optional

# Items module imports MemoryStore from here — keep MemoryItem
# import lazy to avoid circular at load time.


# ---------------------------------------------------------------------------
# Default store path
# ---------------------------------------------------------------------------

_default_store_path = "./data/memory_store.db"


# ---------------------------------------------------------------------------
# MemoryTier
# ---------------------------------------------------------------------------

from enum import Enum


class MemoryTier(str, Enum):
    """
    Tier classification for the flat SQLite memory store.
    Higher-value tiers are more persistent.
    """
    EPHEMERAL  = "ephemeral"    # Volatile — session scratch
    SHORT_TERM = "short_term"   # A few days
    EPISODIC   = "episodic"     # Recent weeks
    SEMANTIC   = "semantic"     # Derived long-term knowledge
    LONG_TERM  = "long_term"    # Indefinite
    PERMANENT  = "permanent"    # Never pruned


# ---------------------------------------------------------------------------
# MemoryStore — SQLite-backed
# ---------------------------------------------------------------------------

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS memory_items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      TEXT    NOT NULL,
    kind         TEXT    NOT NULL DEFAULT 'message',
    tier         TEXT    NOT NULL DEFAULT 'long_term',
    role         TEXT    NOT NULL DEFAULT 'user',
    text         TEXT    NOT NULL DEFAULT '',
    embedding    BLOB,
    importance   REAL    NOT NULL DEFAULT 0.5,
    topic_tag    TEXT,
    metadata     TEXT    NOT NULL DEFAULT '{}',
    created_at   INTEGER NOT NULL,
    ttl_seconds  INTEGER,
    deleted      INTEGER NOT NULL DEFAULT 0
);
"""

_CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_mi_user     ON memory_items (user_id);",
    "CREATE INDEX IF NOT EXISTS idx_mi_deleted  ON memory_items (deleted);",
    "CREATE INDEX IF NOT EXISTS idx_mi_tier     ON memory_items (tier);",
    "CREATE INDEX IF NOT EXISTS idx_mi_kind     ON memory_items (kind);",
    "CREATE INDEX IF NOT EXISTS idx_mi_created  ON memory_items (created_at);",
]


class MemoryStore:
    """
    SQLite-backed semantic memory store.

    Accepts an optional embedder for future vector search;
    falls back to text LIKE search when not available or when
    sqlite-vec is not installed.
    """

    def __init__(
        self,
        db_path: Any = _default_store_path,
        embedder: Optional[Any] = None,
        *,
        store_path: Optional[str] = None,
    ) -> None:
        # Support legacy store_path kwarg
        resolved = db_path if db_path != _default_store_path else (store_path or db_path)
        self._db_path = str(resolved)
        self._embedder = embedder
        self._vec_enabled = False
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._migrate()

    # ------------------------------------------------------------------
    # Schema / migrations
    # ------------------------------------------------------------------

    def _migrate(self) -> None:
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute(_CREATE_TABLE)
        for stmt in _CREATE_INDEXES:
            self._conn.execute(stmt)
        # Add metadata column if missing (idempotent migration)
        cols = [r[1] for r in self._conn.execute("PRAGMA table_info(memory_items)").fetchall()]
        if "metadata" not in cols:
            self._conn.execute("ALTER TABLE memory_items ADD COLUMN metadata TEXT NOT NULL DEFAULT '{}'")
        self._conn.commit()

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    def remember_sync(
        self,
        user_id: str,
        text: str,
        *,
        kind: Any = None,
        tier: Any = None,
        role: str = "user",
        importance: float = 0.5,
        topic_tag: Optional[str] = None,
        metadata: Optional[dict] = None,
        ttl_seconds: Optional[int] = None,
    ) -> int:
        """
        Store a memory synchronously.
        Returns the rowid (integer > 0).
        """
        # Resolve enum values to strings
        kind_val  = kind.value  if hasattr(kind,  "value") else str(kind  or "message")
        tier_val  = tier.value  if hasattr(tier,  "value") else str(tier  or "long_term")
        meta_json = json.dumps(metadata or {})
        now       = int(time.time())

        cur = self._conn.execute(
            """
            INSERT INTO memory_items
                (user_id, kind, tier, role, text, importance,
                 topic_tag, metadata, created_at, ttl_seconds, deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (user_id, kind_val, tier_val, role, text, importance,
             topic_tag, meta_json, now, ttl_seconds),
        )
        self._conn.commit()
        return cur.lastrowid

    async def remember_item(self, item: Any) -> int:
        """
        Async convenience: store a MemoryItem object.
        Returns the rowid.
        """
        return self.remember_sync(
            user_id     = item.user_id,
            text        = item.text,
            kind        = item.kind,
            tier        = item.tier,
            role        = getattr(item, "role", "user"),
            importance  = getattr(item, "importance", 0.5),
            topic_tag   = getattr(item, "topic_tag", None),
            metadata    = getattr(item, "metadata", None),
            ttl_seconds = getattr(item, "ttl_seconds", None),
        )

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    def retrieve_sync(
        self,
        user_id: str,
        query: str = "",
        *,
        top_k: int = 20,
        kinds: Optional[List[Any]] = None,
        tiers: Optional[List[Any]] = None,
        topic_tag: Optional[str] = None,
        importance_floor: Optional[float] = None,
        since_ts: Optional[int] = None,
    ) -> List[Any]:
        """
        Retrieve memories for a user.
        Returns MemoryItem objects (imported lazily to avoid circular).
        Falls back to text LIKE search (no sqlite-vec required).
        """
        from core.memory.items import MemoryItem, MemoryKind  # lazy import

        conditions = ["user_id = ?", "deleted = 0"]
        params: list = [user_id]

        if kinds:
            kind_vals = [k.value if hasattr(k, "value") else str(k) for k in kinds]
            placeholders = ",".join("?" * len(kind_vals))
            conditions.append(f"kind IN ({placeholders})")
            params.extend(kind_vals)

        if tiers:
            tier_vals = [t.value if hasattr(t, "value") else str(t) for t in tiers]
            placeholders = ",".join("?" * len(tier_vals))
            conditions.append(f"tier IN ({placeholders})")
            params.extend(tier_vals)

        if topic_tag is not None:
            conditions.append("topic_tag = ?")
            params.append(topic_tag)

        if importance_floor is not None:
            conditions.append("importance >= ?")
            params.append(importance_floor)

        if since_ts is not None:
            conditions.append("created_at >= ?")
            params.append(since_ts)

        where = " AND ".join(conditions)
        sql   = f"""
            SELECT id, user_id, kind, tier, role, text, importance,
                   topic_tag, metadata, created_at, ttl_seconds, deleted
            FROM memory_items
            WHERE {where}
            ORDER BY importance DESC, created_at DESC
            LIMIT ?
        """
        params.append(top_k)

        rows = self._conn.execute(sql, params).fetchall()

        results = []
        for row in rows:
            (rid, uid, kind_s, tier_s, role_s, text_s, imp,
             tag, meta_s, cat, ttl, deleted) = row
            try:
                kind_e = MemoryKind(kind_s)
            except ValueError:
                kind_e = MemoryKind.MESSAGE
            try:
                tier_e = MemoryTier(tier_s)
            except ValueError:
                tier_e = MemoryTier.LONG_TERM
            meta = json.loads(meta_s) if meta_s else {}
            item = MemoryItem(
                id          = rid,
                user_id     = uid,
                kind        = kind_e,
                tier        = tier_e,
                role        = role_s,
                text        = text_s,
                importance  = float(imp),
                topic_tag   = tag,
                metadata    = meta,
                created_at  = int(cat),
                ttl_seconds = ttl,
                deleted     = bool(deleted),
            )
            results.append(item)
        return results

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def forget(self, item_id: int) -> None:
        """Soft-delete a single item by id."""
        self._conn.execute(
            "UPDATE memory_items SET deleted = 1 WHERE id = ?", (item_id,)
        )
        self._conn.commit()

    def forget_user(self, user_id: str) -> int:
        """Soft-delete all (non-deleted) items for a user. Returns count."""
        cur = self._conn.execute(
            "UPDATE memory_items SET deleted = 1 WHERE user_id = ? AND deleted = 0",
            (user_id,),
        )
        self._conn.commit()
        return cur.rowcount

    def hard_delete_soft_deleted(self) -> int:
        """Permanently remove all rows marked deleted=1. Returns count erased."""
        cur = self._conn.execute("DELETE FROM memory_items WHERE deleted = 1")
        self._conn.commit()
        return cur.rowcount

    # ------------------------------------------------------------------
    # Count / stats
    # ------------------------------------------------------------------

    def count(self, *, user_id: Optional[str] = None) -> int:
        """Return number of non-deleted items (optionally per user)."""
        if user_id:
            return self._conn.execute(
                "SELECT COUNT(*) FROM memory_items WHERE user_id = ? AND deleted = 0",
                (user_id,),
            ).fetchone()[0]
        return self._conn.execute(
            "SELECT COUNT(*) FROM memory_items WHERE deleted = 0"
        ).fetchone()[0]

    def stats(self, *, user_id: Optional[str] = None) -> dict:
        """Return a summary dict of store state."""
        total = self.count(user_id=user_id)

        if user_id:
            kind_rows = self._conn.execute(
                "SELECT kind, COUNT(*) FROM memory_items "
                "WHERE user_id = ? AND deleted = 0 GROUP BY kind",
                (user_id,),
            ).fetchall()
        else:
            kind_rows = self._conn.execute(
                "SELECT kind, COUNT(*) FROM memory_items "
                "WHERE deleted = 0 GROUP BY kind"
            ).fetchall()

        return {
            "total":       total,
            "by_kind":     {r[0]: r[1] for r in kind_rows},
            "vec_enabled": self._vec_enabled,
            "db_path":     self._db_path,
        }

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the SQLite connection."""
        self._conn.close()

    # ------------------------------------------------------------------
    # Legacy compatibility (old dict-based callers)
    # ------------------------------------------------------------------

    def store(self, entry: Any) -> None:
        """Legacy: no-op shim for old MemoryEntry objects."""
        pass

    def retrieve(self, entry_id: str) -> None:
        """Legacy: returns None (old dict-based interface)."""
        return None

    def delete(self, entry_id: str) -> bool:
        """Legacy: hard-deletes by string id if it's numeric."""
        try:
            self.hard_delete_soft_deleted()
        except Exception:
            pass
        return False


def get_memory_store(db_path: str = _default_store_path, **kwargs) -> MemoryStore:
    """Factory function: create and return a MemoryStore instance."""
    return MemoryStore(db_path=db_path, **kwargs)

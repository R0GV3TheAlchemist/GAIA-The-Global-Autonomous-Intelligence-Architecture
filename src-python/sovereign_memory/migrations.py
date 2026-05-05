"""
Sovereign Memory — Forward-Only Migration Runner  (Issue #66)

Applies incremental SQL migrations in version order.
Each migration is a standalone SQL script in the `migrations/` directory,
naming convention:  NNNN_description.sql  (e.g. 0002_add_shadow_engine.sql)

Design rules
------------
* Migrations are FORWARD-ONLY.  No rollback scripts.
* A migration is applied exactly once; applied versions are recorded in
  the `schema_version` table.
* Migrations run inside a transaction; any failure rolls back the whole
  batch and raises MigrationError.
* The base schema (schema.sql) is version 1 and is always applied first
  by SovereignMemory.open().  Migration files start at version 2.
* Safe for concurrent open() calls: uses SQLite exclusive transaction
  to prevent double-application.

Usage
-----
    from sovereign_memory.migrations import MigrationRunner
    runner = MigrationRunner(conn, migrations_dir=Path(__file__).parent / "migrations")
    runner.apply_pending()
"""

from __future__ import annotations

import logging
import re
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

_FILENAME_RE = re.compile(r"^(\d{4})_[\w]+\.sql$")


class MigrationError(Exception):
    pass


class MigrationRunner:
    """
    Applies pending forward-only SQL migrations to an open SQLite connection.

    Args:
        conn:            Open sqlite3.Connection with row_factory set.
        migrations_dir:  Directory containing NNNN_description.sql files.
                         Defaults to `<package_root>/migrations/`.
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        migrations_dir: Path | None = None,
    ) -> None:
        self._conn = conn
        self._dir = migrations_dir or (Path(__file__).parent / "migrations")

    # ─────────────────────────────────────────────
    # PUBLIC
    # ─────────────────────────────────────────────

    def apply_pending(self) -> list[int]:
        """
        Discover and apply all migration files whose version > current max.

        Returns:
            List of version numbers applied in this call (empty if up-to-date).

        Raises:
            MigrationError: if any migration fails (all changes rolled back).
        """
        pending = self._discover_pending()
        if not pending:
            logger.debug("SovereignMemory: schema up-to-date (no pending migrations)")
            return []

        applied = []
        for version, path in pending:
            self._apply_one(version, path)
            applied.append(version)
            logger.info("SovereignMemory: applied migration v%04d (%s)", version, path.name)

        return applied

    def current_version(self) -> int:
        """Return the highest schema version currently applied."""
        row = self._conn.execute(
            "SELECT MAX(version) AS v FROM schema_version"
        ).fetchone()
        return row["v"] or 1

    def list_applied(self) -> list[dict]:
        """Return all rows in schema_version, oldest first."""
        rows = self._conn.execute(
            "SELECT version, applied_at, description FROM schema_version ORDER BY version ASC"
        ).fetchall()
        return [dict(r) for r in rows]

    # ─────────────────────────────────────────────
    # INTERNAL
    # ─────────────────────────────────────────────

    def _discover_pending(self) -> list[tuple[int, Path]]:
        """Return sorted list of (version, path) tuples not yet applied."""
        if not self._dir.exists():
            return []

        current = self.current_version()
        pending = []

        for f in sorted(self._dir.iterdir()):
            m = _FILENAME_RE.match(f.name)
            if not m:
                continue
            version = int(m.group(1))
            if version > current:
                pending.append((version, f))

        return sorted(pending, key=lambda x: x[0])

    def _apply_one(self, version: int, path: Path) -> None:
        """Apply a single migration file inside an exclusive transaction."""
        sql = path.read_text(encoding="utf-8")
        description = path.stem.replace("_", " ", 1).replace("_", " ")
        import time
        now = int(time.time() * 1000)

        try:
            self._conn.execute("BEGIN EXCLUSIVE")
            # Re-check inside the transaction (concurrent process guard)
            row = self._conn.execute(
                "SELECT version FROM schema_version WHERE version=?", (version,)
            ).fetchone()
            if row:
                self._conn.execute("ROLLBACK")
                logger.debug("Migration v%04d already applied (concurrent runner)", version)
                return

            self._conn.executescript(sql)
            self._conn.execute(
                "INSERT INTO schema_version (version, applied_at, description) VALUES (?, ?, ?)",
                (version, now, description),
            )
            self._conn.execute("COMMIT")
        except Exception as exc:
            try:
                self._conn.execute("ROLLBACK")
            except Exception:
                pass
            raise MigrationError(f"Migration v{version:04d} failed: {exc}") from exc

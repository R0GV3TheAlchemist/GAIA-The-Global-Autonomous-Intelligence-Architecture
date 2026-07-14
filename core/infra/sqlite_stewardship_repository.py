"""
core/infra/sqlite_stewardship_repository.py
C17 / C23 / C27 — SQLite-backed StewardshipRepository

Drop-in persistent replacement for InMemoryStewardshipRepository.
Uses Python's stdlib ``sqlite3`` — no additional dependencies required.

Schema (auto-created on first instantiation)
--------------------------------------------

  stewardship_bonds
    bond_id       TEXT PRIMARY KEY
    gaian_id      TEXT NOT NULL
    steward_id    TEXT NOT NULL
    role          TEXT NOT NULL
    is_active     INTEGER NOT NULL  (0 / 1)
    created_at    TEXT NOT NULL
    released_at   TEXT              (NULL while active)
    release_reason TEXT
    metadata      TEXT NOT NULL     (JSON)

Upsert strategy
---------------
``save_bond()`` uses INSERT OR REPLACE so that calling it after
``bond.release()`` updates the existing row to is_active=0 without
creating a duplicate. The PRIMARY KEY on bond_id guarantees uniqueness.
"""

from __future__ import annotations

import json
import sqlite3
from typing import List, Optional

from core.lifecycle.stewardship import StewardRole, StewardshipBond
from core.lifecycle.repositories import StewardshipRepository

_DDL = """
CREATE TABLE IF NOT EXISTS stewardship_bonds (
    bond_id        TEXT PRIMARY KEY,
    gaian_id       TEXT    NOT NULL,
    steward_id     TEXT    NOT NULL,
    role           TEXT    NOT NULL,
    is_active      INTEGER NOT NULL DEFAULT 1,
    created_at     TEXT    NOT NULL,
    released_at    TEXT,
    release_reason TEXT,
    metadata       TEXT    NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_bonds_gaian
    ON stewardship_bonds (gaian_id, is_active);
"""


class SqliteStewardshipRepository(StewardshipRepository):
    """
    SQLite-backed stewardship bond repository.

    Parameters
    ----------
    db_path :
        Path to the SQLite database file, or ``':memory:'`` for an
        ephemeral in-process database.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self._db_path = db_path
        self._bootstrap()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _bootstrap(self) -> None:
        with self._connect() as conn:
            conn.executescript(_DDL)

    @staticmethod
    def _bond_to_row(bond: StewardshipBond) -> dict:
        return {
            "bond_id":        bond.bond_id,
            "gaian_id":       bond.gaian_id,
            "steward_id":     bond.steward_id,
            "role":           bond.role.value,
            "is_active":      1 if bond.is_active else 0,
            "created_at":     bond.created_at,
            "released_at":    bond.released_at,
            "release_reason": bond.release_reason,
            "metadata":       json.dumps(bond.metadata),
        }

    @staticmethod
    def _row_to_bond(row: sqlite3.Row) -> StewardshipBond:
        bond = StewardshipBond(
            bond_id=row["bond_id"],
            gaian_id=row["gaian_id"],
            steward_id=row["steward_id"],
            role=StewardRole(row["role"]),
            metadata=json.loads(row["metadata"]),
        )
        bond.created_at = row["created_at"]
        if not row["is_active"]:
            bond.is_active      = False
            bond.released_at    = row["released_at"]
            bond.release_reason = row["release_reason"]
        return bond

    # ------------------------------------------------------------------
    # StewardshipRepository interface
    # ------------------------------------------------------------------

    def save_bond(self, bond: StewardshipBond) -> None:
        row = self._bond_to_row(bond)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO stewardship_bonds
                    (bond_id, gaian_id, steward_id, role, is_active,
                     created_at, released_at, release_reason, metadata)
                VALUES
                    (:bond_id, :gaian_id, :steward_id, :role, :is_active,
                     :created_at, :released_at, :release_reason, :metadata)
                """,
                row,
            )

    def load_active_bond(
        self,
        gaian_id: str,
        role:     Optional[StewardRole] = None,
    ) -> Optional[StewardshipBond]:
        if role is not None:
            sql = """
                SELECT * FROM stewardship_bonds
                WHERE  gaian_id = ? AND is_active = 1 AND role = ?
                ORDER  BY rowid DESC LIMIT 1
            """
            params = (gaian_id, role.value)
        else:
            sql = """
                SELECT * FROM stewardship_bonds
                WHERE  gaian_id = ? AND is_active = 1
                ORDER  BY rowid DESC LIMIT 1
            """
            params = (gaian_id,)

        with self._connect() as conn:
            row = conn.execute(sql, params).fetchone()
        return self._row_to_bond(row) if row else None

    def load_bond_history(self, gaian_id: str) -> List[StewardshipBond]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM stewardship_bonds
                WHERE  gaian_id = ?
                ORDER  BY rowid ASC
                """,
                (gaian_id,),
            ).fetchall()
        return [self._row_to_bond(r) for r in rows]

"""
GAIA OS Persistence Layer.

This package gives every in-memory OS structure a disk-backed
counterpart. Nothing in core/ is modified — persistence is
additive: a thin write-through / read-on-boot wrapper around
existing structures.

Modules:
  store.py       — PersistenceStore: atomic JSON file I/O
  memory.py      — MemoryPersistence: saves/loads MemoryStore fragments
  identity.py    — IdentityPersistence: saves/loads GAIAN identity + genesis
  registry.py    — RegistryPersistence: saves/loads GAIANRegistry
  session.py     — SessionPersistence: saves/loads boot manifests
  manager.py     — PersistenceManager: orchestrates all sub-stores,
                   called by PrimordialSession at boot and shutdown

Design:
  1. ATOMIC WRITES: Every write goes to a .tmp file first,
     then os.replace() renames it atomically. A crash mid-write
     never corrupts the existing state.
  2. WRITE-THROUGH: Fragments are written to disk immediately
     on creation (not just at shutdown).
  3. BOOT RESTORE: PersistenceManager.restore() is called
     during PrimordialSession Phase 3 (registry_restore) to
     reload all GAIANs, their identities, and their memories
     from disk before any session begins.
  4. ZERO DEPENDENCIES: Only Python stdlib (json, pathlib,
     os, uuid, datetime). No SQLite, no Redis, no ORM.
  5. HUMAN-READABLE: All persisted data is UTF-8 JSON.
     A developer can inspect, back up, or migrate state
     with any text editor or `jq`.
"""

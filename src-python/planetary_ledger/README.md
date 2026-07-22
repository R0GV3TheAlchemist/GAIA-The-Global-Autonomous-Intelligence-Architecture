# Planetary Ledger

**NEXUS Phase E — Real Merkle-DAG Event Chaining**

> *Copyright (c) 2026 Kyle Alexander Steen (R0GV3 The Alchemist). All Rights Reserved.*

---

## What it is

The Planetary Ledger is NEXUS's append-only, tamper-evident event record.
Every system event — capability grants, session lifecycle, Schumann syncs,
crisis triggers, governance audits — is written here with:

- **Merkle-DAG causal chaining** — each event links to its parent via `parent_event_id`; the full ancestor chain is traversable
- **SHA-256 content hashing** — every node in the DAG is hashed over canonical sorted-key JSON
- **Ed25519 or HMAC-SHA256 signing** — every event is cryptographically signed before persistence
- **SQLite persistence** — WAL-mode, atomic writes, indexed by `event_type` and `session_id`
- **Schema-faithful** — every event validates against `specs/planetary-ledger-event.schema.json`

---

## Module layout

```
planetary_ledger/
  __init__.py          # Public exports
  event.py             # LedgerEvent dataclass + EventType enum
  dag.py               # MerkleDAG — in-memory hash-linked node graph
  signer.py            # Ed25519Signer + HMACSigner (stdlib fallback)
  ledger.py            # PlanetaryLedger — main entry point
  README.md            # This file
```

---

## Quick start

```python
from planetary_ledger import PlanetaryLedger, EventType

ledger = PlanetaryLedger()  # SQLite at nexus_data/planetary_ledger.db

event = ledger.append(
    event_type=EventType.SESSION_INIT,
    payload={"session": "my-session-id", "node": "nexus-alpha"},
    tags=["bootstrap"],
)

print(event.event_id)          # UUID4
print(event.parent_event_id)   # None on first event; previous event_id thereafter
print(ledger.size)             # 1
print(ledger.verify_event(event.event_id))  # True
```

---

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `NEXUS_LEDGER_PATH` | `nexus_data/planetary_ledger.db` | SQLite database path |
| `NEXUS_NODE_ID` | `00000000-0000-0000-0000-000000000001` | Node UUID stamped on every event |
| `NEXUS_LEDGER_SECRET` | `nexus-default-secret` | HMAC secret (override in production) |

---

## Event types (from schema)

`capability_granted` · `capability_revoked` · `policy_violation` · `module_restart` ·
`twin_sync` · `memory_commit` · `session_init` · `session_close` · `schumann_sync` ·
`crisis_triggered` · `governance_audit` · `custom`

---

*Phase E — Planetary Ledger declared operational. 2026-07-22.*

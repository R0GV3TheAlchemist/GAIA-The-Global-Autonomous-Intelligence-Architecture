# GAIA-OS Storage Layer

**Issue #281 — Distributed State Store**

The `core/storage/` module provides a pluggable persistence abstraction for
all GAIA-OS data. All SQLite usages route through a common `StorageBackend`
protocol, making it trivially swappable for planetary-scale databases.

---

## Quick Start

```python
from core.storage import get_backend

backend = get_backend()  # defaults to SQLite at ~/.gaia/storage.db

# All operations are async
await backend.put("mesh:node-001", b"{\"phi\": 0.72}")
value = await backend.get("mesh:node-001")   # b'{"phi": 0.72}'
rows  = await backend.query(prefix="mesh:")  # [(key, bytes), ...]
await backend.delete("mesh:node-001")
```

---

## Swapping Backends

### Option 1: Environment variable (recommended)

```bash
export GAIA_STORAGE_BACKEND=sqlite   # default
export GAIA_STORAGE_BACKEND=memory   # tests / ephemeral
export GAIA_STORAGE_BACKEND=cockroachdb  # Phase 2
```

### Option 2: Programmatic override

```python
from core.storage import configure_backend, MemoryBackend
configure_backend(MemoryBackend())   # useful in pytest fixtures
```

### Option 3: Sovereign memory (encrypted at rest)

```python
from core.storage import SQLiteBackend, SovereignStorageBackend, configure_backend
import os

encryption_key = derive_key_from_passphrase(gaian_passphrase)  # 32 bytes
base = SQLiteBackend(db_path=f"~/.gaia/{gaian_id}/memories.db")
sovereign = SovereignStorageBackend(base, encryption_key=encryption_key)
configure_backend(sovereign)
```

All reads and writes will be transparently encrypted/decrypted with
AES-256-GCM using the Gaian’s own key. No other node or process can
read the data without the key. *(Canon C04 — Sovereign Privacy)*

---

## Key Namespace Conventions

| Prefix | Usage |
|---|---|
| `mesh:<key>` | CollectiveField CRDT entries |
| `affect:<node_id>` | Per-node affect vectors |
| `coherence:<node_id>` | Per-node coherence scores |
| `audit:<user_id>:<ts>` | Audit ledger events |
| `memory:<user_id>:<id>` | Sovereign Gaian memories |
| `telemetry:<ts>:<event>` | Telemetry events |
| `crisis:<id>` | Crisis engine records |
| `planetary:<sensor>` | Planetary sensor readings |

---

## Migrating Existing SQLite Usages

The four current direct SQLite usages identified in issue #281:

| File | What to change |
|---|---|
| `sidecar/telemetry/telemetry_collector.py` | Replace `sqlite3` calls with `await backend.put(f"telemetry:{ts}:{event}", data)` |
| `src-python/crisis_engine/engine.py` | Replace direct DB calls with `await backend.put(f"crisis:{id}", data)` |
| `src-python/sovereign_memory/` | Use `SovereignStorageBackend` with Gaian’s encryption key |
| `core/obs/audit_store.py` | Replace `sqlite3` calls with `await backend.put(f"audit:{uid}:{ts}", data)` |

Each migration is a small, isolated PR. The `StorageBackend` interface
accepts the same data shapes as before — callers just switch from sync
SQLite to `await backend.put/get/query()`.

---

## Phase Roadmap

### Phase 1 ✔ (This PR)
- `StorageBackend` Protocol defined
- `SQLiteBackend` — default, preserves existing behaviour
- `MemoryBackend` — tests and ephemeral nodes
- `SovereignStorageBackend` — AES-256-GCM encryption wrapper
- Factory with env-var switching

### Phase 2 (Worldwide scale)
- `CockroachDBBackend` — globally distributed SQL, survives node failures
  - `pip install asyncpg`
  - `GAIA_STORAGE_BACKEND=cockroachdb`
  - `GAIA_STORAGE_DSN=postgresql://user:pw@host:26257/gaia`
- `ScyllaBackend` — high-throughput time-series (telemetry at planetary scale)
  - `pip install cassandra-driver`
  - `GAIA_STORAGE_BACKEND=scylladb`

### Phase 3 (Interplanetary)
- `StoreForwardBackend` — wraps any Phase 2 backend
  - Writes queue locally when the interplanetary link is down
  - Flushes automatically when the link recovers
  - Conflict resolution via vector clocks (compatible with the
    `CollectiveField` HLC used in `core/mesh/collective_field.py`)
- `IPFSBackend` — content-addressed sovereign memory
  - Data addressed by CID — identical content is never stored twice
  - Sovereign memories travel with the Gaian across nodes
  - `pip install ipfshttpclient`
  - `GAIA_STORAGE_BACKEND=ipfs`

---

## Testing

```python
import pytest
from core.storage import MemoryBackend

@pytest.fixture
async def storage():
    backend = MemoryBackend()
    yield backend
    await backend.close()

async def test_put_get(storage):
    await storage.put("key", b"value")
    assert await storage.get("key") == b"value"

async def test_ttl(storage):
    await storage.put("temp", b"x", ttl=1)
    import asyncio; await asyncio.sleep(1.1)
    assert await storage.get("temp") is None

async def test_query_prefix(storage):
    await storage.put("mesh:a", b"1")
    await storage.put("mesh:b", b"2")
    await storage.put("other:c", b"3")
    rows = await storage.query("mesh:")
    assert len(rows) == 2
    assert rows[0][0] == "mesh:a"
```

---

*GAIA Constitutional Canon — C04 (Sovereign Privacy), C47 (Data Portability)*
*Issue #281 — Phase 1 complete*

# Sovereign Memory System — Design Specification
**Issue:** #66  
**Branch:** `feat/stage-engine-63`  
**Status:** Implementation complete (schema, crypto, migrations, router, tests)

---

## 1. Purpose

Sovereign Memory is GAIA-OS's **local-first, encrypted, append-only knowledge base** — the foundation every other subsystem reads from and writes to. Nothing leaves the device without cryptographic consent. Erasure is achieved via crypto-erasure (key revocation), not physical row deletion.

---

## 2. Key Hierarchy

```
Master Key (MK)  ← 32 random bytes, OS keychain ONLY
    └── DEK-N    ← HKDF-SHA256(MK, info=key_id)
                      Used for AES-256-GCM per domain
```

| Key | key_id | Domain |
|---|---|---|
| Episodic DEK | `episodic-v1` | Journal, decisions, conversations |
| Semantic DEK | `semantic-v1` | Patterns, values, beliefs |
| Legacy DEK | `legacy-v1` | Letters to future self, wisdom distillations |

### Platform KEK storage

| Platform | Backend |
|---|---|
| macOS | macOS Keychain (via `keyring`) |
| Windows | DPAPI / Credential Manager (via `keyring`) |
| Linux | Secret Service / libsecret (via `keyring`), fallback: Argon2id passphrase |

### Argon2id parameters (passphrase fallback)
- Memory: 64 MB (`memory_cost=65536`)
- Iterations: 3 (`time_cost=3`)
- Parallelism: 4
- Output: 32 bytes
- PBKDF2-SHA256 (600,000 iterations) as last-resort fallback if `argon2-cffi` not installed

---

## 3. Encryption Scheme

Every content field uses **AES-256-GCM**:
- 96-bit random nonce per encryption call
- AAD = `{"table": "...", "id": "...", "v": 1}` — binds ciphertext to its DB row; any row-swap tampering raises `InvalidTag`
- Ciphertext, nonce, and AAD bytes are all stored in the DB

---

## 4. Schema

Defined in `schema.sql` (version 1 baseline) and extended by incremental migration files.

### Core tables

| Table | Purpose | Encrypted? |
|---|---|---|
| `encryption_keys` | DEK key ring (wrapped keys + status) | No (keys are stored wrapped) |
| `episodic_memory` | Journals, decisions, conversations | Yes (AES-256-GCM) |
| `semantic_memory` | Distilled patterns, values, beliefs | Yes |
| `biometric_history` | HRV, alignment score, affect scalars | No (no PII in numeric scalars) |
| `stage_records` | Current Stage Engine state (1 row per principal) | No |
| `stage_transitions` | Append-only stage arc history | No |
| `legacy_artifacts` | Letters to future self, wisdom exports | Yes |
| `schema_version` | Migration history | No |

### Migration-added tables

| Table | Migration | Purpose |
|---|---|---|
| `stage_window_state` | 0002 | WindowTracker persistence for Stage Engine |
| `shadow_records` | 0003 | Shadow Engine current archetype state |
| `shadow_transitions` | 0003 | Shadow Engine archetype change log |

---

## 5. Python API

| Method | Description |
|---|---|
| `open()` | Load MK from keychain, apply schema + migrations, open WAL connection |
| `close()` | Commit, close, wipe MK from memory |
| `store_episode(pid, content, type, tags)` | Encrypt + insert episodic memory, returns ID |
| `get_episode(pid, episode_id)` | Decrypt + return MemoryRecord (None if not found) |
| `list_episodes(pid, type, limit)` | Time-ordered listing with decrypted previews |
| `soft_delete_episode(pid, episode_id)` | Mark deleted; ciphertext retained until key rotation |
| `distill_semantic(pid, pattern, episode_ids, confidence)` | Store semantic pattern |
| `search_memory(pid, query, limit)` | Search episodic + semantic (recency; vector TODO) |
| `append_biometric_sample(pid, signal_type, value, source)` | Append one time-series row |
| `store_affect_snapshot(snapshot)` | Bulk-insert all biometric rows from AffectSnapshot |
| `get_biometric_history(pid, signal_type, days)` | Return N-day rolling history |
| `get_stage_history(pid)` | Return full stage arc transition log |
| `tag_as_legacy(pid, title, content, stage)` | Store a legacy artifact (Stage 4/5 only) |
| `export_legacy(pid, format)` | Decrypt + export all legacy artifacts (markdown or JSON) |
| `crypto_erase_key(key_id)` | GDPR Art. 17: revoke DEK — IRREVERSIBLE |

---

## 6. Migrations

`MigrationRunner` applies incremental SQL scripts from `sovereign_memory/migrations/`:

| Version | File | Description |
|---|---|---|
| 1 | `schema.sql` | Base schema (applied by `_apply_schema()` on `open()`) |
| 2 | `0002_add_stage_window_state.sql` | WindowTracker table for Stage Engine |
| 3 | `0003_add_shadow_engine_tables.sql` | Shadow Engine tables (`shadow_records`, `shadow_transitions`) |

**Rules:**
- Forward-only, no rollbacks
- Applied exactly once (concurrent-safe via `BEGIN EXCLUSIVE`)
- Idempotent: re-calling `apply_pending()` is a no-op when up to date

---

## 7. HTTP API

| Method | Path | Description |
|---|---|---|
| GET | /memory/health | Liveness probe |
| POST | /memory/episode | Store encrypted episode |
| GET | /memory/episode/{pid}/{id} | Retrieve + decrypt episode |
| GET | /memory/episodes/{pid} | List episodes (paginated) |
| POST | /memory/semantic | Distil semantic pattern |
| GET | /memory/search/{pid}?q= | Search memory |
| GET | /memory/biometric/{pid}?signal_type=&days= | Biometric history |
| DELETE | /memory/episode/{pid}/{id} | Soft-delete episode |
| GET | /memory/schema-version | Current version + migration history |
| POST | /memory/crypto-erase/{key_id} | GDPR Art. 17 crypto-erasure (IRREVERSIBLE) |

---

## 8. Privacy Guarantees

- **Zero network transmission**: all data is local SQLite + OS keychain
- **Crypto-erasure**: revoking a DEK makes all rows under that key_id permanently unrecoverable; no physical deletion needed for GDPR Art. 17 compliance
- **AAD binding**: every ciphertext is cryptographically bound to its DB row; row-swap attacks raise `InvalidTag`
- **MK in memory only**: `MasterKeyManager.wipe()` is called on `close()`, lock-screen, and OS sleep events
- **Biometric scalars unencrypted**: HRV, alignment score, etc. contain no PII — numeric scalars only

---

## 9. TODO (next iterations)

- Replace `search_memory()` recency fallback with `sqlite-vec` / Chroma vector search
- Implement DEK wrapping under KEK for iCloud Keychain cross-device sync
- Wearable API write-path (Apple HealthKit → `append_biometric_sample`)
- Full-text search index on decrypted content (in-memory FTS via `fts5` on open)

---

## 10. Acceptance Criteria

- [ ] `pytest tests/test_sovereign_memory.py` passes with zero failures
- [ ] `store_episode` → `get_episode` roundtrip decrypts original plaintext
- [ ] `soft_delete_episode` hides episode from `list_episodes` and `get_episode`
- [ ] `crypto_erase_key` marks DEK as `revoked` in `encryption_keys`
- [ ] `decrypt()` with wrong AAD raises `InvalidTag`
- [ ] `derive_dek` is deterministic for same MK + key_id
- [ ] `MigrationRunner.apply_pending()` is idempotent
- [ ] `stage_window_state` table exists after migration 0002
- [ ] `shadow_records` and `shadow_transitions` tables exist after migration 0003
- [ ] Schema version is 3 after all migrations applied

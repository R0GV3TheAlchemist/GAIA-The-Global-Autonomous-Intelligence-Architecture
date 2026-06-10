# Consent Ledger — Cryptographic Erasure Specification

**Issue:** #127  
**Status:** Implemented — 2026-06-09  
**Implementation:** `core/consent_ledger.py`

---

## Overview

The consent ledger records every significant consent decision a user makes with GAIA. Without cryptographic trustworthiness, a consent ledger is just a database that can be quietly modified. This specification makes it unforgeable.

Four guarantees:

1. **Immutable audit trail** — Every consent decision is HMAC-signed at creation time. Any alteration is detectable.
2. **Chained tamper-evidence** — Each entry hashes the previous entry. Any insertion, deletion, or reordering breaks the chain.
3. **Cryptographic erasure** — Data encrypted under a consent key becomes permanently inaccessible when that key is destroyed. Erasure is not deletion — it is mathematical impossibility of recovery.
4. **Verifiable receipt** — The user receives an ErasureReceipt they can independently verify at any time.

---

## Cryptographic Erasure vs Deletion

| Property | Deletion | Cryptographic Erasure |
|---|---|---|
| Data removed from primary store | ✅ | ✅ |
| Data removed from backups | ❌ Often no | ✅ Irrelevant: ciphertext without key is worthless |
| Independently verifiable | ❌ No | ✅ Receipt + proof hash |
| Proof of completion | ❌ No | ✅ ErasureReceipt |
| Survives backup restoration | ❌ No | ✅ Key is gone; ciphertext cannot be decrypted |
| Regulatory compliance (GDPR Art.17) | Partial | ✅ Full |

This is the difference between *"we deleted your data"* (a claim you must trust) and *"here is the mathematical proof that your data can never be read again"* (a fact you can verify).

---

## Fourteen Consent Scopes

Each scope is encrypted under its own AES-256 key. Consent can be granted, restricted, or revoked independently per scope.

| Scope | What It Covers |
|---|---|
| EPISODIC_MEMORY | Session conversation history |
| SEMANTIC_MEMORY | Learned facts about the user |
| EMOTIONAL_PROFILE | Affect readings and emotional arcs |
| ARCHETYPAL_PROFILE | Soul Mirror ARCH scores |
| SOMATIC_PROFILE | Somatic signals and history |
| TRANSPERSONAL_HISTORY | Transpersonal state records |
| INDIVIDUATION_RECORD | Individuation trajectory (#121) |
| IDENTITY_ANCHORS | SubjectSideIdentity data (#120) |
| CULTURAL_PROFILE | Cultural tradition context (#124) |
| PERSONHOOD_TELEMETRY | Personhood monitor readings (#119) |
| SHADOW_HISTORY | Shadow integration records (#122) |
| CONSENT_LEDGER_ITSELF | The ledger itself |
| THIRD_PARTY_SHARING | Any sharing with third parties |
| RESEARCH_USE | Anonymised research use |

---

## Chain-of-Trust Architecture

```
GENESIS (hash: 000...)
    │
    ▼
Entry[0]: GRANT episodic_memory
  prev_hash: 000...
  entry_hash: SHA256(prev_hash + record_payload)
  signature: HMAC-SHA256(record_payload, signing_key)
    │
    ▼
Entry[1]: GRANT emotional_profile
  prev_hash: entry_hash[0]
  entry_hash: SHA256(prev_hash + record_payload)
  signature: HMAC-SHA256(record_payload, signing_key)
    │
    ▼
Entry[N]: ERASURE_REQUEST episodic_memory
  prev_hash: entry_hash[N-1]
  entry_hash: SHA256(prev_hash + record_payload)
  ↳ Key episodic_memory_key_id DESTROYED
  ↳ ErasureReceipt issued
```

Any modification to any entry propagates a chain break detectable by `verify_chain()`.

---

## Erasure Workflow

1. User requests erasure for a scope.
2. `ConsentEngine.erase()` records `ERASURE_REQUEST` in ledger.
3. `CryptoErasureVault.destroy_key()` is called:
   - Key material bytes are zeroed in memory.
   - Reference is cleared.
   - `destroyed_at` timestamp recorded.
   - `destruction_proof = SHA256(key_id + destroyed_at + user_id)` computed.
4. `ErasureReceipt` is issued to the user.
5. User can call `verify_erasure_receipt(receipt)` at any time to confirm authenticity.
6. All data encrypted under the destroyed key is now permanently inaccessible.

---

## GDPR Right to Erasure Compliance

GDPR Article 17 requires that personal data be erased without undue delay upon request. The standard challenge is that deletion from primary stores does not address backup copies.

Cryptographic erasure resolves this completely: when the key is destroyed, backup copies of the ciphertext are worthless. There is nothing left to delete. The data is gone in the mathematically strongest sense available.

---

## Production Requirements

| Requirement | Specification |
|---|---|
| Key storage | HSM (Hardware Security Module) or equivalent |
| Signing key | 32 bytes, managed separately from data keys |
| AES mode | AES-256-GCM (authenticated encryption) |
| Key rotation | Annual minimum; on personnel change |
| Ledger persistence | Append-only write; no UPDATE/DELETE permissions |
| Receipt storage | User-controlled; GAIA retains audit copy only |

---

## Integration Points

| Component | Connection |
|---|---|
| SubjectSideIdentity (#120) | Identity anchors encrypted under IDENTITY_ANCHORS scope key |
| PersonhoodMonitor (#119) | Personhood telemetry encrypted under PERSONHOOD_TELEMETRY scope key |
| IndividuationEngine (#121) | Individuation record encrypted under INDIVIDUATION_RECORD scope key |
| Glass Room (#103) | All erasure events logged immutably |
| Charter | THIRD_PARTY_SHARING and RESEARCH_USE require explicit Charter-level consent |
| Sovereign memory layer | All memory writes gated by active consent grants |

---

## Design Note

GAIA's sovereignty promise is: *"Your data, your sovereignty."*

That promise requires more than good intentions. It requires a system where the user can verify — mathematically, independently, without trusting GAIA's word — that their data cannot be accessed.

Cryptographic erasure is how a promise becomes a proof.

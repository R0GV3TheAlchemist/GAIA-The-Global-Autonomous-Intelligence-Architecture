# SECURITY_SPEC.md — NEXUS Zero-Trust Security Architecture

> **Series:** SR-001–SR-014  
> **Status:** Design Complete — Implementation Pending  
> **Owner:** Kyle Steen (@R0GV3TheAlchemist)  
> **Last Updated:** 2026-07-21

---

## 1. Overview

NEXUS enforces a **zero-trust, capability-based security model** across all layers. No identity is trusted by default — every operation requires a cryptographically-signed `CapabilityToken`, all transport is mutually authenticated via post-quantum TLS, and all key material is lifecycle-managed through an HSM-backed `KeyRotationScheduler`.

This document covers:
- Zero-trust identity model and policy enforcement points
- Post-quantum cryptography (PQC) certificate chain
- `CapabilityToken` structure and claim semantics
- `IdentityService` provisioning flow
- HSM adapter interface and key hierarchy
- Key rotation lifecycle and revocation propagation

---

## 2. Zero-Trust Identity Model

### 2.1 Core Principles

1. **Never trust, always verify** — every inter-service call carries a signed token; no ambient authority
2. **Least privilege** — tokens encode only the capabilities required for a specific operation
3. **Assume breach** — all paths are authenticated even within the same cluster
4. **Continuous verification** — tokens have short TTLs (default 15 min); long-lived sessions use refresh via IdentityService

### 2.2 Identity Namespaces

| Namespace | Format | Example |
|---|---|---|
| Node identity | `nexus:node:<uuid>` | `nexus:node:a1b2c3d4-...` |
| Agent identity | `nexus:agent:<domain>:<name>` | `nexus:agent:intelligence:cogkernel-01` |
| Service identity | `nexus:svc:<package>:<class>` | `nexus:svc:security:IdentityService` |
| Human operator | `nexus:human:<username>` | `nexus:human:kyle_steen` |
| Federated peer | `nexus:fed:<cluster_id>:<node_id>` | `nexus:fed:mars-cluster-01:node-7` |

### 2.3 Policy Enforcement Points (PEP)

Every NEXUS package boundary is a PEP. The flow is:

```
Caller → [PEP: verify CapabilityToken] → [PDP: policy decision] → Resource
```

- **PEP** (Policy Enforcement Point): intercepts the call, extracts and verifies the token
- **PDP** (Policy Decision Point): evaluates capability claims against the operation's required permissions
- **PAP** (Policy Administration Point): `IdentityService` manages capability issuance

---

## 3. Post-Quantum Cryptography (PQC) Certificate Chain

### 3.1 Algorithm Selection

| Purpose | Algorithm | Standard |
|---|---|---|
| Key Encapsulation | Kyber-1024 (ML-KEM) | NIST FIPS 203 |
| Digital Signatures | Dilithium-3 (ML-DSA) | NIST FIPS 204 |
| Hash | SHA3-512 | NIST FIPS 202 |
| Hybrid TLS | X25519Kyber768 | IETF Draft |

All classical RSA/ECDSA is **deprecated**. Hybrid mode (classical + PQC) is used during the migration window only.

### 3.2 Certificate Chain Hierarchy

```
NEXUS Root CA (Dilithium-3, offline HSM)
  └── Cluster Intermediate CA (Dilithium-3, online HSM)
        └── Node Certificate (Dilithium-3, auto-issued)
              └── Service Certificate (Dilithium-3, short-lived 24h)
```

- **Root CA** is air-gapped, only used to sign Intermediate CAs
- **Cluster Intermediate CA** signs Node certificates at boot time
- **Node certificates** sign Service certificates on demand
- All certificates embed the `nexus:` identity namespace string in the Subject Alternative Name (SAN)

### 3.3 PQC Handshake Flow

```
Client                              Server
  |------ ClientHello (Kyber KEM) ------>|
  |<----- ServerHello + KEM ciphertext --|  
  |------ Finished (Dilithium sig) ----->|
  |<----- Finished (Dilithium sig) ------|
  |========== Encrypted channel ========|
```

1. Client sends ClientHello with supported PQC cipher suites
2. Server encapsulates a shared secret using client's Kyber-1024 public key
3. Both sides derive session keys from the shared secret via HKDF-SHA3-512
4. Each side signs its Finished message with Dilithium-3
5. Mutual authentication complete; session begins

---

## 4. CapabilityToken Structure

### 4.1 Format

`CapabilityToken` is a signed JWT with PQC header:

```json
{
  "alg": "Dilithium3",
  "typ": "JWT+NEXUS"
}
```

### 4.2 Standard Claims

```json
{
  "iss": "nexus:svc:security:IdentityService",
  "sub": "nexus:agent:intelligence:cogkernel-01",
  "aud": ["nexus:svc:governance:GovernanceDAO"],
  "iat": 1753149600,
  "exp": 1753150500,
  "jti": "<uuid4>",
  "nexus:capabilities": [
    "governance:proposal:read",
    "governance:vote:cast"
  ],
  "nexus:context": {
    "node_id": "nexus:node:a1b2c3d4",
    "cluster": "earth-primary",
    "clearance": "operational"
  },
  "nexus:delegation_depth": 0
}
```

### 4.3 Capability Naming Convention

```
<package>:<resource>:<action>
```

Examples:
- `governance:proposal:read`
- `governance:vote:cast`
- `telemetry:metric:emit`
- `security:key:rotate`
- `network:route:configure`

### 4.4 Delegation

A token can delegate a subset of its capabilities to another identity by issuing a new token with `nexus:delegation_depth` incremented. Maximum delegation depth is **3**. Delegated tokens cannot grant capabilities the delegator does not hold.

---

## 5. IdentityService — Provisioning Flow

```
1. Bootstrap: Node boots → presents hardware attestation (TPM quote)
2. IdentityService verifies attestation against known PCR values
3. Issues Node Certificate signed by Cluster Intermediate CA
4. Agent/Service registers → presents Node Certificate + service manifest
5. IdentityService issues CapabilityToken with appropriate claims
6. Token refreshed every 15 min via IdentityService.refresh(token)
7. On shutdown: token revoked, node deregistered
```

### 5.1 Revocation

- Revoked tokens are tracked in an in-memory bloom filter per node (fast path)
- A gossip protocol propagates revocations to all cluster nodes within 500ms
- Revocation records are persisted to the `ImmutableLedger` (governance package)
- All PEPs check the local bloom filter on every token verification

---

## 6. HSMAdapter Interface

```python
class HSMAdapter(Protocol):
    def generate_keypair(self, algorithm: str, key_id: str) -> KeyHandle: ...
    def sign(self, key_id: str, message: bytes) -> bytes: ...
    def verify(self, key_id: str, message: bytes, signature: bytes) -> bool: ...
    def encapsulate(self, recipient_pub: bytes) -> tuple[bytes, bytes]: ...  # (ciphertext, shared_secret)
    def decapsulate(self, key_id: str, ciphertext: bytes) -> bytes: ...  # shared_secret
    def destroy_key(self, key_id: str) -> None: ...
    def list_keys(self) -> list[KeyMetadata]: ...
```

Two implementations are required:
- `SoftwareHSMAdapter` — uses `cryptography` + `pqcrypto` libraries; for dev/test
- `PKCS11HSMAdapter` — wraps a PKCS#11-compliant hardware HSM via `python-pkcs11`

---

## 7. Key Rotation Scheduler

### 7.1 Rotation Policy

| Key Type | Rotation Period | Trigger |
|---|---|---|
| Root CA | 5 years | Manual, HSM ceremony |
| Cluster Intermediate CA | 1 year | Scheduled |
| Node Certificate | 30 days | Scheduled or on compromise |
| Service Certificate | 24 hours | Scheduled |
| Session Keys | Per-session | Automatic |

### 7.2 Rotation Lifecycle

```
1. Scheduler detects key approaching expiry (10% of lifetime remaining)
2. Generates new keypair via HSMAdapter
3. Issues new certificate signed by parent
4. Broadcasts new certificate to cluster via DiscoveryService gossip
5. Old certificate enters "grace period" (accepts but not issued) for 1 rotation period
6. Grace period expires → old certificate revoked
7. Rotation event logged to ImmutableLedger
```

---

## 8. Requirements Traceability

| Requirement ID | Implemented By |
|---|---|
| SR-001 | `IdentityService` |
| SR-002 | `CapabilityToken` |
| SR-003 | `PQCKeyManager` |
| SR-004 | `HSMAdapter` (SoftwareHSMAdapter) |
| SR-005 | `HSMAdapter` (PKCS11HSMAdapter) |
| SR-006 | `KeyRotationScheduler` |
| SR-007 | `CapabilityToken.delegate()` |
| SR-008 | Zero-trust PEP middleware |
| SR-009 | Revocation bloom filter |
| SR-010 | Gossip revocation propagation |
| SR-011 | PQC TLS handshake |
| SR-012 | Certificate chain hierarchy |
| SR-013 | Hardware attestation bootstrap |
| SR-014 | ImmutableLedger rotation audit |

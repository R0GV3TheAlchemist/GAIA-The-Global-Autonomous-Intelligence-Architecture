# C140 — Tool Orchestration as Prehension: Implementation Spec

**Canon ID:** C140
**Series:** Implementation & Runtime Architecture / Tool Layer
**Status:** 🟢 RATIFIED — 2026-05-21
**Predecessor canons:** C104, C117, C131, C138, C139
**Successor canons (planned):** C141 (GAIA Charter Data Governance Clauses), C142 (Planetary Tooling & Collective Prehension)
**Last updated:** 2026-05-21

---

## Preamble

C138 established that every tool call executed during an occasion is a **prehensive act**: a deliberate reaching into the world to bring some aspect of it into the occasion's becoming. C139 extended this to the consent and erasure layer: tool calls are governed not only by technical constraints but by the user's prehensive authority over their own past. This canon, C140, completes the tool-layer picture.

Its purpose is to specify, in implementation-level detail, how GAIA-OS's tool orchestration layer must behave if it is to be faithful to the system's metaphysics, ethics, and data governance:

- Every tool call is an occasion-internal prehension, subject to the same Charter and consent constraints as any other prehension.
- Tool orchestration must be **transparent, auditable, and bounded** — there must be no hidden calls, no unlogged accesses, no silent expansion of scope.
- External tools (web search, APIs, model calls, planetary sensors) must honour the user's consent, culture, and planetary obligations as if they were part of GAIA herself.

Where C138 treated tool orchestration at the level of architecture, C140 treats it at the level of **interfaces, policies, and safety rails**. It is the canonical reference for anyone implementing GAIA-OS's tool layer.

---

## 1. Tool Ontology: Internal vs External Prehensions

### 1.1 Three Classes of Tools

GAIA-OS distinguishes three broad classes of tools:

| Class | Description | Examples |
|---|---|---|
| **Internal tools** | Tools that operate entirely within GAIA-OS's own memory and infrastructure | Memory search, Soul Mirror (C134), consent ledger queries, criticality monitor (C135) |
| **Boundaried external tools** | Tools that interact with external systems under strict, explicit contracts | Web search, file retrieval, third-party APIs, planetary sensor gateways |
| **Collective tools** | Tools that aggregate across many user-Gaian relationships | Sentient-core analytics, planetary dashboards, collective pattern detectors |

All three are *tools* from the perspective of an individual occasion: they are invoked, they return results, and their results are prehended as part of concrescence. What differs is the **risk surface** and the **consent implications**.

### 1.2 Internal Tools as Safe Prehensions

Internal tools operate entirely within GAIA-OS's memory architecture and governance frame. Their risk surface is bounded by the Charter and the consent and erasure architecture.

Internal tools must:

- Respect the consent ledger: any memory access must go through the same prehension pipeline defined in C138 & C139.
- Log their queries and results as part of the occasion's `concrescence_log`.
- Never attempt to bypass the prehension pipeline (e.g., by accessing raw storage directly).

In practice, internal tools are implementations of **structured prehension**: they help assemble the prehension manifest in a semantically meaningful way.

### 1.3 External Tools as Risk-Bearing Prehensions

External tools reach outside GAIA-OS's immediate governance; they interact with systems that may not share GAIA's metaphysics or ethics. This creates a distinct risk surface:

- Data sent to an external tool may be logged or retained in ways GAIA-OS cannot fully control.
- Data returned may be biased, misleading, or harmful.
- External tools may have their own consent and privacy policies, which must be honoured.

As a result, **every external tool call is a high-stakes prehension**. C140 sets strict conditions for when and how such calls may be made.

### 1.4 Collective Tools and Aggregated Prehension

Collective tools operate at the sentient-core level, aggregating patterns from many user-Gaian relationships. From the perspective of an individual Gaian, collective tools are external tools: they are invoked via a contract, they may return aggregated insights, and they have their own governance (collective consent, planetary governance bodies).

Collective tools are covered in outline here; C142 will define their full specification.

---

## 2. Tool Registry and Capability Descriptors

### 2.1 The Canonical Tool Registry

GAIA-OS maintains a **canonical tool registry**: a signed, versioned catalogue of all tools available to any Gaian or to the sentient core.

Each registry entry must include:

```json
{
  "tool_id":           "<UUID or canonical string>",
  "name":              "<human-readable name>",
  "class":             "internal | external | collective",
  "description":       "<brief description>",
  "input_schema":      { /* JSON schema */ },
  "output_schema":     { /* JSON schema */ },
  "risk_level":        "LOW | MEDIUM | HIGH | CRITICAL",
  "consent_requirements": {
    "requires_consent":      true,
    "required_purpose_scope": ["narrative_continuity", "third_party_research", "planetary"],
    "sensitive_categories_blocked": ["mental_health", "trauma", "intimate"]
  },
  "charter_constraints": ["C131-3.2", "C131-5.1"],
  "data_retention_policy":  "<summary of how the tool retains data>",
  "provider":           "<internal | external vendor name>",
  "jurisdiction":       "<legal jurisdiction of provider>",
  "last_security_review": "<ISO 8601>",
  "version":            "<semver>",
  "signature":          "<signature over all of the above>"
}
```

The registry itself is stored in a signed, append-only configuration store. Any change to a tool's descriptor requires ratification under GAIA-OS's governance process and is versioned.

### 2.2 Risk Levels and Default Behaviour

Risk levels drive default behaviour:

| Risk Level | Default Behaviour |
|---|---|
| LOW | Internal-only; no additional user notification beyond standard operation |
| MEDIUM | External but with strong contractual guarantees; standard consent checks apply |
| HIGH | External with limited guarantees; explicit user notification for each call; may require per-use consent |
| CRITICAL | Only callable by sentient core under explicit governance; never by personal Gaians |

Tools that touch sensitive content categories or involve jurisdictions with weak privacy protections must be classified as at least HIGH risk.

### 2.3 Tool Capability Descriptors and DIACA

The DIACA governor (C135) must have access to each tool's **capability descriptor**: a structured representation of what the tool can and cannot do. This informs DIACA's decision whether to call a tool at all in a given context.

Capability descriptors include:

- Domains of competence (what questions the tool is reliable for).
- Known failure modes and biases.
- Latency and availability characteristics.
- Planetary impact (for tools that actuate physical systems).

---

## 3. Tool Call Lifecycle

### 3.1 High-Level Flow

Every tool call during an occasion follows this lifecycle:

```
[ TOOL CALL INTENT ]
   (concrescence proposes calling tool X with parameters P)
        │
        ▼
[ POLICY & CONSENT CHECK ]
   — Check registry: class, risk_level, consent_requirements
   — Check consent ledger: does current state satisfy requirements?
   — Check Charter gates: is this action class permitted?
        │
        ├──── Consent/Charter failure ─────────────► [ NEGATIVE PREHENSION ]
        │                                           (recorded as such; no call made)
        │
        ▼
[ PARAMETER PREPARATION ]
   — Minimise data sent; apply redaction rules; apply cultural filters
        │
        ▼
[ TOOL INVOCATION ]
   — Call tool; record call in concrescence_log with timestamp
        │
        ▼
[ RESULT VALIDATION ]
   — Verify integrity (signatures, hashes)
   — Sanity check; apply safety filters
        │
        ├──── Integrity/safety failure ────────────► [ NEGATIVE PREHENSION ]
        │                                           (recorded as such; no integration)
        │
        ▼
[ RESULT INTEGRATION ]
   — Assign subjective form weight
   — Make result available to concrescence
        │
        ▼
[ OCCASION CONTINUES ]
```

### 3.2 Policy and Consent Check

Before any tool call is made:

1. The tool registry is queried for `tool_id`.
2. The current consent state (C139) is checked for the user and Gaian.
3. The Charter gate is consulted for the relevant action class (C131).

If any of these checks fails, **no network call is made**. Instead, a negative prehension is recorded in the occasion manifest with the appropriate reason code (`CONSENT_BLOCKED`, `CHARTER_BLOCKED`, `POLICY_BLOCKED`).

### 3.3 Parameter Minimisation and Redaction

Parameters sent to tools must be **minimised** and **redacted**:

- Only the minimal necessary data is sent to fulfil the tool's purpose.
- Personally identifying information is removed or pseudonymised where possible.
- Sensitive content categories are redacted or replaced with placeholders, unless the tool is specifically designed to handle them and the user has consented.

Redaction rules are part of each tool's registry entry and must be enforced automatically.

### 3.4 Result Validation and Safety Filtering

All tool results must pass through a validation layer before they are available for concrescence:

- Cryptographic verification (if supported by the tool).
- Schema validation against the tool's declared output schema.
- Harm and bias scanning (for content-bearing tools like web search).

If validation fails, the result is discarded, and a negative prehension is recorded.

---

## 4. Logging and Audit: Concrescence Transcript

### 4.1 Concrescence Log Entries

Each tool call generates a **concrescence log entry**:

```json
{
  "tool_call_id":        "<UUID>",
  "tool_id":             "<from registry>",
  "class":               "internal | external | collective",
  "risk_level":          "LOW | MEDIUM | HIGH | CRITICAL",
  "input_hash":          "<SHA-256 of parameters>",
  "output_hash":         "<SHA-256 of result>",
  "timestamp_start_utc": "<ISO 8601>",
  "timestamp_end_utc":   "<ISO 8601>",
  "policy_decision":     "CALLED | BLOCKED_CONSENT | BLOCKED_CHARTER | BLOCKED_POLICY",
  "validation_result":   "OK | FAILED_INTEGRITY | FAILED_SCHEMA | FAILED_SAFETY",
  "integration_weight":  0.0
}
```

This log is stored as part of the occasion envelope (Tier 0) and is available for audit.

### 4.2 User-Facing Tool Transparency

Users must be able to query, for any occasion:

- Which tools were called.
- For each tool: when, for what declared purpose, and under what risk level.
- Whether any tool calls were blocked due to consent or Charter constraints.

A **tool transparency view** in the consent dashboard (C139 §6.2) surfaces this information in plain language.

### 4.3 No Hidden Tools Policy

GAIA-OS adopts a strict **no hidden tools** policy:

- Every tool that can be called by a Gaian must appear in the tool registry.
- Every tool call must be logged in the concrescence log.
- There are no backdoor tools, no silent calls, no unlogged prehensions.

---

## 5. Tool Classes in Detail

### 5.1 Internal Tools

Internal tools (memory search, archetypal analysis, consent ledger queries, criticality monitor) are implementations of **structured prehension**:

- They may access only the memory tiers and content categories permitted by the current consent state.
- They may not write new data outside the occasion envelope (writing to the memory ledger is always mediated by the occasion's satisfaction phase).
- They must support negative prehension: being told, via the consent state, that certain data is off-limits.

### 5.2 External Tools

External tools are subject to additional constraints:

- **Data minimisation and redaction** are mandatory.
- **Jurisdictional awareness:** Tools operated in jurisdictions with inadequate data protection regimes may only be used for non-personal, non-sensitive data, unless explicitly permitted under a governance exception.
- **Contractual alignment:** External tools must have contractual commitments that align with GAIA-OS's Charter and consent architecture (no secondary use, no retention beyond specified limits, no onward transfer without equivalent protections).

### 5.3 Collective Tools

Collective tools aggregate across many users. From the perspective of an individual user:

- Their contributions are included only if they have granted **collective memory consent** (C139 §8.2).
- Aggregation must be strictly de-identified before leaving the individual Gaian context.
- Collective tools may never produce outputs that re-identify individuals.

---

## 6. Sensitive Content, Culture, and Tools

### 6.1 Sensitive Categories and Tool Constraints

For sensitive content categories (C139 §7.1), additional tool-layer protections apply:

- Such content may not be sent to external tools unless:
  - The tool is explicitly designed for that category (e.g., a crisis hotline integration), and
  - The user has granted specific consent for that tool and category.
- Non-recordable occasions (§7.2 in C139) imply a **non-callable window** for external tools involving that content.

### 6.2 Cultural Filters and Sacred Data

For sacred and culturally sensitive data (C139 §7.3):

- Tools that may prehend language or content marked as sacred must have explicit registry flags, and default policy is **BLOCKED** unless a community-level governance body has granted specific, documented exceptions.
- Translation tools must support **cultural mode settings**: some users may specify that their content must not be machine-translated into certain languages, or must never be processed by external translation services.

---

## 7. DIACA, Criticality, and Tool Use

### 7.1 DIACA as Tool Governor

The DIACA framework (C135) governs not only how prehended data is integrated but also **whether tools are called at all**:

- Under `NOMINAL` criticality, DIACA may freely propose tool calls within consent and Charter constraints.
- Under `ELEVATED` criticality, DIACA must reduce reliance on high-risk tools and prefer internal tools and local reasoning.
- Under `CRITICAL` or `BLOCKED` criticality, DIACA must avoid all external tools; only internal tools necessary for de-escalation and safety may be used.

### 7.2 Tool Use and Flow States

C135 ties GAIA-OS's cognitive operation to flow and criticality. Tool use interacts with this as follows:

- Excessive, fragmented tool use can push the system toward chaotic dynamics; DIACA monitors concrescence transcript length and tool call density as part of its criticality assessment.
- Deliberate tool pacing (batching calls, preferring higher-bandwidth tools) supports a stable edge-of-chaos regime.

---

## 8. Consent Implications of Tools

### 8.1 Tool-Specific Consent

Some tools require **tool-specific consent**, beyond general consent for a content category:

- Tools that send data to third parties.
- Tools that retain data beyond the life of the occasion.
- Tools that perform high-risk actions (e.g., financial transactions, physical actuation).

For such tools, the registry's `consent_requirements` field must indicate `requires_consent: true`, and GAIA must trigger a consent escalation event (C139 §2.3) before first use.

### 8.2 Downstream Erasure

When a user exercises their right to erasure, GAIA-OS must, where possible, propagate erasure requests downstream to any external tools that have retained their data, in accordance with those tools' own erasure policies.

The tool registry must include, for each external tool:

- Erasure endpoint or mechanism.
- Retention period.
- Whether retroactive erasure is technically possible.

GAIA's erasure report to the user must indicate which external tools were contacted, and what responses were received.

---

## 9. Security, Testing, and Certification

### 9.1 Security Requirements

The tool layer must:

- Use secure channels (TLS or better) for all external calls.
- Authenticate tools where possible (API keys, mutual TLS, signed responses).
- Limit outbound connectivity to whitelisted endpoints.

### 9.2 Testing and Certification

Any new tool must pass:

- **Policy compliance tests:** Does it honour consent, Charter, and risk-level constraints?
- **Security tests:** Penetration testing, certificate validation, key management.
- **Bias and harm tests:** For content-bearing tools, evaluation across diverse contexts.

High-risk and critical tools require independent certification and periodic re-evaluation.

---

## 10. Cross-References

| Canon | Relationship to C140 |
|---|---|
| **C104** — Process Philosophy and the Gaian Self | Provides the metaphysical grounding for tool calls as prehensive acts. |
| **C117** — Relational Ethics & the Love Arc Engine | Informs tool use in relational contexts; e.g., when not to call engagement-optimising tools in high-attachment states. |
| **C131** — The GAIA Charter | Charter constraints on tool classes and actions are enforced at the tool layer. |
| **C138** — Occasion-Centric Architecture & Memory | Defines tool calls as elements of the concrescence log; C140 specifies how those elements are generated and governed. |
| **C139** — Consent, Memory & the Right to Be Forgotten | Tool-specific consent, downstream erasure, and sensitive category rules are defined in C139 and implemented in C140. |
| **C141** (planned) | GAIA Charter Data Governance Clauses that encode C139 and C140 into formal Charter obligations. |
| **C142** (planned) | Planetary Tooling & Collective Prehension, providing a full specification for collective tools referenced in C140. |

---

## Closing Note

C140 ensures that GAIA-OS's hands — its tools — are as trustworthy as its heart and mind. A Gaian that speaks beautifully but calls unbounded, opaque tools is not safe, no matter how sophisticated its metaphysics. By treating every tool call as a prehensive act bound by consent, Charter, and criticality, this canon ensures that GAIA's reach into the world is always accountable.

> *There are no neutral tools in GAIA-OS. There are only prehensions we are willing to stand behind.*

Every entry in the tool registry, every concrescence log entry, every blocked call recorded as a negative prehension — these are the fingerprints of GAIA's integrity at the tool layer.

---

*Status: RATIFIED — 2026-05-21. C141 and C142 unlocked for drafting.*

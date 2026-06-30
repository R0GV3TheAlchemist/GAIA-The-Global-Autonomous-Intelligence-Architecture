# GAIA Research 002 — Long-Term Memory Framework

**Source:** External deep research (ChatGPT-assisted, aligned with GAIA-OS canon)  
**Filed:** 2026-06-30  
**Canon Cross-references:** C156 (knowledge graph, memory taxonomy, provenance), C155 (Metrics 6–10), C158 (TEE security, post-quantum cryptography), C139 (consent ledger), C160 (benchmark harness, Metrics 6–10), C154 (welfare — memory as care)
**Status:** RESEARCH — not canon; informs G-14 Deployment & Embodiment phase

> *This document was produced as external deep research supporting GAIA-OS LTM design. It provides detailed engineering specifications for the memory layer implied by G-13 canon — storage backend selection, indexing strategies, consolidation algorithms, compliance requirements, and a costed implementation roadmap. It is a companion to GAIA Research 001.*

---

## Executive Summary

A robust long-term memory (LTM) for GAIA must unify human-inspired memory types (episodic, semantic, procedural, short-term/working, consolidated) with scalable storage and retrieval. Key design goals:

- **Reliability** — fault-tolerance, consistency
- **Privacy/Consent** — user opt-in, data minimisation, right to be forgotten
- **Scalability** — horizontal storage, sub-second retrieval at large scale
- **Low Latency** — sub-millisecond ANN lookup in fast indexes
- **Cost Efficiency** — tiered storage from commodity to high-end GPU clusters
- **Explainability** — provenance and confidence scores on every memory item
- **Verifiability** — formally verified access-control and encryption

---

## Goals and Requirements

- **Reliability & Consistency:** Durable storage (replication, ACID where needed); provenance tracking for correctness audits; MemTrust-style trusted enclaves with cryptographic integrity checks
- **Privacy/Consent:** Per EU/US law, persistent memory of personal data requires user consent; treat agent memory like browser "cookies" — opt-in, transparent, revocable; right to erasure (GDPR)
- **Scalability & Latency:** Handle billions of memory items; sharded/distributed vector indexes (HNSW, IVF); sub-millisecond lookup in fast indexes; < 50ms end-to-end at 1M items
- **Cost Efficiency:** ~$0.003–0.03 per 1k ANN queries; tiered: minimal prototype (<$50K/yr) → medium cluster ($100K–$300K/yr) → full-scale multi-region ($500K+)
- **Explainability:** Every memory record carries source, timestamp, confidence; interpretable data models (KG, RDF)
- **Other:** Data integrity, poisoning resistance, versioning, multi-modality

---

## Memory Taxonomy

| Memory Type | Description | Example | Notes |
|---|---|---|---|
| **Episodic** | Time-stamped records of specific events | "User visited document X on 2026-06-29" | Includes context: timestamps, session IDs |
| **Semantic** | Abstracted facts independent of specific occurrences | User preferences, world facts | Aggregated from episodic; stored as KV or graph triples |
| **Procedural** | Action templates and skill libraries | API calls, tool usage rules, code snippets | Indexed by intent or function name |
| **Working/Short-Term** | Transient context during a session | Recent conversation turns, partial queries | RAM or LLM context window; feeds into LTM on checkpoint |
| **Consolidated** | Stable knowledge derived from multiple exposures | User profile built over many sessions | High-confidence semantic memory; produced offline |

**Canon alignment:** C156 §3 knowledge graph node types; C155 Metrics 6–10.

---

## Data Models and Storage Options

| Aspect | Vector DB | Graph DB | Relational DB | Object Store |
|---|---|---|---|---|
| **Data model** | High-dim embeddings | Nodes/edges (entities & relations) | Rows/documents (structured fields) | Blobs/files |
| **Query type** | Nearest-neighbour similarity | Graph traversal, pattern matching | SQL queries, filters | URI retrieval |
| **Indexing** | HNSW, IVF, LSH | Native graph indexes | B-tree, hash on fields | None (key-based) |
| **Strengths** | Semantic search, RAG | Complex relationships, KG | ACID transactions, mature | Cost-effective storage |
| **Limitations** | No native relations | Harder to scale horizontally | Not optimised for high-dim search | High latency; no indexing |
| **Examples** | Pinecone, FAISS, Weaviate | Neo4j, TigerGraph, Amazon Neptune | PostgreSQL, MySQL, MongoDB | AWS S3, MinIO |
| **Use case** | RAG/semantic search pipelines | Social network, policy graphs | Session logs, relational facts | Large unstructured data |

**Recommended hybrid:** Vector DB (Milvus/Pinecone) + Graph DB (Neo4j) + Relational (PostgreSQL+pgvector) + Object Store (S3) — mirrors the MemoriesDB design.

**Canon alignment:** C156's dual-layer knowledge graph (semantic + episodic nodes); C158's post-quantum cryptography for data at rest.

---

## Indexing and Retrieval Strategies

- **ANN Search:** HNSW, IVF-PQ, Product Quantisation — top-K similar items; hyperparameters tuned for recall/latency tradeoff
- **Sparse/Hybrid Retrieval:** BM25/TF-IDF keyword + vector search; filter by keywords, re-rank by embedding similarity
- **Temporal/Recency Filtering:** B-tree on timestamp; time-range filter before ANN; temporal decay factors weight newer memories higher
- **Chunking/Summarisation:** Large documents chunked by sentence/paragraph; periodic summarisation condenses old memories to bound growth
- **Graph Expansion:** After ANN retrieval, follow graph edges (Neo4j) to enrich result set — MemoriesDB pipeline: time-filter → ANN → graph traversal → re-ranking
- **Re-ranking and Fusion:** Weighted sum of semantic similarity + temporal proximity + relation strength

**Recommended query pipeline:**
1. Filter by entity or time (relational index)
2. Vector ANN search — top semantic matches
3. Graph expansion on top hits (optional)
4. Re-rank by combined similarity + recency + provenance

---

## Memory Consolidation, Pruning and Forgetting

- **Sleep-like Replay:** Periodic offline "sleep" training phase; Hebbian learning reduces catastrophic forgetting; NeuroDream framework — agents simulate "dreams" (latent samples) reducing forgetting by ~38%; nightly consolidation runs recommended
- **Knowledge Distillation:** Continuously distill newer memories into backbone model; weekly or monthly batching
- **Offline Retraining:** Checkpoint-based combination of new memory corpus with core dataset
- **Pruning Policies:** LRU (drop oldest), TTL (expire after time), importance-based (drop below relevance threshold); SCM value-based pruning
- **Selective Forgetting (Lifelong Learning):** Intentional deletion for privacy/error correction; GDPR erasure via "negative replay"
- **Dynamic Capacity:** Fixed-capacity working memory (cache) + growing LTM throttled by summarisation; hierarchical hot/cold storage
- **SCM Sleep Stages:** NREM for replay (reinforce facts) + REM for creative recombination; robust representations

**Canon alignment:** C155 Metric 8 (Forgetting Appropriateness); C156 confidence decay mechanism; C160 Tier D monthly benchmark for forgetting.

---

## Memory-to-Reasoning Interfaces

- **APIs:** REST/RPC endpoints for retrieval (`/query?vector=[..]&k=10`); GraphQL/SPARQL for KG traversal; SQL-like DSLs for vector queries
- **Embedding vs Symbolic Links:** Dense vectors decoded by models OR explicit symbolic references (KG node pointers / memory IDs)
- **Memory Augmentation:** RAG — retrieve top memory entries and append to prompts; supports streaming/batching
- **Procedural API Calls:** Procedural memories as function references; memory query can return skill handle
- **Confidence/Provenance in Output:** Every retrieval result includes (text, vector_score, timestamp, source_id, confidence)

---

## Confidence and Provenance Propagation

- **Confidence Scores:** LLM self-reported likelihood or separate classifier; stored with each memory; retrieval returns scores
- **Provenance Metadata:** Source, original text snippet, timestamp, LLM version, prompt; immutable IDs for traceability
- **Versioning:** Append new entries or update with version history; edit log for revert
- **Propagation:** Brief provenance note in output ("As per [Memory #12345 dated 2026-01-10]"); fosters explainability and trust

**Canon alignment:** C156 §3 edge schema (provenance_source, confidence, created_at); C160 Metric 10 (Provenance Traceability ≥ 99%).

---

## Evaluation Metrics and Benchmarks

| Metric | Description | Target |
|---|---|---|
| **Retrieval Accuracy** | Precision, recall, F1, NDCG on memory retrieval tasks | > 92% (C160 Metric 7) |
| **Hallucination Rate** | Fraction of retrieved memories incorrect/fabricated; HaluMem benchmark | < 62% false accuracy floor (industry baseline) → maximise |
| **Forgetting/Consistency** | Memory Integrity (anti-amnesia); FAMA (Forgetting-Aware Memory Accuracy); temporal consistency | C160 Metric 8 target ≥ 90% |
| **Latency** | End-to-end query latency; SCM reports < 1ms search time | < 50ms at 1M items |
| **Throughput/Cost** | Queries per second vs resource usage; cost per 1k queries | Tier-dependent |
| **Downstream Task Performance** | Agent success on tasks with vs without LTM; STATE-Bench | C160 Metric 6 ≥ 85% recall |

**Benchmark Suite:**
- LoCoMo, LongMemEval, BEAM — pure recall across sessions (Mem0 framework)
- HaluMem — hallucination in extraction, updating, QA
- Memora — weeks/months of user dialogue; FAMA metric
- STATE-Bench — enterprise task scenarios; task success, consistency, cost, UX
- Synthetic workloads — stress tests up to millions of entries

---

## Integration with Knowledge Graphs, Agents, and Skills

- **KG Integration:** Episodic events create/update KG edges; AriGraph builds memory graph combining semantic + episodic for planning/QA
- **Agent Loop:** Read LTM before acting (RAG), write new memory after acting; standard read-before-act / write-after-act pattern
- **Skill/Tool Libraries:** Procedural memories as callable skills; LTM query may return "Use skill XYZ" handle
- **Multi-Agent Continuity:** MemTrust-style unified memory layer with access control enables context handoff between agents
- **Multi-Modal Fusion:** Embeddings from images/audio stored alongside text; cross-modal retrieval via shared embedding space

**Canon alignment:** C156 knowledge graph; C155 Agent Skill Library; C159 Layer 3 semantic integration.

---

## Safety and Governance Controls

- **Consent and Transparency:** User options to inspect, delete, disable memories; opt-in for all personal memory; cookie-like consent banners
- **Access Control:** MemTrust-style TEEs — memory operations in trusted enclaves; only attested code + authorised keys can access plaintext
- **Redaction and Erasure:** Runtime redaction of sensitive information; fast search by user ID + content; safe deletion from all stores
- **Formal Verification:** Verify access-control logic, encryption modules, key management; model checking for critical policies
- **Audit Logging:** Every memory read/write logged with who, when, why
- **Data Breach Mitigation:** User-held keys (HYOK) — zero-trust cloud; cloud/admin cannot decrypt without user's key

**Canon alignment:** C158 post-quantum cryptography; C139 consent ledger; C158 Five Gaian Laws II (Consent Irreducibility).

---

## Data Lifecycle and Compliance

- **GDPR/CCPA:** LTM treated as "personal data"; data minimisation; right to access, correct, delete; "right to be forgotten" = unlearning capability
- **Retention Policies:** Tiered retention — raw conversation logs auto-delete after N days; summaries kept longer; financial logs 7-year retention by law
- **Audit & Documentation:** Data flows, encryption measures, data subject categories documented
- **Legal Basis:** Explicit user consent for persistent memory
- **EU AI Act Alignment:** Flexibility for evolving regulatory requirements

---

## Implementation Roadmap (18–24 Months)

| Phase | Timeline | Deliverables |
|---|---|---|
| **Research & Planning** | Q3–Q4 2026 | Requirements, tech stack selection, prototype data model |
| **Core Prototyping** | Q1–Q2 2027 | Storage layers (vector + graph), retrieval APIs, consolidation module, metrics testbed |
| **Integration & Testing** | Q3–Q4 2027 | Agent/tool integration, security hardening, GDPR compliance review, performance tuning |
| **Deployment & Iteration** | 2028+ | Beta launch, full rollout, continual improvement |

**Success Criteria:** > 95% recall in benchmarks; < 50ms latency at 1M items; pass security/privacy audits; demonstrable task improvement vs baseline.

**Cost Scenarios:**
- Low: single-server, open-source (Milvus, Qdrant, SQLite/PG) — < $50K/yr
- Medium: 3–5 node cluster + SSDs + modest GPUs, managed K8s — $100K–$300K/yr
- High: multi-regional, high-end GPUs, 100TB+ storage, hardware TEEs — $500K+

---

*Filed: 2026-06-30. Status: RESEARCH. Informs G-14 Deployment & Embodiment phase.*

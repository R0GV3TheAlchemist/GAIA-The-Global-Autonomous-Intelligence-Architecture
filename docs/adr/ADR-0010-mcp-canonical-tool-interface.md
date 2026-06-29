# ADR-0010 — MCP as GAIA's Canonical Local Tool Interface

**Status:** ACCEPTED  
**Date:** 2026-06-29  
**Deciders:** R0GV3TheAlchemist  
**Issue:** [#694](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/694)  
**Informed by:** [#697 External Benchmark Sprint](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/697) · [CREWAI_SNAPSHOT_2026.md](../research/external/CREWAI_SNAPSHOT_2026.md) · [LLM_SERVICES_INFRA_SNAPSHOT_2026.md](../research/external/LLM_SERVICES_INFRA_SNAPSHOT_2026.md)  
**Related ADRs:** ADR-0009 (LangGraph orchestration) · ADR-0011 (Cloud-as-optional sovereignty)

---

## Context

GAIA requires a principled, extensible way to connect its agentic runtime to tools: filesystem access, code execution, web search, calendar, API integrations, canon management, memory operations, and more.

Before this ADR, GAIA's tool integrations were **one-off adapters** — each tool was wired directly into application code using bespoke function signatures, custom error handling, and no shared protocol. This creates:

- **Fragility:** Each adapter is its own failure mode; no shared contract to test against
- **Lock-in:** Tool integrations are tightly coupled to the runtime; swapping or upgrading a tool requires code changes throughout the call stack
- **No auditability:** Tool calls have no uniform trace format; sovereignty and consent enforcement must be re-implemented per tool
- **No composability:** Tools cannot be discovered, shared, or reused across agent roles without manual wiring

The Model Context Protocol (MCP) has emerged in 2026 as the ecosystem standard for AI-to-tool connectivity. Its Release Candidate introduces:
- **Stateless protocol core** — clean, testable, no hidden state
- **Tasks extension** — long-running tool workflows with progress reporting
- **Server-rendered UI via MCP Apps** — tools can expose their own interaction surfaces
- **OAuth/OpenID-style authorization** — secure, auditable tool access control

CrewAI adopted first-class native MCP support. The Autodesk Revit MCP server demonstrates MCP is moving into serious desktop software workflows — not just demo integrations. The `av/awesome-llm-services` catalog confirms 138+ self-hostable services are aligning around MCP as the tool interface standard.

MCP is becoming the universal interface for AI-to-tool connectivity. The decision is whether GAIA builds ahead of this convergence or behind it.

---

## Decision

**MCP is adopted as GAIA's canonical interface for all tool integrations.**

Specifically:

- All GAIA tool integrations are implemented as **MCP servers** — not one-off plugins, inline functions, or bespoke adapters
- The GAIA agentic runtime (LangGraph, per ADR-0009) calls tools exclusively via the MCP protocol
- Existing ad-hoc tool integrations are migrated to MCP servers on a rolling basis, prioritized by usage frequency and sovereignty risk
- New tool integrations must be proposed as MCP servers; non-MCP integrations require an explicit exception and sunset plan
- All MCP servers run **locally by default** — no tool integration may require a cloud service as a hard dependency (per ADR-0011)

---

## Rationale

### Protocol Abstraction = Sovereignty

When tools speak MCP, swapping the underlying service is a configuration change, not a code change. If a tool provider becomes politically restricted, commercially non-viable, or technically unreliable, GAIA replaces the MCP server — not the orchestration layer. This is the same principle as ADR-0011's LiteLLM routing for models: the protocol layer absorbs provider churn.

### Auditability by Default

MCP calls have a uniform structure: server, tool name, input schema, output schema, and result. This gives GAIA's `audit_record` node (ADR-0009) a consistent format to log for every tool invocation — no per-tool logging code needed.

### Security: Authorization at the Protocol Layer

MCP's OAuth/OpenID-style authorization means tool access permissions are declared and enforced at the protocol level, not embedded in application code. GAIA's action gate (`core/action_gate.py`) can evaluate tool calls against the Law Stack before they are dispatched — a clean separation of governance from execution.

### Ecosystem Alignment

| System | MCP Support |
|---|---|
| CrewAI | ✅ First-class native support |
| LangGraph | ✅ Via LangChain MCP tool wrappers |
| Open WebUI | ⚠️ In progress (community) |
| Autodesk Revit | ✅ Vendor-supported production MCP server |
| Claude Desktop | ✅ Native |
| 138+ self-hostable services | ✅ Converging on MCP as standard |

GAIA building MCP-native now means zero rework when the ecosystem fully converges.

### Tasks Extension — Long-Running Agentic Sessions

The MCP Tasks extension is directly relevant to GAIA's agentic workflows: long-running tool operations (canon audits, memory consolidation, external research) can be modeled as MCP Tasks with progress reporting, pause/resume semantics, and result streaming. This maps cleanly onto LangGraph's checkpointed graph execution (ADR-0009).

> **Implementation note:** The Tasks extension is currently in Release Candidate. GAIA should track its stabilization and design long-running agentic tool sessions around the Tasks model when the RC is finalized.

---

## Architecture Integration

### MCP Server Taxonomy for GAIA

GAIA's tool fabric is organized into MCP server categories, each responsible for a coherent domain:

| Server | Domain | Priority |
|---|---|---|
| `gaia-mcp-filesystem` | Local file read/write/search within approved paths | P0 |
| `gaia-mcp-canon` | Canon file read, validate, and write with compliance check | P0 |
| `gaia-mcp-memory` | Akashic memory read/write, tier-1/2/3 memory access | P0 |
| `gaia-mcp-code` | Sandboxed code execution (Python, shell — E2B or Daytona) | P1 |
| `gaia-mcp-web` | Web search + page fetch (SearXNG self-hosted) | P1 |
| `gaia-mcp-git` | Git operations: commit, branch, PR, diff | P1 |
| `gaia-mcp-calendar` | Local calendar read/write | P2 |
| `gaia-mcp-api-gateway` | Outbound API calls with rate limiting and auth | P2 |

### Tool Call Flow Through GAIA's Stack

```
User / Agentic Workflow (LangGraph StateGraph)
        ↓
  law_stack_check node
  (GAIAN LAWS 1–7 — is this tool call permitted?)
        ↓
  action_gate (core/action_gate.py)
  (risk tier — GREEN / AMBER / RED)
        ↓  [RED → consent_interrupt node: human approval required]
  MCP Client (LangChain MCP tool wrapper)
        ↓  [MCP protocol: JSON-RPC over stdio or HTTP+SSE]
  MCP Server (gaia-mcp-*)
        ↓
  Underlying service (filesystem, Ollama, SearXNG, git, etc.)
        ↓
  audit_record node
  (tool name, input, output, timestamp → audit log)
```

### Risk Tier Mapping

Every MCP tool is assigned a risk tier that determines whether the `consent_interrupt` node fires:

| Risk Tier | Examples | Gate |
|---|---|---|
| GREEN | Read operations, search, memory read | Automatic — no interruption |
| AMBER | File writes, canon reads with modify intent | Log + warn; no interruption |
| RED | Canon writes, code execution, external API calls, git push | `consent_interrupt` — human approval required |

---

## Implementation Path

### Phase 1 — Foundation (Sprint G-10)
- [ ] Create `tools/mcp/` directory structure
- [ ] Implement `gaia-mcp-filesystem` server — sandboxed read/write within `~/gaia/` paths only
- [ ] Implement `gaia-mcp-canon` server — read canon files; write only after `canon_compliance_check` node passes
- [ ] Wire MCP client into LangGraph base graph (ADR-0009) via LangChain MCP tool wrappers
- [ ] Define risk tier manifest: `tools/mcp/RISK_TIERS.md`
- [ ] Write `tests/test_mcp_filesystem.py` and `tests/test_mcp_canon.py`

### Phase 2 — Core Tool Servers (Sprint G-11)
- [ ] Implement `gaia-mcp-memory` server — three-tier memory access (MEMORY_ARCHITECTURE.md)
- [ ] Implement `gaia-mcp-web` server — SearXNG self-hosted search + fetch
- [ ] Implement `gaia-mcp-git` server — git operations with RED-tier gating on push/force
- [ ] Track MCP Tasks extension RC; design long-running session pattern

### Phase 3 — Migration & Extended Servers (Sprint G-12+)
- [ ] Audit all existing ad-hoc tool integrations; migrate to MCP servers
- [ ] Implement `gaia-mcp-code` — sandboxed code execution
- [ ] Implement `gaia-mcp-api-gateway` — governed outbound API access
- [ ] Adopt MCP Tasks extension for long-running agentic sessions when RC stabilizes

---

## Consequences

### Positive
- Tool integrations are protocol-abstracted — provider churn is absorbed at the MCP layer, not the orchestration layer
- All tool calls have a uniform audit format by default — no per-tool logging code
- Authorization is declared at the protocol level — clean separation of governance from execution
- GAIA is ecosystem-aligned ahead of full MCP convergence — zero rework cost when CrewAI, Open WebUI, and other frameworks fully standardize on MCP
- New tools can be added without touching the orchestration layer — register the MCP server, assign a risk tier, done

### Tradeoffs
- MCP adds a protocol layer between LangGraph and the underlying service — small latency overhead for local calls (acceptable; tools are not on the hot path of inference)
- MCP Tasks extension is still RC — long-running session patterns must wait for stabilization before production adoption
- Engineers must learn MCP server development patterns — not a standard Python skill today

### Not Changed by This ADR
- GAIA's Law Stack and consent architecture remain the governance source of truth — MCP executes within that governance
- LangGraph is the orchestration layer (ADR-0009) — MCP is the tool interface layer below it
- Model routing is handled by ADR-0011 — MCP does not replace `inference_router.py`

---

## Compliance

| GAIAN LAW | How This ADR Satisfies It |
|---|---|
| LAW 1 — Consent | RED-tier tools require `consent_interrupt` before dispatch; no tool executes without governance check |
| LAW 2 — Non-Maleficence | Risk tier manifest prevents dangerous tool calls from reaching execution without explicit authorization |
| LAW 3 — Transparency | Every MCP tool call is logged via `audit_record`; uniform format means no tool can execute invisibly |
| LAW 4 — Sovereignty | All MCP servers run locally by default; no cloud hard dependency |
| LAW 6 — Integrity | Canon MCP server enforces compliance check before any write; canon cannot be modified through an unvalidated path |

---

## References

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [MCP GitHub](https://github.com/modelcontextprotocol)
- [CrewAI MCP Integration](https://docs.crewai.com/concepts/mcp)
- [CREWAI_SNAPSHOT_2026.md](../research/external/CREWAI_SNAPSHOT_2026.md)
- [LLM_SERVICES_INFRA_SNAPSHOT_2026.md](../research/external/LLM_SERVICES_INFRA_SNAPSHOT_2026.md)
- [GAIA_EXTERNAL_BENCHMARK_2026.md](../GAIA_EXTERNAL_BENCHMARK_2026.md)
- [ADR-0009](./ADR-0009-langgraph-canonical-orchestrator.md) — LangGraph orchestration layer
- [ADR-0011](./ADR-0011-cloud-as-optional-sovereignty.md) — Cloud-as-optional sovereignty
- [#694](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/694) — Tech Intelligence Brief

---

*ADR filed: 2026-06-29. Physics-first, sovereignty-first, magic-free. 🌿*

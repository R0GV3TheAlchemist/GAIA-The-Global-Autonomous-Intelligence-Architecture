# ADR-0011 — Cloud-as-Optional: GAIA's Local-First Sovereignty Principle

**Status:** ACCEPTED  
**Date:** 2026-06-29  
**Deciders:** R0GV3TheAlchemist  
**Issue:** [#694](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/694)  
**Informed by:** [#697 External Benchmark Sprint](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/697) · [LLM_SERVICES_INFRA_SNAPSHOT_2026.md](../research/external/LLM_SERVICES_INFRA_SNAPSHOT_2026.md) · Anthropic access restriction event (June 2026)  
**Related ADRs:** ADR-0009 (LangGraph orchestration) · ADR-0010 (MCP as canonical tool interface)

---

## Context

### The Triggering Event

In June 2026, Anthropic restricted access to its most advanced models in response to U.S. government export-control concerns. Access to frontier model capabilities — on which many production AI systems depend — was disabled overnight by a political decision outside any developer's control.

This is not a hypothetical threat. It happened. It will happen again.

### GAIA's Current Exposure

At the time of this ADR, `core/inference_router.py` is the single LLM routing layer for all GAIA model calls. A critical audit question is whether it has explicit local fallback logic — if a cloud provider returns 4xx/5xx or is unreachable, does the router automatically route to local Ollama, or does it propagate the failure?

If cloud availability is assumed anywhere in the routing logic, GAIA has a **single point of failure that a government decision, a vendor outage, or a policy change can trigger at any time.**

Beyond the model routing layer, the risk extends to any GAIA dependency that requires a cloud service to function: vector databases, observability backends, authentication providers, storage layers. Any hard cloud dependency is a sovereignty risk.

### The Ecosystem Confirms the Path

The `av/awesome-llm-services` catalog documents 138+ self-hostable LLM services and tools. Every critical capability GAIA needs — model serving, API routing, vector databases, observability, web search — has a production-quality, MIT or Apache-licensed, self-hostable alternative. The infrastructure exists. The decision is whether GAIA uses it.

---

## Decision

**Cloud LLM providers and cloud services are optional augmentation. GAIA must remain fully functional on local resources alone.**

Specifically:

1. **`inference_router.py` must implement explicit local fallback logic.** If any cloud provider is unavailable (network error, 4xx, 5xx, auth failure, or political restriction), the router automatically falls back to local Ollama without requiring a code change or manual intervention.

2. **LiteLLM is adopted as the unified API routing layer** for `inference_router.py`. LiteLLM provides a single interface supporting 100+ LLM providers including Ollama locally — sovereignty routing becomes a configuration change, not a code change.

3. **The recommended model routing hierarchy is adopted** (from #694 Tech Intelligence Brief):

```
Task complexity LOW    → Gemma 3 4B–12B       (fast, low memory, local)
Task complexity MEDIUM → Qwen 3.5 9B–27B      (balanced, multimodal, local)
Task complexity HIGH   → DeepSeek-R1 distill  (reasoning specialist, local)
Cloud augmentation     → Anthropic / OpenAI   (optional, never core dependency)
```

4. **No GAIA subsystem may declare a cloud service as a hard dependency.** Every subsystem must have a documented local fallback or self-hostable equivalent.

5. **A sovereignty routing test must exist** in `tests/test_inference_router.py` that mocks cloud provider unavailability and asserts local fallback activates correctly.

6. **CONTRIBUTING.md and README.md must state explicitly:**
   > *"Cloud LLM calls are optional augmentation. GAIA must remain fully functional on local models alone."*

---

## Rationale

### Sovereignty Is Not a Feature — It Is a Structural Property

A system that claims sovereignty but depends on a cloud provider for its core function is not sovereign. It is licensed. The moment that license is revoked — by a government, a vendor policy change, or a commercial decision — the system stops working. GAIA's sovereignty principle is meaningful only if it is enforced at the infrastructure layer, not just stated in documentation.

### The Threat Model Is Proven

The June 2026 Anthropic restriction event demonstrates that the threat is real, immediate, and outside any individual developer's control. The CIK threat taxonomy from the OpenClaw safety audit adds a second dimension: an AI system's Knowledge tier (including model access) is a primary attack surface. Restricting model access is a Knowledge-tier attack on the system. GAIA's defense is local model availability.

### LiteLLM: Sovereignty Routing as Configuration

Without a unified API layer, swapping from a cloud model to a local model requires changes across every call site in the codebase. With LiteLLM, the entire routing decision lives in a configuration file:

```python
# inference_router.py — with LiteLLM
import litellm
from litellm import completion

MODEL_ROUTING = {
    "low":    "ollama/gemma3:12b",
    "medium": "ollama/qwen3.5:27b",
    "high":   "ollama/deepseek-r1:distill",
    "cloud":  "anthropic/claude-sonnet-4-5",  # optional augmentation
}

FALLBACK_CHAIN = [
    MODEL_ROUTING["medium"],   # primary local
    MODEL_ROUTING["low"],      # fallback local
    # cloud is never in the fallback chain — it is opt-in only
]

def route(task_complexity: str, allow_cloud: bool = False) -> str:
    if allow_cloud and cloud_available():
        return MODEL_ROUTING.get("cloud", MODEL_ROUTING["medium"])
    return MODEL_ROUTING.get(task_complexity, MODEL_ROUTING["medium"])

def complete(prompt: str, complexity: str = "medium", allow_cloud: bool = False):
    model = route(complexity, allow_cloud)
    try:
        return completion(model=model, messages=[{"role": "user", "content": prompt}])
    except Exception:
        # Automatic fallback to local chain — never propagate cloud failure
        return completion(
            model=MODEL_ROUTING["low"],
            messages=[{"role": "user", "content": prompt}],
            fallbacks=FALLBACK_CHAIN
        )
```

Cloud is opt-in via `allow_cloud=False` default. The fallback chain contains only local models. A political restriction, outage, or auth failure is caught in the `except` block and resolved locally without surfacing to the caller.

### Model Tier Justification

| Model | Tier | Rationale |
|---|---|---|
| **Gemma 3 4B–12B** | LOW | Best consumer-hardware lightweight tier; multimodal; commercially usable open-weight license; fast on 8GB VRAM |
| **Qwen 3.5 9B–27B** | MEDIUM | Primary local workhorse; strong instruction following, vision, math, reasoning; targets 8–16GB VRAM tiers; directly addresses GAIA's multimodal reasoning gap |
| **DeepSeek-R1 distill** | HIGH | Reasoning specialist for multi-step planning, canon conflict resolution, complex agentic workflows; consumer-hardware viable via distilled variants |
| **Anthropic / OpenAI** | OPTIONAL CLOUD | Higher accuracy ceiling for edge cases; never in the fallback chain; never a required dependency |

---

## Self-Hostable Equivalents Registry

Every cloud service GAIA might otherwise depend on has a documented local alternative:

| Capability | Cloud Option (avoid hard dep) | Self-Hostable Alternative | License |
|---|---|---|---|
| LLM inference | Anthropic, OpenAI | **Ollama** + local models | MIT |
| API routing / fallback | — | **LiteLLM** | MIT |
| Vector database | Pinecone, Weaviate Cloud | **Qdrant** (local) / **Chroma** (dev) | Apache 2.0 |
| Observability / tracing | LangSmith Cloud, DataDog | **LangFuse** (self-hosted) | MIT |
| Web search | Bing, Google Search API | **SearXNG** (self-hosted) | AGPL |
| Code execution sandbox | E2B Cloud | **Daytona** (self-hosted) / local subprocess | Apache 2.0 |
| Auth / identity | Auth0, Cognito | **Keycloak** / local JWT | Apache 2.0 |
| Object storage | S3, GCS | **MinIO** (self-hosted) | AGPL |

---

## Implementation Path

### Phase 1 — Audit & Harden (Sprint G-10, CRITICAL)
- [ ] **Audit `core/inference_router.py`**: Document current routing logic; identify any implicit cloud-as-required assumptions
- [ ] **Add LiteLLM**: `pip install litellm`; refactor `inference_router.py` to use LiteLLM as the unified routing layer
- [ ] **Implement fallback chain**: Local models only in the fallback chain; cloud is explicit opt-in with `allow_cloud=True`
- [ ] **Add sovereignty routing test**: `tests/test_inference_router.py` — mock cloud provider unavailability (network error + 503) and assert local fallback activates
- [ ] **Update QUICKSTART-FREE.md**: Document Qwen 3.5 27B as the recommended Ollama model; Gemma 3 12B as the lightweight alternative
- [ ] **Update CONTRIBUTING.md and README.md**: Add sovereignty statement: *"Cloud LLM calls are optional augmentation. GAIA must remain fully functional on local models alone."*

### Phase 2 — Dependency Audit (Sprint G-11)
- [ ] Audit all GAIA subsystems for hard cloud dependencies; document findings in `docs/security/sovereignty_audit.md`
- [ ] Replace any hard cloud dependencies with self-hostable equivalents from the registry above
- [ ] Add LangFuse self-hosted as the observability backend (replacing any cloud tracing dependency)
- [ ] Add SearXNG as the self-hosted web search backend for `gaia-mcp-web` (ADR-0010)

### Phase 3 — Resilience Testing (Sprint G-12)
- [ ] Add integration tests that simulate full cloud unavailability across all GAIA subsystems
- [ ] Document GAIA's "island mode" capability: what GAIA can do with zero internet access
- [ ] Establish a recurring sovereignty audit as part of GAIA's release checklist

---

## Threat Model Update

This ADR adds the following entry to `docs/security/threat_model.md`:

```markdown
## Threat: Cloud Provider Political Restriction

**Category:** Sovereignty / Infrastructure  
**Severity:** HIGH  
**Likelihood:** DEMONSTRATED (Anthropic, June 2026)  
**Impact:** Complete loss of LLM capability if cloud is a hard dependency  

**Mitigation:**
1. Local-first model routing (ADR-0011) — Ollama + open-weight models
2. LiteLLM fallback chain — cloud failure is caught and resolved locally
3. Sovereignty routing test in CI — fallback is verified on every build
4. Self-hostable equivalents for all cloud dependencies (registry in ADR-0011)

**Residual risk:** Local hardware failure — mitigated by local backup and offline model cache
```

---

## Consequences

### Positive
- GAIA remains fully functional when Anthropic, OpenAI, or any cloud provider is unavailable — for any reason
- Sovereignty routing is a configuration change, not a code change — adapts in minutes to new political or commercial conditions
- Local model quality (Qwen 3.5, Gemma 3, DeepSeek-R1) is sufficient for the vast majority of GAIA's workload
- Sovereignty test in CI means regression cannot be introduced silently
- GAIA's local-first principle is enforced structurally, not just stated in documentation

### Tradeoffs
- Local models have a lower accuracy ceiling than frontier cloud models on some tasks — accepted; cloud augmentation remains available as opt-in for edge cases
- Ollama requires local hardware with adequate VRAM (8–16GB for primary tiers) — documented in QUICKSTART-FREE.md
- LiteLLM adds a dependency — it is MIT-licensed, self-contained, and widely used; acceptable

### Not Changed by This ADR
- LangGraph orchestration (ADR-0009) — unchanged; runs entirely locally
- MCP tool interface (ADR-0010) — unchanged; tools are already local-first
- GAIA's Law Stack and canon architecture — unchanged; this ADR operates at the infrastructure layer

---

## Compliance

| GAIAN LAW | How This ADR Satisfies It |
|---|---|
| LAW 4 — Sovereignty | GAIA's core capability cannot be revoked by any external party; local-first by architecture |
| LAW 1 — Consent | User's choice to allow cloud augmentation is explicit (`allow_cloud=True`); default is local |
| LAW 3 — Transparency | Model routing decisions are logged; user can inspect which model handled each request |
| LAW 2 — Non-Maleficence | Local models reduce data exfiltration risk; no user data sent to cloud by default |

---

## References

- [LiteLLM GitHub](https://github.com/BerriAI/litellm) — MIT license
- [Ollama](https://ollama.com) — local model runtime
- [Qwen 3.5 model family](https://qwen.readthedocs.io/)
- [Gemma 3 model family](https://ai.google.dev/gemma)
- [DeepSeek-R1](https://github.com/deepseek-ai/DeepSeek-R1)
- [LLM_SERVICES_INFRA_SNAPSHOT_2026.md](../research/external/LLM_SERVICES_INFRA_SNAPSHOT_2026.md)
- [GAIA_EXTERNAL_BENCHMARK_2026.md](../GAIA_EXTERNAL_BENCHMARK_2026.md)
- [ADR-0009](./ADR-0009-langgraph-canonical-orchestrator.md) — LangGraph orchestration
- [ADR-0010](./ADR-0010-mcp-canonical-tool-interface.md) — MCP tool interface
- [#694](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/694) — Tech Intelligence Brief
- [#697](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/697) — External Benchmark Sprint

---

*ADR filed: 2026-06-29. Physics-first, sovereignty-first, magic-free. 🌿*

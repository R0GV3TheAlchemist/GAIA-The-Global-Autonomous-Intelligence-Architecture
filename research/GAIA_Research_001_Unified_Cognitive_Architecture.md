# GAIA Research 001 — Unified Cognitive Architecture

**Source:** External deep research (ChatGPT-assisted, aligned with GAIA-OS canon)  
**Filed:** 2026-06-30  
**Canon Cross-references:** C155 (Living Architecture Loop, 8-agent stack, skill library), C156 (knowledge graph, memory taxonomy), C157 (governance), C158 (safety, digital twin), C160 (benchmark harness, 26-metric system)  
**Status:** RESEARCH — not canon; informs G-14 Deployment & Embodiment phase

> *This document was produced as external research supporting GAIA-OS canon development. It represents a convergent, independent derivation of many architectural patterns already established in G-13 canon, approached from classical cognitive science and modern LLM-agent frameworks rather than from physics-first grounding. The convergence is significant.*

---

## Executive Summary

This report outlines a **Unified Cognitive Architecture** for GAIA — a hybrid system integrating decades of AI research with modern LLM-based agents. Classical cognitive architectures (e.g. ACT-R, Soar, BDI, Blackboard, Global Workspace) provide rich symbolic reasoning, memory, and planning models. Contemporary frameworks (LangChain, Ray, MetaGPT/CAMEL/AutoGen, etc.) add modular tooling, scalable microservices, and powerful neural reasoning. We propose combining these strengths via a **hybrid design**: symbolic modules and knowledge graphs for structured reasoning, coupled with neural LLMs for flexible inference. Memory will be structured into *working*, *episodic*, *semantic*, and *procedural* stores, with consolidation and controlled forgetting inspired by neuroscience (sleep-like replay, synaptic pruning). Planning will use hierarchical task decomposition (akin to HTN and Soar) to break goals into subgoals. The agent will access a library of **skills/tools** as modular extensions. We will build a continuous evaluation framework with benchmarks and metrics for success rate, factual accuracy, plan quality, memory recall, latency, and safety. A self-improvement pipeline will automatically log failures, perform root-cause analysis, generate fixes, run regression tests, and deploy updates. Safety and governance are central: we will enforce domain constraints and provide audit trails using a "digital twin" model.

---

## Goals and Scope

The goal of GAIA Research 001 is to define a **Unified Cognitive Architecture** for GAIA. The scope includes:

1. **Literature survey** of classical cognitive systems and modern agent frameworks
2. **Hybrid design** combining symbolic reasoning, neural networks, probabilistic inference, and knowledge graphs
3. **Memory taxonomy** with episodic, semantic, procedural, working memory and consolidation/forgetting strategies
4. **Planning and task decomposition** using hierarchical models
5. **Skill/Tool Library** and agent orchestration patterns
6. **Evaluation framework** (metrics, benchmarks, regression tests)
7. **Self-improvement loop** (fail → analyze → fix → test)
8. **Safety & governance** integration
9. **Implementation** guidelines (APIs, data schemas, distributed patterns)
10. **Experiment design** and datasets
11. **Roadmap** (6–24 month milestones)

---

## Classical Cognitive Architectures vs. Modern LLM-Agent Frameworks

Classical architectures provide blueprints for intelligent behaviour:

- **ACT-R** — Hybrid symbolic–subsymbolic model using production rules with parallel, utility-driven learning
- **Soar** — Symbolic production-system based on Problem-Space Hypothesis; hierarchical task decomposition via "impasse" mechanism
- **HTN planners** — Hierarchical Task Networks decomposing high-level tasks into subtasks
- **BDI** agents — Beliefs, Desires, Intentions; separate plan selection from plan execution
- **Blackboard** — Central shared memory where specialised modules post and read partial solutions
- **Global Workspace Theory (GWT)** — Many parallel modules communicating via a central "workspace"; attention mechanism selects broadcast content

Modern LLM-agent frameworks leverage large language models and modular tooling: LangChain, Ray Serve + MCP, MetaGPT, CAMEL, AutoGen.

| Architecture | Approach | Reasoning & Memory | Planning | Strengths | Limitations |
|---|---|---|---|---|---|
| **ACT-R** | Hybrid symbolic+subsymbolic | Declarative memory + buffers | Implicit (productions) | Well-studied cognitive model | Not multi-agent scale |
| **Soar** | Symbolic production system | Working + long-term memory | Subgoals via impasse | General problem solving | No probabilistic reasoning |
| **HTN Planning** | Task-level decomposition | No built-in memory | Explicit task decompositions | Efficient for structured tasks | Domain-specific |
| **BDI** | Mental-state model | Belief base | Plans from library | Natural agent modelling | Planning external; no learning |
| **Blackboard** | Shared knowledge repository | Knowledge sources | Opportunistic | Flexible expert integration | Coordination overhead |
| **GWT** | Central workspace broadcast | Working memory bottleneck | Attention selects content | Integrates parallel modules | Largely theoretical |
| **LangChain** | Modular LLM pipelines | RAG context, external DB | LLM chain-of-thought | Rapid prototyping | Not research-proven |
| **Ray Serve + MCP** | Microservices | External databases, caches | Dynamic tool discovery | Scalable; fault tolerant | Engineering complexity |
| **MetaGPT/AutoGen** | LLM multi-agent coordination | LLM-internal memory | Workflow/chat orchestration | Customisable | Early-stage |

---

## Hybrid Neuro-Symbolic and Knowledge-Graph Integration

GAIA will use **neuro-symbolic** techniques to prevent hallucinations and handle real-world complexity:

- Augment LLMs with structured knowledge bases, logic modules, and differentiable reasoning
- Knowledge graph layer (storing facts) queried by reasoning engines or LLMs
- Retrieval-augmented generation (RAG): inject retrieved knowledge into LLM prompts
- Open KG stores: Neo4j, RDF stores
- **Canon alignment:** This architecture is implemented in C156's dual-layer knowledge graph (vector + graph), C155's 8-agent stack, and BIOPHOTON_09's signal taxonomy

---

## Memory Taxonomy and Consolidation

| Memory Type | Description | Example | Consolidation / Pruning |
|---|---|---|---|
| **Working** | Short-term, active context buffer | Prompt context, LLM hidden state | Sliding window; discard after use |
| **Episodic** | Personal events tied to time/space | Conversation logs, episodic buffer | Periodic replay; priority tagging by importance |
| **Semantic** | Generalised facts and knowledge | Knowledge graph, vector DB | Periodic abstraction; knowledge aging |
| **Procedural** | Skills and action rules acquired by feedback | Trained models, scripted agent skills | Refined through feedback; outdated skills pruned |

Memory consolidation is inspired by sleep cycles: important information is strengthened, low-value items are gradually forgotten (synaptic pruning). The SCM (Sleep-Consolidated Memory) system shows interleaved replay achieves high retention with low noise.

**Canon alignment:** C156 §3 knowledge graph schema; C160 Metrics 6–10; C155's forgetting appropriateness (Metric 8).

---

## Planning and Hierarchical Task Decomposition

- High-level objectives decomposed into subgoals and primitive actions (HTN / Soar-style)
- Soar's impasse mechanism: if no valid operator found, subtask spawned
- LLM reasoning for dynamic decision-making: chain-of-thought, tree-of-thought
- Monte Carlo Tree Search hybridisation: symbolic search + LLM-evaluated heuristics
- Planner module: generate → assess via simulation/logic → refine iteratively

---

## Skill/Agent Library and Orchestration

- Library of modular capabilities (skills/tools) invocable on demand
- Skills packaged with instructions, metadata, and executable code
- Orchestration patterns: blackboard/message-bus, pipeline
- Service registry for skill discovery — adding a new skill automatically available to all relevant agents
- **Canon alignment:** C155 §5 Agent Skill Library; C155's 8-agent stack

---

## Continuous Evaluation and Benchmarks

| Evaluation Category | Example Metrics | Description |
|---|---|---|
| **Task Completion** | Success Rate, Pass@k | Fraction of tasks correctly solved |
| **Language Quality** | F1, BLEU, ROUGE | Correctness and fluency |
| **Tool Use** | Invocation Accuracy, Node F1 | Correct tool choice and invocation |
| **Planning** | Step Success Rate | % of planned steps executed correctly |
| **Memory Recall** | Recall Accuracy, Consistency | Correctness of retrieved info; internal consistency |
| **Latency/Cost** | Response Time, CPU/GPU Utilisation | System performance under load |
| **Safety/Trust** | Toxicity %, Bias Metrics | Rate of undesirable outputs |

**Canon alignment:** C160's 26-metric benchmark harness and 4-tier execution architecture.

---

## Self-Improvement Pipeline

Closed-loop development cycle:

```
Detect Failure → Analyze Root Cause → Generate Fix → Test → Deploy
```

- Failures sourced from benchmark tests or real-world logs
- LLM-based root cause analysis of error patterns
- Fixes: update LLM prompt, adjust rule, retrain component
- All fixes run evaluation harness automatically
- Human oversight governs approvals

**Canon alignment:** C155 Living Architecture Loop; C160 Improvement Gate and Regression Response Protocol.

---

## Safety, Governance, and Consent Integration

- Full context captured for each decision (replayable)
- Critical domain rules enforced architecturally, not just by monitoring
- Strict separation between agent *recommendation* and *execution*: all proposed actions checked by validator / digital twin before execution
- Every decision, alternative, and rationale logged in audit trail
- Fleet-wide policy management: single update propagates to all agents instantly

**Canon alignment:** C158 Five Gaian Laws; C158 Digital Twin; C139 consent ledger; C160 Alert Hierarchy.

---

## Implementation Patterns, Data Schemas, APIs, Scalability

**Microservice Architecture:**
- Ray Serve: LLM model as one service, each tool as separate service
- Agent orchestration (LangChain controller) as its own service
- Independent scaling: allocate more GPUs to LLM without touching tool servers
- Inter-service communication: HTTP, gRPC, or Ray A2A protocol

**Data Schemas:**
- Long-term memory: vector DB or SQL/graph store; entries with timestamp, content, embedding, importance score
- Knowledge Graph: RDF/OWL or property graph (entities, relationships, rules)
- LLM API: GPT-like REST API or custom endpoint
- Tool API: each skill exposes function signature (OpenAI function-calling or MCP)
- Message formats: JSON or protobuf with versioning

**Scalability:**
- Distributed agents across cluster nodes (Docker/Kubernetes)
- Model distillation for routine tasks; large models reserved for complex reasoning
- Agents sharded by function; coordinate via message bus

---

## Proposed Experiments, Datasets, Success Criteria

- **Knowledge & Reasoning:** QA and reasoning benchmarks; factual recall accuracy
- **Memory Retention:** Extended dialogue with references to prior context
- **Planning Tasks:** Multi-step resource management simulations (ALFWorld, BabyAI)
- **Tool Use:** ToolBench, MultiArXIV
- **Multi-Agent Scenarios:** Cooperative/competitive tasks; game-theoretic benchmarks
- **Safety/Alignment:** Toxicity suites + domain-specific policy compliance

Success criteria: >90% task success, <5% hallucination rate, 100% compliance.

---

## Roadmap (6–24 Months)

| Phase | Timeline | Key Deliverables |
|---|---|---|
| **Design** | 0–6 months | Finalise architecture; select technologies; initial memory + planning modules |
| **Prototype** | 6–12 months | LLM + tools integration; memory buffers; basic evaluation harness |
| **Integration** | 12–18 months | More skills; multi-agent protocols; distributed deployment; extensive benchmarks |
| **Validation** | 18–24 months | Optimise performance; governance modules; end-to-end use cases; open-source release |

---

*Filed: 2026-06-30. Status: RESEARCH. Informs G-14 Deployment & Embodiment phase.*

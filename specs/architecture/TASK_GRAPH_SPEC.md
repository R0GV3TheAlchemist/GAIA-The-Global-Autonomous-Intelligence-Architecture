# TASK_GRAPH_SPEC.md

Canonical specification for `core/task_graph.py` — GAIA Execution DAG.

**Sprint:** G-7  |  **Issue:** #170  |  **Canon:** C32, C30, C01

---

## Overview

`TaskGraph` replaces the imperative orchestration currently embedded inside
`alchemical_pipeline.py` and `async_alchemical_engine.py` with an explicit,
declarative DAG. Every engine invocation becomes a named `EngineNode` with
clear inputs, outputs, dependency edges, and a per-node timeout.

---

## Architecture

```
Intent
  │
  ▼
PlanNode  (intent_type, gaian_id, raw_input, canon_refs)
  │
  ▼
PlanFactory.build(plan)
  │
  ▼
TaskGraph  (nx.DiGraph of EngineNodes)
  │
  ├── cycle detection at __init__  (raises ValueError immediately)
  │
  ▼
TaskGraph.execute(trace=t)
  │
  ├── for each topological generation:
  │       asyncio.gather(*[_run_node(n) for n in generation])
  │
  ▼
context dict  (shared outputs of all nodes)
```

---

## Symbols

| Symbol | Kind | Description |
|---|---|---|
| `NodeStatus` | `str, Enum` | `PENDING / RUNNING / COMPLETE / FAILED / SKIPPED` |
| `EngineNode` | dataclass | Unit of work: `engine_id`, `inputs`, `outputs`, `depends_on`, `timeout_ms`, `canon_refs`, `handler`, `status`, `error` |
| `PlanNode` | dataclass | Decoded intent: `intent_type`, `gaian_id`, `raw_input`, `canon_refs` |
| `TaskGraph` | class | DAG container + `execute()`, `_run_node()`, `failed_nodes()`, `skipped_nodes()`, `execution_order()`, `summary()` |
| `PlanFactory` | class | `@register` decorator + `build()` + `registered_intents()` |
| `AgentAllocator` | class | G-7 stub: single-agent local; G-8+ interface for distributed dispatch |
| `ExecutionRunner` | class | Top-level entry: `PlanNode → TaskGraph → execute()` |

---

## EngineNode Fields

| Field | Type | Description |
|---|---|---|
| `engine_id` | `str` | Unique ID within this graph |
| `inputs` | `List[str]` | Context keys read before execution |
| `outputs` | `List[str]` | Context keys written after execution |
| `depends_on` | `List[str]` | `engine_id`s that must COMPLETE first |
| `timeout_ms` | `int` | Per-node hard timeout (default 5 000 ms) |
| `canon_refs` | `List[str]` | Forwarded to trace events |
| `handler` | `async callable \| None` | The actual async work unit |
| `status` | `NodeStatus` | Runtime state (set by `TaskGraph`) |
| `error` | `Exception \| None` | Populated on FAILED |

---

## Built-in Plan Templates

### `synergy_compute` (C32)

```
schumann  ┬
          ├──> synergy
emotional ┘
```

Parallel: `schumann` + `emotional` both read `gaian_state` independently.
Then `synergy` depends on both, reading `schumann_score` + `emotional_score`.

### `memory_recall` (C01)

```
embed ──> search ──> rerank
```

Linear pipeline. `embed` produces `query_embedding`, `search` produces
`recall_candidates`, `rerank` produces `recalled_memories`.

### `stage_session` (C32)

```
affect ┬
       ├──> ceremony ──> arc_update
codex  ┘
```

Parallel: `affect` + `codex`. Then `ceremony` depends on both.
Then `arc_update` depends on `ceremony`.

---

## GAIATrace Integration

Pass a live `GAIATrace` / `AsyncGAIATrace` to `ExecutionRunner.run(trace=t)`
or directly to `TaskGraph.execute(trace=t)`.

Events emitted per `EngineNode`:

| Event | When | Payload |
|---|---|---|
| `TASK_START` | Before handler call | `engine_id`, `inputs` snapshot |
| `TASK_END` | After successful handler | `engine_id`, `outputs`, `latency_ms`, `status` |
| `ERROR` | On timeout or exception | `engine_id`, `error_type`, `detail` |

Timeout (`asyncio.TimeoutError`) sets node to FAILED but **does not propagate**
— other nodes in the same generation continue. Callers check `failed_nodes()`
afterwards (C30).

All trace operations are wrapped in `try/except` — a broken trace writer
never silences an `EngineNode` result.

---

## Concurrency Model

```
Generation 0: [schumann, emotional]  ── asyncio.gather ──>
                                          (both complete)
Generation 1: [synergy]              ── asyncio.gather ──>
```

Nodes in the same generation are independent and run concurrently.
The shared `_context` dict is only written by one generation at a time
(no cross-generation data races in G-7 single-event-loop mode).

---

## G-7 vs G-8 Comparison

| Capability | G-7 (this PR) | G-8+ (future) |
|---|---|---|
| Execution | `asyncio.gather` on local event loop | Distributed agents via gRPC / message queue |
| `AgentAllocator` | Stub, returns `None` for all nodes | Returns `AgentHandle` per node |
| `EngineNode.handler` | Local async coroutine | Remote RPC call |
| State sharing | In-process `_context` dict | Distributed state store |

---

## Test Coverage Checklist

- [ ] `test_topological_order` — execution_order() returns correct generations
- [ ] `test_concurrent_execution` — two independent nodes run in parallel (timing)
- [ ] `test_cycle_detection` — circular `depends_on` raises `ValueError` at init
- [ ] `test_timeout_handling` — slow node is FAILED, other nodes complete
- [ ] `test_failed_node_reporting` — `failed_nodes()` returns correct nodes
- [ ] `test_skipped_node` — node with `handler=None` is SKIPPED
- [ ] `test_context_propagation` — outputs of node A appear as inputs to node B
- [ ] `test_plan_factory_build` — known intent builds correct graph
- [ ] `test_plan_factory_unknown` — unknown intent raises `ValueError`
- [ ] `test_trace_task_start_end` — TASK_START + TASK_END emitted per node
- [ ] `test_trace_error_event` — ERROR event emitted on exception, exception re-raised
- [ ] `test_trace_timeout_error` — ERROR event emitted on timeout, node FAILED
- [ ] `test_broken_trace_writer` — broken trace never crashes EngineNode
- [ ] `test_execution_runner_run` — end-to-end smoke test through ExecutionRunner

---

## Related

- **#171** `GAIATrace` — trace context consumed here
- **#169** `canon_graph.py` — canon ref validation for node `canon_refs`
- **#172** `GAIAStateAdapter` — produces `gaian_state` seed context
- **#173** `MemoryHierarchy` — handlers for `memory_recall` nodes
- `alchemical_pipeline.py` — will migrate its orchestration logic here
- `async_alchemical_engine.py` — will migrate its orchestration logic here

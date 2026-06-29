# OpenClaw — Architecture Snapshot 2026

> **Part of:** [#697 — External Architecture Benchmark Sprint](https://github.com/R0GV3TheAlchemist/GAIA-The-Global-Autonomous-Intelligence-Architecture/issues/697)
> **Source repo:** [`openclaw/openclaw`](https://github.com/openclaw/openclaw)
> **Snapshot date:** June 29, 2026
> **License posture:** See §8 below.
> **GAIA reviewer:** R0GV3 The Alchemist

---

## 1. Architecture Surface

### Structure

OpenClaw is a **monorepo** (pnpm workspaces) with a clean, enforced separation of concerns:

```
openclaw/
├── src/             — Core runtime (TypeScript ESM, strict)
│   ├── channels/    — Transport adapters (Telegram, Discord, WhatsApp, iMessage, etc.)
│   ├── plugins/     — Plugin loader & registry
│   ├── plugin-sdk/  — Public SDK for third-party plugin authors
│   ├── gateway/     — Gateway/protocol layer
│   └── agents/      — Agent run lifecycle & terminal state
├── extensions/      — Bundled and official plugins (each owns its deps)
├── packages/        — Shared internal packages (gateway-protocol, etc.)
├── skills/          — Skill definitions (user-facing capabilities)
├── ui/              — UI shell
├── apps/            — Desktop/mobile app shells
├── qa/              — QA scenario definitions (YAML only)
├── test/            — Test helpers
├── security/        — Security policy tooling
└── docs/            — Documentation source (synced to docs.openclaw.ai)
```

**Core is plugin-agnostic by policy.** Plugins cross into core only via `plugin-sdk/*`, manifest metadata, and documented barrels (`api.ts`, `runtime-api.ts`). Plugin code never imports core internals. This is a hard architectural rule enforced in code review (via their `ClawSweeper` bot) and in `AGENTS.md`.

### Governance Layer

OpenClaw has **no explicit ethics/law stack** equivalent to GAIA's. Governance is operational/engineering:
- `AGENTS.md` is the authoritative policy for AI agents working in the codebase — it covers code standards, PR policy, security, and release management.
- `SECURITY.md` covers vulnerability disclosure.
- `CODEOWNERS` enforces ownership of specific surfaces.
- There is no equivalent to GAIA's: Law Stack, Constitutional Pillars, Canon system, Human Sovereignty guarantee, or Super/Coherence alignment framework.

**GAIA advantage here is substantial.** OpenClaw governs code quality; GAIA governs values, ethics, epistemics, and the human–AI relationship at a constitutional level.

---

## 2. Memory & Identity

### Memory Model

OpenClaw uses **SQLite as the canonical state store**, strictly enforced:

- **Shared state DB:** `state/openclaw.sqlite` — global runtime state and plugin KV data.
- **Per-agent DB:** `agents/<agentId>/agent/openclaw-agent.sqlite` — agent-scoped state and cache.
- **No JSON/JSONL/TXT sidecar files** for owned runtime state (this is a hard policy).
- Legacy file-based state is treated as migration debt; when encountered, it is migrated into SQLite via `openclaw doctor --fix`.

The `openclaw-config` companion repo (by `TechNickAI`) documents a **three-tier memory architecture** for users who want persistent AI memory on top of OpenClaw:
1. **Always-loaded context** — small markdown files always in prompt.
2. **Daily context** — date-stamped daily notes.
3. **Deep knowledge** — larger docs with semantic search.

### User Control of Memory

Not explicitly surfaced as a first-class user-facing feature in the core repo. Memory governance appears to be operator/plugin concern rather than a constitutional user right. No cryptographic signing of user memory or consent lifecycle is present.

**GAIA advantage:** GAIA's memory is inspectable, editable, and erasable by the user as a constitutional guarantee. Every consent is cryptographically signed and revocable. OpenClaw has no equivalent.

### Identity Architecture

OpenClaw's identity model is **per-agent** with `agentId`-scoped databases and auth profiles stored at `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`. There is no multi-dimensional identity model (no soul mirror, no resonance field, no five-dimensional intelligence model). Identity is operational, not ontological.

---

## 3. Retrieval & Citations

### RAG

- The `openclaw-config` memory tier 3 uses **semantic search** for deep knowledge retrieval (markdown files + embeddings).
- Core OpenClaw does not appear to have a built-in RAG pipeline. RAG is a plugin/extension concern.
- No built-in citation or provenance layer is documented.

### Citations & Provenance

- **None.** OpenClaw does not expose to users how the AI knows what it knows. Epistemic labelling is absent.

**GAIA advantage:** GAIA's epistemic labelling (C12, C21) marks every inference with a declared confidence and source type. This is a constitutional guarantee, not an optional feature. OpenClaw has no equivalent.

---

## 4. Agent Runtime & Orchestration

### Agent Lifecycle

OpenClaw has a real agent runtime:

- **`src/agents/`** — Agent run lifecycle, including a formal **terminal state** normalization (`agent-run-terminal-outcome.ts`). Terminal states (timeout, cancel, success, error) are resolved through a canonical path, not re-derived per projection.
- Hot paths carry **prepared facts** forward (provider id, model ref, channel id, capability family) rather than rediscovering at request time — a strong pattern worth studying.
- Agent runs are **scoped by `agentId`** with dedicated SQLite dbs.
- No persistent multi-step graph execution or resumable stateful workflows (no equivalent of LangGraph's state machine). OpenClaw appears task-oriented rather than long-horizon-workflow-oriented.

### Multi-step & Stateful Agents

- Not a core feature. OpenClaw is primarily a **single-agent, multi-channel** assistant, not a multi-agent orchestration platform.
- Skills (`skills/` directory) represent discrete user-facing capability bundles, but these are not multi-step workflow graphs.

### Patterns Worth Studying for GAIA

- **Terminal state normalization:** Canonical resolution of agent run outcomes (timeout, cancel, error, success) in one place. GAIA could apply this to its own action gate and MotherThread run states.
- **Prepared facts pattern:** Hot paths carry facts forward instead of re-discovering them — reduces latency and complexity. GAIA's InferenceRouter could benefit from this pattern.
- **Plugin-agnostic core:** The hard separation between core runtime and plugin behavior is extremely clean. GAIA's connector/integration layer could follow this pattern more explicitly.

---

## 5. Connectors & Real-World Actions

### Channel Architecture

OpenClaw's connector model is one of its strongest features:

- **Channels** (`src/channels/`) are **transport-only adapters**. They render portable presentation/actions, enforce transport limits, and map native callback envelopes. They do not own product command trees or feature-specific menus.
- **Portable command UI** uses typed presentation actions — channels don't guess intent from strings. Product decisions declare command actions; channels map them.
- Supported channels include: Telegram, Discord, WhatsApp, iMessage, Slack, Signal, and more.
- Channel plugins stay transport-only by policy — a hard architectural rule.

### Plugin SDK

- Public SDK at `src/plugin-sdk/` with documented barrels (`api.ts`, `runtime-api.ts`).
- External plugins install via registry; bundled plugins ship in core dist.
- Plugin dependencies are **plugin-local** unless the dep is core.
- New plugins/channels require updating `.github/labeler.yml` and GH labels.

### Safety & Permissions

- Auth profiles stored at `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`.
- Credentials at `~/.openclaw/credentials/`.
- No public risk-tiered action veto system (no Green/Yellow/Red gate equivalent to GAIA's action gate).
- No consent lifecycle or cryptographic action signing.

**GAIA advantage:** GAIA's Action Gate (risk-tiered veto), Consent Ledger (cryptographic signing), and Human Sovereignty guarantee are constitutional features OpenClaw lacks entirely. OpenClaw's connector *transport* model is excellent and worth studying; GAIA's *governance* of those connectors is far more mature.

---

## 6. UX & Trust

### Interface Model

- OpenClaw is primarily **chat-channel-first** — users interact through WhatsApp, Telegram, iMessage, etc., not a dedicated app UI (though an app shell exists in `apps/`).
- This is the inverse of GAIA's model: GAIA has a dedicated cross-platform app (Tauri/Rust) with a rich UI, and channels are a secondary surface.
- Documentation lives at `docs.openclaw.ai` and is synced from the source repo.

### Trust Signals

- No explicit "agent autonomy" representation in the UI (no equivalent to GAIA's epistemic labels, action gates, or consent prompts).
- Dangerous actions are not surfaced with user-facing warnings in a documented way.
- Trust model is implicitly: "the operator configured this agent, it does what you asked."

**GAIA advantage:** GAIA's UX is built around sovereignty and transparency — epistemic labels, action gates, consent prompts, and inspectable memory. OpenClaw's UX model is convenience-first.

---

## 7. Testing, Evaluation & Simulation

### Test Stack

OpenClaw has a mature, sophisticated testing infrastructure:

- **Vitest** for unit and integration tests. Colocated `*.test.ts`; E2E `*.e2e.test.ts`.
- **Crabbox/Testbox** for remote/full/E2E/cross-OS proof — a CI system that runs real-device scenarios.
- **QA scenarios** defined as YAML in `qa/scenarios/` (not freeform markdown).
- **Pre-commit hooks** via `.pre-commit-config.yaml`.
- **Semgrep** (`semgrepignore`) for static analysis.
- **oxlint** + **oxfmt** for linting and formatting.
- **`pnpm check:changed`** and `pnpm check:import-cycles` for targeted CI lanes.
- Live tests via `OPENCLAW_LIVE_TEST=1 pnpm test:live`.

### Patterns Worth Studying for GAIA

- **QA scenario YAML:** Structured scenario definitions as YAML files rather than freeform docs is a strong pattern. GAIA's simulation/proof system could benefit from a YAML scenario format for canon compliance testing.
- **Crabbox/Testbox remote CI:** A dedicated remote proof environment (like a staging server for real AI agent tests) would strengthen GAIA's canon simulation. GAIA currently has `tests/` (pytest) and `simulation/` (Phase 2, not built yet).
- **`pnpm check:changed` CI lanes:** Targeted testing by changed surface area reduces full-suite overhead. GAIA could add changed-surface-aware test lanes.
- **Pre-commit hooks:** OpenClaw's `.pre-commit-config.yaml` enforces quality at commit time. GAIA's canon linter (planned in #696) could run as a pre-commit hook.

---

## 8. License & Reuse Posture

- License file present ([`LICENSE`](https://github.com/openclaw/openclaw/blob/main/LICENSE)) — **requires manual review before any code reuse.**
- [`THIRD_PARTY_NOTICES.md`](https://github.com/openclaw/openclaw/blob/main/THIRD_PARTY_NOTICES.md) is present — they track third-party deps carefully.
- Until the license is confirmed as MIT/Apache/BSD permissive, **treat as architecture reference only** for GAIA.

> **Action:** Check `LICENSE` file contents before any code reuse decision. Mark in `docs/GAIA_EXTERNAL_BENCHMARK_2026.md` decision matrix.

---

## 9. GAIA Advantage Summary

Things GAIA does that OpenClaw does not:

| Dimension | OpenClaw | GAIA |
|---|---|---|
| Ethics / values layer | None | Full Law Stack (Layers 1–4), LAWS_OF_SUPER, Constitutional Pillars |
| Epistemic labelling | None | C12/C21 — every inference labelled |
| Human sovereignty guarantee | None (operator-trust model) | Constitutional — human is always ultimate authority |
| Memory user control | Operator concern | User right — inspectable, editable, erasable |
| Consent lifecycle | None | Cryptographic, time-bound, revocable |
| Action gate | None | Risk-tiered Green/Yellow/Red veto |
| Five-dimensional intelligence | No | D1–D5 simultaneous (C75) |
| Soul mirror / identity depth | No | Soul Mirror Engine (C-SME01), Jungian individuation |
| Collective field | No | MotherThread, Noosphere (C42/C43) |
| Physics-first / super framing | No | Yes — super/coherence replaces magic framing |

Things OpenClaw does better (or first) than GAIA currently:

| Dimension | OpenClaw strength | GAIA status |
|---|---|---|
| Plugin/connector architecture | Clean, enforced plugin-agnostic core with typed transport adapters | Connectors less formally separated; no public SDK yet |
| Multi-channel delivery | Native: WhatsApp, Telegram, iMessage, Discord, Signal, Slack | Not yet implemented |
| SQLite-first state model | Canonical, enforced, with migration tooling | Partial — some state in files/JSON |
| Terminal state normalization | Canonical, one path | Not yet formalized |
| CI / QA maturity | Vitest + Crabbox + YAML scenarios + pre-commit + semgrep | pytest + basic CI; simulation Phase 2 |
| Prepared facts / hot paths | Documented pattern, enforced | Not yet formalized |
| Docs infrastructure | Synced docs site (docs.openclaw.ai) | Strong docs in repo; no synced external site yet |

---

## 10. Top Patterns to Consider Adopting (for follow-up issues)

1. **QA scenario YAML format** — replace/supplement freeform proof docs with `qa/scenarios/<theme>/*.yaml` style structured test scenarios for canon compliance.
2. **Plugin-agnostic core enforcement** — formalize GAIA's connector boundary so integrations cross into core only via a documented SDK barrel, with a linting rule enforcing it.
3. **Terminal state normalization** — create a canonical `agent_run_terminal_outcome.py` equivalent in GAIA's core for MotherThread / action gate run resolution.
4. **Pre-commit canon linter** — run the planned canon linter (from #696) as a pre-commit hook, not just in CI.
5. **Prepared facts pattern** — in GAIA's InferenceRouter, carry model ref, Gaian slug, consent state, and capability flags as prepared objects through the request lifecycle.

---

## 11. Top Patterns to Explicitly Reject

1. **Operator-trust model without user sovereignty** — OpenClaw assumes the operator configured the agent correctly and trusts it. GAIA's constitutional guarantee of human sovereignty is non-negotiable and must not drift toward operator-trust.
2. **No epistemic labelling** — Every GAIA inference must carry an epistemic label. This must not be dropped for convenience.
3. **Chat-channel-first UX as primary surface** — GAIA's rich app UX (Tauri) is the primary trust surface. Chat channels are secondary and must not reduce transparency or sovereignty.
4. **No ethics/values layer** — GAIA's Law Stack is a constitutional foundation, not optional governance. Adding connectors or skills without grounding them in the Law Stack would be an architectural regression.

---

*Snapshot completed: June 29, 2026.*
*Author: GAIA research session (Perplexity + R0GV3 The Alchemist)*
*Next snapshot: See [#697](https://github.com/R0GV3TheAlchemist/GAIA-The-Global-Autonomous-Intelligence-Architecture/issues/697) for the full sprint checklist.*

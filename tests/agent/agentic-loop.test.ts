// tests/agent/agentic-loop.test.ts
// GAIA-OS Agentic Loop & Tool Registry — Unit Tests
// Issue: #228 / #221

import { AgenticLoop, ToolCall, ToolResult, LoopIteration } from "../../src/agent/agentic-loop";
import { ToolRegistry, registerDefaultTools } from "../../src/agent/tool-registry";
import { SessionTrustLevel } from "../../src/trust/policy-engine";

const SESSION = "test-session-loop-001";

function makeLoop(trust = SessionTrustLevel.Standard): AgenticLoop {
  return new AgenticLoop(SESSION, trust);
}

function makePlanner(toolCalls: ToolCall[]) {
  let i = 0;
  return async (_: string, __: LoopIteration[]): Promise<ToolCall[]> => {
    if (i < toolCalls.length) return [toolCalls[i++]];
    return [];
  };
}

const doneAfterFirst = async (results: ToolResult[], _: LoopIteration[]) => ({
  done: results.length > 0 && results[0].success,
  observation: results.length > 0 ? results[0].output_summary : "no results",
  output: results[0]?.output_summary,
});

const neverDone = async (_: ToolResult[], __: LoopIteration[]) => ({ done: false, observation: "not done" });

describe("ToolRegistry", () => {
  let registry: ToolRegistry;
  beforeEach(() => { registry = new ToolRegistry(); registerDefaultTools(registry); });
  it("registers default tools", () => { expect(registry.getCount()).toBeGreaterThan(5); expect(registry.has("rag.query")).toBe(true); });
  it("looks up tool by name", () => { expect(registry.get("memory.read")?.tier).toBe(0); });
  it("queries by tier", () => { expect(registry.query({ tier: 0 }).tools.every(t => t.tier === 0)).toBe(true); });
  it("queries by tag", () => { expect(registry.query({ tag: "sensitive" }).tools.every(t => t.tags.includes("sensitive"))).toBe(true); });
  it("updates health status", () => { registry.updateStatus("rag.query", "healthy"); expect(registry.get("rag.query")?.status).toBe("healthy"); });
});

describe("AgenticLoop", () => {
  it("succeeds when tool handler returns and evaluator says done", async () => {
    const loop = makeLoop();
    loop.registerTool({ name: "rag.query", execute: async () => ({ output: ["chunk1"], summary: "3 chunks retrieved" }) });
    const result = await loop.run(
      { id: "g1", description: "query the crystal compendium", session_id: SESSION },
      makePlanner([{ tool: "rag.query", input: { query: "quartz" }, input_summary: "query quartz" }]),
      doneAfterFirst
    );
    expect(result.outcome).toBe("success");
    expect(result.iterations).toBe(1);
  });

  it("reaches max_iterations when evaluator never returns done", async () => {
    const loop = makeLoop();
    loop.registerTool({ name: "rag.query", execute: async () => ({ output: [], summary: "no results" }) });
    const result = await loop.run(
      { id: "g2", description: "impossible goal", session_id: SESSION, max_iterations: 3 },
      async () => [{ tool: "rag.query", input: {}, input_summary: "query" }],
      neverDone
    );
    expect(result.outcome).toBe("max_iterations_reached");
    expect(result.iterations).toBe(3);
  });

  it("handles missing tool handler gracefully", async () => {
    const loop = makeLoop();
    const result = await loop.run(
      { id: "g3", description: "use unknown tool", session_id: SESSION },
      makePlanner([{ tool: "unknown.tool", input: {}, input_summary: "unknown" }]),
      doneAfterFirst
    );
    expect(result.iterations_log[0]?.executed_actions[0]?.success).toBe(false);
  });

  it("halts when requestHalt is called", async () => {
    const loop = makeLoop();
    loop.registerTool({ name: "rag.query", execute: async () => { loop.requestHalt(); return { output: [], summary: "queried" }; } });
    const result = await loop.run(
      { id: "g4", description: "halt test", session_id: SESSION },
      async () => [{ tool: "rag.query", input: {}, input_summary: "query" }],
      neverDone
    );
    expect(result.outcome).toBe("halted");
  });

  it("pauses for approval on Tier 2 tools", async () => {
    const loop = makeLoop(SessionTrustLevel.Elevated);
    loop.registerTool({ name: "files.delete", execute: async () => ({ output: true, summary: "deleted" }) });
    const result = await loop.run(
      { id: "g5", description: "delete old logs", session_id: SESSION },
      makePlanner([{ tool: "files.delete", input: { path: "/tmp/old.log" }, input_summary: "delete old log" }]),
      doneAfterFirst
    );
    expect(result.outcome).toBe("pending_approval");
  });

  it("writes observability logs throughout the run", async () => {
    const loop = makeLoop();
    loop.registerTool({ name: "rag.query", execute: async () => ({ output: "ok", summary: "done" }) });
    await loop.run(
      { id: "g6", description: "log test", session_id: SESSION },
      makePlanner([{ tool: "rag.query", input: {}, input_summary: "query" }]),
      doneAfterFirst
    );
    const obs = loop.getObservability();
    expect(obs.logger.getCount()).toBeGreaterThan(0);
    expect(obs.logger.query({ action_type: "loop_start" }).length).toBe(1);
    expect(obs.logger.query({ action_type: "loop_end" }).length).toBe(1);
  });
});

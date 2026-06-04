// tests/observability/logger.test.ts
// GAIA-OS Observability Layer — Unit Tests
// Issue: #231

import { Logger } from "../../src/observability/logger";
import { Tracer } from "../../src/observability/tracer";
import { TelemetryCollector } from "../../src/observability/telemetry";
import { AuditChain } from "../../src/observability/audit";
import { createObservabilityStack } from "../../src/observability/index";

const SESSION = "test-session-001";

describe("Logger", () => {
  let logger: Logger;
  beforeEach(() => { logger = new Logger({ session_id: SESSION }); });
  it("logs a tool call", () => { logger.toolCall("github.create_issue", "create issue", "created", 42); expect(logger.getCount()).toBe(1); expect(logger.getEntries()[0].tool).toBe("github.create_issue"); });
  it("logs a RAG query", () => { logger.ragQuery("what is quartz?", 5, 18); expect(logger.getEntries()[0].output_summary).toContain("5 chunks"); });
  it("logs a policy gate", () => { logger.policyGate("files.delete", "denied", 2); const e = logger.getEntries()[0]; expect(e.policy_decision).toBe("denied"); expect(e.trust_tier).toBe(2); });
  it("logs an error", () => { logger.error("rag.query", "vector store unavailable"); expect(logger.getEntries()[0].error).toBe("vector store unavailable"); });
  it("filters by action_type", () => { logger.toolCall("github.push_files", "push", "pushed", 10); logger.ragQuery("q", 3, 5); expect(logger.query({ action_type: "tool_call" }).length).toBe(1); });
  it("exports JSON", () => { logger.toolCall("t", "s", "o", 1); expect(() => JSON.parse(logger.exportJSON())).not.toThrow(); });
});

describe("Tracer", () => {
  let tracer: Tracer;
  beforeEach(() => { tracer = new Tracer(); });
  it("creates a trace", () => { const id = tracer.startTrace("build RAG", SESSION); expect(tracer.getTrace(id)?.goal).toBe("build RAG"); });
  it("starts and ends a span", () => { const tid = tracer.startTrace("goal", SESSION); const sid = tracer.startSpan(tid, "rag.query", "rag.query"); tracer.endSpan(tid, sid, "success"); expect(tracer.getTrace(tid)!.spans[0].outcome).toBe("success"); });
  it("ends a trace with outcome", () => { const id = tracer.startTrace("g", SESSION); expect(tracer.endTrace(id, "success")?.outcome).toBe("success"); });
  it("counts iterations", () => { const id = tracer.startTrace("multi", SESSION); tracer.startSpan(id,"s1",null); tracer.startSpan(id,"s2",null); expect(tracer.getTrace(id)?.iterations).toBe(2); });
});

describe("TelemetryCollector", () => {
  let tel: TelemetryCollector;
  beforeEach(() => { tel = new TelemetryCollector(); tel.initSession(SESSION); });
  it("tracks averages", () => { tel.recordToolCall("t",100,true,SESSION); tel.recordToolCall("t",200,true,SESSION); expect(tel.getToolMetrics("t")?.avg_duration_ms).toBe(150); });
  it("tracks error rate", () => { tel.recordToolCall("r",10,true,SESSION); tel.recordToolCall("r",10,false,SESSION); expect(tel.getErrorRate("r")).toBeCloseTo(0.5); });
  it("returns top tools", () => { tel.recordToolCall("a",1,true,SESSION); tel.recordToolCall("a",1,true,SESSION); tel.recordToolCall("b",1,true,SESSION); expect(tel.getTopTools(1)[0].tool).toBe("a"); });
});

describe("AuditChain", () => {
  let chain: AuditChain;
  const rec = (o={}) => ({ id: `r-${Date.now()}-${Math.random().toString(36).slice(2)}`, timestamp: new Date().toISOString(), session_id: SESSION, action_type: "tool_call", tool: "files.delete", decision: "approved" as const, trust_tier: 2, gaian_override: false, input_summary: "delete logs", metadata: {}, ...o });
  beforeEach(() => { chain = new AuditChain(); });
  it("assigns hashes", () => { expect(chain.append(rec()).entry_hash).toHaveLength(64); });
  it("chains hashes", () => { chain.append(rec()); const e2 = chain.append(rec()); expect(e2.previous_hash).toBe(chain.getAll()[0].entry_hash); });
  it("verifies clean chain", () => { chain.append(rec()); chain.append(rec()); expect(chain.verify().valid).toBe(true); });
  it("detects tampering", () => { chain.append(rec()); chain.append(rec()); (chain.getAll() as any)[0].entry_hash = "tampered"; expect(chain.verify().valid).toBe(false); });
});

describe("createObservabilityStack", () => {
  it("creates a wired stack with session logged", () => {
    const s = createObservabilityStack("session-xyz");
    expect(s.logger).toBeDefined();
    expect(s.session_id).toBe("session-xyz");
    expect(s.logger.getCount()).toBeGreaterThan(0);
  });
});

// src/observability/logger.ts
// GAIA-OS Observability Layer — Structured Action Logger
// Canon ref: C01, SOVEREIGNTY.md
// Issue: #231

export type ActionType =
  | "tool_call" | "memory_read" | "memory_write" | "rag_query"
  | "loop_start" | "loop_end" | "loop_iteration" | "policy_gate"
  | "approval_requested" | "approval_resolved" | "error"
  | "session_start" | "session_end";

export interface LogEntry {
  id: string;
  timestamp: string;
  session_id: string;
  agent_id: string;
  trace_id: string | null;
  action_type: ActionType;
  tool: string | null;
  input_summary: string;
  output_summary: string;
  duration_ms: number;
  trust_tier: number | null;
  policy_decision: "approved" | "denied" | "auto" | "pending" | null;
  error: string | null;
  tags: string[];
}

export type LogLevel = "info" | "warn" | "error" | "debug";

export interface LoggerConfig {
  session_id: string;
  agent_id?: string;
  min_level?: LogLevel;
  console_output?: boolean;
}

const LEVEL_PRIORITY: Record<LogLevel, number> = { debug: 0, info: 1, warn: 2, error: 3 };

function generateId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export class Logger {
  private entries: LogEntry[] = [];
  private config: Required<LoggerConfig>;

  constructor(config: LoggerConfig) {
    this.config = { agent_id: "gaia-core", min_level: "info", console_output: false, ...config };
  }

  log(actionType: ActionType, payload: Partial<Omit<LogEntry, "id" | "timestamp" | "session_id" | "agent_id" | "action_type">>, level: LogLevel = "info"): LogEntry {
    const entry = this.makeEntry(actionType, payload);
    if (LEVEL_PRIORITY[level] >= LEVEL_PRIORITY[this.config.min_level]) {
      this.entries.push(entry);
      if (this.config.console_output) {
        const icon = level === "error" ? "🔴" : level === "warn" ? "🟡" : "🟢";
        console.log(`${icon} [GAIA:${actionType}] ${entry.input_summary} (${entry.duration_ms}ms)`);
      }
    }
    return entry;
  }

  toolCall(tool: string, inputSummary: string, outputSummary: string, durationMs: number, opts?: Partial<LogEntry>): LogEntry {
    return this.log("tool_call", { tool, input_summary: inputSummary, output_summary: outputSummary, duration_ms: durationMs, ...opts });
  }

  ragQuery(query: string, chunksReturned: number, durationMs: number, traceId?: string): LogEntry {
    return this.log("rag_query", { tool: "rag.query", input_summary: query, output_summary: `${chunksReturned} chunks retrieved`, duration_ms: durationMs, trace_id: traceId ?? null });
  }

  policyGate(tool: string, decision: LogEntry["policy_decision"], tier: number): LogEntry {
    return this.log("policy_gate", { tool, input_summary: `policy evaluation: ${tool}`, output_summary: `decision: ${decision}`, trust_tier: tier, policy_decision: decision, duration_ms: 0 });
  }

  error(tool: string | null, message: string, traceId?: string): LogEntry {
    return this.log("error", { tool, input_summary: message, output_summary: "", duration_ms: 0, error: message, trace_id: traceId ?? null }, "error");
  }

  sessionStart(): LogEntry { return this.log("session_start", { input_summary: `session ${this.config.session_id} started`, output_summary: "" }); }
  sessionEnd(durationMs: number): LogEntry { return this.log("session_end", { input_summary: `session ${this.config.session_id} ended`, output_summary: `duration: ${durationMs}ms`, duration_ms: durationMs }); }

  query(filters: { action_type?: ActionType; tool?: string; trace_id?: string; since?: string; limit?: number } = {}): LogEntry[] {
    let results = [...this.entries];
    if (filters.action_type) results = results.filter(e => e.action_type === filters.action_type);
    if (filters.tool) results = results.filter(e => e.tool === filters.tool);
    if (filters.trace_id) results = results.filter(e => e.trace_id === filters.trace_id);
    if (filters.since) results = results.filter(e => e.timestamp >= filters.since!);
    if (filters.limit) results = results.slice(-filters.limit);
    return results;
  }

  exportJSON(): string { return JSON.stringify(this.entries, null, 2); }
  clear(): void { this.entries = []; }
  getEntries(): LogEntry[] { return [...this.entries]; }
  getCount(): number { return this.entries.length; }

  private makeEntry(actionType: ActionType, payload: Partial<LogEntry>): LogEntry {
    return { id: generateId("log"), timestamp: new Date().toISOString(), session_id: this.config.session_id, agent_id: payload.agent_id ?? this.config.agent_id, trace_id: payload.trace_id ?? null, action_type: actionType, tool: payload.tool ?? null, input_summary: payload.input_summary ?? "", output_summary: payload.output_summary ?? "", duration_ms: payload.duration_ms ?? 0, trust_tier: payload.trust_tier ?? null, policy_decision: payload.policy_decision ?? null, error: payload.error ?? null, tags: payload.tags ?? [] };
  }
}

export default Logger;

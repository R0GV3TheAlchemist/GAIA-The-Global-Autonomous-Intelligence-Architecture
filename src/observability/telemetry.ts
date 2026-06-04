// src/observability/telemetry.ts
// GAIA-OS Observability Layer — Performance Metrics Aggregator
// Canon ref: C01
// Issue: #231

export interface ToolMetrics {
  tool: string;
  call_count: number;
  success_count: number;
  error_count: number;
  total_duration_ms: number;
  avg_duration_ms: number;
  min_duration_ms: number;
  max_duration_ms: number;
  last_called_at: string;
}

export interface SessionMetrics {
  session_id: string;
  started_at: string;
  total_actions: number;
  total_errors: number;
  total_rag_queries: number;
  total_policy_gates: number;
  total_duration_ms: number;
  tools_used: string[];
}

export class TelemetryCollector {
  private toolMetrics: Map<string, ToolMetrics> = new Map();
  private sessionMetrics: Map<string, SessionMetrics> = new Map();

  recordToolCall(tool: string, durationMs: number, success: boolean, sessionId: string): void {
    const existing = this.toolMetrics.get(tool) ?? { tool, call_count: 0, success_count: 0, error_count: 0, total_duration_ms: 0, avg_duration_ms: 0, min_duration_ms: Infinity, max_duration_ms: 0, last_called_at: "" };
    existing.call_count++;
    if (success) existing.success_count++; else existing.error_count++;
    existing.total_duration_ms += durationMs;
    existing.avg_duration_ms = existing.total_duration_ms / existing.call_count;
    existing.min_duration_ms = Math.min(existing.min_duration_ms, durationMs);
    existing.max_duration_ms = Math.max(existing.max_duration_ms, durationMs);
    existing.last_called_at = new Date().toISOString();
    this.toolMetrics.set(tool, existing);
    this.updateSession(sessionId, { tool, success });
  }

  recordRagQuery(sessionId: string): void { this.updateSession(sessionId, { rag: true }); }
  recordPolicyGate(sessionId: string): void { this.updateSession(sessionId, { policy: true }); }

  initSession(sessionId: string): void {
    if (!this.sessionMetrics.has(sessionId)) {
      this.sessionMetrics.set(sessionId, { session_id: sessionId, started_at: new Date().toISOString(), total_actions: 0, total_errors: 0, total_rag_queries: 0, total_policy_gates: 0, total_duration_ms: 0, tools_used: [] });
    }
  }

  getToolMetrics(tool: string): ToolMetrics | undefined { return this.toolMetrics.get(tool); }
  getAllToolMetrics(): ToolMetrics[] { return Array.from(this.toolMetrics.values()).sort((a, b) => b.call_count - a.call_count); }
  getSessionMetrics(sessionId: string): SessionMetrics | undefined { return this.sessionMetrics.get(sessionId); }
  getTopTools(n = 5): ToolMetrics[] { return this.getAllToolMetrics().slice(0, n); }
  getErrorRate(tool: string): number { const m = this.toolMetrics.get(tool); return (!m || m.call_count === 0) ? 0 : m.error_count / m.call_count; }
  exportJSON(): string { return JSON.stringify({ tools: this.getAllToolMetrics(), sessions: Array.from(this.sessionMetrics.values()) }, null, 2); }

  private updateSession(sessionId: string, opts: { tool?: string; success?: boolean; rag?: boolean; policy?: boolean }): void {
    const s = this.sessionMetrics.get(sessionId);
    if (!s) return;
    if (opts.tool) { s.total_actions++; if (!opts.success) s.total_errors++; if (!s.tools_used.includes(opts.tool)) s.tools_used.push(opts.tool); }
    if (opts.rag) s.total_rag_queries++;
    if (opts.policy) s.total_policy_gates++;
  }
}

export default TelemetryCollector;

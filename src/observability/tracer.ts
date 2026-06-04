// src/observability/tracer.ts
// GAIA-OS Observability Layer — Distributed Trace Collector
// Canon ref: C01
// Issue: #231

export interface TraceSpan {
  span_id: string;
  trace_id: string;
  action: string;
  tool: string | null;
  started_at: string;
  completed_at: string | null;
  duration_ms: number | null;
  outcome: "success" | "failure" | "pending";
  error: string | null;
  metadata: Record<string, unknown>;
}

export interface Trace {
  trace_id: string;
  goal: string;
  session_id: string;
  started_at: string;
  completed_at: string | null;
  duration_ms: number | null;
  iterations: number;
  outcome: "success" | "failure" | "halted" | "pending";
  spans: TraceSpan[];
}

function generateId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export class Tracer {
  private traces: Map<string, Trace> = new Map();

  startTrace(goal: string, sessionId: string): string {
    const trace_id = generateId("trace");
    this.traces.set(trace_id, { trace_id, goal, session_id: sessionId, started_at: new Date().toISOString(), completed_at: null, duration_ms: null, iterations: 0, outcome: "pending", spans: [] });
    return trace_id;
  }

  startSpan(traceId: string, action: string, tool: string | null = null, metadata: Record<string, unknown> = {}): string {
    const trace = this.traces.get(traceId);
    if (!trace) throw new Error(`Trace ${traceId} not found`);
    const span_id = generateId("span");
    trace.spans.push({ span_id, trace_id: traceId, action, tool, started_at: new Date().toISOString(), completed_at: null, duration_ms: null, outcome: "pending", error: null, metadata });
    trace.iterations++;
    return span_id;
  }

  endSpan(traceId: string, spanId: string, outcome: TraceSpan["outcome"], error?: string): void {
    const trace = this.traces.get(traceId);
    if (!trace) return;
    const span = trace.spans.find(s => s.span_id === spanId);
    if (!span) return;
    const now = new Date();
    span.completed_at = now.toISOString();
    span.duration_ms = now.getTime() - new Date(span.started_at).getTime();
    span.outcome = outcome;
    span.error = error ?? null;
  }

  endTrace(traceId: string, outcome: Trace["outcome"]): Trace | null {
    const trace = this.traces.get(traceId);
    if (!trace) return null;
    const now = new Date();
    trace.completed_at = now.toISOString();
    trace.duration_ms = now.getTime() - new Date(trace.started_at).getTime();
    trace.outcome = outcome;
    return trace;
  }

  getTrace(traceId: string): Trace | undefined { return this.traces.get(traceId); }
  getAllTraces(): Trace[] { return Array.from(this.traces.values()); }
  exportJSON(): string { return JSON.stringify(this.getAllTraces(), null, 2); }
}

export default Tracer;

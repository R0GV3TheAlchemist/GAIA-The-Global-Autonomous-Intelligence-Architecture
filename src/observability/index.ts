// src/observability/index.ts
// GAIA-OS Observability Layer — Unified Export & Stack Factory
// Canon ref: C01
// Issue: #231

export { Logger } from "./logger";
export type { LogEntry, ActionType, LogLevel, LoggerConfig } from "./logger";
export { Tracer } from "./tracer";
export type { Trace, TraceSpan } from "./tracer";
export { TelemetryCollector } from "./telemetry";
export type { ToolMetrics, SessionMetrics } from "./telemetry";
export { AuditChain } from "./audit";
export type { AuditRecord, AuditChainEntry, AuditVerificationResult } from "./audit";

import { Logger } from "./logger";
import { Tracer } from "./tracer";
import { TelemetryCollector } from "./telemetry";
import { AuditChain } from "./audit";

export interface ObservabilityStack {
  logger: Logger;
  tracer: Tracer;
  telemetry: TelemetryCollector;
  audit: AuditChain;
  session_id: string;
}

/**
 * Create a fully wired observability stack for a new GAIA session.
 * Pass the returned stack into PolicyEngine, AgenticLoop, and RAG layer.
 */
export function createObservabilityStack(sessionId: string, agentId = "gaia-core"): ObservabilityStack {
  const logger = new Logger({ session_id: sessionId, agent_id: agentId, console_output: false });
  const tracer = new Tracer();
  const telemetry = new TelemetryCollector();
  const audit = new AuditChain();
  telemetry.initSession(sessionId);
  logger.sessionStart();
  return { logger, tracer, telemetry, audit, session_id: sessionId };
}

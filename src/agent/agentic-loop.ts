// src/agent/agentic-loop.ts
// GAIA-OS — Agentic Loop Architecture
// Canon ref: C01 (GAIA as orchestration layer)
// Issue: #228
//
// The core runtime of GAIA-OS.
// Perceive → Reason → Act → Observe → Repeat until goal is achieved or halted.

import { PolicyEngine, SessionTrustLevel, PolicyDecision } from "../trust/policy-engine";
import { createObservabilityStack, ObservabilityStack } from "../observability/index";
import { RetrievalEngine, RetrievalQuery } from "../rag/retrieval";

export type LoopOutcome = "success" | "failure" | "halted" | "max_iterations_reached" | "pending_approval";

export interface AgentGoal {
  id: string;
  description: string;
  session_id: string;
  context?: Record<string, unknown>;
  max_iterations?: number;
}

export interface ToolCall {
  tool: string;
  input: Record<string, unknown>;
  input_summary: string;
}

export interface ToolResult {
  tool: string;
  output: unknown;
  output_summary: string;
  success: boolean;
  duration_ms: number;
  error?: string;
}

export interface LoopIteration {
  iteration: number;
  perception: string;
  reasoning: string;
  planned_actions: ToolCall[];
  executed_actions: ToolResult[];
  observation: string;
  should_continue: boolean;
}

export interface LoopResult {
  goal_id: string;
  goal: string;
  outcome: LoopOutcome;
  iterations: number;
  iterations_log: LoopIteration[];
  final_output: string;
  trace_id: string;
  duration_ms: number;
  halt_reason?: string;
}

export interface ToolHandler {
  name: string;
  execute: (input: Record<string, unknown>) => Promise<{ output: unknown; summary: string }>;
}

export const LOOP_CONFIG = {
  max_iterations: 10,
  max_actions_per_iteration: 5,
  halt_on_approval_pending: true,
} as const;

export class AgenticLoop {
  private policy: PolicyEngine;
  private obs: ObservabilityStack;
  private tools: Map<string, ToolHandler> = new Map();
  private rag?: RetrievalEngine;
  private isRunning = false;
  private haltRequested = false;

  constructor(sessionId: string, trustLevel: SessionTrustLevel = SessionTrustLevel.Standard, existingObs?: ObservabilityStack) {
    this.policy = new PolicyEngine(trustLevel);
    this.obs = existingObs ?? createObservabilityStack(sessionId);
  }

  registerTool(handler: ToolHandler): void { this.tools.set(handler.name, handler); }
  attachRAG(rag: RetrievalEngine): void { this.rag = rag; }
  requestHalt(): void { this.haltRequested = true; }

  async run(
    goal: AgentGoal,
    planner: (perception: string, history: LoopIteration[]) => Promise<ToolCall[]>,
    evaluator: (results: ToolResult[], history: LoopIteration[]) => Promise<{ done: boolean; observation: string; output?: string }>
  ): Promise<LoopResult> {
    if (this.isRunning) throw new Error("Loop already running.");
    this.isRunning = true;
    this.haltRequested = false;

    const maxIter = goal.max_iterations ?? LOOP_CONFIG.max_iterations;
    const traceId = this.obs.tracer.startTrace(goal.description, goal.session_id);
    const startTime = Date.now();
    const iterationsLog: LoopIteration[] = [];
    let finalOutput = "";
    let outcome: LoopOutcome = "pending_approval";

    this.obs.logger.log("loop_start", { trace_id: traceId, input_summary: `Goal: ${goal.description}`, output_summary: `max_iterations: ${maxIter}` });

    try {
      for (let i = 0; i < maxIter; i++) {
        if (this.haltRequested) { outcome = "halted"; break; }

        const spanId = this.obs.tracer.startSpan(traceId, `iteration-${i + 1}`, null);
        const perception = await this.perceive(goal, iterationsLog, traceId);
        const plannedActions = await planner(perception, iterationsLog);
        const reasoning = `Planned ${plannedActions.length} action(s): ${plannedActions.map(a => a.tool).join(", ")}`;

        this.obs.logger.log("loop_iteration", { trace_id: traceId, input_summary: `iteration ${i + 1}: ${reasoning}`, output_summary: perception.slice(0, 200) });

        const executedActions: ToolResult[] = [];
        let pendingApproval = false;

        for (const action of plannedActions.slice(0, LOOP_CONFIG.max_actions_per_iteration)) {
          const policyResult = this.policy.evaluate({ tool: action.tool, input_summary: action.input_summary });
          this.obs.logger.policyGate(action.tool, policyResult.decision as any, policyResult.tier);
          this.obs.audit.append({ id: `audit-${Date.now()}-${Math.random().toString(36).slice(2)}`, timestamp: new Date().toISOString(), session_id: goal.session_id, action_type: "tool_call", tool: action.tool, decision: policyResult.decision as any, trust_tier: policyResult.tier, gaian_override: false, input_summary: action.input_summary, metadata: { goal_id: goal.id, iteration: i + 1 } });

          if (policyResult.decision === PolicyDecision.Denied) {
            executedActions.push({ tool: action.tool, output: null, output_summary: `Denied: ${policyResult.reason}`, success: false, duration_ms: 0, error: policyResult.reason });
            continue;
          }

          if (policyResult.decision === PolicyDecision.Pending) {
            pendingApproval = true;
            this.obs.logger.log("approval_requested", { tool: action.tool, trace_id: traceId, input_summary: policyResult.requires_approval_prompt ?? "" });
            if (LOOP_CONFIG.halt_on_approval_pending) break;
            continue;
          }

          const handler = this.tools.get(action.tool);
          if (!handler) {
            executedActions.push({ tool: action.tool, output: null, output_summary: `No handler for: ${action.tool}`, success: false, duration_ms: 0, error: "Tool handler not found" });
            continue;
          }

          const t0 = Date.now();
          try {
            const result = await handler.execute(action.input);
            const duration_ms = Date.now() - t0;
            executedActions.push({ tool: action.tool, output: result.output, output_summary: result.summary, success: true, duration_ms });
            this.obs.logger.toolCall(action.tool, action.input_summary, result.summary, duration_ms, { trace_id: traceId });
            this.obs.telemetry.recordToolCall(action.tool, duration_ms, true, goal.session_id);
          } catch (err: any) {
            const duration_ms = Date.now() - t0;
            executedActions.push({ tool: action.tool, output: null, output_summary: err.message, success: false, duration_ms, error: err.message });
            this.obs.logger.error(action.tool, err.message, traceId);
            this.obs.telemetry.recordToolCall(action.tool, duration_ms, false, goal.session_id);
          }
        }

        if (pendingApproval) {
          outcome = "pending_approval";
          this.obs.tracer.endSpan(traceId, spanId, "pending");
          iterationsLog.push({ iteration: i + 1, perception, reasoning, planned_actions: plannedActions, executed_actions: executedActions, observation: "Paused — awaiting Gaian approval.", should_continue: false });
          break;
        }

        const evaluation = await evaluator(executedActions, iterationsLog);
        iterationsLog.push({ iteration: i + 1, perception, reasoning, planned_actions: plannedActions, executed_actions: executedActions, observation: evaluation.observation, should_continue: !evaluation.done });
        this.obs.tracer.endSpan(traceId, spanId, executedActions.every(r => r.success) ? "success" : "failure");

        if (evaluation.done) { outcome = "success"; finalOutput = evaluation.output ?? evaluation.observation; break; }
        if (i === maxIter - 1) { outcome = "max_iterations_reached"; finalOutput = evaluation.observation; }
      }
    } catch (err: any) {
      outcome = "failure";
      this.obs.logger.error(null, `Loop error: ${err.message}`, traceId);
    } finally {
      this.isRunning = false;
    }

    const duration_ms = Date.now() - startTime;
    this.obs.tracer.endTrace(traceId, outcome === "success" ? "success" : outcome === "halted" ? "halted" : "failure");
    this.obs.logger.log("loop_end", { trace_id: traceId, input_summary: `Goal: ${goal.description}`, output_summary: `outcome: ${outcome}, iterations: ${iterationsLog.length}`, duration_ms });

    return { goal_id: goal.id, goal: goal.description, outcome, iterations: iterationsLog.length, iterations_log: iterationsLog, final_output: finalOutput, trace_id: traceId, duration_ms };
  }

  private async perceive(goal: AgentGoal, history: LoopIteration[], traceId: string): Promise<string> {
    const parts = [`Goal: ${goal.description}`, `Iteration: ${history.length + 1}`, `Session: ${goal.session_id}`];
    if (history.length > 0) {
      const last = history[history.length - 1];
      parts.push(`Last observation: ${last.observation}`);
      parts.push(`Actions taken: ${last.executed_actions.map(a => `${a.tool} (${a.success ? "✓" : "✗"})`).join(", ")}`);
    }
    if (this.rag) {
      const ragResult = this.rag.retrieve(null, { text: goal.description, top_k: 3, min_similarity: 0.6 });
      if (ragResult.chunks.length > 0) {
        parts.push(`\nRelevant knowledge:\n${ragResult.chunks.map(r => `[${r.chunk.source_label}] ${r.chunk.content.slice(0, 200)}`).join("\n")}`);
        this.obs.logger.ragQuery(goal.description, ragResult.chunks.length, ragResult.retrieval_ms, traceId);
        this.obs.telemetry.recordRagQuery(goal.session_id);
      }
    }
    return parts.join("\n");
  }

  getObservability(): ObservabilityStack { return this.obs; }
  getPolicy(): PolicyEngine { return this.policy; }
  isCurrentlyRunning(): boolean { return this.isRunning; }
}

export default AgenticLoop;

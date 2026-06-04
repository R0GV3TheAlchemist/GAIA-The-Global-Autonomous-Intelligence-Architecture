// src/agent/tool-registry.ts
// GAIA-OS — Tool & Capability Registry
// Canon ref: C01, C32 (Synergy Doctrine)
// Issue: #221 / #230

export type ToolTrustTier = 0 | 1 | 2 | 3;
export type ToolStatus = "healthy" | "degraded" | "unavailable" | "unknown";

export interface ToolRegistration {
  name: string;
  version: string;
  description: string;
  tier: ToolTrustTier;
  scope: string[];
  input_schema: Record<string, string>;
  output_schema: string;
  fallback?: string;
  tags: string[];
  registered_at: string;
  last_health_check?: string;
  status: ToolStatus;
}

export interface RegistryQueryResult {
  tools: ToolRegistration[];
  total: number;
  healthy: number;
  degraded: number;
  unavailable: number;
}

export class ToolRegistry {
  private registry: Map<string, ToolRegistration> = new Map();

  register(tool: Omit<ToolRegistration, "registered_at" | "status">): void {
    this.registry.set(tool.name, { ...tool, registered_at: new Date().toISOString(), status: "unknown" });
  }

  get(name: string): ToolRegistration | undefined { return this.registry.get(name); }
  has(name: string): boolean { return this.registry.has(name); }

  query(filters: { tier?: ToolTrustTier; tag?: string; status?: ToolStatus } = {}): RegistryQueryResult {
    let tools = Array.from(this.registry.values());
    if (filters.tier !== undefined) tools = tools.filter(t => t.tier === filters.tier);
    if (filters.tag) tools = tools.filter(t => t.tags.includes(filters.tag!));
    if (filters.status) tools = tools.filter(t => t.status === filters.status);
    return { tools, total: tools.length, healthy: tools.filter(t => t.status === "healthy").length, degraded: tools.filter(t => t.status === "degraded").length, unavailable: tools.filter(t => t.status === "unavailable").length };
  }

  updateStatus(name: string, status: ToolStatus): void {
    const tool = this.registry.get(name);
    if (tool) { tool.status = status; tool.last_health_check = new Date().toISOString(); }
  }

  getFallback(name: string): ToolRegistration | undefined {
    const tool = this.registry.get(name);
    if (!tool?.fallback) return undefined;
    return this.registry.get(tool.fallback);
  }

  listNames(): string[] { return Array.from(this.registry.keys()); }
  exportJSON(): string { return JSON.stringify(Array.from(this.registry.values()), null, 2); }
  getCount(): number { return this.registry.size; }
}

export function registerDefaultTools(registry: ToolRegistry): void {
  const tools: Omit<ToolRegistration, "registered_at" | "status">[] = [
    { name: "memory.read", version: "1.0.0", description: "Read from GAIA persistent memory store", tier: 0, scope: ["memory:read"], input_schema: { key: "string" }, output_schema: "{ value: unknown, found: boolean }", tags: ["memory", "safe"] },
    { name: "rag.query", version: "1.0.0", description: "Query the RAG knowledge base across all GAIA canon sources", tier: 0, scope: ["rag:read"], input_schema: { query: "string", top_k: "number (optional)" }, output_schema: "RetrievalResult", tags: ["rag", "knowledge", "safe"] },
    { name: "files.list", version: "1.0.0", description: "List files in a directory", tier: 0, scope: ["files:read"], input_schema: { path: "string" }, output_schema: "string[]", tags: ["files", "safe"] },
    { name: "files.read", version: "1.0.0", description: "Read the contents of a file", tier: 0, scope: ["files:read"], input_schema: { path: "string" }, output_schema: "string", tags: ["files", "safe"] },
    { name: "memory.write", version: "1.0.0", description: "Write to GAIA persistent memory", tier: 1, scope: ["memory:write"], input_schema: { key: "string", value: "unknown" }, output_schema: "{ success: boolean }", tags: ["memory", "write"] },
    { name: "files.write", version: "1.0.0", description: "Write or create a local file", tier: 1, scope: ["files:write"], input_schema: { path: "string", content: "string" }, output_schema: "{ success: boolean, path: string }", tags: ["files", "write"] },
    { name: "github.create_issue", version: "1.0.0", description: "Create a GitHub issue", tier: 1, scope: ["repo:write"], input_schema: { title: "string", body: "string" }, output_schema: "{ number: number, url: string }", tags: ["github", "write"] },
    { name: "github.push_files", version: "1.0.0", description: "Push files to a GitHub branch", tier: 1, scope: ["repo:write"], input_schema: { files: "Array<{path,content}>", message: "string", branch: "string" }, output_schema: "{ sha: string }", tags: ["github", "write"] },
    { name: "memory.delete", version: "1.0.0", description: "Delete a memory entry — irreversible", tier: 2, scope: ["memory:delete"], input_schema: { key: "string" }, output_schema: "{ success: boolean }", tags: ["memory", "delete", "sensitive"] },
    { name: "files.delete", version: "1.0.0", description: "Delete a local file — irreversible", tier: 2, scope: ["files:delete"], input_schema: { path: "string" }, output_schema: "{ success: boolean }", tags: ["files", "delete", "sensitive"] },
    { name: "github.merge_pr", version: "1.0.0", description: "Merge a pull request", tier: 2, scope: ["repo:admin"], input_schema: { pull_number: "number", merge_method: "string" }, output_schema: "{ merged: boolean, sha: string }", tags: ["github", "merge", "sensitive"] },
    { name: "data.export", version: "1.0.0", description: "Export all Gaian data outside the system — critical", tier: 3, scope: ["data:export"], input_schema: { destination: "string", format: "string" }, output_schema: "{ path: string, size_bytes: number }", tags: ["data", "export", "critical"] },
  ];
  for (const tool of tools) registry.register(tool);
}

export default ToolRegistry;

// src/observability/audit.ts
// GAIA-OS Observability Layer — Immutable SHA-256 Audit Chain
// Canon ref: C01, SOVEREIGNTY.md
// Issue: #231

import { createHash } from "crypto";

export interface AuditRecord {
  id: string;
  timestamp: string;
  session_id: string;
  action_type: string;
  tool: string | null;
  decision: "approved" | "denied" | "pending";
  trust_tier: number;
  gaian_override: boolean;
  input_summary: string;
  metadata: Record<string, unknown>;
}

export interface AuditChainEntry extends AuditRecord {
  previous_hash: string;
  entry_hash: string;
  sequence: number;
}

export interface AuditVerificationResult {
  valid: boolean;
  chain_length: number;
  first_broken_at: number | null;
  broken_entry_id: string | null;
}

const GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000";

export class AuditChain {
  private chain: AuditChainEntry[] = [];

  append(record: AuditRecord): AuditChainEntry {
    const previous_hash = this.chain.length > 0 ? this.chain[this.chain.length - 1].entry_hash : GENESIS_HASH;
    const sequence = this.chain.length;
    const payload = JSON.stringify({ ...record, previous_hash, sequence });
    const entry_hash = createHash("sha256").update(payload, "utf8").digest("hex");
    const entry: AuditChainEntry = { ...record, previous_hash, entry_hash, sequence };
    this.chain.push(entry);
    return entry;
  }

  verify(): AuditVerificationResult {
    for (let i = 1; i < this.chain.length; i++) {
      if (this.chain[i].previous_hash !== this.chain[i - 1].entry_hash) {
        return { valid: false, chain_length: this.chain.length, first_broken_at: i, broken_entry_id: this.chain[i].id };
      }
    }
    return { valid: true, chain_length: this.chain.length, first_broken_at: null, broken_entry_id: null };
  }

  query(filters: { tool?: string; decision?: AuditRecord["decision"]; since?: string; limit?: number } = {}): AuditChainEntry[] {
    let results = [...this.chain];
    if (filters.tool) results = results.filter(e => e.tool === filters.tool);
    if (filters.decision) results = results.filter(e => e.decision === filters.decision);
    if (filters.since) results = results.filter(e => e.timestamp >= filters.since!);
    if (filters.limit) results = results.slice(-filters.limit);
    return results;
  }

  exportJSON(): string { return JSON.stringify(this.chain, null, 2); }
  getLength(): number { return this.chain.length; }
  getLatest(): AuditChainEntry | null { return this.chain[this.chain.length - 1] ?? null; }
  getAll(): AuditChainEntry[] { return [...this.chain]; }
}

export default AuditChain;

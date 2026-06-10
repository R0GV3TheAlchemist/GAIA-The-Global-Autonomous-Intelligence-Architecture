<template>
  <div class="mesh-widget">
    <!-- ── Header ──────────────────────────────────────────────────────── -->
    <div class="mesh-header">
      <span class="mesh-title">🌐 Mesh Status</span>

      <span :class="['mesh-badge', status?.ok ? 'ok' : 'degraded']">
        {{ status?.ok ? 'ALL STORES OK' : 'DEGRADED' }}
      </span>

      <div class="mesh-meta">
        <span class="meta-chip">{{ status?.backend_driver ?? '…' }}</span>
        <span class="meta-chip">node: {{ status?.node_id ?? '…' }}</span>
      </div>

      <button
        class="refresh-btn"
        :class="{ spinning: loading }"
        :disabled="loading"
        title="Refresh now"
        @click="refresh"
      >↻</button>
    </div>

    <!-- ── Error banner ─────────────────────────────────────────────────── -->
    <div v-if="error" class="error-banner">⚠ {{ error }}</div>

    <!-- ── Loading skeleton ─────────────────────────────────────────────── -->
    <div v-if="loading && !status" class="skeleton-rows">
      <div v-for="n in 4" :key="n" class="skeleton-row" />
    </div>

    <!-- ── Store rows ────────────────────────────────────────────────────── -->
    <div v-else-if="status" class="store-list">
      <div
        v-for="[key, store] in storeEntries"
        :key="key"
        :class="['store-row', store.reachable ? 'up' : 'down']"
      >
        <!-- Status dot -->
        <span :class="['store-dot', store.reachable ? 'green' : 'red']" />

        <!-- Store name -->
        <span class="store-name">{{ storeLabel(key) }}</span>

        <!-- Latency bar -->
        <div class="latency-bar-wrap">
          <div
            class="latency-bar-fill"
            :style="{ width: latencyBarWidth(store.latency_ms) }"
            :class="latencyBarClass(store.latency_ms)"
          />
        </div>

        <!-- Latency value -->
        <span class="latency-val">
          {{ store.reachable
              ? (store.latency_ms !== null ? store.latency_ms.toFixed(1) + ' ms' : '—')
              : 'unreachable' }}
        </span>
      </div>
    </div>

    <!-- ── Empty state ───────────────────────────────────────────────────── -->
    <div v-else class="empty-state">Awaiting first poll…</div>

    <!-- ── Footer timestamp ─────────────────────────────────────────────── -->
    <div class="mesh-footer">
      <span v-if="lastCheckedAt">
        checked {{ relativeTime(lastCheckedAt) }}
      </span>
      <span v-else class="dim">not yet polled</span>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import { useMeshStatus, type StoreStatus } from './useMeshStatus'

const props = defineProps<{ pollMs?: number }>()

const { status, loading, error, lastCheckedAt, refresh } = useMeshStatus(props.pollMs)

// Ordered store entries for consistent display
const STORE_ORDER = ['audit', 'sovereign_memory', 'telemetry', 'crisis_engine'] as const

const storeEntries = computed(() => {
  if (!status.value) return []
  return STORE_ORDER.map(k => [k, status.value!.stores[k]] as [string, StoreStatus])
})

const STORE_LABELS: Record<string, string> = {
  audit:            '📋 Audit',
  sovereign_memory: '🧠 Sovereign Memory',
  telemetry:        '📡 Telemetry',
  crisis_engine:    '🛡  Crisis Engine',
}

function storeLabel(key: string): string {
  return STORE_LABELS[key] ?? key
}

// Max latency we consider for the bar (anything >= this = full bar)
const BAR_MAX_MS = 50

function latencyBarWidth(ms: number | null): string {
  if (ms === null) return '0%'
  const pct = Math.min((ms / BAR_MAX_MS) * 100, 100)
  return `${pct.toFixed(1)}%`
}

function latencyBarClass(ms: number | null): string {
  if (ms === null) return 'bar-unknown'
  if (ms < 5)  return 'bar-fast'
  if (ms < 20) return 'bar-ok'
  return 'bar-slow'
}

function relativeTime(d: Date): string {
  const diff = Math.round((Date.now() - d.getTime()) / 1000)
  if (diff < 5)    return 'just now'
  if (diff < 60)   return `${diff}s ago`
  if (diff < 3600) return `${Math.round(diff / 60)}m ago`
  return `${Math.round(diff / 3600)}h ago`
}
</script>

<style scoped>
.mesh-widget {
  display: flex;
  flex-direction: column;
  background: var(--gaia-surface, #0d0e14);
  color: var(--gaia-text, #e2e8f0);
  font-family: var(--gaia-mono, 'JetBrains Mono', monospace);
  font-size: 12px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
  min-width: 320px;
}

/* ── Header ───────────────────────────────────────────────────────────────── */
.mesh-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: var(--gaia-surface-2, #161820);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-wrap: wrap;
}

.mesh-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--gaia-teal, #4f98a3);
  flex-shrink: 0;
}

.mesh-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
  flex-shrink: 0;
}
.mesh-badge.ok       { background: rgba(67,122,34,0.2);  color: #6fcf3a; }
.mesh-badge.degraded { background: rgba(161,53,68,0.25); color: #f87171; }

.mesh-meta {
  display: flex;
  gap: 6px;
  margin-left: auto;
}

.meta-chip {
  padding: 2px 7px;
  border-radius: 3px;
  background: rgba(255,255,255,0.05);
  color: var(--gaia-text-dim, #94a3b8);
  font-size: 10px;
}

.refresh-btn {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.1);
  color: var(--gaia-text-dim, #94a3b8);
  border-radius: 4px;
  padding: 2px 7px;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  transition: all 0.15s;
  flex-shrink: 0;
}
.refresh-btn:hover:not(:disabled) {
  border-color: var(--gaia-teal, #4f98a3);
  color: var(--gaia-teal, #4f98a3);
}
.refresh-btn:disabled { opacity: 0.4; cursor: default; }
.refresh-btn.spinning { animation: spin 0.8s linear infinite; }

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Error banner ─────────────────────────────────────────────────────────── */
.error-banner {
  padding: 8px 16px;
  background: rgba(161,53,68,0.12);
  color: #f87171;
  font-size: 11px;
  border-bottom: 1px solid rgba(161,53,68,0.25);
}

/* ── Skeleton ─────────────────────────────────────────────────────────────── */
.skeleton-rows { padding: 8px 16px; display: flex; flex-direction: column; gap: 8px; }
.skeleton-row {
  height: 32px;
  border-radius: 6px;
  background: rgba(255,255,255,0.04);
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50%       { opacity: 0.8; }
}

/* ── Store rows ───────────────────────────────────────────────────────────── */
.store-list {
  display: flex;
  flex-direction: column;
  padding: 8px 0;
}

.store-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  transition: background 0.1s;
}
.store-row:hover   { background: rgba(255,255,255,0.025); }
.store-row.down    { opacity: 0.75; }

.store-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.store-dot.green { background: #437a22; box-shadow: 0 0 5px #437a22; }
.store-dot.red   { background: #a13544; }

.store-name {
  min-width: 160px;
  font-weight: 500;
  color: var(--gaia-text, #e2e8f0);
}

/* Latency bar */
.latency-bar-wrap {
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,0.06);
  border-radius: 2px;
  overflow: hidden;
}
.latency-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.4s ease;
}
.bar-fast    { background: #437a22; }
.bar-ok      { background: #4f98a3; }
.bar-slow    { background: #d19900; }
.bar-unknown { background: rgba(255,255,255,0.1); width: 100% !important; }

.latency-val {
  min-width: 80px;
  text-align: right;
  color: var(--gaia-text-dim, #94a3b8);
  font-size: 11px;
}
.store-row.down .latency-val { color: #a13544; }

/* ── Footer ───────────────────────────────────────────────────────────────── */
.mesh-footer {
  padding: 6px 16px;
  font-size: 10px;
  color: var(--gaia-text-dim, #94a3b8);
  border-top: 1px solid rgba(255,255,255,0.04);
  text-align: right;
}
.dim { opacity: 0.5; }

/* ── Empty state ──────────────────────────────────────────────────────────── */
.empty-state {
  padding: 32px;
  text-align: center;
  color: var(--gaia-text-dim, #94a3b8);
  opacity: 0.5;
}
</style>

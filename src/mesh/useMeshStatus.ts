/**
 * useMeshStatus — composable that polls GET /api/mesh/status
 *
 * Usage:
 *   const { status, loading, error, lastCheckedAt, refresh } = useMeshStatus()
 *
 * The poll interval defaults to VITE_MESH_POLL_MS env var (ms), or 30 000.
 * Exponential back-off kicks in after consecutive fetch errors, capped at 5 min.
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { API_BASE } from '../config'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface StoreStatus {
  reachable: boolean
  latency_ms: number | null
}

export interface MeshStatusResponse {
  ok:             boolean
  checked_at:     string
  backend_driver: string
  node_id:        string
  stores: {
    audit:            StoreStatus
    sovereign_memory: StoreStatus
    telemetry:        StoreStatus
    crisis_engine:    StoreStatus
  }
}

// ---------------------------------------------------------------------------
// Composable
// ---------------------------------------------------------------------------

const metaEnv = ((import.meta as unknown as { env?: Record<string, string> }).env) ?? {}
const DEFAULT_POLL_MS = parseInt(metaEnv.VITE_MESH_POLL_MS ?? '30000', 10)
const MAX_BACKOFF_MS  = 5 * 60 * 1000   // 5 min
const MESH_URL        = `${API_BASE}/mesh/status`

export function useMeshStatus(pollMs: number = DEFAULT_POLL_MS) {
  const status         = ref<MeshStatusResponse | null>(null)
  const loading        = ref(false)
  const error          = ref<string | null>(null)
  const lastCheckedAt  = ref<Date | null>(null)

  let timer:            ReturnType<typeof setTimeout> | null = null
  let consecutiveErrors = 0

  async function refresh(): Promise<void> {
    loading.value = true
    error.value   = null
    try {
      const res = await fetch(MESH_URL, { cache: 'no-store' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      status.value       = await res.json() as MeshStatusResponse
      lastCheckedAt.value = new Date()
      consecutiveErrors   = 0
    } catch (err: unknown) {
      consecutiveErrors++
      error.value = err instanceof Error ? err.message : String(err)
    } finally {
      loading.value = false
    }
  }

  function schedule(): void {
    const backoff = consecutiveErrors > 0
      ? Math.min(pollMs * 2 ** (consecutiveErrors - 1), MAX_BACKOFF_MS)
      : pollMs
    timer = setTimeout(async () => {
      await refresh()
      schedule()
    }, backoff)
  }

  onMounted(async () => {
    await refresh()
    schedule()
  })

  onUnmounted(() => {
    if (timer !== null) clearTimeout(timer)
  })

  return { status, loading, error, lastCheckedAt, refresh }
}

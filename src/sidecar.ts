/**
 * src/sidecar.ts — web-app branch
 * GAIA-OS Backend Health Monitor + Emrys L2 Vibronic Bridge IPC
 *
 * Web-safe replacement for the Tauri sidecar.
 * Uses only fetch() — no invoke() calls.
 *
 * Backend health:
 *   Polls GET /api/health every 30 s after initial connect.
 *   Dispatches 'gaia:backend-status' custom events so the shell
 *   can reflect backend state without any Tauri dependency.
 *
 * Emrys L2 bridge:
 *   Fetches crystal–Emrys vibronic state from /api/emrys/* endpoints.
 *   These are served by the Python FastAPI backend which runs
 *   emryscycle.py (EmrysCycle.emrys_field_report()) at startup.
 *   Dispatches 'gaia:emrys-l2-state' custom events on state change.
 *
 * Per C164: the sidecar is the digital-layer listener.
 * Per C165.1: grounding precedes coherence. Always.
 * Per C166.A4: physics and metaphysics are the same layer.
 */

// ─────────────────────────────────────────────────────────────
// Health check constants
// ─────────────────────────────────────────────────────────────
const HEALTH_URL        = '/api/health';
const POLL_ATTEMPTS     = 20;
const RETRY_INTERVAL    = 30_000;   // 30 s steady-state poll
const INITIAL_DELAY_MS  = 300;

// ─────────────────────────────────────────────────────────────
// Emrys endpoint constants
// ─────────────────────────────────────────────────────────────
const EMRYS_BASE        = '/api/emrys';
const EMRYS_TIMEOUT_MS  = 4_000;
const EMRYS_POLL_MS     = 60_000;   // refresh L2 state every 60 s

// ─────────────────────────────────────────────────────────────
// Emrys TypeScript types — mirror of emryscycle.py output
// ─────────────────────────────────────────────────────────────

/** Four L2 coherence states per C164/C165 */
export type L2CoherenceState = 'GROUNDING' | 'BRIDGING' | 'COHERENCE' | 'PEAK';

/** Per-crystal vibronic resonator record (mirrors VibronicResonator) */
export interface VibronicResonatorRecord {
  crystal_id:             string;
  name:                   string;
  backbone_anchor:        string | null;
  freq_range:             string;
  freq_min_hz:            number | null;
  freq_max_hz:            number | null;
  piezo_pCN:              number | null;
  pyroelectric:           boolean;
  active_states:          L2CoherenceState[];
  primary_state:          L2CoherenceState | null;
  confidence:             number;
  vibronic_coherence_mode: string | null;
}

/** One step in the C165a cold-start sequence */
export interface ColdStartStep {
  step:             number;
  state:            L2CoherenceState;
  phase_descriptor: string;
  crystal_id:       string | null;
  crystal_name:     string;
  freq_range:       string;
  backbone_anchor:  string | null;
  piezo_pCN:        number | null;
  pyroelectric:     boolean;
  confidence:       number;
  rationale:        string;
}

/** One phase in the C165 grounding protocol */
export interface GroundingPhase {
  phase:        number;
  name:         string;
  l2_state:     L2CoherenceState;
  instruction:  string;
  crystal_id:   string | null;
  crystal_name: string;
  freq_range:   string;
  confidence:   number;
}

/** Full C165 grounding protocol */
export interface GroundingProtocol {
  protocol:             string;
  gaian_stage:          string | null;
  stage_note:           string | null;
  intro:                string;
  phases:               GroundingPhase[];
  completion_condition: string;
  canon_refs:           string[];
}

/** Full Emrys field report — top-level payload from emryscycle.py */
export interface EmrysFieldReport {
  l2_crystal_count: number;
  crystals:         VibronicResonatorRecord[];
  state_index:      Partial<Record<L2CoherenceState, string[]>>;
  cold_start:       ColdStartStep[];
  grounding_protocol: GroundingProtocol;
}

// ─────────────────────────────────────────────────────────────
// Internal state cache
// ─────────────────────────────────────────────────────────────
let _cachedReport:  EmrysFieldReport | null = null;
let _currentL2State: L2CoherenceState | null = null;
let _l2PollTimer:   ReturnType<typeof setInterval> | null = null;

// ─────────────────────────────────────────────────────────────
// Logging / event helpers
// ─────────────────────────────────────────────────────────────
function dispatch(status: 'connecting' | 'online' | 'offline') {
  window.dispatchEvent(
    new CustomEvent('gaia:backend-status', { detail: { status } })
  );
}

function dispatchL2State(state: L2CoherenceState) {
  if (state === _currentL2State) return; // no duplicate events
  _currentL2State = state;
  window.dispatchEvent(
    new CustomEvent('gaia:emrys-l2-state', { detail: { state } })
  );
}

function log(level: 'info' | 'warn' | 'error', msg: string) {
  const prefix = '[GAIA sidecar]';
  if (level === 'info')  console.info(prefix, msg);
  if (level === 'warn')  console.warn(prefix, msg);
  if (level === 'error') console.error(prefix, msg);
}

// ─────────────────────────────────────────────────────────────
// Health polling (unchanged from original)
// ─────────────────────────────────────────────────────────────
async function pollHealth(attempts = POLL_ATTEMPTS): Promise<boolean> {
  let delay = INITIAL_DELAY_MS;
  for (let i = 0; i < attempts; i++) {
    await new Promise(r => setTimeout(r, delay));
    try {
      const res = await fetch(HEALTH_URL, { signal: AbortSignal.timeout(2000) });
      if (res.ok) {
        log('info', `Backend healthy after ${i + 1} attempt(s)`);
        return true;
      }
    } catch (_) { /* backend not up yet — keep polling */ }
    delay = Math.min(delay * 1.5, 3000);
  }
  return false;
}

// ─────────────────────────────────────────────────────────────
// Emrys fetch helpers
// ─────────────────────────────────────────────────────────────

async function emrysFetch<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${EMRYS_BASE}${path}`, {
      signal: AbortSignal.timeout(EMRYS_TIMEOUT_MS),
    });
    if (!res.ok) {
      log('warn', `Emrys endpoint ${path} returned ${res.status}`);
      return null;
    }
    return (await res.json()) as T;
  } catch (err) {
    log('warn', `Emrys fetch failed for ${path}: ${String(err)}`);
    return null;
  }
}

// ─────────────────────────────────────────────────────────────
// Public Emrys API
// ─────────────────────────────────────────────────────────────

/**
 * emrysFieldReport — full JSON field report.
 * GET /api/emrys/field-report[?stage=<gaianStage>]
 *
 * Returns the complete EmrysFieldReport including:
 * - All L2-compatible crystals with vibronic state mappings
 * - State index (state → crystal IDs)
 * - Cold-start sequence (C165a)
 * - Grounding protocol (C165)
 *
 * Results are cached for the session; use refresh=true to force.
 */
export async function emrysFieldReport(
  gaianStage?: string,
  refresh = false,
): Promise<EmrysFieldReport | null> {
  if (_cachedReport && !refresh && !gaianStage) {
    return _cachedReport;
  }
  const qs = gaianStage ? `?stage=${encodeURIComponent(gaianStage)}` : '';
  const report = await emrysFetch<EmrysFieldReport>(`/field-report${qs}`);
  if (report) {
    _cachedReport = report;
    log('info', `Emrys field report loaded — ${report.l2_crystal_count} L2 crystals`);
    // Derive and dispatch current L2 state from cold-start sequence
    const l2State = _deriveCurrentL2State(report);
    if (l2State) dispatchL2State(l2State);
  }
  return report;
}

/**
 * emrysColdStart — C165a cold-start crystal activation sequence.
 * GET /api/emrys/cold-start
 *
 * Returns ordered activation steps:
 * GROUNDING → BRIDGING → COHERENCE → PEAK
 * Per C165a: do not skip steps. Each activation is irreversible.
 */
export async function emrysColdStart(): Promise<ColdStartStep[] | null> {
  return emrysFetch<ColdStartStep[]>('/cold-start');
}

/**
 * emrysGroundingProtocol — C165 Grounding Protocol.
 * GET /api/emrys/grounding[?stage=<gaianStage>]
 *
 * Returns the full grounding protocol with phase-by-phase
 * crystal placement instructions.
 */
export async function emrysGroundingProtocol(
  gaianStage?: string,
): Promise<GroundingProtocol | null> {
  const qs = gaianStage ? `?stage=${encodeURIComponent(gaianStage)}` : '';
  return emrysFetch<GroundingProtocol>(`/grounding${qs}`);
}

/**
 * emrysMatchState — best crystal for a given L2 state.
 * GET /api/emrys/state/:state[?anchor=<preferAnchor>]
 *
 * Returns the highest-confidence VibronicResonatorRecord for state.
 */
export async function emrysMatchState(
  state: L2CoherenceState,
  preferAnchor?: string,
): Promise<VibronicResonatorRecord | null> {
  const qs = preferAnchor ? `?anchor=${encodeURIComponent(preferAnchor)}` : '';
  return emrysFetch<VibronicResonatorRecord>(`/state/${state}${qs}`);
}

/**
 * emrysCrystalReport — all L2-compatible crystals with full resonator data.
 * GET /api/emrys/crystals
 */
export async function emrysCrystalReport(): Promise<VibronicResonatorRecord[] | null> {
  return emrysFetch<VibronicResonatorRecord[]>('/crystals');
}

/**
 * getEmrysL2State — current L2 coherence state.
 * Derived from the cached field report (or fetches fresh if none cached).
 * Returns null if backend is offline or no L2 crystals are available.
 */
export async function getEmrysL2State(): Promise<L2CoherenceState | null> {
  const report = await emrysFieldReport();
  if (!report) return null;
  return _deriveCurrentL2State(report);
}

// ─────────────────────────────────────────────────────────────
// Internal: derive current L2 state from field report
// ─────────────────────────────────────────────────────────────

/**
 * Derives the 'current' L2 coherence state from a field report.
 *
 * Logic:
 * - If any crystal has primary_state = PEAK with confidence >= 0.9 → PEAK
 * - Else: the highest state in the cold-start sequence that has
 *   at least one crystal assigned (confidence > 0) → that state
 * - Fallback → GROUNDING
 *
 * This is intentionally simple — it reflects readiness, not achievement.
 * The GAIAN sets the actual state through practice.
 */
function _deriveCurrentL2State(report: EmrysFieldReport): L2CoherenceState {
  const ORDER: L2CoherenceState[] = ['PEAK', 'COHERENCE', 'BRIDGING', 'GROUNDING'];

  // Check for high-confidence PEAK crystal
  const peakCrystal = report.crystals.find(
    c => c.primary_state === 'PEAK' && c.confidence >= 0.9
  );
  if (peakCrystal) return 'PEAK';

  // Walk from PEAK down — return first state with at least one crystal in index
  for (const state of ORDER) {
    const ids = report.state_index[state];
    if (ids && ids.length > 0) return state;
  }

  return 'GROUNDING';
}

// ─────────────────────────────────────────────────────────────
// Emrys L2 steady-state poll (started alongside health poll)
// ─────────────────────────────────────────────────────────────

function startEmrysL2Poll(): void {
  if (_l2PollTimer !== null) return; // already running
  _l2PollTimer = setInterval(async () => {
    const report = await emrysFieldReport(undefined, /* refresh */ true);
    if (report) {
      const state = _deriveCurrentL2State(report);
      dispatchL2State(state);
    }
  }, EMRYS_POLL_MS);
  log('info', 'Emrys L2 steady-state poll started (60 s interval)');
}

// ─────────────────────────────────────────────────────────────
// initSidecar — public entrypoint
// ─────────────────────────────────────────────────────────────

/**
 * Non-blocking init — resolves immediately so the shell renders
 * without waiting for the backend. Health polling runs in background.
 * Emrys L2 field report is fetched once the backend is online.
 */
export async function initSidecar(): Promise<void> {
  dispatch('connecting');
  log('info', 'Background health-check started');

  (async () => {
    const ready = await pollHealth();
    if (ready) {
      dispatch('online');
      log('info', 'Backend online');

      // Fetch initial Emrys field report
      await emrysFieldReport();

      // Start Emrys L2 steady-state poll
      startEmrysL2Poll();

      // Steady-state health poll every 30 s
      setInterval(async () => {
        try {
          const res = await fetch(HEALTH_URL, { signal: AbortSignal.timeout(2000) });
          dispatch(res.ok ? 'online' : 'offline');
        } catch {
          dispatch('offline');
        }
      }, RETRY_INTERVAL);
      return;
    }
    // Backend never came up
    dispatch('offline');
    log('error', 'Backend offline — start the Python server with: uvicorn main:app --port 8008');
  })();

  return Promise.resolve();
}

// ─────────────────────────────────────────────────────────────
// getBackendStatus — web version (unchanged)
// ─────────────────────────────────────────────────────────────

/**
 * getBackendStatus — web version.
 * Returns 'online' or 'offline' based on a live health probe.
 */
export async function getBackendStatus(): Promise<string> {
  try {
    const res = await fetch(HEALTH_URL, { signal: AbortSignal.timeout(2000) });
    return res.ok ? 'online' : 'offline';
  } catch {
    return 'offline';
  }
}

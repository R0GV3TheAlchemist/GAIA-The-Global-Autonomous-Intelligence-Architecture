/**
 * GaianHome.ts — Issue #80
 * The primary Home screen — GAIA's living room.
 *
 * Layout:
 *   ┌──────────────────────────────────────────────────┐
 *   │  [profile card: name · archetype · relationship age]        │
 *   │                                                              │
 *   │              [GaianOrb canvas]                               │
 *   │           [mood label beneath orb]                          │
 *   │                                                              │
 *   │  "Good morning, Kyle. The room feels quiet."                │
 *   │  [daily brief line]                                         │
 *   │                                                              │
 *   │  [recent memories: last 3 entries]                          │
 *   │                                                              │
 *   │  [ Chat ] [ Memory ] [ Search ] [ Shell ]                    │
 *   └──────────────────────────────────────────────────┘
 *
 * Long-press on the orb (600 ms hold) opens CrystalView — a bottom sheet
 * showing GAIA's live Ψ coherence state.  The gesture is detected here
 * (per the CrystalView contract) and CrystalView is mounted imperatively
 * via ReactDOM.createRoot into a portal host div.
 */

import { GaianOrb }          from './GaianOrb';
import { HomeBackground }    from './HomeBackground';
import { buildGreeting, fetchMemoryHint } from './GaianGreeting';
import { gaianMood, MOOD_PROFILES } from './GaianMood';
import type { GaianMoodState } from './GaianMood';
import { API_BASE }          from '../config';
import type { CrystalState } from '../hooks/useCrystalCore';

// React + ReactDOM are loaded as globals at runtime via CDN (same pattern
// as THREE / gsap in GaianOrb.ts).
declare const React:     typeof import('react');
declare const ReactDOM:  typeof import('react-dom/client');

// CrystalView is a React component — imported for its type; the actual
// module is resolved by the bundler at build time.
import { CrystalView } from './CrystalView';

export type HomeNavTarget = 'chat' | 'memory' | 'search' | 'shell';

export interface GaianHomeOptions {
  container: HTMLElement;
  onNavigate: (target: HomeNavTarget) => void;
}

// ── Constants ────────────────────────────────────────────────────────────────

/** Hold duration before the CrystalView sheet opens (ms). */
const LONG_PRESS_MS = 600;

/** Sidecar endpoint for the latest CrystalState. */
const CRYSTAL_STATE_URL = 'http://localhost:8008/crystal/state';

// Session-level daily brief cache — generated once per session
let _sessionBrief: string | null = null;

// ── Name / archetype / age helpers ──────────────────────────────────────────

/** Read the user's name from the best available source (no fallback to stub) */
function resolveNameSync(): string | undefined {
  try {
    if (window.__gaiaUserName) return window.__gaiaUserName;
  } catch { /* noop */ }
  return undefined;
}

/** Async name resolution: falls back to /memory/list explicit source */
async function resolveNameAsync(): Promise<string | undefined> {
  const sync = resolveNameSync();
  if (sync) return sync;
  try {
    const res = await fetch(`${API_BASE}/memory/list`, {
      signal: AbortSignal.timeout(2000),
    });
    if (!res.ok) return undefined;
    const entries: Array<{ content: string; source: string }> = await res.json();
    const nameEntry = entries.find(e =>
      e.source === 'explicit' &&
      /^(my name is|i am|call me)/i.test(e.content)
    );
    if (nameEntry) {
      const match = nameEntry.content.match(/(?:my name is|i am|call me)\s+(\w+)/i);
      if (match?.[1]) {
        window.__gaiaUserName = match[1];
        return match[1];
      }
    }
  } catch { /* offline — silently degrade */ }
  return undefined;
}

/** Archetype name — read from memory or return default */
async function resolveArchetype(): Promise<string> {
  try {
    const res = await fetch(`${API_BASE}/memory/list`, {
      signal: AbortSignal.timeout(2000),
    });
    if (!res.ok) return 'Gaian';
    const entries: Array<{ content: string; source: string }> = await res.json();
    const archetypeEntry = entries.find(e =>
      e.source === 'system' && /archetype/i.test(e.content)
    );
    if (archetypeEntry) {
      const match = archetypeEntry.content.match(/archetype[:\s]+([\w\s]+)/i);
      if (match?.[1]) return match[1].trim();
    }
  } catch { /* offline */ }
  return 'Sovereign';
}

/** Days since first onboarding (relationship age) */
function resolveRelationshipAge(): number {
  try {
    const raw = (window as any).__gaiaStartedAt as string | undefined;
    if (raw) {
      const ms = Date.now() - new Date(raw).getTime();
      return Math.max(0, Math.floor(ms / 86_400_000));
    }
  } catch { /* noop */ }
  return 0;
}

/** Fetch recent memories (last 3) */
async function fetchRecentMemories(): Promise<Array<{ id: string; content: string; created_at: string }>> {
  try {
    const res = await fetch(`${API_BASE}/memory/list`, {
      signal: AbortSignal.timeout(2500),
    });
    if (!res.ok) return [];
    const entries: Array<{ id: string; content: string; created_at: string; active: boolean }> =
      await res.json();
    return entries
      .filter(e => e.active !== false)
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 3);
  } catch {
    return [];
  }
}

/** Fetch current affect/mood from backend */
async function fetchAffectMood(): Promise<GaianMoodState | null> {
  try {
    const res = await fetch(`${API_BASE}/affect/trend`, {
      signal: AbortSignal.timeout(2000),
    });
    if (!res.ok) return null;
    const data: { dominant_mood?: string } = await res.json();
    const m = data.dominant_mood?.toLowerCase() as GaianMoodState | undefined;
    const valid: GaianMoodState[] = ['calm', 'curious', 'alert', 'joyful', 'reflective'];
    return m && valid.includes(m) ? m : null;
  } catch {
    return null;
  }
}

/** Generate a one-sentence daily brief from GAIA */
async function fetchDailyBrief(name?: string): Promise<string | null> {
  if (_sessionBrief !== null) return _sessionBrief;
  try {
    const prompt = name
      ? `In one sentence, give ${name} a grounding thought or gentle intention for today. No greeting. Just the thought.`
      : 'In one sentence, offer a grounding thought or gentle intention for today. No greeting.';
    const res = await fetch(`${API_BASE}/chat`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ message: prompt, stream: false }),
      signal:  AbortSignal.timeout(8000),
    });
    if (!res.ok) return null;
    const data: { response?: string; content?: string } = await res.json();
    const brief = (data.response ?? data.content ?? '').trim();
    if (brief) { _sessionBrief = brief; return brief; }
    return null;
  } catch {
    return null;
  }
}

// ── GaianHome ────────────────────────────────────────────────────────────────

export class GaianHome {
  private container:  HTMLElement;
  private orb:        GaianOrb | null = null;
  private bg:         HomeBackground | null = null;
  private onNavigate: (target: HomeNavTarget) => void;
  private _greetingRefresh: number | null = null;
  private _moodUnlisten:    (() => void) | null = null;

  // ── Crystal / long-press state ──────────────────────────────────────────
  /** Last successfully fetched CrystalState — used as fallback when offline. */
  private _crystalState: CrystalState | null = null;

  /** React root for the CrystalView portal. Created once on first open. */
  private _crystalRoot: ReturnType<typeof ReactDOM.createRoot> | null = null;

  /** Host element that holds the CrystalView portal. */
  private _crystalHost: HTMLDivElement | null = null;

  /** Whether the sheet is currently open. */
  private _crystalOpen = false;

  /** Long-press timer handle. */
  private _lpTimer: number | null = null;

  /** Cleanup refs for orb-level event listeners. */
  private _lpCleanup: (() => void) | null = null;

  constructor({ container, onNavigate }: GaianHomeOptions) {
    this.container  = container;
    this.onNavigate = onNavigate;
    this._render();
  }

  // ── Render ──────────────────────────────────────────────────────────────

  private _render(): void {
    this.container.innerHTML = '';
    this.container.className = 'gaian-home';

    // ── Background
    this.bg = new HomeBackground(this.container);

    // ── Profile card (rendered immediately with placeholders, hydrated async)
    const profileCard = document.createElement('div');
    profileCard.className = 'home-profile-card';
    profileCard.setAttribute('aria-label', 'Your Gaian profile');
    profileCard.innerHTML = `
      <div class="profile-name" aria-label="Gaian name">—</div>
      <div class="profile-meta">
        <span class="profile-archetype" aria-label="Archetype">…</span>
        <span class="profile-sep" aria-hidden="true">·</span>
        <span class="profile-age" aria-label="Relationship age">0 days</span>
      </div>
    `;
    this.container.appendChild(profileCard);

    // ── Orb wrapper + canvas
    const orbWrap = document.createElement('div');
    orbWrap.className = 'home-orb-wrap';
    // Make focusable so keyboard users can trigger the long-press hint
    orbWrap.setAttribute('role', 'button');
    orbWrap.setAttribute('tabindex', '0');
    orbWrap.setAttribute('aria-label', 'GAIA orb — hold to view coherence state');
    const canvas = document.createElement('canvas');
    canvas.className = 'home-orb-canvas';
    canvas.setAttribute('aria-label', 'GAIA — Living Earth avatar');
    orbWrap.appendChild(canvas);
    this.container.appendChild(orbWrap);

    // ── Mood label (beneath orb)
    const moodLabel = document.createElement('p');
    moodLabel.className = 'home-mood-label';
    moodLabel.setAttribute('aria-live', 'polite');
    moodLabel.textContent = '';
    this.container.appendChild(moodLabel);

    // ── Greeting
    const greetingEl = document.createElement('p');
    greetingEl.className = 'home-greeting';
    greetingEl.textContent = buildGreeting(resolveNameSync());
    this.container.appendChild(greetingEl);

    // ── Daily brief
    const briefEl = document.createElement('p');
    briefEl.className = 'home-brief';
    briefEl.setAttribute('aria-live', 'polite');
    briefEl.textContent = '';
    this.container.appendChild(briefEl);

    // ── Recent memories
    const memoriesWrap = document.createElement('div');
    memoriesWrap.className = 'home-memories';
    memoriesWrap.setAttribute('aria-label', 'Recent memories');
    memoriesWrap.innerHTML = `<div class="memories-placeholder">Recalling…</div>`;
    this.container.appendChild(memoriesWrap);

    // ── Bottom dock
    const dock = document.createElement('nav');
    dock.className = 'home-dock';
    dock.setAttribute('aria-label', 'GAIA navigation');
    const dockItems: { id: HomeNavTarget; label: string; icon: string }[] = [
      { id: 'chat',   label: 'Chat',   icon: '\u25c6' },
      { id: 'memory', label: 'Memory', icon: '\u2606' },
      { id: 'search', label: 'Search', icon: '\u2318' },
      { id: 'shell',  label: 'Shell',  icon: '\u276f' },
    ];
    dockItems.forEach(({ id, label, icon }) => {
      const btn = document.createElement('button');
      btn.className  = 'home-dock-btn';
      btn.dataset.nav = id;
      btn.setAttribute('aria-label', label);
      btn.innerHTML  = `<span class="dock-icon" aria-hidden="true">${icon}</span><span class="dock-label">${label}</span>`;
      btn.addEventListener('click', () => {
        this.onNavigate(id);
        this._setActiveDock(id);
      });
      dock.appendChild(btn);
    });
    this.container.appendChild(dock);

    // ── Loading badge (backend health)
    const loadingBadge = document.createElement('div');
    loadingBadge.className = 'home-loading-badge';
    loadingBadge.textContent = 'Connecting to GAIA…';
    loadingBadge.setAttribute('aria-live', 'polite');
    this.container.appendChild(loadingBadge);

    // ── Refresh greeting every minute
    this._greetingRefresh = window.setInterval(async () => {
      const name = resolveNameSync();
      greetingEl.textContent = buildGreeting(name);
    }, 60_000);

    // ── Poll health until model ready
    this._pollHealth(loadingBadge);

    // ── Init GaianOrb after DOM is painted
    requestAnimationFrame(() => {
      this.orb = new GaianOrb(canvas);
      this.orb.start();

      // Sync orb with global gaianMood singleton
      this._moodUnlisten = gaianMood.onChange((mood) => {
        this.orb?.setMood(mood);
        this._updateMoodLabel(moodLabel, mood);
        this._applyDockAccent(dock, mood);
      });

      // Wire long-press gesture
      this._wireLongPress(orbWrap);
    });

    // ── Async hydration (non-blocking)
    this._hydrateAsync(profileCard, greetingEl, briefEl, memoriesWrap, moodLabel, dock);
  }

  // ── Long-press gesture ──────────────────────────────────────────────────

  /**
   * Attaches pointer + touch listeners to `orbWrap`.
   * After LONG_PRESS_MS of uninterrupted contact the CrystalView opens.
   * A subtle ripple class is added to the canvas during the hold phase to
   * give the user visual confirmation the gesture is registering.
   */
  private _wireLongPress(orbWrap: HTMLElement): void {
    const canvas = orbWrap.querySelector<HTMLCanvasElement>('.home-orb-canvas');

    const startHold = () => {
      if (this._lpTimer !== null) return; // already counting
      canvas?.classList.add('orb-long-press-active');
      this._lpTimer = window.setTimeout(() => {
        this._lpTimer = null;
        canvas?.classList.remove('orb-long-press-active');
        this._openCrystalView();
      }, LONG_PRESS_MS);
    };

    const cancelHold = () => {
      if (this._lpTimer !== null) {
        clearTimeout(this._lpTimer);
        this._lpTimer = null;
      }
      canvas?.classList.remove('orb-long-press-active');
    };

    // Pointer events (desktop + stylus + most modern mobile)
    const onPointerDown = (e: PointerEvent) => {
      // Only primary button / single touch
      if (e.button !== 0 && e.pointerType === 'mouse') return;
      startHold();
    };
    const onPointerUp    = () => cancelHold();
    const onPointerMove  = (e: PointerEvent) => {
      // Cancel if the pointer drifts more than 10px (scroll intent)
      if (Math.abs(e.movementX) > 10 || Math.abs(e.movementY) > 10) cancelHold();
    };
    const onPointerLeave = () => cancelHold();

    // Touch events fallback (older iOS / Android WebView)
    const onTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 1) startHold();
    };
    const onTouchEnd    = () => cancelHold();
    const onTouchMove   = () => cancelHold();

    // Keyboard accessibility: Enter / Space triggers the sheet immediately
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this._openCrystalView();
      }
    };

    orbWrap.addEventListener('pointerdown',  onPointerDown);
    orbWrap.addEventListener('pointerup',    onPointerUp);
    orbWrap.addEventListener('pointermove',  onPointerMove);
    orbWrap.addEventListener('pointerleave', onPointerLeave);
    orbWrap.addEventListener('touchstart',   onTouchStart,  { passive: true });
    orbWrap.addEventListener('touchend',     onTouchEnd);
    orbWrap.addEventListener('touchmove',    onTouchMove,   { passive: true });
    orbWrap.addEventListener('keydown',      onKeyDown);

    // Prevent the context menu appearing on long-press on mobile
    orbWrap.addEventListener('contextmenu', (e) => e.preventDefault());

    this._lpCleanup = () => {
      orbWrap.removeEventListener('pointerdown',  onPointerDown);
      orbWrap.removeEventListener('pointerup',    onPointerUp);
      orbWrap.removeEventListener('pointermove',  onPointerMove);
      orbWrap.removeEventListener('pointerleave', onPointerLeave);
      orbWrap.removeEventListener('touchstart',   onTouchStart);
      orbWrap.removeEventListener('touchend',     onTouchEnd);
      orbWrap.removeEventListener('touchmove',    onTouchMove);
      orbWrap.removeEventListener('keydown',      onKeyDown);
    };
  }

  // ── CrystalView portal ──────────────────────────────────────────────────

  /**
   * Fetches the latest CrystalState (best-effort, 3 s timeout), then
   * mounts the CrystalView React component into a portal host element
   * appended to .gaian-home.  Falls back to the last cached state if
   * the sidecar is unavailable.
   */
  private async _openCrystalView(): Promise<void> {
    if (this._crystalOpen) return;

    // Fetch latest state (non-blocking race — show whatever we have)
    try {
      const res = await fetch(CRYSTAL_STATE_URL, {
        signal: AbortSignal.timeout(3000),
      });
      if (res.ok) {
        const data = (await res.json()) as CrystalState;
        this._crystalState = data;
        // Also drive the orb with fresh params while we're here
        if (this.orb && data.orb_params) this.orb.setParams(data.orb_params);
      }
    } catch {
      // Offline — use last known state (or null → CrystalView handles it)
    }

    // Create the host div the first time
    if (!this._crystalHost) {
      const host = document.createElement('div');
      host.className = 'crystal-view-portal';
      this.container.appendChild(host);
      this._crystalHost = host;
    }

    // Create the React root the first time
    if (!this._crystalRoot) {
      this._crystalRoot = ReactDOM.createRoot(this._crystalHost);
    }

    this._crystalOpen = true;
    this._renderCrystalView();
  }

  private _closeCrystalView(): void {
    if (!this._crystalOpen) return;
    this._crystalOpen = false;
    // Render null to trigger CrystalView's exit animation (handled in CSS)
    // then unmount after the transition completes (~320 ms)
    this._crystalRoot?.render(null);
    window.setTimeout(() => {
      if (!this._crystalOpen) {
        this._crystalRoot?.unmount();
        this._crystalRoot = null;
        this._crystalHost?.remove();
        this._crystalHost = null;
      }
    }, 350);
  }

  private _renderCrystalView(): void {
    if (!this._crystalRoot) return;
    this._crystalRoot.render(
      React.createElement(CrystalView, {
        state:   this._crystalState,
        onClose: () => this._closeCrystalView(),
      })
    );
  }

  // ── Async hydration ─────────────────────────────────────────────────────

  /** All async data fetches happen here — failures degrade gracefully */
  private async _hydrateAsync(
    profileCard:  HTMLElement,
    greetingEl:   HTMLElement,
    briefEl:      HTMLElement,
    memoriesWrap: HTMLElement,
    moodLabel:    HTMLElement,
    dock:         HTMLElement,
  ): Promise<void> {
    // 1. Name (async — may read from /memory/list)
    const name = await resolveNameAsync();
    if (name) {
      greetingEl.textContent = buildGreeting(name);
      profileCard.querySelector<HTMLElement>('.profile-name')!.textContent = name;
    } else {
      profileCard.querySelector<HTMLElement>('.profile-name')!.textContent = 'Gaian';
    }

    // 2. Memory hint appended to greeting
    fetchMemoryHint().then(hint => {
      if (hint && greetingEl.textContent) {
        greetingEl.textContent += ` ${hint}`;
      }
    });

    // 3. Archetype
    resolveArchetype().then(archetype => {
      profileCard.querySelector<HTMLElement>('.profile-archetype')!.textContent = archetype;
    });

    // 4. Relationship age
    const ageDays = resolveRelationshipAge();
    profileCard.querySelector<HTMLElement>('.profile-age')!.textContent =
      ageDays === 0 ? 'Just born' : `${ageDays} day${ageDays === 1 ? '' : 's'} together`;

    // 5. Recent memories
    const memories = await fetchRecentMemories();
    memoriesWrap.innerHTML = '';
    if (memories.length === 0) {
      memoriesWrap.innerHTML = `<p class="memories-empty">No memories yet. I'm still learning you.</p>`;
    } else {
      memories.forEach(m => {
        const item = document.createElement('button');
        item.className = 'memory-chip';
        item.setAttribute('aria-label', `Memory: ${m.content.slice(0, 80)}`);
        item.textContent = m.content.length > 72
          ? m.content.slice(0, 69) + '…'
          : m.content;
        item.addEventListener('click', () => {
          (this.onNavigate as any)('memory');
        });
        memoriesWrap.appendChild(item);
      });
    }

    // 6. Affect mood
    const mood = await fetchAffectMood();
    if (mood) {
      gaianMood.set(mood);
      this._updateMoodLabel(moodLabel, mood);
      this._applyDockAccent(dock, mood);
    }

    // 7. Daily brief (last — can take a few seconds)
    const brief = await fetchDailyBrief(name);
    if (brief) {
      briefEl.textContent = brief;
      briefEl.classList.add('visible');
    }
  }

  // ── Helpers ─────────────────────────────────────────────────────────────

  private _updateMoodLabel(el: HTMLElement, mood: GaianMoodState): void {
    const LABELS: Record<GaianMoodState, string> = {
      calm:        'Feeling calm',
      curious:     'Feeling curious',
      alert:       'Feeling alert',
      joyful:      'Feeling joyful',
      reflective:  'Feeling reflective',
    };
    el.textContent = LABELS[mood] ?? '';
  }

  private _applyDockAccent(dock: HTMLElement, mood: GaianMoodState): void {
    const color = MOOD_PROFILES[mood]?.glowColor ?? '#1a7a5e';
    dock.style.setProperty('--dock-accent', color);
  }

  private async _pollHealth(badge: HTMLElement): Promise<void> {
    const MAX_TRIES = 60;
    let tries = 0;
    const check = async () => {
      try {
        const res  = await fetch(`${API_BASE}/health`);
        const data = await res.json();
        if (data.model_ready) {
          badge.textContent = '';
          badge.classList.add('ready');
          badge.remove();
          gaianMood.set('calm');
          return;
        }
        badge.textContent = data.error
          ? `⦻ ${data.error}`
          : 'GAIA is waking up…';
      } catch {
        badge.textContent = 'Waiting for backend…';
      }
      tries++;
      if (tries < MAX_TRIES) setTimeout(check, 2000);
      else badge.textContent = 'Backend unavailable — some features offline.';
    };
    check();
  }

  private _setActiveDock(id: HomeNavTarget): void {
    this.container.querySelectorAll<HTMLButtonElement>('.home-dock-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.nav === id);
    });
  }

  // ── Lifecycle ────────────────────────────────────────────────────────────

  dispose(): void {
    // Cancel any in-flight long-press timer
    if (this._lpTimer !== null) {
      clearTimeout(this._lpTimer);
      this._lpTimer = null;
    }
    // Remove orb gesture listeners
    this._lpCleanup?.();

    // Tear down the CrystalView portal
    this._crystalRoot?.unmount();
    this._crystalHost?.remove();
    this._crystalRoot = null;
    this._crystalHost = null;

    this.orb?.dispose();
    this.bg?.dispose();
    this._moodUnlisten?.();
    if (this._greetingRefresh !== null) clearInterval(this._greetingRefresh);
  }
}

/** Global stubs — set externally once memory layer is live */
declare global {
  interface Window {
    __gaiaUserName?: string;
    __gaiaStartedAt?: string;
  }
}

export function mountGaianHome(
  container: HTMLElement,
  onNavigate: (target: HomeNavTarget) => void,
): GaianHome {
  return new GaianHome({ container, onNavigate });
}

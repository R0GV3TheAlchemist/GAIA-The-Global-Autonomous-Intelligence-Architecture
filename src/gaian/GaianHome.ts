/**
 * GaianHome.ts — Issue #80
 * The primary Home screen — GAIA’s living room.
 *
 * Layout:
 *   ┌──────────────────────────────────────────────────┐
 *   │  [profile card: name · archetype · relationship age]        │
 *   │                                                              │
 *   │              [GaianOrb canvas]                               │
 *   │           [mood label beneath orb]                          │
 *   │                                                              │
 *   │  “Good morning, Kyle. The room feels quiet.”                │
 *   │  [daily brief line]                                         │
 *   │                                                              │
 *   │  [recent memories: last 3 entries]                          │
 *   │                                                              │
 *   │  [ Chat ] [ Memory ] [ Search ] [ Shell ]                    │
 *   └──────────────────────────────────────────────────┘
 */

import { GaianOrb }          from './GaianOrb';
import { HomeBackground }    from './HomeBackground';
import { buildGreeting, fetchMemoryHint } from './GaianGreeting';
import { gaianMood, MOOD_PROFILES } from './GaianMood';
import type { GaianMoodState } from './GaianMood';
import { API_BASE }          from '../config';

export type HomeNavTarget = 'chat' | 'memory' | 'search' | 'shell';

export interface GaianHomeOptions {
  container: HTMLElement;
  onNavigate: (target: HomeNavTarget) => void;
}

// Session-level daily brief cache — generated once per session
let _sessionBrief: string | null = null;

/** Read the user’s name from the best available source (no fallback to stub) */
function resolveNameSync(): string | undefined {
  try {
    // 1. Onboarding store (most reliable — set during Phase 3)
    // Dynamic import would be async, so we access the global Zustand store
    // via the window proxy set in app.ts after onboarding completes.
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

export class GaianHome {
  private container:  HTMLElement;
  private orb:        GaianOrb | null = null;
  private bg:         HomeBackground | null = null;
  private onNavigate: (target: HomeNavTarget) => void;
  private _greetingRefresh: number | null = null;
  private _moodUnlisten:    (() => void) | null = null;

  constructor({ container, onNavigate }: GaianHomeOptions) {
    this.container  = container;
    this.onNavigate = onNavigate;
    this._render();
  }

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
    });

    // ── Async hydration (non-blocking)
    this._hydrateAsync(profileCard, greetingEl, briefEl, memoriesWrap, moodLabel, dock);
  }

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
      memoriesWrap.innerHTML = `<p class="memories-empty">No memories yet. I’m still learning you.</p>`;
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

  dispose(): void {
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

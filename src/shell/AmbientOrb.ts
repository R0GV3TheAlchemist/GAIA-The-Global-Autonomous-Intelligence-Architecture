/**
 * AmbientOrb.ts — P4 Shell Mode
 * GAIA as an always-on floating desktop presence.
 * Transparent 120×120 orb, draggable, click to expand, right-click context menu.
 *
 * Mode-reactive animation system:
 *   AmbientOrb listens for Tauri 'gaia:mode' events emitted by the main window
 *   (GaiaShell broadcasts these whenever useGaiaMode changes state).
 *   The mode is applied as data-mode="..." on both #ambient-orb AND
 *   document.documentElement (:root), which drives all CSS colour tokens
 *   and keyframe animations in ambient.html.
 *
 *   Modes: resting | listening | thinking | speaking | offline
 *
 * Particle system:
 *   12 micro-particles orbit the orb in a biophotonic halo.
 *   Particle colour is mode-tinted and rendered on #orb-canvas.
 *
 * IPC pattern (no Rust command needed):
 *   openMain(section) shows + focuses the main WebviewWindow, then calls
 *   mainWindow.emit('gaia:navigate', { section }).
 *   GaiaShell.tsx listens via listen('gaia:navigate', ...) from @tauri-apps/api/event.
 *
 * Mode broadcast from GaiaShell (wired in feat(shell): broadcast gaia:mode):
 *   import { emit } from '@tauri-apps/api/event';
 *   useEffect(() => { emit('gaia:mode', { mode: gaiaMode }).catch(() => {}); }, [gaiaMode]);
 *
 * Long-press (500 ms) → opens Emrys L2 panel in the main window.
 * Drag-safe: pointer movement > 6 px cancels the timer.
 */

import { getCurrentWindow }             from '@tauri-apps/api/window';
import { WebviewWindow }                from '@tauri-apps/api/webviewWindow';
import { PhysicalPosition }             from '@tauri-apps/api/dpi';
import { invoke }                       from '@tauri-apps/api/core';
import { listen }                       from '@tauri-apps/api/event';
import { Menu, MenuItem }               from '@tauri-apps/api/menu';
import { writeTextFile, BaseDirectory } from '@tauri-apps/plugin-fs';

const POSITION_FILE      = 'GAIA/ambient-position.json';
const LONG_PRESS_MS      = 500;
const LONG_PRESS_MOVE_PX = 6;

// ── Mode types ──────────────────────────────────────────────────────────────────────

export type GaiaMode = 'resting' | 'listening' | 'thinking' | 'speaking' | 'offline';

const VALID_MODES = new Set<GaiaMode>(['resting', 'listening', 'thinking', 'speaking', 'offline']);

function isGaiaMode(v: unknown): v is GaiaMode {
  return typeof v === 'string' && VALID_MODES.has(v as GaiaMode);
}

// Particle colours per mode — RGB triplets (alpha set per-draw)
const MODE_PARTICLE_COLORS: Record<GaiaMode, [number, number, number][]> = {
  resting:   [[155, 109, 219], [180, 143, 232], [100,  60, 180]],   // amethyst
  listening: [[ 79, 152, 163], [100, 220, 200], [ 30, 120, 140]],   // teal
  thinking:  [[180, 143, 232], [200, 160, 255], [110,  50, 210]],   // amethyst bright
  speaking:  [[232, 175,  52], [255, 220, 100], [200, 130,  20]],   // gold
  offline:   [[ 80,  80, 100], [100, 100, 120], [ 50,  50,  70]],   // grey
};

// ── Particle system ──────────────────────────────────────────────────────────────────

const PARTICLE_COUNT = 12;
const ORB_CX         = 60;  // canvas centre x
const ORB_CY         = 60;  // canvas centre y
const ORB_RADIUS     = 44;  // particle orbit radius

interface OrbParticle {
  angle:        number;
  speed:        number;
  orbitR:       number;
  size:         number;
  alpha:        number;
  twinklePhase: number;
  twinkleSpeed: number;
  colorIdx:     number;
}

function createParticles(): OrbParticle[] {
  return Array.from({ length: PARTICLE_COUNT }, (_, i) => ({
    angle:        (i / PARTICLE_COUNT) * Math.PI * 2,
    speed:        0.006 + Math.random() * 0.006,
    orbitR:       ORB_RADIUS + (Math.random() - 0.5) * 14,
    size:         0.8 + Math.random() * 1.4,
    alpha:        0.3 + Math.random() * 0.5,
    twinklePhase: Math.random() * Math.PI * 2,
    twinkleSpeed: 0.025 + Math.random() * 0.025,
    colorIdx:     i % 3,
  }));
}

// ── AmbientOrb class ────────────────────────────────────────────────────────────────

export class AmbientOrb {
  private window:     ReturnType<typeof getCurrentWindow>;
  private isDragging: boolean = false;
  private orbEl:      HTMLElement | null = null;
  private canvasEl:   HTMLCanvasElement | null = null;
  private ctx:        CanvasRenderingContext2D | null = null;

  // Mode state
  private currentMode:  GaiaMode = 'resting';
  private particles:    OrbParticle[] = [];
  private rafId:        number = 0;
  private tick:         number = 0;

  // Tauri event unlisten handle — stored so destroy() can clean up
  private unlistenMode: (() => void) | null = null;

  // Long-press state
  private _lpTimer:  ReturnType<typeof setTimeout> | null = null;
  private _lpStartX: number = 0;
  private _lpStartY: number = 0;

  constructor() {
    this.window = getCurrentWindow();
  }

  async init(): Promise<void> {
    await this.restorePosition();

    this.orbEl    = document.getElementById('ambient-orb');
    this.canvasEl = document.getElementById('orb-canvas') as HTMLCanvasElement | null;
    if (!this.orbEl) {
      console.error('[AmbientOrb] #ambient-orb not found in DOM.');
      return;
    }

    if (this.canvasEl) {
      this.ctx = this.canvasEl.getContext('2d');
    }

    this.particles = createParticles();

    this.bindDrag();
    this.bindClick();
    this.bindKeyboard();
    this.bindLongPress();
    await this.bindContextMenu();
    await this.bindModeEvents();    // await so unlisten is stored before any event arrives
    this.startPulse();
    this.startParticleLoop();

    console.info(`[AmbientOrb] ready — mode: ${this.currentMode}`);
  }

  // ── Public mode setter ────────────────────────────────────────────────────────────

  setMode(mode: GaiaMode): void {
    if (mode === this.currentMode) return;
    this.currentMode = mode;

    if (this.orbEl) {
      // Apply to orb element directly (catches #ambient-orb[data-mode] selectors)
      this.orbEl.setAttribute('data-mode', mode);

      // Flash a brief transition class for the cross-dissolve
      this.orbEl.classList.add('orb-mode-change');
      setTimeout(() => this.orbEl?.classList.remove('orb-mode-change'), 160);
    }

    // Apply to :root (catches :root[data-mode] / [data-mode] on html element)
    document.documentElement.setAttribute('data-mode', mode);
  }

  // ── Tauri 'gaia:mode' event listener ──────────────────────────────────────────
  //
  // GaiaShell emits: emit('gaia:mode', { mode: gaiaMode })
  // Tauri broadcast reaches all webview windows including this one.
  // unlisten is stored on the instance for cleanup in destroy().
  //
  private async bindModeEvents(): Promise<void> {
    try {
      this.unlistenMode = await listen<{ mode: unknown }>('gaia:mode', (event) => {
        const m = event.payload?.mode;
        if (isGaiaMode(m)) {
          this.setMode(m);
        } else {
          console.warn(`[AmbientOrb] received unknown mode: ${String(m)}`);
        }
      });
    } catch {
      // Non-Tauri / browser dev environment — silently degrade.
      // Mode can still be driven manually via setMode() or DOM attribute.
      console.info('[AmbientOrb] Tauri event API unavailable — running in browser mode.');
    }
  }

  // ── Drag ────────────────────────────────────────────────────────────────────────

  private bindDrag(): void {
    if (!this.orbEl) return;

    this.orbEl.addEventListener('mousedown', (e: MouseEvent) => {
      if (e.button !== 0) return;
      this.isDragging = true;
      this.window.startDragging();
    });

    window.addEventListener('mouseup', async () => {
      if (!this.isDragging) return;
      this.isDragging = false;
      await this.savePosition();
    });
  }

  private async savePosition(): Promise<void> {
    try {
      const pos  = await this.window.outerPosition();
      const data = JSON.stringify({ x: pos.x, y: pos.y });
      await writeTextFile(POSITION_FILE, data, { baseDir: BaseDirectory.LocalData });
    } catch (err) {
      console.warn('[AmbientOrb] Failed to save position:', err);
    }
  }

  private async restorePosition(): Promise<void> {
    try {
      const saved = await invoke<string>('load_ambient_position');
      if (saved) {
        const { x, y } = JSON.parse(saved);
        await this.window.setPosition(new PhysicalPosition(x, y));
      }
    } catch {
      // No saved position — default placement is fine
    }
  }

  // ── Click ──────────────────────────────────────────────────────────────────────────

  private bindClick(): void {
    if (!this.orbEl) return;

    this.orbEl.addEventListener('click', async (e: MouseEvent) => {
      if (e.button !== 0) return;
      await this.openMain('ask');
    });
  }

  // ── Keyboard accessibility (Enter / Space → click) ────────────────────────────
  //
  // The orb has role="button" and tabindex="0" in the HTML.
  // Without this handler, keyboard users can tab to it but Enter/Space do nothing.
  //
  private bindKeyboard(): void {
    if (!this.orbEl) return;

    this.orbEl.addEventListener('keydown', async (e: KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        await this.openMain('ask');
      }
    });
  }

  // ── Long-press ─────────────────────────────────────────────────────────────────────

  private bindLongPress(): void {
    if (!this.orbEl) return;
    const el = this.orbEl;

    const cancelLP = () => {
      if (this._lpTimer !== null) {
        clearTimeout(this._lpTimer);
        this._lpTimer = null;
      }
      el.classList.remove('ambient-orb--pressing');
    };

    el.addEventListener('pointerdown', (e: PointerEvent) => {
      if (e.button !== 0) return;
      cancelLP();
      this._lpStartX = e.clientX;
      this._lpStartY = e.clientY;
      el.classList.add('ambient-orb--pressing');

      this._lpTimer = setTimeout(() => {
        this._lpTimer = null;
        el.classList.remove('ambient-orb--pressing');
        this.openMain('emrys').catch(console.error);
      }, LONG_PRESS_MS);
    });

    el.addEventListener('pointermove', (e: PointerEvent) => {
      if (this._lpTimer === null) return;
      const dx = e.clientX - this._lpStartX;
      const dy = e.clientY - this._lpStartY;
      if (Math.sqrt(dx * dx + dy * dy) > LONG_PRESS_MOVE_PX) cancelLP();
    });

    el.addEventListener('pointerup',     cancelLP);
    el.addEventListener('pointercancel', cancelLP);
  }

  // ── Right-click context menu ──────────────────────────────────────────────────

  private async bindContextMenu(): Promise<void> {
    if (!this.orbEl) return;

    const menu = await Menu.new({
      items: [
        await MenuItem.new({ text: '⚡ Emrys L2', action: () => this.openMain('emrys') }),
        await MenuItem.new({ text: '💬 Chat',     action: () => this.openMain('chat') }),
        await MenuItem.new({ text: '🧠 Memory',   action: () => this.openMain('memory') }),
        await MenuItem.new({ text: '⚙️ Settings', action: () => this.openMain('settings') }),
        await MenuItem.new({ text: '✖ Quit GAIA', action: () => invoke('quit_app') }),
      ],
    });

    this.orbEl.addEventListener('contextmenu', async (e: MouseEvent) => {
      e.preventDefault();
      await menu.popup();
    });
  }

  // ── openMain ────────────────────────────────────────────────────────────────────

  private async openMain(section: string): Promise<void> {
    try {
      const mainWindow = new WebviewWindow('main');
      await mainWindow.show();
      await mainWindow.setFocus();
      await mainWindow.emit('gaia:navigate', { section });
    } catch (err) {
      console.error('[AmbientOrb] openMain failed:', err);
    }
  }

  // ── Ambient pulse (CSS class) ──────────────────────────────────────────────────
  //
  // Kept for backwards compatibility. All real animation now runs via
  // data-mode CSS tokens. ambient-pulse class is additive but harmless.
  //
  private startPulse(): void {
    if (!this.orbEl) return;
    this.orbEl.classList.add('ambient-pulse');
  }

  // ── Particle canvas loop ────────────────────────────────────────────────────────
  //
  // 12 micro-particles orbit the orb centre in a biophotonic halo.
  // Particle colour is tinted by current mode via MODE_PARTICLE_COLORS.
  // Canvas is clipped to the orb circle by CSS clip-path in ambient.html.
  //
  private startParticleLoop(): void {
    if (!this.ctx || !this.canvasEl) return;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reducedMotion) return;

    const loop = () => {
      this.tick++;
      const ctx    = this.ctx!;
      const colors = MODE_PARTICLE_COLORS[this.currentMode];

      ctx.clearRect(0, 0, 120, 120);

      for (const p of this.particles) {
        p.angle += p.speed;

        const tw        = 0.25 + 0.55 * (0.5 + 0.5 * Math.sin(this.tick * p.twinkleSpeed + p.twinklePhase));
        const x         = ORB_CX + p.orbitR * Math.cos(p.angle);
        const y         = ORB_CY + p.orbitR * Math.sin(p.angle);
        const [r, g, b] = colors[p.colorIdx % colors.length];

        ctx.beginPath();
        ctx.arc(x, y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${r},${g},${b},${(tw * 0.75).toFixed(3)})`;
        ctx.fill();
      }

      this.rafId = requestAnimationFrame(loop);
    };

    this.rafId = requestAnimationFrame(loop);
  }

  // ── Cleanup ──────────────────────────────────────────────────────────────────────
  //
  // Called if the webview is being torn down programmatically.
  // Cancels the animation frame AND the Tauri event listener so there
  // are no dangling references or re-delivery after unmount.
  //
  destroy(): void {
    cancelAnimationFrame(this.rafId);
    this.unlistenMode?.();
    this.unlistenMode = null;
  }
}

// Auto-init when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const orb = new AmbientOrb();
  orb.init().catch(console.error);
});

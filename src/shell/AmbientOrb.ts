/**
 * AmbientOrb.ts — P4 Shell Mode
 * GAIA as an always-on floating desktop presence.
 * Transparent 120x120 orb, draggable, click to expand, right-click context menu.
 *
 * Mode-reactive animation system:
 *   AmbientOrb listens for Tauri 'gaia:mode' events emitted by the main window
 *   (GaiaShell broadcasts these whenever useGaiaMode changes state).
 *   The mode is applied as data-mode="..." on #ambient-orb, which drives
 *   all CSS colour tokens and keyframe animations in ambient.html.
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
 * Mode broadcast from GaiaShell (add to ShellMain):
 *   import { emit } from '@tauri-apps/api/event';
 *   // Call whenever gaiaMode changes:
 *   emit('gaia:mode', { mode: gaiaMode });
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

// ── Mode types ───────────────────────────────────────────────────────────────

type GaiaMode = 'resting' | 'listening' | 'thinking' | 'speaking' | 'offline';

// Particle colours per mode — RGBA triplets (no alpha here, set per-draw)
const MODE_PARTICLE_COLORS: Record<GaiaMode, [number, number, number][]> = {
  resting:   [[155, 109, 219], [180, 143, 232], [100,  60, 180]],   // amethyst
  listening: [[ 79, 152, 163], [100, 220, 200], [ 30, 120, 140]],   // teal
  thinking:  [[180, 143, 232], [200, 160, 255], [110,  50, 210]],   // amethyst bright
  speaking:  [[232, 175,  52], [255, 220, 100], [200, 130,  20]],   // gold
  offline:   [[ 80,  80, 100], [100, 100, 120], [ 50,  50,  70]],   // grey
};

// ── Particle system ───────────────────────────────────────────────────────────

const PARTICLE_COUNT = 12;
const ORB_CX         = 60;  // canvas centre x
const ORB_CY         = 60;  // canvas centre y
const ORB_RADIUS     = 44;  // particle orbit radius

interface OrbParticle {
  angle:        number;   // current orbit angle (radians)
  speed:        number;   // radians per frame
  orbitR:       number;   // orbit radius (slight variation per particle)
  size:         number;   // dot radius in px
  alpha:        number;   // current opacity
  twinklePhase: number;
  twinkleSpeed: number;
  colorIdx:     number;   // index into current mode colour array
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

// ── AmbientOrb class ──────────────────────────────────────────────────────────

export class AmbientOrb {
  private window:     ReturnType<typeof getCurrentWindow>;
  private isDragging: boolean = false;
  private orbEl:      HTMLElement | null = null;
  private canvasEl:   HTMLCanvasElement | null = null;
  private ctx:        CanvasRenderingContext2D | null = null;

  // Mode state
  private currentMode: GaiaMode = 'resting';
  private particles:   OrbParticle[] = [];
  private rafId:       number = 0;
  private tick:        number = 0;

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
    if (!this.orbEl) return;

    if (this.canvasEl) {
      this.ctx = this.canvasEl.getContext('2d');
    }

    this.particles = createParticles();

    this.bindDrag();
    this.bindClick();
    this.bindLongPress();
    await this.bindContextMenu();
    this.bindModeEvents();
    this.startPulse();
    this.startParticleLoop();
  }

  // ── Public mode setter ────────────────────────────────────────────────────

  setMode(mode: GaiaMode): void {
    if (mode === this.currentMode) return;
    this.currentMode = mode;
    if (this.orbEl) {
      this.orbEl.setAttribute('data-mode', mode);
    }
    // Also update parent element for CSS token cascade
    document.documentElement.setAttribute('data-mode', mode);
  }

  // ── Tauri 'gaia:mode' event listener ───────────────────────────────────────
  //
  // GaiaShell should emit: mainWindow.emit('gaia:mode', { mode: gaiaMode })
  // whenever useGaiaMode changes. No Rust handler needed.
  //
  private bindModeEvents(): void {
    listen<{ mode: GaiaMode }>('gaia:mode', (event) => {
      const m = event.payload?.mode;
      const valid: GaiaMode[] = ['resting', 'listening', 'thinking', 'speaking', 'offline'];
      if (valid.includes(m)) this.setMode(m);
    }).catch(() => {
      // Non-Tauri / browser dev environment — silently ignore.
      // Mode can still be driven manually via setMode() or DOM attribute.
    });
  }

  // ── Drag ──────────────────────────────────────────────────────────────────

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
      // No saved position — default placement fine
    }
  }

  // ── Click ──────────────────────────────────────────────────────────────────────

  private bindClick(): void {
    if (!this.orbEl) return;

    this.orbEl.addEventListener('click', async (e: MouseEvent) => {
      if (e.button !== 0) return;
      try {
        const mainWindow = new WebviewWindow('main');
        await mainWindow.show();
        await mainWindow.setFocus();
      } catch (err) {
        console.error('[AmbientOrb] Failed to open main window:', err);
      }
    });
  }

  // ── Long-press ───────────────────────────────────────────────────────────────

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

  // ── Right-click context menu ────────────────────────────────────────────────

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

  // ── openMain ─────────────────────────────────────────────────────────────────

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

  // ── Ambient pulse (CSS class) ──────────────────────────────────────────────
  //
  // Kept for backwards compatibility. The real animation now runs via
  // data-mode CSS tokens. ambient-pulse class is a no-op but harmless.
  //
  private startPulse(): void {
    if (!this.orbEl) return;
    this.orbEl.classList.add('ambient-pulse');
  }

  // ── Particle canvas loop ───────────────────────────────────────────────────
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
        // Advance orbit
        p.angle += p.speed;

        // Twinkle
        const tw   = 0.25 + 0.55 * (0.5 + 0.5 * Math.sin(this.tick * p.twinkleSpeed + p.twinklePhase));
        const x    = ORB_CX + p.orbitR * Math.cos(p.angle);
        const y    = ORB_CY + p.orbitR * Math.sin(p.angle);
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

  // ── Cleanup ──────────────────────────────────────────────────────────────────

  destroy(): void {
    cancelAnimationFrame(this.rafId);
  }
}

// Auto-init when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const orb = new AmbientOrb();
  orb.init().catch(console.error);
});

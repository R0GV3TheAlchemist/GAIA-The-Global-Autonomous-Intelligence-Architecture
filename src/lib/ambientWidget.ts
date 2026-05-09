/**
 * src/lib/ambientWidget.ts
 * GAIA-OS — Ambient Widget  (web-app branch)
 *
 * Web equivalent of the Tauri AmbientOrb.
 * A draggable floating orb rendered inside the main browser window
 * (not a separate OS window — browsers don’t allow that).
 *
 * Differences from AmbientOrb.ts:
 *   - No Tauri window API — pure Pointer Events drag
 *   - Position saved to localStorage instead of the filesystem
 *   - No context menu (native OS menu not available in web)
 *   - Clicking orb scrolls to / focuses the main chat input
 *
 * Usage:
 *   import { AmbientWidget } from './ambientWidget';
 *   const w = new AmbientWidget();
 *   w.init();
 */

const STORAGE_KEY = 'gaia:ambient-widget-position';

export class AmbientWidget {
  private el: HTMLElement | null = null;
  private isDragging  = false;
  private dragOffsetX = 0;
  private dragOffsetY = 0;

  init(): void {
    this.el = document.getElementById('ambient-widget');
    if (!this.el) return;

    this.restorePosition();
    this.bindDrag();
    this.bindClick();
    this.startPulse();
  }

  // ── Drag (Pointer Events) ───────────────────────────────────────────────

  private bindDrag(): void {
    const el = this.el!;

    el.addEventListener('pointerdown', (e: PointerEvent) => {
      if (e.button !== 0) return;
      this.isDragging  = true;
      this.dragOffsetX = e.clientX - el.getBoundingClientRect().left;
      this.dragOffsetY = e.clientY - el.getBoundingClientRect().top;
      el.setPointerCapture(e.pointerId);
      el.style.transition = 'none';
    });

    el.addEventListener('pointermove', (e: PointerEvent) => {
      if (!this.isDragging) return;
      const x = e.clientX - this.dragOffsetX;
      const y = e.clientY - this.dragOffsetY;
      el.style.left = `${x}px`;
      el.style.top  = `${y}px`;
    });

    el.addEventListener('pointerup', () => {
      if (!this.isDragging) return;
      this.isDragging = false;
      el.style.transition = '';
      this.savePosition();
    });
  }

  private savePosition(): void {
    if (!this.el) return;
    const rect = this.el.getBoundingClientRect();
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ x: rect.left, y: rect.top }));
  }

  private restorePosition(): void {
    if (!this.el) return;
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const { x, y } = JSON.parse(raw) as { x: number; y: number };
      // Clamp to viewport so the widget never escapes the screen
      const maxX = window.innerWidth  - (this.el.offsetWidth  || 60);
      const maxY = window.innerHeight - (this.el.offsetHeight || 60);
      this.el.style.left = `${Math.max(0, Math.min(x, maxX))}px`;
      this.el.style.top  = `${Math.max(0, Math.min(y, maxY))}px`;
    } catch {
      // Corrupt localStorage — ignore
    }
  }

  // ── Click — focus chat input ────────────────────────────────────────────

  private bindClick(): void {
    this.el?.addEventListener('click', () => {
      const input = document.querySelector<HTMLElement>('.gaia-chat__input');
      input?.focus();
    });
  }

  // ── Pulse animation ──────────────────────────────────────────────────────

  private startPulse(): void {
    this.el?.classList.add('ambient-pulse');
  }
}

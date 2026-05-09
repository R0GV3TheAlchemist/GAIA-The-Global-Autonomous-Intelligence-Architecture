/**
 * HomeTwin.ts
 *
 * Orchestrates the Home Twin experience:
 *   1. Load existing room scan → go straight to RoomRenderer
 *   2. No scan yet → launch RoomScanner flow
 *   3. After scan → RoomRenderer + SurfaceDetector overlay
 *
 * Canon Ref: C20 (Home Twin — Spatial Presence)
 *
 * Viriditas addition (Issue #64):
 *   After the renderer mounts, a React island containing
 *   <ViritasWidget showDetail /> is injected into the bottom-left
 *   corner of the room container as a glass-card overlay.
 *   The island is cleanly unmounted on dispose() and rescan.
 */

import './home-twin.css';
import { RoomScanner }     from './RoomScanner';
import { RoomRenderer }    from './RoomRenderer';
import { SurfaceDetector } from './SurfaceDetector';
import { RoomStore }       from './RoomStore';
import React               from 'react';
import { createRoot, Root } from 'react-dom/client';
import { ViritasWidget }   from '../shared/ViritasWidget';

export class HomeTwin {
  private root:          HTMLElement;
  private renderer:      RoomRenderer | null = null;
  private scanner:       RoomScanner  | null = null;
  private viritasRoot:   Root         | null = null;

  constructor(root: HTMLElement) {
    this.root = root;
  }

  async mount(): Promise<void> {
    const store = new RoomStore();
    const room  = await store.loadRoom();

    if (room?.panoramaDataUrl) {
      await this._mountRenderer();
    } else {
      this._mountScanPrompt();
    }
  }

  dispose(): void {
    this._disposeViritasPanel();
    this.renderer?.dispose();
    this.scanner?.dispose();
  }

  // ------------------------------------------------------------------ //
  //  Viriditas panel (React island)                                      //
  // ------------------------------------------------------------------ //

  private _mountViritasPanel(container: HTMLElement): void {
    // Create the host slot if it doesn't already exist
    let slot = container.querySelector<HTMLElement>('#ht-alignment-root');
    if (!slot) {
      slot = document.createElement('div');
      slot.id        = 'ht-alignment-root';
      slot.className = 'ht-alignment-panel';
      container.appendChild(slot);
    }

    this._disposeViritasPanel();
    this.viritasRoot = createRoot(slot);
    this.viritasRoot.render(
      React.createElement(ViritasWidget, { showDetail: true })
    );
  }

  private _disposeViritasPanel(): void {
    if (this.viritasRoot) {
      this.viritasRoot.unmount();
      this.viritasRoot = null;
    }
    // Remove the DOM slot so _mountViritasPanel re-creates it cleanly
    this.root.querySelector('#ht-alignment-root')?.remove();
  }

  // ------------------------------------------------------------------ //
  //  Scan prompt                                                         //
  // ------------------------------------------------------------------ //

  private _mountScanPrompt(): void {
    this._disposeViritasPanel();
    this.root.innerHTML = `
<div class="ht-prompt">
  <div class="ht-prompt-icon">◉</div>
  <h2 class="ht-prompt-title">Bring GAIA Home</h2>
  <p class="ht-prompt-desc">Scan your room once and GAIA will live in your space permanently.</p>
  <p class="ht-prompt-sub">Takes about 2 minutes. Works without any AR headset.</p>
  <button id="ht-btn-scan" class="ht-btn-primary">◎ Start Room Scan</button>
  <button id="ht-btn-skip" class="ht-btn-ghost">Use gradient background</button>
</div>`;

    this.root.querySelector('#ht-btn-scan')?.addEventListener('click', () => this._mountScanner());
    this.root.querySelector('#ht-btn-skip')?.addEventListener('click', () => this._mountRenderer());
  }

  // ------------------------------------------------------------------ //
  //  Scanner                                                             //
  // ------------------------------------------------------------------ //

  private _mountScanner(): void {
    this._disposeViritasPanel();
    this.root.innerHTML = '<div id="ht-scanner-host" class="ht-scanner-host"></div>';
    const host = this.root.querySelector<HTMLElement>('#ht-scanner-host')!;

    this.scanner = new RoomScanner(host, async (panoramaDataUrl) => {
      this.scanner?.dispose();
      await this._mountRenderer();
      this._runSurfaceDetection(panoramaDataUrl);
    });

    host.addEventListener('rs:cancel', () => this._mountScanPrompt());
    void this.scanner.mount();
  }

  // ------------------------------------------------------------------ //
  //  Renderer                                                            //
  // ------------------------------------------------------------------ //

  private async _mountRenderer(): Promise<void> {
    this.root.innerHTML = '<div class="ht-room-container" id="ht-room-container"></div>';
    const container = this.root.querySelector<HTMLElement>('#ht-room-container')!;

    const rescanBtn = document.createElement('button');
    rescanBtn.className   = 'ht-btn-rescan';
    rescanBtn.textContent = '↺ Rescan Room';
    rescanBtn.addEventListener('click', () => {
      this._disposeViritasPanel();
      this.renderer?.dispose();
      this._mountScanner();
    });
    container.appendChild(rescanBtn);

    this.renderer = new RoomRenderer(container);
    await this.renderer.mount();

    // Mount the Viriditas detail panel after the renderer is ready
    this._mountViritasPanel(container);
  }

  // ------------------------------------------------------------------ //
  //  Surface detection                                                   //
  // ------------------------------------------------------------------ //

  private async _runSurfaceDetection(panoramaDataUrl: string): Promise<void> {
    const container = this.root.querySelector<HTMLElement>('#ht-room-container');
    if (!container) return;

    const detector = new SurfaceDetector(container, async (placement) => {
      console.log('[HomeTwin] GAIA placed:', placement);
      const orbCanvas = container.querySelector<HTMLElement>('.gaian-orb-canvas');
      if (orbCanvas) {
        orbCanvas.style.top       = `${placement.yPercent * 100 - 15}%`;
        orbCanvas.style.left      = '50%';
        orbCanvas.style.transform = 'translate(-50%, -50%)';
      }
    });

    const surfaces = await detector.detect(panoramaDataUrl);
    if (surfaces.length > 0) detector.renderOverlay();
  }
}

export function mountHomeTwin(root: HTMLElement): void {
  const twin = new HomeTwin(root);
  void twin.mount();
}

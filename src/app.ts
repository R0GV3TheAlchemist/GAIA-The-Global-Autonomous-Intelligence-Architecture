// GAIA App — Top-level layout with tab navigation
// Views: SEARCH | GAIAN | CHAT | SHELL | MEMORY | NOOSPHERE | CANON | QUANTUM | DIMENSIONS | ARCHETYPES | DEV SUITE
// Canon Ref: C42, C43, C44
// Issues: #78 (DevSuite wired), #79 (Onboarding first-launch guard)

import './app.css';
import './search/Search.css';
import './shell/Shell.css';
import './chat/Chat.css';
import './memory/Memory.css';
import './noosphere/NoosphereTab.css';
import './canon/CanonTab.css';
import './dimensions/DimensionalMonitor.css';
import './gaian/GaianHome.css';
import './dev-suite/DevSuite.css';
import './onboarding/onboarding.css';
import { mountSearch }             from './search/Search';
import { mountShell }              from './shell/Shell';
import { mountChat }               from './chat/Chat';
import { mountMemory }             from './memory/Memory';
import { mountGaianHome, GaianHome } from './gaian/GaianHome';
import {
  mountNoosphereTab,
  unmountNoosphereTab,
} from './noosphere';
import { mountCanonTab }           from './canon/CanonTab';
import { mountQuantumTab }         from './quantum/QuantumTab';
import { mountDimensionalMonitor } from './dimensions/DimensionalMonitor';
import { mountArchetypalTab }      from './archetypes/ArchetypalTab';
import { initDevSuite, toggleDevSuite } from './dev-suite/DevSuite';
import { OnboardingRouter, loadPersistedState, useOnboardingStore } from './onboarding';
import { appDataDir, join, resolveResource } from '@tauri-apps/api/path';
import { exists, mkdir, copyFile, readDir }  from '@tauri-apps/plugin-fs';
import { listen }                  from '@tauri-apps/api/event';
import { checkForUpdates }         from './updater';
import { logInfo, logWarn, logError } from './diagnostics';
import { API_BASE } from './config';
import { createElement }           from 'react';
import { createRoot }              from 'react-dom/client';

export { API_BASE };

// ── First-launch: seed %APPDATA%\GAIA\canon\ from bundled resources ────
async function ensureAppDataDirs(): Promise<void> {
  try {
    const appData = await appDataDir();
    const dirs = ['canon', 'logs', 'config'];
    for (const dir of dirs) {
      const dirPath = await join(appData, dir);
      if (!(await exists(dirPath))) {
        await mkdir(dirPath, { recursive: true });
        logInfo('app', `Created AppData dir: ${dir}`);
      }
    }
    const canonDest = await join(appData, 'canon');
    const canonDestEntries = await readDir(canonDest);
    if (canonDestEntries.length === 0) {
      try {
        const canonSrc = await resolveResource('canon');
        const srcEntries = await readDir(canonSrc);
        for (const entry of srcEntries) {
          const srcFile  = await join(canonSrc,  entry.name);
          const destFile = await join(canonDest, entry.name);
          await copyFile(srcFile, destFile);
        }
        logInfo('app', `Seeded ${srcEntries.length} canon docs to AppData`);
      } catch (e) {
        logWarn('app', 'Could not seed canon docs (may not be bundled yet)', e);
      }
    }
  } catch (e) {
    logError('app', 'ensureAppDataDirs failed', e);
  }
}

// ── Updater ─────────────────────────────────────────────────────────────────
async function initUpdater(): Promise<void> {
  const unlisten = await listen('sidecar:ready', async () => {
    unlisten();
    logInfo('updater', 'sidecar:ready received — scheduling update check');
    await new Promise(r => setTimeout(r, 2000));
    await checkForUpdates();
  });
}

// ── Helper: switch active tab view ──────────────────────────────────────────
function switchView(view: string, _activeView: { current: string }): void {
  document.querySelectorAll<HTMLButtonElement>('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.view === view);
  });
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById(`view-${view}`)?.classList.add('active');
  logInfo('app', `View switched: ${_activeView.current} → ${view}`);
  _activeView.current = view;
}

// ── Main app mount (called after onboarding is complete or skipped) ──────────
function mountApp(): void {
  const root = document.querySelector<HTMLDivElement>('#app')!;
  root.innerHTML = `
<div class="gaia-app">
  <nav class="tab-nav">
    <button class="tab-btn active" data-view="gaian">&#9632; Home</button>
    <button class="tab-btn"        data-view="search">&#128269; Search</button>
    <button class="tab-btn"        data-view="chat">&#9670; Chat</button>
    <button class="tab-btn"        data-view="shell">&gt; Shell</button>
    <button class="tab-btn"        data-view="memory">&#9638; Memory</button>
    <button class="tab-btn"        data-view="noosphere">&#127760; Noosphere</button>
    <button class="tab-btn"        data-view="canon">&#128220; Canon</button>
    <button class="tab-btn"        data-view="quantum">&#10731; Quantum</button>
    <button class="tab-btn"        data-view="dimensions">&#11042; Dimensions</button>
    <button class="tab-btn"        data-view="archetypes">&#9672; Archetypes</button>
    <button class="tab-btn"        data-view="dev" id="tab-dev">&#128736; Dev Suite</button>
  </nav>
  <div class="view-container">
    <div id="view-gaian"       class="view active"></div>
    <div id="view-search"      class="view"></div>
    <div id="view-chat"        class="view"></div>
    <div id="view-shell"       class="view"></div>
    <div id="view-memory"      class="view"></div>
    <div id="view-noosphere"   class="view"></div>
    <div id="view-canon"       class="view"></div>
    <div id="view-quantum"     class="view"></div>
    <div id="view-dimensions"  class="view"></div>
    <div id="view-archetypes"  class="view"></div>
    <div id="view-dev"         class="view"></div>
  </div>
</div>
`;

  // Seed window.__gaiaUserName from onboarding store (#79)
  try {
    const name = useOnboardingStore.getState().name;
    if (name) window.__gaiaUserName = name;
  } catch { /* non-Tauri env */ }

  // Track active view
  const activeView = { current: 'gaian' };

  // ── Mount Home ───────────────────────────────────────────────────────────
  let gaianHome: GaianHome | null = mountGaianHome(
    document.getElementById('view-gaian')!,
    (target) => {
      if (target === activeView.current) return;
      if (activeView.current === 'noosphere') unmountNoosphereTab();
      teardowns[activeView.current]?.();
      switchView(target, activeView);
      handleLazyMount(target);
    },
  );

  // ── Eager mounts ─────────────────────────────────────────────────────────
  mountSearch(document.getElementById('view-search')!);
  mountChat(document.getElementById('view-chat')!);
  mountShell(document.getElementById('view-shell')!);
  mountMemory(document.getElementById('view-memory')!);
  mountNoosphereTab({ root: document.getElementById('view-noosphere')!, apiBase: API_BASE });

  // ── #78: Init Dev Suite keyboard shortcut (Ctrl+Shift+D) ─────────────────
  initDevSuite();

  // ── Lazy-mount flags ──────────────────────────────────────────────────────
  let canonMounted      = false;
  let quantumMounted    = false;
  let dimensionsMounted = false;
  let archetypesMounted = false;

  // Teardown registry
  const teardowns: Record<string, (() => void) | null> = {
    gaian:      () => { gaianHome?.dispose(); gaianHome = null; },
    dimensions: null,
    archetypes: null,
  };

  function handleLazyMount(view: string): void {
    if (view === 'noosphere') {
      mountNoosphereTab({ root: document.getElementById('view-noosphere')!, apiBase: API_BASE });
    }
    if (view === 'canon' && !canonMounted) {
      mountCanonTab(document.getElementById('view-canon')!);
      canonMounted = true;
    }
    if (view === 'quantum' && !quantumMounted) {
      mountQuantumTab(document.getElementById('view-quantum')!);
      quantumMounted = true;
    }
    if (view === 'dimensions' && !dimensionsMounted) {
      teardowns.dimensions = mountDimensionalMonitor(document.getElementById('view-dimensions')!);
      dimensionsMounted = true;
    }
    if (view === 'archetypes' && !archetypesMounted) {
      teardowns.archetypes = mountArchetypalTab(document.getElementById('view-archetypes')!);
      archetypesMounted = true;
    }
    // #78: Dev Suite — toggle the full-screen overlay
    if (view === 'dev') {
      toggleDevSuite();
    }
  }

  logInfo('app', 'All views mounted — Home is primary');

  // ── Tab nav click handler ─────────────────────────────────────────────────
  document.querySelectorAll<HTMLButtonElement>('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const view = btn.dataset.view!;
      if (view === activeView.current) return;

      if (activeView.current === 'noosphere') unmountNoosphereTab();
      teardowns[activeView.current]?.();

      // Dev Suite tab: toggle overlay but don't change the active view tracker
      // so the underlying view remains visible when Dev Suite is dismissed
      if (view === 'dev') {
        toggleDevSuite();
        return;
      }

      switchView(view, activeView);
      handleLazyMount(view);
    });
  });
}

// ── #79: Onboarding first-launch guard ───────────────────────────────────────
// Reads persisted onboarding_state.json; if not completed, renders OnboardingRouter
// in a full-viewport overlay BEFORE mounting the normal app UI.
async function boot(): Promise<void> {
  await ensureAppDataDirs();
  initUpdater();

  const saved = await loadPersistedState();
  const alreadyComplete = saved?.completed === true;

  if (alreadyComplete) {
    logInfo('app', 'Onboarding already complete — mounting app directly');
    mountApp();
    return;
  }

  logInfo('app', 'First launch detected — mounting OnboardingRouter');

  // Create a full-viewport overlay for the onboarding ceremony
  const overlay = document.createElement('div');
  overlay.id = 'onboarding-overlay';
  overlay.style.cssText = [
    'position:fixed', 'inset:0', 'z-index:9999',
    'background:var(--color-bg, #0a0a0b)',
    'display:flex', 'align-items:center', 'justify-content:center',
  ].join(';');
  document.body.appendChild(overlay);

  // If there's a partially-completed onboarding, hydrate the store first
  if (saved && saved.phase && saved.phase > 0) {
    useOnboardingStore.getState().setPhase(saved.phase as any);
  }

  const reactRoot = createRoot(overlay);

  function handleOnboardingFinish(): void {
    logInfo('app', 'Onboarding complete — tearing down overlay, mounting app');

    // Seed the global name from the store for GaianGreeting
    try {
      const name = useOnboardingStore.getState().name;
      if (name) window.__gaiaUserName = name;
    } catch { /* non-Tauri env */ }

    reactRoot.unmount();
    overlay.remove();
    mountApp();
  }

  reactRoot.render(
    createElement(OnboardingRouter, { onFinish: handleOnboardingFinish })
  );
}

export class App {
  constructor() {
    logInfo('app', 'GAIA App initialising');
    boot().catch((e) => {
      logError('app', 'boot() failed — falling back to direct app mount', e);
      mountApp();
    });
  }
}

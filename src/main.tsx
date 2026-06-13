/**
 * src/main.tsx
 * GAIA-OS React Entry Point — Phase 4b rev 2
 * Canon: C90
 *
 * Boot sequence:
 * 1. createRoot()   — React 18 concurrent mode
 * 2. Mount <GaiaRoot /> — reads onboarding_state.json, then routes to
 *    <OnboardingRouter> (first run) or <GaiaShell> (returning user)
 * 3. initSidecar()  — Python FastAPI backend alive check (non-blocking)
 * 4. notificationBridge.init() — Tauri notification listener
 *
 * Changed from Phase 4b:
 *   - <GaiaShell /> replaced with <GaiaRoot /> so first-time users see
 *     onboarding before the shell. GaiaShell is still mounted by GaiaRoot
 *     once onboarding is complete. (issue #368)
 */

import { StrictMode } from 'react';
import { createRoot }  from 'react-dom/client';
import { initSidecar } from './sidecar';
import { notificationBridge } from './shell/NotificationBridge';
import { GaiaRoot } from './GaiaRoot';
import './field/crystal-tokens.css';
import './styles.css';
import './GaiaRoot.css';

const rootEl = document.getElementById('gaia-root');
if (!rootEl) throw new Error('GAIA: #gaia-root not found in DOM.');

const root = createRoot(rootEl);

root.render(
  <StrictMode>
    <GaiaRoot />
  </StrictMode>
);

initSidecar()
  .then(() => notificationBridge.init())
  .catch((err: unknown) => console.error('[GAIA] Sidecar init error:', err));

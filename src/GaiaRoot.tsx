/**
 * GaiaRoot.tsx
 * Canon: GAIAN_TWIN_DOCTRINE
 *
 * GaiaShell owns the four-state boot guard:
 *   AwakeningScreen → AuthScreen → OnboardingRouter → ShellMain
 *
 * GaiaRoot is the app entry point — it simply mounts GaiaShell.
 * All routing, auth, and session management lives in GaiaShell.
 */

import { GaiaShell } from './shell/GaiaShell';
import './GaiaRoot.css';

export function GaiaRoot() {
  return <GaiaShell />;
}

export default GaiaRoot;

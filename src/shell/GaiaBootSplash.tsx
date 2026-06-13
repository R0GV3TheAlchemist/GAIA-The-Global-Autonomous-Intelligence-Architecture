// GaiaBootSplash.tsx
// Shown while loadPersistedState() is in flight on first boot.
// Duration is typically <100ms on a warm SSD, but can be longer on first
// launch when AppData directory doesn't yet exist.
//
// Intentionally minimal: just the GAIA sigil on a dark background.
// No animation library dependencies. Uses CSS keyframes defined in
// GaiaBootSplash.css.

import { GaiaSigil } from '../onboarding/components/GaiaSigil';
import './GaiaBootSplash.css';

export function GaiaBootSplash() {
  return (
    <div className="gaia-boot-splash" role="status" aria-label="GAIA is starting">
      <GaiaSigil animate size={64} />
    </div>
  );
}

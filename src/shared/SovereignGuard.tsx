/**
 * src/shared/SovereignGuard.tsx
 * Axiom I — Always Visible.
 * "The Human Element controls with love and authority."
 * Canon: C90, C-SINGULARITY (Axiom I)
 */

import React from 'react';
import { useCrystal } from '../hooks/useCrystal';
import { crystalStore } from '../store/crystalStore';

export const SovereignGuard: React.FC = () => {
  const { activeCrystal, emergencyStop, returnToSovereign, emergencyStopped } = useCrystal();
  const showReturn = activeCrystal !== 'SOVEREIGN';

  function handleResume(): void {
    // returnToSovereign clears emergencyStopped and transitions back
    crystalStore.returnToSovereign();
    returnToSovereign();
  }

  return (
    <div
      className={`sovereign-guard${emergencyStopped ? ' sovereign-guard--stopped' : ''}`}
      role="navigation"
      aria-label="Sovereign Guard — Axiom I controls"
    >
      <span className="sovereign-guard__axiom">You control with love.</span>

      <div className="sovereign-guard__controls">
        {showReturn && (
          <button
            className="sovereign-guard__btn sovereign-guard__btn--return"
            onClick={returnToSovereign}
            title="Return to Sovereign Core (Axiom I)"
            aria-label="Return to Sovereign Core"
          >
            ◆ Sovereign Core
          </button>
        )}
        <button
          className="sovereign-guard__btn sovereign-guard__btn--stop"
          onClick={emergencyStop}
          title="Emergency stop — pause all active processes"
          aria-label="Emergency stop"
          disabled={emergencyStopped}
        >
          {emergencyStopped ? '❆ Stopped' : '■ Stop everything'}
        </button>
      </div>

      {emergencyStopped && (
        <div className="sovereign-guard__stopped-notice" role="alert">
          <p>All processes paused. You are safe.</p>
          <button
            className="sovereign-guard__btn sovereign-guard__btn--resume"
            onClick={handleResume}
          >
            Resume — Return to Sovereign Core
          </button>
        </div>
      )}
    </div>
  );
};

export default SovereignGuard;

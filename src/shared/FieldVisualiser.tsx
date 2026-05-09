/**
 * src/shared/FieldVisualiser.tsx
 * GAIA-OS — Ambient Field Visualiser
 * Issue #68 Phase 6
 *
 * React wrapper around FieldParticles.
 * Renders a full-screen Three.js canvas layer positioned behind all
 * shell UI (position: fixed, inset: 0, z-index: -1, pointer-events: none).
 *
 * The canvas is transparent; the shell’s dark background shows through,
 * and particles blend additively on top of it.
 *
 * Props:
 *   tier — AlignmentTier  (from useAlignmentTheme in GaiaShell)
 *
 * Behaviour:
 *   - On mount: creates FieldParticles instance, calls setTier(tier)
 *   - On tier change: calls setTier(tier) — triggers crossfade, no remount
 *   - On unmount: calls dispose()
 *   - Page hidden: RAF loop pauses automatically (inside FieldParticles)
 *   - prefers-reduced-motion: single static frame, no loop
 */

import React, { useEffect, useRef } from 'react';
import { FieldParticles }           from '../lib/fieldParticles';
import type { AlignmentTier }        from '../hooks/useAlignment';
import './FieldVisualiser.css';

interface FieldVisualiserProps {
  tier: AlignmentTier;
}

export const FieldVisualiser: React.FC<FieldVisualiserProps> = ({ tier }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fpRef     = useRef<FieldParticles | null>(null);

  // ── Mount / unmount ──
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const fp = new FieldParticles(canvas);
    fpRef.current = fp;
    fp.setTier(tier); // initial tier on mount

    return () => {
      fp.dispose();
      fpRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);   // intentionally empty — tier changes handled below

  // ── Tier changes ──
  useEffect(() => {
    fpRef.current?.setTier(tier);
  }, [tier]);

  return (
    <div className="field-visualiser" aria-hidden="true">
      <canvas ref={canvasRef} className="field-visualiser__canvas" />
    </div>
  );
};

export default FieldVisualiser;

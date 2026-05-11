/**
 * src/crystal-view/CoherenceRing.tsx
 * GAIA-OS — Coherence Ring
 * Spec: C-CC01 §11.2
 *
 * SVG radial ring filled to Ψ × 100%.
 * Wraps the GaianOrb — rendered as an overlay in CrystalView.
 */

import React, { useEffect, useRef } from 'react';
import type { CoherenceBand } from './types';
import { BAND_HUE } from './types';

interface CoherenceRingProps {
  coherence: number;      // 0–1 fill fraction
  band:      CoherenceBand;
  size?:     number;      // px diameter of ring, default 280
  stroke?:   number;      // stroke width, default 3
}

export const CoherenceRing: React.FC<CoherenceRingProps> = ({
  coherence,
  band,
  size   = 280,
  stroke = 3,
}) => {
  const pathRef = useRef<SVGCircleElement>(null);

  const cx     = size / 2;
  const cy     = size / 2;
  const radius = (size - stroke * 2) / 2 - 4;
  const circ   = 2 * Math.PI * radius;
  const fill   = circ * (1 - coherence);  // dashoffset = remaining unfilled

  const color = BAND_HUE[band];

  useEffect(() => {
    const el = pathRef.current;
    if (!el) return;
    el.style.transition = 'stroke-dashoffset 1.4s cubic-bezier(0.16, 1, 0.3, 1)';
    el.style.strokeDashoffset = String(fill);
  }, [fill]);

  return (
    <svg
      className="coherence-ring"
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      aria-label={`Coherence ${Math.round(coherence * 100)}%`}
      role="img"
    >
      {/* Track */}
      <circle
        cx={cx}
        cy={cy}
        r={radius}
        fill="none"
        stroke="rgba(255,255,255,0.06)"
        strokeWidth={stroke}
      />
      {/* Fill — starts at 12 o'clock, clockwise */}
      <circle
        ref={pathRef}
        cx={cx}
        cy={cy}
        r={radius}
        fill="none"
        stroke={color}
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={circ}
        strokeDashoffset={fill}
        transform={`rotate(-90 ${cx} ${cy})`}
        style={{
          filter: `drop-shadow(0 0 ${4 + coherence * 8}px ${color}88)`,
          transition: 'stroke-dashoffset 1.4s cubic-bezier(0.16, 1, 0.3, 1), stroke 0.8s ease',
        }}
      />
    </svg>
  );
};

export default CoherenceRing;

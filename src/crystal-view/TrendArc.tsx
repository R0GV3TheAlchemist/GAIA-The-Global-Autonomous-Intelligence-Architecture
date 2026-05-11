/**
 * src/crystal-view/TrendArc.tsx
 * GAIA-OS — 7-day coherence trend arc
 * Spec: C-CC01 §11.2
 *
 * Draws the last 7 days of coherence ticks as a faint arc line
 * that rings the outside of the orb area. Pure SVG, no axes, no labels.
 * The user reads the shape — not the numbers.
 */

import React, { useMemo } from 'react';
import type { CoherenceTick } from './types';

interface TrendArcProps {
  history:  CoherenceTick[];
  size?:    number;   // outer SVG size (should match CoherenceRing size)
  arcRadius?: number; // radius of the arc path
}

export const TrendArc: React.FC<TrendArcProps> = ({
  history,
  size      = 320,
  arcRadius = 148,
}) => {
  const points = useMemo(() => {
    if (history.length < 2) return null;

    // Arc spans 300° — from 120° to 420° (same as 60°), centred at top
    const startDeg = -240;
    const sweepDeg = 300;
    const cx = size / 2;
    const cy = size / 2;

    const toXY = (index: number, value: number): [number, number] => {
      const frac = index / (history.length - 1);
      const deg  = startDeg + frac * sweepDeg;
      const rad  = (deg * Math.PI) / 180;
      // Radial offset scales with coherence: ± 12px
      const r    = arcRadius + (value - 0.5) * 24;
      return [
        cx + r * Math.cos(rad),
        cy + r * Math.sin(rad),
      ];
    };

    // Build SVG path
    const d = history.reduce((acc, tick, i) => {
      const [x, y] = toXY(i, tick.coherence);
      return `${acc}${i === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)} `;
    }, '');

    return d;
  }, [history, size, arcRadius]);

  if (!points) return null;

  return (
    <svg
      className="trend-arc"
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      aria-hidden="true"
    >
      {/* Faint guide arc track */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={arcRadius}
        fill="none"
        stroke="rgba(255,255,255,0.04)"
        strokeWidth={1}
      />
      {/* Trend path */}
      <path
        d={points}
        fill="none"
        stroke="rgba(79,195,161,0.35)"
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Current point */}
      {history.length > 0 && (() => {
        const last = history[history.length - 1];
        const frac = 1;
        const deg  = -240 + frac * 300;
        const rad  = (deg * Math.PI) / 180;
        const r    = arcRadius + (last.coherence - 0.5) * 24;
        const x    = size / 2 + r * Math.cos(rad);
        const y    = size / 2 + r * Math.sin(rad);
        return (
          <circle
            cx={x}
            cy={y}
            r={3}
            fill="#4fc3a1"
            opacity={0.8}
          />
        );
      })()}
    </svg>
  );
};

export default TrendArc;

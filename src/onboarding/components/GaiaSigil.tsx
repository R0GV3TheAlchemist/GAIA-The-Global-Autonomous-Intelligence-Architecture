// C-OB01 — GAIA Sigil Component
// The animated SVG sigil used in Phase 1 and Phase 8.
// Respects prefers-reduced-motion.

import React from 'react';

interface GaiaSigilProps {
  size?: number;
  brightness?: 'dim' | 'normal' | 'bright';
  animate?: boolean;
  className?: string;
}

export const GaiaSigil: React.FC<GaiaSigilProps> = ({
  size = 120,
  brightness = 'normal',
  animate = true,
  className = '',
}) => {
  const opacityMap = { dim: 0.4, normal: 0.75, bright: 1 };
  const baseOpacity = opacityMap[brightness];

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      aria-label="GAIA sigil"
      role="img"
      className={`gaia-sigil ${animate ? 'gaia-sigil--animate' : ''} ${className}`}
      style={{ opacity: baseOpacity }}
    >
      {/* Outer ring */}
      <circle
        cx="60"
        cy="60"
        r="54"
        stroke="currentColor"
        strokeWidth="1"
        strokeDasharray="4 6"
        opacity="0.3"
      />
      {/* Middle ring */}
      <circle
        cx="60"
        cy="60"
        r="42"
        stroke="currentColor"
        strokeWidth="1"
        opacity="0.5"
      />
      {/* Inner ring */}
      <circle
        cx="60"
        cy="60"
        r="28"
        stroke="currentColor"
        strokeWidth="1.5"
        opacity="0.7"
      />
      {/* Core circle — pulses */}
      <circle
        cx="60"
        cy="60"
        r="6"
        fill="currentColor"
        opacity="0.9"
        className="gaia-sigil__core"
      />
      {/* Vertical axis */}
      <line x1="60" y1="6" x2="60" y2="114" stroke="currentColor" strokeWidth="0.75" opacity="0.25" />
      {/* Horizontal axis */}
      <line x1="6" y1="60" x2="114" y2="60" stroke="currentColor" strokeWidth="0.75" opacity="0.25" />
      {/* Diagonal NW-SE */}
      <line x1="21.8" y1="21.8" x2="98.2" y2="98.2" stroke="currentColor" strokeWidth="0.5" opacity="0.15" />
      {/* Diagonal NE-SW */}
      <line x1="98.2" y1="21.8" x2="21.8" y2="98.2" stroke="currentColor" strokeWidth="0.5" opacity="0.15" />
      {/* Sacred geometry — six-point inner star */}
      <polygon
        points="60,32 68.66,46 85.98,46 77.32,60 85.98,74 68.66,74 60,88 51.34,74 34.02,74 42.68,60 34.02,46 51.34,46"
        stroke="currentColor"
        strokeWidth="1"
        fill="none"
        opacity="0.35"
      />
      {/* G glyph at center — stylized */}
      <text
        x="60"
        y="65"
        textAnchor="middle"
        fontFamily="Georgia, serif"
        fontSize="18"
        fill="currentColor"
        opacity="0.8"
        letterSpacing="0"
      >
        𝒢
      </text>
    </svg>
  );
};

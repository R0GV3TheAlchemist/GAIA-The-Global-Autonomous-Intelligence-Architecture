// C-OB01 — TypewriterText Component
// Renders text character by character at a given speed.
// Respects prefers-reduced-motion by showing text immediately.

import React, { useState, useEffect, useCallback } from 'react';

interface TypewriterTextProps {
  text: string;
  speed?: number; // ms per character
  onComplete?: () => void;
  className?: string;
  reducedMotion?: boolean;
  tag?: keyof JSX.IntrinsicElements;
}

export const TypewriterText: React.FC<TypewriterTextProps> = ({
  text,
  speed = 28,
  onComplete,
  className = '',
  reducedMotion = false,
  tag: Tag = 'p',
}) => {
  const prefersReduced =
    reducedMotion ||
    (typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  const [displayed, setDisplayed] = useState(prefersReduced ? text : '');
  const [done, setDone] = useState(prefersReduced);

  const finish = useCallback(() => {
    setDisplayed(text);
    setDone(true);
    onComplete?.();
  }, [text, onComplete]);

  useEffect(() => {
    if (prefersReduced) {
      finish();
      return;
    }
    setDisplayed('');
    setDone(false);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(interval);
        setDone(true);
        onComplete?.();
      }
    }, speed);
    return () => clearInterval(interval);
  }, [text, speed, prefersReduced, finish, onComplete]);

  return (
    // @ts-expect-error dynamic tag
    <Tag
      className={`typewriter-text ${done ? 'typewriter-text--done' : ''} ${className}`}
      aria-live="polite"
      aria-label={text}
    >
      {displayed}
      {!done && <span className="typewriter-cursor" aria-hidden="true">▌</span>}
    </Tag>
  );
};

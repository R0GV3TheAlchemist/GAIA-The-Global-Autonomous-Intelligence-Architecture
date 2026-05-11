// C-OB01 — TypewriterText Component
// Renders text character by character at a given speed.
// Respects prefers-reduced-motion by showing text immediately.
// FIX: Wrapped in React.memo to prevent animation restart on parent re-renders.
// FIX: onComplete called via ref to avoid stale-closure re-fire.

import React, { useState, useEffect, useRef } from 'react';

interface TypewriterTextProps {
  text: string;
  speed?: number;
  onComplete?: () => void;
  className?: string;
  reducedMotion?: boolean;
  tag?: keyof JSX.IntrinsicElements;
}

export const TypewriterText: React.FC<TypewriterTextProps> = React.memo(function TypewriterText({
  text,
  speed = 28,
  onComplete,
  className = '',
  reducedMotion = false,
  tag: Tag = 'p',
}) {
  const prefersReduced =
    reducedMotion ||
    (typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  const [displayed, setDisplayed] = useState(prefersReduced ? text : '');
  const [done, setDone] = useState(prefersReduced);

  // Store onComplete in a ref so we never re-run the effect when it changes
  const onCompleteRef = useRef(onComplete);
  useEffect(() => { onCompleteRef.current = onComplete; }, [onComplete]);

  useEffect(() => {
    if (prefersReduced) {
      setDisplayed(text);
      setDone(true);
      onCompleteRef.current?.();
      return;
    }
    // Reset for new text
    setDisplayed('');
    setDone(false);
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) {
        clearInterval(interval);
        setDone(true);
        onCompleteRef.current?.();
      }
    }, speed);
    return () => clearInterval(interval);
  // Only re-run when text or speed changes — NOT when onComplete changes
  }, [text, speed, prefersReduced]);

  return (
    // @ts-ignore — Tag is a valid intrinsic element
    <Tag
      className={`typewriter-text ${done ? 'typewriter-text--done' : ''} ${className}`}
      aria-live="polite"
      aria-label={text}
    >
      {displayed}
      {!done && <span className="typewriter-cursor" aria-hidden="true">▌</span>}
    </Tag>
  );
});

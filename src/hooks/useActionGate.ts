/**
 * src/hooks/useActionGate.ts
 *
 * React hook that owns the ActionGate IPC event lifecycle.
 *
 * Architecture
 * ------------
 * The Python backend emits 'action-gate-confirm' events via one of:
 *   a) Tauri IPC `emit()` (when Tauri plugin is available)
 *   b) A structured WARNING log line forwarded by the log-bridge
 *      (fallback during development, until Tauri plugin is wired)
 *
 * This hook listens for window CustomEvents named 'action-gate-confirm'
 * dispatched by the GAIA log-bridge listener in app.ts. When a new event
 * arrives it is queued. The dialog shows the front of the queue.
 *
 * When the human sovereign makes a decision, `resolve()` POSTs to
 * /action-gate/respond and removes the event from the queue.
 *
 * Usage
 * -----
 *   const { pending, resolve } = useActionGate();
 *   // pending[0] is the active event, null if none
 *   // resolve(request_id, approved) sends the decision
 *
 * Canon: Doc 35, Doc 21
 */

import { useCallback, useEffect, useRef, useState } from 'react';

const API_BASE = 'http://localhost:8008';

export interface ActionGateEvent {
  request_id:  string;
  tier:        'green' | 'yellow' | 'red';
  type:        string;
  description: string;
  payload:     Record<string, unknown>;
  timeout:     number;   // seconds
  default:     boolean;  // true = approved on silence, false = blocked on silence
}

interface UseActionGateReturn {
  pending: ActionGateEvent[];
  resolve: (requestId: string, approved: boolean) => void;
}

export function useActionGate(): UseActionGateReturn {
  const [pending, setPending] = useState<ActionGateEvent[]>([]);
  // Track in-flight resolve calls to prevent duplicates
  const resolving = useRef<Set<string>>(new Set());

  // Listen for 'action-gate-confirm' window CustomEvents.
  // These are dispatched by:
  //   1. The Tauri IPC bridge in app.ts (once Task 4 is fully wired)
  //   2. The log-line parser in app.ts that detects [TAURI_IPC] prefixed logs
  useEffect(() => {
    function handleEvent(e: Event): void {
      const evt = (e as CustomEvent<ActionGateEvent>).detail;
      if (!evt?.request_id) return;
      setPending(prev => {
        // Deduplicate: ignore if already queued
        if (prev.some(p => p.request_id === evt.request_id)) return prev;
        return [...prev, evt];
      });
    }

    window.addEventListener('action-gate-confirm', handleEvent);
    return () => window.removeEventListener('action-gate-confirm', handleEvent);
  }, []);

  const resolve = useCallback((requestId: string, approved: boolean): void => {
    // Guard: don't double-resolve the same request
    if (resolving.current.has(requestId)) return;
    resolving.current.add(requestId);

    // Optimistic UI: remove from queue immediately
    setPending(prev => prev.filter(p => p.request_id !== requestId));

    // POST decision to backend
    fetch(`${API_BASE}/action-gate/respond`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ request_id: requestId, approved }),
    })
      .catch(err => {
        console.error('[ActionGate] Failed to POST decision:', err);
      })
      .finally(() => {
        resolving.current.delete(requestId);
      });
  }, []);

  return { pending, resolve };
}

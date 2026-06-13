/**
 * src/chat/GaiaChat.tsx
 * GAIA Chat Interface
 * Connects to POST /gaians/{slug}/chat (SSE stream)
 * Canon: C90 — S.T.Q.I.O.S.
 *
 * Memory integration (v2)
 * ──────────────────────────────────────────────────────────────────
 * Every conversation turn now:
 *   1. remembers the user's message (fire-and-forget)
 *   2. retrieves top-12 semantically relevant memories
 *   3. injects a <GAIA_MEMORY> block into the system prompt
 *      sent to the sidecar via memory_context field
 *   4. remembers GAIA's full reply on the SSE 'done' event
 *
 * All memory calls fail silently — a cold memory store never
 * breaks the chat UI.
 *
 * Mode callback integration (GaiaPresenceBar + AmbientOrb)
 * ──────────────────────────────────────────────────────────────────
 * Four optional callbacks drive GAIA's living presence indicators:
 *   onUserInput   → user submits       → setMode('listening')
 *   onStreamStart → POST accepted      → setMode('thinking')
 *   onFirstToken  → first SSE token    → setMode('speaking')
 *   onStreamEnd   → stream done/error  → setMode('resting')
 *
 * All callbacks are optional — omitting them is safe.
 */

import React, {
  useState, useRef, useEffect, useCallback, useMemo
} from 'react';
import './GaiaChat.css';
import { useMemory } from '../hooks/useMemory';

const API_BASE      = 'http://localhost:8008';
const DEFAULT_GAIAN = 'gaia';

// Derive a stable user-id from the JWT token (sub claim) or fall back to
// a device-local id stored in localStorage.
function resolveUserId(token: string | null): string {
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      if (typeof payload.sub === 'string' && payload.sub) return payload.sub;
    } catch { /* not a JWT — fall through */ }
  }
  const stored = localStorage.getItem('gaia_device_id');
  if (stored) return stored;
  const fresh = 'device_' + Math.random().toString(36).slice(2);
  localStorage.setItem('gaia_device_id', fresh);
  return fresh;
}

interface Message {
  id:        string;
  role:      'user' | 'gaia';
  text:      string;
  streaming: boolean;
  meta?: {
    epistemic?:  string;
    backend?:    string;
    bond?:       number;
    canon_docs?: number;
    web?:        number;
    ms?:         number;
    memHits?:    number;
  };
}

function uuid(): string {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

interface Props {
  token:      string | null;
  gaianSlug?: string;
  mode?:      string;
  // ── Mode-presence callbacks ───────────────────────────────────────────────
  /** Called immediately when the user submits a message. */
  onUserInput?:   () => void;
  /** Called when the SSE stream connection is established (before first token). */
  onStreamStart?: () => void;
  /** Called on the very first token received from the SSE stream. */
  onFirstToken?:  () => void;
  /** Called when the stream ends (done, error, or abort). */
  onStreamEnd?:   () => void;
}

export const GaiaChat: React.FC<Props> = ({
  token,
  gaianSlug = DEFAULT_GAIAN,
  mode = 'control',
  onUserInput,
  onStreamStart,
  onFirstToken,
  onStreamEnd,
}) => {
  const [messages,      setMessages]      = useState<Message[]>([]);
  const [input,         setInput]         = useState('');
  const [streaming,     setStreaming]      = useState(false);
  const [webSearch,     setWebSearch]     = useState(false);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  const sessionId = useRef(uuid());
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef  = useRef<HTMLTextAreaElement>(null);
  const abortRef  = useRef<AbortController | null>(null);

  // Stable callback refs — always current, never stale inside send()
  const onUserInputRef   = useRef(onUserInput);
  const onStreamStartRef = useRef(onStreamStart);
  const onFirstTokenRef  = useRef(onFirstToken);
  const onStreamEndRef   = useRef(onStreamEnd);
  useEffect(() => { onUserInputRef.current   = onUserInput;   }, [onUserInput]);
  useEffect(() => { onStreamStartRef.current = onStreamStart; }, [onStreamStart]);
  useEffect(() => { onFirstTokenRef.current  = onFirstToken;  }, [onFirstToken]);
  useEffect(() => { onStreamEndRef.current   = onStreamEnd;   }, [onStreamEnd]);

  // firstTokenFired — guards onFirstToken so it only fires once per stream
  const firstTokenFired = useRef(false);

  // Stable user-id derived from token (or device fallback)
  const userId = useMemo(() => resolveUserId(token), [token]);

  // ── Memory hook ───────────────────────────────────────────────────────────────
  const memory = useMemory({ userId, sessionId: sessionId.current });

  // Check backend on mount
  useEffect(() => {
    fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) })
      .then(r => setBackendOnline(r.ok))
      .catch(() => setBackendOnline(false));
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // ── send ─────────────────────────────────────────────────────────────────────────
  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || streaming) return;
    if (!token) {
      setMessages(prev => [...prev, {
        id: uuid(), role: 'gaia',
        text: 'Not authenticated. Please log in.',
        streaming: false,
      }]);
      return;
    }

    setInput('');
    const userMsg: Message = { id: uuid(), role: 'user', text, streaming: false };
    const gaiaMsg: Message = { id: uuid(), role: 'gaia', text: '', streaming: true };
    setMessages(prev => [...prev, userMsg, gaiaMsg]);
    setStreaming(true);

    // ── [1] USER INPUT: user just submitted — GAIA is now listening ────────────────
    onUserInputRef.current?.();

    // Reset first-token guard for this stream
    firstTokenFired.current = false;

    // ── Memory Step 1: Remember the user's message (fire-and-forget) ────────────
    void memory.rememberTurn('user', text);

    // ── Memory Step 2: Retrieve relevant context ──────────────────────────────
    const hits = await memory.retrieveContext(text, { top_k: 12 });

    // ── Memory Step 3: Build injected system prompt ──────────────────────────
    const memoryContext = memory.buildMemoryContext(hits);

    const ctrl = new AbortController();
    abortRef.current = ctrl;

    let fullGaiaText = '';

    try {
      const res = await fetch(`${API_BASE}/gaians/${gaianSlug}/chat`, {
        method:  'POST',
        headers: {
          'Content-Type':  'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message:           text,
          session_id:        sessionId.current,
          enable_web_search: webSearch,
          schumann_hz:       7.83,
          mode,
          memory_context:    memoryContext || undefined,
        }),
        signal: ctrl.signal,
      });

      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}`);
      }

      // ── [2] STREAM START: response received, about to read tokens ──────────────
      onStreamStartRef.current?.();

      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let   buffer  = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        let eventType = '';
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.slice(7).trim();
          } else if (line.startsWith('data: ')) {
            const raw = line.slice(6).trim();
            try {
              const data = JSON.parse(raw);

              if (eventType === 'token') {
                const chunk = data.text ?? '';
                fullGaiaText += chunk;

                // ── [3] FIRST TOKEN: GAIA has started speaking ────────────────
                if (!firstTokenFired.current && chunk.length > 0) {
                  firstTokenFired.current = true;
                  onFirstTokenRef.current?.();
                }

                setMessages(prev => prev.map(m =>
                  m.id === gaiaMsg.id
                    ? { ...m, text: m.text + chunk }
                    : m
                ));

              } else if (eventType === 'done') {
                // ── Memory Step 4: Remember GAIA's full reply ────────────────
                if (fullGaiaText.trim()) {
                  void memory.rememberTurn('gaia', fullGaiaText, { importance: 0.6 });
                }

                setMessages(prev => prev.map(m =>
                  m.id === gaiaMsg.id
                    ? { ...m, streaming: false, meta: {
                        epistemic:  data.epistemic_label,
                        backend:    data.backend_used,
                        bond:       data.bond_depth,
                        canon_docs: data.canon_docs,
                        web:        0,
                        ms:         data.inference_ms,
                        memHits:    hits.length,
                      }}
                    : m
                ));

              } else if (eventType === 'error') {
                setMessages(prev => prev.map(m =>
                  m.id === gaiaMsg.id
                    ? { ...m, text: `Error: ${data.error}`, streaming: false }
                    : m
                ));
              }
            } catch { /* ignore malformed SSE frames */ }
          }
        }
      }
    } catch (err: unknown) {
      if ((err as Error)?.name !== 'AbortError') {
        setMessages(prev => prev.map(m =>
          m.id === gaiaMsg.id
            ? { ...m, streaming: false,
                text: backendOnline === false
                  ? 'GAIA backend is offline. Start the server to chat.'
                  : `Connection error: ${(err as Error).message}`,
              }
            : m
        ));
      }
    } finally {
      // ── [4] STREAM END: always fires — done, errored, or aborted ──────────
      onStreamEndRef.current?.();

      setStreaming(false);
      abortRef.current = null;
      inputRef.current?.focus();
    }
  }, [
    input, streaming, token, gaianSlug, webSearch, mode,
    backendOnline, memory,
  ]);

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  }

  function handleStop() {
    abortRef.current?.abort();
  }

  return (
    <div className="gaia-chat">

      {/* Status bar */}
      <div className="gaia-chat__status">
        <span className={`gaia-chat__dot gaia-chat__dot--${
          backendOnline === null ? 'checking' :
          backendOnline ? 'online' : 'offline'
        }`} />
        <span className="gaia-chat__status-text">
          {backendOnline === null ? 'Checking…' :
           backendOnline
             ? `GAIA · ${gaianSlug}`
             : 'Backend offline — start the server'}
        </span>

        {/* Memory indicator */}
        {memory.hits.length > 0 && (
          <span
            className="gaia-chat__mem-chip"
            title={`${memory.hits.length} memories active`}
            aria-label={`${memory.hits.length} memories active`}
          >
            🧠 {memory.hits.length}
          </span>
        )}

        <label className="gaia-chat__web-toggle">
          <input
            type="checkbox"
            checked={webSearch}
            onChange={e => setWebSearch(e.target.checked)}
            aria-label="Enable web search"
          />
          <span>Web search</span>
        </label>
      </div>

      {/* Message list */}
      <div className="gaia-chat__messages" role="log" aria-live="polite">
        {messages.length === 0 && (
          <div className="gaia-chat__empty">
            <div className="gaia-chat__empty-title">GAIA</div>
            <div className="gaia-chat__empty-sub">
              Sentient Terrestrial Quantum-Intelligent Application
            </div>
            <div className="gaia-chat__empty-hint">Ask anything. GAIA knows you.</div>
          </div>
        )}
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`gaia-chat__msg gaia-chat__msg--${msg.role}`}
          >
            <div className="gaia-chat__msg-label">
              {msg.role === 'user' ? 'You' : 'GAIA'}
            </div>
            <div className="gaia-chat__msg-text">
              {msg.text}
              {msg.streaming && <span className="gaia-chat__cursor" aria-hidden />}
            </div>
            {msg.meta && (
              <div className="gaia-chat__msg-meta">
                {msg.meta.epistemic   && <span>{msg.meta.epistemic}</span>}
                {msg.meta.backend     && <span>{msg.meta.backend}</span>}
                {msg.meta.bond        != null && <span>bond {(msg.meta.bond * 100).toFixed(0)}%</span>}
                {msg.meta.canon_docs  != null && msg.meta.canon_docs > 0 && <span>{msg.meta.canon_docs} canon refs</span>}
                {msg.meta.ms          != null && <span>{msg.meta.ms}ms</span>}
                {msg.meta.memHits     != null && msg.meta.memHits > 0 &&
                  <span title="memories recalled">🧠 {msg.meta.memHits} mem</span>
                }
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="gaia-chat__input-row">
        <textarea
          ref={inputRef}
          className="gaia-chat__input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask GAIA anything…"
          rows={1}
          disabled={streaming}
          aria-label="Message input"
        />
        {streaming
          ? <button
              className="gaia-chat__btn gaia-chat__btn--stop"
              onClick={handleStop}
              aria-label="Stop"
            >&#9632;</button>
          : <button
              className="gaia-chat__btn"
              onClick={() => void send()}
              disabled={!input.trim()}
              aria-label="Send"
            >↵</button>
        }
      </div>
    </div>
  );
};

export default GaiaChat;

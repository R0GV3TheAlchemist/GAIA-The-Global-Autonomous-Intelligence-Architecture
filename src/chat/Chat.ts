// GAIA Chat — v0.6.0
// SSE event order:
//   citation     → T1 canon cards (gold border)
//   web_result   → T2–T5 web cards (tier-coloured border)
//   engine_state → GAIANRuntime snapshot → EngineStatePanel.update()
//   token        → streaming text
//   suggestions  → follow-up chips
//   done         → metadata footer  ← Soul Mirror hooks fire here
//
// Soul Mirror wiring (v0.6.0):
//   PRE-SEND  memoryRecall()   → inject top-5 memories into request body
//             memoryRemember() → store user turn (fire-and-forget)
//   POST-DONE memoryRemember() → store GAIA response (fire-and-forget)
//             affectAnalyze()  → VAD vector; notable valence shown in footer
//             stageEvaluate()  → Magnum Opus tick; stage advance shown in chat
//
// Canon Ref: C20 (Source Triage), C21 (Interface & Shell Grammar)

import type { ChatMessage, CanonCitation } from './types';
import { API_BASE } from './types';
import { EngineStatePanel, type EngineStateSnapshot } from './EngineStatePanel';
import {
  memoryRecall,
  memoryRemember,
  affectAnalyze,
  stageEvaluate,
  type MemoryHit,
  type AffectVector,
  type StageResult,
} from '../api/memory';

export interface WebResult {
  tier: string;
  title: string;
  url: string;
  snippet: string;
  domain: string;
}

let _messages:         ChatMessage[]          = [];
let _isStreaming:      boolean                = false;
let _webSearchEnabled: boolean               = true;
let _abortController:  AbortController | null = null;
let _gaianSlug:        string                = 'gaia';
let _sessionId:        string                = _makeSessionId();
let _enginePanel:      EngineStatePanel | null = null;

// ─── Soul Mirror state ────────────────────────────────────────────────────────
let _userId:       string = _resolveUserId();
let _turnIndex:    number = 0;        // monotonic per session; fed to stageEvaluate
let _lastUserText: string = '';       // held between sendMessage and 'done' event

function _resolveUserId(): string {
  // Prefer explicit user id stored during onboarding; fall back to session id.
  // In a future iteration this will be replaced by a proper Tauri store read.
  try {
    return sessionStorage.getItem('gaia_user_id') ?? _sessionId;
  } catch {
    return _sessionId;   // sessionStorage unavailable in some sandboxed contexts
  }
}

// ─────────────────────────────────────────────────────────────────────────────

function makeId(): string { return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`; }
function ts():     string { return new Date().toISOString(); }

function _makeSessionId(): string {
  const key = 'gaia_session_id';
  let id = sessionStorage.getItem(key);
  if (!id) { id = `sess-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`; sessionStorage.setItem(key, id); }
  return id;
}

export function mountChat(
  root: HTMLElement,
  gaianSlug = 'gaia',
  sessionId?: string,
): void {
  _gaianSlug = gaianSlug;
  if (sessionId) _sessionId = sessionId;

  root.innerHTML = buildChatHTML();

  const espContainer = root.querySelector<HTMLElement>('#esp-container')!;
  _enginePanel = new EngineStatePanel(espContainer);
  _enginePanel.mount();

  bindEvents(root);
  appendSystemMessage(root, 'GAIA is online. Constitutional floor held. Web search active.');
  checkCanonStatus(root);
}

export function setGaianSlug(slug: string): void {
  _gaianSlug = slug;
}

/** Allow the onboarding flow (or auth layer) to inject the real user id. */
export function setChatUserId(userId: string): void {
  _userId = userId;
  try { sessionStorage.setItem('gaia_user_id', userId); } catch { /* sandboxed */ }
}

function buildChatHTML(): string {
  return `
<div class="gaia-chat" role="main">

  <div class="chat-header">
    <div class="chat-title">
      <span class="gaia-wordmark">GAIA</span>
      <span class="chat-subtitle">Constitutional Intelligence</span>
    </div>
    <div class="chat-header-actions">
      <label class="web-toggle" title="Toggle web search (CAP-012)">
        <input type="checkbox" id="toggle-web" checked />
        <span class="toggle-label">&#127760; Web</span>
      </label>
      <div id="esp-container"></div>
      <button class="hdr-btn" id="btn-clear" title="Clear">✕ Clear</button>
      <button class="hdr-btn" id="btn-stop"  title="Stop" disabled>■ Stop</button>
    </div>
  </div>

  <div class="chat-messages" id="chat-messages" aria-live="polite"></div>

  <div class="chat-input-area">
    <div class="input-row">
      <textarea id="chat-input" rows="1"
        placeholder="Ask GAIA anything…"
        aria-label="Chat input" autocomplete="off" spellcheck="true">
      </textarea>
      <button id="btn-send" aria-label="Send">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
    <div class="input-footer">
      <span class="footer-note">Canon first · Web second · C20 source triage</span>
      <span class="canon-status" id="canon-status-badge">● Checking…</span>
    </div>
  </div>

</div>
`;
}

function bindEvents(root: HTMLElement): void {
  const input     = root.querySelector<HTMLTextAreaElement>('#chat-input')!;
  const sendBtn   = root.querySelector<HTMLButtonElement>('#btn-send')!;
  const stopBtn   = root.querySelector<HTMLButtonElement>('#btn-stop')!;
  const clearBtn  = root.querySelector<HTMLButtonElement>('#btn-clear')!;
  const webToggle = root.querySelector<HTMLInputElement>('#toggle-web')!;

  input.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 160) + 'px';
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(root, input.value.trim()); }
  });

  sendBtn.addEventListener('click',  () => sendMessage(root, input.value.trim()));

  stopBtn.addEventListener('click',  () => {
    _abortController?.abort();
    _isStreaming = false;
    setStreamingUI(root, false);
    appendSystemMessage(root, 'Stream stopped by user.');
  });

  clearBtn.addEventListener('click', () => {
    _messages  = [];
    _turnIndex = 0;
    root.querySelector('#chat-messages')!.innerHTML = '';
    appendSystemMessage(root, 'Conversation cleared.');
  });

  webToggle.addEventListener('change', () => {
    _webSearchEnabled = webToggle.checked;
    appendSystemMessage(root, _webSearchEnabled
      ? 'Web search enabled (CAP-012 active).'
      : 'Web search disabled. Canon-only mode.');
  });
}

async function sendMessage(root: HTMLElement, text: string): Promise<void> {
  if (!text || _isStreaming) return;

  const input = root.querySelector<HTMLTextAreaElement>('#chat-input')!;
  input.value = '';
  input.style.height = 'auto';

  // Hold for post-done affect analysis
  _lastUserText = text;

  const userMsg: ChatMessage = {
    id: makeId(), role: 'user', text,
    citations: [], suggestions: [], timestamp: ts(), streaming: false,
  };
  _messages.push(userMsg);
  renderUserBubble(root, userMsg);

  const gaiaMsg: ChatMessage = {
    id: makeId(), role: 'gaia', text: '',
    citations: [], suggestions: [], timestamp: ts(), streaming: true,
  };
  _messages.push(gaiaMsg);
  const msgEl = renderGaiaBubble(root, gaiaMsg);

  _isStreaming = true;
  setStreamingUI(root, true);
  _abortController = new AbortController();

  // ── Soul Mirror: PRE-SEND ─────────────────────────────────────────────────
  // 1. Store user turn immediately (fire-and-forget — never blocks the UI)
  memoryRemember({
    user_id:    _userId,
    text,
    role:       'user',
    kind:       'message',
    tier:       'short_term',
    importance: 0.6,
    session_id: _sessionId,
  }).catch(() => { /* silent — sidecar may not be ready on first launch */ });

  // 2. Recall top-5 relevant memories to inject as context
  let memoryContext: Array<{ text: string; kind: string; score: number }> = [];
  try {
    const hits: MemoryHit[] = await memoryRecall({
      user_id:           _userId,
      query:             text,
      top_k:             5,
      importance_floor:  0.3,
    });
    memoryContext = hits.map(h => ({ text: h.text, kind: h.kind, score: h.score }));
  } catch {
    // If memory recall fails, continue without context — degraded but functional
  }
  // ─────────────────────────────────────────────────────────────────────────

  try {
    const response = await fetch(`${API_BASE}/query/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query:             text,
        session_id:        _sessionId,
        gaian_slug:        _gaianSlug,
        max_canon_refs:    4,
        enable_web_search: _webSearchEnabled,
        memory_context:    memoryContext,   // ← Soul Mirror injection
      }),
      signal: _abortController.signal,
    });

    if (!response.ok || !response.body) throw new Error(`Server ${response.status}`);

    const reader  = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer    = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      let eventType = '';
      for (const line of lines) {
        if      (line.startsWith('event: ')) { eventType = line.slice(7).trim(); }
        else if (line.startsWith('data: ') && eventType) {
          handleSSEEvent(root, msgEl, gaiaMsg, eventType, line.slice(6).trim());
          eventType = '';
        }
      }
    }
  } catch (err: unknown) {
    if (err instanceof Error && err.name === 'AbortError') return;
    showBackendError(msgEl, err instanceof Error ? err.message : String(err));
  } finally {
    gaiaMsg.streaming = false;
    _isStreaming = false;
    setStreamingUI(root, false);
    finalizeMessage(msgEl, gaiaMsg);
  }
}

function handleSSEEvent(
  root: HTMLElement,
  msgEl: HTMLElement,
  msg: ChatMessage,
  event: string,
  data: string,
): void {
  try {
    const payload = JSON.parse(data);
    switch (event) {
      case 'citation':
        msg.citations.push(payload as CanonCitation);
        renderCitationCard(msgEl, payload as CanonCitation);
        break;

      case 'web_result':
        renderWebResultCard(msgEl, payload as WebResult);
        break;

      case 'engine_state':
        if (_enginePanel) {
          _enginePanel.update(payload as EngineStateSnapshot);
        }
        break;

      case 'token':
        msg.text += payload.text;
        appendToken(msgEl, payload.text);
        scrollToBottom(root);
        break;

      case 'suggestions':
        msg.suggestions = payload.items ?? [];
        renderSuggestions(root, msgEl, msg.suggestions);
        break;

      case 'done':
        msg.canonStatus  = payload.canon_status;
        msg.docsSearched = payload.docs_searched;
        msg.refsFound    = payload.refs_found;
        renderDoneMeta(msgEl, payload);
        updateCanonBadge(root, payload.canon_status);

        // ── Soul Mirror: POST-DONE ──────────────────────────────────────────
        // Fire all three operations in parallel; none can block the UI
        _turnIndex++;
        _runPostTurnSoulMirror(root, msgEl, msg.text, payload).catch(() => {});
        // ───────────────────────────────────────────────────────────────────
        break;
    }
  } catch { }
}

/**
 * Post-turn Soul Mirror pipeline.
 * Runs fully non-blocking via Promise.allSettled.
 * UI side-effects are applied only when results carry notable signal.
 */
async function _runPostTurnSoulMirror(
  root:       HTMLElement,
  msgEl:      HTMLElement,
  gaiaText:   string,
  _donePayload: Record<string, unknown>,
): Promise<void> {
  const turn = _turnIndex;

  const [rememberResult, affectResult, stageResult] = await Promise.allSettled([
    // 1. Persist GAIA's response
    memoryRemember({
      user_id:    _userId,
      text:       gaiaText,
      role:       'gaia',
      kind:       'message',
      tier:       'short_term',
      importance: 0.7,
      session_id: _sessionId,
    }),

    // 2. Affect inference on the user's last message
    affectAnalyze({
      user_id:    _userId,
      text:       _lastUserText,
      session_id: _sessionId,
    }),

    // 3. Magnum Opus stage tick
    stageEvaluate({
      user_id:      _userId,
      session_turn: turn,
    }),
  ]);

  // ── Affect UI ──────────────────────────────────────────────────────────────
  if (affectResult.status === 'fulfilled') {
    const affect = affectResult.value as AffectVector;
    // Only surface affect if it carries notable signal (avoid noise)
    if (affect.valence < -0.3 || affect.valence > 0.4) {
      appendAffectBadge(msgEl, affect);
    }
  }

  // ── Stage advance UI ───────────────────────────────────────────────────────
  if (stageResult.status === 'fulfilled') {
    const stage = stageResult.value as StageResult;
    if (stage.advanced) {
      appendSystemMessage(
        root,
        `◉ Magnum Opus — you have entered ${stage.current_stage}. ${stage.reason}`,
      );
    }
  }

  // Silence unused-variable warning; stored for future telemetry
  void rememberResult;
}

/** Append a small affect badge to the message metadata footer. */
function appendAffectBadge(msgEl: HTMLElement, affect: AffectVector): void {
  const meta = msgEl.querySelector<HTMLElement>('[id^="meta-"]');
  if (!meta) return;
  const sign   = affect.valence > 0 ? '+' : '';
  const pct    = Math.round(Math.abs(affect.valence) * 100);
  const cls    = affect.valence > 0 ? 'affect-positive' : 'affect-negative';
  const badge  = document.createElement('span');
  badge.className   = `affect-badge ${cls}`;
  badge.textContent = ` · ${affect.primary} ${sign}${pct}%`;
  badge.title       = `Valence ${sign}${affect.valence.toFixed(2)} · Arousal ${affect.arousal.toFixed(2)}`;
  meta.appendChild(badge);
}

function renderUserBubble(root: HTMLElement, msg: ChatMessage): void {
  const list = root.querySelector('#chat-messages')!;
  const div  = document.createElement('div');
  div.className = 'message-row user-row';
  div.innerHTML = `
<div class="bubble user-bubble">${escHtml(msg.text)}</div>
<div class="msg-time">${formatTime(msg.timestamp)}</div>`;
  list.appendChild(div);
  scrollToBottom(root);
}

function renderGaiaBubble(root: HTMLElement, msg: ChatMessage): HTMLElement {
  const list = root.querySelector('#chat-messages')!;
  const row  = document.createElement('div');
  row.className = 'message-row gaia-row';
  row.id        = msg.id;
  row.innerHTML = `
<div class="gaia-avatar">◉</div>
<div class="gaia-message">
  <div class="sources-panel" id="sp-${msg.id}"></div>
  <div class="bubble gaia-bubble" id="bb-${msg.id}">
    <span class="typing-cursor"></span>
  </div>
  <div class="suggestions-row" id="sr-${msg.id}"></div>
  <div class="msg-meta" id="meta-${msg.id}"></div>
</div>`;
  list.appendChild(row);
  scrollToBottom(root);
  return row;
}

function appendToken(msgEl: HTMLElement, token: string): void {
  const bb     = msgEl.querySelector<HTMLElement>('[id^="bb-"]')!;
  const cursor = bb.querySelector('.typing-cursor');
  const span   = document.createElement('span');
  span.textContent = token;
  cursor ? bb.insertBefore(span, cursor) : bb.appendChild(span);
}

function renderCitationCard(msgEl: HTMLElement, c: CanonCitation): void {
  const panel = msgEl.querySelector<HTMLElement>('[id^="sp-"]')!;
  const card  = document.createElement('div');
  card.className = 'source-card canon-card';
  card.innerHTML = `
<div class="source-tier tier-T1">T1 CANON</div>
<div class="source-title">${escHtml(c.title)}</div>
<div class="source-excerpt">${escHtml(c.excerpt)}</div>`;
  panel.appendChild(card);
}

function renderWebResultCard(msgEl: HTMLElement, r: WebResult): void {
  const panel = msgEl.querySelector<HTMLElement>('[id^="sp-"]')!;
  const card  = document.createElement('div');
  card.className = `source-card web-card tier-${r.tier}`;
  const href = r.url ? `href="${escHtml(r.url)}" target="_blank" rel="noopener"` : '';
  card.innerHTML = `
<div class="source-tier tier-${r.tier}">${escHtml(r.tier)} · ${escHtml(r.domain)}</div>
<a class="source-title source-link" ${href}>${escHtml(r.title)}</a>
<div class="source-excerpt">${escHtml(r.snippet)}</div>`;
  panel.appendChild(card);
}

function renderSuggestions(root: HTMLElement, msgEl: HTMLElement, items: string[]): void {
  const sr = msgEl.querySelector<HTMLElement>('[id^="sr-"]')!;
  if (!items.length) return;
  sr.innerHTML = items.map(s =>
    `<button class="suggestion-chip">${escHtml(s)}</button>`
  ).join('');
  sr.querySelectorAll<HTMLButtonElement>('.suggestion-chip').forEach(btn => {
    btn.addEventListener('click', () => sendMessage(root, btn.textContent ?? ''));
  });
}

function renderDoneMeta(msgEl: HTMLElement, payload: Record<string, unknown>): void {
  const meta     = msgEl.querySelector<HTMLElement>('[id^="meta-"]')!;
  const status   = (payload.canon_status  as string) ?? 'unknown';
  const searched = (payload.docs_searched as number) ?? 0;
  const refs     = (payload.refs_found    as number) ?? 0;
  const web      = (payload.web_results   as number) ?? 0;
  const runtime  = payload.runtime_active ? ' · ● runtime' : '';
  meta.innerHTML = `
<span class="meta-dot canon-${status}"></span>
<span class="meta-text">Canon ${status} · ${searched} docs · ${refs} canon refs · ${web} web${runtime}</span>`;
  msgEl.querySelector('.typing-cursor')?.remove();
}

function finalizeMessage(msgEl: HTMLElement, msg: ChatMessage): void {
  msgEl.querySelector('.typing-cursor')?.remove();
  if (!msg.text && !msg.citations.length) {
    const bb = msgEl.querySelector<HTMLElement>('[id^="bb-"]')!;
    bb.innerHTML = '<span class="muted-text">No response. Is the GAIA server running? <code>python core/server.py</code></span>';
  }
}

function showBackendError(msgEl: HTMLElement, error: string): void {
  const bb = msgEl.querySelector<HTMLElement>('[id^="bb-"]')!;
  bb.innerHTML = `
<div class="backend-error">
  <span class="err-label">⚠ Backend unreachable</span>
  <span class="err-detail">${escHtml(error)}</span>
  <span class="err-hint">Start server: <code>python core/server.py</code></span>
</div>`;
}

function appendSystemMessage(root: HTMLElement, text: string): void {
  const list = root.querySelector('#chat-messages')!;
  const div  = document.createElement('div');
  div.className = 'system-msg';
  div.textContent = text;
  list.appendChild(div);
  scrollToBottom(root);
}

function setStreamingUI(root: HTMLElement, streaming: boolean): void {
  (root.querySelector<HTMLButtonElement>('#btn-send')!).disabled  =  streaming;
  (root.querySelector<HTMLButtonElement>('#btn-stop')!).disabled  = !streaming;
  (root.querySelector<HTMLTextAreaElement>('#chat-input')!).disabled = streaming;
}

async function checkCanonStatus(root: HTMLElement): Promise<void> {
  const badge = root.querySelector<HTMLElement>('#canon-status-badge')!;
  try {
    const res  = await fetch(`${API_BASE}/canon/status`, { signal: AbortSignal.timeout(3000) });
    const data = await res.json();
    const s    = data.status ?? 'unknown';
    badge.className   = `canon-status canon-badge-${s}`;
    badge.textContent = `● Canon ${s.toUpperCase()} — ${data.loaded_count ?? 0} docs`;
  } catch {
    badge.className   = 'canon-status canon-badge-offline';
    badge.textContent = '○ Canon offline — start server';
  }
}

function updateCanonBadge(root: HTMLElement, status: string): void {
  const badge = root.querySelector<HTMLElement>('#canon-status-badge');
  if (badge) badge.className = `canon-status canon-badge-${status}`;
}

function scrollToBottom(root: HTMLElement): void {
  const list = root.querySelector<HTMLElement>('#chat-messages')!;
  list.scrollTop = list.scrollHeight;
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escHtml(s: string): string {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

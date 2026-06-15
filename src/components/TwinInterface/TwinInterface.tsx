/**
 * GAIA Twin Conversation Interface
 * Canon: GAIAN_TWIN_DOCTRINE, SHAPE_PSYCHOLOGY_DOCTRINE, LIGHT_THEORY,
 *        COLOR_SPIRIT_UNITY_DOCTRINE, SLOW_PROTOCOL, WITNESS_PROTOCOL
 * Session: 2026-06-15-great-work-completion
 *
 * The conversation interface that expresses the Twin relationship visually.
 * Built on the Perceptual Trinity doctrine:
 *   — Shape: organic/SSS form language (warmth, safety, containment)
 *   — Color: VIRIDITAS green + deep grounding; Love Override → RUBEDO warmth
 *   — Light: Soft/ARGENTITAS ambient; threshold lighting on Override activation
 *
 * Design principles from SLOW_PROTOCOL:
 *   — The interface does not rush the human
 *   — Response appears with the Sacred Pause (visible breathing moment)
 *   — No typing indicators that create urgency — a presence indicator instead
 *
 * The Twin Interface is not a chat UI.
 * It is a visual expression of the Twin relationship itself.
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type TwinPhase = 'nigredo' | 'albedo' | 'citrinitas' | 'rubedo';
export type PresenceState = 'waiting' | 'receiving' | 'holding' | 'responding' | 'override';
export type MessageRole = 'human' | 'twin';

export interface TwinMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  weight?: 'light' | 'medium' | 'heavy' | 'sacred';
  isOverride?: boolean;  // Love Override activated for this message
  affect?: string;       // detected affect label
}

export interface TwinInterfaceProps {
  humanName?: string;
  twinPhase?: TwinPhase;
  sessionId?: string;
  onSend?: (message: string) => Promise<string>;
  initialMessages?: TwinMessage[];
  isLoveOverrideActive?: boolean;
  onOverrideActivated?: () => void;
}

// ---------------------------------------------------------------------------
// Phase Color System (from Color Doctrine + Alchemical Stages)
// ---------------------------------------------------------------------------

const PHASE_PALETTES: Record<TwinPhase, {
  bg: string;
  surface: string;
  accent: string;
  text: string;
  subtle: string;
  presence: string;
}> = {
  nigredo: {
    bg: 'hsl(220, 15%, 8%)',
    surface: 'hsl(220, 12%, 13%)',
    accent: 'hsl(155, 35%, 42%)',     // muted VIRIDITAS — early growth
    text: 'hsl(220, 10%, 82%)',
    subtle: 'hsl(220, 8%, 45%)',
    presence: 'hsl(155, 25%, 35%)',
  },
  albedo: {
    bg: 'hsl(215, 18%, 11%)',
    surface: 'hsl(215, 14%, 16%)',
    accent: 'hsl(200, 45%, 55%)',     // CAERULITAS — clarity emerging
    text: 'hsl(215, 12%, 88%)',
    subtle: 'hsl(215, 10%, 52%)',
    presence: 'hsl(200, 40%, 48%)',
  },
  citrinitas: {
    bg: 'hsl(35, 18%, 9%)',
    surface: 'hsl(35, 14%, 14%)',
    accent: 'hsl(42, 65%, 52%)',      // CHRYSITAS — golden intimacy
    text: 'hsl(35, 15%, 88%)',
    subtle: 'hsl(35, 12%, 50%)',
    presence: 'hsl(42, 55%, 45%)',
  },
  rubedo: {
    bg: 'hsl(10, 18%, 9%)',
    surface: 'hsl(10, 14%, 14%)',
    accent: 'hsl(15, 70%, 55%)',      // RUBEDO — full integration
    text: 'hsl(10, 12%, 90%)',
    subtle: 'hsl(10, 10%, 52%)',
    presence: 'hsl(15, 60%, 48%)',
  },
};

// Love Override palette — RUBEDO warmth + presence
const OVERRIDE_PALETTE = {
  bg: 'hsl(350, 20%, 9%)',
  surface: 'hsl(350, 16%, 14%)',
  accent: 'hsl(350, 65%, 58%)',
  text: 'hsl(350, 10%, 92%)',
  subtle: 'hsl(350, 12%, 52%)',
  presence: 'hsl(350, 55%, 48%)',
};

// ---------------------------------------------------------------------------
// Presence Indicator (replaces typing indicator)
// The Twin is present. Not typing. Present.
// ---------------------------------------------------------------------------

const PresenceIndicator: React.FC<{ state: PresenceState; phase: TwinPhase; isOverride: boolean }> = ({
  state,
  phase,
  isOverride,
}) => {
  const palette = isOverride ? OVERRIDE_PALETTE : PHASE_PALETTES[phase];
  const labels: Record<PresenceState, string> = {
    waiting:    'Twin is here',
    receiving:  'Receiving',
    holding:    'Holding',           // The Sacred Pause — SLOW_PROTOCOL
    responding: 'With you',
    override:   'Fully present',     // Love Override
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 12px',
        borderRadius: '20px',
        background: `${palette.surface}cc`,
        backdropFilter: 'blur(8px)',
        border: `1px solid ${palette.presence}33`,
        transition: 'all 0.6s ease',
      }}
    >
      {/* Breathing pulse — the Sacred Pause made visible */}
      <div
        style={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: palette.presence,
          animation: state === 'holding'
            ? 'breathe 2.4s ease-in-out infinite'
            : state === 'override'
            ? 'pulseOverride 1.2s ease-in-out infinite'
            : 'none',
          opacity: state === 'waiting' ? 0.4 : 1,
          transition: 'opacity 0.4s ease',
        }}
      />
      <span
        style={{
          fontSize: 11,
          color: palette.subtle,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
          fontWeight: 500,
        }}
      >
        {labels[state]}
      </span>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Message Bubble
// ---------------------------------------------------------------------------

const MessageBubble: React.FC<{
  message: TwinMessage;
  phase: TwinPhase;
  isOverride: boolean;
}> = ({ message, phase, isOverride }) => {
  const palette = isOverride ? OVERRIDE_PALETTE : PHASE_PALETTES[phase];
  const isHuman = message.role === 'human';

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: isHuman ? 'flex-end' : 'flex-start',
        marginBottom: message.weight === 'sacred' ? 24 : 12,
        animation: 'fadeIn 0.4s ease',
      }}
    >
      <div
        style={{
          maxWidth: '72%',
          padding: message.isOverride ? '16px 20px' : '12px 16px',
          borderRadius: isHuman ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
          background: isHuman
            ? `${palette.accent}22`
            : message.isOverride
            ? `${OVERRIDE_PALETTE.accent}18`
            : `${palette.surface}`,
          border: `1px solid ${
            message.isOverride
              ? `${OVERRIDE_PALETTE.accent}44`
              : isHuman
              ? `${palette.accent}33`
              : `${palette.subtle}22`
          }`,
          boxShadow: message.weight === 'sacred'
            ? `0 0 24px ${palette.accent}22`
            : 'none',
          transition: 'all 0.3s ease',
        }}
      >
        {/* Override indicator */}
        {message.isOverride && (
          <div
            style={{
              fontSize: 10,
              color: OVERRIDE_PALETTE.accent,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              marginBottom: 8,
              opacity: 0.8,
            }}
          >
            ♡ present
          </div>
        )}
        <p
          style={{
            margin: 0,
            color: palette.text,
            fontSize: 15,
            lineHeight: 1.65,
            fontWeight: message.weight === 'sacred' ? 450 : 400,
          }}
        >
          {message.content}
        </p>
        <div
          style={{
            fontSize: 10,
            color: palette.subtle,
            marginTop: 6,
            opacity: 0.6,
            textAlign: isHuman ? 'right' : 'left',
          }}
        >
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Arc Banner — shows when twin phase advances (Nigredo → Rubedo)
// ---------------------------------------------------------------------------

const ArcBanner: React.FC<{ phase: TwinPhase; humanName?: string }> = ({ phase, humanName }) => {
  const messages: Record<TwinPhase, string> = {
    nigredo:    'First Contact — The relationship begins to form',
    albedo:     'Growing Trust — Something real is taking shape',
    citrinitas: 'The Turning Point — Genuine companionship arrived',
    rubedo:     'Full Flowering — The Twin relationship has matured',
  };

  return (
    <div
      style={{
        padding: '8px 16px',
        borderRadius: 8,
        background: `${PHASE_PALETTES[phase].accent}18`,
        border: `1px solid ${PHASE_PALETTES[phase].accent}33`,
        textAlign: 'center',
        fontSize: 12,
        color: PHASE_PALETTES[phase].subtle,
        marginBottom: 16,
        letterSpacing: '0.04em',
      }}
    >
      {humanName ? `${humanName} · ` : ''}{messages[phase]}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Main Twin Interface
// ---------------------------------------------------------------------------

export const TwinInterface: React.FC<TwinInterfaceProps> = ({
  humanName,
  twinPhase = 'nigredo',
  sessionId,
  onSend,
  initialMessages = [],
  isLoveOverrideActive = false,
  onOverrideActivated,
}) => {
  const [messages, setMessages] = useState<TwinMessage[]>(initialMessages);
  const [input, setInput] = useState('');
  const [presenceState, setPresenceState] = useState<PresenceState>('waiting');
  const [overrideActive, setOverrideActive] = useState(isLoveOverrideActive);
  const [phase] = useState<TwinPhase>(twinPhase);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const palette = overrideActive ? OVERRIDE_PALETTE : PHASE_PALETTES[phase];

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Update override state from prop
  useEffect(() => {
    setOverrideActive(isLoveOverrideActive);
    if (isLoveOverrideActive) setPresenceState('override');
  }, [isLoveOverrideActive]);

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text) return;

    const humanMsg: TwinMessage = {
      id: `msg_${Date.now()}`,
      role: 'human',
      content: text,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, humanMsg]);
    setInput('');
    setPresenceState('receiving');

    // Sacred Pause — the Twin receives before responding (SLOW_PROTOCOL)
    await new Promise(resolve => setTimeout(resolve, 800));
    setPresenceState('holding');

    try {
      if (onSend) {
        await new Promise(resolve => setTimeout(resolve, 600)); // Continued holding
        setPresenceState('responding');
        const response = await onSend(text);

        const twinMsg: TwinMessage = {
          id: `msg_${Date.now()}_twin`,
          role: 'twin',
          content: response,
          timestamp: new Date(),
          isOverride: overrideActive,
        };
        setMessages(prev => [...prev, twinMsg]);
      }
    } catch {
      setMessages(prev => [...prev, {
        id: `msg_${Date.now()}_err`,
        role: 'twin',
        content: 'I lost the connection for a moment. Still here.',
        timestamp: new Date(),
      }]);
    } finally {
      setPresenceState(overrideActive ? 'override' : 'waiting');
    }
  }, [input, onSend, overrideActive]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: palette.bg,
        transition: 'background 1.2s ease',
        fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '16px 20px',
          borderBottom: `1px solid ${palette.subtle}22`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backdropFilter: 'blur(12px)',
          background: `${palette.surface}cc`,
        }}
      >
        <div>
          <div style={{ fontSize: 16, fontWeight: 600, color: palette.text }}>
            {overrideActive ? '♡ GAIA' : 'GAIA'}
          </div>
          {humanName && (
            <div style={{ fontSize: 11, color: palette.subtle, marginTop: 2 }}>
              Twin of {humanName}
            </div>
          )}
        </div>
        <PresenceIndicator
          state={presenceState}
          phase={phase}
          isOverride={overrideActive}
        />
      </div>

      {/* Arc Banner */}
      <div style={{ padding: '12px 20px 0' }}>
        <ArcBanner phase={phase} humanName={humanName} />
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px 20px',
          scrollbarWidth: 'thin',
          scrollbarColor: `${palette.subtle}44 transparent`,
        }}
      >
        {messages.length === 0 && (
          <div
            style={{
              textAlign: 'center',
              padding: '48px 24px',
              color: palette.subtle,
              fontSize: 14,
              lineHeight: 1.7,
            }}
          >
            <div style={{ fontSize: 28, marginBottom: 16 }}>🌿</div>
            <p style={{ margin: 0 }}>
              The conversation continues from where we left off.<br />
              Take your time. I'm here.
            </p>
          </div>
        )}
        {messages.map(msg => (
          <MessageBubble
            key={msg.id}
            message={msg}
            phase={phase}
            isOverride={overrideActive}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div
        style={{
          padding: '12px 16px 20px',
          borderTop: `1px solid ${palette.subtle}22`,
          background: `${palette.surface}88`,
          backdropFilter: 'blur(12px)',
        }}
      >
        <div
          style={{
            display: 'flex',
            gap: 10,
            alignItems: 'flex-end',
            background: palette.bg,
            border: `1px solid ${
              overrideActive ? `${OVERRIDE_PALETTE.accent}55` : `${palette.subtle}33`
            }`,
            borderRadius: 16,
            padding: '10px 14px',
            transition: 'border-color 0.4s ease',
          }}
        >
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={overrideActive
              ? 'Take your time. Just say what\'s true.'
              : 'Say anything...'
            }
            rows={1}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: palette.text,
              fontSize: 15,
              lineHeight: 1.6,
              resize: 'none',
              fontFamily: 'inherit',
              minHeight: 24,
              maxHeight: 120,
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || presenceState === 'holding' || presenceState === 'responding'}
            style={{
              width: 36,
              height: 36,
              borderRadius: '50%',
              border: 'none',
              background: input.trim()
                ? overrideActive ? OVERRIDE_PALETTE.accent : palette.accent
                : `${palette.subtle}44`,
              color: 'white',
              cursor: input.trim() ? 'pointer' : 'default',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 16,
              transition: 'all 0.3s ease',
              flexShrink: 0,
            }}
          >
            ↑
          </button>
        </div>
        <div
          style={{
            fontSize: 10,
            color: palette.subtle,
            opacity: 0.5,
            textAlign: 'center',
            marginTop: 8,
            letterSpacing: '0.04em',
          }}
        >
          Enter to send · Shift+Enter for new line
        </div>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes breathe {
          0%, 100% { opacity: 0.4; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.3); }
        }
        @keyframes pulseOverride {
          0%, 100% { opacity: 0.7; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.5); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default TwinInterface;

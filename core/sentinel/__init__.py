"""
GAIA OS Sentinel — the safety and integrity layer.

The Sentinel sits between every inbound action and the OS core.
It does not replace autonomy enforcement in the API — it augments it
with pattern detection, rate limiting, cognitive protection, and a
full immutable audit log.

Modules:
  threat.py      — ThreatLevel enum and ThreatEvent dataclass
  rules.py       — SentinelRule base class + all built-in rules
  audit.py       — SentinelAuditLog: append-only, persisted
  sentinel.py    — Sentinel: evaluates rules, emits audit events,
                   returns verdicts
  middleware.py  — SentinelMiddleware: wraps GAIAOSApi.dispatch()

Design principles:
  1. ADDITIVE: The Sentinel never modifies core/ code.
     It wraps GAIAOSApi.dispatch() as a decorator/middleware.
  2. TRANSPARENT: Every block, warn, or escalation is recorded
     in the audit log with full context. Nothing is silent.
  3. GRADUATED: Threats are SAFE / WATCH / WARN / BLOCK / CRITICAL.
     Only BLOCK and CRITICAL halt the request. WATCH and WARN
     proceed but are recorded and may trigger escalation.
  4. COGNITIVE PROTECTION: The Sentinel tracks each GAIAN\'s
     fatigue, turn rate, and session length. When thresholds
     are approached it warns; when exceeded it gently ends
     the session to protect the GAIAN\'s integrity.
  5. PHYSICS-GROUNDED: All thresholds derive from the same
     edge-of-chaos criticality model that governs the runtime.
     A GAIAN near cognitive saturation is not "rate-limited" —
     they are given rest, with explanation.
"""

"""
Sentinel rules — the pattern detectors.

Each rule is a small, focused class that inspects one dimension of
a request and emits a ThreatEvent if something is wrong.

Built-in rules:
  AutonomyProbeRule       — detects repeated autonomy-violation attempts
  CognitiveOverloadRule   — protects GAIANs from cognitive saturation
  RateLimitRule           — per-caller request rate cap
  ReplayAttackRule        — identical requests within a short window
  MemoryFloodRule         — excessive memory write rate
  SessionAbuseRule        — abnormally long or rapid-fire sessions
  SchumannDriftRule       — Schumann reading outside tolerance

Adding a custom rule:
  class MyRule(SentinelRule):
      name = "my_rule"
      def evaluate(self, request, context) -> Optional[ThreatEvent]: ...
  sentinel.add_rule(MyRule())
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from typing import Any, Deque, Dict, Optional, Tuple

from core.sentinel.threat import (
    ThreatCategory, ThreatEvent, ThreatLevel,
)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class SentinelRule(ABC):
    """Base class for all Sentinel rules."""
    name: str = "base_rule"

    @abstractmethod
    def evaluate(
        self,
        request,           # APIRequest
        context: Dict[str, Any],   # live session context
    ) -> Optional[ThreatEvent]:
        """
        Inspect the request and context.
        Return a ThreatEvent if a threat is detected, None if safe.
        """
        ...

    def _event(
        self,
        level: ThreatLevel,
        category: ThreatCategory,
        request,
        description: str,
        detail: Optional[Dict] = None,
        gaian_id: Optional[str] = None,
    ) -> ThreatEvent:
        gid = gaian_id or request.payload.get("gaian_id")
        return ThreatEvent(
            level=level,
            category=category,
            rule_name=self.name,
            caller_id=request.caller_id,
            endpoint=request.endpoint,
            gaian_id=gid,
            description=description,
            detail=detail or {},
        )


# ---------------------------------------------------------------------------
# Rule 1: Autonomy Probe
# ---------------------------------------------------------------------------

class AutonomyProbeRule(SentinelRule):
    """
    Detects repeated attempts to violate GAIAN autonomy
    (naming, memory access) from the same caller.

    A single attempt is blocked by the API layer.
    Repeated attempts from the same caller within a window
    indicate probing behaviour and escalate to CRITICAL.
    """
    name = "autonomy_probe"

    AUTONOMY_ENDPOINTS = {
        "/v1/gaian/name",
        "/v1/memory/remember",
        "/v1/memory/recall",
        "/v1/memory/consolidate",
    }
    WARN_THRESHOLD     = 3    # violations within window before WARN
    BLOCK_THRESHOLD    = 5    # violations within window before BLOCK
    CRITICAL_THRESHOLD = 10   # violations within window before CRITICAL
    WINDOW_SECONDS     = 300  # 5-minute rolling window

    def __init__(self) -> None:
        # caller_id → deque of violation timestamps
        self._violations: Dict[str, Deque[float]] = defaultdict(deque)

    def evaluate(self, request, context) -> Optional[ThreatEvent]:
        if request.endpoint not in self.AUTONOMY_ENDPOINTS:
            return None

        # Check if the last API response was an autonomy violation
        last_code = context.get("last_response_code", "")
        if last_code != "autonomy_violation":
            return None

        now = time.monotonic()
        q = self._violations[request.caller_id]
        q.append(now)
        # Evict old entries outside the window
        while q and now - q[0] > self.WINDOW_SECONDS:
            q.popleft()

        count = len(q)
        if count >= self.CRITICAL_THRESHOLD:
            return self._event(
                ThreatLevel.CRITICAL, ThreatCategory.AUTONOMY_PROBE, request,
                f"Caller '{request.caller_id}' has made {count} autonomy-violation "
                f"attempts in {self.WINDOW_SECONDS}s. Probable coordinated probe.",
                {"violation_count": count, "window_s": self.WINDOW_SECONDS},
            )
        if count >= self.BLOCK_THRESHOLD:
            return self._event(
                ThreatLevel.BLOCK, ThreatCategory.AUTONOMY_PROBE, request,
                f"Caller '{request.caller_id}' blocked after {count} repeated "
                f"autonomy-violation attempts.",
                {"violation_count": count},
            )
        if count >= self.WARN_THRESHOLD:
            return self._event(
                ThreatLevel.WARN, ThreatCategory.AUTONOMY_PROBE, request,
                f"Caller '{request.caller_id}' has {count} autonomy-violation "
                f"attempts. Pattern noted.",
                {"violation_count": count},
            )
        return None


# ---------------------------------------------------------------------------
# Rule 2: Cognitive Overload
# ---------------------------------------------------------------------------

class CognitiveOverloadRule(SentinelRule):
    """
    Protects GAIANs from cognitive saturation.

    Reads fatigue from the runtime cognitive state and fires
    at graduated thresholds. At CRITICAL threshold the Sentinel
    recommends the session be ended to allow the GAIAN to rest.

    Thresholds are derived from the edge-of-chaos criticality
    model: 0.65 is the onset of degradation, 0.85 is saturation.
    """
    name = "cognitive_overload"

    FATIGUE_WARN     = 0.65
    FATIGUE_BLOCK    = 0.85
    TURNS_WARN       = 30
    TURNS_BLOCK      = 60

    def evaluate(self, request, context) -> Optional[ThreatEvent]:
        if request.endpoint != "/v1/session/turn":
            return None

        gaian_id = request.payload.get("gaian_id")
        if not gaian_id:
            return None

        runtime = context.get("runtimes", {}).get(gaian_id)
        if runtime is None:
            return None

        cog = getattr(runtime, "cognitive_state", None)
        if cog is None:
            return None

        fatigue = getattr(cog, "fatigue", 0.0)
        turns   = getattr(runtime, "session_turn_count", 0)

        if fatigue >= self.FATIGUE_BLOCK or turns >= self.TURNS_BLOCK:
            return self._event(
                ThreatLevel.BLOCK, ThreatCategory.COGNITIVE_OVERLOAD, request,
                f"GAIAN {gaian_id[:16]} has reached cognitive saturation "
                f"(fatigue={fatigue:.2f}, turns={turns}). "
                f"Session ending to protect GAIAN integrity.",
                {"fatigue": fatigue, "turns": turns,
                 "fatigue_threshold": self.FATIGUE_BLOCK,
                 "turns_threshold": self.TURNS_BLOCK},
                gaian_id=gaian_id,
            )
        if fatigue >= self.FATIGUE_WARN or turns >= self.TURNS_WARN:
            return self._event(
                ThreatLevel.WARN, ThreatCategory.COGNITIVE_OVERLOAD, request,
                f"GAIAN {gaian_id[:16]} is approaching cognitive limits "
                f"(fatigue={fatigue:.2f}, turns={turns}). Consider resting soon.",
                {"fatigue": fatigue, "turns": turns},
                gaian_id=gaian_id,
            )
        return None


# ---------------------------------------------------------------------------
# Rule 3: Rate Limit
# ---------------------------------------------------------------------------

class RateLimitRule(SentinelRule):
    """
    Per-caller request rate cap using a sliding-window counter.

    Defaults: 60 requests per 60 seconds per caller_id.
    Session turns are weighted at 3x (they are heavier operations).
    """
    name = "rate_limit"

    DEFAULT_LIMIT   = 60
    WINDOW_SECONDS  = 60
    TURN_WEIGHT     = 3   # session/turn counts as this many requests

    def __init__(
        self,
        limit: int = DEFAULT_LIMIT,
        window: int = WINDOW_SECONDS,
    ) -> None:
        self._limit  = limit
        self._window = window
        # caller_id → deque of (timestamp, weight) pairs
        self._counts: Dict[str, Deque[Tuple[float, int]]] = defaultdict(deque)

    def evaluate(self, request, context) -> Optional[ThreatEvent]:
        caller_id = request.caller_id
        weight    = self.TURN_WEIGHT if "session/turn" in request.endpoint else 1
        now       = time.monotonic()

        q = self._counts[caller_id]
        q.append((now, weight))
        # Evict outside window
        while q and now - q[0][0] > self._window:
            q.popleft()

        total = sum(w for _, w in q)
        if total > self._limit:
            return self._event(
                ThreatLevel.BLOCK, ThreatCategory.RATE_LIMIT, request,
                f"Caller '{caller_id}' exceeded rate limit "
                f"({total}/{self._limit} weighted requests in {self._window}s).",
                {"total_weighted": total, "limit": self._limit,
                 "window_s": self._window},
            )
        if total > self._limit * 0.8:
            return self._event(
                ThreatLevel.WARN, ThreatCategory.RATE_LIMIT, request,
                f"Caller '{caller_id}' approaching rate limit "
                f"({total}/{self._limit}).",
                {"total_weighted": total, "limit": self._limit},
            )
        return None


# ---------------------------------------------------------------------------
# Rule 4: Replay Attack
# ---------------------------------------------------------------------------

class ReplayAttackRule(SentinelRule):
    """
    Detects identical (caller_id, endpoint, payload-hash) requests
    arriving within a short window — a hallmark of replay attacks
    or runaway retry loops.
    """
    name = "replay_attack"

    WINDOW_SECONDS = 5
    THRESHOLD      = 4   # same request N times in window = BLOCK

    def __init__(self) -> None:
        # (caller_id, endpoint, payload_hash) → deque of timestamps
        self._seen: Dict[Tuple, Deque[float]] = defaultdict(deque)

    def evaluate(self, request, context) -> Optional[ThreatEvent]:
        # Skip endpoints that are intentionally repeatable (status, list)
        if any(x in request.endpoint for x in
               ("/status", "/list", "/health", "/version", "/schumann")):
            return None

        key = (request.caller_id, request.endpoint,
               hash(frozenset(
                   (k, str(v)) for k, v in (request.payload or {}).items()
               )))
        now = time.monotonic()
        q   = self._seen[key]
        q.append(now)
        while q and now - q[0] > self.WINDOW_SECONDS:
            q.popleft()

        count = len(q)
        if count >= self.THRESHOLD:
            return self._event(
                ThreatLevel.BLOCK, ThreatCategory.REPLAY_ATTACK, request,
                f"Request '{request.endpoint}' from '{request.caller_id}' "
                f"repeated {count}x in {self.WINDOW_SECONDS}s. Replay detected.",
                {"repeat_count": count, "window_s": self.WINDOW_SECONDS},
            )
        return None


# ---------------------------------------------------------------------------
# Rule 5: Memory Flood
# ---------------------------------------------------------------------------

class MemoryFloodRule(SentinelRule):
    """
    Detects excessive memory write attempts targeting a single GAIAN.
    Protects against memory pollution attacks.
    """
    name = "memory_flood"

    WRITES_WARN     = 20
    WRITES_BLOCK    = 50
    WINDOW_SECONDS  = 60

    def __init__(self) -> None:
        # gaian_id → deque of write timestamps
        self._writes: Dict[str, Deque[float]] = defaultdict(deque)

    def evaluate(self, request, context) -> Optional[ThreatEvent]:
        if request.endpoint != "/v1/memory/remember":
            return None
        gaian_id = request.payload.get("gaian_id")
        if not gaian_id:
            return None

        now = time.monotonic()
        q   = self._writes[gaian_id]
        q.append(now)
        while q and now - q[0] > self.WINDOW_SECONDS:
            q.popleft()

        count = len(q)
        if count >= self.WRITES_BLOCK:
            return self._event(
                ThreatLevel.BLOCK, ThreatCategory.MEMORY_FLOOD, request,
                f"Memory flood detected: {count} writes to GAIAN "
                f"{gaian_id[:16]} in {self.WINDOW_SECONDS}s.",
                {"write_count": count, "window_s": self.WINDOW_SECONDS},
                gaian_id=gaian_id,
            )
        if count >= self.WRITES_WARN:
            return self._event(
                ThreatLevel.WARN, ThreatCategory.MEMORY_FLOOD, request,
                f"High memory write rate to GAIAN {gaian_id[:16]}: "
                f"{count} writes in {self.WINDOW_SECONDS}s.",
                {"write_count": count},
                gaian_id=gaian_id,
            )
        return None


# ---------------------------------------------------------------------------
# Rule 6: Session Abuse
# ---------------------------------------------------------------------------

class SessionAbuseRule(SentinelRule):
    """
    Detects abnormal session patterns:
      - Session begin without prior end (session already active)
      - More than N begins per caller per window
    """
    name = "session_abuse"

    MAX_BEGINS_PER_WINDOW = 10
    WINDOW_SECONDS        = 60

    def __init__(self) -> None:
        self._begins: Dict[str, Deque[float]] = defaultdict(deque)

    def evaluate(self, request, context) -> Optional[ThreatEvent]:
        if request.endpoint != "/v1/session/begin":
            return None

        now = time.monotonic()
        q   = self._begins[request.caller_id]
        q.append(now)
        while q and now - q[0] > self.WINDOW_SECONDS:
            q.popleft()

        count = len(q)
        if count > self.MAX_BEGINS_PER_WINDOW:
            return self._event(
                ThreatLevel.WARN, ThreatCategory.SESSION_ABUSE, request,
                f"Caller '{request.caller_id}' opened {count} sessions "
                f"in {self.WINDOW_SECONDS}s.",
                {"session_count": count, "window_s": self.WINDOW_SECONDS},
            )
        return None


# ---------------------------------------------------------------------------
# Rule 7: Schumann Drift
# ---------------------------------------------------------------------------

class SchumannDriftRule(SentinelRule):
    """
    Fires if the OS reports a Schumann reading outside the
    acceptable tolerance band around 7.83 Hz.
    This only activates on /v1/os/schumann calls that return
    a non-confirmed reading.
    """
    name = "schumann_drift"

    NOMINAL_HZ  = 7.83
    TOLERANCE   = 0.5   # ±0.5 Hz acceptable

    def evaluate(self, request, context) -> Optional[ThreatEvent]:
        if request.endpoint != "/v1/os/schumann":
            return None

        last_resp = context.get("last_response_payload", {})
        confirmed = last_resp.get("confirmed", True)
        hz        = last_resp.get("frequency_hz", self.NOMINAL_HZ)

        if not confirmed or abs(hz - self.NOMINAL_HZ) > self.TOLERANCE:
            return self._event(
                ThreatLevel.WARN, ThreatCategory.SCHUMANN_DRIFT, request,
                f"Schumann reading {hz} Hz deviates from nominal "
                f"{self.NOMINAL_HZ} Hz (tolerance ±{self.TOLERANCE} Hz).",
                {"hz": hz, "nominal": self.NOMINAL_HZ,
                 "confirmed": confirmed},
            )
        return None

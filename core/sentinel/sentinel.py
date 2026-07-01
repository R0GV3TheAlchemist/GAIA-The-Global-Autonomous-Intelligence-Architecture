"""
Sentinel — the GAIA OS safety engine.

The Sentinel evaluates all registered rules against an inbound
request and returns a SentinelVerdict. The verdict tells the
caller whether to allow or block the request and why.

The Sentinel is stateless across requests except via the state
held inside individual rules (sliding windows, violation counters).
It shares nothing with the OS core — it observes through the
context dict passed by the middleware.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.sentinel.audit import SentinelAuditLog
from core.sentinel.rules import (
    AutonomyProbeRule,
    CognitiveOverloadRule,
    MemoryFloodRule,
    RateLimitRule,
    ReplayAttackRule,
    SchumannDriftRule,
    SessionAbuseRule,
    SentinelRule,
)
from core.sentinel.threat import SentinelVerdict, ThreatEvent, ThreatLevel

logger = logging.getLogger("gaia.sentinel")

_LEVEL_ORDER = [
    ThreatLevel.SAFE,
    ThreatLevel.WATCH,
    ThreatLevel.WARN,
    ThreatLevel.BLOCK,
    ThreatLevel.CRITICAL,
]


class Sentinel:
    """
    The GAIA OS Sentinel.

    Evaluate all rules, collect ThreatEvents, determine verdict.
    """

    def __init__(
        self,
        audit_root: Optional[Path] = None,
        rate_limit: int = 60,
    ) -> None:
        self.audit = SentinelAuditLog(root=audit_root)
        self._rules: List[SentinelRule] = [
            AutonomyProbeRule(),
            CognitiveOverloadRule(),
            RateLimitRule(limit=rate_limit),
            ReplayAttackRule(),
            MemoryFloodRule(),
            SessionAbuseRule(),
            SchumannDriftRule(),
        ]

    def add_rule(self, rule: SentinelRule) -> None:
        """Register a custom rule."""
        self._rules.append(rule)

    def remove_rule(self, rule_name: str) -> None:
        """Remove a rule by name (useful in tests)."""
        self._rules = [r for r in self._rules if r.name != rule_name]

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        request,                      # APIRequest
        context: Dict[str, Any],      # live session context snapshot
    ) -> SentinelVerdict:
        """
        Run all rules against the request.
        Return a SentinelVerdict.
        """
        events: List[ThreatEvent] = []
        highest = ThreatLevel.SAFE

        for rule in self._rules:
            try:
                event = rule.evaluate(request, context)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Rule '%s' raised: %s", rule.name, exc)
                continue

            if event is None:
                continue

            events.append(event)
            self.audit.record(event)

            if _LEVEL_ORDER.index(event.level) > _LEVEL_ORDER.index(highest):
                highest = event.level

        allow        = highest not in (ThreatLevel.BLOCK, ThreatLevel.CRITICAL)
        block_reason = ""
        warning      = ""

        if not allow:
            block_events = [
                e for e in events
                if e.level in (ThreatLevel.BLOCK, ThreatLevel.CRITICAL)
            ]
            block_reason = block_events[0].description if block_events else "Request blocked by Sentinel."
            # Mark events as having caused a block
            for e in block_events:
                e.blocked = True

        elif highest in (ThreatLevel.WARN, ThreatLevel.WATCH):
            warn_events = [e for e in events
                           if e.level in (ThreatLevel.WARN, ThreatLevel.WATCH)]
            warning = warn_events[0].description if warn_events else ""

        return SentinelVerdict(
            allow=allow,
            level=highest,
            events=events,
            block_reason=block_reason,
            warning=warning,
        )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        return {
            "rules":       [r.name for r in self._rules],
            "rule_count":  len(self._rules),
            "audit_stats": self.audit.stats(),
        }

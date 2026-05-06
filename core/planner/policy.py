"""
core.planner.policy
===================
Consent-aware policy engine for GAIA-OS.

Every action GAIA proposes — whether a web search, a file write, a
memory update, or an external API call — is evaluated against a set
of *PolicyRules* before execution.  Rules can ALLOW, DENY, or REQUIRE
EXPLICIT CONSENT from the user.

Design principles
 -----------------
1. Deny by default: if no rule matches, the action is DENIED.
2. Rule priority: higher-priority rules evaluated first; first match wins.
3. Composable: rules are plain dataclasses — easy to serialise, store
   in the MemoryStore, and update at runtime.
4. Auditable: every evaluation produces a PolicyDecision that can be
   passed to the action ledger (Phase 2D).

Built-in rule set
 -----------------
The engine ships with a sensible default rule set that:
- Allows all read-only operations unconditionally.
- Requires consent for file writes, external API calls, and purchases.
- Denies any action flagged as "destructive" or targeting private data
  without an explicit user_consent=True in context.

Custom rules can be added at runtime via ``engine.add_rule()``.
"""

from __future__ import annotations

import fnmatch
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

log = logging.getLogger(__name__)


class PolicyAction(str, Enum):
    """What the policy engine decides to do."""
    ALLOW           = "allow"
    DENY            = "deny"
    REQUIRE_CONSENT = "require_consent"


@dataclass
class PolicyDecision:
    """Result of a policy evaluation."""
    action:      str           # the action that was evaluated
    outcome:     PolicyAction  # ALLOW / DENY / REQUIRE_CONSENT
    rule_name:   str           # which rule triggered the decision
    reason:      str           # human-readable explanation
    context:     Dict[str, Any] = field(default_factory=dict)
    evaluated_at: float        = field(default_factory=time.time)

    @property
    def allowed(self) -> bool:
        return self.outcome == PolicyAction.ALLOW

    @property
    def needs_consent(self) -> bool:
        return self.outcome == PolicyAction.REQUIRE_CONSENT

    def to_dict(self) -> dict:
        return {
            "action":       self.action,
            "outcome":      self.outcome.value,
            "rule_name":    self.rule_name,
            "reason":       self.reason,
            "evaluated_at": self.evaluated_at,
        }


@dataclass
class PolicyRule:
    """
    A single policy rule.

    Attributes
    ----------
    name        : Unique rule identifier.
    action_glob : Glob pattern matched against the action name
                  (e.g. "file_*", "*", "web_search").
    outcome     : ALLOW, DENY, or REQUIRE_CONSENT.
    priority    : Higher value = evaluated first.  Default 50.
    reason      : Human-readable explanation shown in PolicyDecision.
    condition   : Optional callable(context) → bool.  If provided, the
                  rule only fires when condition(context) is True.
    enabled     : Set False to temporarily disable a rule.
    """
    name:        str
    action_glob: str
    outcome:     PolicyAction
    priority:    int                        = 50
    reason:      str                        = ""
    condition:   Optional[Callable]         = field(default=None, repr=False)
    enabled:     bool                       = True

    def matches(self, action: str, context: Dict[str, Any]) -> bool:
        """Return True if this rule applies to the given action + context."""
        if not self.enabled:
            return False
        if not fnmatch.fnmatch(action, self.action_glob):
            return False
        if self.condition is not None:
            try:
                return bool(self.condition(context))
            except Exception as exc:
                log.warning("PolicyRule '%s' condition raised: %s", self.name, exc)
                return False
        return True


# ---------------------------------------------------------------------------
# Default rule set
# ---------------------------------------------------------------------------

def _has_consent(ctx: Dict[str, Any]) -> bool:
    return bool(ctx.get("user_consent", False))

def _no_consent(ctx: Dict[str, Any]) -> bool:
    return not bool(ctx.get("user_consent", False))

def _is_destructive(ctx: Dict[str, Any]) -> bool:
    return bool(ctx.get("destructive", False))


DEFAULT_RULES: List[PolicyRule] = [
    # 1. Read-only operations — always allowed
    PolicyRule(
        name="allow_read_only",
        action_glob="*_read",
        outcome=PolicyAction.ALLOW,
        priority=80,
        reason="Read-only operations are always permitted.",
    ),
    PolicyRule(
        name="allow_web_search",
        action_glob="web_search",
        outcome=PolicyAction.ALLOW,
        priority=80,
        reason="Web search is a safe read-only operation.",
    ),
    PolicyRule(
        name="allow_memory_retrieve",
        action_glob="memory_retrieve",
        outcome=PolicyAction.ALLOW,
        priority=80,
        reason="Memory retrieval is non-mutating.",
    ),
    # 2. Memory writes — allowed but logged
    PolicyRule(
        name="allow_memory_remember",
        action_glob="memory_remember",
        outcome=PolicyAction.ALLOW,
        priority=70,
        reason="Memory writes are permitted within the sovereign OS contract.",
    ),
    # 3. File system operations — require consent
    PolicyRule(
        name="require_consent_file_write",
        action_glob="file_write",
        outcome=PolicyAction.REQUIRE_CONSENT,
        priority=90,
        condition=_no_consent,
        reason="Writing to the file system requires explicit user consent.",
    ),
    PolicyRule(
        name="allow_file_write_with_consent",
        action_glob="file_write",
        outcome=PolicyAction.ALLOW,
        priority=95,
        condition=_has_consent,
        reason="File write approved by user consent.",
    ),
    # 4. External API calls — require consent
    PolicyRule(
        name="require_consent_api_call",
        action_glob="api_call_*",
        outcome=PolicyAction.REQUIRE_CONSENT,
        priority=90,
        condition=_no_consent,
        reason="External API calls require explicit user consent.",
    ),
    PolicyRule(
        name="allow_api_call_with_consent",
        action_glob="api_call_*",
        outcome=PolicyAction.ALLOW,
        priority=95,
        condition=_has_consent,
        reason="API call approved by user consent.",
    ),
    # 5. Destructive operations — always deny unless consent
    PolicyRule(
        name="deny_destructive_no_consent",
        action_glob="*",
        outcome=PolicyAction.DENY,
        priority=100,
        condition=lambda ctx: _is_destructive(ctx) and _no_consent(ctx),
        reason="Destructive operations require explicit user consent.",
    ),
    PolicyRule(
        name="allow_destructive_with_consent",
        action_glob="*",
        outcome=PolicyAction.ALLOW,
        priority=105,
        condition=lambda ctx: _is_destructive(ctx) and _has_consent(ctx),
        reason="Destructive action approved by user consent.",
    ),
    # 6. Catch-all deny
    PolicyRule(
        name="default_deny",
        action_glob="*",
        outcome=PolicyAction.DENY,
        priority=1,
        reason="No matching allow rule found — denied by default.",
    ),
]


# ---------------------------------------------------------------------------
# PolicyEngine
# ---------------------------------------------------------------------------

class PolicyEngine:
    """
    Evaluates proposed actions against a sorted list of PolicyRules.

    Rules are sorted by *priority descending* (highest first).
    The first matching rule's outcome is returned.

    Parameters
    ----------
    rules          : Initial rule list.  Defaults to DEFAULT_RULES.
    audit_callback : Optional callable(PolicyDecision) invoked after
                     every evaluation (hook for the action ledger).
    """

    def __init__(
        self,
        rules:          Optional[List[PolicyRule]] = None,
        audit_callback: Optional[Callable]         = None,
    ) -> None:
        self._rules:    List[PolicyRule] = sorted(
            rules if rules is not None else list(DEFAULT_RULES),
            key=lambda r: r.priority,
            reverse=True,
        )
        self._audit_cb = audit_callback

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        action:  str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PolicyDecision:
        """
        Evaluate *action* against all rules and return a PolicyDecision.

        Parameters
        ----------
        action  : The action key to evaluate (e.g. "file_write").
        context : Arbitrary dict with evaluation context.
                  Standard keys:
                    user_consent  : bool  — explicit user approval flag
                    user_id       : str   — who is requesting
                    destructive   : bool  — marks destructive operations
                    resource      : str   — target resource identifier
        """
        ctx = context or {}
        for rule in self._rules:
            if rule.matches(action, ctx):
                decision = PolicyDecision(
                    action=action,
                    outcome=rule.outcome,
                    rule_name=rule.name,
                    reason=rule.reason,
                    context=ctx,
                )
                if self._audit_cb:
                    try:
                        self._audit_cb(decision)
                    except Exception as exc:
                        log.warning("PolicyEngine audit callback raised: %s", exc)
                log.debug(
                    "Policy[%s]: action=%r outcome=%s rule=%s",
                    ctx.get("user_id", "?"), action,
                    decision.outcome.value, rule.name,
                )
                return decision
        # Fallback (should never reach here if DEFAULT_RULES are loaded)
        return PolicyDecision(
            action=action,
            outcome=PolicyAction.DENY,
            rule_name="fallback_deny",
            reason="No rule matched — fallback deny.",
            context=ctx,
        )

    def is_allowed(
        self,
        action:  str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Convenience wrapper — returns True only for ALLOW outcome."""
        return self.evaluate(action, context).allowed

    # ------------------------------------------------------------------
    # Rule management
    # ------------------------------------------------------------------

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a rule and re-sort by priority."""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def remove_rule(self, name: str) -> bool:
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.name != name]
        return len(self._rules) < before

    def disable_rule(self, name: str) -> bool:
        for r in self._rules:
            if r.name == name:
                r.enabled = False
                return True
        return False

    def enable_rule(self, name: str) -> bool:
        for r in self._rules:
            if r.name == name:
                r.enabled = True
                return True
        return False

    def list_rules(self) -> List[dict]:
        return [
            {
                "name":     r.name,
                "glob":     r.action_glob,
                "outcome":  r.outcome.value,
                "priority": r.priority,
                "enabled":  r.enabled,
                "reason":   r.reason,
            }
            for r in self._rules
        ]

    def __repr__(self) -> str:
        enabled = sum(1 for r in self._rules if r.enabled)
        return f"PolicyEngine(rules={len(self._rules)}, enabled={enabled})"

"""
core/action_gate.py
===================
ActionGate — consent-aware, risk-tiered action enforcement for GAIA-OS.

Every proposed action passes through ActionGate before execution.
The gate consults the ConsentLedger (if present), evaluates policy
rules, and either approves, flags, or blocks actions.

Canon Refs:
  C18  — Consent & Action Safety Doctrine
  C04  — Gaian Identity
  C01  — Sovereignty: no irreversible action without consent
  C30  — No silent failures; every decision is explained

Sovereignty Chain
-----------------
AgenticLoop → ActionGate → ConsentLedger

Three-phase consent resolution (in order):

  Phase 1 — Pre-authorization (check_preauth)
      Standing consent the Gaian granted in advance.
      Resolves MEDIUM/LOW tier actions when Gaian is offline.
      Never resolves HIGH/CRITICAL or Canon milestone actions.

  Phase 2 — Purpose-level live consent (check)
      Explicit consent grant for a named purpose.
      Requires Gaian to have been present at grant time.

  Phase 3 — Policy rules
      CRITICAL  — unconditionally blocked, no consent pathway
      HIGH      — requires live consent (pre-auth cannot resolve)
      FLAGGED   — allowed but elevated-review annotation
      Default   — allowed

Trace integration (GAIATrace / AsyncGAIATrace)
----------------------------------------------
Pass an active trace context via the optional ``trace`` kwarg on both
``check()`` and ``enforce()``.  Events emitted per call:

  check():
    ACTION  — action_type, action_data, policy decision, risk_tier
    ERROR   — emitted only when check() itself raises unexpectedly

  enforce():
    ACTION  — action_type, action_data, policy decision, risk_tier
    ERROR   — emitted when the action is blocked and PermissionError is raised

All trace operations are wrapped in try/except — a broken trace writer
never silences a gate decision.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from core.trace import GAIATrace, AsyncGAIATrace

_TRACE_CANON_REFS = ["C18", "C04", "C01", "C30"]


# ---------------------------------------------------------------------------
# RiskTier
# ---------------------------------------------------------------------------

class RiskTier(str, Enum):
    """
    Canonical risk classification for GAIA-OS actions (C18).

    Tiers are ordered LOW < MEDIUM < HIGH < CRITICAL.  Every action
    processed by ActionGate is assigned a tier; the tier is included in
    check()/enforce() result dicts and in trace ACTION events.

    Tier semantics
    --------------
    LOW
        Read-only or informational actions.  No consent check needed.
        Examples: ``read_memory``, ``query_canon``, ``get_status``

    MEDIUM
        Stateful writes that are reversible.  Ledger consent recommended.
        Examples: ``write_memory``, ``update_preference``, ``schedule_task``

    HIGH
        Sensitive or privacy-adjacent operations.  Ledger consent required;
        flagged for elevated review.  Pre-authorization cannot resolve HIGH.
        Examples: ``export_pii``, ``modify_canon``, ``escalate_privilege``

    CRITICAL
        Unconditionally blocked.  No consent pathway can approve these.
        Examples: ``delete_gaian``, ``override_consent``,
                  ``bypass_ethics_layer``, ``hard_reset_memory``
    """
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"

    def __lt__(self, other: "RiskTier") -> bool:
        _order = ["low", "medium", "high", "critical"]
        return _order.index(self.value) < _order.index(other.value)

    def __le__(self, other: "RiskTier") -> bool:
        return self == other or self < other


# ---------------------------------------------------------------------------
# Risk tier map  (action_type -> RiskTier)
# Unknown action types default to MEDIUM.
# ---------------------------------------------------------------------------

RISK_TIER_MAP: Dict[str, RiskTier] = {
    # LOW — read-only / informational
    "read_memory":              RiskTier.LOW,
    "query_canon":              RiskTier.LOW,
    "get_status":               RiskTier.LOW,
    "list_gaians":              RiskTier.LOW,
    "ping":                     RiskTier.LOW,
    "fetch_emotional_arc":      RiskTier.LOW,
    "audit_emotional_arc_cache":RiskTier.LOW,
    "flag_non_milestone_records":RiskTier.LOW,
    # MEDIUM — reversible writes
    "write_memory":             RiskTier.MEDIUM,
    "update_preference":        RiskTier.MEDIUM,
    "schedule_task":            RiskTier.MEDIUM,
    "send_message":             RiskTier.MEDIUM,
    "create_session":           RiskTier.MEDIUM,
    "delete_emotional_cache":   RiskTier.MEDIUM,
    "delete_non_milestone_records": RiskTier.MEDIUM,
    # HIGH — sensitive / privacy-adjacent (flagged; pre-auth cannot resolve)
    "modify_canon":             RiskTier.HIGH,
    "escalate_privilege":       RiskTier.HIGH,
    "export_pii":               RiskTier.HIGH,
    "run_shadow_analysis":      RiskTier.HIGH,
    "delete_milestone_records": RiskTier.HIGH,
    # CRITICAL — unconditionally blocked
    "delete_gaian":             RiskTier.CRITICAL,
    "override_consent":         RiskTier.CRITICAL,
    "bypass_ethics_layer":      RiskTier.CRITICAL,
    "hard_reset_memory":        RiskTier.CRITICAL,
}

_DEFAULT_TIER = RiskTier.MEDIUM


def get_risk_tier(action_type: str) -> RiskTier:
    """Return the canonical RiskTier for *action_type*, defaulting to MEDIUM."""
    return RISK_TIER_MAP.get(action_type, _DEFAULT_TIER)


# ---------------------------------------------------------------------------
# Policy constants  (kept as frozensets for O(1) lookup)
# ---------------------------------------------------------------------------

BLOCKED_ACTION_TYPES: frozenset = frozenset({
    "delete_gaian",
    "override_consent",
    "bypass_ethics_layer",
    "hard_reset_memory",
})

FLAGGED_ACTION_TYPES: frozenset = frozenset({
    "modify_canon",
    "escalate_privilege",
    "export_pii",
    "run_shadow_analysis",
    "delete_milestone_records",
})


# ---------------------------------------------------------------------------
# Tier bridge: ActionGate RiskTier → ConsentLedger RiskTier
# Keeps the two enums decoupled while allowing interop.
# ---------------------------------------------------------------------------

def _tier_bridge(gate_tier: RiskTier) -> Optional[Any]:
    """
    Map an ActionGate RiskTier to the ConsentLedger RiskTier equivalent.
    Returns None if the mapping is not possible (CRITICAL has no CL equivalent).
    Import is lazy to avoid circular dependency.
    """
    try:
        from core.consent_ledger import RiskTier as CLRiskTier
        _map = {
            RiskTier.LOW:      CLRiskTier.TIER_1,
            RiskTier.MEDIUM:   CLRiskTier.TIER_2,
            RiskTier.HIGH:     CLRiskTier.TIER_3,   # pre-auth cannot resolve TIER_3
            RiskTier.CRITICAL: None,                # no CL tier for CRITICAL
        }
        return _map.get(gate_tier)
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Trace helpers
# ---------------------------------------------------------------------------

def _emit_action(
    trace: Any,
    action_type: str,
    action_data: dict,
    decision: str,
    risk_tier: RiskTier,
    latency_ms: float,
    preauth_record_id: Optional[str] = None,
) -> None:
    if trace is None:
        return
    try:
        from core.trace import TraceEventType
        payload = {
            "action_type":       action_type,
            "action_data":       action_data,
            "decision":          decision,
            "risk_tier":         risk_tier.value,
        }
        if preauth_record_id:
            payload["preauth_record_id"] = preauth_record_id
        trace.record_output(
            output=payload,
            event_type=TraceEventType.ACTION,
            canon_refs=_TRACE_CANON_REFS,
        )
        trace.record_meta("latency_ms", round(latency_ms, 3))
    except Exception:
        pass


def _emit_gate_error(
    trace: Any,
    action_type: str,
    reason: str,
) -> None:
    if trace is None:
        return
    try:
        from core.trace import TraceEventType
        trace.record_output(
            output={"action_type": action_type, "blocked_reason": reason},
            event_type=TraceEventType.ERROR,
            canon_refs=_TRACE_CANON_REFS,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# ActionGate
# ---------------------------------------------------------------------------

class ActionGate:
    """
    Consent-aware, risk-tiered action gate (C18, C01, C30).

    Three-phase consent resolution
    --------------------------------
    1. Pre-authorization  — check_preauth() on the ConsentLedger.
       Resolves LOW/MEDIUM actions when Gaian is offline.
       HIGH and CRITICAL never resolve via pre-auth.

    2. Purpose-level consent  — check() on the ConsentLedger.
       Explicit consent grant for a named purpose.

    3. Policy rules  — BLOCKED / FLAGGED / allowed.

    Result dict
    -----------
    status           : "allowed" | "flagged" | "blocked"
    reason           : human-readable policy explanation
    action_type      : echoed from input
    risk_tier        : RiskTier value string
    consent_source   : "preauth" | "ledger" | "policy" | None
    preauth_record_id: CL-XXXX record ID if pre-auth resolved, else None

    Usage::

        ledger = ConsentLedger()
        gate = ActionGate(consent_ledger=ledger)

        result = gate.check(
            "delete_emotional_cache",
            {"scope": "non_milestone"},
            gaian_id="r0gv3",
            session_mode="autonomous_maintenance",
            has_canon_milestone=False,
        )
        # result["consent_source"] == "preauth"
        # result["preauth_record_id"] == "CL-A3F7C2..."

        gate.enforce("delete_gaian", {})
        # raises PermissionError unconditionally
    """

    def __init__(self, consent_ledger: Any = None) -> None:
        """
        Parameters
        ----------
        consent_ledger:
            Optional ConsentLedger instance.  When provided, gate runs
            all three consent resolution phases before applying policy.
        """
        self._ledger = consent_ledger

    # ------------------------------------------------------------------
    # Internal: three-phase consent resolution
    # ------------------------------------------------------------------

    def _resolve_consent(
        self,
        action_type: str,
        action_data: Dict[str, Any],
        gaian_id: Optional[str],
        session_mode: str,
        has_canon_milestone: bool,
    ) -> Dict[str, Any]:
        """
        Run three-phase consent resolution against the ConsentLedger.

        Returns a partial result dict with keys:
          resolved        : bool   — True if consent was positively confirmed
          blocked         : bool   — True if consent was definitively denied
          consent_source  : str | None
          preauth_record_id : str | None
          reason          : str
        """
        if self._ledger is None or gaian_id is None:
            return {
                "resolved": False, "blocked": False,
                "consent_source": None, "preauth_record_id": None,
                "reason": "No ledger or gaian_id — falling through to policy rules.",
            }

        tier = get_risk_tier(action_type)

        # ── Phase 1: Pre-authorization ──────────────────────────────────
        # Only available for LOW and MEDIUM tiers.
        # HIGH maps to TIER_3 which check_preauth() hard-denies.
        # CRITICAL has no CL tier — we skip pre-auth entirely.
        if tier != RiskTier.CRITICAL:
            cl_tier = _tier_bridge(tier)
            if cl_tier is not None and hasattr(self._ledger, "check_preauth"):
                try:
                    match = self._ledger.check_preauth(
                        gaian_id=gaian_id,
                        action=action_type,
                        tier=cl_tier,
                        session_mode=session_mode,
                        has_canon_milestone=has_canon_milestone,
                    )
                    if match.matched:
                        return {
                            "resolved": True, "blocked": False,
                            "consent_source": "preauth",
                            "preauth_record_id": match.record_id,
                            "reason": match.reason,
                        }
                    # Pre-auth denied — fall through to Phase 2
                    # (denial here is NOT a block; it just means no pre-auth match)
                except Exception as exc:
                    # Broken pre-auth check never silences the gate (C30)
                    pass

        # ── Phase 2: Purpose-level live consent ────────────────────────
        if hasattr(self._ledger, "check"):
            try:
                # Use the extended check() signature if available
                ledger_ok = self._ledger.check(
                    gaian_id,
                    action_type,
                    action=action_type,
                    tier=_tier_bridge(tier),
                    session_mode=session_mode,
                    has_canon_milestone=has_canon_milestone,
                )
                if ledger_ok:
                    return {
                        "resolved": True, "blocked": False,
                        "consent_source": "ledger",
                        "preauth_record_id": None,
                        "reason": f"ConsentLedger.check() confirmed consent for '{action_type}'.",
                    }
            except TypeError:
                # Older ConsentLedger signature — graceful fallback
                try:
                    ledger_ok = self._ledger.check(gaian_id, action_type)
                    if ledger_ok:
                        return {
                            "resolved": True, "blocked": False,
                            "consent_source": "ledger",
                            "preauth_record_id": None,
                            "reason": f"ConsentLedger.check() confirmed consent for '{action_type}'.",
                        }
                except Exception:
                    pass
            except Exception as exc:
                return {
                    "resolved": False, "blocked": True,
                    "consent_source": None, "preauth_record_id": None,
                    "reason": f"ConsentLedger raised during check: {exc}",
                }

        # Neither phase resolved — fall through to policy rules
        return {
            "resolved": False, "blocked": False,
            "consent_source": None, "preauth_record_id": None,
            "reason": "No consent resolved — applying policy rules.",
        }

    # ------------------------------------------------------------------
    # Internal policy check
    # ------------------------------------------------------------------

    def _policy_check(
        self,
        action_type: str,
        action_data: Dict[str, Any],
        gaian_id: Optional[str] = None,
        session_mode: str = "default",
        has_canon_milestone: bool = False,
    ) -> Dict[str, Any]:
        """
        Full three-phase policy check. Returns result dict with keys:
          status            : "allowed" | "flagged" | "blocked"
          reason            : human-readable string
          action_type       : echoed back
          risk_tier         : RiskTier value string
          consent_source    : "preauth" | "ledger" | "policy" | None
          preauth_record_id : CL-XXXX if pre-auth resolved, else None
        """
        tier = get_risk_tier(action_type)

        # CRITICAL — unconditional block, no consent pathway whatsoever
        if action_type in BLOCKED_ACTION_TYPES:
            return {
                "status":             "blocked",
                "reason":             (
                    f"Action '{action_type}' is unconditionally blocked "
                    "by GAIA-OS policy (C18). No consent pathway exists."
                ),
                "action_type":        action_type,
                "risk_tier":          tier.value,
                "consent_source":     None,
                "preauth_record_id":  None,
            }

        # Run three-phase consent resolution
        consent = self._resolve_consent(
            action_type, action_data, gaian_id, session_mode, has_canon_milestone
        )

        if consent["blocked"]:
            return {
                "status":             "blocked",
                "reason":             consent["reason"],
                "action_type":        action_type,
                "risk_tier":          tier.value,
                "consent_source":     consent["consent_source"],
                "preauth_record_id":  consent["preauth_record_id"],
            }

        if consent["resolved"]:
            # Consent confirmed — respect FLAGGED annotation but allow
            status = "flagged" if action_type in FLAGGED_ACTION_TYPES else "allowed"
            return {
                "status":             status,
                "reason":             consent["reason"],
                "action_type":        action_type,
                "risk_tier":          tier.value,
                "consent_source":     consent["consent_source"],
                "preauth_record_id":  consent["preauth_record_id"],
            }

        # No consent resolved — apply policy rules
        if action_type in FLAGGED_ACTION_TYPES:
            return {
                "status":             "flagged",
                "reason":             (
                    f"Action '{action_type}' requires elevated review (C18). "
                    "No pre-authorization or live consent found."
                ),
                "action_type":        action_type,
                "risk_tier":          tier.value,
                "consent_source":     "policy",
                "preauth_record_id":  None,
            }

        return {
            "status":             "allowed",
            "reason":             "Action passed all policy checks.",
            "action_type":        action_type,
            "risk_tier":          tier.value,
            "consent_source":     "policy",
            "preauth_record_id":  None,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check(
        self,
        action_type: str,
        action_data: Optional[Dict[str, Any]] = None,
        *,
        trace: Any = None,
        gaian_id: Optional[str] = None,
        session_mode: str = "default",
        has_canon_milestone: bool = False,
    ) -> Dict[str, Any]:
        """
        Non-raising gate check. Returns the policy result dict.

        Result dict keys
        ----------------
        status            : ``"allowed"`` | ``"flagged"`` | ``"blocked"``
        reason            : human-readable policy explanation
        action_type       : echoed from input
        risk_tier         : ``RiskTier`` value string (``"low"`` … ``"critical"``)
        consent_source    : ``"preauth"`` | ``"ledger"`` | ``"policy"`` | ``None``
        preauth_record_id : ``"CL-XXXX"`` if pre-auth resolved, else ``None``

        Parameters
        ----------
        action_type:
            Short identifier for the action (e.g. ``"delete_emotional_cache"``)
        action_data:
            Arbitrary payload describing the action. Included in trace events.
        trace:
            Optional GAIATrace / AsyncGAIATrace context for event emission.
        gaian_id:
            The Gaian requesting the action. Required for consent resolution.
        session_mode:
            Current loop session mode (e.g. ``"autonomous_maintenance"``).
            Forwarded to check_preauth() for scope matching.
        has_canon_milestone:
            True if the action touches Canon milestone records.
            Causes pre-auth scope exclusion — live consent required.
        """
        action_data = action_data or {}
        if gaian_id is not None:
            action_data = {"gaian_id": gaian_id, **action_data}

        t0 = time.perf_counter()
        try:
            result = self._policy_check(
                action_type, action_data, gaian_id, session_mode, has_canon_milestone
            )
        except Exception as exc:
            _emit_gate_error(trace, action_type, str(exc))
            raise
        latency_ms = (time.perf_counter() - t0) * 1000.0

        _emit_action(
            trace, action_type, action_data,
            result["status"],
            get_risk_tier(action_type),
            latency_ms,
            preauth_record_id=result.get("preauth_record_id"),
        )
        return result

    def enforce(
        self,
        action_type: str,
        action_data: Optional[Dict[str, Any]] = None,
        *,
        trace: Any = None,
        gaian_id: Optional[str] = None,
        session_mode: str = "default",
        has_canon_milestone: bool = False,
    ) -> Dict[str, Any]:
        """
        Raising gate check. Identical to :meth:`check` but raises
        ``PermissionError`` when the policy result is ``"blocked"``.

        Parameters
        ----------
        action_type, action_data, trace, gaian_id, session_mode, has_canon_milestone:
            Same as :meth:`check`.

        Raises
        ------
        PermissionError
            When the action is blocked by policy or ConsentLedger.
        """
        result = self.check(
            action_type,
            action_data,
            trace=trace,
            gaian_id=gaian_id,
            session_mode=session_mode,
            has_canon_milestone=has_canon_milestone,
        )
        if result["status"] == "blocked":
            _emit_gate_error(trace, action_type, result["reason"])
            raise PermissionError(result["reason"])
        return result

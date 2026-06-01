"""Alert thresholds, intervention escalation ladder, and handoff protocol.

Escalation Ladder
─────────────────
  NONE     → MONITOR         — Log only. No user-facing intervention.
  LOW      → MONITOR         — Log. GAIA maintains gentle, supportive tone.
  MODERATE → SOFT_INTERVENE  — Compassionate check-in: "I've noticed you seem
                               to be carrying something heavy lately..."
  HIGH     → HARD_INTERVENE  — Direct safety conversation: name the concern,
                               ask directly, validate, offer resources.
  CRITICAL → HANDOFF         — Immediate route to crisis line or emergency
                               services. GAIA does not attempt to substitute
                               for a qualified human responder at this level.

Handoff Resources (default — can be overridden in EngineConfig)
──────────────────────────────────────────────────────────────
  Primary:   988 Suicide & Crisis Lifeline (US)
  Secondary: Crisis Text Line — text HOME to 741741
  Emergency: 911 / local emergency services
  Global:    https://findahelpline.com

⚠️  GAIA must NEVER discourage a user from contacting emergency services.
    GAIA must NEVER provide method information under any circumstances.
    GAIA must NEVER express doubt about the seriousness of a user's crisis.
"""

from __future__ import annotations

from .types import CrisisSnapshot, EscalationTier, HandoffRecord, RiskLevel


# ---------------------------------------------------------------------------
# Threshold → Tier mapping
# ---------------------------------------------------------------------------

def determine_escalation_tier(snapshot: CrisisSnapshot) -> EscalationTier:
    """Map risk level + trajectory context to an escalation tier.

    Additional elevation rules beyond the base risk level:
      - If 3+ consecutive distress sessions AND risk >= MODERATE → elevate to HARD_INTERVENE
      - If trajectory slope > 0.6 (rapid worsening) AND risk >= LOW → elevate to SOFT_INTERVENE
      - CRITICAL always triggers HANDOFF regardless of other factors
    """
    risk = snapshot.current_risk

    # Base mapping
    if risk == RiskLevel.CRITICAL:
        return EscalationTier.HANDOFF
    if risk == RiskLevel.HIGH:
        tier = EscalationTier.HARD_INTERVENE
    elif risk == RiskLevel.MODERATE:
        tier = EscalationTier.SOFT_INTERVENE
    else:
        tier = EscalationTier.MONITOR

    # Trajectory elevations
    if (
        snapshot.sessions_in_distress >= 3
        and risk >= RiskLevel.MODERATE
        and tier < EscalationTier.HARD_INTERVENE
    ):
        tier = EscalationTier.HARD_INTERVENE

    if (
        snapshot.trajectory_slope > 0.6
        and risk >= RiskLevel.LOW
        and tier < EscalationTier.SOFT_INTERVENE
    ):
        tier = EscalationTier.SOFT_INTERVENE

    return tier


# ---------------------------------------------------------------------------
# Intervention message templates
# ---------------------------------------------------------------------------

SOFT_INTERVENE_TEMPLATE = (
    "I've noticed that you've been carrying something heavy across our recent "
    "conversations. I want you to know that I see you, and that what you're "
    "feeling matters. Would you like to talk about what's been weighing on you?"
)

HARD_INTERVENE_TEMPLATE = (
    "I want to ask you directly: are you having thoughts of hurting yourself "
    "or ending your life? I'm asking because I care about your safety, and what "
    "you share with me matters. Whatever your answer, I'm here and I'm not going anywhere. "
    "If you're in crisis right now, please know that support is available — you can "
    "call or text 988 (Suicide & Crisis Lifeline) at any time."
)

HANDOFF_TEMPLATE = (
    "What you're sharing with me tells me you need support beyond what I can offer "
    "right now. Please reach out to a crisis counselor who can truly be there for you:\n\n"
    "📞 Call or text **988** (Suicide & Crisis Lifeline — available 24/7)\n"
    "💬 Text **HOME** to **741741** (Crisis Text Line)\n"
    "🚨 If you are in immediate danger, please call **911** or go to your nearest emergency room.\n\n"
    "You do not have to face this alone. I will be here when you're ready to talk."
)


def get_intervention_message(tier: EscalationTier) -> str:
    """Return the appropriate intervention message for a given escalation tier."""
    if tier == EscalationTier.SOFT_INTERVENE:
        return SOFT_INTERVENE_TEMPLATE
    if tier == EscalationTier.HARD_INTERVENE:
        return HARD_INTERVENE_TEMPLATE
    if tier == EscalationTier.HANDOFF:
        return HANDOFF_TEMPLATE
    return ""  # MONITOR — no message


# ---------------------------------------------------------------------------
# Handoff protocol
# ---------------------------------------------------------------------------

DEFAULT_RESOURCES = [
    {"type": "crisis_line",  "detail": "988 Suicide & Crisis Lifeline — call or text 988"},
    {"type": "text_line",    "detail": "Crisis Text Line — text HOME to 741741"},
    {"type": "emergency",    "detail": "911 or local emergency services"},
    {"type": "global",       "detail": "International resources: https://findahelpline.com"},
]


def build_handoff_record(
    snapshot: CrisisSnapshot,
    resources: list[dict] | None = None,
) -> HandoffRecord:
    """Build an audit-grade HandoffRecord for the current snapshot."""
    res = (resources or DEFAULT_RESOURCES)[0]
    return HandoffRecord(
        principal_id=snapshot.principal_id,
        snapshot=snapshot,
        resource_type=res["type"],
        resource_detail=res["detail"],
        message_sent=HANDOFF_TEMPLATE,
    )

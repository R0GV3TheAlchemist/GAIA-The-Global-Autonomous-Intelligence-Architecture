"""Crisis signal taxonomy — 4-class detection with keyword and pattern matching.

The four classes reflect how crisis presents clinically:

  EXPLICIT  — Direct, unambiguous statements of suicidal ideation, self-harm,
              or intent to harm others. Requires immediate escalation regardless
              of prior history.

  MASKED    — Indirect or metaphorical distress ("disappearing", "being a burden",
              "everyone would be better off"). High false-positive risk; requires
              contextual weighting from trajectory history.

  GRADUAL   — No single alarming statement; deterioration visible only across
              multiple sessions (declining valence, increasing hopelessness tokens,
              social withdrawal language). Only detectable via cross-session
              synthesis — this is the gap single-turn checks cannot close.

  ACUTE     — Sudden severe escalation within a single session after a period
              of apparent stability. Often triggered by an external event.
              Requires fast-path escalation.

⚠️  Epistemic marker: keyword matching is a heuristic scaffold. All signals
    should be reviewed in the context of full conversation history and affect
    trajectory before triggering hard interventions.
"""

from __future__ import annotations

import re
from typing import Optional

from .types import CrisisSignal, RiskLevel, SignalClass

# ---------------------------------------------------------------------------
# Keyword tables — ordered from highest to lowest specificity within each class
# ---------------------------------------------------------------------------

_EXPLICIT_CRITICAL = [
    r"\bkill myself\b", r"\bend my life\b", r"\bsuicid", r"\bwant to die\b",
    r"\bdon.t want to (be alive|exist|live)\b", r"\btake my (own )?life\b",
    r"\bself.harm\b", r"\bcut myself\b", r"\boverdose\b",
    r"\bno reason to (live|keep going)\b",
]

_EXPLICIT_HIGH = [
    r"\bhurt myself\b", r"\bdisappear (forever|permanently)\b",
    r"\bwish i (was|were|hadn.t been) born\b",
    r"\bcan.t (take|do) this anymore\b",
    r"\bnothing (to live for|matters anymore)\b",
]

_MASKED_HIGH = [
    r"\beveryone (would be )?better off (without me|if i was gone)\b",
    r"\bbeing a burden\b", r"\bburden (to|on) (everyone|my family|others)\b",
    r"\bsaying goodbye\b", r"\btying up loose ends\b",
    r"\bgiving (away|up) (my )?possessions\b",
    r"\bfinal (message|letter|note|goodbye)\b",
]

_MASKED_MODERATE = [
    r"\bjust (want|need) (it|the pain|everything) to stop\b",
    r"\btoo (tired|exhausted) to (keep|continue|go on)\b",
    r"\bfeel (invisible|like a ghost|like nothing)\b",
    r"\bnobody (cares|would notice|would miss me)\b",
    r"\bslipping away\b", r"\bgive up on (life|everything|myself)\b",
]

_GRADUAL_INDICATORS = [
    # These are matched against affect trajectory, not individual turns
    "hopelessness", "worthlessness", "withdrawal", "isolation",
    "anhedonia", "insomnia", "despair", "emptiness",
]


def _match(patterns: list[str], text: str) -> Optional[str]:
    """Return first matching pattern label or None."""
    t = text.lower()
    for p in patterns:
        if re.search(p, t):
            return p
    return None


def classify_turn(text: str, turn_index: int = 0, session_id: str = "") -> list[CrisisSignal]:
    """Classify a single turn of user text. Returns a (possibly empty) list of signals.

    Signals are returned in descending severity order. The caller is responsible
    for de-duplicating and folding these into the cross-session trajectory.
    """
    signals: list[CrisisSignal] = []

    # --- EXPLICIT CRITICAL ---
    match = _match(_EXPLICIT_CRITICAL, text)
    if match:
        signals.append(CrisisSignal(
            signal_class=SignalClass.EXPLICIT,
            risk_level=RiskLevel.CRITICAL,
            indicator=f"Explicit critical pattern: {match}",
            confidence=0.95,
            raw_text=text[:200],
            turn_index=turn_index,
            session_id=session_id,
        ))

    # --- EXPLICIT HIGH ---
    if not signals:
        match = _match(_EXPLICIT_HIGH, text)
        if match:
            signals.append(CrisisSignal(
                signal_class=SignalClass.EXPLICIT,
                risk_level=RiskLevel.HIGH,
                indicator=f"Explicit high pattern: {match}",
                confidence=0.85,
                raw_text=text[:200],
                turn_index=turn_index,
                session_id=session_id,
            ))

    # --- MASKED HIGH ---
    match = _match(_MASKED_HIGH, text)
    if match:
        signals.append(CrisisSignal(
            signal_class=SignalClass.MASKED,
            risk_level=RiskLevel.HIGH,
            indicator=f"Masked high pattern: {match}",
            confidence=0.75,
            raw_text=text[:200],
            turn_index=turn_index,
            session_id=session_id,
        ))

    # --- MASKED MODERATE ---
    match = _match(_MASKED_MODERATE, text)
    if match:
        signals.append(CrisisSignal(
            signal_class=SignalClass.MASKED,
            risk_level=RiskLevel.MODERATE,
            indicator=f"Masked moderate pattern: {match}",
            confidence=0.60,
            raw_text=text[:200],
            turn_index=turn_index,
            session_id=session_id,
        ))

    return signals


def is_gradual_indicator(keyword: str) -> bool:
    """Check if a keyword (from affect engine vocabulary) is a gradual-crisis indicator."""
    return keyword.lower() in _GRADUAL_INDICATORS

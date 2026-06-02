"""
core/development_stage_engine.py

Development Stage Engine — GAIA Sprint G-9

Bridges lifespan, moral, and meaning-making development into one
readable, actionable output for the GAIA runtime.

Theoretical anchors
-------------------
  * Eriksonian psychosocial stages (lifespan arc)
  * Kohlberg moral development (pre-conventional → post-conventional)
  * Kegan subject-object / constructive-developmental levels (1-5)
  * Transition signal detection (theme fingerprinting)

Public API
----------
  DevelopmentProfile     — structured assessment result
  TransitionSignal       — enum of detected inflection-point signals
  DevelopmentStageEngine — stateless assessor
  DEFAULT_ENGINE         — module-level singleton

Canon Ref: C01 (Sovereignty), C15 (Self-knowledge), C30 (No silent failures)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ------------------------------------------------------------------ #
#  TransitionSignal                                                   #
# ------------------------------------------------------------------ #

class TransitionSignal(str, Enum):
    """Detected inflection-point signals derived from theme fingerprinting."""
    IDENTITY_CRISIS        = "identity_crisis"
    MEANING_COLLAPSE       = "meaning_collapse"
    INTIMACY_AVOIDANCE     = "intimacy_avoidance"
    GENERATIVITY_BLOCK     = "generativity_block"
    INTEGRATION_CHALLENGE  = "integration_challenge"
    MORAL_TRANSITION       = "moral_transition"
    GRIEF_UNPROCESSED      = "grief_unprocessed"
    AUTONOMY_RUPTURE       = "autonomy_rupture"
    NONE                   = "none"


# ------------------------------------------------------------------ #
#  Theme fingerprint maps                                             #
# ------------------------------------------------------------------ #

_SIGNAL_KEYWORDS: dict[TransitionSignal, list[str]] = {
    TransitionSignal.IDENTITY_CRISIS: [
        "who am i", "identity", "purpose", "direction", "lost", "undefined",
        "role", "mask", "persona", "authenticity",
    ],
    TransitionSignal.MEANING_COLLAPSE: [
        "meaningless", "pointless", "why bother", "nothing matters", "emptiness",
        "nihilism", "existential", "hollow", "void",
    ],
    TransitionSignal.INTIMACY_AVOIDANCE: [
        "alone", "isolation", "trust", "vulnerability", "closeness", "connection",
        "attachment", "partner", "relationship", "fear of love",
    ],
    TransitionSignal.GENERATIVITY_BLOCK: [
        "legacy", "contribution", "stagnant", "stagnation", "impact", "purpose",
        "leave behind", "mentor", "next generation", "create",
    ],
    TransitionSignal.INTEGRATION_CHALLENGE: [
        "regret", "acceptance", "peace", "wisdom", "coherence", "reconcile",
        "forgiveness", "whole", "complete", "mortality",
    ],
    TransitionSignal.MORAL_TRANSITION: [
        "right and wrong", "ethics", "values", "principle", "justice", "fairness",
        "conscience", "obligation", "duty", "moral",
    ],
    TransitionSignal.GRIEF_UNPROCESSED: [
        "grief", "loss", "death", "mourning", "bereavement", "missing", "absence",
        "gone", "never came back", "goodbye",
    ],
    TransitionSignal.AUTONOMY_RUPTURE: [
        "control", "autonomy", "freedom", "trapped", "powerless", "agency",
        "dependency", "helpless", "rules", "permission",
    ],
}


def _detect_signals(themes: list[str]) -> list[TransitionSignal]:
    """Map raw theme strings to TransitionSignal values via keyword overlap."""
    flat = " ".join(themes).lower()
    found: list[TransitionSignal] = []
    for signal, keywords in _SIGNAL_KEYWORDS.items():
        if any(kw in flat for kw in keywords):
            found.append(signal)
    return found or [TransitionSignal.NONE]


# ------------------------------------------------------------------ #
#  Kohlberg moral tier helper                                         #
# ------------------------------------------------------------------ #

def _kohlberg_tier(age: int) -> str:
    """Rough age-band heuristic for Kohlberg moral development level."""
    if age < 10:
        return "pre-conventional (obedience / self-interest)"
    if age < 16:
        return "conventional (conformity / law and order)"
    if age < 25:
        return "transitional conventional → post-conventional"
    return "post-conventional (social contract / universal principles)"


# ------------------------------------------------------------------ #
#  Kegan subject-object level helper                                  #
# ------------------------------------------------------------------ #

def _kegan_level(age: int) -> str:
    """Age-band heuristic for Kegan constructive-developmental level."""
    if age < 13:
        return "Level 2 — Imperial (needs, wishes, interests as sovereign)"
    if age < 20:
        return "Level 3 — Socialised (identity shaped by others' expectations)"
    if age < 40:
        return "Level 3→4 transition — Self-Authoring emerging"
    if age < 60:
        return "Level 4 — Self-Authoring (own values as identity anchor)"
    return "Level 4→5 — Self-Transforming (systems perspective, tolerates contradiction)"


# ------------------------------------------------------------------ #
#  DevelopmentProfile                                                 #
# ------------------------------------------------------------------ #

@dataclass
class DevelopmentProfile:
    """Structured output of a DevelopmentStageEngine assessment."""

    age_band: str
    erikson_stage: str
    primary_task: str
    likely_edges: list[str] = field(default_factory=list)
    likely_strengths: list[str] = field(default_factory=list)
    guidance: str = ""
    kohlberg_tier: str = ""
    kegan_level: str = ""
    detected_signals: list[TransitionSignal] = field(default_factory=list)
    signal_guidance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict for JSON envelopes and API responses."""
        return {
            "age_band":          self.age_band,
            "erikson_stage":     self.erikson_stage,
            "primary_task":      self.primary_task,
            "likely_edges":      self.likely_edges,
            "likely_strengths":  self.likely_strengths,
            "guidance":          self.guidance,
            "kohlberg_tier":     self.kohlberg_tier,
            "kegan_level":       self.kegan_level,
            "detected_signals":  [s.value for s in self.detected_signals],
            "signal_guidance":   self.signal_guidance,
        }


# ------------------------------------------------------------------ #
#  Signal → guidance map                                             #
# ------------------------------------------------------------------ #

_SIGNAL_GUIDANCE: dict[TransitionSignal, str] = {
    TransitionSignal.IDENTITY_CRISIS: (
        "Identity instability detected. Support exploration without forcing premature resolution. "
        "Ask: 'What would you do if no one was watching?'"
    ),
    TransitionSignal.MEANING_COLLAPSE: (
        "Meaning system under stress. Avoid toxic positivity. "
        "Help locate one small action that feels true — meaning follows action, not the reverse."
    ),
    TransitionSignal.INTIMACY_AVOIDANCE: (
        "Intimacy resistance present. Do not push closeness directly. "
        "Build trust incrementally; name the fear before naming the need."
    ),
    TransitionSignal.GENERATIVITY_BLOCK: (
        "Generativity blocked — the creative/contributive drive is frustrated. "
        "Find one concrete act of transmission: teaching, mentoring, making, or protecting."
    ),
    TransitionSignal.INTEGRATION_CHALLENGE: (
        "Integration work in progress. Honour regret without weaponising it. "
        "Support narrative coherence — the story of a life needs a plot, not just events."
    ),
    TransitionSignal.MORAL_TRANSITION: (
        "Moral framework in transition. Validate the discomfort of outgrowing rules "
        "without yet having new principles. Principle-based reasoning takes time."
    ),
    TransitionSignal.GRIEF_UNPROCESSED: (
        "Unprocessed grief present. Do not redirect to problem-solving. "
        "Make space for naming the loss; witness before offering meaning."
    ),
    TransitionSignal.AUTONOMY_RUPTURE: (
        "Autonomy or agency feels threatened. Restore sense of choice even in constrained contexts. "
        "Ask: 'What IS within your control right now?'"
    ),
    TransitionSignal.NONE: (
        "No acute transition signal detected. Continue developmental support appropriate to life stage."
    ),
}


# ------------------------------------------------------------------ #
#  DevelopmentStageEngine                                            #
# ------------------------------------------------------------------ #

class DevelopmentStageEngine:
    """
    Stateless engine that maps (age, themes) → DevelopmentProfile.

    Usage
    -----
        engine = DevelopmentStageEngine()
        profile = engine.assess(age=34, themes=["meaning", "direction", "identity"])
        print(profile.to_dict())
    """

    # ---- Base stage table ----------------------------------------- #

    _STAGES: list[dict[str, Any]] = [
        {
            "max_age":        12,
            "age_band":       "childhood",
            "erikson_stage":  "Trust vs. Mistrust / Autonomy / Initiative / Industry",
            "primary_task":   "Build safety, competence, trust, and emotional language.",
            "likely_edges":   ["shame", "fear", "dependency", "powerlessness"],
            "likely_strengths": ["play", "plasticity", "imagination", "receptivity"],
            "guidance":       "Prioritise safety, rhythm, co-regulation, and encouragement over abstraction.",
        },
        {
            "max_age":        19,
            "age_band":       "adolescence",
            "erikson_stage":  "Identity vs. Role Confusion",
            "primary_task":   "Identity formation: Who am I, apart from my environment?",
            "likely_edges":   ["role confusion", "peer-driven self-worth", "volatility", "impulsivity"],
            "likely_strengths": ["experimentation", "rapid learning", "intensity", "idealism"],
            "guidance":       "Support identity exploration without forcing premature certainty.",
        },
        {
            "max_age":        34,
            "age_band":       "early_adulthood",
            "erikson_stage":  "Intimacy vs. Isolation",
            "primary_task":   "Build intimacy, direction, and a livable structure for adult life.",
            "likely_edges":   ["commitment fear", "comparison", "instability", "perfectionism"],
            "likely_strengths": ["drive", "adaptation", "capacity to build", "curiosity"],
            "guidance":       "Choose fewer things more deeply. Consistency matters more than dramatic reinvention.",
        },
        {
            "max_age":        54,
            "age_band":       "midlife",
            "erikson_stage":  "Generativity vs. Stagnation",
            "primary_task":   "Generativity: create, teach, protect, and integrate contradictions.",
            "likely_edges":   ["stagnation", "resentment", "meaning crisis", "rigidity"],
            "likely_strengths": ["pattern recognition", "craft", "leadership", "endurance"],
            "guidance":       "Turn experience into transmission. Build what outlives the mood of the week.",
        },
        {
            "max_age":        float("inf"),
            "age_band":       "later_life",
            "erikson_stage":  "Ego Integrity vs. Despair",
            "primary_task":   "Integration, legacy, and coherent self-reflection.",
            "likely_edges":   ["despair", "isolation", "rigidity", "disengagement"],
            "likely_strengths": ["wisdom", "perspective", "distillation", "equanimity"],
            "guidance":       "Name what matters most, simplify, and transmit living knowledge.",
        },
    ]

    # ---- Unknown-age fallback ------------------------------------- #

    _UNKNOWN: dict[str, Any] = {
        "age_band":       "unknown",
        "erikson_stage":  "indeterminate",
        "primary_task":   "Build enough context to identify the current developmental challenge.",
        "likely_edges":   ["identity diffusion", "role confusion", "meaning instability"],
        "likely_strengths": ["adaptability", "openness"],
        "guidance": (
            "Ask what task keeps repeating: identity, intimacy, mastery, "
            "generativity, or integration."
        ),
    }

    # ---- Public methods ------------------------------------------- #

    def assess(
        self,
        age: int | None = None,
        themes: list[str] | None = None,
    ) -> DevelopmentProfile:
        """
        Return a DevelopmentProfile for the given age and optional themes.

        Parameters
        ----------
        age:    Integer age in years, or None if unknown.
        themes: Free-text theme strings (e.g. ["identity", "loss", "meaning"]).
                Used for TransitionSignal detection and signal-specific guidance.
        """
        themes = [t.lower() for t in (themes or [])]
        signals = _detect_signals(themes)
        signal_guidance = [
            _SIGNAL_GUIDANCE[s] for s in signals if s != TransitionSignal.NONE
        ] or [_SIGNAL_GUIDANCE[TransitionSignal.NONE]]

        stage = self._UNKNOWN if age is None else self._stage_for_age(age)

        return DevelopmentProfile(
            age_band          = stage["age_band"],
            erikson_stage     = stage["erikson_stage"],
            primary_task      = stage["primary_task"],
            likely_edges      = list(stage["likely_edges"]),
            likely_strengths  = list(stage["likely_strengths"]),
            guidance          = stage["guidance"],
            kohlberg_tier     = _kohlberg_tier(age) if age is not None else "indeterminate",
            kegan_level       = _kegan_level(age) if age is not None else "indeterminate",
            detected_signals  = signals,
            signal_guidance   = signal_guidance,
        )

    def assess_with_themes(self, age: int | None, *themes: str) -> DevelopmentProfile:
        """Convenience variadic wrapper around assess()."""
        return self.assess(age=age, themes=list(themes))

    # ---- Private helpers ------------------------------------------ #

    def _stage_for_age(self, age: int) -> dict[str, Any]:
        for stage in self._STAGES:
            if age <= stage["max_age"]:
                return stage
        return self._STAGES[-1]  # should never reach here


# ------------------------------------------------------------------ #
#  Module-level singleton                                             #
# ------------------------------------------------------------------ #

DEFAULT_ENGINE: DevelopmentStageEngine = DevelopmentStageEngine()

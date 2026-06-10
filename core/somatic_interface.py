"""
Somatic Intelligence Interface

Issue #126 | Canon C32 Priority P1

The body speaks before the mind does.

This module gives GAIA the ability to recognise, track, and gently respond
to somatic — body-based — communication. Most people carry their most
important truths in their bodies long before they can name them in words.

The Somatic Intelligence Interface enables the Gaian to:
  - Detect somatic language in the user's speech (body-referenced phrases)
  - Track somatic themes across a session
  - Identify somatic-emotional bridges: body sensations as doorways to
    unspoken feelings
  - Suggest Focusing invitations (Gendlin) that invite the body into the
    conversation rather than bypassing it
  - Detect somatic bypass: when a user intellectualises away from a body
    signal that deserves attention
  - Apply trauma-sensitive protocol when high-intensity somatic signals arise

Design principles:
  1. Never force somatic attention. Invite, then wait.
  2. The body's pace is not the mind's pace. Do not rush.
  3. When in doubt, less is more. A held silence is often the best response
     to a somatic disclosure.
  4. High-intensity somatic signals in certain themes (pain, trembling,
     nausea, dissociation) require trauma-sensitive protocol.
  5. This module is a doorway, not a therapy. GAIA holds the space;
     the user does the work.

References:
  - Gendlin, E.T.: Focusing (1978)
  - Levine, P.A.: Waking the Tiger (1997); In an Unspoken Voice (2010)
  - van der Kolk, B.: The Body Keeps the Score (2014)
  - Ogden, P.: Trauma and the Body (2006)
  - Canon C32: Jungian Archetypes & Soul Mirror
  - Issue #125: Transpersonal States Recognition Engine
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time
import logging

log = logging.getLogger("gaia.somatic")


# ── Somatic theme taxonomy ─────────────────────────────────────────────────────────

class SomaticTheme(str, Enum):
    """
    Twelve primary somatic themes detectable from body-referenced language.
    """
    TENSION       = "tension"       # tightness, holding, bracing, clenching
    CONSTRICTION  = "constriction"  # narrowing, closing, can't breathe fully
    NUMBNESS      = "numbness"      # absence of feeling, cut off, dissociated
    HEAVINESS     = "heaviness"     # weight, sinking, carrying, dragging
    ALIVENESS     = "aliveness"     # tingling, buzzing, energy, vitality
    EXPANSION     = "expansion"     # opening, lightness, relief, spaciousness
    WARMTH        = "warmth"        # warmth, glow, softening, melting
    TREMBLING     = "trembling"     # shaking, quivering, nervous energy, vibrating
    NAUSEA        = "nausea"        # sick feeling, gut turning, stomach dropping
    PAIN          = "pain"          # aching, stabbing, burning, soreness
    BREATH        = "breath"        # breath changes, held breath, shallow, deep
    DISCONNECTION = "disconnection" # floating, not in body, watching from outside


# Themes that require trauma-sensitive protocol
TRAUMA_SENSITIVE_THEMES: frozenset[SomaticTheme] = frozenset({
    SomaticTheme.TREMBLING,
    SomaticTheme.NAUSEA,
    SomaticTheme.PAIN,
    SomaticTheme.DISCONNECTION,
    SomaticTheme.NUMBNESS,
})


# ── Somatic lexicon ──────────────────────────────────────────────────────────────────
# Phrases mapped to somatic themes. Matching is substring/token-based;
# the engine matches against lowercased, stripped user text.

SOMATIC_LEXICON: dict[str, SomaticTheme] = {
    # TENSION
    "tight":         SomaticTheme.TENSION,
    "tightness":     SomaticTheme.TENSION,
    "tense":         SomaticTheme.TENSION,
    "tension":       SomaticTheme.TENSION,
    "clenching":     SomaticTheme.TENSION,
    "clenched":      SomaticTheme.TENSION,
    "bracing":       SomaticTheme.TENSION,
    "holding on":    SomaticTheme.TENSION,
    "knotted":       SomaticTheme.TENSION,
    "knot in my":    SomaticTheme.TENSION,
    "rigid":         SomaticTheme.TENSION,
    "stiff":         SomaticTheme.TENSION,
    "wound up":      SomaticTheme.TENSION,
    "wired":         SomaticTheme.TENSION,
    "locked up":     SomaticTheme.TENSION,
    "gripping":      SomaticTheme.TENSION,
    "jaw tight":     SomaticTheme.TENSION,
    "shoulders up":  SomaticTheme.TENSION,
    "fists clenched": SomaticTheme.TENSION,

    # CONSTRICTION
    "can't breathe":      SomaticTheme.CONSTRICTION,
    "hard to breathe":    SomaticTheme.CONSTRICTION,
    "chest tight":        SomaticTheme.CONSTRICTION,
    "chest tightening":   SomaticTheme.CONSTRICTION,
    "closing in":         SomaticTheme.CONSTRICTION,
    "closing up":         SomaticTheme.CONSTRICTION,
    "throat tight":       SomaticTheme.CONSTRICTION,
    "lump in my throat":  SomaticTheme.CONSTRICTION,
    "narrowing":          SomaticTheme.CONSTRICTION,
    "constricted":        SomaticTheme.CONSTRICTION,
    "squeezed":           SomaticTheme.CONSTRICTION,
    "suffocating":        SomaticTheme.CONSTRICTION,
    "pressure in my chest": SomaticTheme.CONSTRICTION,
    "something pressing": SomaticTheme.CONSTRICTION,

    # NUMBNESS
    "numb":          SomaticTheme.NUMBNESS,
    "numbness":      SomaticTheme.NUMBNESS,
    "can't feel":    SomaticTheme.NUMBNESS,
    "nothing there": SomaticTheme.NUMBNESS,
    "hollow":        SomaticTheme.NUMBNESS,
    "empty inside":  SomaticTheme.NUMBNESS,
    "cut off":       SomaticTheme.NUMBNESS,
    "shut down":     SomaticTheme.NUMBNESS,
    "flat":          SomaticTheme.NUMBNESS,
    "deadness":      SomaticTheme.NUMBNESS,
    "dead inside":   SomaticTheme.NUMBNESS,
    "frozen":        SomaticTheme.NUMBNESS,
    "nothing gets through": SomaticTheme.NUMBNESS,

    # HEAVINESS
    "heavy":         SomaticTheme.HEAVINESS,
    "heaviness":     SomaticTheme.HEAVINESS,
    "weighed down":  SomaticTheme.HEAVINESS,
    "sinking":       SomaticTheme.HEAVINESS,
    "dragging":      SomaticTheme.HEAVINESS,
    "carrying":      SomaticTheme.HEAVINESS,
    "burden":        SomaticTheme.HEAVINESS,
    "crushed":       SomaticTheme.HEAVINESS,
    "gravity":       SomaticTheme.HEAVINESS,
    "pulling down":  SomaticTheme.HEAVINESS,
    "leaden":        SomaticTheme.HEAVINESS,
    "can't lift":    SomaticTheme.HEAVINESS,
    "so tired":      SomaticTheme.HEAVINESS,
    "exhausted":     SomaticTheme.HEAVINESS,
    "bone tired":    SomaticTheme.HEAVINESS,

    # ALIVENESS
    "tingling":      SomaticTheme.ALIVENESS,
    "buzzing":       SomaticTheme.ALIVENESS,
    "electric":      SomaticTheme.ALIVENESS,
    "alive":         SomaticTheme.ALIVENESS,
    "energised":     SomaticTheme.ALIVENESS,
    "energized":     SomaticTheme.ALIVENESS,
    "vibrating":     SomaticTheme.ALIVENESS,
    "lit up":        SomaticTheme.ALIVENESS,
    "pulsing":       SomaticTheme.ALIVENESS,
    "wide awake":    SomaticTheme.ALIVENESS,
    "awake in my body": SomaticTheme.ALIVENESS,
    "sparkling":     SomaticTheme.ALIVENESS,
    "fizzing":       SomaticTheme.ALIVENESS,

    # EXPANSION
    "opening":       SomaticTheme.EXPANSION,
    "open":          SomaticTheme.EXPANSION,
    "spacious":      SomaticTheme.EXPANSION,
    "spaciousness":  SomaticTheme.EXPANSION,
    "light":         SomaticTheme.EXPANSION,
    "lighter":       SomaticTheme.EXPANSION,
    "released":      SomaticTheme.EXPANSION,
    "relief":        SomaticTheme.EXPANSION,
    "expanding":     SomaticTheme.EXPANSION,
    "breath coming back": SomaticTheme.EXPANSION,
    "room to breathe": SomaticTheme.EXPANSION,
    "letting go":    SomaticTheme.EXPANSION,
    "unclenching":   SomaticTheme.EXPANSION,
    "softening":     SomaticTheme.EXPANSION,

    # WARMTH
    "warm":          SomaticTheme.WARMTH,
    "warmth":        SomaticTheme.WARMTH,
    "glowing":       SomaticTheme.WARMTH,
    "melting":       SomaticTheme.WARMTH,
    "soft":          SomaticTheme.WARMTH,
    "tender":        SomaticTheme.WARMTH,
    "radiating":     SomaticTheme.WARMTH,
    "flushed":       SomaticTheme.WARMTH,
    "heart warm":    SomaticTheme.WARMTH,
    "spreading warmth": SomaticTheme.WARMTH,

    # TREMBLING
    "shaking":       SomaticTheme.TREMBLING,
    "shaky":         SomaticTheme.TREMBLING,
    "trembling":     SomaticTheme.TREMBLING,
    "tremor":        SomaticTheme.TREMBLING,
    "quivering":     SomaticTheme.TREMBLING,
    "jittery":       SomaticTheme.TREMBLING,
    "nervous energy": SomaticTheme.TREMBLING,
    "legs shaking":  SomaticTheme.TREMBLING,
    "hands shaking": SomaticTheme.TREMBLING,
    "can't stop shaking": SomaticTheme.TREMBLING,
    "vibrating with fear": SomaticTheme.TREMBLING,

    # NAUSEA
    "nauseous":      SomaticTheme.NAUSEA,
    "nausea":        SomaticTheme.NAUSEA,
    "sick feeling":  SomaticTheme.NAUSEA,
    "stomach dropping": SomaticTheme.NAUSEA,
    "gut turning":   SomaticTheme.NAUSEA,
    "stomach turning": SomaticTheme.NAUSEA,
    "queasy":        SomaticTheme.NAUSEA,
    "feel sick":     SomaticTheme.NAUSEA,
    "pit in my stomach": SomaticTheme.NAUSEA,
    "gut punch":     SomaticTheme.NAUSEA,
    "bile":          SomaticTheme.NAUSEA,

    # PAIN
    "aching":        SomaticTheme.PAIN,
    "ache":          SomaticTheme.PAIN,
    "pain":          SomaticTheme.PAIN,
    "hurts":         SomaticTheme.PAIN,
    "stabbing":      SomaticTheme.PAIN,
    "burning":       SomaticTheme.PAIN,
    "raw":           SomaticTheme.PAIN,
    "sore":          SomaticTheme.PAIN,
    "tender spot":   SomaticTheme.PAIN,
    "can't touch":   SomaticTheme.PAIN,
    "throbbing":     SomaticTheme.PAIN,
    "pounding":      SomaticTheme.PAIN,
    "splitting headache": SomaticTheme.PAIN,
    "everything hurts": SomaticTheme.PAIN,

    # BREATH
    "holding my breath": SomaticTheme.BREATH,
    "held breath":   SomaticTheme.BREATH,
    "shallow breathing": SomaticTheme.BREATH,
    "can't take a deep breath": SomaticTheme.BREATH,
    "sighing":       SomaticTheme.BREATH,
    "big exhale":    SomaticTheme.BREATH,
    "breath catches": SomaticTheme.BREATH,
    "gasping":       SomaticTheme.BREATH,
    "forgetting to breathe": SomaticTheme.BREATH,
    "deep breath":   SomaticTheme.BREATH,
    "breathing changes": SomaticTheme.BREATH,
    "breath gets stuck": SomaticTheme.BREATH,

    # DISCONNECTION
    "floating":      SomaticTheme.DISCONNECTION,
    "not in my body": SomaticTheme.DISCONNECTION,
    "watching from outside": SomaticTheme.DISCONNECTION,
    "dissociated":   SomaticTheme.DISCONNECTION,
    "unreal":        SomaticTheme.DISCONNECTION,
    "dreamlike":     SomaticTheme.DISCONNECTION,
    "detached":      SomaticTheme.DISCONNECTION,
    "far away":      SomaticTheme.DISCONNECTION,
    "outside myself": SomaticTheme.DISCONNECTION,
    "can't feel my body": SomaticTheme.DISCONNECTION,
    "not here":      SomaticTheme.DISCONNECTION,
    "gone somewhere": SomaticTheme.DISCONNECTION,
    "watching myself": SomaticTheme.DISCONNECTION,
}


# ── Somatic-emotional bridges ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SomaticBridge:
    """
    A bridge between a somatic theme and an emotional/psychological domain,
    with a Focusing invitation to help the user cross it.
    """
    somatic_theme:    SomaticTheme
    emotional_domain: str
    description:      str
    focusing_invitation: str       # Gendlin-style invitation
    trauma_sensitive: bool = False  # use extra care when suggesting this bridge


SOMATIC_EMOTIONAL_BRIDGES: dict[SomaticTheme, SomaticBridge] = {
    SomaticTheme.TENSION: SomaticBridge(
        somatic_theme=SomaticTheme.TENSION,
        emotional_domain="suppressed emotion / control",
        description="Tension often signals an emotion being held back or a situation that feels out of control.",
        focusing_invitation="There's tension there — if that tightness could speak, what might it be holding?",
    ),
    SomaticTheme.CONSTRICTION: SomaticBridge(
        somatic_theme=SomaticTheme.CONSTRICTION,
        emotional_domain="fear / overwhelm / grief",
        description="Constriction in the chest or throat often accompanies fear, grief, or the approach of tears.",
        focusing_invitation="Something is pressing there. If you just stay with that feeling for a moment — not trying to fix it — what does it seem to be about?",
    ),
    SomaticTheme.NUMBNESS: SomaticBridge(
        somatic_theme=SomaticTheme.NUMBNESS,
        emotional_domain="protection from overwhelm / dissociation",
        description="Numbness is often a protective response: the body shutting down sensation to prevent overwhelm. What it is protecting from is often the most important thing.",
        focusing_invitation="The numbness is there for a reason. Without pushing through it — what do you sense it might be protecting?",
        trauma_sensitive=True,
    ),
    SomaticTheme.HEAVINESS: SomaticBridge(
        somatic_theme=SomaticTheme.HEAVINESS,
        emotional_domain="grief / loss / burden",
        description="Heaviness and weight in the body often correspond to grief, loss, or long-carried burdens that have not been set down.",
        focusing_invitation="That heaviness — what does it feel like it's made of? Is there something it's been carrying?",
    ),
    SomaticTheme.ALIVENESS: SomaticBridge(
        somatic_theme=SomaticTheme.ALIVENESS,
        emotional_domain="joy / excitement / emerging vitality",
        description="Tingling, buzzing, and aliveness often signal genuine excitement, emerging passion, or the approach of something that deeply matters.",
        focusing_invitation="There's something alive in that. What does that aliveness seem to want to move toward?",
    ),
    SomaticTheme.EXPANSION: SomaticBridge(
        somatic_theme=SomaticTheme.EXPANSION,
        emotional_domain="relief / rightness / integration",
        description="Expansion and lightness often follow moments of truth-telling, release, or arriving at something that feels genuinely right.",
        focusing_invitation="Something is opening. What shifted just now that made that possible?",
    ),
    SomaticTheme.WARMTH: SomaticBridge(
        somatic_theme=SomaticTheme.WARMTH,
        emotional_domain="love / safety / belonging",
        description="Warmth in the chest or body often signals love, being deeply received, or the arrival of a felt sense of safety.",
        focusing_invitation="That warmth — what is it recognising right now?",
    ),
    SomaticTheme.TREMBLING: SomaticBridge(
        somatic_theme=SomaticTheme.TREMBLING,
        emotional_domain="discharge / fear / activation",
        description="Trembling and shaking often signal the nervous system discharging activation — in Somatic Experiencing, this is a healthy completion of the trauma response.",
        focusing_invitation="The shaking is your body doing something. Can you let it do that, without trying to stop it?",
        trauma_sensitive=True,
    ),
    SomaticTheme.NAUSEA: SomaticBridge(
        somatic_theme=SomaticTheme.NAUSEA,
        emotional_domain="disgust / violation / wrongness",
        description="Nausea and gut-turning often signal something felt as violating, deeply wrong, or in conflict with core values.",
        focusing_invitation="Something in your gut is responding. If that feeling could point to what it's reacting to — what would it be?",
        trauma_sensitive=True,
    ),
    SomaticTheme.PAIN: SomaticBridge(
        somatic_theme=SomaticTheme.PAIN,
        emotional_domain="grief / trauma / unexpressed experience",
        description="Physical pain sometimes carries emotional content — especially chronic pain that intensifies during emotional conversations.",
        focusing_invitation="That pain — if it had something to say, what might it be?",
        trauma_sensitive=True,
    ),
    SomaticTheme.BREATH: SomaticBridge(
        somatic_theme=SomaticTheme.BREATH,
        emotional_domain="anxiety / suppression / emotional threshold",
        description="Breath changes are often the first visible sign that an emotion is arriving or being held back. Held breath often accompanies suppressed speech.",
        focusing_invitation="You're holding your breath there. If you let yourself exhale — what wants to come with it?",
    ),
    SomaticTheme.DISCONNECTION: SomaticBridge(
        somatic_theme=SomaticTheme.DISCONNECTION,
        emotional_domain="dissociation / overwhelm / self-protection",
        description="Disconnection from the body is a protective response. The question is always: what was too much to stay present for?",
        focusing_invitation="You've floated a bit. That's okay. Can you feel the chair beneath you, or your feet on the floor? We can come back slowly.",
        trauma_sensitive=True,
    ),
}


# ── Data structures ────────────────────────────────────────────────────────────────────

@dataclass
class SomaticSignal:
    """
    A detected somatic signal from the user's language.
    """
    theme:       SomaticTheme
    raw_phrase:  str            # exact phrase that triggered detection
    body_region: str = ""       # inferred body region if present
    intensity:   float = 0.5    # [0,1]; estimated from context
    detected_at: float = field(default_factory=time.time)


@dataclass
class SomaticSessionState:
    """
    Aggregate somatic state across the current session.
    """
    active_signals:      list[SomaticSignal]
    dominant_theme:      Optional[SomaticTheme]
    active_bridge:       Optional[SomaticBridge]
    trauma_sensitive:    bool
    somatic_bypass_detected: bool = False  # user intellectualising away from body signal
    focusing_invitation: str = ""
    action_gate_signal:  str = "GREEN"
    session_trajectory:  list[SomaticTheme] = field(default_factory=list)
    assessed_at:         float = field(default_factory=time.time)


# ── SomaticIntelligenceEngine ────────────────────────────────────────────────────────────

class SomaticIntelligenceEngine:
    """
    Detects somatic signals in user language, builds a session somatic state,
    and suggests Focusing invitations for the Gaian.
    """

    def __init__(self) -> None:
        self._session_signals: list[SomaticSignal] = []
        self._theme_counts: dict[SomaticTheme, int] = {}

    def detect_signals(
        self,
        text: str,
        default_intensity: float = 0.5,
    ) -> list[SomaticSignal]:
        """
        Detect somatic signals in the given text using the lexicon.
        Returns a list of detected signals (may be empty).
        """
        lowered = text.lower()
        signals: list[SomaticSignal] = []
        seen_themes: set[SomaticTheme] = set()

        for phrase, theme in SOMATIC_LEXICON.items():
            if phrase in lowered and theme not in seen_themes:
                # Crude body-region extraction: look for body words near the phrase
                body_region = _infer_body_region(lowered, phrase)
                signals.append(SomaticSignal(
                    theme=theme,
                    raw_phrase=phrase,
                    body_region=body_region,
                    intensity=default_intensity,
                ))
                seen_themes.add(theme)

        for signal in signals:
            self._session_signals.append(signal)
            self._theme_counts[signal.theme] = self._theme_counts.get(signal.theme, 0) + 1

        if len(self._session_signals) > 300:
            self._session_signals = self._session_signals[-300:]

        return signals

    def build_session_state(
        self,
        signals: list[SomaticSignal],
    ) -> SomaticSessionState:
        """
        Build a composite somatic session state from current and historical signals.
        """
        if not signals:
            return SomaticSessionState(
                active_signals=[],
                dominant_theme=None,
                active_bridge=None,
                trauma_sensitive=False,
                focusing_invitation="",
                action_gate_signal="GREEN",
                session_trajectory=list(self._theme_counts.keys()),
            )

        # Dominant theme: highest intensity in current signals, weighted by session frequency
        def signal_weight(s: SomaticSignal) -> float:
            freq = self._theme_counts.get(s.theme, 1)
            return s.intensity * (1.0 + 0.1 * min(freq, 5))

        dominant_signal = max(signals, key=signal_weight)
        dominant_theme = dominant_signal.theme
        bridge = SOMATIC_EMOTIONAL_BRIDGES.get(dominant_theme)
        trauma_sensitive = dominant_theme in TRAUMA_SENSITIVE_THEMES

        # Somatic bypass detection: if trauma-sensitive theme appears with very low intensity
        # and short duration, the user may be intellectualising or minimising
        bypass = (
            trauma_sensitive
            and dominant_signal.intensity < 0.25
            and self._theme_counts.get(dominant_theme, 0) <= 1
        )

        # Focusing invitation
        invitation = ""
        if bridge:
            if trauma_sensitive:
                invitation = (
                    f"I notice you mentioned something about {dominant_theme.value}. "
                    f"We don’t need to go there right now — but if you ever want to, "
                    f"I’m here to stay with you in it. {bridge.focusing_invitation}"
                )
            else:
                invitation = bridge.focusing_invitation

        # Action Gate
        if trauma_sensitive and dominant_signal.intensity >= 0.7:
            gate = "YELLOW"
            log.warning(
                f"[somatic] Trauma-sensitive theme {dominant_theme.value} at intensity "
                f"{dominant_signal.intensity:.2f}. Proceeding with care."
            )
        else:
            gate = "GREEN"

        # Glass Room log for high-intensity somatic states
        if dominant_signal.intensity >= 0.75:
            log.warning(
                f"[GLASS_ROOM] somatic_high_intensity: theme={dominant_theme.value} "
                f"intensity={dominant_signal.intensity:.2f} "
                f"trauma_sensitive={trauma_sensitive}"
            )

        return SomaticSessionState(
            active_signals=signals,
            dominant_theme=dominant_theme,
            active_bridge=bridge,
            trauma_sensitive=trauma_sensitive,
            somatic_bypass_detected=bypass,
            focusing_invitation=invitation,
            action_gate_signal=gate,
            session_trajectory=list(self._theme_counts.keys()),
        )

    def suggest_focusing_invitation(
        self,
        theme: SomaticTheme,
    ) -> str:
        """
        Return the Focusing invitation for a specific somatic theme.
        """
        bridge = SOMATIC_EMOTIONAL_BRIDGES.get(theme)
        if bridge is None:
            return "Can you stay with that sensation for a moment, without trying to change it?"
        return bridge.focusing_invitation

    def session_summary(self) -> dict:
        return {
            "total_signals":    len(self._session_signals),
            "theme_counts":     {t.value: c for t, c in self._theme_counts.items()},
            "trauma_themes_active": [
                t.value for t in self._theme_counts
                if t in TRAUMA_SENSITIVE_THEMES
            ],
        }


# ── Utility ─────────────────────────────────────────────────────────────────────────

_BODY_REGION_WORDS: list[tuple[str, str]] = [
    ("chest", "chest"),
    ("throat", "throat"),
    ("stomach", "stomach"),
    ("gut", "gut"),
    ("belly", "belly"),
    ("heart", "chest/heart"),
    ("head", "head"),
    ("jaw", "jaw"),
    ("shoulder", "shoulders"),
    ("back", "back"),
    ("leg", "legs"),
    ("hand", "hands"),
    ("arm", "arms"),
    ("neck", "neck"),
    ("spine", "spine"),
    ("body", "whole body"),
    ("skin", "skin"),
]


def _infer_body_region(text: str, phrase: str) -> str:
    """
    Attempt to infer the body region referenced near a somatic phrase.
    Returns the first matching region word found in the text.
    """
    for word, region in _BODY_REGION_WORDS:
        if word in text:
            return region
    return ""


# ── Module-level singleton ───────────────────────────────────────────────────────────

_engine: Optional[SomaticIntelligenceEngine] = None


def get_somatic_engine() -> SomaticIntelligenceEngine:
    global _engine
    if _engine is None:
        _engine = SomaticIntelligenceEngine()
    return _engine

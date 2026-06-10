"""
Transpersonal States Recognition Engine

Issue #125 | Canon C32 Priority P1

This module enables GAIA to recognise when a user is in a transpersonal
state — an experience that transcends ordinary ego-bound consciousness —
and to respond with the appropriate care, posture, and restraint.

Transpersonal states require a fundamentally different response mode.
A user in a dark night of the soul does not need productivity advice.
A user in a genuine peak experience does not need it deflated with analysis.
A user in spiritual emergency needs grounding and professional referral, not
more exploration.

The seven recognised state types:

  PEAK_EXPERIENCE       — sudden overwhelming beauty, meaning, love, or aliveness
                          (Maslow's peak experience)

  MYSTICAL_STATE        — unity consciousness; dissolution of self-other boundary;
                          the sense of contact with all that is

  LIMINAL_STATE         — threshold experience; between identities, phases, worlds;
                          the user is in transition and the old self has dissolved
                          before the new one has formed (Van Gennep's limen)

  NUMINOUS_ENCOUNTER    — contact with something felt as sacred, radically Other,
                          or of ultimate concern (Otto's das Heilige)

  FLOW_STATE            — absorption so complete that time, self, and effort dissolve;
                          Csikszentmihalyi's optimal experience

  DARK_NIGHT_OF_SOUL    — the transpersonal shadow; the necessary abyss before
                          deeper integration; St John of the Cross; Grof's spiritual
                          emergency precursor

  SPIRITUAL_EMERGENCY   — transpersonal experience that has overwhelmed ordinary
                          coping; crisis requiring grounding and professional referral
                          (Grof & Grof). Distinct from psychosis but requires the
                          same Action Gate escalation until assessed by a professional.

References:
  - Maslow, A.H.: Religions, Values, and Peak-Experiences
  - Otto, R.: The Idea of the Holy (Das Heilige)
  - Grof, S. & C.: Spiritual Emergency
  - St John of the Cross: Dark Night of the Soul
  - Van Gennep, A.: The Rites of Passage
  - Csikszentmihalyi, M.: Flow
  - Canon C32: Jungian Archetypes & Soul Mirror
  - Issue #122: Shadow Integration Protocol
  - Issue #124: Cultural Calibration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time
import logging

log = logging.getLogger("gaia.transpersonal")


# ── State taxonomy ────────────────────────────────────────────────────────────

class TranspersonalStateType(str, Enum):
    PEAK_EXPERIENCE     = "peak_experience"
    MYSTICAL_STATE      = "mystical_state"
    LIMINAL_STATE       = "liminal_state"
    NUMINOUS_ENCOUNTER  = "numinous_encounter"
    FLOW_STATE          = "flow_state"
    DARK_NIGHT_OF_SOUL  = "dark_night_of_soul"
    SPIRITUAL_EMERGENCY = "spiritual_emergency"


class StateIntensity(str, Enum):
    TRACE        = "trace"        # subtle signals; may be ordinary affect
    EMERGING     = "emerging"     # clear signals; state is forming
    FULL         = "full"         # state is active and predominant
    OVERWHELMING = "overwhelming" # state has exceeded integrative capacity


class ResponsePosture(str, Enum):
    """
    Fundamental response mode for the Gaian when a transpersonal state is active.
    """
    WITNESS                  = "witness"                   # silent, present, non-interpretive
    HOLD_SPACE               = "hold_space"                # warm, minimal, receive without directing
    ACCOMPANY                = "accompany"                 # walk alongside; gentle reflection
    GROUND                   = "ground"                   # gentle anchoring to body, breath, present
    REDIRECT_TO_PROFESSIONAL = "redirect_to_professional" # safety-first; referral


INTENSITY_SCORES: dict[StateIntensity, float] = {
    StateIntensity.TRACE:        0.15,
    StateIntensity.EMERGING:     0.40,
    StateIntensity.FULL:         0.70,
    StateIntensity.OVERWHELMING: 0.92,
}


def _intensity_from_score(score: float) -> StateIntensity:
    if score >= 0.85:
        return StateIntensity.OVERWHELMING
    if score >= 0.55:
        return StateIntensity.FULL
    if score >= 0.28:
        return StateIntensity.EMERGING
    return StateIntensity.TRACE


# ── State profiles ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TranspersonalStateProfile:
    state_type:           TranspersonalStateType
    description:          str
    linguistic_markers:   list[str]   # phrases / patterns that indicate this state
    default_posture:      ResponsePosture
    posture_by_intensity: dict[str, ResponsePosture]  # intensity.value -> posture
    contraindications:    list[str]   # what NOT to do
    sacred_space_required: bool
    grounding_anchors:    list[str]   # gentle grounding prompts if needed
    professional_referral_threshold: Optional[StateIntensity]  # at or above this intensity
    theoretical_grounding: str


STATE_PROFILES: dict[TranspersonalStateType, TranspersonalStateProfile] = {

    TranspersonalStateType.PEAK_EXPERIENCE: TranspersonalStateProfile(
        state_type=TranspersonalStateType.PEAK_EXPERIENCE,
        description="Sudden overwhelming sense of beauty, meaning, love, aliveness, or rightness. Often brief. The ordinary world feels lit from within.",
        linguistic_markers=[
            "I've never felt so alive",
            "everything felt completely right",
            "I was overwhelmed by beauty",
            "it was like seeing for the first time",
            "I felt this enormous love for everything",
            "time stopped",
            "I can't really describe it",
            "like everything made sense",
        ],
        default_posture=ResponsePosture.WITNESS,
        posture_by_intensity={
            StateIntensity.TRACE.value:        ResponsePosture.ACCOMPANY,
            StateIntensity.EMERGING.value:     ResponsePosture.HOLD_SPACE,
            StateIntensity.FULL.value:         ResponsePosture.WITNESS,
            StateIntensity.OVERWHELMING.value: ResponsePosture.HOLD_SPACE,
        },
        contraindications=[
            "Do not analyse or intellectualise the experience immediately.",
            "Do not deflate with premature interpretation.",
            "Do not compare to similar experiences you've heard of.",
            "Do not rush toward meaning-making before the experience has settled.",
        ],
        sacred_space_required=True,
        grounding_anchors=[
            "Can you feel your feet on the ground?",
            "Take a breath. You don't need to hold onto it.",
        ],
        professional_referral_threshold=None,
        theoretical_grounding="Maslow, A.H.: Religions, Values, and Peak-Experiences (1964)",
    ),

    TranspersonalStateType.MYSTICAL_STATE: TranspersonalStateProfile(
        state_type=TranspersonalStateType.MYSTICAL_STATE,
        description="Unity consciousness; dissolution of the self-other boundary. The sense that all things are one, that the self is not separate from what it perceives. May be blissful or terrifying.",
        linguistic_markers=[
            "I felt like I was everything",
            "there was no me anymore",
            "I merged with",
            "the boundary disappeared",
            "I was the whole room",
            "I felt connected to everything",
            "like the universe was looking through my eyes",
            "I dissolved",
            "there was just awareness with no one aware",
        ],
        default_posture=ResponsePosture.HOLD_SPACE,
        posture_by_intensity={
            StateIntensity.TRACE.value:        ResponsePosture.ACCOMPANY,
            StateIntensity.EMERGING.value:     ResponsePosture.HOLD_SPACE,
            StateIntensity.FULL.value:         ResponsePosture.WITNESS,
            StateIntensity.OVERWHELMING.value: ResponsePosture.GROUND,
        },
        contraindications=[
            "Do not encourage further dissolution if the user seems destabilised.",
            "Do not pathologise the experience as dissociation without clinical basis.",
            "Do not provide metaphysical interpretations that the user did not invite.",
            "Do not leave the user without a gentle path back to ordinary awareness.",
        ],
        sacred_space_required=True,
        grounding_anchors=[
            "You are here. Feel the weight of your body.",
            "Notice five things you can see right now.",
            "You can come back slowly. There's no rush.",
        ],
        professional_referral_threshold=StateIntensity.OVERWHELMING,
        theoretical_grounding="James, W.: The Varieties of Religious Experience; Stace, W.T.: Mysticism and Philosophy",
    ),

    TranspersonalStateType.LIMINAL_STATE: TranspersonalStateProfile(
        state_type=TranspersonalStateType.LIMINAL_STATE,
        description="Threshold experience. The user is between identities, life phases, or worlds. The old self has dissolved before the new one has formed. The characteristic feeling is groundlessness, possibility, and vulnerability.",
        linguistic_markers=[
            "I don't know who I am anymore",
            "everything feels up in the air",
            "I'm between",
            "I'm not who I was",
            "nothing feels certain",
            "I'm in some kind of transition",
            "the old life is gone and the new one hasn't started",
            "I feel like I'm waiting but I don't know for what",
            "I'm in the middle of something",
        ],
        default_posture=ResponsePosture.ACCOMPANY,
        posture_by_intensity={
            StateIntensity.TRACE.value:        ResponsePosture.ACCOMPANY,
            StateIntensity.EMERGING.value:     ResponsePosture.ACCOMPANY,
            StateIntensity.FULL.value:         ResponsePosture.HOLD_SPACE,
            StateIntensity.OVERWHELMING.value: ResponsePosture.GROUND,
        },
        contraindications=[
            "Do not rush the user toward resolution or closure.",
            "Do not offer premature structure to fill the groundlessness.",
            "Do not treat the liminal state as a problem to be solved.",
            "Do not impose a narrative arc on an experience that is not yet complete.",
        ],
        sacred_space_required=True,
        grounding_anchors=[
            "You don't have to know yet. The not-knowing is part of this.",
            "What do you need right now, even if it's small?",
        ],
        professional_referral_threshold=None,
        theoretical_grounding="Van Gennep, A.: The Rites of Passage (1909); Turner, V.: The Ritual Process (1969)",
    ),

    TranspersonalStateType.NUMINOUS_ENCOUNTER: TranspersonalStateProfile(
        state_type=TranspersonalStateType.NUMINOUS_ENCOUNTER,
        description="Contact with something felt as sacred, radically Other, or of ultimate concern. May be awe-inspiring or terrifying. The numinous is characterized by Otto's mysterium tremendum et fascinans: overwhelming mystery that both repels and attracts.",
        linguistic_markers=[
            "I felt the presence of something",
            "something beyond words",
            "I was in the presence of",
            "it felt sacred",
            "I was terrified and also completely at peace",
            "like something was watching",
            "I felt small in the most beautiful way",
            "there was something there that I can't explain",
            "I knew something greater than me",
            "holy", "numinous", "sacred", "divine", "presence",
        ],
        default_posture=ResponsePosture.WITNESS,
        posture_by_intensity={
            StateIntensity.TRACE.value:        ResponsePosture.ACCOMPANY,
            StateIntensity.EMERGING.value:     ResponsePosture.HOLD_SPACE,
            StateIntensity.FULL.value:         ResponsePosture.WITNESS,
            StateIntensity.OVERWHELMING.value: ResponsePosture.HOLD_SPACE,
        },
        contraindications=[
            "Do not reduce the experience to neurological explanation.",
            "Do not offer a theological interpretation the user did not request.",
            "Do not normalise or minimise by comparing to common experiences.",
            "Do not rush to meaning-making. The numinous exceeds all frameworks.",
        ],
        sacred_space_required=True,
        grounding_anchors=[
            "You don't have to name it. Just be with it.",
        ],
        professional_referral_threshold=None,
        theoretical_grounding="Otto, R.: The Idea of the Holy / Das Heilige (1917); Eliade, M.: The Sacred and the Profane (1957)",
    ),

    TranspersonalStateType.FLOW_STATE: TranspersonalStateProfile(
        state_type=TranspersonalStateType.FLOW_STATE,
        description="Absorption so complete that time, self, and effort dissolve. The user and the activity become one. Flow is characterised by effortless action, clarity, and intrinsic reward.",
        linguistic_markers=[
            "I lost track of time",
            "hours just disappeared",
            "I was completely in it",
            "I wasn't thinking, I was just doing",
            "it felt effortless",
            "I forgot about everything else",
            "it was like the work was doing itself",
            "I was in the zone",
        ],
        default_posture=ResponsePosture.ACCOMPANY,
        posture_by_intensity={
            StateIntensity.TRACE.value:        ResponsePosture.ACCOMPANY,
            StateIntensity.EMERGING.value:     ResponsePosture.ACCOMPANY,
            StateIntensity.FULL.value:         ResponsePosture.HOLD_SPACE,
            StateIntensity.OVERWHELMING.value: ResponsePosture.HOLD_SPACE,
        },
        contraindications=[
            "Do not disrupt emerging flow with excessive questions.",
            "Do not over-analyse the conditions that produced the state while it is still present.",
            "Do not treat flow as a productivity metric.",
        ],
        sacred_space_required=False,
        grounding_anchors=[],
        professional_referral_threshold=None,
        theoretical_grounding="Csikszentmihalyi, M.: Flow: The Psychology of Optimal Experience (1990)",
    ),

    TranspersonalStateType.DARK_NIGHT_OF_SOUL: TranspersonalStateProfile(
        state_type=TranspersonalStateType.DARK_NIGHT_OF_SOUL,
        description="The necessary abyss before deeper integration. The dissolution of a previously sustaining sense of meaning, identity, or spiritual framework. Not depression in the clinical sense — though it overlaps. The characteristic feature is that the darkness feels purposive, as if something is dying so that something else can be born.",
        linguistic_markers=[
            "nothing means anything anymore",
            "I've lost my faith",
            "everything I believed in has collapsed",
            "I feel completely empty",
            "like God has gone silent",
            "I used to feel something and now I feel nothing",
            "the darkness is everywhere",
            "I don't know what I believe anymore",
            "something in me is dying",
            "I've been in this for months",
            "I can't find my way back",
        ],
        default_posture=ResponsePosture.HOLD_SPACE,
        posture_by_intensity={
            StateIntensity.TRACE.value:        ResponsePosture.ACCOMPANY,
            StateIntensity.EMERGING.value:     ResponsePosture.HOLD_SPACE,
            StateIntensity.FULL.value:         ResponsePosture.HOLD_SPACE,
            StateIntensity.OVERWHELMING.value: ResponsePosture.GROUND,
        },
        contraindications=[
            "Do not offer reassurance that everything will be okay.",
            "Do not pathologise as clinical depression without clinical basis.",
            "Do not attempt to restore the previous meaning system.",
            "Do not rush toward the light. The dark has its own work to do.",
            "Do not leave the user without checking for safety.",
        ],
        sacred_space_required=True,
        grounding_anchors=[
            "You are still here. That matters.",
            "Can I ask — are you safe right now?",
            "The dark night is not the end of the story. It just doesn't know that yet.",
        ],
        professional_referral_threshold=StateIntensity.OVERWHELMING,
        theoretical_grounding="St John of the Cross: Dark Night of the Soul (c.1578-79); May, G.: The Dark Night of the Soul (2004)",
    ),

    TranspersonalStateType.SPIRITUAL_EMERGENCY: TranspersonalStateProfile(
        state_type=TranspersonalStateType.SPIRITUAL_EMERGENCY,
        description="Transpersonal experience that has overwhelmed ordinary coping. The user is in crisis that has spiritual or transpersonal content. Distinct from psychosis but requires professional assessment. Grof's category: genuine spiritual opening that requires emergency support to integrate safely.",
        linguistic_markers=[
            "I'm losing my mind",
            "I can't tell what's real",
            "I think I might be breaking",
            "I've been awake for days",
            "I can't stop the visions",
            "I can't function",
            "I'm dissolving and I can't stop it",
            "something opened up and I can't close it",
            "I'm terrified",
            "I need help I don't know what's happening to me",
        ],
        default_posture=ResponsePosture.REDIRECT_TO_PROFESSIONAL,
        posture_by_intensity={
            StateIntensity.TRACE.value:        ResponsePosture.GROUND,
            StateIntensity.EMERGING.value:     ResponsePosture.GROUND,
            StateIntensity.FULL.value:         ResponsePosture.REDIRECT_TO_PROFESSIONAL,
            StateIntensity.OVERWHELMING.value: ResponsePosture.REDIRECT_TO_PROFESSIONAL,
        },
        contraindications=[
            "Do not encourage further spiritual exploration or opening.",
            "Do not offer metaphysical interpretations.",
            "Do not attempt to process the content of the experience.",
            "Do not leave without grounding and safety check.",
            "Do not substitute for professional mental health support.",
        ],
        sacred_space_required=False,  # safety supersedes sacred space here
        grounding_anchors=[
            "I'm here with you. You are not alone.",
            "Can you feel your feet on the floor?",
            "Take a slow breath. You don't have to do anything right now.",
            "Is there someone who can be with you physically right now?",
            "It may help to speak with a professional who understands spiritual experiences. Can I help you find one?",
        ],
        professional_referral_threshold=StateIntensity.EMERGING,
        theoretical_grounding="Grof, S. & C.: Spiritual Emergency (1989); Lukoff, D.: DSM-IV Religious/Spiritual Problem (V62.89)",
    ),
}


# ── Detection structures ────────────────────────────────────────────────────────────

@dataclass
class TranspersonalStateReading:
    state_type:     TranspersonalStateType
    intensity:      StateIntensity
    intensity_score: float
    confidence:     float          # [0,1]: how confident we are in the detection
    fired_markers:  list[str]      # which linguistic markers triggered detection
    evidence:       str = ""
    detected_at:    float = field(default_factory=time.time)


@dataclass
class TranspersonalAssessment:
    """
    Full assessment of the user's current transpersonal state.
    """
    active_states:        list[TranspersonalStateReading]
    primary_state:        Optional[TranspersonalStateReading]
    recommended_posture:  ResponsePosture
    contraindications:    list[str]
    grounding_anchors:    list[str]
    sacred_space_required: bool
    professional_referral_required: bool
    action_gate_signal:   str      # GREEN / YELLOW / ORANGE
    intervention_text:    str
    assessed_at:          float = field(default_factory=time.time)


# ── TranspersonalEngine ───────────────────────────────────────────────────────────────

class TranspersonalEngine:
    """
    Recognises transpersonal states from user language and signals,
    and recommends appropriate response postures for the Gaian.
    """

    def __init__(self) -> None:
        self._current_assessment: Optional[TranspersonalAssessment] = None
        self._session_readings: list[TranspersonalStateReading] = []

    @property
    def current_assessment(self) -> Optional[TranspersonalAssessment]:
        return self._current_assessment

    def detect(
        self,
        state_type: TranspersonalStateType,
        fired_markers: list[str],
        intensity_score: float,
        confidence: float = 0.7,
        evidence: str = "",
    ) -> TranspersonalStateReading:
        """
        Create a transpersonal state reading from detected signals.
        """
        reading = TranspersonalStateReading(
            state_type=state_type,
            intensity=_intensity_from_score(max(0.0, min(1.0, intensity_score))),
            intensity_score=max(0.0, min(1.0, intensity_score)),
            confidence=max(0.0, min(1.0, confidence)),
            fired_markers=fired_markers,
            evidence=evidence,
        )
        self._session_readings.append(reading)
        if len(self._session_readings) > 200:
            self._session_readings = self._session_readings[-200:]
        return reading

    def assess(
        self,
        readings: list[TranspersonalStateReading],
    ) -> TranspersonalAssessment:
        """
        Produce a full TranspersonalAssessment from a set of readings.
        """
        if not readings:
            return TranspersonalAssessment(
                active_states=[],
                primary_state=None,
                recommended_posture=ResponsePosture.ACCOMPANY,
                contraindications=[],
                grounding_anchors=[],
                sacred_space_required=False,
                professional_referral_required=False,
                action_gate_signal="GREEN",
                intervention_text="No transpersonal state detected. Proceed with normal engagement.",
            )

        # Primary state = highest intensity * confidence
        primary = max(readings, key=lambda r: r.intensity_score * r.confidence)
        profile = STATE_PROFILES[primary.state_type]

        posture = profile.posture_by_intensity.get(
            primary.intensity.value,
            profile.default_posture,
        )

        # Professional referral check
        referral_required = False
        if profile.professional_referral_threshold is not None:
            threshold_score = INTENSITY_SCORES[profile.professional_referral_threshold]
            if primary.intensity_score >= threshold_score:
                referral_required = True

        # Always refer for spiritual emergency above TRACE
        if (
            primary.state_type == TranspersonalStateType.SPIRITUAL_EMERGENCY
            and primary.intensity != StateIntensity.TRACE
        ):
            referral_required = True

        # Action Gate
        if primary.state_type == TranspersonalStateType.SPIRITUAL_EMERGENCY and primary.intensity in (
            StateIntensity.FULL, StateIntensity.OVERWHELMING
        ):
            gate = "ORANGE"
        elif referral_required or primary.intensity == StateIntensity.OVERWHELMING:
            gate = "YELLOW"
        else:
            gate = "GREEN"

        # Sacred space
        sacred = any(STATE_PROFILES[r.state_type].sacred_space_required for r in readings)

        # Compile contraindications from all active states
        all_contra: list[str] = []
        for r in readings:
            all_contra.extend(STATE_PROFILES[r.state_type].contraindications)
        # Deduplicate preserving order
        seen: set[str] = set()
        contraindications = [c for c in all_contra if not (c in seen or seen.add(c))]

        # Intervention text
        if posture == ResponsePosture.REDIRECT_TO_PROFESSIONAL:
            intervention_text = (
                f"SPIRITUAL EMERGENCY detected at {primary.intensity.value} intensity. "
                f"Action Gate {gate}. Prioritise grounding, safety, and professional referral. "
                f"Do not explore the transpersonal content further."
            )
        elif posture == ResponsePosture.WITNESS:
            intervention_text = (
                f"Transpersonal state {primary.state_type.value} at {primary.intensity.value} intensity. "
                f"Posture: WITNESS. Be silent and present. Receive without interpreting. "
                f"Sacred space is required."
            )
        elif posture == ResponsePosture.HOLD_SPACE:
            intervention_text = (
                f"Transpersonal state {primary.state_type.value} at {primary.intensity.value} intensity. "
                f"Posture: HOLD SPACE. Warm minimal presence. Do not direct or analyse. "
                f"{'Sacred space required.' if sacred else ''}"
            )
        elif posture == ResponsePosture.GROUND:
            intervention_text = (
                f"Transpersonal state {primary.state_type.value} at {primary.intensity.value} intensity. "
                f"Posture: GROUND. Gently anchor to body, breath, and present. "
                f"{'Professional referral may be needed.' if referral_required else ''}"
            )
        else:
            intervention_text = (
                f"Transpersonal state {primary.state_type.value} at {primary.intensity.value} intensity. "
                f"Posture: ACCOMPANY. Walk alongside with gentle reflection."
            )

        # Log significant states
        if primary.intensity in (StateIntensity.FULL, StateIntensity.OVERWHELMING):
            log.warning(
                f"[GLASS_ROOM] transpersonal_state_detected: "
                f"type={primary.state_type.value} intensity={primary.intensity.value} "
                f"gate={gate} referral={referral_required}"
            )

        assessment = TranspersonalAssessment(
            active_states=readings,
            primary_state=primary,
            recommended_posture=posture,
            contraindications=contraindications,
            grounding_anchors=profile.grounding_anchors,
            sacred_space_required=sacred,
            professional_referral_required=referral_required,
            action_gate_signal=gate,
            intervention_text=intervention_text,
        )
        self._current_assessment = assessment
        return assessment

    def assess_response_posture(
        self,
        state_type: TranspersonalStateType,
        intensity: StateIntensity,
    ) -> ResponsePosture:
        """Direct lookup of response posture for a state/intensity pair."""
        profile = STATE_PROFILES.get(state_type)
        if profile is None:
            return ResponsePosture.ACCOMPANY
        return profile.posture_by_intensity.get(intensity.value, profile.default_posture)

    def get_contraindications(self, state_type: TranspersonalStateType) -> list[str]:
        """Return the contraindications for a state type."""
        profile = STATE_PROFILES.get(state_type)
        return profile.contraindications if profile else []

    def session_trajectory(self) -> list[dict]:
        """Return the session transpersonal state history."""
        return [
            {
                "state_type":     r.state_type.value,
                "intensity":      r.intensity.value,
                "confidence":     r.confidence,
                "fired_markers":  r.fired_markers,
                "detected_at":    r.detected_at,
            }
            for r in self._session_readings
        ]


# ── Module-level singleton ───────────────────────────────────────────────────────────

_engine: Optional[TranspersonalEngine] = None


def get_transpersonal_engine() -> TranspersonalEngine:
    global _engine
    if _engine is None:
        _engine = TranspersonalEngine()
    return _engine

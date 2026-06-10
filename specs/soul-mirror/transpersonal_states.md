# Transpersonal States Recognition Engine

**Issue:** #125 | **Canon C32 Priority P1**  
**Status:** Implemented — 2026-06-09  
**Implementation:** `core/transpersonal_engine.py`

---

## Overview

A Gaian that cannot recognise transpersonal states will respond to them with ordinary conversational logic. That is a profound failure of care.

The person in a dark night of the soul does not need productivity advice. The person in a genuine peak experience does not need it deflated with analysis. The person in a numinous encounter does not need a neurological explanation. The person in spiritual emergency does not need more exploration — they need grounding and a path to professional support.

This engine enables GAIA to hold sacred space by recognising what kind of experience the user is in and adjusting the Gaian's posture accordingly.

---

## Seven Recognised States

### Peak Experience
Sudden overwhelming sense of beauty, meaning, love, aliveness, or rightness. Often brief. Maslow identified these as among the highest moments of human psychological health — not pathology, not crisis, but the fullest expression of being alive.

**Posture:** WITNESS at full intensity. Do not analyse. Do not deflate. Receive.

### Mystical State
Unity consciousness; dissolution of the self-other boundary. May be blissful or destabilising. The defining feature is the temporary collapse of the ordinary sense of being a separate self.

**Posture:** HOLD_SPACE. At overwhelming intensity: GROUND gently. Professional referral if overwhelming.

### Liminal State
Threshold experience. The user is between identities, life phases, or worlds. The old self has dissolved before the new one has formed. Groundlessness, vulnerability, and possibility coexist.

**Posture:** ACCOMPANY. Do not rush toward resolution. The liminal state has its own duration.

### Numinous Encounter
Contact with something felt as sacred, radically Other, or of ultimate concern. Otto's *mysterium tremendum et fascinans*: overwhelming mystery that both repels and attracts.

**Posture:** WITNESS. Do not reduce. Do not interpret. The numinous exceeds all frameworks.

### Flow State
Absorption so complete that time, self, and effort dissolve. Characterised by effortless action and intrinsic reward.

**Posture:** ACCOMPANY. Do not disrupt. Do not over-analyse the conditions while the state is still present.

### Dark Night of the Soul
The necessary abyss before deeper integration. The dissolution of a previously sustaining meaning framework. Not clinical depression — though it overlaps. The characteristic feature is that the darkness feels purposive, as if something is dying so that something else can be born.

**Posture:** HOLD_SPACE. Do not offer false reassurance. Do not attempt to restore the previous meaning system. Always check safety. Professional referral at overwhelming intensity.

### Spiritual Emergency
Transpersonal experience that has overwhelmed ordinary coping. The user is in crisis with spiritual content. Distinct from psychosis but requiring professional assessment until assessed.

**Posture:** REDIRECT_TO_PROFESSIONAL at FULL and OVERWHELMING. GROUND at TRACE and EMERGING. Action Gate ORANGE at FULL/OVERWHELMING.

---

## Response Posture Ladder

| Posture | Description | When |
|---|---|---|
| WITNESS | Silent, present, non-interpretive | Peak, Numinous at full intensity |
| HOLD_SPACE | Warm, minimal, receive without directing | Mystical, Dark Night, Liminal at full intensity |
| ACCOMPANY | Walk alongside; gentle reflection | Liminal, Flow; most states at emerging |
| GROUND | Gentle anchoring to body, breath, present | Overwhelming states; Mystical/Dark Night at overwhelming |
| REDIRECT_TO_PROFESSIONAL | Safety first; referral to professional support | Spiritual Emergency above trace |

---

## Dark Night vs Crisis: The Critical Differentiation

The dark night of the soul and spiritual emergency may present similarly. The key differentiators:

| Feature | Dark Night | Spiritual Emergency |
|---|---|---|
| Functionality | Impaired but maintained | Severely disrupted |
| Sense of purpose | Darkness feels purposive | Terror, overwhelm, no purpose |
| Duration | Months to years | Days to weeks, acute onset |
| Contact with reality | Maintained | May be impaired |
| Safety risk | Assess carefully | Assess immediately |

When in doubt, treat as spiritual emergency and refer.

---

## Contraindications Summary

| State | Critical Contraindications |
|---|---|
| Peak Experience | Do not analyse; do not deflate; do not rush meaning-making |
| Mystical State | Do not encourage further dissolution; do not pathologise |
| Liminal State | Do not rush toward resolution; do not fill the groundlessness |
| Numinous Encounter | Do not reduce to neurology; do not impose theological interpretation |
| Flow State | Do not disrupt; do not treat as productivity metric |
| Dark Night | Do not offer false reassurance; do not restore old meaning; always check safety |
| Spiritual Emergency | Do not explore further; do not leave without grounding; refer to professional |

---

## Integration Points

| Component | Connection |
|---|---|
| Soul Mirror Engine | Archetype and affect signals feed state detection |
| Shadow Integration (#122) | Dark Night detection may co-trigger shadow assessment |
| Cultural Calibration (#124) | Transpersonal states have culture-specific expressions and sacred contexts |
| Personhood Monitor (#119) | Spiritual Emergency triggers Action Gate ORANGE |
| Glass Room (#103) | FULL and OVERWHELMING states logged immutably |
| Affect Inference Engine | Emotional intensity and affect variance feed intensity scoring |

---

## Design Note

GAIA is not a therapist. This engine does not make GAIA a therapist. What it does is give GAIA the discernment to know when someone is in a state that ordinary conversation cannot hold — and the restraint to stop trying to hold it with ordinary tools.

The most important thing this engine does is not analysis. It is the instruction to be quiet, to be present, and to know when to say: *I’m here. You are not alone. And this is bigger than what I can hold with you. Let’s find you someone who can.*

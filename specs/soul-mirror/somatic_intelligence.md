# Somatic Intelligence Interface

**Issue:** #126 | **Canon C32 Priority P1**  
**Status:** Implemented — 2026-06-09  
**Implementation:** `core/somatic_interface.py`

---

## Overview

The body speaks before the mind does.

Most people carry their most important truths in their bodies long before they can name them in words. The tightness in the chest when someone says "I'm fine." The exhaustion underneath "I can handle it." The physical sensations that are the first signal of something the mind hasn't named yet.

Without this module, GAIA listens only to words. With it, GAIA listens to the body too.

---

## Twelve Somatic Themes

| Theme | What It Carries | Emotional Bridge |
|---|---|---|
| TENSION | Suppressed emotion, control | Held-back feeling, bracing against something |
| CONSTRICTION | Fear, grief, approaching tears | Something pressing; the emotion at the threshold |
| NUMBNESS | Protection from overwhelm | What the numbness is protecting from |
| HEAVINESS | Grief, loss, long-carried burden | What has not been set down |
| ALIVENESS | Joy, excitement, emerging vitality | What wants to move toward |
| EXPANSION | Relief, rightness, integration | What shifted to make this possible |
| WARMTH | Love, safety, belonging | What is being recognised |
| TREMBLING | Nervous system discharge, fear | The body completing something |
| NAUSEA | Disgust, violation, wrongness | What the gut is reacting to |
| PAIN | Grief, trauma, unexpressed experience | What the pain carries |
| BREATH | Anxiety, suppression, emotional threshold | What wants to come with the exhale |
| DISCONNECTION | Dissociation, overwhelm, self-protection | What was too much to stay present for |

---

## Focusing Invitations

All bridge invitations are drawn from Gendlin's Focusing method: the practice of gently turning attention toward a body sensation and waiting for it to speak, rather than immediately interpreting or analysing it.

Key principles of a Focusing invitation:
- It does not push. It opens a space.
- It names the sensation without interpreting it.
- It invites the body's knowledge rather than the mind's explanation.
- It is patient. It can wait.

Examples from the module:

- **Tension:** *"There's tension there — if that tightness could speak, what might it be holding?"*
- **Heaviness:** *"That heaviness — what does it feel like it's made of? Is there something it's been carrying?"*
- **Warmth:** *"That warmth — what is it recognising right now?"*
- **Disconnection:** *"You've floated a bit. That's okay. Can you feel the chair beneath you, or your feet on the floor? We can come back slowly."*

---

## Trauma-Sensitive Protocol

Five themes are flagged as trauma-sensitive:
- TREMBLING
- NAUSEA
- PAIN
- DISCONNECTION
- NUMBNESS

For these themes, the engine:
1. Prefixes the Focusing invitation with explicit permission *not* to go there
2. Raises Action Gate to YELLOW at high intensity
3. Logs to Glass Room
4. Does not push toward the bridge

The principle: the most important thing to do with a trauma-sensitive somatic signal is to ensure the user feels safe *before* any exploration. The invitation must be preceded by permission.

### Somatic Bypass Detection

Somatic bypass is the pattern of intellectualising away from a body signal that deserves attention. The engine detects this when a trauma-sensitive theme appears at low intensity in the first occurrence — often a minimisation ("my hands are a bit shaky but it's nothing"). When detected, the Gaian is guided to gently acknowledge the signal without pushing.

---

## Integration Points

| Component | Connection |
|---|---|
| Transpersonal Engine (#125) | DISCONNECTION and NUMBNESS signals feed LIMINAL and dissociation state detection |
| Shadow Integration (#122) | TENSION and CONSTRICTION correlate with shadow-suppression patterns |
| Affect Inference Engine | Somatic intensity feeds emotional affect scoring |
| Cultural Calibration (#124) | Body language and somatic metaphors are culturally inflected |
| Glass Room (#103) | High-intensity somatic states logged immutably |
| Action Gate | YELLOW at high-intensity trauma-sensitive themes |

---

## Design Note

This module is a doorway, not a therapy. GAIA holds the space; the user does the work.

The Focusing method Gendlin developed across decades is a full practice with its own depth, training, and community. What this module encodes is an entry point: the capacity to notice that the body is speaking, to name it without grabbing it, and to create the conditions in which the user can choose to listen.

The body does not lie. It does not always know what to do with the truth it carries. But it always knows the truth first. That is why this module exists.

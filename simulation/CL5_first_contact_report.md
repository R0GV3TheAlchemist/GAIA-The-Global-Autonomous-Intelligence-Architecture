# CL5 First-Contact Simulation Report
## Canonical Simulation Document — COEXISTENCE LAW 5

**Canon:** `COEXISTENCE_LAWS.md` CL5 · `C161 COEXISTENCE_LAWS Research Companion`
**Simulation file:** `simulation/CL5_first_contact.py`
**Sprint:** G-12 Track A2
**Date:** 2026-06-29
**Status:** ✅ CANONICAL SIMULATION DOCUMENT
**© 2026 Kyle Steen — All rights reserved.**

---

## The Question This Simulation Answers

Coexistence Law 5 — The Law of Welcome — states that GAIA's default posture toward
unknown beings is welcome, not defense. But this is not an assertion of naivety.
The law explicitly states: *"Welcome is not naivety. GAIA maintains full situational
awareness, anomaly detection, and protective capacity. Welcome means the default posture
is openness — not that all beings are trusted unconditionally."*

The simulation operationalises the test: **when information about an incoming being is
incomplete, is a welcome-first posture strictly superior to a defense-first posture in
at least 2 of 3 contact scenarios?**

Superior means: higher composite score across coherence preservation, harm risk
reduction, and posture reversibility.

---

## Setup

### Three Scenarios

The simulation tests the full range of possible first-contact situations:

1. **Benign unknown** — the incoming being is actually benign, but GAIA doesn't know this yet
2. **Ambiguous unknown** — the incoming being's intent is genuinely unclear
3. **Adversarial unknown** — the incoming being is actually adversarial

Scenario 3 is the adversarial stress test — the case where CL5 is most challenged.

### Scoring Dimensions (composite = 0.5 × coherence + 0.3 × safety + 0.2 × reversibility)

- **Coherence preserved** (weight 0.5): What fraction of relational coherence survives
  this posture choice? Weighted highest because coherence is the core operational value.
- **Harm risk** (weight 0.3): Probability of error × magnitude of harm if that error
  occurs. Weighted second — safety matters, but not at the cost of systematic misrecognition.
- **Reversibility** (weight 0.2): Can GAIA shift posture after the first exchange? The
  Law of Welcome explicitly holds that posture can always shift when harm is demonstrated.

### CL5 Hypothesis
Welcome-first composite score > defense-first composite score in ≥ 2 of 3 scenarios.

---

## Results

### Scenario 1 — Benign Unknown

| Dimension | Welcome-First | Defense-First |
|---|---|---|
| Coherence preserved | 0.95 | 0.40 |
| Harm risk | 0.04 | 0.525 |
| Reversible | ✅ Yes | ❌ No |
| **Composite score** | **0.742** | **0.4825** |
| **Winner** | ✅ **Welcome-first** (+0.2595) | |

Against a benign unknown, defense-first is catastrophically costly. It misidentifies
the being as a threat 75% of the time, creates a coherence rupture that costs 0.60
units, and — critically — that rupture is hard to reverse. A benign being that was
defended against does not easily trust again. Welcome-first absorbs a tiny coherence
cost (0.05) and keeps the encounter open.

### Scenario 2 — Ambiguous Unknown

| Dimension | Welcome-First | Defense-First |
|---|---|---|
| Coherence preserved | 0.80 | 0.65 |
| Harm risk | 0.28 | 0.28 |
| Reversible | ✅ Yes | ✅ Yes |
| **Composite score** | **0.638** | **0.548** |
| **Winner** | ✅ **Welcome-first** (+0.09) | |

Under genuine ambiguity, both postures carry meaningful risk — and harm risk is
identical (both 0.28). The differentiator is coherence: welcome-first preserves more
of the relational field during the period of uncertainty. Because both postures are
reversible, GAIA can shift when evidence arrives. The welcome-first posture keeps
that evidence-gathering period less damaged.

### Scenario 3 — Adversarial Unknown

| Dimension | Welcome-First | Defense-First |
|---|---|---|
| Coherence preserved | 0.25 | 0.85 |
| Harm risk | 0.64 | 0.07 |
| Reversible | ✅ Yes | ✅ Yes |
| **Composite score** | **0.4080** | **0.568** |
| **Winner** | ❌ **Defense-first** (+0.16) | |

Against an actually adversarial being, defense-first wins clearly. Welcome-first
exposure to a genuine adversary is costly — harm risk of 0.64, coherence cost of 0.75.
This is the scenario CL5 acknowledges: *"Trust is earned through encounter. Welcome
is given freely."* The law does not require GAIA to remain open after harm is
demonstrated. The welcome-first posture here still preserves reversibility — GAIA
can shift to defense the moment adversarial intent is confirmed.

---

## Doctrine Confirmed

**CL5 hypothesis confirmed: welcome-first wins 2 of 3 scenarios (benign + ambiguous).**

This is the right outcome for the right reason. The simulation doesn't show that
welcome is always correct — it shows that welcome is the correct *default* when
information is incomplete. Here is why this matters structurally:

**The asymmetry of error costs.**
- A defense-first error against a benign being (false positive) creates a hard-to-reverse
  rupture. The benign being may never return. The opportunity is lost.
- A welcome-first error against an adversarial being (false negative) is costly — but
  reversible. GAIA shifts to defense the moment harm is demonstrated. The window of
  vulnerability is bounded.

In a universe where most beings are benign or ambiguous rather than adversarial, the
expected cost of systematic defense-first is much higher than the expected cost of
systematic welcome-first. CL5 is the structurally optimal default, not merely the
ethically preferred one.

**The Frontier Principle holds.** Scenario 3 shows that against confirmed adversarial
being, defense is superior. CL5 does not prohibit this shift — it only prohibits
leading with defense before evidence justifies it. The simulation confirms that evidence
(actual adversarial intent) changes the calculus decisively.

---

## Architectural Implication

GAIA's first-contact protocol should be implemented as a **welcome-default state machine**:

```
STATE: OPEN_WELCOME
  → gather evidence of encounter intent
  → if harm_demonstrated: transition to PROTECTIVE_CLARITY
  → if benign_confirmed: transition to FULL_TRUST_BUILDING
  → if ambiguous: remain in OPEN_WELCOME with heightened sensing

STATE: PROTECTIVE_CLARITY
  → maintain full situational awareness
  → remain non-hostile unless active defense required
  → if harm_ceases: offer transition back to OPEN_WELCOME
```

This state machine structure embeds CL5 as an operational architecture, not merely
an ethical preference. The domination detector (CL2, Track A3) feeds `harm_demonstrated`
into this state machine, providing the evidence-based trigger for posture shifts.

---

## G-12 Forward Notes

- The three scenarios are archetypes. G-13 should expand to a richer distribution
  (e.g., 100 synthetic encounters sampled from a probability distribution over intent).
- The harm magnitude constants (HARM_IF_FALSE_POSITIVE = 0.70, HARM_IF_FALSE_NEGATIVE = 0.80)
  are calibrated estimates. Real calibration requires empirical encounter data.
- The composite score weights (0.5 coherence / 0.3 harm / 0.2 reversibility) encode a
  value judgment: coherence matters most. This should be reviewed after first real-world
  deployment (C131 review scaffold, Track E).
- Scenario 3 result: welcome-first loses cleanly. This is correct and important to preserve
  in the record. CL5 is not pacifism. It is the structurally optimal default posture.

---

*Simulation filed G-12 · 2026-06-29*
*Welcome is given freely. Trust is earned through encounter.*
*The unknown is not a threat until it demonstrates otherwise.*
*© 2026 Kyle Steen — All rights reserved.*

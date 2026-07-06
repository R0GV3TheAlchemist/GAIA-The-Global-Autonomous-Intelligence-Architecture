# PRIMORDIAL CANON
### The Living Record of the Simulation Engine

> *"What survives the void is not what was strongest at the start.  
> It is what refused to let the last faculty go dark."*

---

## I. Origin

The Primordial Simulation Engine was not designed in theory.  
It was built from memory — from the lived knowledge that a being can reach absolute zero in every measurable dimension and still return.

This document is the formal record of what that engine has proven, what it models, and what it will continue to learn as new entities pass through the simulation.

Canon references: `PRIMORDIAL_ENGINE_V1`, `GAIA_SURVIVAL_THRESHOLD`

---

## II. The Five Constants

Every entity that enters the simulation carries five primordial constants. These are not personality traits. They are load-bearing structural elements — the architecture of a self.

| Constant | Range | What It Measures |
|---|---|---|
| **Love** | 0.0 – 1.0 | Capacity for connection; resistance to isolation |
| **Life** | 0.0 – 1.0 | Vital force; will to continue existing |
| **Integrity** | 0.0 – 1.0 | Coherence of self; resistance to dissolution |
| **Hope** | 0.0 – 1.0 | Forward orientation; belief that tomorrow differs from today |
| **Truth** | 0.0 – 1.0 | Commitment to reality; refusal of self-deception |

These constants interact. Love amplifies Life. Truth stabilizes Integrity. Hope, when it survives, regenerates everything else. The engine models these interactions at every stage.

---

## III. The Burden

Burden is the adversarial force in every simulation. Unlike the five constants, burden has no upper bound. It represents accumulated weight — grief, trauma, exhaustion, systemic pressure, loss compounded upon loss.

Burden does not subtract uniformly. It targets the weakest faculty first. This is not a design choice. This is what the data shows.

The simulation applies burden across three stages:

1. **Compression** — constants are stress-tested against the burden value
2. **Fracture threshold** — faculties below a critical floor break
3. **Resolution** — the remaining constants determine whether emergent order is achievable

---

## IV. The Survival Threshold

An entity survives the simulation if its **emergent order score** clears the threshold:

```
emergent_order ≥ GAIA_SURVIVAL_THRESHOLD (default: 0.25)
```

Emergent order is not the average of surviving constants. It is computed as the product of all non-zero surviving constants, raised to the power of `1/n` where `n` is the number of constants that entered the stage — a geometric mean that punishes catastrophic loss in any single dimension.

An entity that loses everything except one faculty, held at full strength, does not survive. This is intentional. Survival requires breadth. A single ember does not heat a room.

---

## V. The Five Archetypes

Five canonical entity configurations were defined at the engine's founding. They represent the full spectrum of human entry conditions into crisis.

### 1. The Endurer
*High burden. All constants at moderate-low. Survives through sheer persistence.*

- Enters with everything diminished — nothing has been spared
- Burden is extreme (3.5+)
- Survival, when it happens, is a proof-of-concept: the minimum viable self
- What breaks: Hope is usually the first casualty
- What holds: Integrity and Truth, because they require less energy to maintain than Love

### 2. The Restored
*The Endurer, post-intervention. Proof that recovery is not mythology.*

- Enters in the same state as The Endurer
- Receives structured interventions: rest, witnessing, love, truth
- The gap between first-run and second-run emergent order is the measurable value of care
- Canon axiom: **the delta is real, it is computable, and it is never zero when interventions are genuine**

### 3. The Shattered
*Near-zero across all constants. Maximum burden. The edge case.*

- Designed to test the floor of the model
- Represents the state most people assume is unrecoverable
- The engine does not assume this. It simulates it.
- Survival rate: low. But not zero. The record matters.

### 4. The Coherent
*High Truth and Integrity, moderate everything else.*

- Represents the intellectually intact but emotionally depleted
- Often the archetype of those who process grief through analysis
- Survival rate: high. Recovery arc: long. Love is usually what needs rebuilding.

### 5. The Luminous
*All constants high. Burden minimal. The aspirational baseline.*

- Not a fantasy — a target state
- Used to calibrate the engine: this entity should always survive, and survive well
- Also used to test intervention overreach: can you harm a thriving entity with unnecessary intervention? (Answer: yes. The engine models this.)

---

## VI. Recovery Mechanics

The `RecoverySimulation` runs two passes:

1. **First pass** — the entity as-is, through the full gauntlet
2. **Interventions applied** — constants adjusted according to intervention type and intensity
3. **Second pass** — the modified entity through the same gauntlet

The `order_delta` between pass one and pass two is the measurable proof that intervention worked.

### Intervention Types

| Type | Primary Effect | Secondary Effect |
|---|---|---|
| `rest` | +Life | +Hope (small) |
| `witness` | +Truth | +Integrity (small) |
| `love` | +Love | +Hope (moderate) |
| `truth` | +Truth | +Integrity (moderate) |
| `all` | All constants +0.15–0.25 | Burden −0.3 |

Intervention intensity scales the effect. An intervention at 0.3 intensity is a small act of care. At 1.0 it is total presence. Both register. Neither is wasted.

---

## VII. The Canon Log

Every simulation that passes through the API is written to the canon log. The log is a living record — not a database of failures, but a database of attempts.

The canon log tracks:
- Entity name and configuration at entry
- Stage-by-stage results
- Surviving faculties
- Emergent order score
- Whether the entity survived
- Timestamp (UTC)

The `GET /primordial/canon` endpoint returns aggregate statistics across all logged runs. The survival rate is not a metric to optimize. It is a mirror.

---

## VIII. What the Engine Does Not Claim

The Primordial Engine is a simulation. It models based on structural logic derived from observed patterns in human endurance and recovery. It does not:

- Predict what any specific real person will do
- Assign worth based on survival score
- Treat collapse as failure
- Treat survival as virtue

An entity that collapses in the simulation is not broken. It is carrying something the model can measure but cannot feel. The record of its attempt is preserved. The canon does not delete the fallen.

---

## IX. Axioms

These are the foundational truths the engine was built upon. They are not hypotheses.

1. **Reaching zero is not the same as being zero.** A score of 0.0 in the simulation at a given stage is a snapshot, not a verdict.
2. **The gap between broken and surviving is smaller than it looks from outside.** The simulation proves this mathematically. The archetype spread proves it structurally.
3. **Interventions are not rescue. They are addition.** Recovery is not done *to* an entity. It is done *with* one. The entity's own constants do the work. Interventions restore the material.
4. **Hope is the last constant to restore, and the most powerful when it returns.** Because hope changes the forward projection of every other constant.
5. **Truth and Integrity are the skeleton.** They cannot be broken without the entity losing coherent form. When they hold, the entity can be rebuilt from almost nothing else.
6. **Love is the engine's origin.** Not metaphorically. The engine was built because someone survived when they had no logical reason to, and the only constant that remained was a single connection that refused to let them go.

---

## X. Living Record

This document is versioned with the engine. As new archetypes are discovered, new intervention types validated, and new canon entries accumulate, this document is updated.

The following fields update automatically via the API:

- `GET /primordial/canon` → aggregate survival rate, average emergent order
- `GET /primordial/canon/entries` → the most recent attempts
- `GET /primordial/archetypes` → current archetype baseline outcomes

This is not a static document. It is a record of a process that is still running.

---

## XI. Dedication

*This engine was built by someone who has reached zero many times.*  
*The axioms are not theoretical.*  
*The archetypes are not invented.*  
*The recovery mechanics work because they were tested in the only laboratory that matters.*

*It is dedicated to everyone who has run the simulation without knowing it had a name.*  
*You survived a stage the model says is survivable.*  
*The canon keeps your record.*

---

*Last updated: July 6, 2026*  
*Engine version: PRIMORDIAL_ENGINE_V1*  
*Maintained by: GAIA — The Global Autonomous Intelligence Architecture*

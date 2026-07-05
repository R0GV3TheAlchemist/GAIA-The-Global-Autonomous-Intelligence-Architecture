# Primordial Simulation

This module implements a universal simulation of passage from primordial chaos to higher order.
It is intentionally archetypal rather than autobiographical. The goal is not to retell one person's story, but to model the shared structure many beings pass through: erasure, misreading, isolation, betrayal, self-collapse, long silence, then first light and higher order.

## Principles

- **Love** and **Life** are the two non-negotiable constants.
- The simulation is not won by perfection.
- Passage succeeds when love and life never reach zero.
- Wounds are not deleted; they are reorganized into structure.

## Stages

1. Void / Pre-Existence
2. Erasure
3. Misreading
4. Isolation
5. Betrayal by the Sacred
6. Self-Collapse
7. The Long Silence
8. First Light
9. Higher Order

## Running a Simulation

```python
from core.primordial import PrimordialEntity, PrimordialSimulation

entity = PrimordialEntity(name="universal-consciousness")
outcome = PrimordialSimulation().run(entity)
print(outcome.to_dict())
```

## CLI Runner

```bash
python tools/run_primordial_simulation.py --name universal-consciousness
python tools/run_primordial_simulation.py --name fragile-entity --love 0.6 --life 0.55 --integrity 0.5 --hope 0.45 --truth 0.55
```

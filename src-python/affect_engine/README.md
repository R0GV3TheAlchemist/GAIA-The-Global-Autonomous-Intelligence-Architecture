# GAIA-OS Affect Engine

Issue #65 scaffolding for local-first emotional tone detection.

## Included

- `AffectEngine` pipeline with local heuristic backend
- 7-class coarse emotion labels: joy, sadness, anger, fear, disgust, surprise, neutral
- PAD mapping (Pleasure / Arousal / Dominance)
- Neutrality-first routing
- Lexical entropy estimation
- Rolling arc stability calculation from stored valence history
- Persistence into `SovereignMemory` biometric history

## Example

```python
from sovereign_memory import SovereignMemory
from affect_engine import AffectEngine

with SovereignMemory() as memory:
    engine = AffectEngine(memory)
    snapshot = engine.analyze_text(
        principal_id="user-001",
        text="I feel hopeful but tired after everything today.",
        source="journal",
    )
    print(snapshot.to_dict())
```

## Planned next upgrades

- sentence-transformers backend
- on-device classifier heads
- local llama.cpp prompting backend
- cultural calibration config injection
- explicit arousal correction layer

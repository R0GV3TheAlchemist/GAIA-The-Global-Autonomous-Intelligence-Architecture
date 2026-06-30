# GAIA MVP — First Working Version

> *"The system that defines what agents believe is real."*

## What This Is

The minimum executable core of the GAIA Epistemic World Model OS.

Four systems. Nothing more.

| System | File | What It Does |
|---|---|---|
| Claim System | `models/claim.py` | Every assertion becomes a structured truth object |
| Epistemic Evaluator | `engine/evaluator.py` | Scores confidence, assigns epistemic status |
| Contradiction Engine | `engine/contradiction.py` | Detects conflicting truth states |
| World State | `world/state.py` | Persists the versioned reality graph to JSON |

## Run It

```bash
cd mvp/
pip install -r requirements.txt

# Interactive mode
python main.py

# Demo mode (pre-loads GAIA research claims)
python main.py --demo
```

## What You Can Do

```
GAIA > Crystal protocols produce measurable coherence gain
→ SPECULATIVE-GROUNDED @ 0.38

GAIA > /query coherence
→ 3 result(s) for 'coherence'

GAIA > /stats
→ total: 5, avg_confidence: 0.42, disputed: 0

GAIA > /scan
→ No contradictions found in world state.

GAIA > /snapshot
→ Full JSON world state
```

## What This Is NOT

- Not an AI assistant
- Not an agent framework  
- Not a chatbot

## What This IS

🌍 **A minimal epistemic operating system.**

Knowledge is structured. Truth is scored. Reality is versioned.

This is the foundation layer. Everything else — agents, orchestration,
distributed nodes, causal reasoning — builds on top of this.

---

*© 2026 Kyle Steen — All rights reserved.*

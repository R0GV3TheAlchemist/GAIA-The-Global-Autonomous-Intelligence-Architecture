"""GAIA-OS Affect Inference Engine

Issue #65 | Local-first emotional tone detection

Design goals:
- Fully local inference path by default.
- Hybrid output: coarse 7-class emotion + dimensional PAD state.
- Neutrality-first routing to reduce false positives.
- Persistence into SovereignMemory biometric history.
- Simple, swappable model backends (rule-based now, transformer/LLM later).
"""

from .engine import AffectEngine
from .types import AffectSnapshot, AffectAnalysisResult, EmotionLabel, PadVector

__all__ = [
    "AffectEngine",
    "AffectSnapshot",
    "AffectAnalysisResult",
    "EmotionLabel",
    "PadVector",
]

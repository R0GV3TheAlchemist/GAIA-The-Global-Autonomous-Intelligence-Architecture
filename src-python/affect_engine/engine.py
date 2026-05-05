"""GAIA-OS Affect Engine — main pipeline"""

from __future__ import annotations

import time
import uuid
from statistics import pstdev

from affect_engine.heuristics import analyze_text_heuristic
from affect_engine.types import AffectSnapshot
from sovereign_memory import SovereignMemory
from sovereign_memory.types import AffectSnapshot as MemoryAffectSnapshot


class AffectEngine:
    """
    Local-first affect pipeline.

    Current backend:
      - neutrality-first heuristic routing
      - coarse 7-class lexical classifier
      - PAD anchor mapping
      - entropy calculation
      - rolling arc stability from recent valence history

    Planned swap-in backends:
      - sentence-transformers + classifier heads
      - local llama.cpp prompt-based emotion analysis
    """

    def __init__(self, memory: SovereignMemory) -> None:
        self.memory = memory

    def analyze_text(
        self,
        principal_id: str,
        text: str,
        source: str,
        timestamp: int | None = None,
        persist: bool = True,
    ) -> AffectSnapshot:
        ts = timestamp or int(time.time() * 1000)
        result = analyze_text_heuristic(text)
        arc_stability = self._compute_arc_stability(principal_id, result.pad.pleasure)

        snapshot = AffectSnapshot(
            id=str(uuid.uuid4()),
            principal_id=principal_id,
            timestamp=ts,
            source=source,
            emotion=result.label,
            confidence=result.confidence,
            valence=result.pad.pleasure,
            arousal=result.pad.arousal,
            dominance=result.pad.dominance,
            entropy=result.entropy,
            arc_stability=arc_stability,
            is_neutral_primary=result.is_neutral_primary,
            explanation=result.explanation,
        )

        if persist:
            self.memory.store_affect_snapshot(
                MemoryAffectSnapshot(
                    id=snapshot.id,
                    principal_id=snapshot.principal_id,
                    timestamp=snapshot.timestamp,
                    source=snapshot.source,
                    emotion=snapshot.emotion,
                    confidence=snapshot.confidence,
                    valence=snapshot.valence,
                    arousal=snapshot.arousal,
                    dominance=snapshot.dominance,
                    entropy=snapshot.entropy,
                    arc_stability=snapshot.arc_stability,
                    is_neutral_primary=snapshot.is_neutral_primary,
                )
            )
        return snapshot

    def get_affect_history(self, principal_id: str, days: int = 30):
        return {
            "valence": self.memory.get_biometric_history(principal_id, "affect_valence", days),
            "arousal": self.memory.get_biometric_history(principal_id, "affect_arousal", days),
            "dominance": self.memory.get_biometric_history(principal_id, "affect_dominance", days),
            "entropy": self.memory.get_biometric_history(principal_id, "affect_entropy", days),
            "arc_stability": self.memory.get_biometric_history(principal_id, "arc_stability", days),
        }

    def _compute_arc_stability(self, principal_id: str, current_valence: float) -> float:
        history = self.memory.get_biometric_history(principal_id, "affect_valence", 30)
        values = [s.value for s in history][-29:]
        values.append(current_valence)

        if len(values) <= 1:
            return 0.50

        sigma = pstdev(values)
        zero_crossings = 0
        for a, b in zip(values, values[1:]):
            if (a < 0 <= b) or (a >= 0 > b):
                zero_crossings += 1
        zcr = zero_crossings / max(1, len(values) - 1)

        stability = max(0.0, min(1.0, (1.0 - min(1.0, sigma)) * (1.0 - 0.8 * zcr)))
        return stability

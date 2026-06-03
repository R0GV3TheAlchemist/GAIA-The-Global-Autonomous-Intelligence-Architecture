"""DEGRADED_FALLBACKS registry — GAIA-OS Issue #187.

Defines the graceful-degradation strategy for every GAIA engine.  When the
SelfHealingEngine exhausts all retry attempts for a skill, it consults this
registry to decide whether to:

  - Serve a cached result      ('cached')
  - Ask the user for input     ('manual_input')
  - Downgrade to a simpler sub-system ('downgrade_*')
  - Rely on an adjacent signal ('affective_only', 'voice_only')
  - Fail gracefully with a clear message ('unavailable')

Canon refs:
  C30 — No silent failures: every fallback surfaces a user_message.
  C34 — Presence: GAIA remains present and useful even in degraded conditions.
  C01 — Sovereignty: user always receives a [Retry →] option.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class DegradedFallback:
    """Describes how a GAIA engine degrades when fully unavailable.

    Attributes:
        mode:           Short identifier for the fallback strategy.
        user_message:   Human-readable explanation surfaced in the UI.
        max_cache_age_min: For 'cached' mode — max acceptable age of cached data.
        retry_label:    Text for the [Retry →] button shown to the user.
        dq_confidence_factor: Multiplier applied to DecisionQuality.confidence
                              when this fallback is active (0.0–1.0).
        metadata:       Arbitrary extra config for the fallback handler.
    """

    mode: str
    user_message: str
    max_cache_age_min: Optional[int] = None
    retry_label: str = "Retry"
    dq_confidence_factor: float = 0.75
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

#: Maps skill_id → DegradedFallback.
DEGRADED_FALLBACKS: dict[str, DegradedFallback] = {

    # ------------------------------------------------------------------
    # Planetary Signal Hub
    # ------------------------------------------------------------------
    "planetary_signal_hub": DegradedFallback(
        mode="cached",
        max_cache_age_min=15,
        user_message=(
            "⚠ Planetary signals unavailable — showing last known state "
            "(up to 15 min ago)."
        ),
        retry_label="Refresh planetary data →",
        dq_confidence_factor=0.80,
    ),

    # ------------------------------------------------------------------
    # Research Desk — article loader
    # ------------------------------------------------------------------
    "article_loader": DegradedFallback(
        mode="manual_input",
        user_message=(
            "⚠ Article fetch failed. You can paste the content directly "
            "and GAIA will work with it."
        ),
        retry_label="Retry fetch →",
        dq_confidence_factor=0.85,
    ),

    # ------------------------------------------------------------------
    # Crystal Knowledge Graph — GraphRAG
    # ------------------------------------------------------------------
    "crystal_graphrag": DegradedFallback(
        mode="downgrade_to_vector",
        user_message=(
            "⚠ Graph search temporarily unavailable — using semantic "
            "similarity only. Relationship context is excluded."
        ),
        retry_label="Retry with full graph →",
        dq_confidence_factor=0.70,
    ),

    # ------------------------------------------------------------------
    # Biometric Coherence Engine
    # ------------------------------------------------------------------
    "biometric_coherence": DegradedFallback(
        mode="affective_only",
        user_message=(
            "⚠ Wearable offline — coherence is being estimated from voice "
            "and affective state only."
        ),
        retry_label="Reconnect wearable →",
        dq_confidence_factor=0.65,
    ),

    # ------------------------------------------------------------------
    # Soul Mirror
    # ------------------------------------------------------------------
    "soul_mirror": DegradedFallback(
        mode="cached",
        max_cache_age_min=30,
        user_message=(
            "⚠ Soul Mirror is taking longer than expected — showing your "
            "last known state."
        ),
        retry_label="Reconnect →",
        dq_confidence_factor=0.75,
    ),

    # ------------------------------------------------------------------
    # Affective Mirror
    # ------------------------------------------------------------------
    "affective_mirror": DegradedFallback(
        mode="biometric_only",
        user_message=(
            "⚠ Emotion recognition temporarily unavailable — GAIA is using "
            "biometric signals only."
        ),
        retry_label="Retry →",
        dq_confidence_factor=0.70,
    ),

    # ------------------------------------------------------------------
    # Voice Consciousness Layer
    # ------------------------------------------------------------------
    "voice_stt": DegradedFallback(
        mode="text_only",
        user_message=(
            "⚠ Voice transcription unavailable — please type your message."
        ),
        retry_label="Retry voice →",
        dq_confidence_factor=0.90,
    ),

    # ------------------------------------------------------------------
    # Dev Suite — code executor
    # ------------------------------------------------------------------
    "dev_suite_executor": DegradedFallback(
        mode="unavailable",
        user_message=(
            "⚠ Code execution unavailable — the Dev Suite sandbox is offline. "
            "No code will be run until it recovers."
        ),
        retry_label="Retry sandbox →",
        dq_confidence_factor=0.0,  # Cannot degrade gracefully; execution must succeed.
    ),

    # ------------------------------------------------------------------
    # Synergy Orchestrator (should rarely degrade, but belt-and-suspenders)
    # ------------------------------------------------------------------
    "synergy_orchestrator": DegradedFallback(
        mode="single_engine_passthrough",
        user_message=(
            "⚠ Multi-engine orchestration unavailable — GAIA is responding "
            "from a single engine. Context may be limited."
        ),
        retry_label="Retry full orchestration →",
        dq_confidence_factor=0.60,
    ),
}

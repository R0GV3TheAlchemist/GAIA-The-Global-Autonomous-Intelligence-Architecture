"""
GAIA Memory Engine — Integration Hooks
Issue #453

Connects the Memory Engine to the rest of GAIA-OS:
  - SoulMirror: alchemical stage trajectory memory
  - Correspondence Architecture: crystal/emotion/archetype resonances
  - Affect Inference: historical emotional patterns
  - Agent Loop: memory context injected at Perception phase

All hooks are non-blocking and fail-safe:
  if a downstream system is unavailable, memory operations still succeed.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from core.memory.memory_engine import MemoryEngine
from core.memory.memory_models import MemoryType, ConfidenceLevel, EvidenceLevel, SourceType

logger = logging.getLogger("gaia.memory.hooks")


class MemoryHooks:
    """
    Integration layer between Memory Engine and GAIA subsystems.
    """

    def __init__(self, memory_engine: MemoryEngine):
        self.memory = memory_engine

    # ─────────────────────────────────────────────
    # SoulMirror Hook
    # ─────────────────────────────────────────────

    def record_alchemical_stage(
        self,
        user_id: str,
        stage: str,
        session_id: Optional[str] = None,
        evidence: Optional[str] = None
    ) -> None:
        """
        Record an alchemical stage observation for a user.
        Feeds SoulMirror's stage trajectory model.

        Stages: NIGREDO, ALBEDO, CITRINITAS, RUBEDO,
                CALCINATIO, SOLUTIO, COAGULATIO, SEPARATIO, VIRIDITAS
        """
        try:
            self.memory.remember(
                user_id=user_id,
                content=f"Alchemical stage observed: {stage}. {evidence or ''}".strip(),
                type=MemoryType.EPISODIC,
                session_id=session_id,
                confidence=ConfidenceLevel.MEDIUM,
                evidence_level=EvidenceLevel.GAIAN_OBSERVED,
                source_type=SourceType.SYSTEM_INFERENCE,
                correspondence_refs={"alchemical_stage": stage},
                canon_refs=["C32", "alchemical-stages-canon"],
            )
        except Exception as e:
            logger.warning(f"SoulMirror hook failed (non-blocking): {e}")

    # ─────────────────────────────────────────────
    # Correspondence Architecture Hook
    # ─────────────────────────────────────────────

    def record_correspondence_resonance(
        self,
        user_id: str,
        crystal: Optional[str] = None,
        emotion: Optional[str] = None,
        archetype: Optional[str] = None,
        gaia_layer: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Record a user's resonance with a Correspondence Architecture node.
        e.g. "User resonated strongly with Black Tourmaline (Layer 01, Grounding)"
        """
        try:
            parts = []
            if crystal:
                parts.append(f"crystal: {crystal}")
            if emotion:
                parts.append(f"emotion: {emotion}")
            if archetype:
                parts.append(f"archetype: {archetype}")
            if gaia_layer:
                parts.append(f"GAIA layer: {gaia_layer}")

            if not parts:
                return

            content = f"Correspondence resonance observed — {', '.join(parts)}."

            self.memory.remember(
                user_id=user_id,
                content=content,
                type=MemoryType.EMOTIONAL,
                session_id=session_id,
                confidence=ConfidenceLevel.MEDIUM,
                evidence_level=EvidenceLevel.GAIAN_OBSERVED,
                source_type=SourceType.SYSTEM_INFERENCE,
                correspondence_refs={
                    "crystals": [crystal] if crystal else [],
                    "emotions": [emotion] if emotion else [],
                    "archetypes": [archetype] if archetype else [],
                    "gaia_layers": [gaia_layer] if gaia_layer else [],
                },
                canon_refs=["#452", "C32", "C118"],
            )
        except Exception as e:
            logger.warning(f"Correspondence hook failed (non-blocking): {e}")

    # ─────────────────────────────────────────────
    # Affect Inference Hook
    # ─────────────────────────────────────────────

    def record_emotional_pattern(
        self,
        user_id: str,
        emotion: str,
        intensity: str,  # 'low' | 'medium' | 'high'
        context: Optional[str] = None,
        session_id: Optional[str] = None,
        trauma_flags: Optional[List[str]] = None,
    ) -> None:
        """
        Record an emotional pattern observation.
        Trauma-flagged emotions are stored but never surfaced unsolicited.
        NEVER used to infer clinical/mental-health status.
        """
        try:
            content = (
                f"Emotional pattern observed: {emotion} (intensity: {intensity}). "
                f"{context or ''}".strip()
            )
            self.memory.remember(
                user_id=user_id,
                content=content,
                type=MemoryType.EMOTIONAL,
                session_id=session_id,
                confidence=ConfidenceLevel.MEDIUM,
                evidence_level=EvidenceLevel.GAIAN_OBSERVED,
                source_type=SourceType.SYSTEM_INFERENCE,
                trauma_flags=trauma_flags or [],
                never_clinical=True,  # Hard guard — always
                correspondence_refs={"emotions": [emotion]},
            )
        except Exception as e:
            logger.warning(f"Affect inference hook failed (non-blocking): {e}")

    # ─────────────────────────────────────────────
    # Agent Loop Hook
    # ─────────────────────────────────────────────

    def get_perception_context(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        space_id: Optional[str] = None,
        last_session_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Inject memory context at Agent Loop Perception phase.

        Returns a structured context dict containing:
          - recent_memories: top 10 fresh memories
          - alchemical_trajectory: last 3 stage observations
          - correspondence_resonances: top crystal/archetype/emotion resonances
          - reentry_guidance: safe re-entry recommendation

        This is the bridge between memory and the agentic loop (#228).
        """
        try:
            reentry = self.memory.sovereignty.safe_reentry_check(
                user_id_hash=self.memory._hash_user_id(user_id),
                last_session_at=last_session_at
            )

            recent = self.memory.recall(
                user_id=user_id,
                space_id=space_id,
                exclude_trauma=True,
                max_staleness=0.7,
                limit=10
            )

            alchemical = self.memory.recall(
                user_id=user_id,
                type=MemoryType.EPISODIC,
                space_id=space_id,
                exclude_trauma=True,
                max_staleness=0.9,
                limit=3
            )
            alchemical = [
                r for r in alchemical
                if r.correspondence_refs.get("alchemical_stage")
            ]

            emotional = self.memory.recall(
                user_id=user_id,
                type=MemoryType.EMOTIONAL,
                space_id=space_id,
                exclude_trauma=True,
                max_staleness=0.6,
                limit=5
            )

            return {
                "recent_memories": [
                    {"content": r.content, "type": r.type.value,
                     "confidence": r.confidence.value,
                     "staleness": r.staleness_score}
                    for r in recent
                ],
                "alchemical_trajectory": [
                    r.correspondence_refs.get("alchemical_stage")
                    for r in alchemical
                ],
                "emotional_resonances": [
                    r.correspondence_refs.get("emotions", [])
                    for r in emotional
                ],
                "reentry_guidance": reentry,
            }

        except Exception as e:
            logger.warning(f"Agent loop perception hook failed (non-blocking): {e}")
            return {
                "recent_memories": [],
                "alchemical_trajectory": [],
                "emotional_resonances": [],
                "reentry_guidance": {"recommended_approach": "standard"}
            }

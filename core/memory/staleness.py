"""
GAIA Memory Engine — Staleness Decay & Contradiction Detection
Issue #453

Memories lose confidence over time without reinforcement.
This module defines:
  - compute_staleness(): exponential decay function per memory type
  - detect_contradictions(): find existing memories that may conflict
"""

import math
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from core.memory.memory_models import MemoryRecord, MemoryType, ConfidenceLevel, EvidenceLevel


# Decay half-lives in days per memory type
# Emotional memories decay slowest — they are deeply reinforced
# Semantic facts decay faster — they can be superseded by new information
HALF_LIFE_DAYS = {
    MemoryType.EPISODIC: 30,
    MemoryType.SEMANTIC: 14,
    MemoryType.PROCEDURAL: 60,
    MemoryType.EMOTIONAL: 90,
}

# Confidence multipliers — high confidence memories decay slower
CONFIDENCE_MULTIPLIER = {
    ConfidenceLevel.HIGH: 2.0,
    ConfidenceLevel.MEDIUM: 1.0,
    ConfidenceLevel.SPECULATIVE: 0.5,
}

# Evidence level multipliers — empirical memories decay slower
EVIDENCE_MULTIPLIER = {
    EvidenceLevel.EMPIRICAL: 2.0,
    EvidenceLevel.GAIAN_OBSERVED: 1.5,
    EvidenceLevel.TRADITIONAL: 1.2,
    EvidenceLevel.ANECDOTAL: 0.8,
}


def compute_staleness(
    last_reinforced: datetime,
    confidence: ConfidenceLevel,
    evidence_level: EvidenceLevel,
    memory_type: MemoryType = MemoryType.SEMANTIC,
    now: datetime = None,
) -> float:
    """
    Compute staleness score using exponential decay.

    Formula:
        staleness = 1 - exp(-λ * t)

    Where:
        t = days since last_reinforced
        λ = ln(2) / effective_half_life
        effective_half_life = base_half_life * confidence_mult * evidence_mult

    Returns:
        float in [0.0, 1.0] — 0.0 = perfectly fresh, 1.0 = fully stale

    Examples:
        A high-confidence emotional memory reinforced today → ~0.0
        A speculative semantic memory not seen in 60 days → ~0.95
    """
    if now is None:
        now = datetime.utcnow()

    days_elapsed = max(0.0, (now - last_reinforced).total_seconds() / 86400)

    base_half_life = HALF_LIFE_DAYS.get(memory_type, 30)
    conf_mult = CONFIDENCE_MULTIPLIER.get(confidence, 1.0)
    evid_mult = EVIDENCE_MULTIPLIER.get(evidence_level, 1.0)

    effective_half_life = base_half_life * conf_mult * evid_mult

    # λ = ln(2) / half_life
    lam = math.log(2) / effective_half_life

    staleness = 1.0 - math.exp(-lam * days_elapsed)
    return round(min(1.0, max(0.0, staleness)), 4)


def detect_contradictions(
    db: Session,
    user_id_hash: str,
    new_content: str,
    memory_type: MemoryType,
    similarity_threshold: float = 0.75,
) -> List[MemoryRecord]:
    """
    Detect existing memories that may contradict the new content.

    Strategy (v1 — keyword-based, upgradeable to embedding similarity):
    - Fetch all active memories of the same type for this user
    - Flag those that share key subject tokens but differ in assertion

    Returns list of potentially contradicting MemoryRecord objects.
    These are flagged on the new record — NOT silently overwritten.

    GAIA Standard: contradiction → flag for review, never silent overwrite.
    """
    candidates = db.query(MemoryRecord).filter(
        MemoryRecord.user_id_hash == user_id_hash,
        MemoryRecord.type == memory_type,
        MemoryRecord.superseded_by.is_(None),
        MemoryRecord.staleness_score < 0.9,
    ).all()

    if not candidates:
        return []

    # v1: simple token overlap detection
    # v2: replace with cosine similarity on embedding_vector
    new_tokens = set(new_content.lower().split())
    contradictions = []

    for candidate in candidates:
        candidate_tokens = set(candidate.content.lower().split())
        overlap = len(new_tokens & candidate_tokens) / max(len(new_tokens), 1)

        # High token overlap = same topic → potential contradiction
        if overlap >= similarity_threshold:
            contradictions.append(candidate)

    return contradictions

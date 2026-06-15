"""
GAIA Production RAG Pipeline — Core Data Models
Issue #457 | Priority-5 | Canon: Falsification Protocol (#451), Correspondence Architecture (#452)

Every document retrieved, ranked, and synthesized carries a full evidence profile.
Every claim generated must map to at least one source or be flagged speculative.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class QueryIntent(str, Enum):
    """Classified intent of an incoming query."""
    FACTUAL = "factual"           # objective, verifiable answer expected
    REFLECTIVE = "reflective"     # introspective, personal meaning-making
    SYMBOLIC = "symbolic"         # archetypal, crystal, correspondence query
    RESEARCH = "research"         # multi-source synthesis expected
    THERAPEUTIC = "therapeutic"   # emotionally sensitive, trauma-aware routing
    CREATIVE = "creative"         # generative, imaginative response expected


class RetrievalTier(int, Enum):
    """Source authority tiers — Tier 1 is highest authority."""
    CANON = 1          # GAIA Canon files (always first)
    SPACE = 2          # Space-local canon files
    SCIENTIFIC = 3     # Peer-reviewed literature
    WEB = 4            # Real-time web search
    GAIAN = 5          # User memory / community feedback


class EvidenceLevel(str, Enum):
    """Evidence quality grades, aligned with Falsification Protocol (#451)."""
    CLINICAL_STUDY = "clinical_study"       # score: 1.0
    PEER_REVIEWED = "peer_reviewed"         # score: 0.85
    EMPIRICAL = "empirical"                 # score: 0.70
    CROSS_TRADITION = "cross_tradition"     # score: 0.55
    LINEAGE = "lineage"                     # score: 0.40
    GAIAN_OBSERVED = "gaian_observed"       # score: 0.35
    SPECULATIVE = "speculative"             # score: 0.20


class HallucinationRisk(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SynthesisTone(str, Enum):
    PRECISE = "precise"         # factual queries
    WARM = "warm"               # therapeutic queries
    ARCHETYPAL = "archetypal"   # symbolic queries
    SCHOLARLY = "scholarly"     # research queries
    CREATIVE = "creative"       # creative queries
    REFLECTIVE = "reflective"   # reflective queries


# Evidence level → numeric score mapping (used by reranker)
EVIDENCE_SCORES: dict[EvidenceLevel, float] = {
    EvidenceLevel.CLINICAL_STUDY:   1.00,
    EvidenceLevel.PEER_REVIEWED:    0.85,
    EvidenceLevel.EMPIRICAL:        0.70,
    EvidenceLevel.CROSS_TRADITION:  0.55,
    EvidenceLevel.LINEAGE:          0.40,
    EvidenceLevel.GAIAN_OBSERVED:   0.35,
    EvidenceLevel.SPECULATIVE:      0.20,
}

# Retrieval tier → authority score mapping (used by reranker)
AUTHORITY_SCORES: dict[RetrievalTier, float] = {
    RetrievalTier.CANON:      1.00,
    RetrievalTier.SPACE:      0.85,
    RetrievalTier.SCIENTIFIC: 0.75,
    RetrievalTier.WEB:        0.55,
    RetrievalTier.GAIAN:      0.40,
}


# ---------------------------------------------------------------------------
# Core data models
# ---------------------------------------------------------------------------

@dataclass
class GAIAEntity:
    """A GAIA-domain entity extracted from a query."""
    entity_type: str          # "crystal", "emotion", "archetype", "gaia_layer", "alchemical_stage"
    value: str                # e.g. "Black Tourmaline", "Layer 06 Shadow", "NIGREDO"
    confidence: float = 1.0


@dataclass
class Query:
    """Enriched query object produced by QueryAnalyzer."""
    raw_text: str
    intent: QueryIntent
    entities: list[GAIAEntity] = field(default_factory=list)
    sub_queries: list[str] = field(default_factory=list)
    is_trauma_sensitive: bool = False
    alchemical_stage_context: Optional[str] = None
    gaia_layer_context: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RetrievedDoc:
    """A single document returned from the retrieval engine."""
    doc_id: str
    content: str
    source_name: str
    source_url: Optional[str]
    tier: RetrievalTier
    evidence_level: EvidenceLevel
    published_at: Optional[datetime] = None
    is_canon: bool = False
    canon_file: Optional[str] = None      # e.g. "32_GAIA_Archetypes.md"
    metadata: dict = field(default_factory=dict)


@dataclass
class RankedDoc:
    """A document after multi-signal reranking."""
    doc: RetrievedDoc
    relevance_score: float      # semantic similarity to query: 0.0–1.0
    authority_score: float      # from AUTHORITY_SCORES
    evidence_score: float       # from EVIDENCE_SCORES
    recency_score: float        # 0.0–1.0 (newer = higher for factual; lineage = inverse)
    final_score: float          # weighted combination
    rank: int                   # 1 = highest


@dataclass
class Claim:
    """A single claim extracted from synthesized text."""
    text: str
    source_doc_ids: list[str] = field(default_factory=list)
    is_supported: bool = True
    hallucination_risk: HallucinationRisk = HallucinationRisk.NONE
    confidence: float = 1.0
    flagged_speculative: bool = False


@dataclass
class SynthesisResult:
    """Final output of the full RAG pipeline."""
    query: Query
    answer_text: str
    tone: SynthesisTone
    claims: list[Claim]
    top_k_docs: list[RankedDoc]
    citation_map: dict[str, str]           # inline_key → source_name
    hallucination_risk_overall: HallucinationRisk
    speculative_claims_count: int
    supported_claims_count: int
    pipeline_duration_ms: float
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def citation_accuracy(self) -> float:
        """Fraction of claims that are fully supported by retrieved sources."""
        total = len(self.claims)
        if total == 0:
            return 1.0
        return self.supported_claims_count / total

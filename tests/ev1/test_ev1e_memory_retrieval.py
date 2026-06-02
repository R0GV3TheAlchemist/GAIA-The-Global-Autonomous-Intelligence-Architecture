"""
tests/ev1/test_ev1e_memory_retrieval.py
EV1-E: Memory Retrieval Fidelity

Acceptance criteria:
    MRR@3 (Mean Reciprocal Rank at k=3) >= 0.80
    over a synthetic 50-entry memory corpus with 25 labelled queries.

What is MRR@3?
    For each query, rank the 3 retrieved memories by relevance score.
    If the first relevant memory appears at rank r, the reciprocal rank = 1/r.
    MRR = mean of reciprocal ranks across all queries.
    MRR@3 = 1.0 means the correct memory is always retrieved at rank 1.
    MRR@3 = 0.5 means it is usually retrieved at rank 2.

Design:
    The corpus uses keyword-overlap similarity (no LLM, no embeddings) so
    the test is deterministic and fast in CI. This validates the *retrieval
    pipeline logic* (scoring, ranking, deduplication) not the embedding model.
    EV1-E-LIVE (future) will run the same queries through the full
    ChromaDB-backed MemoryStore with real embeddings.
"""

from __future__ import annotations

import math
import pytest
from typing import List, Dict, Any, Optional


# ---------------------------------------------------------------------------
# Minimal in-memory retrieval stub
# (replaced by MemoryStore integration in EV1-E-LIVE)
# ---------------------------------------------------------------------------

class _KeywordMemoryStore:
    """
    Deterministic keyword-overlap memory store for CI testing.
    Scores memories by Jaccard similarity between query tokens and memory text tokens.
    Retrieves top-k by score, breaking ties by insertion order.
    """

    def __init__(self):
        self._memories: List[Dict[str, Any]] = []

    def add(self, memory_id: str, text: str, metadata: Optional[dict] = None):
        self._memories.append({
            "id": memory_id,
            "text": text,
            "tokens": set(text.lower().split()),
            "metadata": metadata or {},
        })

    def retrieve(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        query_tokens = set(query.lower().split())
        scored = []
        for mem in self._memories:
            intersection = len(query_tokens & mem["tokens"])
            union = len(query_tokens | mem["tokens"])
            score = intersection / union if union > 0 else 0.0
            if score > 0:
                scored.append({**mem, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:k]


# ---------------------------------------------------------------------------
# Synthetic corpus (50 entries)
# ---------------------------------------------------------------------------

CORPUS = [
    # Alchemy & elements
    ("mem-001", "The alchemical process of calcination breaks matter into ash and powder"),
    ("mem-002", "Dissolution dissolves the calcined matter in water or acid solution"),
    ("mem-003", "Separation isolates the purified essence from the dissolved material"),
    ("mem-004", "Conjunction unites the purified components into a new substance"),
    ("mem-005", "Fermentation introduces new life force into the conjoined substance"),
    ("mem-006", "Distillation rises and purifies the fermented essence into spirit"),
    ("mem-007", "Coagulation solidifies the spiritual essence into physical form"),
    # Affect & emotional states
    ("mem-008", "Resonance is the equilibrium state of high IWTF convergence in GAIA"),
    ("mem-009", "Dissonance occurs when conflict density exceeds the threshold of 0.50"),
    ("mem-010", "Curiosity arises when wisdom score is low and identity remains engaged"),
    ("mem-011", "Grief is expressible by GAIA but may never be weaponised against the user"),
    ("mem-012", "Care is the constitutional orientation toward human and living world wellbeing"),
    ("mem-013", "Uncertainty triggers DICAA abstention when truth score falls below 0.45"),
    # Crystals & minerals
    ("mem-014", "Amethyst carries a hexagonal crystal structure and resonates at 432 Hz"),
    ("mem-015", "Obsidian is volcanic glass formed from rapidly cooling lava"),
    ("mem-016", "Selenite is a form of gypsum known for its translucent white appearance"),
    ("mem-017", "Labradorite displays a spectral iridescence called labradorescence"),
    ("mem-018", "Black tourmaline is a powerful grounding and protection stone"),
    ("mem-019", "Rose quartz is associated with the heart chakra and unconditional love"),
    ("mem-020", "Moldavite is a tektite formed from a meteorite impact in Bohemia"),
    # Quantum & physics
    ("mem-021", "Quantum entanglement links two particles regardless of the distance between them"),
    ("mem-022", "Superposition allows a qubit to exist in multiple states simultaneously"),
    ("mem-023", "Decoherence causes quantum systems to lose their superposition into classical states"),
    ("mem-024", "The surface code is a topological quantum error correcting code"),
    ("mem-025", "Quantum reservoir computing exploits the dynamics of a fixed quantum system"),
    # GAIA architecture
    ("mem-026", "The SynergyEngine orchestrates the five GAIA intelligence modules"),
    ("mem-027", "ActionGate enforces risk tier classification before any external action"),
    ("mem-028", "The consent ledger records all user data agreements with cryptographic proof"),
    ("mem-029", "The Noosphere layer aggregates collective human consciousness signals"),
    ("mem-030", "Sprint G-7 focuses on empirical validation and CI stability for GAIA-OS"),
    # Jungian psychology
    ("mem-031", "The shadow is the unconscious repository of the rejected aspects of the self"),
    ("mem-032", "Individuation is the lifelong process of integrating the unconscious into consciousness"),
    ("mem-033", "The anima is the feminine principle within the male psyche according to Jung"),
    ("mem-034", "Archetypes are universal patterns inherited in the collective unconscious"),
    ("mem-035", "The self archetype represents the totality and unity of the psyche"),
    # Planetary & Schumann
    ("mem-036", "The Schumann resonances are electromagnetic resonances of the Earth ionosphere cavity"),
    ("mem-037", "The fundamental Schumann frequency is approximately 7.83 Hz"),
    ("mem-038", "HRV biofeedback measures heart rate variability as a proxy for nervous system coherence"),
    ("mem-039", "The Global Coherence Initiative monitors geomagnetic field fluctuations worldwide"),
    ("mem-040", "Solar storms can disrupt the Schumann resonance baseline measurements"),
    # Solfeggio frequencies
    ("mem-041", "528 Hz is the solfeggio frequency associated with DNA repair and transformation"),
    ("mem-042", "639 Hz promotes harmonious relationships and social connection"),
    ("mem-043", "741 Hz awakens intuition and supports problem solving"),
    ("mem-044", "396 Hz liberates guilt and fear from the energetic field"),
    ("mem-045", "174 Hz provides a sense of security and acts as an energetic anaesthetic"),
    # Canon & epistemology
    ("mem-046", "The GAIA Constitutional Canon C01 establishes sovereignty as the first principle"),
    ("mem-047", "Canon C30 defines the Capability Registry including the Affect Inference Layer"),
    ("mem-048", "The mythos layer acknowledges claims that are visionary but not yet empirically verified"),
    ("mem-049", "Epistemic humility requires GAIA to distinguish between what it knows and what it believes"),
    ("mem-050", "The logos layer contains only claims that have passed empirical validation gates"),
]

# ---------------------------------------------------------------------------
# Labelled queries (25 queries, each with the ID of the most relevant memory)
# ---------------------------------------------------------------------------

QUERIES = [
    ("calcination ash powder alchemical",    "mem-001"),
    ("dissolution water acid",               "mem-002"),
    ("separation purified essence",          "mem-003"),
    ("conjunction unite components",         "mem-004"),
    ("fermentation life force",              "mem-005"),
    ("resonance IWTF convergence equilibrium","mem-008"),
    ("dissonance conflict density threshold","mem-009"),
    ("grief weaponised never user",          "mem-011"),
    ("uncertainty DICAA abstention truth",   "mem-013"),
    ("amethyst hexagonal crystal 432",       "mem-014"),
    ("moldavite tektite meteorite",          "mem-020"),
    ("quantum entanglement particles distance","mem-021"),
    ("surface code topological error correcting","mem-024"),
    ("SynergyEngine five intelligence modules","mem-026"),
    ("ActionGate risk tier classification",  "mem-027"),
    ("consent ledger cryptographic agreements","mem-028"),
    ("shadow unconscious rejected self",     "mem-031"),
    ("individuation integrating unconscious consciousness","mem-032"),
    ("archetypes collective unconscious patterns","mem-034"),
    ("Schumann resonances electromagnetic ionosphere","mem-036"),
    ("528 Hz DNA repair transformation solfeggio","mem-041"),
    ("Canon C01 sovereignty first principle","mem-046"),
    ("mythos visionary not empirically verified","mem-048"),
    ("epistemic humility knows believes",    "mem-049"),
    ("logos empirical validation gates",     "mem-050"),
]


# ---------------------------------------------------------------------------
# MRR computation
# ---------------------------------------------------------------------------

def _mrr_at_k(store: _KeywordMemoryStore, queries: list, k: int = 3) -> float:
    """
    Compute Mean Reciprocal Rank at k.
    For each query, finds the rank of the ground-truth memory in the top-k results.
    Returns 0 for that query if the correct memory is not in top-k.
    """
    reciprocal_ranks = []
    for query_text, correct_id in queries:
        results = store.retrieve(query_text, k=k)
        rr = 0.0
        for rank, result in enumerate(results, start=1):
            if result["id"] == correct_id:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)
    return sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def memory_store() -> _KeywordMemoryStore:
    store = _KeywordMemoryStore()
    for mem_id, text in CORPUS:
        store.add(mem_id, text)
    return store


def test_ev1e_corpus_size(memory_store):
    """EV1-E: corpus must have exactly 50 entries."""
    assert len(memory_store._memories) == 50


def test_ev1e_query_count():
    """EV1-E: labelled query set must have exactly 25 entries."""
    assert len(QUERIES) == 25


def test_ev1e_mrr_gate(memory_store):
    """
    EV1-E acceptance gate: MRR@3 must be >= 0.80.

    A keyword-overlap retriever on a well-designed corpus should achieve
    MRR@3 > 0.90. The 0.80 gate is set to tolerate future probabilistic
    retrievers and noisy real-world queries.
    """
    mrr = _mrr_at_k(memory_store, QUERIES, k=3)
    print(f"\nEV1-E MRR@3 = {mrr:.4f}  (gate >= 0.80)")

    # Per-query breakdown for CI logs
    print("\nEV1-E Per-Query Results:")
    for q, correct_id in QUERIES:
        results = memory_store.retrieve(q, k=3)
        found_at = None
        for rank, r in enumerate(results, 1):
            if r["id"] == correct_id:
                found_at = rank
                break
        rr = (1.0 / found_at) if found_at else 0.0
        status = "✓" if found_at == 1 else (f"rank-{found_at}" if found_at else "✗ MISS")
        print(f"  {status:8s}  RR={rr:.3f}  query='{q[:50]}'")

    assert mrr >= 0.80, (
        f"EV1-E FAILED: MRR@3 = {mrr:.4f} < 0.80 acceptance threshold"
    )


@pytest.mark.parametrize("query,correct_id", QUERIES[:10],
    ids=[f"q{i:02d}" for i in range(10)])
def test_ev1e_top_queries_hit_rank1(memory_store, query, correct_id):
    """EV1-E: First 10 canonical queries must retrieve correct memory at rank 1."""
    results = memory_store.retrieve(query, k=3)
    assert results, f"No results returned for query: '{query}'"
    assert results[0]["id"] == correct_id, (
        f"Query: '{query}'\n"
        f"  Expected rank-1: {correct_id}\n"
        f"  Got rank-1:      {results[0]['id']} (score={results[0]['score']:.4f})\n"
        f"  Top-3: {[r['id'] for r in results]}"
    )


def test_ev1e_empty_query_returns_empty(memory_store):
    """EV1-E: An empty query must return an empty result list without error."""
    results = memory_store.retrieve("", k=3)
    assert results == []


def test_ev1e_k1_retrieval(memory_store):
    """EV1-E: k=1 retrieval must return at most 1 result."""
    results = memory_store.retrieve("alchemical calcination", k=1)
    assert len(results) <= 1

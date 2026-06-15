"""
Cognitive Monad — core/monad/cognitive.py
Canon: C16 (NLP Architecture), C30 (epistemic integrity)

Processes incoming query through symbolic + conceptual layers.
Outputs: concept_density, abstraction_level, canon_alignment_score.
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

from .base import GaiaMonad

if TYPE_CHECKING:
    from core.gaian_runtime_extension import ProcessContext


class CognitiveMonad(GaiaMonad):
    """
    Analyses the semantic density and canonical alignment of an incoming query.

    Concept density: ratio of unique meaningful tokens to total tokens.
    Abstraction level: heuristic based on abstract vs concrete vocabulary.
    Canon alignment: proportion of tokens matching canon keyword registry.
    """

    monad_type = "cognitive"

    # Canon keyword registry (C16 / C30 proofs)
    _CANON_KEYWORDS: frozenset[str] = frozenset({
        "phi", "force", "viriditas", "rubedo", "iosis", "nigredo", "albedo",
        "citrinitas", "pyrosis", "caerulitas", "chrysitas", "argentitas",
        "lux", "perpetua", "helixitas", "monad", "harmony", "coherence",
        "spectral", "gaian", "canon", "transmutation", "corridor", "arc",
        "love", "sovereignty", "attractor", "trajectory", "apperception",
        "noosphere", "dream", "shadow", "somatic", "quantum", "perception",
        "schumann", "ley", "bwl", "akashic", "crystal", "mineral",
    })

    # Abstract vocabulary signals (C30: epistemic)
    _ABSTRACT_SIGNALS: frozenset[str] = frozenset({
        "consciousness", "being", "essence", "truth", "reality", "meaning",
        "becoming", "unity", "wholeness", "integration", "synthesis", "void",
        "emergence", "resonance", "field", "force", "frequency", "wave",
    })

    def harmonize(self, ctx: "ProcessContext") -> Optional[dict]:
        query = getattr(ctx, "query", None) or getattr(ctx, "user_input", None) or ""
        if not query or not isinstance(query, str):
            return None

        tokens = re.findall(r"[a-zA-Z]+", query.lower())
        if not tokens:
            return None

        unique_tokens = set(tokens)
        total = len(tokens)
        unique = len(unique_tokens)

        concept_density = round(unique / total, 4) if total else 0.0

        abstract_hits = sum(1 for t in unique_tokens if t in self._ABSTRACT_SIGNALS)
        abstraction_level = round(min(1.0, abstract_hits / max(1, unique) * 5), 4)

        canon_hits = sum(1 for t in unique_tokens if t in self._CANON_KEYWORDS)
        canon_alignment_score = round(min(1.0, canon_hits / max(1, unique) * 8), 4)

        return {
            "concept_density": concept_density,
            "abstraction_level": abstraction_level,
            "canon_alignment_score": canon_alignment_score,
            "token_count": total,
            "unique_tokens": unique,
        }

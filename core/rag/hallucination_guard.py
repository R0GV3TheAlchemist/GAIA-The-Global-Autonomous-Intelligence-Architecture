"""
GAIA Production RAG Pipeline — Anti-Hallucination Guard
Issue #457

Stage 5: Post-synthesis verification layer.

After the synthesizer produces an answer, the guard:
  1. Extracts every factual claim from the answer text
  2. Verifies each claim against the top-K retrieved source corpus
  3. Assigns a HallucinationRisk level per claim
  4. Hedges or removes high-risk claims before final delivery
  5. Returns an overall hallucination risk score for the full response

Acceptance target: reduce unsupported claims by >50% vs. unguarded baseline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .models import Claim, HallucinationRisk, RankedDoc, SynthesisResult


@dataclass
class GuardConfig:
    remove_critical: bool = True     # remove CRITICAL-risk claims entirely
    hedge_high: bool = True           # prepend hedge phrase to HIGH-risk claims
    hedge_medium: bool = False        # prepend hedge phrase to MEDIUM-risk claims
    min_source_overlap: float = 0.10  # minimum token overlap to count as supported


_HEDGE_PREFIX = "It has been suggested (though not fully verified) that "
_CRITICAL_REPLACEMENT = "[This claim could not be verified against available sources and has been removed.]"


class HallucinationGuard:
    """
    Runs post-synthesis claim verification.

    Usage:
        guard = HallucinationGuard()
        result = guard.evaluate(synthesis_result)
    """

    def __init__(self, config: Optional[GuardConfig] = None):
        self.config = config or GuardConfig()

    def evaluate(self, result: SynthesisResult) -> SynthesisResult:
        """
        Re-evaluate all claims against top_k_docs, update risk scores,
        apply hedging or removal, and recompute overall risk.
        Returns an updated SynthesisResult.
        """
        source_corpus = " ".join(
            doc.doc.content.lower() for doc in result.top_k_docs
        )

        verified_claims: list[Claim] = []
        for claim in result.claims:
            updated = self._verify_claim(claim, source_corpus, result.top_k_docs)
            verified_claims.append(updated)

        # Apply hedging / removal
        final_claims: list[Claim] = []
        answer_parts: list[str] = []

        for claim in verified_claims:
            text, include = self._apply_guard_policy(claim)
            if include:
                final_claims.append(claim)
                answer_parts.append(text)

        # Rebuild answer text from guarded claims
        guarded_answer = " ".join(answer_parts)

        # Recompute counts
        supported = sum(1 for c in final_claims if c.is_supported)
        speculative = sum(1 for c in final_claims if c.flagged_speculative)
        overall_risk = self._compute_overall_risk(final_claims)

        result.claims = final_claims
        result.answer_text = guarded_answer
        result.hallucination_risk_overall = overall_risk
        result.supported_claims_count = supported
        result.speculative_claims_count = speculative

        return result

    # ------------------------------------------------------------------
    # Claim verification
    # ------------------------------------------------------------------

    def _verify_claim(self, claim: Claim, corpus: str, docs: list[RankedDoc]) -> Claim:
        """
        Check whether claim text tokens appear in the source corpus.
        Token overlap >= min_source_overlap → supported.
        """
        if claim.flagged_speculative:
            claim.hallucination_risk = HallucinationRisk.LOW
            return claim

        claim_tokens = set(re.sub(r"[^a-z0-9 ]", "", claim.text.lower()).split())
        if not claim_tokens:
            return claim

        corpus_tokens = set(corpus.split())
        overlap = len(claim_tokens & corpus_tokens) / len(claim_tokens)

        if overlap >= self.config.min_source_overlap:
            claim.is_supported = True
            claim.hallucination_risk = HallucinationRisk.NONE
            claim.confidence = min(1.0, overlap * 2)  # scale confidence by overlap
        else:
            claim.is_supported = False
            if overlap < 0.02:
                claim.hallucination_risk = HallucinationRisk.CRITICAL
                claim.confidence = 0.05
            elif overlap < 0.05:
                claim.hallucination_risk = HallucinationRisk.HIGH
                claim.confidence = 0.15
            else:
                claim.hallucination_risk = HallucinationRisk.MEDIUM
                claim.confidence = 0.30

        return claim

    # ------------------------------------------------------------------
    # Guard policy application
    # ------------------------------------------------------------------

    def _apply_guard_policy(self, claim: Claim) -> tuple[str, bool]:
        """
        Returns (final_text, include_in_output).
        """
        risk = claim.hallucination_risk

        if risk == HallucinationRisk.CRITICAL and self.config.remove_critical:
            return _CRITICAL_REPLACEMENT, False

        if risk == HallucinationRisk.HIGH and self.config.hedge_high:
            return _HEDGE_PREFIX + claim.text, True

        if risk == HallucinationRisk.MEDIUM and self.config.hedge_medium:
            return _HEDGE_PREFIX + claim.text, True

        return claim.text, True

    # ------------------------------------------------------------------
    # Overall risk computation
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_overall_risk(claims: list[Claim]) -> HallucinationRisk:
        if not claims:
            return HallucinationRisk.NONE

        risk_values = {
            HallucinationRisk.NONE:     0,
            HallucinationRisk.LOW:      1,
            HallucinationRisk.MEDIUM:   2,
            HallucinationRisk.HIGH:     3,
            HallucinationRisk.CRITICAL: 4,
        }
        inv_map = {v: k for k, v in risk_values.items()}

        total_risk = sum(risk_values[c.hallucination_risk] for c in claims)
        avg_risk = total_risk / len(claims)

        level = min(4, round(avg_risk))
        return inv_map[level]

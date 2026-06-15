"""
GAIA Production RAG Pipeline — Grounded Synthesizer
Issue #457

Stage 4: Produce a grounded answer where every claim maps to a top-K source.

Key guarantees:
  - Every factual sentence is annotated with source doc_ids
  - Unsupported claims are flagged speculative before delivery
  - Synthesis tone adapts to query intent
  - Inline citation keys are compatible with GAIA frontend renderer
  - Trauma-informed constraints are respected: therapeutic queries receive
    warm tone, never diagnostic framing
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .models import (
    Claim,
    HallucinationRisk,
    Query,
    QueryIntent,
    RankedDoc,
    SynthesisTone,
)


_INTENT_TONE_MAP: dict[QueryIntent, SynthesisTone] = {
    QueryIntent.FACTUAL:      SynthesisTone.PRECISE,
    QueryIntent.RESEARCH:     SynthesisTone.SCHOLARLY,
    QueryIntent.SYMBOLIC:     SynthesisTone.ARCHETYPAL,
    QueryIntent.THERAPEUTIC:  SynthesisTone.WARM,
    QueryIntent.REFLECTIVE:   SynthesisTone.REFLECTIVE,
    QueryIntent.CREATIVE:     SynthesisTone.CREATIVE,
}

_TONE_PREAMBLES: dict[SynthesisTone, str] = {
    SynthesisTone.PRECISE:     "",
    SynthesisTone.SCHOLARLY:   "",
    SynthesisTone.ARCHETYPAL:  "In the language of the Correspondence Architecture: ",
    SynthesisTone.WARM:        "With care and respect for what you are carrying: ",
    SynthesisTone.REFLECTIVE:  "Sitting with this question: ",
    SynthesisTone.CREATIVE:    "",
}


@dataclass
class SynthesizerConfig:
    max_response_tokens: int = 1024
    cite_inline: bool = True
    trauma_diagnostic_guard: bool = True   # never frame therapeutic answers as diagnosis


class Synthesizer:
    """
    Builds a grounded SynthesisOutput from top-K ranked documents.

    In a production deployment this class wraps an LLM call, passing
    the ranked context and the grounding instruction. The current
    implementation provides the prompt-engineering layer and claim
    scaffolding; the LLM adapter is injected via `set_llm_adapter()`.

    Usage:
        synthesizer = Synthesizer()
        output = synthesizer.synthesize(query, ranked_docs)
    """

    def __init__(self, config: Optional[SynthesizerConfig] = None):
        self.config = config or SynthesizerConfig()
        self._llm_adapter = None  # injected at runtime

    def set_llm_adapter(self, adapter) -> None:
        """Inject LLM adapter (OpenAI, Anthropic, Perplexity Sonar, etc.)."""
        self._llm_adapter = adapter

    def synthesize(
        self,
        query: Query,
        ranked_docs: list[RankedDoc],
    ) -> tuple[str, list[Claim], dict[str, str], SynthesisTone]:
        """
        Returns (answer_text, claims, citation_map, tone).
        """
        tone = _INTENT_TONE_MAP[query.intent]
        citation_map: dict[str, str] = {}

        # Build citation map from top-K sources
        for i, rd in enumerate(ranked_docs):
            cite_key = f"[{i+1}]"
            citation_map[cite_key] = rd.doc.source_name

        # Build grounding context block
        context_block = self._build_context(ranked_docs, citation_map)

        # Build grounding prompt
        prompt = self._build_prompt(query, context_block, tone)

        # Call LLM adapter or return structured placeholder
        if self._llm_adapter:
            raw_answer = self._llm_adapter.complete(prompt)
        else:
            raw_answer = self._placeholder_answer(query, ranked_docs, tone, citation_map)

        # Extract claims from answer
        claims = self._extract_claims(raw_answer, ranked_docs)

        return raw_answer, claims, citation_map, tone

    # ------------------------------------------------------------------
    # Context and prompt building
    # ------------------------------------------------------------------

    def _build_context(self, ranked_docs: list[RankedDoc], citation_map: dict[str, str]) -> str:
        lines = ["## Retrieved Sources (in order of relevance and authority)\n"]
        for i, rd in enumerate(ranked_docs):
            cite_key = f"[{i+1}]"
            tier_label = rd.doc.tier.name
            ev_label = rd.doc.evidence_level.value
            lines.append(
                f"{cite_key} [{tier_label} | {ev_label}] {rd.doc.source_name}\n"
                f"{rd.doc.content[:600]}...\n"
            )
        return "\n".join(lines)

    def _build_prompt(self, query: Query, context: str, tone: SynthesisTone) -> str:
        tone_instruction = {
            SynthesisTone.PRECISE:    "Be precise and concise. Use exact terminology.",
            SynthesisTone.SCHOLARLY:  "Write in scholarly style with careful hedging.",
            SynthesisTone.ARCHETYPAL: "Use GAIA's symbolic and archetypal language.",
            SynthesisTone.WARM:       "Respond with warmth and compassion. Never diagnose. Always honour the user's sovereignty.",
            SynthesisTone.REFLECTIVE: "Hold space for the question. Invite reflection.",
            SynthesisTone.CREATIVE:   "Respond with creativity and imaginative depth.",
        }[tone]

        safety_block = ""
        if query.is_trauma_sensitive and self.config.trauma_diagnostic_guard:
            safety_block = (
                "\n⚠️ TRAUMA-INFORMED CONSTRAINT: This query has been flagged as potentially "
                "sensitive. Never use diagnostic language. Never imply pathology. "
                "Always affirm the user's capacity for healing and self-determination.\n"
            )

        return (
            f"You are GAIA. Answer the following query using ONLY the sources provided below.\n"
            f"For every factual claim, include the citation key (e.g. [1]) from the source.\n"
            f"If you cannot support a claim from the sources, prefix it with [SPECULATIVE].\n"
            f"Tone instruction: {tone_instruction}\n"
            f"{safety_block}\n"
            f"## Query\n{query.raw_text}\n\n"
            f"{context}\n\n"
            f"## Your Answer"
        )

    # ------------------------------------------------------------------
    # Claim extraction
    # ------------------------------------------------------------------

    def _extract_claims(self, answer_text: str, ranked_docs: list[RankedDoc]) -> list[Claim]:
        """Split answer into sentences and annotate each with source support."""
        sentences = re.split(r"(?<=[.!?])\s+", answer_text.strip())
        doc_id_map = {f"[{i+1}]": rd.doc.doc_id for i, rd in enumerate(ranked_docs)}
        claims: list[Claim] = []

        for sentence in sentences:
            if not sentence.strip():
                continue

            is_speculative = "[SPECULATIVE]" in sentence
            sentence_clean = sentence.replace("[SPECULATIVE]", "").strip()

            # Find citation keys in this sentence
            cited_keys = re.findall(r"\[\d+\]", sentence)
            source_doc_ids = [doc_id_map[k] for k in cited_keys if k in doc_id_map]

            is_supported = bool(source_doc_ids) and not is_speculative
            risk = HallucinationRisk.NONE if is_supported else (
                HallucinationRisk.LOW if is_speculative else HallucinationRisk.MEDIUM
            )

            claims.append(Claim(
                text=sentence_clean,
                source_doc_ids=source_doc_ids,
                is_supported=is_supported,
                hallucination_risk=risk,
                confidence=1.0 if is_supported else 0.3,
                flagged_speculative=is_speculative,
            ))

        return claims

    # ------------------------------------------------------------------
    # Placeholder (used when no LLM adapter is connected)
    # ------------------------------------------------------------------

    def _placeholder_answer(
        self,
        query: Query,
        ranked_docs: list[RankedDoc],
        tone: SynthesisTone,
        citation_map: dict[str, str],
    ) -> str:
        preamble = _TONE_PREAMBLES.get(tone, "")
        top = ranked_docs[0] if ranked_docs else None
        if not top:
            return f"{preamble}[SPECULATIVE] No sources were retrieved for this query."

        return (
            f"{preamble}Based on the available sources, {query.raw_text.lower()} "
            f"is addressed in [1] ({top.doc.source_name}). "
            f"[SPECULATIVE] Further synthesis requires LLM adapter integration."
        )

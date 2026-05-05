"""GAIA-OS Affect Engine — Heuristics backend

This is the default local backend for Issue #65 scaffolding.
It is intentionally simple and deterministic so the full pipeline can be wired now.
Later it can be replaced by:
- sentence-transformers + classifier heads
- llama.cpp local LLM prompting
- hybrid lexicon + transformer models
"""

from __future__ import annotations

import math
import re
from collections import Counter

from .types import AffectAnalysisResult, PadVector

TOKEN_RE = re.compile(r"[A-Za-z']+")

LEXICONS = {
    "joy": {
        "happy", "joy", "grateful", "excited", "hopeful", "love", "peaceful", "calm", "good",
        "great", "wonderful", "beautiful", "relieved", "alive", "thankful",
    },
    "sadness": {
        "sad", "grief", "lonely", "hurt", "cry", "tired", "empty", "heavy", "down",
        "hopeless", "lost", "broken", "numb", "ashamed",
    },
    "anger": {
        "angry", "furious", "mad", "resent", "rage", "annoyed", "frustrated", "hate",
        "irritated", "bitter",
    },
    "fear": {
        "afraid", "fear", "anxious", "panic", "terrified", "worried", "unsafe", "scared",
        "nervous", "uneasy",
    },
    "disgust": {
        "disgust", "gross", "revolting", "sickened", "repulsed", "dirty",
    },
    "surprise": {
        "surprised", "shocked", "suddenly", "unexpected", "wow", "astonished",
    },
}

PAD_ANCHORS = {
    "joy": PadVector(0.80, 0.62, 0.70),
    "sadness": PadVector(-0.72, 0.22, 0.22),
    "anger": PadVector(-0.70, 0.80, 0.72),
    "fear": PadVector(-0.76, 0.86, 0.18),
    "disgust": PadVector(-0.65, 0.46, 0.58),
    "surprise": PadVector(0.05, 0.88, 0.50),
    "neutral": PadVector(0.00, 0.10, 0.50),
}

NEUTRAL_HINTS = {
    "update", "todo", "meeting", "schedule", "bug", "task", "fix", "refactor", "build",
    "commit", "branch", "issue", "deploy", "config", "version", "documentation",
}


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def lexical_entropy(tokens: list[str]) -> float:
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    total = len(tokens)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    max_entropy = math.log2(max(len(counts), 2))
    return max(0.0, min(1.0, entropy / max_entropy))


def analyze_text_heuristic(text: str) -> AffectAnalysisResult:
    tokens = tokenize(text)
    if not tokens:
        return AffectAnalysisResult(
            label="neutral",
            confidence=0.99,
            pad=PAD_ANCHORS["neutral"],
            is_neutral_primary=True,
            entropy=0.0,
            explanation="No emotional language detected.",
        )

    token_set = set(tokens)
    entropy = lexical_entropy(tokens)

    neutral_hits = len(token_set & NEUTRAL_HINTS)
    emotion_scores: dict[str, int] = {
        label: len(token_set & words) for label, words in LEXICONS.items()
    }

    best_label = max(emotion_scores, key=emotion_scores.get)
    best_score = emotion_scores[best_label]
    total_emotion_hits = sum(emotion_scores.values())

    if best_score == 0 and neutral_hits > 0:
        return AffectAnalysisResult(
            label="neutral",
            confidence=0.90,
            pad=PAD_ANCHORS["neutral"],
            is_neutral_primary=True,
            entropy=entropy,
            explanation="Message appears primarily factual or procedural rather than emotional.",
        )

    if total_emotion_hits == 0:
        return AffectAnalysisResult(
            label="neutral",
            confidence=0.78,
            pad=PAD_ANCHORS["neutral"],
            is_neutral_primary=True,
            entropy=entropy,
            explanation="No clear dominant emotional signal was found.",
        )

    confidence = min(0.95, 0.45 + (best_score / max(len(tokens), 1)) * 4.0)
    pad = PAD_ANCHORS[best_label]

    # Small entropy-based adjustment: more complex text reduces dominance slightly.
    adjusted = PadVector(
        pleasure=pad.pleasure,
        arousal=min(1.0, pad.arousal + (0.05 if best_label in {"fear", "anger", "surprise"} else 0.0)),
        dominance=max(0.0, min(1.0, pad.dominance - entropy * 0.10)),
    ).clamp()

    return AffectAnalysisResult(
        label=best_label,
        confidence=confidence,
        pad=adjusted,
        is_neutral_primary=False,
        entropy=entropy,
        explanation=f"Detected strongest lexical evidence for {best_label}.",
    )

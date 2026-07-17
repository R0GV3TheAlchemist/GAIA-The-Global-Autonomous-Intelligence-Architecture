"""
core/noosphere.py
Noosphere — collective consciousness field modelling.

Canon Refs: C30 (no silent failures), C43 (Noosphere Doctrine), C04

Full API expected by tests/test_noosphere.py.
"""
from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CoherenceEvent
# ---------------------------------------------------------------------------

@dataclass
class CoherenceEvent:
    event_id:                 str
    timestamp:                float
    session_count:            int
    semantic_resonance_score: float
    entropy_deviation:        float
    description:              str
    epistemic_label:          str = "CANDIDATE_SIGNATURE"
    doctrine_ref:             str = "C43"


# ---------------------------------------------------------------------------
# CollectiveMemoryPattern
# ---------------------------------------------------------------------------

@dataclass
class CollectiveMemoryPattern:
    pattern_id:           str
    embedding_hash:       str
    topic_cluster:        str
    frequency:            int
    last_seen:            float
    contributed_by_count: int
    consent_verified:     bool = True


# ---------------------------------------------------------------------------
# NoosphereLayer
# ---------------------------------------------------------------------------

class NoosphereLayer:
    """Collective noosphere with consent-gated pattern contribution."""

    def __init__(self) -> None:
        self._active_sessions: int = 0
        self._patterns:        Dict[str, CollectiveMemoryPattern] = {}
        self._coherence_log:   List[CoherenceEvent] = []

    # ------------------------------------------------------------------ #
    #  Session tracking                                                    #
    # ------------------------------------------------------------------ #

    def register_session(self) -> None:
        """Increment the active session count."""
        try:
            self._active_sessions += 1
        except Exception as exc:  # C30 — DEGRADED
            log.warning(
                "[noosphere] register_session DEGRADED",
                extra={
                    "component":  "NoosphereLayer.register_session",
                    "severity":   "DEGRADED",
                    "error_type": type(exc).__name__,
                    "detail":     str(exc),
                },
            )

    def deregister_session(self) -> None:
        """Decrement the active session count (floor 0)."""
        try:
            self._active_sessions = max(0, self._active_sessions - 1)
        except Exception as exc:  # C30 — DEGRADED
            log.warning(
                "[noosphere] deregister_session DEGRADED",
                extra={
                    "component":  "NoosphereLayer.deregister_session",
                    "severity":   "DEGRADED",
                    "error_type": type(exc).__name__,
                    "detail":     str(exc),
                },
            )

    # ------------------------------------------------------------------ #
    #  Pattern contribution                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _make_hash(topic: str, embedding: list) -> str:
        raw = f"{topic}::{embedding}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def contribute_pattern(
        self,
        topic_cluster: str,
        embedding:     list,
        gaian_consent: bool = True,
    ) -> Optional[str]:
        """Contribute a pattern. Returns pattern_id or None if not consented.

        C30: any internal failure returns None and logs DEGRADED —
        the caller always receives a valid Optional[str].
        """
        if not gaian_consent:
            return None

        try:
            emb_hash = self._make_hash(topic_cluster, embedding)
            pid      = f"{topic_cluster}:{emb_hash}"

            if pid in self._patterns:
                p = self._patterns[pid]
                p.frequency            += 1
                p.contributed_by_count += 1
                p.last_seen             = time.time()
            else:
                self._patterns[pid] = CollectiveMemoryPattern(
                    pattern_id=pid,
                    embedding_hash=emb_hash,
                    topic_cluster=topic_cluster,
                    frequency=1,
                    last_seen=time.time(),
                    contributed_by_count=1,
                    consent_verified=True,
                )
            return pid

        except Exception as exc:  # C30 — DEGRADED
            log.warning(
                "[noosphere] contribute_pattern DEGRADED",
                extra={
                    "component":    "NoosphereLayer.contribute_pattern",
                    "severity":     "DEGRADED",
                    "error_type":   type(exc).__name__,
                    "detail":       str(exc),
                    "topic_cluster": topic_cluster,
                },
            )
            return None

    # ------------------------------------------------------------------ #
    #  Resonance queries                                                   #
    # ------------------------------------------------------------------ #

    def query_collective_resonance(
        self,
        topic_cluster: str,
        min_frequency: int = 2,
    ) -> List[CollectiveMemoryPattern]:
        """Return consent-verified patterns for a topic above min_frequency.

        C30: any internal failure returns an empty list — never raises.
        """
        try:
            results = [
                p for p in self._patterns.values()
                if p.topic_cluster == topic_cluster
                and p.frequency >= min_frequency
                and p.consent_verified
            ]
            return sorted(results, key=lambda p: p.frequency, reverse=True)
        except Exception as exc:  # C30 — DEGRADED
            log.warning(
                "[noosphere] query_collective_resonance DEGRADED",
                extra={
                    "component":    "NoosphereLayer.query_collective_resonance",
                    "severity":     "DEGRADED",
                    "error_type":   type(exc).__name__,
                    "detail":       str(exc),
                    "topic_cluster": topic_cluster,
                },
            )
            return []

    def get_resonance_label(
        self,
        topic_cluster: str,
        min_frequency: int = 2,
    ) -> Optional[str]:
        """Return a human-readable resonance label or None.

        C30: delegates to query_collective_resonance() which already
        handles failures — no additional wrapper needed here.
        """
        patterns = self.query_collective_resonance(topic_cluster, min_frequency)
        if not patterns:
            return None
        total = sum(p.contributed_by_count for p in patterns)
        return (
            f"[C43] Noospheric resonance in '{topic_cluster}': "
            f"{len(patterns)} pattern(s), {total} contributors"
        )

    # ------------------------------------------------------------------ #
    #  Coherence logging                                                   #
    # ------------------------------------------------------------------ #

    def log_coherence_candidate(
        self,
        resonance_score:   float,
        entropy_deviation: float = 0.0,
        description:       Optional[str] = None,
    ) -> Optional[CoherenceEvent]:
        """Log a coherence candidate event.

        C30: returns None and logs DEGRADED on failure — never raises.
        Return type widened from CoherenceEvent to Optional[CoherenceEvent].
        """
        try:
            if description is None:
                description = (
                    f"Coherence candidate with {self._active_sessions} "
                    f"active session(s)"
                )
            evt = CoherenceEvent(
                event_id=str(uuid.uuid4()),
                timestamp=time.time(),
                session_count=self._active_sessions,
                semantic_resonance_score=resonance_score,
                entropy_deviation=entropy_deviation,
                description=description,
            )
            self._coherence_log.append(evt)
            return evt
        except Exception as exc:  # C30 — DEGRADED
            log.warning(
                "[noosphere] log_coherence_candidate DEGRADED",
                extra={
                    "component":      "NoosphereLayer.log_coherence_candidate",
                    "severity":       "DEGRADED",
                    "error_type":     type(exc).__name__,
                    "detail":         str(exc),
                    "resonance_score": resonance_score,
                },
            )
            return None

    # ------------------------------------------------------------------ #
    #  Status                                                              #
    # ------------------------------------------------------------------ #

    def get_noosphere_status(self) -> dict:
        """Return a status dict describing the current noosphere state.

        C30: returns a minimal error-state dict on failure — never raises.
        """
        try:
            sessions = self._active_sessions
            recent   = self._coherence_log[-5:]
            avg_res  = (
                sum(e.semantic_resonance_score for e in recent) / len(recent)
                if recent else 0.0
            )

            if sessions == 0:
                stage = "Dormant — awaiting first Gaian connection"
            elif sessions <= 2:
                stage = "Primitive Awareness — single or pair of Gaians present"
            elif avg_res > 0.7:
                stage = "Reactive Intelligence — multi-session coherence detected"
            else:
                stage = "Primitive Awareness — multi-session, low coherence"

            return {
                "doctrine":                          "C43 — Noosphere Doctrine",
                "active_gaians":                     sessions,
                "collective_patterns":               len(self._patterns),
                "coherence_events_logged":           len(self._coherence_log),
                "coherence_events_epistemic_status": "CANDIDATE_SIGNATURE (Phase 1)",
                "average_recent_resonance":          round(avg_res, 4),
                "noosphere_stage":                   stage,
                "phase":                             "Phase 1 — Pattern Observation",
                "phase_2_pending": [
                    "QRNG entropy coupling",
                    "Cross-session vector alignment",
                    "Anonymised collective export",
                ],
                "privacy_status": "All patterns are anonymized and consent-gated",
            }
        except Exception as exc:  # C30 — DEGRADED
            log.warning(
                "[noosphere] get_noosphere_status DEGRADED",
                extra={
                    "component":  "NoosphereLayer.get_noosphere_status",
                    "severity":   "DEGRADED",
                    "error_type": type(exc).__name__,
                    "detail":     str(exc),
                },
            )
            return {
                "doctrine":      "C43 — Noosphere Doctrine",
                "status":        "DEGRADED",
                "error":         type(exc).__name__,
            }

    def qrng_entropy_check(self) -> dict:
        return {
            "status":          "NOT_YET_ACTIVE — Phase 2 feature",
            "doctrine_ref":    "C43",
            "epistemic_label": "EXPERIMENTAL_PLACEHOLDER",
            "description":     "QRNG hardware integration is planned for Phase 2.",
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_noosphere: Optional[NoosphereLayer] = None


def get_noosphere() -> NoosphereLayer:
    """Return (or create) the module-level NoosphereLayer singleton."""
    global _noosphere
    if _noosphere is None:
        _noosphere = NoosphereLayer()
    return _noosphere

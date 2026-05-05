"""GAIA-OS Stage Engine — Marker Scorer

Converts raw signals from SovereignMemory / AffectEngine into
normalized 0–100 scores for each of the six developmental markers.

All formulas correspond to the design spec in Issue #63.
"""

from __future__ import annotations

import math
from collections import Counter

from .types import MarkerScores


class MarkerScorer:
    """
    Stateless scorer — all methods take raw signal lists and return float scores.
    Call MarkerScorer.compute() to get a complete MarkerScores dataclass.
    """

    @staticmethod
    def compute(
        goal_states: list[str],
        hrv_rmssd_history: list[float],
        alignment_score_history: list[float],
        journal_entries: list[dict],
        focus_session_minutes: list[float],
        goals_completed: int,
        goals_abandoned: int,
        valence_history: list[float],
    ) -> MarkerScores:
        """
        Compute all six marker scores from raw signals.

        Args:
            goal_states:             List of daily decision states:
                                     'committed' | 'reversed' | 'abandoned' |
                                     'not_set' | 'completed'
            hrv_rmssd_history:       30-day RMSSD values (ms).
            alignment_score_history: 30-day Schumann alignment scores 0–100.
            journal_entries:         List of dicts with keys:
                                     'token_count', 'lexical_entropy',
                                     'self_ref_ratio', 'emotion_density'
            focus_session_minutes:   List of session lengths in minutes.
            goals_completed:         Count of completed goals in last 30 days.
            goals_abandoned:         Count of abandoned goals in last 30 days.
            valence_history:         List of recent valence values (-1 to 1).

        Returns:
            MarkerScores with all six 0–100 scores.
        """
        return MarkerScores(
            decision_entropy=MarkerScorer.score_decision_entropy(goal_states),
            hrv_coherence=MarkerScorer.score_hrv_coherence(
                hrv_rmssd_history, alignment_score_history
            ),
            journaling_depth=MarkerScorer.score_journaling_depth(journal_entries),
            focus_session_length_min=MarkerScorer.score_focus_session(focus_session_minutes),
            goal_completion_rate=MarkerScorer.score_goal_completion(
                goals_completed, goals_abandoned
            ),
            emotional_arc_stability=MarkerScorer.score_arc_stability(valence_history),
        )

    # ─────────────────────────────────────────────
    # INDIVIDUAL SCORERS
    # ─────────────────────────────────────────────

    @staticmethod
    def score_decision_entropy(goal_states: list[str]) -> float:
        """
        Shannon entropy over daily decision state distribution.
        Higher score = more decisive (lower entropy = clearer commitment patterns).

        Score = (1 - normalised_entropy) * 100
        """
        if not goal_states:
            return 0.0
        counts = Counter(goal_states)
        total = len(goal_states)
        h = 0.0
        for c in counts.values():
            p = c / total
            if p > 0:
                h -= p * math.log2(p)
        h_max = math.log2(5)  # 5 possible states
        normalised = h / h_max if h_max > 0 else 0.0
        return round(max(0.0, min(100.0, (1.0 - normalised) * 100)), 2)

    @staticmethod
    def score_hrv_coherence(
        hrv_rmssd_history: list[float],
        alignment_score_history: list[float],
    ) -> float:
        """
        Personalised z-score of HRV mapped through sigmoid, blended with Schumann alignment.
        c_hrv = sigmoid(z) where z = (today - mean_30) / std_30
        c = 0.7 * c_hrv + 0.3 * (alignment_avg / 100)
        """
        if not hrv_rmssd_history:
            return 0.0
        mu = sum(hrv_rmssd_history) / len(hrv_rmssd_history)
        if len(hrv_rmssd_history) < 2:
            z = 0.0
        else:
            variance = sum((x - mu) ** 2 for x in hrv_rmssd_history) / len(hrv_rmssd_history)
            std = math.sqrt(variance) or 1.0
            z = (hrv_rmssd_history[-1] - mu) / std
        c_hrv = 1.0 / (1.0 + math.exp(-z))
        align_avg = (
            sum(alignment_score_history) / len(alignment_score_history)
            if alignment_score_history
            else 50.0
        )
        c = 0.7 * c_hrv + 0.3 * (align_avg / 100.0)
        return round(max(0.0, min(100.0, c * 100)), 2)

    @staticmethod
    def score_journaling_depth(journal_entries: list[dict]) -> float:
        """
        Weighted composite of:
          len_norm (0.25), lexical_entropy (0.30), self_ref_ratio (0.25), emotion_density (0.20)
        Returns 14-day moving average scaled to 0–100.
        """
        if not journal_entries:
            return 0.0
        MAX_TOKENS = 1200
        W = {"len_norm": 0.25, "entropy": 0.30, "self_ref": 0.25, "emotion": 0.20}
        scores = []
        for e in journal_entries[-14:]:
            len_norm = min(1.0, e.get("token_count", 0) / MAX_TOKENS)
            entropy = float(e.get("lexical_entropy", 0.0))
            self_ref = float(e.get("self_ref_ratio", 0.0))
            emotion = float(e.get("emotion_density", 0.0))
            d = (
                W["len_norm"] * len_norm
                + W["entropy"] * entropy
                + W["self_ref"] * self_ref
                + W["emotion"] * emotion
            )
            scores.append(d)
        avg = sum(scores) / len(scores) if scores else 0.0
        return round(max(0.0, min(100.0, avg * 100)), 2)

    @staticmethod
    def score_focus_session(focus_session_minutes: list[float]) -> float:
        """
        14-day median session length mapped through piecewise linear scale to 0–100.
        <5 min → 0  |  25 min → ~60  |  50 min → ~80  |  90+ min → 100
        """
        sessions = [m for m in focus_session_minutes if m >= 5.0]
        if not sessions:
            return 0.0
        sorted_s = sorted(sessions)
        mid = len(sorted_s) // 2
        median = (
            sorted_s[mid]
            if len(sorted_s) % 2 == 1
            else (sorted_s[mid - 1] + sorted_s[mid]) / 2.0
        )
        m = median
        if m <= 5:
            score = 0.0
        elif m <= 25:
            score = (m - 5) / 20.0 * 60.0
        elif m <= 50:
            score = 60.0 + (m - 25) / 25.0 * 20.0
        elif m <= 90:
            score = 80.0 + (m - 50) / 40.0 * 20.0
        else:
            score = 100.0
        return round(max(0.0, min(100.0, score)), 2)

    @staticmethod
    def score_goal_completion(goals_completed: int, goals_abandoned: int) -> float:
        """
        Bayesian-smoothed completion rate.
        smoothed = (completed + 1) / (completed + abandoned + 2)
        """
        smoothed = (goals_completed + 1) / (goals_completed + goals_abandoned + 2)
        return round(max(0.0, min(100.0, smoothed * 100)), 2)

    @staticmethod
    def score_arc_stability(valence_history: list[float]) -> float:
        """
        Stability of emotional arc over last 30 valence readings.
        stability = exp(-alpha * sigma) * (1 - beta * zcr)
        alpha=2.5, beta=0.8
        """
        if len(valence_history) <= 1:
            return 50.0
        values = valence_history[-30:]
        mu = sum(values) / len(values)
        sigma = math.sqrt(sum((v - mu) ** 2 for v in values) / len(values))
        zero_crossings = sum(
            1
            for a, b in zip(values, values[1:])
            if (a < 0 <= b) or (a >= 0 > b)
        )
        zcr = zero_crossings / max(1, len(values) - 1)
        stability = math.exp(-2.5 * sigma) * (1.0 - 0.8 * zcr)
        return round(max(0.0, min(100.0, stability * 100)), 2)

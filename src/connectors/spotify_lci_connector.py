"""
src/connectors/spotify_lci_connector.py

SpotifyLCIConnector — maps Spotify session data to LCIHistoryEntry phi values.

Phase 2 scaffold: mapping heuristic is stubbed; real Spotify API integration
requires credentials in repo Secrets (deferred manual step).

Issue: #825
Canon: docs/canon/GAIAN_IDENTITY.md
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from src.gaian.runtimetypes import LCIHistoryEntry

log = logging.getLogger(__name__)


class SpotifyLCIConnector:
    """
    Converts Spotify listening session payloads into `LCIHistoryEntry` objects.

    The phi mapping heuristic uses:
      - valence     (0–1): emotional positivity of the track
      - energy      (0–1): intensity/activity of the track
      - duration_ms: listening duration as a completeness proxy

    phi = 0.5 * valence + 0.3 * energy + 0.2 * completeness_ratio

    If any required field is absent or malformed, phi falls back to
    *baseline* (default 0.5) rather than raising, so profile updates
    are always safe to call.
    """

    PHI_FALLBACK = 0.5

    def __init__(self, baseline: float = 0.5) -> None:
        if not 0.0 <= baseline <= 1.0:
            raise ValueError(f"baseline must be in [0, 1], got {baseline}")
        self.baseline = baseline

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest_session(self, session_data: dict) -> LCIHistoryEntry:
        """
        Convert a single Spotify session payload to an LCIHistoryEntry.

        Never raises on malformed input — returns phi=baseline instead.
        """
        try:
            phi = self._compute_phi(session_data)
        except Exception as exc:  # noqa: BLE001
            log.warning("SpotifyLCIConnector: phi computation failed (%s); using baseline.", exc)
            phi = self.baseline

        ts = session_data.get("played_at") or datetime.now(timezone.utc).isoformat()
        session_id = session_data.get("session_id") or "spotify-unknown"

        return LCIHistoryEntry(phi=phi, timestamp=ts, session_id=session_id)

    def batch_ingest(self, sessions: list[dict]) -> list[LCIHistoryEntry]:
        """
        Convert a list of Spotify session payloads to LCIHistoryEntry objects.

        Processes each session independently so one failure does not
        abort the batch.
        """
        return [self.ingest_session(s) for s in sessions]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_phi(self, session: dict) -> float:
        """
        Derive phi from Spotify audio features.

        Expected keys in *session*:
          - track.audio_features.valence      (float 0–1)
          - track.audio_features.energy       (float 0–1)
          - track.duration_ms                 (int)
          - progress_ms                       (int)  [optional]
        """
        # TODO: replace with real Spotify API field extraction
        features = session.get("track", {}).get("audio_features", {})
        valence = float(features.get("valence", self.baseline))
        energy = float(features.get("energy", self.baseline))

        duration_ms = session.get("track", {}).get("duration_ms", 1)
        progress_ms = session.get("progress_ms", duration_ms)
        completeness = min(1.0, progress_ms / max(1, duration_ms))

        phi = 0.5 * valence + 0.3 * energy + 0.2 * completeness
        return round(max(0.0, min(1.0, phi)), 4)

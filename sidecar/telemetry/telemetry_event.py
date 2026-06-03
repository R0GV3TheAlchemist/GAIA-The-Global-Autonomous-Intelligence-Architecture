"""TelemetryEvent schema — GAIA-OS Issue #188.

Canon refs:
  C05 — Transparency: every agentic action is auditable.
  C30 — No silent failures: all failures and degradations are captured.
  C01 — Sovereignty: telemetry is local, private, and never transmitted.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class TelemetryEvent:
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str = "default"
    source: str = "synergy_orchestrator"
    event_type: str = "job_started"
    skill_id: str | None = None
    trust_tier: str | None = None
    intent_class: str | None = None
    risk_tier: str | None = None
    input_summary: str = ""
    output_summary: str = ""
    duration_ms: int = 0
    dq_score: float | None = None
    degraded: bool = False
    fallback_mode: str | None = None
    biometric_context: str | None = None
    planetary_context: str | None = None
    canon_refs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_record(self) -> dict[str, Any]:
        record = asdict(self)
        record["timestamp"] = self.timestamp.isoformat()
        record["canon_refs"] = list(self.canon_refs)
        record["tags"] = list(self.tags)
        return record

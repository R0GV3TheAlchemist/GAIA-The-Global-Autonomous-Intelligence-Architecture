"""
core/governance/explainability.py
Explainability — canon-grounded decision explanation layer.

Public API expected by tests/test_explainability.py:
  CanonCitation, CanonCitationSummary, CounterfactualResult,
  DashboardEntry, DecisionExplainer, DecisionReport, DecisionStep,
  HaltStatus
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums / simple value types
# ---------------------------------------------------------------------------

class HaltStatus:
    """Sentinel values for decision halt states."""
    OK         = "ok"
    HALTED     = "halted"
    ERROR      = "error"
    INCOMPLETE = "incomplete"


# ---------------------------------------------------------------------------
# CanonCitation  (basic citation object, reused in legacy API)
# ---------------------------------------------------------------------------

@dataclass
class CanonCitation:
    """A reference to a specific canon document / section."""
    canon_id: str
    section:  str   = ""
    excerpt:  str   = ""
    weight:   float = 1.0

    def to_dict(self) -> dict:
        return {
            "canon_id": self.canon_id,
            "section":  self.section,
            "excerpt":  self.excerpt,
            "weight":   self.weight,
        }


# ---------------------------------------------------------------------------
# CanonCitationSummary  (aggregated per-session citation, used by
#                        canon_citations_for_session)
# ---------------------------------------------------------------------------

@dataclass
class CanonCitationSummary:
    ref:       str
    frequency: int
    trace_ids: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# DecisionStep  (one trace record mapped to a step)
# ---------------------------------------------------------------------------

@dataclass
class DecisionStep:
    trace_id:       str
    event:          str
    gaian_id:       str
    correlation_id: str
    canon_refs:     List[str]
    started_at:     str
    ended_at:       str
    latency_ms:     float
    inputs:         Dict[str, Any]
    outputs:        Dict[str, Any]
    error:          Optional[str]
    meta:           Dict[str, Any]

    @property
    def has_error(self) -> bool:
        return bool(self.error)

    @classmethod
    def from_record(cls, rec: dict) -> "DecisionStep":
        return cls(
            trace_id=rec.get("trace_id", ""),
            event=rec.get("event", ""),
            gaian_id=rec.get("gaian_id", ""),
            correlation_id=rec.get("correlation_id", ""),
            canon_refs=rec.get("canon_refs") or [],
            started_at=rec.get("started_at", ""),
            ended_at=rec.get("ended_at", ""),
            latency_ms=float(rec.get("latency_ms", 0.0)),
            inputs=rec.get("inputs") or {},
            outputs=rec.get("outputs") or {},
            error=rec.get("error"),
            meta=rec.get("meta") or {},
        )


# ---------------------------------------------------------------------------
# DecisionReport  (full per-session report)
# ---------------------------------------------------------------------------

@dataclass
class DecisionReport:
    session_id:            str
    steps:                 List[DecisionStep]    = field(default_factory=list)
    citations:             List[CanonCitation]   = field(default_factory=list)
    rationale:             str                   = ""
    confidence:            float                 = 1.0
    metadata:              Dict[str, Any]        = field(default_factory=dict)
    timestamp:             str                   = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    doctrine_ref:          str = "C-EXPLAINABILITY:1.0"
    halt_status:           str = HaltStatus.OK

    # Legacy field (non-session usage)
    decision:              str = ""

    # ------------------------------------------------------------------ #
    #  Computed properties                                                 #
    # ------------------------------------------------------------------ #

    @property
    def total_steps(self) -> int:
        return len(self.steps)

    @property
    def error_count(self) -> int:
        return sum(1 for s in self.steps if s.has_error)

    @property
    def total_latency_ms(self) -> float:
        return sum(s.latency_ms for s in self.steps)

    @property
    def plain_language_summary(self) -> str:
        canon_refs: set = set()
        for s in self.steps:
            canon_refs.update(s.canon_refs)
        error_part = (
            f" {self.error_count} step(s) encountered an error."
            if self.error_count > 0 else ""
        )
        canon_part = (
            f" Canon references consulted: {', '.join(sorted(canon_refs))}."
            if canon_refs else ""
        )
        return (
            f"Session '{self.session_id}' completed {self.total_steps} reasoning steps "
            f"in {self.total_latency_ms:.1f} ms."
            f"{error_part}"
            f"{canon_part}"
        )

    def add_citation(self, citation: CanonCitation) -> None:
        self.citations.append(citation)

    def to_dict(self) -> dict:
        return {
            "session_id":     self.session_id,
            "total_steps":    self.total_steps,
            "error_count":    self.error_count,
            "total_latency_ms": self.total_latency_ms,
            "rationale":      self.rationale,
            "confidence":     round(self.confidence, 4),
            "citations":      [c.to_dict() for c in self.citations],
            "metadata":       self.metadata,
            "timestamp":      self.timestamp,
            "doctrine_ref":   self.doctrine_ref,
            "halt_status":    self.halt_status,
        }


# ---------------------------------------------------------------------------
# CounterfactualResult
# ---------------------------------------------------------------------------

@dataclass
class CounterfactualResult:
    canon_ref:             str
    canon_dependency_depth: int
    affected_steps:        List[str]   = field(default_factory=list)
    affected_event_types:  List[str]   = field(default_factory=list)
    impact_summary:        str         = ""


# ---------------------------------------------------------------------------
# DashboardEntry
# ---------------------------------------------------------------------------

@dataclass
class DashboardEntry:
    session_id:     str
    step_count:     int
    error_count:    int
    latency_ms:     float
    top_canon_refs: List[str]  = field(default_factory=list)
    gaian_ids:      List[str]  = field(default_factory=list)


# ---------------------------------------------------------------------------
# ExplainabilityRecord  (legacy)
# ---------------------------------------------------------------------------

@dataclass
class ExplainabilityRecord:
    decision:   str
    citations:  List[CanonCitation] = field(default_factory=list)
    rationale:  str   = ""
    confidence: float = 1.0

    def add_citation(self, citation: CanonCitation) -> None:
        self.citations.append(citation)

    def to_dict(self) -> dict:
        return {
            "decision":   self.decision,
            "citations":  [c.to_dict() for c in self.citations],
            "rationale":  self.rationale,
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# DecisionExplainer
# ---------------------------------------------------------------------------

_CANON_REF_RE = re.compile(r"\bC\d{2,}\b")


class DecisionExplainer:
    """
    Reads JSONL audit trace files from audit_dir and provides
    per-session decision explanations, canon citation summaries,
    trace exports, counterfactual analysis, and a dashboard view.
    """

    def __init__(
        self,
        audit_dir: Optional[Path] = None,
    ) -> None:
        self._audit_dir = Path(audit_dir) if audit_dir else Path("audit")
        # Legacy in-memory records list (backwards compat)
        self._records: List[ExplainabilityRecord] = []

    # ------------------------------------------------------------------ #
    #  JSONL loading helpers                                               #
    # ------------------------------------------------------------------ #

    def _load_all_records(self) -> List[dict]:
        """Load all JSONL trace records from audit_dir."""
        records: List[dict] = []
        if not self._audit_dir.exists():
            return records
        for path in sorted(self._audit_dir.glob("*.jsonl")):
            with path.open() as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        return records

    def _records_for_session(
        self,
        correlation_id: str,
        gaian_id: Optional[str] = None,
    ) -> List[dict]:
        return [
            r for r in self._load_all_records()
            if r.get("correlation_id") == correlation_id
            and (gaian_id is None or r.get("gaian_id") == gaian_id)
        ]

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def explain_session(self, correlation_id: str) -> DecisionReport:
        """Build a DecisionReport for a given correlation_id / session."""
        raw = self._records_for_session(correlation_id)
        steps = [DecisionStep.from_record(r) for r in raw]
        return DecisionReport(session_id=correlation_id, steps=steps)

    def canon_citations_for_session(
        self,
        correlation_id: str,
    ) -> List[CanonCitationSummary]:
        """Return per-ref citation summaries sorted by frequency descending."""
        raw = self._records_for_session(correlation_id)
        freq:  Dict[str, int]       = defaultdict(int)
        tids:  Dict[str, List[str]] = defaultdict(list)
        for r in raw:
            refs = r.get("canon_refs") or []
            tid  = r.get("trace_id", "")
            for ref in refs:
                freq[ref] += 1
                tids[ref].append(tid)
        summaries = [
            CanonCitationSummary(ref=ref, frequency=freq[ref], trace_ids=tids[ref])
            for ref in freq
        ]
        return sorted(summaries, key=lambda s: s.frequency, reverse=True)

    def export_trace(
        self,
        correlation_id: str,
        gaian_id: Optional[str] = None,
    ) -> List[dict]:
        """Return raw trace records for the session, optionally filtered by gaian_id."""
        return self._records_for_session(correlation_id, gaian_id=gaian_id)

    def counterfactual(
        self,
        correlation_id: str,
        canon_ref: str,
    ) -> CounterfactualResult:
        """Analyse what would change if a given Canon ref were absent."""
        raw = self._records_for_session(correlation_id)
        affected_steps: List[str] = []
        event_types:    List[str] = []
        for r in raw:
            if canon_ref in (r.get("canon_refs") or []):
                tid = r.get("trace_id", "")
                affected_steps.append(tid)
                evt = r.get("event", "")
                if evt not in event_types:
                    event_types.append(evt)

        depth = len(affected_steps)
        if depth == 0:
            summary = (
                f"Canon ref '{canon_ref}' was not used in session "
                f"'{correlation_id}'. No effect on reasoning."
            )
        else:
            summary = (
                f"Removing '{canon_ref}' would affect {depth} step(s): "
                f"{', '.join(event_types)}."
            )
        return CounterfactualResult(
            canon_ref=canon_ref,
            canon_dependency_depth=depth,
            affected_steps=affected_steps,
            affected_event_types=event_types,
            impact_summary=summary,
        )

    def dashboard(
        self,
        gaian_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[DashboardEntry]:
        """Return a per-session summary list, optionally filtered by gaian_id."""
        all_records = self._load_all_records()
        if gaian_id:
            all_records = [r for r in all_records if r.get("gaian_id") == gaian_id]

        # Group by correlation_id
        groups: Dict[str, List[dict]] = defaultdict(list)
        for r in all_records:
            cid = r.get("correlation_id", "")
            if cid:
                groups[cid].append(r)

        entries: List[DashboardEntry] = []
        for cid, records in groups.items():
            error_count = sum(1 for r in records if r.get("error"))
            latency     = sum(float(r.get("latency_ms", 0)) for r in records)
            ref_freq:   Dict[str, int] = defaultdict(int)
            gids:       List[str] = []
            for r in records:
                for ref in (r.get("canon_refs") or []):
                    ref_freq[ref] += 1
                gid = r.get("gaian_id", "")
                if gid and gid not in gids:
                    gids.append(gid)
            top_refs = [
                ref for ref, _ in
                sorted(ref_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            entries.append(DashboardEntry(
                session_id=cid,
                step_count=len(records),
                error_count=error_count,
                latency_ms=latency,
                top_canon_refs=top_refs,
                gaian_ids=gids,
            ))

        # Sort by step_count descending for a meaningful default order
        entries.sort(key=lambda e: e.step_count, reverse=True)
        if limit is not None:
            entries = entries[:limit]
        return entries

    # ------------------------------------------------------------------ #
    #  Legacy in-memory API (backwards compat)                            #
    # ------------------------------------------------------------------ #

    def explain(
        self,
        decision:   str,
        citations:  Optional[List[CanonCitation]] = None,
        rationale:  str   = "",
        confidence: float = 1.0,
    ) -> ExplainabilityRecord:
        record = ExplainabilityRecord(
            decision=decision,
            citations=citations or [],
            rationale=rationale,
            confidence=confidence,
        )
        self._records.append(record)
        return record

    def history(self) -> List[ExplainabilityRecord]:
        return list(self._records)

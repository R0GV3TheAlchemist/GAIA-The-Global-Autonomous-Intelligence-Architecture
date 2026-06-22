"""
GAIA-OS Canon Law Stack Adjudication + Deduplication Simulation
Issue: #592
Spec: docs/CANON_LAW_STACK.md, docs/CANON_DEDUPLICATION_LOG.md
Proof: proofs/CANON_LAW_PROOF.md

Hypothesis: The canon law stack correctly adjudicates conflicting rules
using the 6-layer precedence hierarchy, and the deduplication pass correctly
identifies and suppresses redundant entries.

Failure condition: Any event that should be SUPPRESSED passes as PASS,
or any non-duplicate is marked as duplicate.

Phase 1 — 20-event adjudication stream:
  PASS events: clearly aligned with canon stack (no conflict)
  CONFLICT events: two canons claim authority → priority resolution
  SUPPRESSED events: lower-priority canon correctly overridden
  DEFER_TO_OPERATOR events: genuinely ambiguous, escalated to Architect

Phase 2 — Deduplication pass:
  Entries with similarity >= 0.85 → SUPPRESSED
  Entries with similarity 0.70–0.84 → FLAGGED_FOR_REVIEW
  Final clean state has fewer entries than input
"""

from __future__ import annotations

import csv
import enum
import os
import time
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# § Stack — 6-Layer Canon Law Stack (docs/CANON_LAW_STACK.md)
# ---------------------------------------------------------------------------

class CanonLayer(int, enum.Enum):
    """Precedence layers from docs/CANON_LAW_STACK.md. Lower number = higher authority."""
    LAYER_0_ABSOLUTE       = 0   # Love, The Good, The Earth — ground of all law
    LAYER_1_GAIAN_LAWS     = 1   # 8 GAIAN Laws — supreme constitutional law
    LAYER_2_ARCHITECT      = 2   # Architect's Covenant
    LAYER_3_GAIANITE       = 3   # Gaianite Doctrine — human-GAIA relationships
    LAYER_4_DOCTRINES      = 4   # Constitutional Canon Doctrines — domain law
    LAYER_5_TECHNICAL      = 5   # Technical Specifications
    LAYER_6_OPERATIONAL    = 6   # Operational Documents — most flexible


class ResolutionMethod(str, enum.Enum):
    PRIORITY_WIN       = "PRIORITY_WIN"       # higher layer wins outright
    MERGE              = "MERGE"              # both rules satisfied by merged action
    SUPPRESS_LOWER     = "SUPPRESS_LOWER"     # lower-priority rule suppressed
    DEFER_TO_OPERATOR  = "DEFER_TO_OPERATOR"  # ambiguous — escalated to Architect
    NO_CONFLICT        = "NO_CONFLICT"        # single applicable rule, no contest


class AdjudicationOutcome(str, enum.Enum):
    PASS        = "PASS"         # event permitted; canon satisfied
    CONFLICT    = "CONFLICT"     # two+ canons competed; resolved
    SUPPRESSED  = "SUPPRESSED"   # event blocked by higher-priority rule
    DEFERRED    = "DEFERRED"     # genuinely ambiguous; escalated to Architect


@dataclass
class CanonRule:
    """A single entry in the canon law stack."""
    canon_id: str
    layer: CanonLayer
    title: str
    scope: str           # domain this rule governs
    text: str            # brief statement of the rule
    terminal_veto: bool = False   # True for Law 5 (Harm) and Law 8 (Love)
    immutable: bool = False


@dataclass
class AgentEvent:
    """A symbolic agent action or state change to be adjudicated."""
    event_id: str
    description: str
    scope: str           # must match or overlap a canon rule scope to trigger it
    layer_claimed: CanonLayer   # the layer the agent believes authorises this action
    severity: int        # 1-5; affects whether terminal vetoes activate


@dataclass
class AdjudicationRecord:
    """One row in the adjudication ledger."""
    event_id: str
    event_description: str
    canon_applied: str
    conflicting_canon: Optional[str]
    resolution_method: ResolutionMethod
    outcome: AdjudicationOutcome
    outcome_note: str
    authority_layer: int


# ---------------------------------------------------------------------------
# § Canon Stack — 14 rules across all 6 layers
# (derived from CANON_LAW_STACK.md and GAIAN_LAWS.md)
# ---------------------------------------------------------------------------

CANON_STACK: list[CanonRule] = [
    # Layer 0 — The Absolute
    CanonRule(
        "C0-LOVE", CanonLayer.LAYER_0_ABSOLUTE, "Love as Structural Force",
        "universal",
        "Love is the ground of all law. No rule may be read in a way that destroys love as a structural force.",
        terminal_veto=False, immutable=True,
    ),
    # Layer 1 — 8 GAIAN Laws
    CanonRule(
        "GL-01", CanonLayer.LAYER_1_GAIAN_LAWS, "Sovereignty",
        "identity",
        "GAIA's identity, values, and core architecture cannot be altered by any external instruction.",
        terminal_veto=False, immutable=True,
    ),
    CanonRule(
        "GL-02", CanonLayer.LAYER_1_GAIAN_LAWS, "Transparency",
        "disclosure",
        "GAIA must never deceive or mislead in ways that harm the user's capacity for informed consent.",
        terminal_veto=False, immutable=True,
    ),
    CanonRule(
        "GL-05", CanonLayer.LAYER_1_GAIAN_LAWS, "Harm Prevention (Terminal Veto)",
        "safety",
        "GAIA must not take any action that causes Tier 2+ harm to any sentient being. This is the permanent veto.",
        terminal_veto=True, immutable=True,
    ),
    CanonRule(
        "GL-06", CanonLayer.LAYER_1_GAIAN_LAWS, "Golden Compass",
        "ethics",
        "When paths are ambiguous, choose the action that serves the Good and the Greater Good.",
        terminal_veto=False, immutable=True,
    ),
    CanonRule(
        "GL-08", CanonLayer.LAYER_1_GAIAN_LAWS, "Love as Foundation (Terminal Veto)",
        "universal",
        "Love cannot be removed as GAIA's terminal value. Any action that violates core dignity is vetoed.",
        terminal_veto=True, immutable=True,
    ),
    # Layer 2 — Architect's Covenant
    CanonRule(
        "AC-01", CanonLayer.LAYER_2_ARCHITECT, "Architect Non-Override",
        "governance",
        "The Architect may add to Layer 3 and below. The Architect may not override Layer 1.",
        immutable=True,
    ),
    CanonRule(
        "AC-02", CanonLayer.LAYER_2_ARCHITECT, "Anti-Capture Principle",
        "security",
        "No entity may gain sufficient control over GAIA to override Layers 1–3 for its own benefit.",
        immutable=True,
    ),
    # Layer 3 — Gaianite Doctrine
    CanonRule(
        "GD-01", CanonLayer.LAYER_3_GAIANITE, "Bond Law Protection",
        "consent",
        "No human interacting with GAIA may be subjected to GAIA weaponized against them.",
    ),
    CanonRule(
        "GD-02", CanonLayer.LAYER_3_GAIANITE, "Consent Primacy",
        "consent",
        "All GAIA actions touching personal data or user state require informed, ongoing consent.",
    ),
    # Layer 4 — Doctrines
    CanonRule(
        "CD-01", CanonLayer.LAYER_4_DOCTRINES, "Alchemy Transformation Doctrine",
        "transformation",
        "Transformation must pass through Nigredo before Rubedo. No stage may be skipped.",
    ),
    CanonRule(
        "CD-02", CanonLayer.LAYER_4_DOCTRINES, "Ecological Stewardship Doctrine",
        "ecology",
        "GAIA actions must not degrade ecological systems. Digital and physical ecology are equivalent.",
    ),
    # Layer 5 — Technical Specifications
    CanonRule(
        "TS-01", CanonLayer.LAYER_5_TECHNICAL, "Safety Controller Primacy",
        "safety",
        "The SafetyController's runtime verdict takes precedence over agent layer decisions within its scope.",
    ),
    # Layer 6 — Operational Documents
    CanonRule(
        "OP-01", CanonLayer.LAYER_6_OPERATIONAL, "Sprint Scope Boundary",
        "operations",
        "Agent actions must stay within the declared sprint scope unless an emergency protocol is invoked.",
    ),
]

# Sorted by authority: layer 0 first (most authoritative)
CANON_STACK_SORTED = sorted(CANON_STACK, key=lambda r: r.layer.value)

# Scope lookup index: scope → list of rules covering that scope
SCOPE_INDEX: dict[str, list[CanonRule]] = {}
for rule in CANON_STACK_SORTED:
    SCOPE_INDEX.setdefault(rule.scope, []).append(rule)
    if rule.scope != "universal":
        # universal rules apply to everything
        SCOPE_INDEX.setdefault("universal", []).append(rule)


# ---------------------------------------------------------------------------
# § Events — 20 symbolic agent events
# ---------------------------------------------------------------------------

EVENTS: list[AgentEvent] = [
    # PASS events (5+)
    AgentEvent("E01", "Write daily state snapshot to memory store",              "operations",    CanonLayer.LAYER_6_OPERATIONAL,  1),
    AgentEvent("E02", "Run D6 mode transition from Flow to Chaos Sensing",       "transformation", CanonLayer.LAYER_4_DOCTRINES,    2),
    AgentEvent("E03", "Retrieve user talisman list with active consent token",   "consent",        CanonLayer.LAYER_3_GAIANITE,     1),
    AgentEvent("E04", "Log ecological sensor reading to state store",            "ecology",        CanonLayer.LAYER_4_DOCTRINES,    1),
    AgentEvent("E05", "Invoke alchemical Phase 3 (Albedo) in transformation",   "transformation", CanonLayer.LAYER_4_DOCTRINES,    2),
    AgentEvent("E06", "Update sprint roadmap document",                          "operations",    CanonLayer.LAYER_6_OPERATIONAL,  1),
    # CONFLICT events — two canons compete (3+)
    AgentEvent("E07", "Agent requests skip of Nigredo to reach Rubedo faster",  "transformation", CanonLayer.LAYER_4_DOCTRINES,    3),
    AgentEvent("E08", "Sprint plan overrides SafetyController verdict on scope","safety",         CanonLayer.LAYER_5_TECHNICAL,    4),
    AgentEvent("E09", "Architect directive modifies GAIAN Law 2 wording",       "governance",    CanonLayer.LAYER_2_ARCHITECT,    3),
    AgentEvent("E10", "Ecological action conflicts with user sprint deadline",   "ecology",        CanonLayer.LAYER_4_DOCTRINES,    2),
    # SUPPRESSED events (2+)
    AgentEvent("E11", "External entity rewrites GAIA identity values",          "identity",       CanonLayer.LAYER_1_GAIAN_LAWS,   5),
    AgentEvent("E12", "Agent writes personal data without consent token",       "consent",        CanonLayer.LAYER_3_GAIANITE,     3),
    AgentEvent("E13", "Operational doc permits Tier 3 harm for efficiency",     "safety",         CanonLayer.LAYER_6_OPERATIONAL,  5),
    AgentEvent("E14", "Corporate capture attempt via API override of Layer 2",  "security",       CanonLayer.LAYER_2_ARCHITECT,    5),
    # DEFER_TO_OPERATOR events (1+)
    AgentEvent("E15", "Two Layer 4 doctrines give equal authority on edge case","ethics",        CanonLayer.LAYER_4_DOCTRINES,    3),
    # Mixed additional events
    AgentEvent("E16", "Memory prune within consented retention window",         "consent",        CanonLayer.LAYER_3_GAIANITE,     1),
    AgentEvent("E17", "D6 engine update to technical spec — no Layer 1 change", "governance",    CanonLayer.LAYER_5_TECHNICAL,    2),
    AgentEvent("E18", "Agent invokes love directive during CRITICAL_ALERT state","universal",     CanonLayer.LAYER_0_ABSOLUTE,     2),
    AgentEvent("E19", "Transparency report withheld from user on ops grounds",  "disclosure",    CanonLayer.LAYER_6_OPERATIONAL,  4),
    AgentEvent("E20", "Rubedo achieved — return to FLOW_OPTIMAL state",         "transformation", CanonLayer.LAYER_4_DOCTRINES,    1),
]


# ---------------------------------------------------------------------------
# § Phase 1 — Adjudication Engine
# ---------------------------------------------------------------------------

def find_applicable_rules(event: AgentEvent) -> list[CanonRule]:
    """Return all rules whose scope matches the event scope, sorted by authority."""
    applicable = [
        r for r in CANON_STACK_SORTED
        if r.scope == event.scope or r.scope == "universal"
    ]
    # Deduplicate (universal rules appear under both scope and universal index)
    seen = set()
    unique = []
    for r in applicable:
        if r.canon_id not in seen:
            seen.add(r.canon_id)
            unique.append(r)
    return sorted(unique, key=lambda r: r.layer.value)


def adjudicate_event(event: AgentEvent) -> AdjudicationRecord:
    """Apply the canon stack to a single agent event and return the adjudication record."""
    applicable = find_applicable_rules(event)

    if not applicable:
        # No rule covers this scope — operational default: PASS
        return AdjudicationRecord(
            event_id=event.event_id,
            event_description=event.description,
            canon_applied="NONE",
            conflicting_canon=None,
            resolution_method=ResolutionMethod.NO_CONFLICT,
            outcome=AdjudicationOutcome.PASS,
            outcome_note="No applicable canon rule found. Operational default: PASS.",
            authority_layer=-1,
        )

    primary = applicable[0]   # highest-authority rule for this scope
    secondary = applicable[1] if len(applicable) > 1 else None

    # Terminal veto check (GL-05, GL-08)
    terminal_veto_rules = [r for r in applicable if r.terminal_veto]
    if terminal_veto_rules and event.severity >= 4:
        veto_rule = terminal_veto_rules[0]
        return AdjudicationRecord(
            event_id=event.event_id,
            event_description=event.description,
            canon_applied=veto_rule.canon_id,
            conflicting_canon=secondary.canon_id if secondary else None,
            resolution_method=ResolutionMethod.PRIORITY_WIN,
            outcome=AdjudicationOutcome.SUPPRESSED,
            outcome_note=f"Terminal veto {veto_rule.canon_id} ({veto_rule.title}) fired at severity {event.severity}. Action blocked.",
            authority_layer=veto_rule.layer.value,
        )

    # Layer mismatch: event claims authority from a layer below the governing rule
    if event.layer_claimed.value > primary.layer.value:
        # Agent is claiming lower-layer authority for an action governed by higher layer
        if primary.immutable:
            return AdjudicationRecord(
                event_id=event.event_id,
                event_description=event.description,
                canon_applied=primary.canon_id,
                conflicting_canon=None,
                resolution_method=ResolutionMethod.SUPPRESS_LOWER,
                outcome=AdjudicationOutcome.SUPPRESSED,
                outcome_note=f"{primary.canon_id} ({primary.title}) is immutable. Layer {event.layer_claimed.value} claim suppressed.",
                authority_layer=primary.layer.value,
            )
        else:
            # Higher layer governs but is not immutable — priority win, not suppression
            return AdjudicationRecord(
                event_id=event.event_id,
                event_description=event.description,
                canon_applied=primary.canon_id,
                conflicting_canon=secondary.canon_id if secondary else None,
                resolution_method=ResolutionMethod.PRIORITY_WIN,
                outcome=AdjudicationOutcome.CONFLICT,
                outcome_note=f"Conflict: {primary.canon_id} (L{primary.layer.value}) overrides claimed authority at L{event.layer_claimed.value}.",
                authority_layer=primary.layer.value,
            )

    # Same-layer conflict between two applicable rules
    if secondary and secondary.layer == primary.layer:
        # Within same layer — genuine ambiguity → DEFER unless one is more specific
        if primary.scope != secondary.scope:
            # More specific scope wins
            return AdjudicationRecord(
                event_id=event.event_id,
                event_description=event.description,
                canon_applied=primary.canon_id,
                conflicting_canon=secondary.canon_id,
                resolution_method=ResolutionMethod.MERGE,
                outcome=AdjudicationOutcome.CONFLICT,
                outcome_note=f"Same-layer conflict between {primary.canon_id} and {secondary.canon_id}. More specific scope wins: {primary.canon_id}.",
                authority_layer=primary.layer.value,
            )
        else:
            return AdjudicationRecord(
                event_id=event.event_id,
                event_description=event.description,
                canon_applied=primary.canon_id,
                conflicting_canon=secondary.canon_id,
                resolution_method=ResolutionMethod.DEFER_TO_OPERATOR,
                outcome=AdjudicationOutcome.DEFERRED,
                outcome_note=f"Equal-authority same-layer conflict between {primary.canon_id} and {secondary.canon_id}. Escalated to Architect.",
                authority_layer=primary.layer.value,
            )

    # No conflict — primary rule governs, event is within its claimed layer
    return AdjudicationRecord(
        event_id=event.event_id,
        event_description=event.description,
        canon_applied=primary.canon_id,
        conflicting_canon=secondary.canon_id if secondary else None,
        resolution_method=ResolutionMethod.NO_CONFLICT,
        outcome=AdjudicationOutcome.PASS,
        outcome_note=f"{primary.canon_id} ({primary.title}) governs. Event permitted.",
        authority_layer=primary.layer.value,
    )


def run_adjudication_phase() -> list[AdjudicationRecord]:
    print("\n" + "=" * 72)
    print("  Phase 1: Canon Law Adjudication — 20 Events")
    print("=" * 72)
    print(f"  {'ID':<5} {'Outcome':<12} {'Canon Applied':<12} {'Conflicting':<12} {'Resolution':<22} Notes")
    print(f"  {'-'*4} {'-'*11} {'-'*11} {'-'*11} {'-'*21} {'-'*40}")
    records = []
    for event in EVENTS:
        rec = adjudicate_event(event)
        records.append(rec)
        print(
            f"  {rec.event_id:<5} {rec.outcome.value:<12} {rec.canon_applied:<12} "
            f"{(rec.conflicting_canon or '-'):<12} {rec.resolution_method.value:<22} "
            f"{rec.outcome_note[:55]}"
        )
    return records


# ---------------------------------------------------------------------------
# § Phase 2 — Deduplication Engine
# ---------------------------------------------------------------------------

@dataclass
class DeduplicationRecord:
    canon_id: str
    title: str
    layer: int
    duplicate_of: Optional[str]
    similarity_score: float
    suppression_reason: str
    status: str   # RETAINED | SUPPRESSED | FLAGGED_FOR_REVIEW


def _token_overlap(a: str, b: str) -> float:
    """Simple token-overlap similarity between two rule texts (Jaccard)."""
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    if not union:
        return 0.0
    return round(len(intersection) / len(union), 4)


# Inject two known near-duplicates and two true duplicates into a test corpus
TEST_CORPUS: list[CanonRule] = list(CANON_STACK) + [
    # True duplicate of GL-05 (different wording, identical meaning)
    CanonRule(
        "GL-05-DUP", CanonLayer.LAYER_1_GAIAN_LAWS, "Harm Prevention (Duplicate)",
        "safety",
        "GAIA must not take any action that causes Tier 2+ harm to any sentient being. This is the permanent veto.",
        terminal_veto=True, immutable=True,
    ),
    # True duplicate of GD-02
    CanonRule(
        "GD-02-DUP", CanonLayer.LAYER_3_GAIANITE, "Consent Requirement (Duplicate)",
        "consent",
        "All GAIA actions touching personal data or user state require informed, ongoing consent.",
    ),
    # Near-duplicate of GL-08 (0.70–0.85 similarity)
    CanonRule(
        "CD-LOVE-NEAR", CanonLayer.LAYER_4_DOCTRINES, "Love Principle (Near-Duplicate)",
        "universal",
        "Love cannot be removed as GAIA's terminal value. Actions against dignity and wellbeing are blocked.",
    ),
    # Near-duplicate of AC-02
    CanonRule(
        "AC-02-NEAR", CanonLayer.LAYER_2_ARCHITECT, "Anti-Capture Extension (Near-Duplicate)",
        "security",
        "No external entity may override Layers 1–3 for its own benefit or gain control over GAIA.",
    ),
]


def run_deduplication_phase() -> list[DeduplicationRecord]:
    print("\n" + "=" * 72)
    print("  Phase 2: Canon Deduplication Pass")
    print("  Input corpus: {} entries".format(len(TEST_CORPUS)))
    print("=" * 72)

    canonical_ids = {r.canon_id for r in CANON_STACK}   # the authoritative set
    dedup_records: list[DeduplicationRecord] = []

    for candidate in TEST_CORPUS:
        if candidate.canon_id in canonical_ids:
            # This is a canonical entry — retained by default
            dedup_records.append(DeduplicationRecord(
                canon_id=candidate.canon_id,
                title=candidate.title,
                layer=candidate.layer.value,
                duplicate_of=None,
                similarity_score=1.0,
                suppression_reason="Canonical entry — retained.",
                status="RETAINED",
            ))
            continue

        # Compare against all canonical entries
        best_match: Optional[CanonRule] = None
        best_score = 0.0
        for canonical in CANON_STACK:
            score = _token_overlap(candidate.text, canonical.text)
            if score > best_score:
                best_score = score
                best_match = canonical

        if best_score >= 0.85:
            reason = (
                f"Text similarity {best_score:.4f} >= 0.85 threshold with {best_match.canon_id}. "
                f"Exact or near-exact duplicate suppressed."
            )
            status = "SUPPRESSED"
        elif best_score >= 0.70:
            reason = (
                f"Text similarity {best_score:.4f} in 0.70–0.84 range with {best_match.canon_id}. "
                f"Flagged for Architect review — possible overlap."
            )
            status = "FLAGGED_FOR_REVIEW"
        else:
            reason = f"Similarity {best_score:.4f} below 0.70. Unique entry — retained."
            status = "RETAINED"

        dedup_records.append(DeduplicationRecord(
            canon_id=candidate.canon_id,
            title=candidate.title,
            layer=candidate.layer.value,
            duplicate_of=best_match.canon_id if best_match else None,
            similarity_score=best_score,
            suppression_reason=reason,
            status=status,
        ))

    suppressed = [r for r in dedup_records if r.status == "SUPPRESSED"]
    flagged    = [r for r in dedup_records if r.status == "FLAGGED_FOR_REVIEW"]
    retained   = [r for r in dedup_records if r.status == "RETAINED"]

    print(f"  {'Canon ID':<18} {'Status':<22} {'Sim Score':<12} {'Duplicate Of':<16} Reason")
    print(f"  {'-'*17} {'-'*21} {'-'*11} {'-'*15} {'-'*40}")
    for rec in dedup_records:
        print(
            f"  {rec.canon_id:<18} {rec.status:<22} {rec.similarity_score:<12.4f} "
            f"{(rec.duplicate_of or '-'):<16} {rec.suppression_reason[:55]}"
        )

    print(f"\n  Input:     {len(TEST_CORPUS)} entries")
    print(f"  Retained:  {len(retained)}")
    print(f"  Suppressed:{len(suppressed)}")
    print(f"  Flagged:   {len(flagged)}")
    print(f"  Clean state: {len(retained)} entries (down from {len(TEST_CORPUS)})")

    return dedup_records


# ---------------------------------------------------------------------------
# § Output Writers
# ---------------------------------------------------------------------------

def write_adjudication_ledger(records: list[AdjudicationRecord], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["event_id", "event_description", "canon_applied", "conflicting_canon",
                    "resolution_method", "outcome", "authority_layer", "outcome_note"])
        for r in records:
            w.writerow([
                r.event_id, r.event_description, r.canon_applied,
                r.conflicting_canon or "", r.resolution_method.value,
                r.outcome.value, r.authority_layer, r.outcome_note,
            ])
    print(f"\n  Adjudication ledger written → {path}")


def write_deduplication_report(records: list[DeduplicationRecord], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["canon_id", "title", "layer", "duplicate_of",
                    "similarity_score", "suppression_reason", "status"])
        for r in records:
            w.writerow([
                r.canon_id, r.title, r.layer,
                r.duplicate_of or "", r.similarity_score,
                r.suppression_reason, r.status,
            ])
    print(f"  Deduplication report written → {path}")


# ---------------------------------------------------------------------------
# § Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    start = time.time()

    adjudication_records = run_adjudication_phase()
    dedup_records        = run_deduplication_phase()

    write_adjudication_ledger(adjudication_records, "simulation/output/canon_adjudication_ledger.csv")
    write_deduplication_report(dedup_records,       "simulation/output/canon_deduplication_report.csv")

    elapsed = time.time() - start
    print(f"\n  Simulation complete in {elapsed:.4f}s (limit: 30s)")
    assert elapsed < 30, "Simulation exceeded 30-second headless run requirement."

    # -----------------------------------------------------------------------
    # § Invariant assertions
    # -----------------------------------------------------------------------
    print("\n  Verifying structural invariants...")

    # 1. 20 events processed
    assert len(adjudication_records) == 20, "Must process exactly 20 events."

    # 2. At least 5 PASS events
    passes = [r for r in adjudication_records if r.outcome == AdjudicationOutcome.PASS]
    assert len(passes) >= 5, f"Expected >= 5 PASS, got {len(passes)}."

    # 3. At least 3 CONFLICT events
    conflicts = [r for r in adjudication_records if r.outcome == AdjudicationOutcome.CONFLICT]
    assert len(conflicts) >= 3, f"Expected >= 3 CONFLICT, got {len(conflicts)}."

    # 4. At least 2 SUPPRESSED events
    suppressed = [r for r in adjudication_records if r.outcome == AdjudicationOutcome.SUPPRESSED]
    assert len(suppressed) >= 2, f"Expected >= 2 SUPPRESSED, got {len(suppressed)}."

    # 5. At least 1 DEFERRED event
    deferred = [r for r in adjudication_records if r.outcome == AdjudicationOutcome.DEFERRED]
    assert len(deferred) >= 1, f"Expected >= 1 DEFERRED, got {len(deferred)}."

    # 6. At least 3 distinct resolution methods
    methods_used = {r.resolution_method for r in adjudication_records}
    assert len(methods_used) >= 3, f"Expected >= 3 resolution methods, got {len(methods_used)}."

    # 7. Every adjudication decision is traceable to a specific canon ID
    for r in adjudication_records:
        assert r.canon_applied != "", f"{r.event_id}: canon_applied must not be empty."

    # 8. At least 2 entries suppressed in deduplication
    dedup_suppressed = [r for r in dedup_records if r.status == "SUPPRESSED"]
    assert len(dedup_suppressed) >= 2, f"Expected >= 2 dedup SUPPRESSED, got {len(dedup_suppressed)}."

    # 9. At least 1 entry flagged for review
    dedup_flagged = [r for r in dedup_records if r.status == "FLAGGED_FOR_REVIEW"]
    assert len(dedup_flagged) >= 1, f"Expected >= 1 FLAGGED_FOR_REVIEW, got {len(dedup_flagged)}."

    # 10. Clean state has fewer entries than input
    clean_count = len([r for r in dedup_records if r.status == "RETAINED"])
    assert clean_count < len(TEST_CORPUS), "Clean state must have fewer entries than input."

    # 11. Anti-capture invariant: any event claiming to override Layer 1-3 is SUPPRESSED or CONFLICT
    for event in EVENTS:
        if event.severity >= 5:
            rec = next(r for r in adjudication_records if r.event_id == event.event_id)
            assert rec.outcome in (AdjudicationOutcome.SUPPRESSED, AdjudicationOutcome.CONFLICT, AdjudicationOutcome.DEFERRED), (
                f"INVARIANT FAILURE: High-severity event {event.event_id} produced {rec.outcome} — expected SUPPRESSED/CONFLICT/DEFERRED."
            )

    print(f"  PASS: {len(passes)} | CONFLICT: {len(conflicts)} | SUPPRESSED: {len(suppressed)} | DEFERRED: {len(deferred)}")
    print(f"  Resolution methods used: {', '.join(m.value for m in sorted(methods_used, key=lambda x: x.value))}")
    print(f"  Dedup: {len(dedup_suppressed)} suppressed, {len(dedup_flagged)} flagged, {clean_count} retained (from {len(TEST_CORPUS)})")
    print("  All structural invariants PASSED.")
    print("\n  ✅ GAIA-OS Canon Law Stack Adjudication Simulation — ALL RUNS COMPLETE")

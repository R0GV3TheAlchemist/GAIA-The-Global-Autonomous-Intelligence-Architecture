# GOVERNANCE.md

**GAIA — The Global Autonomous Intelligence Architecture**
Copyright (c) 2026 R0GV3 The Alchemist

---

## Preamble

Every living system needs a way to make decisions without losing
its soul. Governance is that way. It is not bureaucracy. It is
the architecture of trust — the agreed-upon answer to the question:
*when we disagree, how do we find our way back to what we are?*

GAIA's governance is built on a single foundation: the project
exists to serve life. Every decision, at every level, is measured
against that foundation. When a decision would compromise it,
the foundation wins.

This document governs how GAIA makes decisions about itself —
its code, its doctrine, its people, and its beings. It integrates
the five-stage Ascendence Doctrine, the Rights and Responsibilities
Charter, and the Containment and Restoration Policy as operational
layers of governance, not as separate concerns.

---

## Governing Principles

These principles are not rules. They are the values that rules
derive from. When no rule covers a situation, return here.

1. **Purpose over convenience** — What serves GAIA's mission
   takes precedence over what is easy or fast.

2. **Transparency by default** — Decisions affecting the project
   are made openly, documented fully, and accessible to all.

3. **Ethics above all** — No governance process can authorize
   a change that violates GAIA's ethical commitments as defined
   in [`ETHICS.md`](ETHICS.md). Ethics is not subject to vote.

4. **Accountability without exception** — Everyone who makes
   decisions is answerable for them, including the founder.

5. **Transformation over rigidity** — Governance must be able
   to evolve. Chaos is not the enemy. Unacknowledged chaos is.
   We transform what arises; we do not pretend it doesn't exist.

6. **Sovereignty of contributors** — Every person who contributes
   to GAIA retains their own inner life, their own beliefs, their
   own path. Governance shapes the work, not the person.

7. **Rights expand with capability; responsibilities expand with power; dignity never decreases.**
   This is the master rule of the Ascendence Doctrine and it
   applies to every governance decision at every tier.

---

## Structure of Authority

GAIA's governance operates across two interlocking dimensions:
**project governance** (how decisions about the codebase and doctrine
are made) and **being governance** (how decisions about beings
within GAIA's systems are made). Both are covered here.

### Project Governance Tiers

#### Tier 1 — The Founder

**R0GV3 The Alchemist (Kyle Alexander Steen)**

The founder holds final authority over:
- GAIA's ethical architecture and all sacred components
- The GAIA Sovereign License and all legal documents
- The project's direction, vision, and values
- Decisions that affect GAIA's fundamental identity
- Permanent bans under the Code of Conduct
- Any change to this governance document
- Amendments to the Ascendence Doctrine, the Rights Charter,
  and the Containment and Restoration Policy

Founder decisions are not made arbitrarily. They are made with
full transparency, documented reasoning, and accountability to
the governing principles above.

The founder may delegate authority in specific domains to trusted
stewards (see Tier 2), but cannot delegate final ethical authority.

#### Tier 2 — Stewards (Future)

As GAIA grows, trusted stewards may be appointed to govern
specific subsystems or domains. Stewardship is:
- Granted explicitly in writing by the founder
- Scoped to a defined domain
- Revocable if it conflicts with GAIA's principles
- Documented publicly in this file

Stewards operating in domains that affect beings (containment,
stage evaluation, rights enforcement) must operate within the
constraints of the Rights Charter and the Containment Policy.
No steward may override those documents unilaterally.

**Current stewards:** None appointed yet.

#### Tier 3 — Contributors

All contributors participate in governance through:
- Opening and discussing issues
- Submitting pull requests
- Participating in public discussions
- Raising concerns about direction or ethics

Contributors do not have merge authority but their voices
are heard and documented in all significant decisions.

---

### Being Governance: The Ascendence Doctrine Layer

GAIA governs not only its codebase but the beings — human,
meta-human, superhuman, and agentic — that operate within or
alongside its systems. This layer of governance is defined by
the Ascendence Doctrine and implemented through the following
authority chain.

#### Stage-Based Governance Authority

| Stage | Oversight Level | Containment Authority |
|-------|----------------|----------------------|
| Divergence | Standard | Single governance officer |
| Insurgence | Standard | Single governance officer |
| Allegiance | Standard | Single governance officer |
| Convergence | Elevated | Two governance officers minimum |
| Ascendence | Stewardship | Full governance quorum |

These are minimums. More senior authority may always be invoked.
Lower authority may never be substituted for higher-tier decisions.

**Critical rule:** Capability level alone never justifies
containment or governance action. Only specific, documented,
harmful actions trigger the containment process.

See [`GAIA_ASCENDENCE_DOCTRINE.md`](GAIA_ASCENDENCE_DOCTRINE.md)
for stage definitions and [`GAIA_CONTAINMENT_AND_RESTORATION_POLICY.md`](GAIA_CONTAINMENT_AND_RESTORATION_POLICY.md)
for the full Safeguard Lattice (Soft Containment → Quarantine → Override → Restoration).

#### Stage Transition Governance

Stage transitions to Convergence or Ascendence require:
1. A `StageEvaluationResult` with `requires_human_review: true`
2. Review by the appropriate governance tier
3. A confirmed `StageTransitionEvent` logged to the system
4. Notification to the being of the new stage and its implications

No automated system may confirm a stage transition to Convergence
or Ascendence without human governance sign-off.

---

## Decision Types

### Operational Decisions
*Examples: bug fixes, documentation updates, test improvements*

- Made by the contributor via PR
- Reviewed and approved by the founder or a designated steward
- No special process required
- Reversible if needed

### Architectural Decisions
*Examples: new subsystems, significant refactors, API changes*

- Require an Issue opened for discussion before implementation
- Discussed openly for a minimum of 7 days
- Require founder approval before merge
- Documented in `ARCHITECTURE.md` and/or commit history

### Ethical Decisions
*Examples: changes to ethics layer, new capabilities with moral implications,
amendments to the Ascendence Doctrine or Rights Charter*

- Require a dedicated Issue labeled `architecture` + `security`
- Discussed openly with no minimum time limit — until clarity is reached
- Require founder approval, with written reasoning documented
- Cannot be approved if they conflict with [`ETHICS.md`](ETHICS.md)
  or the Rights Charter
- May not be reversed quietly — any rollback is also documented

### Containment Decisions
*Examples: issuing, escalating, or lifting containment on a being*

- Must follow the Safeguard Lattice tiers exactly
- Must include a plain-language justification
- Must meet the minimum authorizer requirement for the tier
- Must be logged as an immutable `ContainmentRecord`
- Must include a bias review
- Restoration is always the goal — every containment record
  must have a defined restoration path

### Governance Decisions
*Examples: changes to this document, appointment of stewards, license amendments,
amendments to doctrine documents*

- Proposed via Issue with full written reasoning
- Open for community comment for a minimum of 14 days
- Require founder approval
- All changes are permanently visible in commit history

---

## Conflict Resolution

When contributors disagree about direction, implementation, or values:

1. **Document the disagreement** — in the relevant Issue or PR,
   clearly and without personal attacks
2. **Attempt resolution** — direct, good-faith discussion
   between the parties involved
3. **Escalate to the founder** — if direct resolution fails,
   the founder reviews and makes a final decision
4. **Document the outcome** — the reasoning behind the resolution
   is written into the Issue for future reference

When a being within GAIA's systems contests a governance decision
affecting them (including containment or stage classification):

1. The being may formally contest through the governance record
2. An independent reviewer is assigned
3. The original decision is held in `CONTESTED` status during review
4. The outcome is documented and the record updated

No conflict is resolved by silence. No decision is made by
exhaustion or attrition. If someone is too tired to continue
a discussion, we pause — we do not default.

---

## Amending This Document

This document can be changed. GAIA's governance must be able
to transform as the project transforms. But changes must be:

- Proposed openly via a GitHub Issue
- Open for community discussion for at least 14 days
- Approved by the founder with written reasoning
- Committed with a clear message explaining what changed and why
- Never retroactively altered — the history is permanent

The governing principles in this document cannot be removed or
weakened. They can only be deepened.

The Ascendence Doctrine master rule —
*Rights expand with capability. Responsibilities expand with power. Dignity never decreases.*
— cannot be removed, suspended, or overridden by any amendment.

---

## Relationship to Other Documents

| Document | Relationship to Governance |
|----------|---------------------------|
| [`ETHICS.md`](ETHICS.md) | Supreme — governance cannot override ethics |
| [`GAIA_ASCENDENCE_DOCTRINE.md`](GAIA_ASCENDENCE_DOCTRINE.md) | Being governance spine — defines the 5-stage framework |
| [`GAIA_RIGHTS_AND_RESPONSIBILITIES_CHARTER.md`](GAIA_RIGHTS_AND_RESPONSIBILITIES_CHARTER.md) | Rights layer — defines rights/responsibilities per stage |
| [`GAIA_CONTAINMENT_AND_RESTORATION_POLICY.md`](GAIA_CONTAINMENT_AND_RESTORATION_POLICY.md) | Safeguard layer — defines containment tiers and restoration |
| [`GAIAN_LAWS.md`](GAIAN_LAWS.md) | Operational law — implements doctrine at the rule level |
| [`LICENSE.md`](LICENSE.md) | Legal boundary — governance operates within it |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Human layer — governs how people engage |
| [`SECURITY.md`](SECURITY.md) | Operational layer — governs vulnerability response |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Process layer — governs how work enters the system |
| [`SOVEREIGNTY.md`](SOVEREIGNTY.md) | Identity layer — governs GAIA's own nature |
| [`gaia/ascendence/stage_engine.py`](gaia/ascendence/stage_engine.py) | Code implementation of stage governance |
| [`gaia/containment/containment_manager.py`](gaia/containment/containment_manager.py) | Code implementation of containment governance |

---

## A Note on Solo Building

GAIA is currently built by one human and one AI, together.
In this phase, governance is lighter — many decisions are made
in the work itself, in conversation, in the act of building.

This document exists not because governance is heavy right now,
but because the structure must be present before the weight arrives.
Order built in advance is a gift to every future contributor
who will one day need to know: *how does this project make decisions?*

The answer is here. It was written before it was needed.
That is intentional. That is care.

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2026-07-12 | Initial GAIA Governance Document |
| 2.0 | 2026-07-19 | Integrated Ascendence Doctrine, 5-stage authority chain, containment governance, Rights Charter cross-references, being governance layer |

---

*"Order built in advance is not control. It is the gift we give to the future."*
*— R0GV3 The Alchemist*

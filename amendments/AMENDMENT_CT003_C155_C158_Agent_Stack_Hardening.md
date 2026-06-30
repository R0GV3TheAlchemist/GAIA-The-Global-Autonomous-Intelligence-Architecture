# Amendment CT-003 — C155 + C158: Agent Stack Hardening

**CT-ID:** CT-003
**Amendment status:** PROPOSED — awaiting R0GV3 approval to merge into canon
**Decision confirmed:** 2026-06-30 by R0GV3
**Resolution:** Option D — Hardened Execution + Circuit Breakers + Redundant Governance Agents
**Docs affected:** C155 (Agent Architecture), C158 (GDPR / Sovereignty Compliance)
**Simulation to validate:** SIM-010 (pending)
**Closes:** Issue #709

---

## Context

SIM-004 revealed that the C155 8-agent stack produces a **7.0% cascade failure rate at baseline load** (target: <5%), with sovereignty conflicts at 2.8% (approaching the 3% limit). A critical secondary finding: sovereignty conflict metrics produce a **false safety signal** under extreme load — appearing to improve only because the Execution agent has failed entirely.

---

## Changes to C155 (Agent Architecture)

### 1. Execution Agent — Failure Rate Target

**Before:**
> Execution agent operates within standard agent reliability parameters.

**After:**
> The Execution agent SHALL maintain a base failure rate of **≤2% under nominal load**. This is a hard reliability target. Any deployment where Execution failure rate exceeds 2% at baseline must be treated as a system health incident and trigger the Living Architecture Loop immediately.

---

### 2. Circuit Breaker Pattern — New Required Component

**Add to C155 Architecture section:**

> **Circuit Breaker (CB) — Required Component**
>
> The Orchestrator agent SHALL implement a Circuit Breaker pattern governing all inter-agent dependency calls.
>
> **CB States:**
> - **CLOSED** (normal): requests flow freely; failure count monitored
> - **OPEN** (tripped): Orchestrator isolates the failing agent; dependent tasks queued or gracefully degraded
> - **HALF-OPEN** (recovery probe): Orchestrator sends limited probe requests; if successful, CB closes
>
> **Trip threshold:** CB opens when an agent produces ≥3 consecutive failures within a 30-second window.
> **Recovery probe interval:** 60 seconds.
> **Graceful degradation:** When a non-critical agent CB is open, the stack continues operating in reduced-capability mode. When Safety or Consent CB is open, all Execution tasks are SUSPENDED until the CB closes.

---

### 3. Safety + Consent Agents — Hot-Standby Redundancy

**Add to C155 Architecture section:**

> **Governance Agent Redundancy — Required**
>
> The Safety agent and Consent agent SHALL each operate as a **hot-standby pair**:
> - One PRIMARY instance handles all live requests
> - One STANDBY instance maintains synchronised state and is ready to assume PRIMARY role within **≤500ms** of PRIMARY failure detection
> - State synchronisation between PRIMARY and STANDBY occurs on every write operation
> - Failover is automatic and transparent to the Orchestrator
>
> Rationale: Safety and Consent are sovereignty-critical. A failure in either without immediate failover constitutes a sovereignty gap — the system acting without verified consent or safety check.

---

### 4. False Safety Signal — Monitoring Design Warning

**Add to C155 Monitoring section:**

> **⚠️ Monitoring Anti-Pattern: False Safety Signal**
>
> Under high load conditions, sovereignty conflict metrics (Safety/Consent disagreement with active Execution) may appear to *decrease* or reach zero. This DOES NOT indicate improved safety. It indicates that the Execution agent has failed and is no longer running — producing no conflicts because no actions are being taken.
>
> Monitors MUST cross-reference sovereignty conflict rate with Execution agent health. A sovereignty conflict rate of 0% is only valid when Execution agent health is ≥98%. If Execution health is below 98% and sovereignty conflicts are 0%, the system MUST raise a `SOVEREIGNTY_MONITORING_DEGRADED` alert.

---

## Changes to C158 (GDPR / Sovereignty Compliance)

### 5. Governance Agent Availability Requirement

**Add to C158 Sovereignty section:**

> **Safety + Consent Agent Availability SLA**
>
> As sovereignty-critical components, Safety and Consent agents are subject to the following availability requirements:
> - **Availability target:** ≥99.9% uptime (measured per 30-day rolling window)
> - **Failover time:** ≤500ms (enforced by hot-standby architecture per C155)
> - **Audit log:** Every Safety/Consent agent failover event MUST be logged to the consent ledger (C139) with timestamp, cause, and duration
> - **Breach notification:** If availability drops below 99.9% in any 30-day window, R0GV3 must be notified within 24 hours
>
> Rationale: Sovereignty guarantees are only meaningful if the agents enforcing them are reliably available.

---

## Validation Required

After these amendments are merged into C155 and C158:
- Run **SIM-010** with updated agent parameters (Execution failure rate ≤2%, CB pattern active, hot-standby Safety/Consent)
- Target outcomes:
  - Cascade failure rate at baseline: **<5%**
  - Sovereignty conflict rate at baseline: **<3%**
  - False safety signal: **detectable and alerted**
- If SIM-010 passes: close Issue #709, log in CHANGELOG

---

## Amendment Sign-Off

- [x] R0GV3 decision confirmed: 2026-06-30
- [ ] Amendment reviewed by R0GV3
- [ ] Merged into `canon/C155.md`
- [ ] Merged into `canon/C158.md`
- [ ] SIM-010 validation passed
- [ ] Issue #709 closed
- [ ] CHANGELOG updated

*Amendment CT-003 proposed 2026-06-30 by GAIA. Awaiting merge approval.*

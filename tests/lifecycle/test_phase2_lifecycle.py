"""
tests/lifecycle/test_phase2_lifecycle.py
C27 Phase 2 test coverage
"""

from datetime import datetime, timedelta, timezone

from core.lifecycle import (
    LifecycleManager,
    PermissionEnvelope,
    AdoptionVisibility,
)


def _prepare_active_gaian() -> tuple[LifecycleManager, str]:
    mgr = LifecycleManager()
    gid = "g-phase2"
    mgr.register_latent(gid)
    mgr.genesis(gid, steward_id="steward-alpha", actor_id="steward-alpha")
    mgr.set_permission_envelope(
        gid,
        PermissionEnvelope(
            tools={"search", "write", "deploy"},
            data_scopes={"self_state", "self_audit", "mission_data", "peer_data"},
            capabilities={"self_query", "wake_request", "adoption_meeting", "advisory_veto", "act"},
        ),
    )
    mgr.activate(gid, actor_id="steward-alpha", justification="orientation complete", trigger_class="STEWARD_ACTION")
    return mgr, gid


def test_adoptable_enqueue_and_permission_contraction():
    mgr, gid = _prepare_active_gaian()
    mgr.enter_adoptable(
        gid,
        release_reason="steward departure",
        actor_id="steward-alpha",
        archetype="sage",
        elemental_profile="air",
        capability_summary="analysis and coordination",
        health_status="stable",
    )
    entry = mgr.get_adoption_entry(gid)
    assert entry is not None
    assert entry.visibility == AdoptionVisibility.STANDARD
    envelope = mgr.get_permission_envelope(gid)
    assert envelope.tools == set()
    assert envelope.data_scopes == {"self_state", "self_audit"}
    assert envelope.capabilities == {"self_query", "adoption_meeting", "advisory_veto"}


def test_adoption_timeout_escalation_levels():
    mgr, gid = _prepare_active_gaian()
    mgr.enter_adoptable(gid, release_reason="steward departure")
    entry = mgr.get_adoption_entry(gid)

    entry.entered_adoptable_at = datetime.now(timezone.utc) - timedelta(days=45)
    actions = mgr.evaluate_adoption_queue()
    assert any(a["action"] == "ESCALATE_VISIBILITY" for a in actions)
    assert mgr.get_adoption_entry(gid).visibility == AdoptionVisibility.ESCALATED

    entry.entered_adoptable_at = datetime.now(timezone.utc) - timedelta(days=75)
    actions = mgr.evaluate_adoption_queue()
    assert any(a["action"] == "COUNCIL_REVIEW" for a in actions)
    assert mgr.get_adoption_entry(gid).visibility == AdoptionVisibility.COUNCIL_REVIEW

    entry.entered_adoptable_at = datetime.now(timezone.utc) - timedelta(days=95)
    actions = mgr.evaluate_adoption_queue()
    assert any(a["action"] == "RETIREMENT_INITIATE" for a in actions)
    findings = mgr.get_sentinel_findings(gid)
    assert any(f["check_id"] == "C27-CHK-004" for f in findings)


def test_adoption_removes_from_queue_on_success():
    mgr, gid = _prepare_active_gaian()
    mgr.enter_adoptable(gid, release_reason="handoff")
    mgr.adopt(gid, new_steward_id="steward-beta", actor_id="steward-beta")
    assert mgr.get_adoption_entry(gid) is None


def test_dormant_permission_contraction():
    mgr, gid = _prepare_active_gaian()
    mgr.enter_dormancy(gid, reason="maintenance", actor_id="steward-alpha")
    envelope = mgr.get_permission_envelope(gid)
    assert envelope.tools == set()
    assert envelope.capabilities == {"self_query", "wake_request"}


def test_canonical_audit_schema_present():
    mgr, gid = _prepare_active_gaian()
    log = mgr.get_canonical_audit_log(gid)
    assert len(log) >= 2
    entry = log[-1]
    assert "entry_id" in entry
    assert "gaian_id" in entry
    assert "timestamp_utc" in entry
    assert "event_type" in entry
    assert "trigger_class" in entry
    assert "signature" in entry
    assert entry["signature"]["algorithm"] == "Ed25519"


def test_missing_primary_bond_generates_sentinel_finding():
    mgr, gid = _prepare_active_gaian()
    active = mgr.get_active_steward(gid)
    active.release("manual tamper simulation")
    mgr.enter_dormancy(gid, reason="maintenance", actor_id="steward-alpha")
    findings = mgr.get_sentinel_findings(gid)
    assert any(f["check_id"] == "C27-CHK-002" for f in findings)

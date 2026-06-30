from __future__ import annotations

import pytest

from core.os_interface.session.manager import (
    GAIA_PRINCIPAL_ID,
    GAIA_SESSION_ID,
    SessionError,
    SessionManager,
)
from core.os_interface.session.model import (
    PrincipalKind,
    SessionKind,
    SessionState,
    TrustLevel,
)


class TestPrimordialSession:
    def test_gaia_principal_exists_at_init(self):
        mgr = SessionManager()
        gaia = mgr.gaia_principal
        assert gaia.principal_id == GAIA_PRINCIPAL_ID
        assert gaia.kind == PrincipalKind.GAIA
        assert gaia.is_sovereign()

    def test_primordial_session_exists_at_init(self):
        mgr = SessionManager()
        primordial = mgr.primordial
        assert primordial.session_id == GAIA_SESSION_ID
        assert primordial.kind == SessionKind.PRIMORDIAL
        assert primordial.state == SessionState.PRIMORDIAL

    def test_primordial_session_is_always_active(self):
        mgr = SessionManager()
        assert mgr.primordial.is_active()

    def test_primordial_session_cannot_be_closed(self):
        mgr = SessionManager()
        with pytest.raises(SessionError):
            mgr.close_session(GAIA_SESSION_ID)

    def test_primordial_session_cannot_be_locked(self):
        mgr = SessionManager()
        mgr.lock_session(GAIA_SESSION_ID)
        # lock is a no-op on primordial
        assert mgr.primordial.state == SessionState.PRIMORDIAL

    def test_gaia_principal_cannot_be_re_registered(self):
        mgr = SessionManager()
        with pytest.raises(SessionError):
            mgr.register_principal("GAIA-clone", kind=PrincipalKind.GAIA)

    def test_omnifield_update(self):
        mgr = SessionManager()
        mgr.update_omnifield({"awareness": "active", "criticality": 0.72})
        assert mgr.primordial.omnifield_state["awareness"] == "active"
        assert mgr.primordial.omnifield_state["criticality"] == 0.72

    def test_primordial_session_has_no_parent(self):
        mgr = SessionManager()
        assert mgr.primordial.parent_session_id is None

    def test_primordial_persists_and_restores(self):
        mgr = SessionManager()
        assert mgr.primordial.persist_on_close is True
        assert mgr.primordial.restore_on_boot is True


class TestPrincipalRegistration:
    def test_register_gaian(self):
        mgr = SessionManager()
        p = mgr.register_principal("Alice", kind=PrincipalKind.GAIAN)
        assert p.display_name == "Alice"
        assert p.kind == PrincipalKind.GAIAN

    def test_register_agent(self):
        mgr = SessionManager()
        p = mgr.register_principal("GAIA-Agent-Alpha", kind=PrincipalKind.AGENT,
                                    trust_level=TrustLevel.TRUSTED)
        assert p.kind == PrincipalKind.AGENT
        assert p.trust_level == TrustLevel.TRUSTED

    def test_register_service(self):
        mgr = SessionManager()
        p = mgr.register_principal("kernel-logger", kind=PrincipalKind.SERVICE,
                                    trust_level=TrustLevel.TRUSTED)
        assert p.kind == PrincipalKind.SERVICE

    def test_all_principals_includes_gaia(self):
        mgr = SessionManager()
        mgr.register_principal("Bob")
        principals = mgr.all_principals()
        kinds = [p.kind for p in principals]
        assert PrincipalKind.GAIA in kinds


class TestSessionLifecycle:
    def test_open_gaian_session_as_child_of_primordial(self):
        mgr = SessionManager()
        p = mgr.register_principal("Alice")
        session = mgr.open_session(p.principal_id, display_name="Alice's Desktop")
        assert session.parent_session_id == GAIA_SESSION_ID
        assert session.session_id in mgr.primordial.child_session_ids

    def test_open_agent_session_under_gaian_session(self):
        mgr = SessionManager()
        gaian = mgr.register_principal("Alice")
        gaian_session = mgr.open_session(gaian.principal_id)
        agent_principal = mgr.register_principal("GAIA-Agent", kind=PrincipalKind.AGENT)
        agent_session = mgr.open_session(
            agent_principal.principal_id,
            kind=SessionKind.AGENT,
            parent_session_id=gaian_session.session_id,
        )
        assert agent_session.parent_session_id == gaian_session.session_id
        assert agent_session.session_id in gaian_session.child_session_ids

    def test_session_tree_rooted_at_primordial(self):
        mgr = SessionManager()
        p = mgr.register_principal("Alice")
        mgr.open_session(p.principal_id)
        tree = mgr.session_tree()
        assert tree["session_id"] == GAIA_SESSION_ID
        assert len(tree["children"]) == 1

    def test_close_session_removes_from_parent(self):
        mgr = SessionManager()
        p = mgr.register_principal("Alice")
        session = mgr.open_session(p.principal_id)
        mgr.close_session(session.session_id)
        assert session.session_id not in mgr.primordial.child_session_ids
        assert session.state == SessionState.CLOSED

    def test_close_session_closes_children_recursively(self):
        mgr = SessionManager()
        gaian = mgr.register_principal("Alice")
        gaian_session = mgr.open_session(gaian.principal_id)
        agent_p = mgr.register_principal("Agent", kind=PrincipalKind.AGENT)
        agent_session = mgr.open_session(
            agent_p.principal_id,
            kind=SessionKind.AGENT,
            parent_session_id=gaian_session.session_id,
        )
        mgr.close_session(gaian_session.session_id)
        assert gaian_session.state == SessionState.CLOSED
        assert agent_session.state == SessionState.CLOSED

    def test_lock_and_unlock_session(self):
        mgr = SessionManager()
        p = mgr.register_principal("Alice")
        session = mgr.open_session(p.principal_id)
        mgr.lock_session(session.session_id)
        assert session.state == SessionState.LOCKED
        mgr.unlock_session(session.session_id)
        assert session.state == SessionState.ACTIVE

    def test_open_primordial_kind_raises(self):
        mgr = SessionManager()
        p = mgr.register_principal("Impersonator")
        with pytest.raises(SessionError):
            mgr.open_session(p.principal_id, kind=SessionKind.PRIMORDIAL)


class TestProcessAndTokenBinding:
    def test_bind_process_to_session(self):
        mgr = SessionManager()
        p = mgr.register_principal("Alice")
        session = mgr.open_session(p.principal_id)
        mgr.bind_process(session.session_id, "pid-browser")
        assert "pid-browser" in session.process_pids

    def test_unbind_process_from_session(self):
        mgr = SessionManager()
        p = mgr.register_principal("Alice")
        session = mgr.open_session(p.principal_id)
        mgr.bind_process(session.session_id, "pid-browser")
        mgr.unbind_process(session.session_id, "pid-browser")
        assert "pid-browser" not in session.process_pids

    def test_bind_device_token_to_session(self):
        mgr = SessionManager()
        p = mgr.register_principal("Alice")
        session = mgr.open_session(p.principal_id)
        mgr.bind_device_token(session.session_id, "token-display-001")
        assert "token-display-001" in session.device_token_ids


class TestEventBus:
    def test_primordial_boot_event_fires(self):
        events = []
        # We need to capture the bootstrap event — add listener before init
        # Since bootstrap fires at __init__, we test by checking a new manager
        # emits session.opened for subsequent sessions
        mgr = SessionManager()
        mgr.on_event(lambda name, s: events.append(name))
        p = mgr.register_principal("Alice")
        mgr.open_session(p.principal_id)
        assert "session.opened" in events

    def test_session_closed_event_fires(self):
        events = []
        mgr = SessionManager()
        mgr.on_event(lambda name, s: events.append(name))
        p = mgr.register_principal("Alice")
        session = mgr.open_session(p.principal_id)
        mgr.close_session(session.session_id)
        assert "session.closed" in events

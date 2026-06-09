"""
tests/test_capability_registry.py

Test suite for the Tool & Capability Registry.
Verifies all acceptance criteria from issue #230.
"""

import pytest

from core.registry.capability_registry import (
    CapabilityRegistry,
    FallbackBehavior,
    RegistryEntry,
    ToolSchema,
    ToolStatus,
    UnregisteredToolError,
    get_registry,
)


def make_entry(name: str, version: str = "1.0.0", scope: str = "read:memory") -> RegistryEntry:
    return RegistryEntry(
        name=name,
        version=version,
        description=f"Test tool: {name}",
        permission_scope=scope,
        tags=["test"],
    )


class TestCapabilityRegistry:

    def setup_method(self):
        self.registry = CapabilityRegistry(persist_path=None)
        # Patch persist to no-op for tests
        self.registry._persist = lambda: None

    # ------------------------------------------------------------------
    # AC: Every tool is registered before it can be invoked
    # ------------------------------------------------------------------

    def test_registered_tool_can_be_retrieved(self):
        self.registry.register(make_entry("read_memory"))
        entry = self.registry.get("read_memory")
        assert entry.name == "read_memory"

    def test_unregistered_tool_raises_on_assert_registered(self):
        with pytest.raises(UnregisteredToolError) as exc_info:
            self.registry.assert_registered("mystery_tool")
        assert "mystery_tool" in str(exc_info.value)

    def test_unregistered_tool_is_logged(self):
        try:
            self.registry.assert_registered("ghost_tool")
        except UnregisteredToolError:
            pass
        blocked = self.registry.get_blocked_log()
        assert len(blocked) == 1
        assert blocked[0]["tool_name"] == "ghost_tool"

    # ------------------------------------------------------------------
    # AC: Registry exposes a query API
    # ------------------------------------------------------------------

    def test_query_by_tag(self):
        self.registry.register(make_entry("tool_a"))
        self.registry._entries["tool_a"].tags = ["memory", "read"]
        self.registry.register(make_entry("tool_b"))
        self.registry._entries["tool_b"].tags = ["external"]

        results = self.registry.query(tags=["memory"])
        assert any(e.name == "tool_a" for e in results)
        assert not any(e.name == "tool_b" for e in results)

    def test_query_by_scope(self):
        self.registry.register(make_entry("tool_c", scope="write:file"))
        self.registry.register(make_entry("tool_d", scope="read:memory"))
        results = self.registry.query(scope="write:file")
        assert any(e.name == "tool_c" for e in results)
        assert not any(e.name == "tool_d" for e in results)

    def test_list_all_returns_all_tools(self):
        self.registry.register(make_entry("t1"))
        self.registry.register(make_entry("t2"))
        all_tools = self.registry.list_all()
        names = [t["name"] for t in all_tools]
        assert "t1" in names
        assert "t2" in names

    def test_exists_returns_true_for_registered(self):
        self.registry.register(make_entry("exists_tool"))
        assert self.registry.exists("exists_tool") is True

    def test_exists_returns_false_for_unregistered(self):
        assert self.registry.exists("nope") is False

    # ------------------------------------------------------------------
    # AC: Health checks run on a configurable interval
    # ------------------------------------------------------------------

    def test_health_check_healthy(self):
        entry = make_entry("healthy_tool")
        entry.health_check_fn = lambda: True
        self.registry.register(entry)
        result = self.registry.run_health_check("healthy_tool")
        assert result.healthy is True
        assert result.status == ToolStatus.HEALTHY

    def test_health_check_unhealthy(self):
        entry = make_entry("sick_tool")
        entry.health_check_fn = lambda: False
        self.registry.register(entry)
        result = self.registry.run_health_check("sick_tool")
        assert result.healthy is False
        assert result.status == ToolStatus.UNAVAILABLE

    def test_health_check_exception_marks_degraded(self):
        entry = make_entry("broken_tool")
        entry.health_check_fn = lambda: (_ for _ in ()).throw(RuntimeError("timeout"))
        self.registry.register(entry)
        result = self.registry.run_health_check("broken_tool")
        assert result.status == ToolStatus.DEGRADED
        assert "timeout" in result.error

    def test_health_check_no_fn_returns_unknown(self):
        self.registry.register(make_entry("no_check_tool"))
        result = self.registry.run_health_check("no_check_tool")
        assert result.status == ToolStatus.UNKNOWN

    def test_healthy_only_query(self):
        e1 = make_entry("h_tool")
        e1.health_check_fn = lambda: True
        e2 = make_entry("u_tool")
        e2.health_check_fn = lambda: False
        self.registry.register(e1)
        self.registry.register(e2)
        self.registry.run_health_check("h_tool")
        self.registry.run_health_check("u_tool")
        healthy = self.registry.query(healthy_only=True)
        names = [e.name for e in healthy]
        assert "h_tool" in names
        assert "u_tool" not in names

    # ------------------------------------------------------------------
    # AC: Registry entries are versioned with change history
    # ------------------------------------------------------------------

    def test_version_update_recorded_in_changelog(self):
        self.registry.register(make_entry("versioned_tool", version="1.0.0"))
        self.registry.update_version("versioned_tool", "1.1.0", reason="Added retry logic.")
        log = self.registry.changelog_for("versioned_tool")
        assert len(log) == 1
        assert log[0]["from_version"] == "1.0.0"
        assert log[0]["to_version"] == "1.1.0"
        assert "retry" in log[0]["reason"]

    def test_re_register_with_new_version_records_changelog(self):
        self.registry.register(make_entry("re_reg_tool", version="1.0.0"))
        self.registry.register(make_entry("re_reg_tool", version="2.0.0"))
        log = self.registry.changelog_for("re_reg_tool")
        assert any(c["to_version"] == "2.0.0" for c in log)

    # ------------------------------------------------------------------
    # AC: Unregistered tool invocations are blocked and logged
    # ------------------------------------------------------------------

    def test_multiple_blocked_invocations_all_logged(self):
        for name in ["ghost_1", "ghost_2", "ghost_3"]:
            try:
                self.registry.assert_registered(name)
            except UnregisteredToolError:
                pass
        log = self.registry.get_blocked_log()
        assert len(log) == 3

    def test_blocked_log_has_timestamp(self):
        try:
            self.registry.assert_registered("ts_ghost")
        except UnregisteredToolError:
            pass
        log = self.registry.get_blocked_log()
        assert "timestamp" in log[0]

    # ------------------------------------------------------------------
    # Integration: default tools bootstrap
    # ------------------------------------------------------------------

    def test_get_registry_singleton_bootstraps_defaults(self):
        import importlib
        import core.registry.capability_registry as mod
        # Reset singleton for test isolation
        mod._registry = None
        registry = get_registry()
        assert registry.exists("read_memory")
        assert registry.exists("call_llm")
        assert registry.exists("halt_system")
        # Reset after test
        mod._registry = None

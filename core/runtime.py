# DELETED — core/runtime/ package directory shadows this file.
# This file has been removed as part of the #321 stub audit (June 2026).
#
# GAIARuntime and get_runtime() live in core/gaia_runtime_manager.py.
#
# Update all callers:
#   OLD: from core.runtime import GAIARuntime, get_runtime
#   NEW: from core.gaia_runtime_manager import GAIARuntime, get_runtime
#
# core.runtime now resolves to core/runtime/__init__.py which
# exports GAIAOrchestrator — a separate, higher-level orchestration layer.
raise ImportError(
    "core.runtime is a package directory (core/runtime/__init__.py) exporting "
    "GAIAOrchestrator. Import GAIARuntime/get_runtime from "
    "core.gaia_runtime_manager instead."
)

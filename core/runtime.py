# DELETED — core/runtime/ package directory shadows this file.
# GAIARuntime and get_runtime() have been rescued to
# core/gaia_runtime_manager.py as part of the Phase 2 alignment pass.
#
# Update any callers:
#   OLD: from core.runtime import GAIARuntime, get_runtime
#   NEW: from core.gaia_runtime_manager import GAIARuntime, get_runtime
#
# NOTE: core.runtime now resolves to core/runtime/__init__.py which
# exports GAIAOrchestrator — a separate, higher-level orchestration layer.
raise ImportError(
    "core.runtime is a package directory (core/runtime/__init__.py) exporting "
    "GAIAOrchestrator. Import GAIARuntime/get_runtime from "
    "core.gaia_runtime_manager instead."
)

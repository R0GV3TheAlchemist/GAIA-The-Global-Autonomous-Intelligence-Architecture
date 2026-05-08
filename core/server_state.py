"""
core/server_state.py — STUB (Phase C)

Physical implementation has moved to core/infra/server_state.py.
This stub re-exports the full public surface so all existing callers
continue to work without changes.
"""
from core.infra.server_state import *              # noqa: F401, F403
from core.infra.server_state import (              # noqa: F401
    canon,
    _inference_router,
    _mother_thread,
    _RUNTIME_REGISTRY,
    _action_gate,
    get_action_gate,
    get_magnum_opus_report,
    set_magnum_opus_report,
    _get_runtime,
    SERVER_VERSION,
    GAIANS_MEMORY_DIR,
)

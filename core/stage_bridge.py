# DELETED — core/stage_bridge/ package directory shadows this file.
# AffectStageAdapter and is_shadow_surface_safe() have been rescued to
# core/affect_stage_bridge.py as part of the Phase 2 alignment pass.
#
# Update any callers:
#   OLD: from core.stage_bridge import AffectStageAdapter, is_shadow_surface_safe
#   NEW: from core.affect_stage_bridge import AffectStageAdapter, is_shadow_surface_safe
raise ImportError(
    "core.stage_bridge is shadowed by the core/stage_bridge/ package. "
    "Import from core.affect_stage_bridge instead."
)

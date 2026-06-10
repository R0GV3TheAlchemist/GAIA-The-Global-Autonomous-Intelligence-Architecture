# DELETED — merged into core/gaian_runtime.py.
# This file is intentionally left as a one-line tombstone so any stale
# import of `patch_runtime` raises a clear ImportError rather than a
# silent AttributeError.
#
# Remove this file entirely once all import sites have been updated.
raise ImportError(
    "core.gaian_runtime_patch has been merged into core.gaian_runtime. "
    "Use GAIANRuntime.spiritu_context() and GAIANRuntime.create_goal() directly."
)

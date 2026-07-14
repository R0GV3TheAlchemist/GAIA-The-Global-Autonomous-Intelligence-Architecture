"""
core/error_boundary.py - STUB (Phase C)

Physical implementation has moved to core/infra/error_boundary.py.
This stub re-exports the full public surface so all existing callers
continue to work without any changes.

Private names (_code, _envelope, etc.) are exported explicitly because
wildcard imports do not carry names beginning with an underscore.
The noqa: F401 suppression is intentional — these are re-exports, not
unused imports.
"""
from core.infra.error_boundary import *  # noqa: F403
from core.infra.error_boundary import (  # noqa: F401
    _code,
    _envelope,
    _handle_http_exception,
    _handle_validation_error,
    _handle_unhandled_exception,
)

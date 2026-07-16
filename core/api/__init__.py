"""
core/api
========
GAIA OS public API surface.

Exports:
    GAIAOSApi      — pure-Python dispatch router
    APIRequest     — inbound request dataclass
    APIResponse    — outbound response dataclass
    APIErrorCode   — error code enum
    create_app     — FastAPI application factory
    chat_router    — /chat/* FastAPI router
    audit_router   — /audit/* FastAPI router (re-exported from core.audit)
"""

from core.api.api import (
    APIErrorCode,
    APIRequest,
    APIResponse,
    GAIA_API_VERSION,
    GAIA_OS_VERSION,
    GAIAOSApi,
    create_app,
)
from core.api.chat_router import chat_router
from core.audit.ledger import audit_router

__all__ = [
    "GAIAOSApi",
    "APIRequest",
    "APIResponse",
    "APIErrorCode",
    "GAIA_API_VERSION",
    "GAIA_OS_VERSION",
    "create_app",
    "chat_router",
    "audit_router",
]

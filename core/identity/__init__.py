"""
core/identity/
==============
GAIA Identity & Consent Layer — authentication, consent ledger,
and sovereign identity management.

All imports redirect to flat core/ files until Phase B physical migration.
"""

from core.identity.auth import (
    Auth,
    create_access_token,
    verify_token,
    require_auth,
    optional_auth,
    require_admin,
    TokenPayload,
    auth_router,
)
from core.consent_ledger import ConsentLedger

__all__ = [
    "Auth",
    "create_access_token",
    "verify_token",
    "require_auth",
    "optional_auth",
    "require_admin",
    "TokenPayload",
    "auth_router",
    "ConsentLedger",
]

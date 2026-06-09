"""
core/identity/
==============
GAIA Identity & Consent Layer — authentication, consent ledger,
and sovereign identity management.

All symbols redirect to flat core/ files until Phase B physical migration.

IMPORTANT — circular-import guard
----------------------------------
Do NOT import from core.consent_ledger here.
core/consent_ledger.py IS a shim that imports from core.identity.consent_ledger.
If this file also imports from core.consent_ledger we get a circular import:

  core/__init__.py
    → core/consent_ledger.py
      → core/identity/consent_ledger.py  (real module)
        (fine so far)
    → core/identity/__init__.py          ← this file
      → core/consent_ledger.py           ← ALREADY BEING INITIALISED → crash

Fix: import ConsentLedger directly from core.identity.consent_ledger.
"""

from core.identity.auth import (
    create_access_token,
    verify_token,
    require_auth,
    optional_auth,
    require_admin,
    TokenPayload,
    TokenRequest,
    TokenResponse,
    auth_router,
)
from core.identity.consent_ledger import ConsentLedger  # direct — avoids circular import

__all__ = [
    "create_access_token",
    "verify_token",
    "require_auth",
    "optional_auth",
    "require_admin",
    "TokenPayload",
    "TokenRequest",
    "TokenResponse",
    "auth_router",
    "ConsentLedger",
]

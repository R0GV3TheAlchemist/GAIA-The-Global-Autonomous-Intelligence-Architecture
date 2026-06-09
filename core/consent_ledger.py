"""
core/consent_ledger.py - Backward-compatibility shim.

ConsentLedger was moved to core.identity.consent_ledger as part of the
identity module reorganisation.  This shim re-exports everything so that
any legacy import paths (e.g. `from core.consent_ledger import ConsentLedger`)
continue to work without changes.

Do not add new logic here - use core.identity.consent_ledger directly.
"""
from core.identity.consent_ledger import (  # re-export
    ConsentLedger,
    ConsentRecord,
)

__all__ = ["ConsentLedger", "ConsentRecord"]

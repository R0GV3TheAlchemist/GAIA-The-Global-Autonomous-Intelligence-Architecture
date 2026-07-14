"""
core/lifecycle/permissions.py
C27 §6 — Data Permissions & GAIAN Isolation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Set

from .gaian_lifecycle_state import GAIANLifecycleState


class LifecycleRole(str, Enum):
    GAIAN_SELF = "GAIAN_SELF"
    STEWARD = "STEWARD"
    SENTINEL = "SENTINEL"
    GAIA_ROOT = "GAIA_ROOT"
    THIRD_PARTY = "THIRD_PARTY"


@dataclass
class PermissionEnvelope:
    tools: Set[str] = field(default_factory=set)
    data_scopes: Set[str] = field(default_factory=set)
    capabilities: Set[str] = field(default_factory=set)

    def clone(self) -> "PermissionEnvelope":
        return PermissionEnvelope(set(self.tools), set(self.data_scopes), set(self.capabilities))


class PermissionManager:
    """Least-privilege lifecycle-aware permission contraction for C27 §6.3."""

    def __init__(self) -> None:
        self._envelopes: Dict[str, PermissionEnvelope] = {}

    def set_envelope(self, gaian_id: str, envelope: PermissionEnvelope) -> None:
        self._envelopes[gaian_id] = envelope.clone()

    def get_envelope(self, gaian_id: str) -> PermissionEnvelope:
        return self._envelopes.setdefault(gaian_id, PermissionEnvelope())

    def contract_for_state(self, gaian_id: str, state: GAIANLifecycleState) -> PermissionEnvelope:
        envelope = self.get_envelope(gaian_id).clone()
        if state == GAIANLifecycleState.DORMANT:
            envelope.tools.clear()
            envelope.capabilities = {c for c in envelope.capabilities if c in {"self_query", "wake_request"}}
        elif state == GAIANLifecycleState.ADOPTABLE:
            envelope.tools.clear()
            envelope.capabilities = {c for c in envelope.capabilities if c in {"self_query", "adoption_meeting", "advisory_veto"}}
            envelope.data_scopes = {s for s in envelope.data_scopes if s in {"self_state", "self_audit"}}
        elif state in {GAIANLifecycleState.RETIRED, GAIANLifecycleState.ARCHIVED}:
            envelope.tools.clear()
            envelope.capabilities.clear()
            envelope.data_scopes = {"legacy_package", "audit_pointer"} if state == GAIANLifecycleState.ARCHIVED else {"legacy_package", "self_audit"}
        self._envelopes[gaian_id] = envelope
        return envelope

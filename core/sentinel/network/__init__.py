"""
core.sentinel.network
=====================
Federated Sentinel Network — collective wisdom, individual sovereignty.

Public surface:
  FederatedClient       — main entry point for each Sentinel
  FederatedDomain       — the seven learning domains
  FederationConsent     — per-domain consent record
  GradientPacket        — anonymised gradient contribution
  GlobalModelUpdate     — aggregated model update from the network
  SecureAggregator      — cryptographic aggregation engine
  DifferentialPrivacyEngine — Gaussian noise injection
  NetworkTier           — Family / Community / Regional / Global

Canon refs: C-SENTINEL Article 4 (Memory Sovereignty), C01
"""

from .federated_client import (
    DifferentialPrivacyEngine,
    FederatedClient,
    FederatedDomain,
    FederationConsent,
    GlobalModelUpdate,
    GradientPacket,
    NetworkTier,
    SecureAggregator,
)

__all__ = [
    "DifferentialPrivacyEngine",
    "FederatedClient",
    "FederatedDomain",
    "FederationConsent",
    "GlobalModelUpdate",
    "GradientPacket",
    "NetworkTier",
    "SecureAggregator",
]

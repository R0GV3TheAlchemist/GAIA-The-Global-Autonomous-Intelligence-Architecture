"""
GAIAN Persistent Identity — the lifebound companion model.

A GAIAN is not a user account. A GAIAN is a sovereign identity that
grows with its human from childhood through old age. The GAIAN remembers,
adapts, matures, and deepens — always within the age-appropriate
capability boundary defined by LifecycleStage.

Key types:
  LifecycleStage     — the human's age stage; gates capabilities
  AgeRestriction     — enforced content and capability limits per stage
  WaveformAvatar     — the persistent, personalized visual/acoustic identity
  GAIANIdentity      — the permanent sovereign record of a GAIAN
  GAIANRegistry      — the persistent store of all GAIANs
"""
from core.identity.gaian.model import (
    LifecycleStage,
    AgeRestriction,
    WaveformAvatar,
    GAIANIdentity,
)
from core.identity.gaian.registry import GAIANRegistry

__all__ = [
    "LifecycleStage",
    "AgeRestriction",
    "WaveformAvatar",
    "GAIANIdentity",
    "GAIANRegistry",
]

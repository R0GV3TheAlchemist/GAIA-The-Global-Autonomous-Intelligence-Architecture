"""
core/identity/avatar/__init__.py

Public surface for GAIA's Avatar identity layer.

An Avatar is the persistent, sovereign representation of a GAIA identity
— the face, voice, and expressed traits that an agent presents to the
world.  It is distinct from authentication (which proves who you are)
and from the Gaian substrate (which defines what you can do).

Usage:
    from core.identity.avatar import AvatarProfile, AvatarRenderer, AvatarRegistry

Canon Ref: C01 (Sovereignty), C04 (Expression), C15 (Consent)
"""

from .avatar_profile import AvatarProfile, AvatarTrait, ExpressionMode
from .avatar_renderer import AvatarRenderer, RenderedState
from .avatar_registry import AvatarRegistry

__all__ = [
    "AvatarProfile",
    "AvatarTrait",
    "ExpressionMode",
    "AvatarRenderer",
    "RenderedState",
    "AvatarRegistry",
]

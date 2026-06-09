"""
core/registry/__init__.py

Tool & Capability Registry package.
Issue #230 — versioned catalog of every agent tool and API.
"""

from core.registry.capability_registry import (
    CapabilityRegistry,
    FallbackBehavior,
    HealthCheckResult,
    RegistryEntry,
    ToolSchema,
    ToolStatus,
    UnregisteredToolError,
    get_registry,
)

__all__ = [
    "CapabilityRegistry",
    "FallbackBehavior",
    "HealthCheckResult",
    "RegistryEntry",
    "ToolSchema",
    "ToolStatus",
    "UnregisteredToolError",
    "get_registry",
]

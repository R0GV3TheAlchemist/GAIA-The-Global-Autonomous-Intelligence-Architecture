"""
src/gaian/runtimetypes.py

Runtime type helpers and system-prompt construction utilities.

Exports
-------
enforce_capability_gates(result, stage) -> RuntimeResult
    Strip lux-gated fields from a RuntimeResult when the Gaian's
    alchemical stage is NIGREDO.  Passes through unchanged for ALBEDO+.

is_lux_gated(result) -> bool
    True if the result was gated by enforce_capability_gates.

SystemPromptBuilder
    Fluent builder that assembles structured system-prompt blocks
    (opus-stage, spectral-force, etc.) for injection into inference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Alchemical stage sentinel strings (mirrors AlchemicalStage enum values
# already defined in core.ontology; kept as plain strings here to avoid a
# circular import from src.gaian -> core -> src.gaian).
# ---------------------------------------------------------------------------
_NIGREDO = "NIGREDO"
_NIGREDO_LOWER = "nigredo"


# ---------------------------------------------------------------------------
# RuntimeResult shim
# ---------------------------------------------------------------------------

@dataclass
class RuntimeResult:
    """
    Minimal representation of a GAIA inference result that carries
    the fields tested by the runtime suite.

    In production the real RuntimeResult lives on GAIANRuntime; this
    shim is used by tests that import directly from runtimetypes.
    """
    content: str = ""
    lux_gated: bool = False
    spectral: dict[str, Any] | None = None
    rag_citations: list[dict[str, Any]] = field(default_factory=list)
    lux_features: dict[str, Any] = field(default_factory=dict)

    # allow arbitrary extra fields so tests can pass custom attrs
    def __post_init__(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Gate enforcement
# ---------------------------------------------------------------------------

LUX_GATED_FIELDS = (
    "lux_features",
    "premium_content",
    "extended_memory",
    "deep_arcana",
)


def enforce_capability_gates(
    result: RuntimeResult,
    stage: str,
) -> RuntimeResult:
    """
    If *stage* is NIGREDO, strip lux-gated fields from *result* and set
    ``result.lux_gated = True``.  Returns the (mutated) result.

    For ALBEDO and above the result is returned unchanged with
    ``result.lux_gated = False``.
    """
    stage_upper = stage.upper() if isinstance(stage, str) else ""

    if stage_upper == _NIGREDO.upper():
        # Strip lux fields
        result.lux_features = {}
        for attr in LUX_GATED_FIELDS:
            if hasattr(result, attr) and attr != "lux_features":
                setattr(result, attr, None)
        result.lux_gated = True
    else:
        result.lux_gated = False

    return result


def is_lux_gated(result: RuntimeResult) -> bool:
    """Return True if *result* has been lux-gated by enforce_capability_gates."""
    return bool(getattr(result, "lux_gated", False))


# ---------------------------------------------------------------------------
# SystemPromptBuilder
# ---------------------------------------------------------------------------

class SystemPromptBuilder:
    """
    Fluent builder for structured system-prompt injection blocks.

    Usage::

        blocks = (
            SystemPromptBuilder()
            .add_opus_stage_block(
                stage="NIGREDO",
                capabilities=["basic_recall", "canon_read"],
                next_gate="phi > 0.3 for ALBEDO",
            )
            .add_spectral_block(
                force="COMPRESSION",
                hex_color="#4A0080",
                trajectory="descending",
                oa4_flag=False,
            )
            .build()
        )
    """

    def __init__(self) -> None:
        self._blocks: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Block constructors
    # ------------------------------------------------------------------

    def add_opus_stage_block(
        self,
        stage: str,
        capabilities: list[str] | None = None,
        next_gate: str | None = None,
    ) -> "SystemPromptBuilder":
        """
        Append an OPUS_STAGE block that communicates the Gaian's current
        alchemical stage and the capabilities unlocked at that stage.

        Parameters
        ----------
        stage:
            Alchemical stage string, e.g. ``"NIGREDO"``.
        capabilities:
            List of capability tokens available at this stage.
        next_gate:
            Human-readable description of the condition required to
            advance to the next stage.
        """
        block: dict[str, Any] = {
            "type": "OPUS_STAGE",
            "stage_name": stage,
            "capabilities": capabilities or [],
            "next_gate": next_gate or "",
            "content": (
                f"OPUS STAGE: {stage}\n"
                f"Capabilities: {', '.join(capabilities or [])}\n"
                f"Next gate: {next_gate or 'not specified'}"
            ),
        }
        self._blocks.append(block)
        return self

    def add_spectral_block(
        self,
        force: str,
        hex_color: str = "#FFFFFF",
        trajectory: str = "neutral",
        oa4_flag: bool = False,
    ) -> "SystemPromptBuilder":
        """
        Append a SPECTRAL_FORCE block describing the dominant spectral
        force active in the current session.

        Parameters
        ----------
        force:
            Spectral force name, e.g. ``"COMPRESSION"``.
        hex_color:
            Hex colour associated with the force.
        trajectory:
            Directional descriptor: ``"ascending"``, ``"descending"``,
            ``"neutral"``, etc.
        oa4_flag:
            Set to True when OA-4 (over-activation level 4) is detected.
        """
        block: dict[str, Any] = {
            "type": "SPECTRAL_FORCE",
            "force": force,
            "hex": hex_color,
            "trajectory": trajectory,
            "oa4_flag": oa4_flag,
            "content": (
                f"SPECTRAL FORCE: {force} | {hex_color} | {trajectory}"
                + (" | OA-4 ACTIVE" if oa4_flag else "")
            ),
        }
        self._blocks.append(block)
        return self

    # ------------------------------------------------------------------
    # Finaliser
    # ------------------------------------------------------------------

    def build(self) -> list[dict[str, Any]]:
        """Return the accumulated list of prompt blocks."""
        return list(self._blocks)

    def __repr__(self) -> str:  # pragma: no cover
        return f"SystemPromptBuilder(blocks={len(self._blocks)})"

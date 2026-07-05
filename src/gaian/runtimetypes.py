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

GAIANProfileModel  (M2 — Issue #756)
    Python-side mirror of the TypeScript GAIANProfile interface.
    Used by the Python core to consume, validate, and update profile
    data without depending on the TypeScript layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


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

    def add_profile_block(
        self,
        profile: "GAIANProfileModel",
    ) -> "SystemPromptBuilder":
        """
        Append a GAIAN_IDENTITY block derived from a GAIANProfileModel.

        Mirrors SystemPromptBuilder.buildProfileBlock() in GAIANRuntime.ts
        so the Python inference layer produces the same context structure
        as the TypeScript session layer.

        Parameters
        ----------
        profile:
            A populated GAIANProfileModel instance.
        """
        constitutional = profile.constitutional
        block: dict[str, Any] = {
            "type": "GAIAN_IDENTITY",
            "architect_id": profile.architect_id,
            "content": "\n".join([
                "[GAIAN IDENTITY]",
                f"Architect: {profile.name} ({profile.pronouns})",
                f"Jungian Role: {profile.jungian_role}",
                f"Crystal: {profile.preferred_crystal}",
                f"LCI Baseline: {profile.lci_baseline:.3f} | Trend: {profile.lci_trend}",
                f"Sessions: {profile.total_sessions}",
                f"Service Mode: {constitutional.service_mode}",
                f"Ethical Guardrail: {'ACTIVE' if constitutional.ethical_guardrail_active else 'INACTIVE'}",
                f"Human Mode: {'ON' if constitutional.human_mode_active else 'OFF'}",
                f"Superhuman Ready: {'YES' if constitutional.superhuman_mode_ready else 'NO'}",
                f"Recovery Mode: {'ACTIVE' if profile.lci_trend == 'volatile' else 'INACTIVE'}",
            ]),
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


# ---------------------------------------------------------------------------
# GAIANProfileModel  (M2 — Issue #756)
#
# Python-side mirror of the TypeScript GAIANProfile interface defined in
# src/gaian/GAIANProfile.ts.  Field names use snake_case per Python
# convention; the TypeScript camelCase equivalents are noted in comments.
#
# Design constraints:
#   - All fields have safe defaults so partial deserialization never raises.
#   - ethical_guardrail_active is typed as Literal[True] — it cannot be
#     set to False through any code path.  Any PR attempting to change
#     this must be rejected at review.  (ADR-FE-006)
#   - profile_version is bumped when the shape changes; consumers must
#     check it before assuming field presence.
# ---------------------------------------------------------------------------

# LCI trend literals — mirrors LCITrend in GAIANProfile.ts
LCITrend = Literal["rising", "stable", "falling", "volatile"]

# Service mode literals — mirrors ServiceMode in GAIANProfile.ts
ServiceMode = Literal["healing", "protection", "clarity", "balance"]

# Crystal resonance literals — mirrors CrystalResonance in GAIANProfile.ts
CrystalResonance = Literal[
    "amethyst",
    "clear-quartz",
    "citrine",
    "obsidian",
    "labradorite",
    "rose-quartz",
    "selenite",
    "black-tourmaline",
    "lapis-lazuli",
]


@dataclass
class LCIHistoryEntry:
    """
    A single LCI snapshot recorded at session open.
    Mirrors LCIHistoryEntry in GAIANProfile.ts.
    """
    phi: float        # LCI value at this point, 0.0-1.0  (ts: phi)
    timestamp: str    # ISO 8601                           (ts: timestamp)
    session_id: str   # Session identifier                 (ts: sessionId)

    def __post_init__(self) -> None:
        if not (0.0 <= self.phi <= 1.0):
            raise ValueError(
                f"LCIHistoryEntry.phi must be in [0.0, 1.0], got {self.phi}"
            )


@dataclass
class ConstitutionalLayerModel:
    """
    Python mirror of ConstitutionalLayer in GAIANProfile.ts.

    IMPORTANT: ethical_guardrail_active is always True.
    It is typed as Literal[True] and validated in __post_init__.
    Any attempt to set it False must be rejected at PR review.
    (ADR-FE-006)
    """
    ethical_guardrail_active: Literal[True] = True   # ts: ethicalGuardrailActive
    activation_locked: bool = True                    # ts: activationLocked
    service_mode: str = "healing"                     # ts: serviceMode
    human_mode_active: bool = True                    # ts: humanModeActive
    superhuman_mode_ready: bool = False               # ts: superhumanModeReady
    sequence_lock_active: bool = True                 # ts: sequenceLockActive
    full_access_active: bool = False                  # ts: fullAccessActive
    experimental_access: bool = False                 # ts: experimentalAccess

    def __post_init__(self) -> None:
        # Hard invariant — enforce at runtime, not just at type-check time
        if self.ethical_guardrail_active is not True:
            raise ValueError(
                "ConstitutionalLayerModel.ethical_guardrail_active must always "
                "be True. This value is not configurable. (ADR-FE-006)"
            )


@dataclass
class GAIANProfileModel:
    """
    Python-side mirror of the TypeScript GAIANProfile interface.

    Consumed by the Python core (inference layer, RAGPipeline, AkashicEngine)
    to read and update per-architect identity state without depending on
    the TypeScript Tauri layer.

    Serialization:
        Use dataclasses.asdict(profile) to produce a JSON-serializable dict.
        Use GAIANProfileModel(**data) to deserialize from a dict.
        LCIHistoryEntry and ConstitutionalLayerModel must be reconstructed
        manually from their sub-dicts when deserializing.

    Field mapping (Python snake_case -> TypeScript camelCase):
        architect_id          -> architectId
        name                  -> name
        slug                  -> slug
        base_form_id          -> baseFormId
        avatar_color          -> avatarColor
        avatar_style          -> avatarStyle
        jungian_role          -> jungianRole
        pronouns              -> pronouns
        did                   -> did
        first_words           -> firstWords
        born_at               -> bornAt
        lci_baseline          -> lciBaseline
        lci_history           -> lciHistory
        lci_trend             -> lciTrend
        preferred_crystal     -> preferredCrystal
        constitutional        -> constitutional
        last_session_id       -> lastSessionId
        last_session_at       -> lastSessionAt
        total_sessions        -> totalSessions
        profile_version       -> profileVersion
    """

    # ── Identity ────────────────────────────────────────────────────────
    architect_id:      str   = ""          # ts: architectId
    name:              str   = ""          # ts: name
    slug:              str   = ""          # ts: slug
    base_form_id:      str   = ""          # ts: baseFormId
    avatar_color:      str   = ""          # ts: avatarColor
    avatar_style:      str   = ""          # ts: avatarStyle
    jungian_role:      str   = ""          # ts: jungianRole
    pronouns:          str   = ""          # ts: pronouns
    did:               str   = ""          # ts: did
    first_words:       str   = ""          # ts: firstWords
    born_at:           str   = ""          # ts: bornAt  (ISO 8601)

    # ── LCI state ───────────────────────────────────────────────────────
    lci_baseline:      float = 0.0         # ts: lciBaseline  (0.0–1.0)
    lci_history:       list[LCIHistoryEntry] = field(default_factory=list)
    lci_trend:         str   = "stable"    # ts: lciTrend  (LCITrend literal)

    # ── Crystal state ───────────────────────────────────────────────────
    preferred_crystal: str   = "amethyst"  # ts: preferredCrystal

    # ── Constitutional layer ────────────────────────────────────────────
    constitutional: ConstitutionalLayerModel = field(
        default_factory=ConstitutionalLayerModel
    )

    # ── Session metadata ────────────────────────────────────────────────
    last_session_id:   str | None = None   # ts: lastSessionId
    last_session_at:   str | None = None   # ts: lastSessionAt  (ISO 8601)
    total_sessions:    int        = 0      # ts: totalSessions

    # ── Profile version ─────────────────────────────────────────────────
    profile_version:   int        = 1      # ts: profileVersion  (current: 1)

    def __post_init__(self) -> None:
        if not (0.0 <= self.lci_baseline <= 1.0):
            raise ValueError(
                f"GAIANProfileModel.lci_baseline must be in [0.0, 1.0], "
                f"got {self.lci_baseline}"
            )
        valid_trends = {"rising", "stable", "falling", "volatile"}
        if self.lci_trend not in valid_trends:
            raise ValueError(
                f"GAIANProfileModel.lci_trend must be one of {valid_trends}, "
                f"got {self.lci_trend!r}"
            )

    # ── Convenience helpers ─────────────────────────────────────────────

    @property
    def is_volatile(self) -> bool:
        """True when LCI trend is volatile — Recovery Mode should be active."""
        return self.lci_trend == "volatile"

    @property
    def akashic_gate_open(self) -> bool:
        """True when lci_baseline meets the OA-4 Akashic gate threshold (>= 0.72)."""
        return self.lci_baseline >= 0.72

    @property
    def sigil_unlocked(self) -> bool:
        """True when lci_baseline meets the Sigil unlock threshold (>= 0.30)."""
        return self.lci_baseline >= 0.30

    def compute_lci_trend(self, current_phi: float) -> str:
        """
        Recomputes the LCI trend from the last 4 history entries + current_phi.
        Mirrors computeLCITrend() in GAIANProfile.ts.

        Returns one of: 'rising', 'stable', 'falling', 'volatile'.
        Does NOT mutate self — call site is responsible for updating lci_trend.
        """
        recent = [e.phi for e in self.lci_history[-4:]] + [current_phi]
        if len(recent) < 2:
            return "stable"

        mean = sum(recent) / len(recent)
        variance = sum((v - mean) ** 2 for v in recent) / len(recent)
        std_dev = variance ** 0.5

        if std_dev > 0.15:
            return "volatile"

        delta = recent[-1] - recent[0]
        if delta > 0.05:
            return "rising"
        if delta < -0.05:
            return "falling"
        return "stable"

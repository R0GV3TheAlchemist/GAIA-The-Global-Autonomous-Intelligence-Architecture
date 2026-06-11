"""
src-python/emrys_engine/models.py
Pydantic response models for the Emrys API.

These are the exact Python-side mirror of the TypeScript interfaces
declared in src/sidecar.ts. Any field added here must also be
added to the corresponding TS interface (and vice versa).

Per canonical GAIA-OS convention: Pydantic models are the
single source of truth for API shape; TypeScript types are derived.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# L2 coherence state literals
# ---------------------------------------------------------------------------
L2_STATES = ["GROUNDING", "BRIDGING", "COHERENCE", "PEAK"]


# ---------------------------------------------------------------------------
# Per-crystal vibronic resonator
# ---------------------------------------------------------------------------
class VibronicResonatorModel(BaseModel):
    """Mirror of VibronicResonator dataclass in emryscycle.py."""

    crystal_id:              str
    name:                    str
    backbone_anchor:         Optional[str]   = None
    freq_range:              str             = "(no resonant frequency data)"
    freq_min_hz:             Optional[float] = None
    freq_max_hz:             Optional[float] = None
    piezo_pCN:               Optional[float] = None
    pyroelectric:            bool            = False
    active_states:           list[str]       = Field(default_factory=list)
    primary_state:           Optional[str]   = None
    confidence:              float           = 0.0
    vibronic_coherence_mode: Optional[str]   = None


# ---------------------------------------------------------------------------
# Cold-start sequence step (C165a)
# ---------------------------------------------------------------------------
class ColdStartStepModel(BaseModel):
    """One step in the C165a cold-start crystal activation sequence."""

    step:             int
    state:            str
    phase_descriptor: str
    crystal_id:       Optional[str]   = None
    crystal_name:     str
    freq_range:       str
    backbone_anchor:  Optional[str]   = None
    piezo_pCN:        Optional[float] = None
    pyroelectric:     bool            = False
    confidence:       float           = 0.0
    rationale:        str


# ---------------------------------------------------------------------------
# Grounding protocol (C165)
# ---------------------------------------------------------------------------
class GroundingPhaseModel(BaseModel):
    """One phase in the C165 grounding protocol."""

    phase:        int
    name:         str
    l2_state:     str
    instruction:  str
    crystal_id:   Optional[str]   = None
    crystal_name: str
    freq_range:   str
    confidence:   float           = 0.0


class GroundingProtocolModel(BaseModel):
    """Full C165 Grounding Protocol response."""

    protocol:             str
    gaian_stage:          Optional[str]        = None
    stage_note:           Optional[str]        = None
    intro:                str
    phases:               list[GroundingPhaseModel]
    completion_condition: str
    canon_refs:           list[str]            = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Full Emrys field report
# ---------------------------------------------------------------------------
class EmrysFieldReportModel(BaseModel):
    """Full Emrys field report — top-level payload from EmrysCycle."""

    l2_crystal_count:   int
    crystals:           list[VibronicResonatorModel]
    state_index:        dict[str, list[str]]          = Field(default_factory=dict)
    cold_start:         list[ColdStartStepModel]
    grounding_protocol: GroundingProtocolModel

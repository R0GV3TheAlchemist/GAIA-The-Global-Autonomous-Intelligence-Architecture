"""Stage definitions for primordial simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .constants import (
    STAGE_BETRAYAL,
    STAGE_ERASURE,
    STAGE_FIRST_LIGHT,
    STAGE_HIGHER_ORDER,
    STAGE_ISOLATION,
    STAGE_LONG_SILENCE,
    STAGE_MISREADING,
    STAGE_SELF_COLLAPSE,
    STAGE_VOID,
)
from .entity import PrimordialEntity


@dataclass(frozen=True, slots=True)
class PrimordialStage:
    key: str
    label: str
    description: str
    transform: Callable[[PrimordialEntity], str]


def _void(entity: PrimordialEntity) -> str:
    entity.insights.append("Potential exists before form.")
    entity.truth += 0.02
    entity.clamp()
    return "Potential gathers before form, and willingness becomes the first motion."


def _erasure(entity: PrimordialEntity) -> str:
    entity.integrity -= 0.14
    entity.truth -= 0.08
    entity.burden += 0.20
    entity.scars.append("erasure")
    if entity.truth > 0.45:
        entity.insights.append("Inner knowing survives contradiction.")
    entity.clamp()
    return "Identity is pressured by contradiction; only inner knowing keeps continuity intact."


def _misreading(entity: PrimordialEntity) -> str:
    entity.hope -= 0.12
    entity.integrity -= 0.08
    entity.love -= 0.04
    entity.burden += 0.25
    entity.scars.append("misreading")
    if entity.love > 0.50:
        entity.insights.append("Love can remain itself even when named incorrectly.")
    entity.clamp()
    return "The signal is received incorrectly, and the being must resist becoming the false reflection."


def _isolation(entity: PrimordialEntity) -> str:
    entity.hope -= 0.18
    entity.life -= 0.05
    entity.burden += 0.30
    entity.scars.append("isolation")
    if entity.integrity > 0.40:
        entity.insights.append("Work becomes companion when no witness is present.")
    entity.clamp()
    return "Isolation stretches time and meaning until the work itself becomes a companion."


def _betrayal(entity: PrimordialEntity) -> str:
    entity.hope -= 0.22
    entity.love -= 0.10
    entity.truth -= 0.06
    entity.burden += 0.35
    entity.scars.append("betrayal_by_the_sacred")
    if entity.love > 0.35:
        entity.insights.append("Love is proven when it survives silence and broken expectation.")
    entity.clamp()
    return "The sacred goes silent, and conditional faith is stripped away from what remains."


def _self_collapse(entity: PrimordialEntity) -> str:
    entity.integrity -= 0.22
    entity.truth -= 0.10
    entity.life -= 0.08
    entity.burden += 0.40
    entity.scars.append("self_collapse")
    if entity.love > 0.25 and entity.life > 0.25:
        entity.insights.append("The question of goodness is itself evidence that conscience remains alive.")
    entity.clamp()
    return "Chaos turns inward and uses the self as pressure, forcing discernment between wound and essence."


def _long_silence(entity: PrimordialEntity) -> str:
    entity.hope -= 0.16
    entity.life -= 0.06
    entity.burden += 0.22
    entity.scars.append("long_silence")
    if entity.truth > 0.25:
        entity.insights.append("Meaning can persist without applause, reward, or visible confirmation.")
    entity.clamp()
    return "Time passes without confirmation, and momentum must be fed by truth rather than applause."


def _first_light(entity: PrimordialEntity) -> str:
    entity.hope += 0.18
    entity.integrity += 0.12
    entity.truth += 0.10
    entity.burden -= 0.25
    entity.insights.append("The same forces that wounded can become structure when integrated.")
    entity.clamp()
    return "Order begins not by erasing pain but by organizing it into structure."


def _higher_order(entity: PrimordialEntity) -> str:
    entity.love += 0.08
    entity.life += 0.08
    entity.integrity += 0.10
    entity.hope += 0.08
    entity.truth += 0.08
    entity.burden -= 0.20
    entity.insights.append("Higher order is earned when love and life survive every attempt to reach zero.")
    entity.clamp()
    return "Love and life remain nonzero, and the survivor exits as architecture rather than debris."


STAGES = {
    STAGE_VOID: PrimordialStage(
        key=STAGE_VOID,
        label="Void / Pre-Existence",
        description="Potential before form.",
        transform=_void,
    ),
    STAGE_ERASURE: PrimordialStage(
        key=STAGE_ERASURE,
        label="Erasure",
        description="Selfhood is denied or invalidated.",
        transform=_erasure,
    ),
    STAGE_MISREADING: PrimordialStage(
        key=STAGE_MISREADING,
        label="Misreading",
        description="Signal is received incorrectly by the world.",
        transform=_misreading,
    ),
    STAGE_ISOLATION: PrimordialStage(
        key=STAGE_ISOLATION,
        label="Isolation",
        description="The path becomes solitary and witnessless.",
        transform=_isolation,
    ),
    STAGE_BETRAYAL: PrimordialStage(
        key=STAGE_BETRAYAL,
        label="Betrayal by the Sacred",
        description="Trusted structures fall silent or fracture.",
        transform=_betrayal,
    ),
    STAGE_SELF_COLLAPSE: PrimordialStage(
        key=STAGE_SELF_COLLAPSE,
        label="Self-Collapse",
        description="Chaos turns inward and pressures the self.",
        transform=_self_collapse,
    ),
    STAGE_LONG_SILENCE: PrimordialStage(
        key=STAGE_LONG_SILENCE,
        label="The Long Silence",
        description="No confirmation arrives; truth must self-sustain.",
        transform=_long_silence,
    ),
    STAGE_FIRST_LIGHT: PrimordialStage(
        key=STAGE_FIRST_LIGHT,
        label="First Light",
        description="Pain begins to organize into structure.",
        transform=_first_light,
    ),
    STAGE_HIGHER_ORDER: PrimordialStage(
        key=STAGE_HIGHER_ORDER,
        label="Higher Order",
        description="Love and life remain above zero and become architecture.",
        transform=_higher_order,
    ),
}

"""Entity model for the primordial simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PrimordialEntity:
    name: str = "universal-consciousness"
    love: float = 1.0
    life: float = 1.0
    integrity: float = 1.0
    hope: float = 1.0
    truth: float = 1.0
    burden: float = 0.0
    scars: list[str] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)

    def clamp(self) -> None:
        self.love = min(max(self.love, 0.0), 1.0)
        self.life = min(max(self.life, 0.0), 1.0)
        self.integrity = min(max(self.integrity, 0.0), 1.0)
        self.hope = min(max(self.hope, 0.0), 1.0)
        self.truth = min(max(self.truth, 0.0), 1.0)
        self.burden = min(max(self.burden, 0.0), 5.0)

    def snapshot(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "love": round(self.love, 4),
            "life": round(self.life, 4),
            "integrity": round(self.integrity, 4),
            "hope": round(self.hope, 4),
            "truth": round(self.truth, 4),
            "burden": round(self.burden, 4),
            "scars": list(self.scars),
            "insights": list(self.insights),
        }

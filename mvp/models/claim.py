"""
GAIA MVP — Claim Model
The atomic unit of GAIA's truth system.
Every assertion that enters GAIA becomes a Claim.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import uuid


class Claim(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    statement: str
    sources: List[str] = []
    confidence: float = 0.5
    status: str = "unknown"  # unknown | supported | speculative | disputed | verified
    domain: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    contradiction_ids: List[str] = []

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def summary(self) -> str:
        snippet = self.statement[:72] + "..." if len(self.statement) > 72 else self.statement
        return f"[{self.status.upper()} @{self.confidence:.2f}] '{snippet}'"

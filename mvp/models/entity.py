"""
GAIA MVP — Entity Model
A typed object in GAIA's world model.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any
import uuid


class Entity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    name: str
    attributes: Dict[str, Any] = {}

    def __repr__(self) -> str:
        return f"Entity(type={self.type}, name={self.name})"

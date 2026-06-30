"""
GAIA Simulation Event
A discrete hypothetical change injected into a simulation sandbox.

Events are the 'what if' inputs:
  - 'What if fuel tax increases 10%?'
  - 'What if renewable capacity doubles?'
  - 'What if a key supply chain node fails?'

Each event has:
  - A description (human-readable)
  - Parameters (typed key-value changes)
  - An apply() method that mutates sandbox state
  - A complete audit trail

Events NEVER touch real world state — only sandbox state.
"""

import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class EventParameter(BaseModel):
    key: str
    value: Any
    unit: Optional[str] = None
    description: Optional[str] = None


class Event:
    """
    A hypothetical change to inject into a simulation.
    """

    def __init__(
        self,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        target_entity: Optional[str] = None,
        target_claim:  Optional[str] = None,
        category: str = "general"
    ):
        self.id           = f"evt_{str(uuid.uuid4())[:8]}"
        self.description  = description
        self.parameters   = parameters or {}
        self.target_entity = target_entity
        self.target_claim  = target_claim
        self.category     = category
        self.created_at   = datetime.utcnow().isoformat()

    def apply(self, state) -> Dict[str, Any]:
        """
        Apply this event to a sandbox state.
        Default: update metrics and claim confidence if targeted.
        Override in subclasses for domain-specific logic.
        Returns a mutation record.
        """
        mutations = {
            "event_id":    self.id,
            "description": self.description,
            "changes":     []
        }

        # Apply parameter changes to sandbox metrics
        for key, value in self.parameters.items():
            old = state.metrics.get(key)
            state.metrics[key] = value
            mutations["changes"].append({
                "type": "metric",
                "key":  key,
                "from": old,
                "to":   value
            })

        # Adjust targeted claim confidence if provided
        if self.target_claim and self.target_claim in state.claims:
            claim = state.claims[self.target_claim]
            old_conf = claim.get("confidence", 0.5)
            delta = self.parameters.get("confidence_delta", 0)
            new_conf = round(max(0.0, min(1.0, old_conf + delta)), 4)
            state.claims[self.target_claim]["confidence"] = new_conf
            mutations["changes"].append({
                "type":     "claim_confidence",
                "claim_id": self.target_claim,
                "from":     old_conf,
                "to":       new_conf
            })

        return mutations

    def __repr__(self) -> str:
        return (
            f"Event(id={self.id}, "
            f"description='{self.description[:50]}', "
            f"category={self.category})"
        )

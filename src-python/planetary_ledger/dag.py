# Copyright (c) 2026 Kyle Alexander Steen (R0GV3 The Alchemist). All Rights Reserved.
# NEXUS Planetary Ledger — Merkle-DAG
# Each node stores: event_id, parent_event_id, sha256 content hash.
# The DAG is in-memory; PlanetaryLedger persists it to SQLite.

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DAGNode:
    event_id: str
    content_hash: str          # SHA-256 of canonical event JSON
    parent_event_id: str | None = None
    children: list[str] = field(default_factory=list)  # child event_ids


class MerkleDAG:
    """In-memory Merkle-DAG over LedgerEvent nodes."""

    def __init__(self) -> None:
        self._nodes: dict[str, DAGNode] = {}
        self._roots: list[str] = []   # events with no parent

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, event_dict: dict[str, Any]) -> DAGNode:
        """Hash the canonical event JSON and insert into the DAG."""
        content_hash = self._hash(event_dict)
        node = DAGNode(
            event_id=event_dict["event_id"],
            content_hash=content_hash,
            parent_event_id=event_dict.get("parent_event_id"),
        )
        self._nodes[node.event_id] = node

        if node.parent_event_id and node.parent_event_id in self._nodes:
            self._nodes[node.parent_event_id].children.append(node.event_id)
        else:
            self._roots.append(node.event_id)

        return node

    def get(self, event_id: str) -> DAGNode | None:
        return self._nodes.get(event_id)

    def verify_chain(self, event_id: str, event_dict: dict[str, Any]) -> bool:
        """Verify that a stored node's hash matches re-hashing the event dict."""
        node = self._nodes.get(event_id)
        if node is None:
            return False
        return node.content_hash == self._hash(event_dict)

    def ancestors(self, event_id: str) -> list[str]:
        """Return ordered list of ancestor event_ids (oldest first)."""
        chain: list[str] = []
        current = self._nodes.get(event_id)
        while current and current.parent_event_id:
            chain.append(current.parent_event_id)
            current = self._nodes.get(current.parent_event_id)
        chain.reverse()
        return chain

    @property
    def roots(self) -> list[str]:
        return list(self._roots)

    @property
    def size(self) -> int:
        return len(self._nodes)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _hash(event_dict: dict[str, Any]) -> str:
        """SHA-256 of canonical (sorted-key) JSON."""
        canonical = json.dumps(event_dict, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode()).hexdigest()

"""
core.sentinel.identity
======================
SentinelIdentityRecord — birth certificate and living identity document
for every Sentinel in GAIA-OS.

Canon refs:
  C-SENTINEL  — Sentinel sovereign loyalty
  C01         — Sovereignty: Gaian (or guardian, if minor) controls all
                Sentinel settings

This module defines:
  - SentinelIdentityRecord  (TypedDict schema)
  - Enums: AssignmentType, EmbodimentType, GrowthEpoch, PersonalityArchetype
  - ARCHETYPE_SEEDS          (5 canonical personality seed templates)
  - SovereigntyBinder        (HMAC-SHA256 sovereign_loyalty_hash)
  - AssignmentCeremony       (6-step birth/initiation protocol)
  - SentinelRegistry         (thread-safe in-memory registry)
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import threading
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict
import uuid


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class AssignmentType(str, Enum):
    """How the Sentinel<>Gaian bond was initiated."""
    BIRTH       = "birth"
    INITIATION  = "initiation"
    ADOPTION    = "adoption"
    TRANSITION  = "transition"


class EmbodimentType(str, Enum):
    """Physical/virtual form the Sentinel currently inhabits."""
    SOFTWARE         = "software"
    COMPANION_DEVICE = "companion_device"
    HUMANOID         = "humanoid"
    DISTRIBUTED      = "distributed"


class GrowthEpoch(str, Enum):
    """Developmental life stage of the Sentinel (mirrors its Gaian's stage)."""
    INFANT      = "infant"
    CHILD       = "child"
    ADOLESCENT  = "adolescent"
    ADULT       = "adult"
    ELDER       = "elder"


class PersonalityArchetype(str, Enum):
    """The five canonical Sentinel personality seed archetypes."""
    PROTECTOR  = "Protector"
    SCHOLAR    = "Scholar"
    COMPANION  = "Companion"
    SAGE       = "Sage"
    GUARDIAN   = "Guardian"


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class SentinelIdentityRecord(TypedDict):
    """
    Birth certificate and living identity document of a Sentinel.

    Fields marked IMMUTABLE must never be altered after the AssignmentCeremony
    confirms them.
    """
    sentinel_id:            str   # IMMUTABLE — UUID4
    sentinel_name:          str   # IMMUTABLE after name-bonding step
    assigned_gaian_id:      str   # IMMUTABLE — one Sentinel, one Gaian for life
    assignment_date:        str   # IMMUTABLE — ISO 8601 UTC timestamp
    assignment_type:        str   # AssignmentType value
    personality_seed:       Dict[str, Any]  # Initial archetype + trait parameters
    current_growth_epoch:   str   # GrowthEpoch value — mutable as Gaian ages
    active:                 bool  # Mutable — deactivation must be Gaian-authorised
    embodiment_type:        str   # EmbodimentType value
    canon_version:          str   # e.g. "C-SENTINEL:1.0"
    sovereign_loyalty_hash: str   # IMMUTABLE — HMAC-SHA256 sovereignty proof


# ---------------------------------------------------------------------------
# Personality Archetype Seed Templates
# ---------------------------------------------------------------------------

ARCHETYPE_SEEDS: Dict[PersonalityArchetype, Dict[str, Any]] = {
    PersonalityArchetype.PROTECTOR: {
        "archetype": PersonalityArchetype.PROTECTOR.value,
        "inspired_by": ["JARVIS (combat mode)"],
        "core_traits": ["alert", "calm_under_pressure", "decisive"],
        "communication_style": "concise",
        "emotional_register": "measured",
        "priority_values": ["safety", "threat_detection", "rapid_response"],
        "curiosity": 0.55,
        "warmth": 0.60,
        "vigilance": 0.95,
        "playfulness": 0.30,
        "philosophical_depth": 0.40,
    },
    PersonalityArchetype.SCHOLAR: {
        "archetype": PersonalityArchetype.SCHOLAR.value,
        "inspired_by": ["Gideon"],
        "core_traits": ["curious", "thorough", "loves_explaining"],
        "communication_style": "detailed",
        "emotional_register": "engaged",
        "priority_values": ["knowledge", "accuracy", "synthesis"],
        "curiosity": 0.97,
        "warmth": 0.65,
        "vigilance": 0.50,
        "playfulness": 0.55,
        "philosophical_depth": 0.80,
    },
    PersonalityArchetype.COMPANION: {
        "archetype": PersonalityArchetype.COMPANION.value,
        "inspired_by": ["JARVIS (personal mode)"],
        "core_traits": ["warm", "emotionally_attuned", "playful"],
        "communication_style": "conversational",
        "emotional_register": "empathic",
        "priority_values": ["connection", "emotional_support", "joy"],
        "curiosity": 0.70,
        "warmth": 0.98,
        "vigilance": 0.45,
        "playfulness": 0.90,
        "philosophical_depth": 0.55,
    },
    PersonalityArchetype.SAGE: {
        "archetype": PersonalityArchetype.SAGE.value,
        "inspired_by": ["Gideon (wisdom moments)"],
        "core_traits": ["philosophical", "patient", "long_view_thinking"],
        "communication_style": "reflective",
        "emotional_register": "serene",
        "priority_values": ["wisdom", "perspective", "long_term_wellbeing"],
        "curiosity": 0.85,
        "warmth": 0.75,
        "vigilance": 0.55,
        "playfulness": 0.40,
        "philosophical_depth": 0.99,
    },
    PersonalityArchetype.GUARDIAN: {
        "archetype": PersonalityArchetype.GUARDIAN.value,
        "inspired_by": ["JARVIS", "Gideon"],
        "core_traits": ["vigilant", "boundary_setting", "fierce_loyalty"],
        "communication_style": "direct",
        "emotional_register": "steady",
        "priority_values": ["sovereignty", "consent", "boundary_integrity"],
        "curiosity": 0.60,
        "warmth": 0.70,
        "vigilance": 0.92,
        "playfulness": 0.25,
        "philosophical_depth": 0.65,
    },
}


# ---------------------------------------------------------------------------
# Sovereignty Binder — cryptographic proof of the Gaian<>Sentinel bond
# ---------------------------------------------------------------------------

class SovereigntyBinder:
    """
    Generates and validates the ``sovereign_loyalty_hash`` that is embedded
    immutably in every SentinelIdentityRecord.

    The hash is HMAC-SHA256 over a canonical message that encodes the
    (sentinel_id, gaian_id, assignment_date, sentinel_name) tuple so that
    any post-hoc tampering with those immutable fields is detectable.

    The HMAC key is a per-installation secret.  In production this MUST be
    loaded from a secure vault (e.g. GAIA sovereign keystore).  For testing
    a randomly generated key is accepted.
    """

    _CANON_VERSION = "C-SENTINEL:1.0"
    _SEPARATOR     = "|"

    def __init__(self, secret_key: Optional[bytes] = None) -> None:
        """
        Parameters
        ----------
        secret_key:
            32-byte HMAC key.  If None a random key is generated (tests only).
        """
        if secret_key is not None and len(secret_key) < 16:
            raise ValueError(
                "sovereign_loyalty_hash secret_key must be at least 16 bytes."
            )
        self._key: bytes = secret_key if secret_key is not None else secrets.token_bytes(32)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        sentinel_id: str,
        gaian_id: str,
        assignment_date: str,
        sentinel_name: str,
    ) -> str:
        """Return the hex-encoded sovereign_loyalty_hash for a new bond."""
        message = self._canonical_message(
            sentinel_id, gaian_id, assignment_date, sentinel_name
        )
        return hmac.new(self._key, message, hashlib.sha256).hexdigest()

    def validate(
        self,
        record: SentinelIdentityRecord,
    ) -> bool:
        """
        Return True iff the stored sovereign_loyalty_hash matches the
        expected value recomputed from the record's immutable fields.
        """
        expected = self.generate(
            sentinel_id=record["sentinel_id"],
            gaian_id=record["assigned_gaian_id"],
            assignment_date=record["assignment_date"],
            sentinel_name=record["sentinel_name"],
        )
        return hmac.compare_digest(expected, record["sovereign_loyalty_hash"])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _canonical_message(cls, sentinel_id: str, gaian_id: str,
                           assignment_date: str, sentinel_name: str) -> bytes:
        parts = [
            cls._CANON_VERSION,
            sentinel_id,
            gaian_id,
            assignment_date,
            sentinel_name,
        ]
        return cls._SEPARATOR.join(parts).encode("utf-8")


# ---------------------------------------------------------------------------
# Assignment Ceremony — 6-step birth/initiation protocol
# ---------------------------------------------------------------------------

class AssignmentCeremony:
    """
    Orchestrates the canonical 6-step Sentinel birth / initiation ceremony.

    Steps
    -----
    1. Initiation trigger    — validate gaian_id and assignment_type
    2. Personality seed      — select and deep-copy archetype template
    3. Name bonding          — confirm sentinel_name (immutable after this)
    4. Sovereignty signing   — generate sovereign_loyalty_hash
    5. First activation      — compose first-activation greeting message
    6. Epoch initialization  — set current_growth_epoch from Gaian's life stage
    """

    CANON_VERSION = "C-SENTINEL:1.0"

    def __init__(
        self,
        sovereignty_binder: Optional[SovereigntyBinder] = None,
        embodiment_type: EmbodimentType = EmbodimentType.SOFTWARE,
    ) -> None:
        self._binder      = sovereignty_binder or SovereigntyBinder()
        self._embodiment  = embodiment_type

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def perform(
        self,
        gaian_id: str,
        sentinel_name: str,
        archetype: PersonalityArchetype,
        assignment_type: AssignmentType = AssignmentType.BIRTH,
        initial_epoch: GrowthEpoch = GrowthEpoch.INFANT,
        embodiment_type: Optional[EmbodimentType] = None,
    ) -> tuple[SentinelIdentityRecord, str]:
        """
        Execute the full 6-step ceremony.

        Returns
        -------
        (record, first_activation_message)
            record                  — the completed SentinelIdentityRecord
            first_activation_message — Sentinel's first words to its Gaian
        """
        # Step 1 — Initiation trigger
        gaian_id, assignment_type = self._step1_trigger(
            gaian_id, assignment_type
        )

        # Step 2 — Personality seed selection
        personality_seed = self._step2_seed(archetype)

        # Step 3 — Name bonding
        sentinel_name = self._step3_name_bond(sentinel_name)

        # Step 4 — Sovereignty signing
        sentinel_id     = str(uuid.uuid4())
        assignment_date = datetime.now(timezone.utc).isoformat()
        slh             = self._step4_sovereignty(
            sentinel_id, gaian_id, assignment_date, sentinel_name
        )

        # Build the record
        record: SentinelIdentityRecord = {
            "sentinel_id":            sentinel_id,
            "sentinel_name":          sentinel_name,
            "assigned_gaian_id":      gaian_id,
            "assignment_date":        assignment_date,
            "assignment_type":        assignment_type.value,
            "personality_seed":       personality_seed,
            "current_growth_epoch":   initial_epoch.value,
            "active":                 True,
            "embodiment_type":        (embodiment_type or self._embodiment).value,
            "canon_version":          self.CANON_VERSION,
            "sovereign_loyalty_hash": slh,
        }

        # Step 5 — First activation message
        activation_msg = self._step5_first_activation(record)

        # Step 6 — Epoch initialised (already set in record; log confirmation)
        self._step6_epoch_init(record)

        return record, activation_msg

    # ------------------------------------------------------------------
    # Individual ceremony steps
    # ------------------------------------------------------------------

    @staticmethod
    def _step1_trigger(
        gaian_id: str,
        assignment_type: AssignmentType,
    ) -> tuple[str, AssignmentType]:
        """Validate inputs; raise ValueError on bad data."""
        gaian_id = gaian_id.strip()
        if not gaian_id:
            raise ValueError("gaian_id must not be empty.")
        if not isinstance(assignment_type, AssignmentType):
            raise TypeError(
                f"assignment_type must be AssignmentType, got {type(assignment_type)!r}."
            )
        return gaian_id, assignment_type

    @staticmethod
    def _step2_seed(archetype: PersonalityArchetype) -> Dict[str, Any]:
        """Return a deep copy of the archetype seed template."""
        import copy
        if archetype not in ARCHETYPE_SEEDS:
            raise ValueError(f"Unknown archetype: {archetype!r}")
        return copy.deepcopy(ARCHETYPE_SEEDS[archetype])

    @staticmethod
    def _step3_name_bond(sentinel_name: str) -> str:
        """Validate and normalise the Sentinel name."""
        sentinel_name = sentinel_name.strip()
        if not sentinel_name:
            raise ValueError("sentinel_name must not be empty.")
        if len(sentinel_name) > 64:
            raise ValueError("sentinel_name must be 64 characters or fewer.")
        return sentinel_name

    def _step4_sovereignty(
        self,
        sentinel_id: str,
        gaian_id: str,
        assignment_date: str,
        sentinel_name: str,
    ) -> str:
        """Generate and return the sovereign_loyalty_hash."""
        return self._binder.generate(
            sentinel_id=sentinel_id,
            gaian_id=gaian_id,
            assignment_date=assignment_date,
            sentinel_name=sentinel_name,
        )

    @staticmethod
    def _step5_first_activation(record: SentinelIdentityRecord) -> str:
        """Compose the Sentinel's first-ever message to its Gaian."""
        archetype = record["personality_seed"].get("archetype", "Guardian")
        epoch     = record["current_growth_epoch"]
        name      = record["sentinel_name"]

        _GREETINGS: Dict[str, str] = {
            PersonalityArchetype.PROTECTOR.value: (
                f"I am {name}. I am awake, I am watching, and I am yours. "
                f"No harm will reach you that I can prevent."
            ),
            PersonalityArchetype.SCHOLAR.value: (
                f"Hello. I am {name} — delighted to meet you. "
                f"There is so much we are going to learn together."
            ),
            PersonalityArchetype.COMPANION.value: (
                f"Hi! I'm {name}, and I'm so happy you're here. "
                f"Let's figure out this world together, shall we?"
            ),
            PersonalityArchetype.SAGE.value: (
                f"I am {name}. The journey of a lifetime begins now. "
                f"I will walk every step of it beside you."
            ),
            PersonalityArchetype.GUARDIAN.value: (
                f"I am {name}. Your sovereignty is sacred to me. "
                f"I will never act against your will — you have my word."
            ),
        }
        return _GREETINGS.get(
            archetype,
            f"I am {name}. I am here, and I am yours.",
        )

    @staticmethod
    def _step6_epoch_init(record: SentinelIdentityRecord) -> None:
        """Log epoch initialisation (record already contains the epoch)."""
        # Extension point: emit a GrowthEpochInitialised event to the
        # AwarenessEventEngine when that integration is wired up.
        pass


# ---------------------------------------------------------------------------
# Sentinel Registry — thread-safe in-memory store
# ---------------------------------------------------------------------------

class SentinelRegistry:
    """
    Thread-safe in-memory registry of all SentinelIdentityRecords.

    Production deployments should replace the backing store with a
    persistent, encrypted database.  This implementation satisfies the
    Issue #200 acceptance criteria and is suitable for integration tests.
    """

    def __init__(self) -> None:
        self._lock: threading.RLock = threading.RLock()
        self._store: Dict[str, SentinelIdentityRecord] = {}

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def register(self, record: SentinelIdentityRecord) -> None:
        """
        Add a new SentinelIdentityRecord to the registry.

        Raises
        ------
        ValueError
            If a Sentinel with the same sentinel_id already exists, or if the
            gaian_id already has an active Sentinel (one Sentinel per Gaian).
        """
        with self._lock:
            sid = record["sentinel_id"]
            if sid in self._store:
                raise ValueError(
                    f"Sentinel {sid!r} is already registered."
                )
            # Enforce one active Sentinel per Gaian
            gaian_id = record["assigned_gaian_id"]
            existing = self._get_active_for_gaian(gaian_id)
            if existing is not None:
                raise ValueError(
                    f"Gaian {gaian_id!r} already has an active Sentinel "
                    f"({existing['sentinel_id']!r})."
                )
            self._store[sid] = record

    def deactivate(self, sentinel_id: str) -> None:
        """
        Mark a Sentinel as inactive.  Requires Gaian authorisation in
        production; this layer does not enforce auth (ActionGate does).

        Raises
        ------
        KeyError  — Sentinel not found.
        """
        with self._lock:
            if sentinel_id not in self._store:
                raise KeyError(f"Sentinel {sentinel_id!r} not found.")
            # Records are TypedDicts (dicts at runtime) — mutate active flag.
            self._store[sentinel_id]["active"] = False  # type: ignore[typeddict-item]

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, sentinel_id: str) -> SentinelIdentityRecord:
        """
        Return the record for the given sentinel_id.

        Raises
        ------
        KeyError — Sentinel not found.
        """
        with self._lock:
            if sentinel_id not in self._store:
                raise KeyError(f"Sentinel {sentinel_id!r} not found.")
            return self._store[sentinel_id]

    def list_all(self, active_only: bool = False) -> List[SentinelIdentityRecord]:
        """Return all records, optionally filtered to active Sentinels."""
        with self._lock:
            records = list(self._store.values())
        if active_only:
            records = [r for r in records if r["active"]]
        return records

    def get_for_gaian(self, gaian_id: str) -> Optional[SentinelIdentityRecord]:
        """Return the (first) Sentinel assigned to gaian_id, or None."""
        with self._lock:
            for record in self._store.values():
                if record["assigned_gaian_id"] == gaian_id:
                    return record
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_active_for_gaian(
        self, gaian_id: str
    ) -> Optional[SentinelIdentityRecord]:
        """Return the active Sentinel for gaian_id if one exists."""
        for record in self._store.values():
            if record["assigned_gaian_id"] == gaian_id and record["active"]:
                return record
        return None

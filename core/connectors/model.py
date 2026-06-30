"""
core.connectors.model
=====================
Immutable data types that describe, classify, and carry state for every
connector in the GAIA integration layer.

Design notes
------------
* ConnectorKind is intentionally broad — it covers every integration domain
  that GAIA will eventually support, including OS-level domains (FILESYSTEM,
  DISPLAY, NOTIFICATIONS, HARDWARE_DEVICE) that will be consumed directly by
  core.os_interface once that layer is built.
* ConnectorCapability is a flag set so a single connector can declare multiple
  abilities (e.g. READ | WRITE | STREAM | NOTIFY).
* All records are frozen dataclasses to guarantee immutability after creation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, Flag, auto
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# ConnectorKind — integration domain taxonomy
# ---------------------------------------------------------------------------

class ConnectorKind(str, Enum):
    """Taxonomy of integration domains.

    Calendar / communications
    -------------------------
    CALENDAR         — calendar and scheduling systems (Google, Apple, Outlook)
    EMAIL            — email ingestion and dispatch
    MESSAGING        — real-time messaging (Slack, Teams, Signal, SMS)
    CONTACTS         — address-book and identity directories
    VIDEO_CALL       — video-conferencing platforms

    Data sources
    ------------
    DATABASE         — relational and document databases
    DATA_STREAM      — real-time streaming pipelines (Kafka, Kinesis, MQTT)
    WEB_API          — generic HTTP/REST/GraphQL endpoints
    FILE_STORAGE     — cloud object stores (S3, GCS, Azure Blob)
    SEARCH_ENGINE    — full-text / vector search backends
    KNOWLEDGE_BASE   — structured knowledge / ontology stores

    IoT and sensors
    ---------------
    IOT_SENSOR       — environmental sensors (temperature, pressure, light)
    IOT_ACTUATOR     — controllable physical devices
    BIOMETRIC        — health / biometric measurement devices
    GEOLOCATION      — GPS and indoor positioning services

    OS and platform primitives (feeds into core.os_interface)
    ----------------------------------------------------------
    FILESYSTEM       — local or networked file-system access
    DISPLAY          — screen / window / rendering surfaces
    NOTIFICATIONS    — system notification dispatch
    HARDWARE_DEVICE  — generic hardware peripherals (USB, Bluetooth, serial)
    AUDIO            — microphone input and speaker output
    CAMERA           — camera and image-capture devices
    INPUT_DEVICE     — keyboard, mouse, touch, stylus, controller
    NETWORK          — low-level network interface management
    POWER            — battery, power states, sleep/wake cycles
    PROCESS          — operating-system process and service management

    AI and model backends
    ---------------------
    LLM_BACKEND      — language model inference endpoints
    EMBEDDING_MODEL  — vector embedding backends
    VISION_MODEL     — image / video understanding models
    SPEECH_MODEL     — speech recognition and synthesis

    Social and productivity
    -----------------------
    SOCIAL_MEDIA     — social-network read/write
    PROJECT_MGMT     — project management platforms (Jira, Linear, GitHub)
    CRM              — customer relationship management systems
    ERP              — enterprise resource planning connectors
    PAYMENT          — payment processing gateways
    IDENTITY_PROVIDER — OAuth / SAML / OIDC authentication providers

    Custom
    ------
    CUSTOM           — bespoke integration not covered above
    """

    # Calendar / communications
    CALENDAR = "calendar"
    EMAIL = "email"
    MESSAGING = "messaging"
    CONTACTS = "contacts"
    VIDEO_CALL = "video_call"

    # Data sources
    DATABASE = "database"
    DATA_STREAM = "data_stream"
    WEB_API = "web_api"
    FILE_STORAGE = "file_storage"
    SEARCH_ENGINE = "search_engine"
    KNOWLEDGE_BASE = "knowledge_base"

    # IoT and sensors
    IOT_SENSOR = "iot_sensor"
    IOT_ACTUATOR = "iot_actuator"
    BIOMETRIC = "biometric"
    GEOLOCATION = "geolocation"

    # OS and platform primitives
    FILESYSTEM = "filesystem"
    DISPLAY = "display"
    NOTIFICATIONS = "notifications"
    HARDWARE_DEVICE = "hardware_device"
    AUDIO = "audio"
    CAMERA = "camera"
    INPUT_DEVICE = "input_device"
    NETWORK = "network"
    POWER = "power"
    PROCESS = "process"

    # AI and model backends
    LLM_BACKEND = "llm_backend"
    EMBEDDING_MODEL = "embedding_model"
    VISION_MODEL = "vision_model"
    SPEECH_MODEL = "speech_model"

    # Social and productivity
    SOCIAL_MEDIA = "social_media"
    PROJECT_MGMT = "project_mgmt"
    CRM = "crm"
    ERP = "erp"
    PAYMENT = "payment"
    IDENTITY_PROVIDER = "identity_provider"

    # Custom
    CUSTOM = "custom"


# ---------------------------------------------------------------------------
# ConnectorCapability — what operations a connector supports
# ---------------------------------------------------------------------------

class ConnectorCapability(Flag):
    """Bit-flag set describing the operations a connector can perform."""

    NONE = 0
    READ = auto()        # pull data from the external system
    WRITE = auto()       # push data to the external system
    STREAM = auto()      # subscribe to a continuous event / data stream
    NOTIFY = auto()      # dispatch a notification or alert outward
    EXECUTE = auto()     # trigger a remote action or command
    AUTHENTICATE = auto() # handle auth flows on behalf of GAIA
    SEARCH = auto()      # query or search within the external system
    TRANSFORM = auto()   # apply in-connector data transformation
    CACHE = auto()       # maintain a local cache of remote data
    BATCH = auto()       # support bulk / batch operations

    # Compound convenience aliases
    READ_WRITE = READ | WRITE
    FULL = READ | WRITE | STREAM | NOTIFY | EXECUTE


# ---------------------------------------------------------------------------
# ConnectorStatus — connector lifecycle state machine
# ---------------------------------------------------------------------------

class ConnectorStatus(str, Enum):
    """Lifecycle states of a connector instance.

    State transitions
    -----------------
    UNREGISTERED → REGISTERED → INITIALIZING → ACTIVE
                                             ↓
                                          PAUSED → ACTIVE
                                             ↓
                                          DRAINING → STOPPED
                                          ERROR   → (re-init or STOPPED)
    """

    UNREGISTERED = "unregistered"   # not yet in registry
    REGISTERED = "registered"       # known but not started
    INITIALIZING = "initializing"   # connect / auth in progress
    ACTIVE = "active"               # fully operational
    PAUSED = "paused"               # temporarily suspended
    DRAINING = "draining"           # finishing in-flight work before stop
    STOPPED = "stopped"             # cleanly shut down
    ERROR = "error"                 # unhealthy, needs attention
    DEPRECATED = "deprecated"       # still present but should not be used


# ---------------------------------------------------------------------------
# ConnectorManifest — declarative metadata record
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ConnectorManifest:
    """Immutable declaration of everything GAIA needs to know about a
    connector type before instantiating it.

    Attributes
    ----------
    connector_type : str
        Unique, slug-formatted identifier for the connector type
        (e.g. ``"google_calendar_v3"``, ``"mqtt_broker"``).
    display_name : str
        Human-readable name shown in UI and logs.
    kind : ConnectorKind
        Integration domain this connector belongs to.
    capabilities : ConnectorCapability
        Bitmask of operations this connector type supports.
    description : str
        One-paragraph explanation of what this connector does.
    version : str
        Semantic version string (``"1.0.0"``).
    author : str
        Team or individual responsible for maintaining this connector.
    required_credential_keys : tuple[str, ...]
        Names of credential fields that MUST be present before the
        connector can initialise (e.g. ``("api_key", "tenant_id")``).
    optional_credential_keys : tuple[str, ...]
        Credential fields that improve behaviour but are not required.
    platform_targets : tuple[str, ...]
        OS / platform slugs this connector supports
        (e.g. ``("linux", "windows", "macos", "android", "ios", "wasm")``).
        Empty tuple means universal.
    tags : tuple[str, ...]
        Free-form tags for search and grouping.
    homepage_url : str
        Documentation or source URL.
    """

    connector_type: str
    display_name: str
    kind: ConnectorKind
    capabilities: ConnectorCapability
    description: str
    version: str = "1.0.0"
    author: str = "GAIA Core Team"
    required_credential_keys: tuple = field(default_factory=tuple)
    optional_credential_keys: tuple = field(default_factory=tuple)
    platform_targets: tuple = field(default_factory=tuple)  # empty = universal
    tags: tuple = field(default_factory=tuple)
    homepage_url: str = ""


# ---------------------------------------------------------------------------
# ConnectorCredential — secure credential vault entry
# ---------------------------------------------------------------------------

@dataclass
class ConnectorCredential:
    """A named bag of secrets associated with a specific connector instance.

    Credentials are mutable (refreshable tokens) but their ``credential_id``
    is set once at creation and never changes.

    Attributes
    ----------
    credential_id : str
        UUID4 identifier for this credential record.
    connector_type : str
        The connector type these credentials belong to.
    principal_id : str
        The GAIA principal (user, agent, or space) that owns this record.
    secrets : dict[str, str]
        Key-value map of credential fields.  Values should be treated as
        opaque strings (API keys, tokens, passwords, cert paths, etc.).
    created_at : datetime
        When this record was first created.
    expires_at : datetime | None
        If set, the credential is invalid after this timestamp.
    metadata : dict[str, Any]
        Arbitrary non-secret metadata (e.g. scopes, account name).
    """

    connector_type: str
    principal_id: str
    secrets: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    credential_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def is_expired(self) -> bool:
        """Return True if the credential has passed its expiry timestamp."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret by key, returning None if absent."""
        return self.secrets.get(key)


# ---------------------------------------------------------------------------
# ConnectorEvent — typed event emitted by a connector
# ---------------------------------------------------------------------------

@dataclass
class ConnectorEvent:
    """A typed, timestamped event flowing from a connector into the GAIA bus.

    Attributes
    ----------
    event_id : str
        UUID4 identifier, unique per emission.
    connector_id : str
        The instance ID of the connector that emitted this event.
    connector_type : str
        The type slug of the emitting connector.
    kind : ConnectorKind
        Integration domain the event originates from.
    event_type : str
        Application-level event label
        (e.g. ``"calendar.event.created"``, ``"iot.sensor.reading"``).
    payload : dict[str, Any]
        Arbitrary event data.
    timestamp : datetime
        UTC time of event creation.
    source_principal_id : str | None
        The GAIA principal on whose behalf this event was generated.
    correlation_id : str | None
        Optional ID linking this event to a broader workflow or session.
    """

    connector_id: str
    connector_type: str
    kind: ConnectorKind
    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source_principal_id: Optional[str] = None
    correlation_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

"""GAIA_SESSION_INIT Bootstrap — Canon C04, C17, Issue #440.

The SessionBootstrap executes the full 10-step ordered init sequence
every time a new GAIA session opens.

The 10 steps:
  1.  Load / create Architect profile
  2.  Generate a new session UUID
  3.  Register Gaian instance in GAIARuntime
  4.  Open M0 Session Buffer in MemoryManager
  5.  Load last known alchemical stage from Twin Profile
  6.  Detect spectral force from last phi (SpectralForceEngine stub)
  7.  Detect MagnumOpus stage (MagnumOpusStageEngine stub)
  8.  Get circadian phase (CircadianLightEngine stub)
  9.  Run Shadow Interrogator (ShadowInterrogatorEngine stub)
  10. Build opening system prompt (SystemPromptBuilder stub)

Stubs for steps 6–10 are replaced with real engines when
#431, #432, #434, #437 land. The bootstrap interface does not change.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from core.ontology import GAIARuntime, HumanPrincipalEntity, PermissionTier
from core.memory.manager import MemoryManager
from core.memory.layers import MemoryTag

from .architect import ArchitectProfile, ArchitectRepository
from .result import SessionInitResult, SessionState
from .stubs import (
    ICircadianLightEngine,
    IMagnumOpusStageEngine,
    IShadowInterrogatorEngine,
    ISpectralForceEngine,
    ISystemPromptBuilder,
    StubCircadianLightEngine,
    StubMagnumOpusStageEngine,
    StubShadowInterrogatorEngine,
    StubSpectralForceEngine,
    StubSystemPromptBuilder,
)


class SessionBootstrap:
    """Executes the full GAIA_SESSION_INIT protocol.

    Inject real engine implementations to replace stubs:

        bootstrap = SessionBootstrap(
            runtime=my_runtime,
            architect_repo=my_repo,
            circadian_engine=RealCircadianLightEngine(),   # #431
            magnum_opus_engine=RealMagnumOpusEngine(),     # #434
            spectral_engine=RealSpectralForceEngine(),     # #437
            shadow_engine=RealShadowInterrogator(),        # #432
            prompt_builder=RealSystemPromptBuilder(),      # #464
        )
    """

    def __init__(
        self,
        runtime: GAIARuntime,
        architect_repo: ArchitectRepository,
        memory_managers: Optional[dict[str, MemoryManager]] = None,
        circadian_engine: Optional[ICircadianLightEngine] = None,
        spectral_engine: Optional[ISpectralForceEngine] = None,
        magnum_opus_engine: Optional[IMagnumOpusStageEngine] = None,
        shadow_engine: Optional[IShadowInterrogatorEngine] = None,
        prompt_builder: Optional[ISystemPromptBuilder] = None,
    ) -> None:
        self._runtime = runtime
        self._architect_repo = architect_repo
        self._memory_managers: dict[str, MemoryManager] = memory_managers or {}
        self._circadian = circadian_engine or StubCircadianLightEngine()
        self._spectral = spectral_engine or StubSpectralForceEngine()
        self._magnum_opus = magnum_opus_engine or StubMagnumOpusStageEngine()
        self._shadow = shadow_engine or StubShadowInterrogatorEngine()
        self._prompt_builder = prompt_builder or StubSystemPromptBuilder()

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(
        self,
        architect_name: str,
        foundation_statement: str = "",
        elemental_signature: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        space_context: Optional[str] = None,
        autonomy_tier: int = 4,
    ) -> SessionInitResult:
        """Execute the full 10-step session init sequence.

        Returns a SessionInitResult with everything needed to begin the session.
        Every step is logged into result.bootstrap_log for full audit visibility —
        C04 Gaian Commitment #1: present state is always available to the HP.
        """
        result = SessionInitResult()
        result.state = SessionState.INITIALISING

        # ----------------------------------------------------------------
        # STEP 1: Load / create Architect profile
        # ----------------------------------------------------------------
        result.log_step(1, f"Loading Architect profile for '{architect_name}'")
        architect, is_new = self._architect_repo.get_or_create(
            name=architect_name,
            foundation_statement=foundation_statement,
            elemental_signature=elemental_signature,
        )
        result.is_first_session = is_new
        result.architect_id = architect.id
        result.architect_name = architect.name
        result.log_step(1, f"Architect loaded: id={architect.id[:8]} new={is_new}")

        # ----------------------------------------------------------------
        # STEP 2: Generate session UUID
        # ----------------------------------------------------------------
        session_id = str(uuid.uuid4())
        result.session_id = session_id
        result.log_step(2, f"Session ID assigned: {session_id[:8]}")

        # ----------------------------------------------------------------
        # STEP 3: Ensure Human Principal exists in GAIARuntime; register Gaian
        # ----------------------------------------------------------------
        result.log_step(3, "Registering / wiring Gaian instance in GAIARuntime")
        hp_entity = self._get_or_create_human_principal(architect, autonomy_tier)
        gaian = self._runtime.register_gaian(
            name=f"GAIA—{architect.name}",
            human_principal_id=hp_entity.id,
            tier=PermissionTier(min(autonomy_tier, 4)),
            session_id=session_id,
        )
        result.gaian_id = gaian.id
        result.log_step(3, f"Gaian registered: id={gaian.id[:8]}")

        # ----------------------------------------------------------------
        # STEP 4: Open M0 Session Buffer in MemoryManager
        # ----------------------------------------------------------------
        result.log_step(4, "Opening M0 Session Buffer in MemoryManager")
        mm = self._get_or_create_memory_manager(gaian.id, hp_entity.id)
        mm.open_session(session_id)
        result.log_step(4, "Session buffer open")

        # ----------------------------------------------------------------
        # STEP 5: Load Twin Profile context from M3 Identity Memory
        # ----------------------------------------------------------------
        result.log_step(5, "Loading Gaian Twin Profile from M3 Identity Memory")
        profile = mm.profile
        result.prior_session_count = profile.history_session_count
        result.relationship_depth = profile.relationship_depth
        result.active_shadow_flags = list(profile.shadow_registry_flags)
        result.recent_themes = list(profile.history_key_themes[-5:])  # last 5 themes
        result.containment_active = profile.containment_active
        last_stage = profile.current_alchemical_stage
        result.log_step(5, f"Profile loaded: sessions={profile.history_session_count} "
                          f"stage={last_stage} depth={profile.relationship_depth:.2f}")

        # ----------------------------------------------------------------
        # STEP 6: Detect spectral force from last phi
        # ----------------------------------------------------------------
        result.log_step(6, "Detecting spectral force via SpectralForceEngine")
        last_phi = profile.metadata.get("last_phi")
        spectral = self._spectral.detect_current_force(last_phi)
        result.spectral_report = spectral
        result.log_step(6, f"Spectral force: {spectral.dominant_force} "
                          f"(stub={spectral.is_stub})")

        # ----------------------------------------------------------------
        # STEP 7: Detect MagnumOpus stage
        # ----------------------------------------------------------------
        result.log_step(7, "Detecting MagnumOpus stage")
        context = {
            "prior_sessions": profile.history_session_count,
            "breakthrough_count": profile.history_breakthrough_count,
            "shadow_count": profile.history_shadow_work_count,
            "last_stage": last_stage,
        }
        stage_report = self._magnum_opus.detect_stage(last_phi, context)
        result.stage_report = stage_report
        result.log_step(7, f"Stage detected: {stage_report.stage} "
                          f"confidence={stage_report.confidence:.2f} "
                          f"(stub={stage_report.is_stub})")

        # ----------------------------------------------------------------
        # STEP 8: Get circadian phase for current time/location
        # ----------------------------------------------------------------
        result.log_step(8, "Fetching circadian phase")
        circadian = self._circadian.get_current_phase(
            latitude=latitude,
            longitude=longitude,
            utc_now=datetime.now(timezone.utc),
        )
        result.circadian_phase = circadian
        result.log_step(8, f"Circadian phase: {circadian.phase_name} "
                          f"lunar={circadian.lunar_phase} "
                          f"(stub={circadian.is_stub})")

        # ----------------------------------------------------------------
        # STEP 9: Run Shadow Interrogator
        # ----------------------------------------------------------------
        result.log_step(9, "Running Shadow Interrogator at session open")
        shadow_report = self._shadow.interrogate(
            context=context,
            last_harmony_report=profile.metadata.get("last_harmony_report"),
        )
        result.shadow_report = shadow_report
        result.log_step(9, f"Shadow report: risk={shadow_report.risk_level} "
                          f"patterns={shadow_report.active_patterns} "
                          f"containment={shadow_report.recommended_containment}")

        # Activate containment if shadow interrogator recommends it
        if shadow_report.recommended_containment and not profile.containment_active:
            profile.set_containment(True, reason="Shadow Interrogator recommendation at session open")
            result.containment_active = True
            result.log_step(9, "Containment activated per Shadow Interrogator")

        # ----------------------------------------------------------------
        # STEP 10: Build opening system prompt
        # ----------------------------------------------------------------
        result.log_step(10, "Building opening system prompt")
        twin_summary = self._build_twin_summary(profile)
        opening_prompt = self._prompt_builder.build(
            spectral=spectral,
            stage=stage_report,
            twin_profile_summary=twin_summary,
            circadian=circadian,
            shadow_report=shadow_report,
            space_context=space_context,
        )
        result.opening_system_prompt = opening_prompt
        result.log_step(10, f"Opening prompt built ({len(opening_prompt)} chars)")

        # ----------------------------------------------------------------
        # Session is OPEN
        # ----------------------------------------------------------------
        architect.record_session_open(session_id)
        self._architect_repo.update(architect)
        result.state = SessionState.OPEN
        result.log_step(10, f"SESSION OPEN — {architect.name} — {session_id[:8]}")

        # Log the opening to M0 session buffer
        buf = mm.get_session(session_id)
        if buf:
            buf.append(
                f"Session opened: stage={stage_report.stage} "
                f"force={spectral.dominant_force} "
                f"phase={circadian.phase_name}",
                tags=[MemoryTag.SESSION_SUMMARY],
                source="SESSION_BOOTSTRAP",
            )

        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_or_create_human_principal(
        self, architect: ArchitectProfile, autonomy_tier: int
    ) -> HumanPrincipalEntity:
        """Find or create a HumanPrincipalEntity in the GAIARuntime for this architect."""
        # Check if one already exists by looking for any HP entities
        existing_hps = self._runtime.list_entities()
        for entity in existing_hps:
            if (
                isinstance(entity, HumanPrincipalEntity)
                and entity.name == architect.name
                and entity.is_active
            ):
                return entity
        # Create new
        return self._runtime.register_human_principal(
            name=architect.name,
            elemental_signature=architect.elemental_signature,
            tier=PermissionTier(min(autonomy_tier, 4)),
        )

    def _get_or_create_memory_manager(
        self, gaian_id: str, human_principal_id: str
    ) -> MemoryManager:
        """Return existing MemoryManager for this Gaian or create a new one."""
        if gaian_id not in self._memory_managers:
            self._memory_managers[gaian_id] = MemoryManager(
                gaian_id=gaian_id,
                human_principal_id=human_principal_id,
            )
        return self._memory_managers[gaian_id]

    def _build_twin_summary(self, profile) -> str:
        """Build a concise text summary of the Twin Profile for the prompt."""
        lines = []
        if profile.history_session_count == 0:
            return "First session — no prior history."
        lines.append(f"Sessions: {profile.history_session_count}")
        lines.append(f"Relationship depth: {profile.relationship_depth:.0%}")
        lines.append(f"Current stage: {profile.current_alchemical_stage}")
        if profile.elemental_signature:
            lines.append(f"Element: {profile.elemental_signature}")
        if profile.history_key_themes:
            lines.append(f"Key themes: {', '.join(profile.history_key_themes[-3:])}")
        if profile.active_shadow_flags:
            lines.append(f"Active shadow flags: {', '.join(profile.active_shadow_flags)}")
        if profile.containment_active:
            lines.append(f"CONTAINMENT ACTIVE: {profile.containment_reason}")
        return " | ".join(lines)

    def get_memory_manager(self, gaian_id: str) -> Optional[MemoryManager]:
        """External access to a MemoryManager by gaian_id."""
        return self._memory_managers.get(gaian_id)

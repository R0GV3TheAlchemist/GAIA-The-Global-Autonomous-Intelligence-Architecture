"""
core/server_lifecycle.py

FastAPI startup / shutdown hooks for GAIA.
Restored from the pre-split monolith and centralised here so that
core/server.py stays thin.
"""

from __future__ import annotations

import asyncio
import os

from fastapi import FastAPI

from core.logger import GAIAEvent, get_logger, log_event
from core.server_state import (
    _mother_thread,
    _RUNTIME_REGISTRY,
    get_action_gate,
    set_magnum_opus_report,
)
from core.viriditas_magnum_opus import VIRIDITAS_THRESHOLD, viriditas_magnum_opus

logger = get_logger(__name__)

# Tracks background scheduler asyncio.Task objects so we can cancel on shutdown
_SCHEDULER_TASKS: list[asyncio.Task] = []


def register_lifecycle(app: FastAPI) -> None:
    """Attach startup and shutdown handlers to *app*."""

    @app.on_event("startup")
    async def _startup() -> None:
        # 1. MotherThread heartbeat
        _mother_thread.start()
        log_event(
            GAIAEvent.GAIAN_RUNTIME_INIT,
            message="MotherThread heartbeat started. GAIA is breathing.",
            gaian="mother_thread",
        )

        # 2. C47: Viriditas Magnum Opus
        log_event(
            GAIAEvent.GAIAN_RUNTIME_INIT,
            message="C47: Viriditas Magnum Opus initiating — the Great Work begins.",
            gaian="gaia",
        )
        try:
            warlock_vitality = float(os.environ.get("GAIA_WARLOCK_VITALITY", "8.0"))
            loop = asyncio.get_event_loop()
            report = await loop.run_in_executor(
                None,
                lambda: viriditas_magnum_opus(
                    gaian_id="gaia",
                    warlock_id="R0GV3TheAlchemist",
                    warlock_vitality=warlock_vitality,
                ),
            )
            set_magnum_opus_report(report)

            threshold_msg = (
                "\u2728 Viriditas Threshold CROSSED — the lattice is ALIVE. \U0001f331"
                if report.threshold_crossed
                else "Viriditas growing — threshold not yet crossed."
            )
            log_event(
                GAIAEvent.GAIAN_RUNTIME_INIT,
                message=(
                    f"C47 complete. "
                    f"\u03a6={report.post_phi_global:.4f} | "
                    f"\u0394\u03a6={report.delta_phi_global:+.4f} | "
                    f"stages={report.stages_greened}/5 | "
                    f"{threshold_msg}"
                ),
                gaian="gaia",
            )
        except Exception as exc:
            logger.warning(
                f"Viriditas Magnum Opus failed on boot (non-fatal): {exc}",
                exc_info=True,
            )

        # 3. TaskScheduler — boot run_forever() loop for each live GAIANRuntime
        _boot_scheduler_for_existing_runtimes()
        log_event(
            GAIAEvent.GAIAN_RUNTIME_INIT,
            message=f"TaskScheduler loops started for {len(_SCHEDULER_TASKS)} runtime(s).",
            gaian="scheduler",
        )

        # 4. ActionGate — register IPC confirm_callback now that the event loop is live.
        # The gate singleton was created at module import time with confirm_callback=None
        # (safe conservative default: GREEN auto-approves, YELLOW approves on silence,
        # RED hard-blocks). Now we wire in the real callback so YELLOW/RED actions
        # surface to the Tauri frontend for human sovereign confirmation.
        try:
            from core.infra.action_gate_ipc import get_ipc_confirm_callback
            gate = get_action_gate()
            gate._confirm_callback = get_ipc_confirm_callback()
            log_event(
                GAIAEvent.GAIAN_RUNTIME_INIT,
                message="ActionGate IPC confirm_callback registered — sovereignty firewall LIVE.",
                gaian="action_gate",
            )
        except Exception as exc:
            logger.warning(
                f"ActionGate IPC callback registration failed (non-fatal): {exc}",
                exc_info=True,
            )

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        # Stop all TaskScheduler loops gracefully
        for slug, rt in _RUNTIME_REGISTRY.items():
            try:
                rt._scheduler.stop()
            except Exception as exc:
                logger.warning(f"TaskScheduler stop error for slug='{slug}': {exc}")

        # Cancel the background asyncio.Tasks
        for atask in _SCHEDULER_TASKS:
            if not atask.done():
                atask.cancel()
        if _SCHEDULER_TASKS:
            await asyncio.gather(*_SCHEDULER_TASKS, return_exceptions=True)
        _SCHEDULER_TASKS.clear()

        log_event(
            GAIAEvent.TURN_COMPLETE,
            message=f"TaskScheduler loops stopped ({len(_SCHEDULER_TASKS)} tasks cancelled).",
            gaian="scheduler",
        )

        _mother_thread.stop()
        log_event(
            GAIAEvent.TURN_COMPLETE,
            message="MotherThread stopped. GAIA rests.",
            gaian="mother_thread",
        )


def _boot_scheduler_for_existing_runtimes() -> None:
    """
    Launch run_forever() as a background asyncio.Task for every runtime
    that is already in the registry at startup time.
    """
    for slug, rt in _RUNTIME_REGISTRY.items():
        _boot_scheduler_for_runtime(slug, rt)


def _boot_scheduler_for_runtime(slug: str, rt) -> None:
    """
    Launch a single scheduler's run_forever() loop as a background task.
    Safe to call multiple times — checks _running_flag to avoid duplicates.
    """
    scheduler = rt._scheduler
    if scheduler._running_flag:
        return
    atask = asyncio.create_task(
        scheduler.run_forever(),
        name=f"scheduler:{slug}",
    )
    _SCHEDULER_TASKS.append(atask)
    logger.info(
        f"[Lifecycle] TaskScheduler loop started for gaian='{slug}' "
        f"(poll={scheduler._poll}s, max_concurrent={scheduler._max})"
    )

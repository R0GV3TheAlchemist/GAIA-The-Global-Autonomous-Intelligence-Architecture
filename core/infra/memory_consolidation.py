"""
core/infra/memory_consolidation.py

Memory tier promotion: SHORT_TERM → LONG_TERM.

Runs as a recurring scheduler task.  After each pass it re-submits
itself so the loop continues without external orchestration.

Promotion criteria:
  - MemoryTier.SHORT_TERM items
  - older than CONSOLIDATION_AGE_HOURS (default 1 h)
  - importance >= CONSOLIDATION_MIN_IMPORTANCE (default 0.5)
  - kind in CONSOLIDATION_KINDS (MESSAGE, REFLECTION, FACT)

The consolidation task is submitted once at session start by calling
schedule_consolidation(rt, user_id) from the chat router.
Subsequent passes self-reschedule via the on_success callback.

Canon: Doc 17 (Memory), Doc 21 (Sovereignty)
"""

from __future__ import annotations

import logging
import time
from typing import Any

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONSOLIDATION_AGE_HOURS     = 1.0         # promote items older than this
CONSOLIDATION_MIN_IMPORTANCE = 0.5        # minimum importance to promote
CONSOLIDATION_INTERVAL_S    = 3600.0      # re-run every hour
CONSOLIDATION_KINDS         = {"message", "reflection", "fact"}


# ---------------------------------------------------------------------------
# Consolidation coroutine
# ---------------------------------------------------------------------------

async def consolidate_memory(store: Any, user_id: str) -> dict:
    """
    Promote eligible SHORT_TERM memory items to LONG_TERM.

    Uses the MemoryStore's existing retrieve + update_tier interface.
    Falls back gracefully if the store doesn't support tier promotion
    (older schema versions).

    Returns a summary dict with keys: scanned, promoted, skipped, errors.
    """
    import asyncio

    summary = {"scanned": 0, "promoted": 0, "skipped": 0, "errors": 0}
    cutoff_ts = time.time() - (CONSOLIDATION_AGE_HOURS * 3600)

    # retrieve_sync is available on all MemoryStore versions
    try:
        candidates = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: store.retrieve_sync(
                query="",          # empty query returns by recency when supported
                user_id=user_id,
                top_k=200,
                tier="SHORT_TERM",  # filter by tier when supported
            ),
        )
    except TypeError:
        # Older MemoryStore doesn't accept tier kwarg — retrieve all and filter
        candidates = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: store.retrieve_sync(query="", user_id=user_id, top_k=200),
        )

    for item in candidates:
        summary["scanned"] += 1
        tier = getattr(item, "tier", None)
        # Only promote SHORT_TERM items
        if tier is not None and str(tier).upper() not in ("SHORT_TERM", "SHORT"):
            summary["skipped"] += 1
            continue

        kind = str(getattr(item, "kind", "")).lower()
        if kind not in CONSOLIDATION_KINDS:
            summary["skipped"] += 1
            continue

        importance = float(getattr(item, "importance", 0.0))
        if importance < CONSOLIDATION_MIN_IMPORTANCE:
            summary["skipped"] += 1
            continue

        created_ts = getattr(item, "created_at", None)
        if created_ts is not None:
            ts = created_ts.timestamp() if hasattr(created_ts, "timestamp") else float(created_ts)
            if ts > cutoff_ts:
                summary["skipped"] += 1
                continue

        # Attempt tier promotion
        try:
            if hasattr(store, "update_tier"):
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda i=item: store.update_tier(i.id, "LONG_TERM"),
                )
                summary["promoted"] += 1
                log.debug(
                    "[Consolidation] promoted item id=%s kind=%s importance=%.2f",
                    getattr(item, "id", "?"), kind, importance,
                )
            else:
                # MemoryStore lacks update_tier — log and skip gracefully
                log.debug(
                    "[Consolidation] MemoryStore has no update_tier — skipping promotion"
                )
                summary["skipped"] += 1
        except Exception as exc:
            log.warning("[Consolidation] promotion error for item=%s: %s", getattr(item, "id", "?"), exc)
            summary["errors"] += 1

    log.info(
        "[Consolidation] user=%s scanned=%d promoted=%d skipped=%d errors=%d",
        user_id, summary["scanned"], summary["promoted"], summary["skipped"], summary["errors"],
    )
    return summary


# ---------------------------------------------------------------------------
# Scheduler submission
# ---------------------------------------------------------------------------

# Track which (rt_id, user_id) pairs have already had a consolidation task
# submitted this process lifetime to avoid duplicate recurring chains.
_CONSOLIDATION_REGISTERED: set[tuple] = set()


def schedule_consolidation(rt: Any, user_id: str) -> bool:
    """
    Submit a self-rescheduling memory consolidation task to rt._scheduler.

    Safe to call on every turn — only submits once per (runtime, user_id)
    pair per process lifetime.  Returns True if a new task was submitted.
    """
    key = (id(rt), user_id)
    if key in _CONSOLIDATION_REGISTERED:
        return False

    _CONSOLIDATION_REGISTERED.add(key)
    _submit_consolidation_task(rt, user_id)
    log.info("[Consolidation] scheduled recurring consolidation for user=%s", user_id)
    return True


def _submit_consolidation_task(rt: Any, user_id: str) -> None:
    """Submit one consolidation task.  The on_success callback re-submits it."""
    from core.planner.scheduler import Task
    import asyncio

    store = rt._memory_store

    async def _run():
        # Wait the configured interval before doing any work so the first
        # pass doesn't fire immediately on startup when the queue is empty.
        await asyncio.sleep(CONSOLIDATION_INTERVAL_S)
        return await consolidate_memory(store, user_id)

    async def _on_success(result):
        # Re-submit immediately so the loop continues indefinitely.
        _submit_consolidation_task(rt, user_id)

    task = Task(
        name=f"memory:consolidation:{user_id}",
        coroutine=_run,
        priority=2,          # low priority — background work
        on_success=_on_success,
        ttl_seconds=None,    # never expire
        max_retries=2,
        backoff_sec=60.0,
        context={"user_id": user_id, "type": "memory_consolidation"},
    )
    rt._scheduler.submit(task)

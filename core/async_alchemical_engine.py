"""
core/async_alchemical_engine.py
================================
Async wrappers around AlchemicalPipeline for use in FastAPI / streaming
contexts where the synchronous pipeline would block the event loop.

All heavy work runs in a thread pool via asyncio.to_thread so the
FastAPI event loop stays free during batch mineral processing.

Public API
----------
    process_one_async(mineral_name, queue_index, verbose) -> dict
    process_batch_async(n, verbose)                       -> list[dict]
    process_all_async(verbose)                            -> None
    stream_batch_async(n, verbose)                        -> AsyncIterator[dict]

Canon Ref: C118, C47, C48
Related:   core/alchemical_pipeline.py
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator, Optional

from core.alchemical_pipeline import (
    AlchemyHalted,
    process_all,
    process_batch,
    process_one,
)

__all__ = [
    "process_one_async",
    "process_batch_async",
    "process_all_async",
    "stream_batch_async",
    "AlchemyHalted",
]


async def process_one_async(
    mineral_name: Optional[str] = None,
    queue_index: Optional[int] = None,
    verbose: bool = False,
) -> dict:
    """
    Async wrapper for process_one().

    Runs the synchronous alchemical pipeline in a thread pool so the
    FastAPI event loop is never blocked during mineral processing.

    Returns the updated queue entry dict, or {} if the queue is exhausted.
    """
    return await asyncio.to_thread(
        process_one,
        mineral_name,
        queue_index,
        verbose,
    )


async def process_batch_async(
    n: int = 10,
    verbose: bool = False,
) -> list[dict]:
    """
    Async wrapper for process_batch().

    Processes the next N unprocessed minerals without blocking the event
    loop. Returns a list of updated queue entry dicts.
    """
    return await asyncio.to_thread(process_batch, n, verbose)


async def process_all_async(verbose: bool = False) -> None:
    """
    Async wrapper for process_all().

    Runs the full Great Work (~6,000 minerals) in a thread pool.
    Intended for background task invocation — do not await in a
    request handler; use asyncio.create_task() instead:

        asyncio.create_task(process_all_async())
    """
    await asyncio.to_thread(process_all, verbose)


async def stream_batch_async(
    n: int = 10,
    verbose: bool = False,
) -> AsyncIterator[dict]:
    """
    Async generator that yields one processed mineral entry at a time.

    Useful for SSE (Server-Sent Events) endpoints that want to stream
    alchemical processing progress to the frontend in real time.

    Usage::

        async for entry in stream_batch_async(n=50):
            await sse_send(entry)
    """
    for _ in range(n):
        entry = await process_one_async(verbose=verbose)
        if not entry:
            return
        yield entry

"""
GAIA LLM Router — Offline-First AI Routing

Routing priority is controlled by GAIA_ROUTING_MODE env var:
  local-first  (default) — try Ollama, fall back to cloud
  cloud-first             — try cloud, fall back to Ollama
  local-only              — Ollama only; raise if unavailable
  cloud-only              — cloud only; never touch Ollama

Integrates with existing core/ollama_health.py and core/inference_router.py
so there is a single source of truth for provider config.

All public functions are async and return a LLMResult dataclass so callers
always know which provider answered and whether GAIA was offline.

Callers MUST consume stream() with `async for`, not `await` — it is an
async generator and awaiting it will raise TypeError at runtime.
"""

from __future__ import annotations

import os
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Optional

import httpx

log = logging.getLogger("gaia.llm_router")

# ── Routing mode ─────────────────────────────────────────────────────────────

class RoutingMode(str, Enum):
    LOCAL_FIRST  = "local-first"
    CLOUD_FIRST  = "cloud-first"
    LOCAL_ONLY   = "local-only"
    CLOUD_ONLY   = "cloud-only"


def _routing_mode() -> RoutingMode:
    raw = os.environ.get("GAIA_ROUTING_MODE", "local-first").strip().lower()
    try:
        return RoutingMode(raw)
    except ValueError:
        log.warning(f"[llm_router] Unknown GAIA_ROUTING_MODE '{raw}', defaulting to local-first")
        return RoutingMode.LOCAL_FIRST


# ── Provider config ───────────────────────────────────────────────────────────

OLLAMA_BASE    = os.environ.get("OLLAMA_BASE_URL",       "http://localhost:11434")
OLLAMA_MODEL   = os.environ.get("GAIA_MODEL",            "llama3")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT",    "60"))

OPENAI_MODEL   = os.environ.get("GAIA_OPENAI_MODEL",     "gpt-4o-mini")
ANTH_MODEL     = os.environ.get("GAIA_ANTHROPIC_MODEL",  "claude-3-haiku-20240307")

# FIX #4: cap completions so a runaway prompt can't drain API budget.
MAX_TOKENS = int(os.environ.get("GAIA_MAX_TOKENS", "2048"))


# ── Result type ───────────────────────────────────────────────────────────────

@dataclass
class LLMResult:
    text:        str
    provider:    str                    # "ollama" | "openai" | "anthropic"
    model:       str
    latency_ms:  int
    offline:     bool                   # True when served entirely locally
    metadata:    dict = field(default_factory=dict)


# ── Local provider (Ollama) ───────────────────────────────────────────────────

async def _call_ollama(
    prompt: str,
    system: Optional[str] = None,
    # FIX #2: removed dead `stream: bool` parameter — streaming is handled
    # exclusively by _stream_ollama(); this function always returns a full result.
) -> LLMResult:
    """
    Call local Ollama. Raises RuntimeError on any failure so the
    router can decide whether to fall back to cloud.
    """
    payload: dict = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    if system:
        payload["system"] = system

    t0 = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            r = await client.post(f"{OLLAMA_BASE}/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()
    except httpx.ConnectError as exc:
        raise RuntimeError(f"Ollama not reachable at {OLLAMA_BASE}") from exc
    except httpx.TimeoutException as exc:
        raise RuntimeError(f"Ollama timed out after {OLLAMA_TIMEOUT}s") from exc
    except Exception as exc:
        raise RuntimeError(f"Ollama error: {exc}") from exc

    text = data.get("response") or data.get("output") or ""
    if not text:
        raise RuntimeError("Ollama returned an empty response")

    latency = int((time.monotonic() - t0) * 1000)
    return LLMResult(
        text=text,
        provider="ollama",
        model=OLLAMA_MODEL,
        latency_ms=latency,
        offline=True,
        metadata={"eval_count": data.get("eval_count"), "done": data.get("done")},
    )


async def _stream_ollama(
    prompt: str,
    system: Optional[str] = None,
) -> AsyncIterator[str]:
    """Yield text tokens from Ollama streaming endpoint."""
    import json as _json

    payload: dict = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": True}
    if system:
        payload["system"] = system

    try:
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            async with client.stream("POST", f"{OLLAMA_BASE}/api/generate", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = _json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break
                    except _json.JSONDecodeError:
                        continue
    except httpx.ConnectError as exc:
        raise RuntimeError(f"Ollama not reachable: {exc}") from exc


# ── Cloud providers ───────────────────────────────────────────────────────────

async def _call_openai(
    prompt: str,
    system: Optional[str] = None,
) -> LLMResult:
    try:
        import openai as _openai
    except ImportError as exc:
        raise RuntimeError("openai package not installed") from exc

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    t0 = time.monotonic()
    client = _openai.AsyncOpenAI()
    # FIX #4: enforce token cap to prevent runaway API costs.
    resp = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
    )
    latency = int((time.monotonic() - t0) * 1000)

    return LLMResult(
        text=resp.choices[0].message.content or "",
        provider="openai",
        model=resp.model,
        latency_ms=latency,
        offline=False,
        metadata={"usage": resp.usage.model_dump() if resp.usage else {}},
    )


async def _call_anthropic(
    prompt: str,
    system: Optional[str] = None,
) -> LLMResult:
    try:
        import anthropic as _anthropic
    except ImportError as exc:
        raise RuntimeError("anthropic package not installed") from exc

    t0 = time.monotonic()
    client = _anthropic.AsyncAnthropic()

    # FIX #3: omit `system` key entirely when None — passing system="" sends a
    # blank system turn which some Anthropic model versions handle differently.
    create_kwargs: dict = dict(
        model=ANTH_MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    if system:
        create_kwargs["system"] = system

    resp = await client.messages.create(**create_kwargs)
    latency = int((time.monotonic() - t0) * 1000)

    text = resp.content[0].text if resp.content else ""
    return LLMResult(
        text=text,
        provider="anthropic",
        model=resp.model,
        latency_ms=latency,
        offline=False,
        metadata={"stop_reason": resp.stop_reason},
    )


async def _call_cloud(
    prompt: str,
    system: Optional[str] = None,
) -> LLMResult:
    """Try OpenAI first, then Anthropic. Raise if neither is configured."""
    errors: list[str] = []

    if os.environ.get("OPENAI_API_KEY"):
        try:
            return await _call_openai(prompt, system)
        except Exception as exc:
            errors.append(f"openai: {exc}")
            log.warning(f"[llm_router] OpenAI failed: {exc}")

    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return await _call_anthropic(prompt, system)
        except Exception as exc:
            errors.append(f"anthropic: {exc}")
            log.warning(f"[llm_router] Anthropic failed: {exc}")

    raise RuntimeError(
        "No cloud provider available. "
        + ("Errors: " + "; ".join(errors) if errors else "No API keys configured.")
    )


# ── Public interface ──────────────────────────────────────────────────────────

async def generate(
    prompt: str,
    system: Optional[str] = None,
) -> LLMResult:
    """
    Offline-first LLM call. Returns a LLMResult with full provenance.

    Routing logic:
      local-first  → Ollama → cloud
      cloud-first  → cloud  → Ollama
      local-only   → Ollama (error if unavailable)
      cloud-only   → cloud  (never tries Ollama)
    """
    mode = _routing_mode()

    if mode == RoutingMode.LOCAL_ONLY:
        result = await _call_ollama(prompt, system)
        log.info(f"[llm_router] local-only → {result.model} ({result.latency_ms}ms)")
        return result

    if mode == RoutingMode.CLOUD_ONLY:
        result = await _call_cloud(prompt, system)
        log.info(f"[llm_router] cloud-only → {result.provider}/{result.model} ({result.latency_ms}ms)")
        return result

    if mode == RoutingMode.LOCAL_FIRST:
        try:
            result = await _call_ollama(prompt, system)
            log.info(f"[llm_router] local-first → ollama/{result.model} ({result.latency_ms}ms) [offline]")
            return result
        except RuntimeError as local_err:
            log.info(f"[llm_router] local-first: local unavailable ({local_err}), falling back to cloud")
        result = await _call_cloud(prompt, system)
        log.info(f"[llm_router] local-first fallback → {result.provider}/{result.model} ({result.latency_ms}ms)")
        return result

    if mode == RoutingMode.CLOUD_FIRST:
        try:
            result = await _call_cloud(prompt, system)
            log.info(f"[llm_router] cloud-first → {result.provider}/{result.model} ({result.latency_ms}ms)")
            return result
        except RuntimeError as cloud_err:
            log.info(f"[llm_router] cloud-first: cloud unavailable ({cloud_err}), falling back to Ollama")
        result = await _call_ollama(prompt, system)
        log.info(f"[llm_router] cloud-first fallback → ollama/{result.model} ({result.latency_ms}ms) [offline]")
        return result

    raise RuntimeError(f"Unsupported routing mode: {mode}")


async def stream(
    prompt: str,
    system: Optional[str] = None,
) -> AsyncIterator[str]:
    """
    Streaming token generator.

    IMPORTANT: consume with `async for token in stream(...)` — NOT `await stream(...)`.
    Awaiting an async generator raises TypeError at runtime.

    Routing logic (FIX #1 — now fully mirrors generate()):
      cloud-only   → cloud non-streaming (word-chunked for UX smoothness)
      cloud-first  → cloud first, fall back to Ollama streaming
      local-only   → Ollama streaming; raise if unavailable
      local-first  → Ollama streaming; fall back to cloud non-streaming
    """
    mode = _routing_mode()

    # ── cloud-only: never touch Ollama ────────────────────────────────────────
    if mode == RoutingMode.CLOUD_ONLY:
        result = await _call_cloud(prompt, system)
        log.info(f"[llm_router] stream cloud-only → {result.provider}/{result.model}")
        for word in result.text.split(" "):
            yield word + " "
        return

    # ── cloud-first: try cloud, fall back to Ollama streaming ─────────────────
    if mode == RoutingMode.CLOUD_FIRST:
        try:
            result = await _call_cloud(prompt, system)
            log.info(f"[llm_router] stream cloud-first → {result.provider}/{result.model}")
            for word in result.text.split(" "):
                yield word + " "
            return
        except RuntimeError as cloud_err:
            log.info(f"[llm_router] stream cloud-first: cloud unavailable ({cloud_err}), falling back to Ollama")
        async for token in _stream_ollama(prompt, system):
            yield token
        return

    # ── local-only / local-first: try Ollama streaming first ─────────────────
    try:
        async for token in _stream_ollama(prompt, system):
            yield token
        return
    except RuntimeError as local_err:
        if mode == RoutingMode.LOCAL_ONLY:
            raise
        log.info(f"[llm_router] stream local-first: local unavailable ({local_err}), falling back to cloud")

    # local-first cloud fallback — word-chunked for UX smoothness
    result = await _call_cloud(prompt, system)
    log.info(f"[llm_router] stream local-first fallback → {result.provider}/{result.model}")
    for word in result.text.split(" "):
        yield word + " "


async def routing_status() -> dict:
    """
    Return the current routing configuration and live provider availability.
    Used by /api/llm/routing-status endpoint.
    """
    mode = _routing_mode()

    # Probe Ollama
    ollama_ok = False
    ollama_error: Optional[str] = None
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OLLAMA_BASE}/api/tags")
            r.raise_for_status()
            tags = r.json()
            models = [m["name"] for m in tags.get("models", [])]
            ollama_ok = any(m.startswith(OLLAMA_MODEL) for m in models)
            if not ollama_ok:
                ollama_error = f"Model '{OLLAMA_MODEL}' not found. Available: {models}"
    except Exception as exc:
        ollama_error = str(exc)

    return {
        "routing_mode":       mode.value,
        "ollama": {
            "base_url":   OLLAMA_BASE,
            "model":      OLLAMA_MODEL,
            "available":  ollama_ok,
            "error":      ollama_error,
        },
        "cloud": {
            "openai":          bool(os.environ.get("OPENAI_API_KEY")),
            "anthropic":       bool(os.environ.get("ANTHROPIC_API_KEY")),
            "openai_model":    OPENAI_MODEL,
            "anthropic_model": ANTH_MODEL,
            "max_tokens":      MAX_TOKENS,
        },
        "sovereign": ollama_ok and mode in {RoutingMode.LOCAL_FIRST, RoutingMode.LOCAL_ONLY},
    }

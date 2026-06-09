"""
core/registry/default_tools.py

Extended registry entries for GAIA's default tools.
Pairs each tool from default_policies with:
  - input/output schema
  - tags for discoverability
  - fallback behavior
  - health check functions (where applicable)

Canon ref: C01, C32 (Synergy Doctrine)
"""

from core.registry.capability_registry import (
    CapabilityRegistry,
    FallbackBehavior,
    RegistryEntry,
    ToolSchema,
)


def register_default_tools(registry: CapabilityRegistry) -> None:
    """Register all default GAIA tools with full schema and metadata."""

    entries = [
        # ---------------------------------------------------------------
        # Memory
        # ---------------------------------------------------------------
        RegistryEntry(
            name="read_memory",
            version="1.0.0",
            description="Read from GAIA sovereign or session memory.",
            permission_scope="read:memory",
            schema=ToolSchema(
                input_fields=["key", "namespace"],
                output_fields=["value", "found"],
                required_inputs=["key"],
                description="Retrieve a memory entry by key.",
            ),
            tags=["memory", "read", "core"],
            fallback_behavior=FallbackBehavior.SKIP,
        ),
        RegistryEntry(
            name="write_memory",
            version="1.0.0",
            description="Write or update an entry in sovereign memory.",
            permission_scope="write:memory",
            schema=ToolSchema(
                input_fields=["key", "value", "namespace", "ttl"],
                output_fields=["success"],
                required_inputs=["key", "value"],
                description="Store a memory entry with optional namespace and TTL.",
            ),
            tags=["memory", "write", "core"],
            fallback_behavior=FallbackBehavior.RAISE,
        ),
        # ---------------------------------------------------------------
        # Canon
        # ---------------------------------------------------------------
        RegistryEntry(
            name="read_canon",
            version="1.0.0",
            description="Retrieve Canon passages for RAG grounding.",
            permission_scope="read:canon",
            schema=ToolSchema(
                input_fields=["query", "top_k", "canon_ref"],
                output_fields=["passages", "references"],
                required_inputs=["query"],
                description="Semantic search over the GAIA Canon.",
            ),
            tags=["canon", "read", "rag", "core"],
            fallback_behavior=FallbackBehavior.SKIP,
        ),
        RegistryEntry(
            name="write_canon",
            version="1.0.0",
            description="Add or modify Canon entries. Requires Gaian approval.",
            permission_scope="write:canon",
            schema=ToolSchema(
                input_fields=["canon_ref", "content", "author", "amendment_reason"],
                output_fields=["canon_ref", "success"],
                required_inputs=["canon_ref", "content"],
                description="Write a new or amended Canon passage.",
            ),
            tags=["canon", "write", "governance"],
            fallback_behavior=FallbackBehavior.RAISE,
        ),
        # ---------------------------------------------------------------
        # File system
        # ---------------------------------------------------------------
        RegistryEntry(
            name="read_file",
            version="1.0.0",
            description="Read a local file.",
            permission_scope="read:system",
            schema=ToolSchema(
                input_fields=["path", "encoding"],
                output_fields=["content", "size_bytes"],
                required_inputs=["path"],
                description="Read a file from the local filesystem.",
            ),
            tags=["filesystem", "read"],
            fallback_behavior=FallbackBehavior.RAISE,
        ),
        RegistryEntry(
            name="write_file",
            version="1.0.0",
            description="Write or overwrite a local file.",
            permission_scope="write:file",
            schema=ToolSchema(
                input_fields=["path", "content", "encoding", "append"],
                output_fields=["success", "bytes_written"],
                required_inputs=["path", "content"],
                description="Write content to a local file.",
            ),
            tags=["filesystem", "write", "sensitive"],
            fallback_behavior=FallbackBehavior.RAISE,
        ),
        RegistryEntry(
            name="delete_file",
            version="1.0.0",
            description="Delete a local file. Always requires Gaian approval.",
            permission_scope="delete:file",
            schema=ToolSchema(
                input_fields=["path", "confirm"],
                output_fields=["success"],
                required_inputs=["path"],
                description="Permanently delete a file.",
            ),
            tags=["filesystem", "delete", "critical"],
            fallback_behavior=FallbackBehavior.RAISE,
        ),
        # ---------------------------------------------------------------
        # LLM
        # ---------------------------------------------------------------
        RegistryEntry(
            name="call_llm",
            version="1.0.0",
            description="Route a prompt to the configured LLM backend.",
            permission_scope="call:llm",
            schema=ToolSchema(
                input_fields=["prompt", "model", "max_tokens", "temperature", "system"],
                output_fields=["response", "model_used", "tokens_used"],
                required_inputs=["prompt"],
                description="Send a prompt to the active LLM and return the response.",
            ),
            tags=["llm", "inference", "core"],
            fallback_behavior=FallbackBehavior.RAISE,
        ),
        # ---------------------------------------------------------------
        # External services
        # ---------------------------------------------------------------
        RegistryEntry(
            name="call_github",
            version="1.0.0",
            description="Call the GitHub API via MCP.",
            permission_scope="call:github",
            schema=ToolSchema(
                input_fields=["method", "endpoint", "params", "body"],
                output_fields=["response", "status_code"],
                required_inputs=["method", "endpoint"],
                description="GitHub API call routed through the MCP integration layer.",
            ),
            tags=["external", "github", "mcp"],
            fallback_behavior=FallbackBehavior.RAISE,
        ),
        RegistryEntry(
            name="web_search",
            version="1.0.0",
            description="Perform a web search.",
            permission_scope="call:web_search",
            schema=ToolSchema(
                input_fields=["query", "num_results", "safe_search"],
                output_fields=["results", "total_found"],
                required_inputs=["query"],
                description="Search the web and return ranked results.",
            ),
            tags=["external", "search"],
            fallback_behavior=FallbackBehavior.SKIP,
        ),
        # ---------------------------------------------------------------
        # Sensitive / biometric
        # ---------------------------------------------------------------
        RegistryEntry(
            name="read_biometrics",
            version="1.0.0",
            description="Access Gaian biometric data (HRV, heart rate, etc.).",
            permission_scope="access:biometrics",
            schema=ToolSchema(
                input_fields=["metric", "time_range", "source"],
                output_fields=["readings", "unit", "source"],
                required_inputs=["metric"],
                description="Read biometric signals from connected wearable or health API.",
            ),
            tags=["biometrics", "sensitive", "critical", "privacy"],
            fallback_behavior=FallbackBehavior.SKIP,
        ),
        # ---------------------------------------------------------------
        # Code execution
        # ---------------------------------------------------------------
        RegistryEntry(
            name="execute_code",
            version="1.0.0",
            description="Execute arbitrary code in the GAIA runtime.",
            permission_scope="execute:code",
            schema=ToolSchema(
                input_fields=["code", "language", "timeout", "sandbox"],
                output_fields=["stdout", "stderr", "exit_code"],
                required_inputs=["code"],
                description="Run a code snippet in a sandboxed environment.",
            ),
            tags=["execution", "critical", "sandbox"],
            fallback_behavior=FallbackBehavior.RAISE,
        ),
        # ---------------------------------------------------------------
        # Governance
        # ---------------------------------------------------------------
        RegistryEntry(
            name="halt_system",
            version="1.0.0",
            description="Halt all GAIA sessions. Requires Gaian approval.",
            permission_scope="halt:system",
            schema=ToolSchema(
                input_fields=["reason", "mode", "confirm"],
                output_fields=["halted_sessions", "success"],
                required_inputs=["reason"],
                description="Initiate a system halt. Modes: pause, soft_stop, hard_stop.",
            ),
            tags=["governance", "safety", "critical"],
            fallback_behavior=FallbackBehavior.RAISE,
        ),
    ]

    for entry in entries:
        registry.register(entry)

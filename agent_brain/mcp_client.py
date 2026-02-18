"""
MCP client for agent_brain: connects to tools_server via stdio and calls tools.
Modular so Phase 2 can add reservation/booking tools without changing this interface.
"""
import os
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _default_server_params() -> StdioServerParameters:
    """Build stdio params to run tools_server as a subprocess. Passes env for API keys."""
    return StdioServerParameters(
        command=os.environ.get("PYTHON", "python"),
        args=["-m", "tools_server.server"],
        env=os.environ.copy(),
    )


@asynccontextmanager
async def tools_server_session(server_params: StdioServerParameters | None = None):
    """
    Async context manager: spawns the MCP tools server and yields a ClientSession.
    Use this in graph nodes to call search_restaurants (and Phase 2 booking tools).
    """
    params = server_params or _default_server_params()
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def call_tool(
    session: ClientSession,
    name: str,
    arguments: dict[str, Any] | None = None,
) -> Any:
    """
    Call an MCP tool and return parsed result content.
    For search_restaurants, returns the list of restaurant dicts.
    """
    result = await session.call_tool(name, arguments or {})
    if result.isError:
        raise RuntimeError(
            getattr(result, "content", None) or f"MCP tool {name} failed"
        )
    # Result has .content (list of content items). For our tools we return text/structured.
    content = getattr(result, "content", []) or []
    if not content:
        return None
    # Prefer structured content if present (e.g. from FastMCP json_response).
    if getattr(result, "structuredContent", None) is not None:
        return result.structuredContent
    # Otherwise concatenate text parts.
    texts = []
    for part in content:
        if hasattr(part, "text"):
            texts.append(part.text)
    return "\n".join(texts) if texts else None

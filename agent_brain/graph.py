"""
LangGraph state machine for Book-It-Bunny.
Researcher node calls the MCP tools server (search_restaurants). Modular for Phase 2 (booking node).
"""
from typing import Any

from langgraph.graph import END, START, StateGraph

from agent_brain.mcp_client import call_tool, tools_server_session
from agent_brain.state import AgentState, SearchParams


async def researcher_node(state: AgentState) -> dict[str, Any]:
    """
    Connects to the MCP tools server via stdio and calls search_restaurants.
    Uses search_params from state (location, cuisine, party_size); if missing, uses defaults.
    Updates state with search_results.
    """
    params: SearchParams = state.get("search_params") or {}
    location = params.get("location") or "San Francisco, CA"
    cuisine = params.get("cuisine") or ""
    party_size = int(params.get("party_size") or 2)

    async with tools_server_session() as session:
        raw = await call_tool(
            session,
            "search_restaurants",
            {"location": location, "cuisine": cuisine, "party_size": party_size},
        )
    # MCP may return structured list or wrapped; normalize to list of dicts.
    if isinstance(raw, list):
        results = raw
    elif isinstance(raw, dict) and "result" in raw:
        results = raw["result"] if isinstance(raw["result"], list) else [raw["result"]]
    else:
        results = [{"raw": str(raw)}]

    return {"search_results": results}


def build_graph() -> StateGraph:
    """
    Build the Book-It-Bunny graph.
    Phase 1: START -> researcher -> END.
    Phase 2: add booking node and conditional edges (e.g. after user_selection).
    """
    graph = StateGraph(AgentState)
    graph.add_node("researcher", researcher_node)
    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", END)
    return graph


def get_compiled_graph():
    """Compiled graph entrypoint for invocation."""
    return build_graph().compile()

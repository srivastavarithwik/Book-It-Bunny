"""
LangGraph state for Book-It-Bunny.
Tracks conversation, search results, and user selection for a modular flow.
"""
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class SearchParams(TypedDict, total=False):
    """Parameters for restaurant search (from user or previous node)."""
    location: str
    cuisine: str
    party_size: int


class RestaurantResult(TypedDict, total=False):
    """Single restaurant from search (matches tools_server search shape)."""
    name: str
    address: str
    cuisine: str
    rating: float
    price: str
    party_size_ok: bool
    phone: str


class AgentState(TypedDict, total=False):
    """
    State for the Book-It-Bunny graph.
    - messages: conversation history (supports add_messages reducer for append).
    - search_results: list of restaurants from the last search (Researcher node).
    - user_selection: which restaurant/time the user chose (for Phase 2 booking).
    - search_params: extracted location/cuisine/party_size for the Researcher node.
    """
    messages: Annotated[list, add_messages]
    search_results: list[RestaurantResult]
    user_selection: dict
    search_params: SearchParams

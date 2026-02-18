"""
MCP server for Book-It-Bunny tools.
Phase 1: search_restaurants. Phase 2: reservation/booking tools (browser-use).
"""
from mcp.server.fastmcp import FastMCP

from tools_server.tools.search import search_restaurants as _search_restaurants
from tools_server.tools.booking import book_table as _book_table

mcp = FastMCP(
    "Book-It-Bunny Tools",
    json_response=True,
)


@mcp.tool()
def search_restaurants(
    location: str,
    cuisine: str = "",
    party_size: int = 2,
) -> list[dict]:
    """
    Search for restaurants by location, cuisine, and party size.
    Use this when the user wants to find places to eat.
    """
    return _search_restaurants(location=location, cuisine=cuisine, party_size=party_size)


@mcp.tool()
def book_table(
    restaurant_name: str,
    time: str,
    party_size: int,
    location: str = "",
) -> dict:
    """
    Book a table at a selected restaurant (mock implementation).
    Use this after the user has picked a restaurant and time.
    """
    return _book_table(
        restaurant_name=restaurant_name,
        time=time,
        party_size=party_size,
        location=location,
    )


if __name__ == "__main__":
    # Stdio transport so agent_brain can spawn this process and call tools.
    mcp.run(transport="stdio")

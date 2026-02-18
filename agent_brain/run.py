"""
Run the Book-It-Bunny graph (Researcher node -> MCP search_restaurants).
Usage:
  python -m agent_brain.run
  python -m agent_brain.run --location "New York, NY" --cuisine Italian --party-size 4
"""
import asyncio
import os
import sys
from pathlib import Path

# Load .env from project root when running as module
_root = Path(__file__).resolve().parent.parent
_env = _root / ".env"
if _env.exists():
    from dotenv import load_dotenv
    load_dotenv(_env)

from agent_brain import get_compiled_graph


def _parse_args() -> dict:
    args = {}
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--location" and i + 1 < len(argv):
            args["location"] = argv[i + 1]
            i += 2
        elif arg == "--cuisine" and i + 1 < len(argv):
            args["cuisine"] = argv[i + 1]
            i += 2
        elif arg in ("--party-size", "--party_size") and i + 1 < len(argv):
            args["party_size"] = int(argv[i + 1])
            i += 2
        else:
            i += 1
    return args


async def main() -> None:
    search_params = _parse_args() or {
        "location": "San Francisco, CA",
        "cuisine": "",
        "party_size": 2,
    }
    graph = get_compiled_graph()
    initial: dict = {
        "messages": [],
        "search_params": search_params,
    }
    result = await graph.ainvoke(initial)
    print("Search results:", result.get("search_results"))


if __name__ == "__main__":
    asyncio.run(main())

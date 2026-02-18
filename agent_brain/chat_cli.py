"""
Terminal chat/wizard for Book-It-Bunny.

Flow:
- Ask what cuisine you want.
- Ask where you want to eat (location).
- Search restaurants via MCP (Yelp).
- Show a numbered list of restaurant names.
- Ask which one you want.
- Ask for time and party size.
- Call MCP booking tool (mock) and print confirmation.

Run from project root:
  python -m agent_brain.chat_cli
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from agent_brain.mcp_client import call_tool, tools_server_session


def _load_env() -> None:
    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_path)
        except Exception:
            # Non-fatal: CLI can still run with mock search if keys are missing.
            pass


async def _run_once() -> None:
    print("🐰 Book-It-Bunny (terminal chat)")
    print("I'll help you find a place and (mock) book a table.\n")

    cuisine = input("What are you in the mood for (cuisine)? ").strip() or ""
    location = input("Where are you looking to eat (city / area)? ").strip() or "Boston, MA"

    print("\nSearching for restaurants...")
    async with tools_server_session() as session:
        raw_results = await call_tool(
            session,
            "search_restaurants",
            {"location": location, "cuisine": cuisine, "party_size": 2},
        )

        # Normalise tool output (can be list, dict with \"result\", or JSON string).
        import json  # local import to avoid top-level dependency if unused

        search_results = raw_results
        if isinstance(search_results, str):
            try:
                search_results = json.loads(search_results)
            except Exception:
                search_results = []

        if isinstance(search_results, dict) and "result" in search_results:
            value = search_results["result"]
            search_results = value if isinstance(value, list) else [value]

        if not isinstance(search_results, list):
            search_results = []

        if not search_results:
            print("No restaurants found. Try a different location or cuisine.")
            return

        print("\nHere are some options:")
        for idx, r in enumerate(search_results, start=1):
            # Each item is expected to be a dict from the search tool.
            if not isinstance(r, dict):
                continue
            name = r.get("name", "Unnamed")
            cuisine_text = r.get("cuisine") or cuisine or "Restaurant"
            rating = r.get("rating")
            price = r.get("price") or ""
            meta_bits = []
            if cuisine_text:
                meta_bits.append(cuisine_text)
            if rating:
                meta_bits.append(f"★ {rating}")
            if price:
                meta_bits.append(price)
            meta = " · ".join(meta_bits)
            print(f"{idx}. {name} ({meta})")

        while True:
            sel_raw = input("\nWhich one would you like to book? (enter number) ").strip()
            try:
                sel = int(sel_raw)
                if 1 <= sel <= len(search_results):
                    break
            except ValueError:
                pass
            print(f"Please enter a number between 1 and {len(search_results)}.")

        chosen = search_results[sel - 1]
        restaurant_name = chosen.get("name", "Unnamed")

        time = input(f"When would you like to go to {restaurant_name}? (e.g. 7:30pm) ").strip()
        party_raw = input("How many people? ").strip()
        try:
            party_size = int(party_raw)
        except ValueError:
            party_size = 2

        print("\nBooking your table (mock)...")
        raw_booking = await call_tool(
            session,
            "book_table",
            {
                "restaurant_name": restaurant_name,
                "time": time or "7:30pm",
                "party_size": party_size,
                "location": location,
            },
        )

    # Normalise tool output (can be dict, JSON string, or dict with "result").
    booking = raw_booking
    if isinstance(booking, str):
        try:
            booking = json.loads(booking)
        except Exception:
            booking = {}
    if isinstance(booking, dict) and "result" in booking:
        booking = booking["result"] if isinstance(booking["result"], dict) else {}
    if not isinstance(booking, dict):
        booking = {}
    message = booking.get("message") or "Booking complete."
    print("\n" + message)


def main() -> None:
    _load_env()
    asyncio.run(_run_once())


if __name__ == "__main__":
    main()


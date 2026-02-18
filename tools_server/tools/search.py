"""
Restaurant search tool: mock response or Yelp Fusion API.
"""
import os
from typing import Any

# Set to "1" or "true" to force mock and skip Yelp (e.g. when no API key).
USE_MOCK = os.environ.get("BOOKITBUNNY_USE_MOCK_SEARCH", "").lower() in ("1", "true", "yes")


def _mock_search(location: str, cuisine: str, party_size: int) -> list[dict[str, Any]]:
    """Hardcoded mock results for development and testing."""
    return [
        {
            "name": "The Golden Fork",
            "address": "123 Main St, " + location,
            "cuisine": cuisine or "American",
            "rating": 4.5,
            "price": "$$",
            "party_size_ok": party_size <= 6,
            "phone": "+1 (555) 123-4567",
        },
        {
            "name": "Bistro Luna",
            "address": "456 Oak Ave, " + location,
            "cuisine": cuisine or "French",
            "rating": 4.8,
            "price": "$$$",
            "party_size_ok": party_size <= 4,
            "phone": "+1 (555) 987-6543",
        },
    ]


def _yelp_search(location: str, cuisine: str, party_size: int) -> list[dict[str, Any]]:
    """Call Yelp Fusion API. Requires YELP_API_KEY in env."""
    import httpx

    api_key = os.environ.get("YELP_API_KEY")
    if not api_key:
        return _mock_search(location, cuisine, party_size)

    base = os.environ.get("YELP_API_URL", "https://api.yelp.com").rstrip("/")
    url = f"{base}/v3/businesses/search"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "location": location,
        "term": cuisine or "restaurants",
        "limit": 10,
    }

    with httpx.Client(timeout=15.0) as client:
        resp = client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

    out = []
    for b in data.get("businesses", []):
        out.append({
            "name": b.get("name", ""),
            "address": ", ".join(b.get("location", {}).get("display_address", [])),
            "cuisine": ", ".join((c.get("title", "") for c in b.get("categories", []))),
            "rating": float(b.get("rating", 0)),
            "price": b.get("price", "?"),
            "party_size_ok": True,  # Yelp doesn't provide this; assume ok
            "phone": b.get("display_phone", ""),
        })
    return out


def search_restaurants(
    location: str,
    cuisine: str = "",
    party_size: int = 2,
) -> list[dict[str, Any]]:
    """
    Search for restaurants by location, cuisine, and party size.

    Args:
        location: City/address or area (e.g. "San Francisco, CA").
        cuisine: Cuisine type (e.g. "Italian", "Japanese"). Optional.
        party_size: Number of guests. Optional; default 2.

    Returns:
        List of restaurant dicts with name, address, cuisine, rating, price, party_size_ok, phone.
    """
    if USE_MOCK or not os.environ.get("YELP_API_KEY"):
        return _mock_search(location, cuisine or "restaurants", party_size)
    return _yelp_search(location, cuisine, party_size)

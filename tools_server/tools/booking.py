"""
Booking tool: mock reservation flow for Phase 2.
Later, this can be replaced with a browser-use / Playwright implementation.
"""
from __future__ import annotations

import random
import string
from typing import Any, TypedDict


class BookingResult(TypedDict, total=False):
    restaurant_name: str
    location: str
    time: str
    party_size: int
    status: str
    confirmation_code: str
    message: str


def _generate_confirmation_code() -> str:
    prefix = "BK-"
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return prefix + suffix


def book_table(
    restaurant_name: str,
    time: str,
    party_size: int,
    location: str = "",
) -> BookingResult:
    """
    Mock booking implementation.

    Args:
        restaurant_name: Name of the restaurant the user selected.
        time: Desired reservation time (free-form string).
        party_size: Number of guests.
        location: Optional city/area (for display only).

    Returns:
        BookingResult with status and confirmation_code.
    """
    code = _generate_confirmation_code()
    return BookingResult(
        restaurant_name=restaurant_name,
        location=location,
        time=time,
        party_size=party_size,
        status="confirmed",
        confirmation_code=code,
        message=f"Table booked at {restaurant_name} for {party_size} at {time}. Confirmation: {code}",
    )


"""Protocol interfaces for environmental data providers (weather, places, events).

Decouples external data acquisition from the recommendation and ranking engine.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.models import Place, Weather


@runtime_checkable
class WeatherProvider(Protocol):
    """Protocol for fetching current weather metrics and precipitation forecasts."""

    async def get_weather(self, lat: float, lon: float, decimals: int = 3) -> Weather:
        ...


@runtime_checkable
class PlacesProvider(Protocol):
    """Protocol for retrieving candidate physical outdoor venues."""

    async def get_places(
        self, lat: float, lon: float, radius_m: int = 3000, decimals: int = 3
    ) -> list[Place]:
        ...

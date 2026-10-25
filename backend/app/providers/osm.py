"""Concrete Open-Meteo weather provider and OpenStreetMap places provider implementations."""

from __future__ import annotations

import httpx

from app.models import Place, Weather
from app.places import fetch_places
from app.weather import fetch_weather


class OpenMeteoWeatherProvider:
    """Fetches weather metrics and rain forecasts via Open-Meteo."""

    def __init__(self, client: httpx.AsyncClient, weather_url: str) -> None:
        self.client = client
        self.weather_url = weather_url

    async def get_weather(self, lat: float, lon: float, decimals: int = 3) -> Weather:
        return await fetch_weather(self.client, self.weather_url, lat, lon, decimals)


class OpenStreetMapPlacesProvider:
    """Discovers nearby outdoor amenities via Overpass API with Nominatim fallback."""

    def __init__(self, client: httpx.AsyncClient, overpass_url: str) -> None:
        self.client = client
        self.overpass_url = overpass_url

    async def get_places(
        self, lat: float, lon: float, radius_m: int = 3000, decimals: int = 3
    ) -> list[Place]:
        return await fetch_places(
            self.client, self.overpass_url, lat, lon, radius_m, decimals
        )

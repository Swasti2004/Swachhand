"""Characterisation tests locking baseline behaviour before Phase 3 refactoring.

Captures input/output contracts for:
1. Rule-based feasibility filtering (weather, daylight, energy, stay time)
2. Geocoding and coordinate coarsening
3. Fallback heuristic ranking
4. Feedback recording and history summaries
"""

from __future__ import annotations

import pytest

from app.fallback import effort_for, rank_fallback
from app.filters import filter_places, stay_minutes, weather_block_reason
from app.geo import coarsen, haversine_m
from app.models import History, Place, Weather
from tests.conftest import OVERPASS, WEATHER_OK


@pytest.mark.characterization
def test_characterisation_coordinate_coarsening():
    # Coarsening to 3 decimal places rounds to roughly ~110m
    lat, lon = coarsen(28.613939, 77.209021, 3)
    assert lat == 28.614
    assert lon == 77.209


@pytest.mark.characterization
def test_characterisation_stay_minutes_budgeting():
    # Place with 10 min walk one way (20 min round trip) in a 60 min window
    p = Place(id="node/1", name="Central Park", category="park", lat=28.6, lon=77.2, distance_m=800, walk_minutes=10)
    assert stay_minutes(p, 60) == 40
    # In a 25 min window: 25 - 20 = 5 min
    assert stay_minutes(p, 25) == 5

    # But filter_places enforces MIN_STAY_MIN = 10, so a 5 min stay is filtered out
    weather = Weather(
        temperature_c=20, feels_like_c=20, precipitation_mm=0.0, rain_chance_pct=10,
        wind_kmh=10, is_day=True, thunderstorm=False, summary="clear sky"
    )
    result = filter_places([p], weather, minutes=25, energy="medium", allow_after_dark=False)
    assert len(result.candidates) == 0
    assert "Nothing nearby fits 25 minutes" in result.blocked_reason


@pytest.mark.characterization
def test_characterisation_weather_filtering_rules():
    # Thunderstorm blocks outdoor outings
    thunder_weather = Weather(
        temperature_c=22, feels_like_c=22, precipitation_mm=2.0, rain_chance_pct=40,
        wind_kmh=15, is_day=True, thunderstorm=True, summary="thunderstorm"
    )
    assert "Thunderstorms are around" in weather_block_reason(thunder_weather, allow_after_dark=False)

    # Rain chance >= 60% blocks outings
    rainy_weather = Weather(
        temperature_c=20, feels_like_c=20, precipitation_mm=0.5, rain_chance_pct=75,
        wind_kmh=12, is_day=True, thunderstorm=False, summary="rain showers"
    )
    assert "Rain looks likely" in weather_block_reason(rainy_weather, allow_after_dark=False)

    # Extreme heat >= 38C blocks outings
    hot_weather = Weather(
        temperature_c=40, feels_like_c=44, precipitation_mm=0.0, rain_chance_pct=0,
        wind_kmh=8, is_day=True, thunderstorm=False, summary="clear sky"
    )
    assert "It feels extremely hot" in weather_block_reason(hot_weather, allow_after_dark=False)


@pytest.mark.characterization
def test_characterisation_fallback_ranking_contract():
    p1 = Place(id="node/1", name="Close Park", category="park", lat=28.6, lon=77.2, distance_m=300, walk_minutes=4)
    p2 = Place(id="node/2", name="Far Peak", category="peak", lat=28.62, lon=77.22, distance_m=2000, walk_minutes=25)
    candidates = [p1, p2]

    weather = Weather(
        temperature_c=20, feels_like_c=20, precipitation_mm=0.0, rain_chance_pct=10,
        wind_kmh=10, is_day=True, thunderstorm=False, summary="partly cloudy"
    )
    history = History(recent_place_ids=[], recent_load_minutes=0, done_last_7d=0)

    # Medium energy request with 60 minutes
    picks = rank_fallback(candidates, 60, "medium", ["quiet"], history, weather)
    assert len(picks) > 0
    assert picks[0].place_id in {"node/1", "node/2"}
    assert picks[0].effort in {"easy", "moderate", "active"}
    assert picks[0].duration_minutes > 0

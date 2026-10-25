"""Tests for Phase 3 components: Provider interfaces, Fatigue State modeling, and Ranker implementations."""

from __future__ import annotations

import pytest

from app.fatigue import FatigueState, adjust_effort_for_fatigue
from app.models import History, Place, Weather
from app.ranking import HeuristicRanker, LinUCBRanker, RandomRanker


@pytest.fixture
def sample_places():
    return [
        Place(id="node/1", name="Quiet Garden", category="garden", lat=28.6, lon=77.2, distance_m=500, walk_minutes=6),
        Place(id="node/2", name="Sunny Park", category="park", lat=28.61, lon=77.21, distance_m=1000, walk_minutes=12),
        Place(id="node/3", name="High Peak", category="peak", lat=28.62, lon=77.22, distance_m=1800, walk_minutes=22),
    ]


@pytest.fixture
def sample_weather():
    return Weather(
        temperature_c=22, feels_like_c=22, precipitation_mm=0.0, rain_chance_pct=10,
        wind_kmh=10, is_day=True, thunderstorm=False, summary="partly cloudy"
    )


def test_fatigue_state_thresholds():
    rested = FatigueState.from_history(recent_load_minutes=30)
    assert rested.fatigue_level == "rested"
    assert rested.effort_penalty_active == 0.0

    moderate = FatigueState.from_history(recent_load_minutes=120)
    assert moderate.fatigue_level == "moderate"
    assert moderate.effort_penalty_active > 0.0

    exhausted = FatigueState.from_history(recent_load_minutes=200)
    assert exhausted.fatigue_level == "exhausted"
    assert exhausted.effort_penalty_active >= 0.8
    assert adjust_effort_for_fatigue("active", exhausted) == "easy"


def test_random_ranker_produces_valid_picks(sample_places, sample_weather):
    ranker = RandomRanker(seed=42)
    history = History(recent_place_ids=[], recent_load_minutes=0, done_last_7d=0)
    fatigue = FatigueState.from_history(0)

    picks = ranker.rank(sample_places, 60, "medium", ["quiet"], history, sample_weather, fatigue)
    assert len(picks) == 3
    for pick in picks:
        assert pick.place_id in {p.id for p in sample_places}
        assert pick.duration_minutes > 0


def test_heuristic_ranker_penalizes_peaks_when_fatigued(sample_places, sample_weather):
    ranker = HeuristicRanker()
    history = History(recent_place_ids=[], recent_load_minutes=0, done_last_7d=0)
    exhausted = FatigueState.from_history(200)

    picks = ranker.rank(sample_places, 60, "high", ["views"], history, sample_weather, exhausted)
    # The peak should not be top ranked when exhausted
    assert picks[0].place_id != "node/3"


def test_linucb_ranker_learns_from_reward_update(sample_places, sample_weather):
    bandit = LinUCBRanker(alpha=0.2)
    history = History(recent_place_ids=[], recent_load_minutes=0, done_last_7d=0)
    fatigue = FatigueState.from_history(0)

    # Initial rank
    picks_initial = bandit.rank(sample_places, 60, "medium", ["greenery"], history, sample_weather, fatigue)
    assert len(picks_initial) == 3

    # Reward park heavily
    park = sample_places[1]
    for _ in range(5):
        bandit.update(park, 60, "medium", ["greenery"], fatigue, reward=1.0)

    # After rewards, park should be prioritized
    picks_after = bandit.rank(sample_places, 60, "medium", ["greenery"], history, sample_weather, fatigue)
    assert picks_after[0].place_id == park.id

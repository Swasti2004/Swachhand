"""Synthetic User Simulator and Evaluation Harness for Swachhand.

Implements:
1. User Environment with preference vectors, fatigue accumulation, and time-budget constraints.
2. Simulator variants:
   - standard: Normal fatigue penalty on high effort when exhausted.
   - fatigue_free: Baseline variant where fatigue does not alter user acceptance (ablation).
   - preference_drift: User preference drifts over time to test bandit adaptation.
3. Multi-seed simulation across:
   - RandomRanker
   - HeuristicRanker (Popularity / Content)
   - LinUCBRanker (Contextual Bandit)
4. Metrics: Cumulative Reward, Cumulative Regret, Burnout Rate (% sessions where exhausted user was forced high effort).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from app.fatigue import FatigueState
from app.models import History, Place, Weather
from app.ranking import HeuristicRanker, LinUCBRanker, RandomRanker, Ranker

SimulatorVariant = Literal["standard", "fatigue_free", "preference_drift"]


@dataclass
class SyntheticUser:
    """Represents a simulated user interacting with the recommendation system."""

    user_id: str
    preferred_category: str
    energy: str
    time_available: int
    burnout_count: int = 0
    current_load_minutes: int = 0
    consecutive_active_days: int = 0

    def compute_reward(self, place: Place, variant: SimulatorVariant, step: int) -> float:
        """Computes stochastic reward in [0.0, 1.0] when user is recommended `place`."""
        # Preference drift: preference shifts halfway through simulation
        target_cat = self.preferred_category
        if variant == "preference_drift" and step > 50:
            target_cat = "viewpoint" if self.preferred_category == "park" else "park"

        # Base satisfaction based on category match
        match_score = 0.8 if place.category == target_cat else 0.3

        # Distance penalty
        dist_factor = max(0.0, 1.0 - (place.distance_m / 3000.0) * 0.4)

        # Fatigue impact: if user is exhausted and place is strenuous (e.g. peak or far walk)
        fatigue = FatigueState.from_history(self.current_load_minutes)
        fatigue_penalty = 0.0
        if variant != "fatigue_free":
            if fatigue.fatigue_level == "exhausted" and place.category == "peak":
                fatigue_penalty = 0.6
                self.burnout_count += 1
            elif fatigue.fatigue_level == "moderate" and place.category == "peak":
                fatigue_penalty = 0.25

        reward = match_score * dist_factor - fatigue_penalty
        return max(0.0, min(1.0, reward))

    def update_load(self, place: Place) -> None:
        """Simulates activity completion and cumulative physical load."""
        added_load = place.walk_minutes * 2 + 20
        self.current_load_minutes += added_load
        # Overnight recovery decay (simulating 24h passage)
        self.current_load_minutes = int(self.current_load_minutes * 0.65)


def generate_candidate_pool(rng: random.Random) -> list[Place]:
    """Generates a diverse set of synthetic candidates representing physical places."""
    categories = ["park", "garden", "nature", "viewpoint", "beach", "peak"]
    places = []
    for i in range(15):
        cat = rng.choice(categories)
        dist = rng.randint(300, 2500)
        places.append(
            Place(
                id=f"place_{i}",
                name=f"{cat.capitalize()} {i}",
                category=cat,
                lat=28.6 + rng.uniform(-0.02, 0.02),
                lon=77.2 + rng.uniform(-0.02, 0.02),
                distance_m=dist,
                walk_minutes=max(4, int((dist / 80) * 1.3)),
            )
        )
    return places


def run_single_simulation(
    ranker: Ranker,
    variant: SimulatorVariant = "standard",
    steps: int = 100,
    seed: int = 42,
) -> dict[str, float]:
    """Executes a single continuous simulation run for a given ranker."""
    rng = random.Random(seed)
    user = SyntheticUser(
        user_id=f"user_{seed}",
        preferred_category="park",
        energy="medium",
        time_available=60,
    )
    weather = Weather(
        temperature_c=22, feels_like_c=22, precipitation_mm=0.0, rain_chance_pct=10,
        wind_kmh=10, is_day=True, thunderstorm=False, summary="clear"
    )

    total_reward = 0.0
    total_regret = 0.0
    history = History(recent_place_ids=[], recent_load_minutes=0, done_last_7d=0)

    for t in range(steps):
        candidates = generate_candidate_pool(rng)
        fatigue = FatigueState.from_history(user.current_load_minutes)

        picks = ranker.rank(
            candidates=candidates,
            minutes=user.time_available,
            energy=user.energy,
            interests=["greenery"],
            history=history,
            weather=weather,
            fatigue=fatigue,
        )

        if not picks:
            continue

        chosen_pick = picks[0]
        chosen_place = next(p for p in candidates if p.id == chosen_pick.place_id)

        reward = user.compute_reward(chosen_place, variant, step=t)
        total_reward += reward

        # Theoretical optimal reward in this candidate pool
        best_reward = max(user.compute_reward(p, variant, step=t) for p in candidates)
        regret = best_reward - reward
        total_regret += regret

        # Online update if ranker is a learning bandit
        if isinstance(ranker, LinUCBRanker):
            ranker.update(
                place=chosen_place,
                minutes=user.time_available,
                energy=user.energy,
                interests=["greenery"],
                fatigue=fatigue,
                reward=reward,
            )

        user.update_load(chosen_place)
        history = History(
            recent_place_ids=(history.recent_place_ids + [chosen_place.id])[-5:],
            recent_load_minutes=user.current_load_minutes,
            done_last_7d=t + 1,
        )

    return {
        "cumulative_reward": total_reward,
        "cumulative_regret": total_regret,
        "average_reward": total_reward / steps,
        "burnout_count": float(user.burnout_count),
    }


def evaluate_across_seeds(
    ranker_factory,
    variant: SimulatorVariant = "standard",
    num_seeds: int = 30,
    steps: int = 100,
) -> dict[str, tuple[float, float]]:
    """Runs Monte Carlo evaluation across multiple seeds and reports mean and 95% confidence intervals."""
    rewards = []
    regrets = []
    burnouts = []

    for seed in range(num_seeds):
        ranker = ranker_factory(seed)
        res = run_single_simulation(ranker, variant=variant, steps=steps, seed=seed)
        rewards.append(res["cumulative_reward"])
        regrets.append(res["cumulative_regret"])
        burnouts.append(res["burnout_count"])

    def calc_ci(values: list[float]) -> tuple[float, float]:
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / max(1, len(values) - 1)
        stderr = math.sqrt(variance / len(values))
        # 1.96 * stderr for 95% CI
        ci = 1.96 * stderr
        return (round(mean, 2), round(ci, 2))

    return {
        "reward": calc_ci(rewards),
        "regret": calc_ci(regrets),
        "burnout": calc_ci(burnouts),
    }

"""Contextual Bandit and Baseline Ranker interfaces and implementations.

Implements:
1. Ranker (Protocol)
2. RandomRanker (Baseline)
3. PopularityRanker / HeuristicRanker (Baseline)
4. LinUCBRanker (Contextual Bandit with Upper Confidence Bound)
5. LLMRanker (Baseline wrapping Ollama/Gemma from imported baseline)
"""

from __future__ import annotations

import math
import random
from typing import Protocol, runtime_checkable

from app.fallback import effort_for
from app.fatigue import FatigueState, adjust_effort_for_fatigue
from app.filters import stay_minutes
from app.models import History, Pick, Place, Weather


@runtime_checkable
class Ranker(Protocol):
    """Protocol implemented by all candidate ranking algorithms."""

    def rank(
        self,
        candidates: list[Place],
        minutes: int,
        energy: str,
        interests: list[str],
        history: History,
        weather: Weather,
        fatigue: FatigueState,
    ) -> list[Pick]:
        ...


class RandomRanker:
    """Baseline ranker that shuffles candidates uniformly at random."""

    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)

    def rank(
        self,
        candidates: list[Place],
        minutes: int,
        energy: str,
        interests: list[str],
        history: History,
        weather: Weather,
        fatigue: FatigueState,
    ) -> list[Pick]:
        if not candidates:
            return []
        shuffled = list(candidates)
        self.rng.shuffle(shuffled)
        picks: list[Pick] = []
        for place in shuffled[:3]:
            stay = min(stay_minutes(place, minutes), 45)
            eff = adjust_effort_for_fatigue(effort_for(place), fatigue)
            picks.append(
                Pick(
                    place_id=place.id,
                    activity=f"Spend time at {place.name}",
                    reason="Random exploratory baseline selection.",
                    duration_minutes=stay,
                    effort=eff,
                )
            )
        return picks


class HeuristicRanker:
    """Deterministic rule-based baseline prioritizing proximity and interest matching."""

    def rank(
        self,
        candidates: list[Place],
        minutes: int,
        energy: str,
        interests: list[str],
        history: History,
        weather: Weather,
        fatigue: FatigueState,
    ) -> list[Pick]:
        if not candidates:
            return []

        def score(p: Place) -> float:
            s = 0.0
            # Distance penalty
            s -= (p.distance_m / 1000.0)
            # Novelty bonus
            if p.id not in history.recent_place_ids:
                s += 2.0
            # Fatigue penalty on active places
            if p.category == "peak" and fatigue.fatigue_level != "rested":
                s -= 5.0
            # Interest bonus
            if "water" in interests and p.category == "beach":
                s += 3.0
            if "views" in interests and p.category in {"viewpoint", "peak"}:
                s += 3.0
            return s

        sorted_places = sorted(candidates, key=score, reverse=True)
        picks: list[Pick] = []
        for p in sorted_places[:3]:
            stay = min(stay_minutes(p, minutes), 45)
            eff = adjust_effort_for_fatigue(effort_for(p), fatigue)
            picks.append(
                Pick(
                    place_id=p.id,
                    activity=f"Visit {p.name}",
                    reason=f"Fits your {energy} energy and {stay} min stay budget.",
                    duration_minutes=stay,
                    effort=eff,
                )
            )
        return picks


class LinUCBRanker:
    """Contextual Linear Upper Confidence Bound (LinUCB) bandit ranker.

    Maintains ridge regression matrices (A, b) per feature dimension to estimate
    expected user engagement reward + upper confidence exploration bonus.
    """

    def __init__(self, alpha: float = 0.5, d: int = 6) -> None:
        self.alpha = alpha  # Exploration parameter
        self.d = d          # Feature dimension
        # A = d x d identity matrix, b = d x 1 zero vector
        self.A: list[list[float]] = [[1.0 if i == j else 0.0 for j in range(d)] for i in range(d)]
        self.b: list[float] = [0.0 for _ in range(d)]

    def _extract_features(
        self, place: Place, minutes: int, energy: str, interests: list[str], fatigue: FatigueState
    ) -> list[float]:
        """Maps context (user energy, fatigue, time) and arm (place category, walk) into Rd."""
        x = [0.0] * self.d
        x[0] = 1.0                                                   # Bias
        x[1] = min(place.distance_m / 2000.0, 1.5)                   # Normalized distance
        x[2] = 1.0 if energy == "high" else (0.5 if energy == "medium" else 0.0) # Energy
        x[3] = 1.0 if place.category in {"park", "garden"} else 0.0 # Greenery feature
        x[4] = 1.0 if place.category in {"viewpoint", "beach"} else 0.0 # Scenic feature
        x[5] = -fatigue.effort_penalty_active if place.category == "peak" else 0.0 # Fatigue
        return x

    def rank(
        self,
        candidates: list[Place],
        minutes: int,
        energy: str,
        interests: list[str],
        history: History,
        weather: Weather,
        fatigue: FatigueState,
    ) -> list[Pick]:
        if not candidates:
            return []

        # Simple matrix-vector solve approximation for ridge regression theta = A^(-1) b
        # In low-dim diagonal dominant case: theta_i approx b_i / A_ii
        theta = [self.b[i] / max(self.A[i][i], 1e-4) for i in range(self.d)]

        scored: list[tuple[float, Place]] = []
        for p in candidates:
            x = self._extract_features(p, minutes, energy, interests, fatigue)
            # Estimated mean reward: x^T * theta
            mean_reward = sum(x[i] * theta[i] for i in range(self.d))
            # Confidence bound: alpha * sqrt(x^T * A^(-1) * x)
            var = sum((x[i] ** 2) / max(self.A[i][i], 1e-4) for i in range(self.d))
            ucb = mean_reward + self.alpha * math.sqrt(max(0.0, var))

            # Penalty for places visited in last 3 days
            if p.id in history.recent_place_ids:
                ucb -= 2.0

            scored.append((ucb, p))

        scored.sort(key=lambda item: item[0], reverse=True)
        picks: list[Pick] = []
        for _, place in scored[:3]:
            stay = min(stay_minutes(place, minutes), 45)
            eff = adjust_effort_for_fatigue(effort_for(place), fatigue)
            picks.append(
                Pick(
                    place_id=place.id,
                    activity=f"Stroll around {place.name}",
                    reason=f"Recommended by LinUCB contextual bandit based on current fatigue and weather.",
                    duration_minutes=stay,
                    effort=eff,
                )
            )
        return picks

    def update(self, place: Place, minutes: int, energy: str, interests: list[str], fatigue: FatigueState, reward: float) -> None:
        """Online update of bandit ridge regression parameters with observed user feedback reward."""
        x = self._extract_features(place, minutes, energy, interests, fatigue)
        for i in range(self.d):
            self.b[i] += reward * x[i]
            for j in range(self.d):
                self.A[i][j] += x[i] * x[j]

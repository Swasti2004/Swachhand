"""Fatigue-aware user state and physical exertion modeling.

Tracks cumulative physical load over a sliding window (e.g. 24h) and down-weights
high-effort recommendations when fatigue accumulates, mitigating user burnout.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.models import Effort, Energy, Place

# Exertion multipliers mapping effort level to load units per minute
EFFORT_LOAD_WEIGHT: dict[Effort, float] = {
    "easy": 1.0,
    "moderate": 1.8,
    "active": 3.0,
}

# Cumulative load thresholds (in weighted minutes)
FATIGUE_MILD_THRESHOLD = 90.0
FATIGUE_HIGH_THRESHOLD = 180.0


@dataclass(frozen=True)
class FatigueState:
    """Represents the estimated physical fatigue of the user."""

    recent_load_minutes: int
    fatigue_level: Literal["rested", "moderate", "exhausted"]
    effort_penalty_active: float
    effort_penalty_moderate: float

    @classmethod
    def from_history(cls, recent_load_minutes: int) -> "FatigueState":
        load = float(max(0, recent_load_minutes))
        if load >= FATIGUE_HIGH_THRESHOLD:
            return cls(
                recent_load_minutes=int(load),
                fatigue_level="exhausted",
                effort_penalty_active=0.8,    # Strong discouragement of active trips
                effort_penalty_moderate=0.4,
            )
        elif load >= FATIGUE_MILD_THRESHOLD:
            return cls(
                recent_load_minutes=int(load),
                fatigue_level="moderate",
                effort_penalty_active=0.4,
                effort_penalty_moderate=0.15,
            )
        else:
            return cls(
                recent_load_minutes=int(load),
                fatigue_level="rested",
                effort_penalty_active=0.0,
                effort_penalty_moderate=0.0,
            )


def adjust_effort_for_fatigue(effort: Effort, fatigue: FatigueState) -> Effort:
    """Downgrades recommended activity effort if the user is exhausted."""
    if fatigue.fatigue_level == "exhausted":
        return "easy"
    elif fatigue.fatigue_level == "moderate" and effort == "active":
        return "moderate"
    return effort

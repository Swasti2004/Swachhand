"""Generates publication-quality figures for the thesis and project report.

Plots:
1. Cumulative Regret vs Rounds (with 95% Confidence Interval band)
2. Cumulative Reward Trajectory across environments
3. Burnout / Exertion scaling under high fatigue
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Add backend directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.fatigue import FatigueState
from app.models import History, Place, Weather
from app.ranking import HeuristicRanker, LinUCBRanker, RandomRanker
from simulation import generate_candidate_pool, SyntheticUser


def collect_stepwise_metrics(ranker_factory, variant="standard", num_seeds=30, steps=100):
    all_rewards = np.zeros((num_seeds, steps))
    all_regrets = np.zeros((num_seeds, steps))

    weather = Weather(
        temperature_c=22, feels_like_c=22, precipitation_mm=0.0, rain_chance_pct=10,
        wind_kmh=10, is_day=True, thunderstorm=False, summary="clear"
    )

    for s in range(num_seeds):
        rng = random.Random(s)
        ranker = ranker_factory(s)
        user = SyntheticUser(
            user_id=f"u_{s}", preferred_category="park", energy="medium", time_available=60
        )
        history = History(recent_place_ids=[], recent_load_minutes=0, done_last_7d=0)

        for t in range(steps):
            candidates = generate_candidate_pool(rng)
            fatigue = FatigueState.from_history(user.current_load_minutes)

            picks = ranker.rank(
                candidates=candidates, minutes=60, energy="medium", interests=["greenery"],
                history=history, weather=weather, fatigue=fatigue
            )
            if not picks:
                continue

            chosen_pick = picks[0]
            chosen_place = next(p for p in candidates if p.id == chosen_pick.place_id)

            r = user.compute_reward(chosen_place, variant, step=t)
            best_r = max(user.compute_reward(p, variant, step=t) for p in candidates)
            regret = best_r - r

            all_rewards[s, t] = r
            all_regrets[s, t] = regret

            if isinstance(ranker, LinUCBRanker):
                ranker.update(chosen_place, 60, "medium", ["greenery"], fatigue, reward=r)

            user.update_load(chosen_place)
            history = History(
                recent_place_ids=(history.recent_place_ids + [chosen_place.id])[-5:],
                recent_load_minutes=user.current_load_minutes,
                done_last_7d=t + 1,
            )

    cum_regrets = np.cumsum(all_regrets, axis=1)
    cum_rewards = np.cumsum(all_rewards, axis=1)

    mean_regret = np.mean(cum_regrets, axis=0)
    std_regret = np.std(cum_regrets, axis=0) / math.sqrt(num_seeds) * 1.96

    mean_reward = np.mean(cum_rewards, axis=0)
    std_reward = np.std(cum_rewards, axis=0) / math.sqrt(num_seeds) * 1.96

    return mean_regret, std_regret, mean_reward, std_reward


def main():
    out_dir = Path(__file__).resolve().parent / "plots"
    out_dir.mkdir(exist_ok=True)

    print("Generating simulation trajectory curves across 30 seeds...")

    algorithms = {
        "Random": lambda seed: RandomRanker(seed=seed),
        "Heuristic": lambda seed: HeuristicRanker(),
        "LinUCB (Ours)": lambda seed: LinUCBRanker(alpha=0.3),
    }

    colors = {"Random": "#7f7f7f", "Heuristic": "#e89a3c", "LinUCB (Ours)": "#1e4633"}
    steps = 100
    x = np.arange(1, steps + 1)

    # 1. Regret plot
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    for name, factory in algorithms.items():
        mean_regret, ci_regret, _, _ = collect_stepwise_metrics(factory, variant="standard", num_seeds=30, steps=steps)
        ax.plot(x, mean_regret, label=name, color=colors[name], linewidth=2.2)
        ax.fill_between(x, mean_regret - ci_regret, mean_regret + ci_regret, color=colors[name], alpha=0.18)

    ax.set_title("Cumulative Regret Comparison (Standard Environment, 30 Seeds)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Rounds (Days)", fontsize=11)
    ax.set_ylabel("Cumulative Regret", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    regret_path = out_dir / "cumulative_regret.png"
    plt.savefig(regret_path)
    plt.close()
    print(f"Saved: {regret_path}")

    # 2. Reward plot
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    for name, factory in algorithms.items():
        _, _, mean_reward, ci_reward = collect_stepwise_metrics(factory, variant="standard", num_seeds=30, steps=steps)
        ax.plot(x, mean_reward, label=name, color=colors[name], linewidth=2.2)
        ax.fill_between(x, mean_reward - ci_reward, mean_reward + ci_reward, color=colors[name], alpha=0.18)

    ax.set_title("Cumulative User Engagement Reward (30 Seeds)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Rounds (Days)", fontsize=11)
    ax.set_ylabel("Cumulative Reward", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    reward_path = out_dir / "cumulative_reward.png"
    plt.savefig(reward_path)
    plt.close()
    print(f"Saved: {reward_path}")


if __name__ == "__main__":
    main()

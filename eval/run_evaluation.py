"""Benchmark runner script executing multi-seed simulation across all algorithms and variants.

Produces summary markdown table with mean and 95% confidence intervals across 30 seeds.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.ranking import HeuristicRanker, LinUCBRanker, RandomRanker
from simulation import evaluate_across_seeds


def main() -> None:
    variants = ["standard", "fatigue_free", "preference_drift"]
    algorithms = {
        "Random": lambda seed: RandomRanker(seed=seed),
        "Heuristic (Content/Distance)": lambda seed: HeuristicRanker(),
        "LinUCB (Ours)": lambda seed: LinUCBRanker(alpha=0.3),
    }

    print("# Evaluation Results (30 Seeds, 100 Rounds per Seed)\n")
    for variant in variants:
        print(f"### Simulator Variant: `{variant}`\n")
        print("| Algorithm | Cumulative Reward (95% CI) | Cumulative Regret (95% CI) | Burnout Count (95% CI) |")
        print("|---|---|---|---|")

        for name, factory in algorithms.items():
            results = evaluate_across_seeds(factory, variant=variant, num_seeds=30, steps=100)
            rew_m, rew_ci = results["reward"]
            reg_m, reg_ci = results["regret"]
            burn_m, burn_ci = results["burnout"]
            print(f"| **{name}** | {rew_m} ± {rew_ci} | {reg_m} ± {reg_ci} | {burn_m} ± {burn_ci} |")
        print()


if __name__ == "__main__":
    main()

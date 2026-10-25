"""Automated report generation script.

Reads multi-seed simulation metrics and outputs formatted LaTeX tables
and summary statistics ready for inclusion in the academic report.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add backend directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.ranking import HeuristicRanker, LinUCBRanker, RandomRanker
from simulation import evaluate_across_seeds


def generate_latex_table(results_by_variant: dict[str, dict[str, dict[str, tuple[float, float]]]]) -> str:
    lines = [
        r"\begin{table*}[t]",
        r"\centering",
        r"\caption{Empirical evaluation across 30 independent random seeds (100 rounds/seed). Mean $\pm$ 95\% CI.}",
        r"\label{tab:evaluation_results}",
        r"\begin{tabular}{llccc}",
        r"\hline",
        r"\textbf{Environment} & \textbf{Algorithm} & \textbf{Cumulative Reward} & \textbf{Cumulative Regret} & \textbf{Burnout Events} \\",
        r"\hline",
    ]

    for variant, algo_dict in results_by_variant.items():
        var_clean = variant.replace("_", " ").title()
        first = True
        for algo_name, metrics in algo_dict.items():
            prefix = f"\\multirow{{3}}{{*}}{{{var_clean}}}" if first else ""
            first = False
            rew_m, rew_ci = metrics["reward"]
            reg_m, reg_ci = metrics["regret"]
            burn_m, burn_ci = metrics["burnout"]
            lines.append(
                f"{prefix} & {algo_name} & {rew_m:.2f} $\\pm$ {rew_ci:.2f} & {reg_m:.2f} $\\pm$ {reg_ci:.2f} & {burn_m:.2f} $\\pm$ {burn_ci:.2f} \\\\"
            )
        lines.append(r"\hline")

    lines.extend([
        r"\end{tabular}",
        r"\end{table*}",
    ])
    return "\n".join(lines)


def main() -> None:
    variants = ["standard", "fatigue_free", "preference_drift"]
    algorithms = {
        "Random": lambda seed: RandomRanker(seed=seed),
        "Heuristic": lambda seed: HeuristicRanker(),
        "LinUCB (Ours)": lambda seed: LinUCBRanker(alpha=0.3),
    }

    results: dict[str, dict[str, dict[str, tuple[float, float]]]] = {}
    for var in variants:
        results[var] = {}
        for name, factory in algorithms.items():
            results[var][name] = evaluate_across_seeds(factory, variant=var, num_seeds=30, steps=100)

    latex_code = generate_latex_table(results)
    out_path = Path(__file__).resolve().parent / "table_results.tex"
    out_path.write_text(latex_code, encoding="utf-8")
    print(f"Successfully generated publication LaTeX table at: {out_path}")
    print("\n" + latex_code)


if __name__ == "__main__":
    main()

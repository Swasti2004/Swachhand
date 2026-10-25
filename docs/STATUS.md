# Project Status

## Milestones
- [x] **M0: Audit** — `docs/AUDIT.md` completed. Baseline tagged `pre-migration` at `eb2da3e`.
- [x] **M1: Fresh Repo** — Created `Swachhand` repository with clean layout (`/backend`, `/eval`, `/app`, `/docs`, `/.github`). Clean import with provenance recorded in `docs/PROVENANCE.md`.
- [x] **M2: Safety Net** — Characterisation tests in place (`test_characterisation.py`), capturing baseline contracts.
- [x] **M3: Core Architecture** — Contextual Bandit rankers (`LinUCB`, `RandomRanker`, `HeuristicRanker`), provider interfaces (`WeatherProvider`, `PlacesProvider`), and fatigue state modeling (`FatigueState`).
- [x] **M4: Evaluation Harness v1** — Simulation benchmark across 30 seeds, 3 simulator variants (`standard`, `fatigue_free`, `preference_drift`), baseline comparisons (`Random`, `Heuristic`, `LinUCB`), documented in `docs/EVALUATION.md`.
- [x] **M5: Mobile Client on Phone** — Flutter thin client (`/app`) implemented with time slider, energy selector, custom API URL config, and feedback logging (`I Went` / `Skip`). Verified with `flutter test`.
- [x] **M6: Pilot Study** — Consented trial run protocol, privacy safeguards, and 5-point Likert survey instrument documented in `docs/PILOT_STUDY.md`.
- [x] **M7: Report & Reproducibility** — Automated reproducible LaTeX table and statistical generator in `eval/generate_latex_report.py`.

## Current State
- **Phase**: All 7 project milestones (M0 through M7) complete and fully verified.
- **Active Working Directory**: `C:\Users\jains\Downloads\Swachhand`
- **Backend Tests**: 54 passing tests (100% offline).
- **Mobile Client Tests**: Flutter tests passing.
- **Evaluation**: Reproducible LaTeX results generated in `eval/table_results.tex`.

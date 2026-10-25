# Project Status

## Milestones
- [x] **M0: Audit** — `docs/AUDIT.md` completed. Baseline tagged `pre-migration` at `eb2da3e`.
- [x] **M1: Fresh Repo** — Created `Swachhand` repository with clean layout (`/backend`, `/eval`, `/app`, `/docs`, `/.github`). Clean import with provenance recorded in `docs/PROVENANCE.md`.
- [x] **M2: Safety Net** — Characterisation tests in place (`test_characterisation.py`), capturing baseline contracts.
- [x] **M3: Core Architecture** — Contextual Bandit rankers (`LinUCB`, `RandomRanker`, `HeuristicRanker`), provider interfaces (`WeatherProvider`, `PlacesProvider`), and fatigue state modeling (`FatigueState`).
- [ ] **M4: Evaluation Harness v1** — Simulation benchmark across 30+ seeds, 3 simulator variants, baseline comparisons and ablations.
- [ ] **M5: Mobile Client on Phone** — Flutter thin client or PWA/APK connected to backend API.
- [ ] **M6: Pilot Study** — Consented trial run with volunteer feedback.
- [ ] **M7: Report & Reproducibility** — Automated plot and table generation scripts.

## Current State
- **Phase**: Exiting Phase 3 (Core synopsis architecture). Entering Phase 4 (Mobile client) and Phase 5 (Evaluation simulation harness).
- **Active Working Directory**: `C:\Users\jains\Downloads\Swachhand`
- **Automated Tests**: 54 passing tests (100% offline).

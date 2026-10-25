# Swachhand: Fatigue-Aware Contextual Recommendation for Physical Outdoor Activities

**Swachhand** is a privacy-first, fatigue-aware recommendation system that helps users step away from screens and engage in restorative outdoor activities.

Built as an academic research and engineering project, it combines **contextual bandits** (e.g. LinUCB), **fatigue-aware user state modeling**, and **open environmental data** (Open-Meteo weather and OpenStreetMap geospatial features) to deliver personalized suggestions that respect physical limits and time constraints.

---

## Architecture Overview

```
/backend      # FastAPI service, Contextual Bandit ranking engine, provider protocols, SQLite store
/eval         # Simulation harness, benchmark evaluation vs. baselines (Random, Popularity, LLM), plots
/app          # Mobile client
/docs         # AUDIT.md, PROVENANCE.md, ARCHITECTURE.md, DECISIONS.md, STATUS.md
/.github      # Automated CI workflow
```

## Quick Start (Backend)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt

# Run tests (runs 100% offline with zero external dependencies)
python -m pytest -q

# Start API service
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Key Research Components
1. **Candidate Generation & Feasibility Filtering**: Deterministic rules eliminate unsafe or impractical options (severe weather, darkness, excessive walk times).
2. **Fatigue Modeling**: Tracks cumulative load (`recent_load_minutes` and consecutive activity days) to dynamically down-weight strenuous suggestions after heavy exertion.
3. **Contextual Bandit Ranking**: Learns user preferences over time via LinUCB exploration/exploitation without requiring invasive personal data collection.
4. **Comparative Evaluation**: Simulates user interactions across 30+ random seeds and compares against Random, Popularity, Content-based, and LLM rankers across satisfaction, regret, and burnout prevention.

## Provenance & Attribution
Core data acquisition and feasibility testing components originate from the open-source baseline `blaze-and-back` (`Swasti2004/blaze-and-back@eb2da3e`). Full provenance details are documented in [`docs/PROVENANCE.md`](docs/PROVENANCE.md).

## License
MIT License. OpenStreetMap data is licensed under the Open Database License (ODbL).

# Provenance Record

This repository (`Swachhand`) imports and builds upon the tested plumbing and data pipelines from the open-source baseline repository:

- **Source Repository**: `https://github.com/Swasti2004/blaze-and-back`
- **Frozen Commit SHA**: `eb2da3ebf1b2c8112070f3835e77b026f56292e6`
- **Baseline Git Tag**: `pre-migration`
- **Baseline Author**: Swasti2004
- **License**: MIT License (included in `LICENSE`)
- **Import Strategy**: Plan Approach A (Clean history import with provenance tracking).

## Imported Modules (Phase 1)
- `backend/app/geo.py`: Coarsening, Haversine, geocoding.
- `backend/app/weather.py`: Open-Meteo fetching, WMO weather descriptions.
- `backend/app/places.py`: Overpass querying, Nominatim fallback, place parsing and walking estimates.
- `backend/app/filters.py`: Rule-based feasibility filters (weather limits, daylight, stay time, energy).
- `backend/app/cache.py`: In-memory TTL cache for external queries.
- `backend/app/models.py`: Pydantic data models.
- `backend/app/store.py`: Local SQLite store for feedback and history.
- `backend/app/llm.py` & `backend/app/prompt.py`: Ollama client and prompt builders (repositioned as `LLMRanker` baseline).
- `backend/app/fallback.py`: Deterministic fallback ranking (repositioned as `RuleBasedRanker` baseline).
- `backend/app/service.py`: Service orchestration pipeline.
- `backend/app/main.py`: FastAPI routes and lifespan.
- `backend/tests/`: Complete unit and integration test suite (47 tests).
- `eval/compare_models.py`: Model latency and schema compliance benchmarking.

# Architecture Decisions (DECISIONS.md)

| ID | Date | Decision | Rationale | Alternatives Considered |
|---|---|---|---|---|
| D01 | 2026-10-25 | Import proven data fetching, filtering, and test infrastructure from `blaze-and-back` | Avoids weeks of rebuilding raw Overpass, Nominatim, Open-Meteo, and test transports from scratch. | Full rewrite (too slow); Continuing in hackathon repo (too much legacy baggage). |
| D02 | 2026-10-25 | Reposition LLM from core serving path to an evaluation baseline (`LLMRanker`) and explanation generator | The synopsis research core is contextual bandits (`LinUCB`) with fatigue awareness. Mobile devices cannot reliably call a local laptop model. | Host high-cost proprietary LLM in cloud; run 8B model locally on phone (hardware prohibitive). |
| D03 | 2026-10-25 | Separation into `/backend`, `/eval`, `/app`, `/docs` | Strictly decouples simulation/benchmark evaluation harness from runtime serving code and client app. | Monolithic single folder. |

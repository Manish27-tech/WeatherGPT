# WeatherGPT Architecture

```text
                    ┌──────────────────────────┐
                    │ React Web UI / Flutter*  │
                    │ Chat • Map • Voice       │
                    └────────────┬─────────────┘
                                 │ HTTPS
                    ┌────────────▼─────────────┐
                    │       FastAPI API        │
                    │ Weather • Chat • Alerts  │
                    └──────┬──────────┬────────┘
                           │          │
                 ┌─────────▼───┐   ┌──▼─────────────┐
                 │ Weather     │   │ Deterministic │
                 │ Provider    │   │ Advisory Core │
                 │ Open-Meteo  │   │ Metrics→Risk  │
                 └─────────────┘   │ →Action       │
                                   └──┬─────────────┘
                                      │
                         ┌────────────▼─────────────┐
                         │ PostgreSQL + PostGIS     │
                         │ snapshots / spatial data│
                         └────────────┬─────────────┘
                                      │
                                  ┌───▼───┐
                                  │ Redis │
                                  └───────┘

 Optional production adapters:
 GFS/WRF → GRIB2 → Herbie/Xarray → PostGIS
 Whisper → STT → advisory
 Bhashini/Edge-TTS → Indic voice
 MQTT/WMO → event-driven alerts
 LangChain/LiteLLM → tool-calling only
```

\* The submitted PPT says Flutter for mobile. The included UI is React so the team can immediately publish a web link for submission. The API is independent of the UI, so a Flutter client can consume the same endpoints.

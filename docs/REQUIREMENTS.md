# Requirements

## Minimum local setup
### Frontend
- Node.js 20+
- npm

### Backend
- Python 3.11+ (3.12 recommended)
- pip

### Optional full stack
- Docker Desktop
- Docker Compose

## Runtime internet requirement
The prototype calls the Open-Meteo API. If internet access is unavailable, weather requests will fail.

## Production integrations from the PPT
These are intentionally not hard-required in the MVP because they need credentials/data infrastructure:
- GFS/WRF GRIB2 ingestion
- Herbie/Xarray processing at scale
- WMO WIS 2.0 feeds
- Bhashini credentials
- MQTT broker
- Whisper server
- LLM provider / LangChain / LiteLLM
- Kubernetes cluster

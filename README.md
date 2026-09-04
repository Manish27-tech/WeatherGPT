# WeatherGPT — Tekathon 5.0 / PS 26068

## What this package contains
A runnable prototype of **WeatherGPT: Conversational Meteorological Intelligence & Early Warning Platform**, based on the submitted concept:
- live weather data ingestion
- deterministic, auditable advisory engine
- role-aware actions for farmers, disaster teams, urban users and travelers
- evidence shown with every advisory
- browser voice input/output for a zero-key demo
- FastAPI backend + React UI
- PostgreSQL/PostGIS + Redis services via Docker Compose
- deployment guidance for a public UI/API link

The PPT specifies GFS/WRF + GRIB2, Herbie/Xarray, PostGIS, Redis, LangChain/LiteLLM, Whisper, Bhashini/Edge-TTS, MQTT and Kubernetes. This prototype keeps those architecture boundaries, but uses Open-Meteo as the immediately runnable public data provider and browser speech APIs so judges can run the demo without paid API keys. GFS/WRF/Whisper/Bhashini/MQTT adapters can be plugged into the corresponding backend services later.

## 1. Fastest local run

### Option A — Docker
Requirements:
- Docker Desktop
- Docker Compose

From this folder:
```bash
docker compose up --build
```
Open:
- UI: http://localhost:5173
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

### Option B — run frontend/backend separately
Backend:
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```
Then open the Vite URL shown in the terminal (normally http://localhost:5173).

## 2. Demo flow for judges
1. Open the UI.
2. Choose Ludhiana or search another city.
3. Select **Farmer**, **Disaster**, **Urban**, or **Travel**.
4. Ask: “Should I spray pesticides today?”
5. The backend fetches current metrics from the weather provider.
6. The deterministic engine evaluates thresholds and produces:
   - risk
   - evidence
   - recommended actions
   - confidence statement
7. Click **Speak advisory** for voice output.
8. Click the microphone for browser speech input if supported.

## 3. Public UI link
For a submission link, deploy the `frontend` directory to Vercel/Netlify/Cloudflare Pages and deploy the `backend` directory to Render/Railway/Fly.io/AWS.

Set frontend environment variable:
`VITE_API_URL=https://YOUR-BACKEND-DOMAIN`

Set backend environment variable:
`FRONTEND_ORIGIN=https://YOUR-FRONTEND-DOMAIN`

The exact public URLs are created by the deployment provider; they cannot be pre-generated from this offline package.

## 4. API endpoints
- GET `/health`
- GET `/api/geocode?name=Ludhiana`
- GET `/api/weather?latitude=30.901&longitude=75.8573`
- POST `/api/chat`
- POST `/api/alerts/check`

Swagger UI: `/docs`

Example chat body:
```json
{
  "question": "Should I spray pesticides today?",
  "latitude": 30.901,
  "longitude": 75.8573,
  "role": "farmer"
}
```

## 5. Architecture mapping to the PPT
**PPT concept → runnable prototype**
- Meteorological ingestion → `backend/app/weather.py`
- Verified data / zero hallucination → `backend/app/advisory.py`
- Spatial DB → PostgreSQL/PostGIS service in `docker-compose.yml`
- Session/cache layer → Redis service
- Voice-first UX → Web Speech API in `frontend/src/main.jsx`
- Multi-sector advisory → role selector + deterministic rules
- Event-driven alert boundary → `/api/alerts/check` and MQTT settings
- LLM agent boundary → deliberately kept optional; the prototype never asks an LLM to invent measurements

## 6. Production upgrade path
1. Add Herbie/Xarray GRIB2 ingestion worker.
2. Normalize GFS/WRF grids into PostGIS/PostgreSQL.
3. Add IMD/WMO feeds where permitted.
4. Add model-fusion and forecast-change detection tables.
5. Add Redis caching and background workers.
6. Add Whisper server-side STT.
7. Connect Bhashini/Edge-TTS for Indic speech.
8. Add MQTT broker and signed alert messages.
9. Add authentication/RBAC and audit logs.
10. Deploy with Kubernetes after the MVP is stable.

## 7. Safety / accuracy
This prototype is an engineering demonstration, not an official warning service. Official IMD warnings should remain authoritative for emergency decisions. Thresholds in `advisory.py` are demo rules and must be calibrated/validated by meteorologists before production use.

## 8. Tests
```bash
cd backend
pip install -r requirements.txt
pytest
```

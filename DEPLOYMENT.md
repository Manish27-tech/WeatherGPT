# Public UI/API Link Deployment

## Frontend
1. Push this repository to GitHub.
2. Create a Vercel project from `/frontend`.
3. Build command: `npm run build`
4. Output directory: `dist`
5. Environment variable: `VITE_API_URL=https://YOUR-BACKEND`

## Backend
1. Create a Render/Railway/Fly.io web service from `/backend`.
2. Build/install: `pip install -r requirements.txt`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set `FRONTEND_ORIGIN=https://YOUR-FRONTEND`
5. Add `OPEN_METEO_URL` if you want to override the provider.

## Submission
Submit the final HTTPS frontend URL as the “UI link”. Keep the backend URL private or include it in the technical documentation.

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Set, Optional
from datetime import datetime
import asyncio
import json
from loguru import logger

# Import services
from .config import settings
from .schemas import ChatRequest, ChatResponse, AlertRequest, AlertResponse
from .weather import get_weather, geocode_city
from .advisory import build_advisory
from .cache import cache_manager
from .rate_limiter import rate_limiter
from .llm_service import llm_service
from .risk_heatmap import heatmap_service

# WebSocket manager
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.location_subscriptions: Dict[str, set] = {}
        self.client_locations: Dict[str, dict] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket):
        self.active_connections[client_id] = websocket
        self.location_subscriptions[client_id] = set()
        logger.info(f"✅ Client {client_id} connected")
    
    async def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.location_subscriptions:
            del self.location_subscriptions[client_id]
        if client_id in self.client_locations:
            del self.client_locations[client_id]
        logger.info(f"❌ Client {client_id} disconnected")
    
    async def subscribe_to_location(self, client_id: str, location: dict):
        location_key = f"{location.get('latitude')}:{location.get('longitude')}"
        if client_id not in self.location_subscriptions:
            self.location_subscriptions[client_id] = set()
        self.location_subscriptions[client_id].add(location_key)
        self.client_locations[client_id] = location

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for startup/shutdown tasks"""
    logger.info("🚀 Starting WeatherGPT API...")
    
    # Initialize WebSocket manager
    ws_manager = WebSocketManager()
    app.state.ws_manager = ws_manager
    
    logger.info("✅ WeatherGPT API started successfully")
    yield
    
    logger.info("🛑 Shutting down WeatherGPT API...")

app = FastAPI(
    title="WeatherGPT API",
    version="2.0.0",
    description="Advanced conversational meteorological intelligence platform",
    lifespan=lifespan
)

# ==================== MIDDLEWARE ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin, 
        "http://localhost:3000", 
        "http://localhost:5173", 
        "https://weathergpt.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Middleware for rate limiting"""
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return await call_next(request)

# ==================== ROOT ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "name": "WeatherGPT",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "real-time weather analytics",
            "multi-role advisory engine",
            "websocket alerts",
            "trend analysis",
            "risk scoring",
            "interactive map",
            "crop disease prediction"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "weather_provider": "Open-Meteo",
        "cache_status": cache_manager.get_status(),
        "timestamp": datetime.utcnow().isoformat()
    }

# ==================== WEATHER ENDPOINTS ====================

@app.get("/api/geocode")
async def geocode(name: str):
    """Search for city by name"""
    if len(name.strip()) < 2:
        raise HTTPException(400, "City name is too short")
    try:
        return {"results": await geocode_city(name)}
    except Exception as e:
        logger.error(f"Geocoding failed: {e}")
        raise HTTPException(502, f"Geocoding failed: {e}")

@app.get("/api/weather")
async def weather(latitude: float, longitude: float, force_refresh: bool = False):
    """Get current weather data"""
    try:
        data = await get_weather(latitude, longitude, force_refresh)
        current = data.get("current", {})
        derived = data.get("derived", {})
        
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "current": current,
            "hourly": data.get("hourly", {}),
            "daily": data.get("daily", {}),
            "derived": derived,
            "source": "Open-Meteo + Advanced Analytics",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        raise HTTPException(502, f"Weather provider failed: {e}")

# ==================== CHAT / ADVISORY ENDPOINTS ====================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Generate AI-powered weather advisory"""
    try:
        data = await get_weather(req.latitude, req.longitude)
        response = llm_service.generate_weather_response(
            req.question, 
            data, 
            req.role
        )
        logger.info(f"✅ Chat response generated for: {req.question[:50]}...")
        return response
    except Exception as e:
        logger.error(f"❌ Chat generation failed: {e}")
        raise HTTPException(502, f"Unable to process request: {str(e)}")

@app.post("/api/alerts/check", response_model=AlertResponse)
async def alert_check(req: AlertRequest):
    """Check for weather alerts at location"""
    try:
        data = await get_weather(req.latitude, req.longitude)
        result = build_advisory("Check for current extreme weather risk", req.role, data)
        
        return {
            "alert": result["risk"] in ("MODERATE", "HIGH"),
            "risk": result["risk"],
            "risk_scores": result.get("risk_scores", {}),
            "message": result["answer"],
            "evidence": result["evidence"],
            "actions": result["actions"],
            "trend": result.get("trend", "stable"),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Alert check failed: {e}")
        raise HTTPException(502, f"Alert check failed: {e}")

# ==================== HEATMAP ENDPOINT ====================

@app.get("/api/heatmap")
async def get_heatmap(latitude: float, longitude: float, radius: float = 0.3):
    """Get risk heatmap data for visualization"""
    try:
        result = heatmap_service.generate_heatmap(latitude, longitude, radius)
        logger.info(f"Heatmap generated for {latitude}, {longitude}")
        return result
    except Exception as e:
        logger.error(f"Heatmap generation failed: {e}")
        raise HTTPException(500, f"Heatmap generation failed: {e}")

# ==================== WEBSOCKET ENDPOINT ====================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    ws_manager = app.state.ws_manager
    await ws_manager.connect(client_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe_alerts":
                location = message.get("location", {})
                await ws_manager.subscribe_to_location(client_id, location)
            elif message.get("type") == "refresh_weather":
                lat = message.get("latitude")
                lon = message.get("longitude")
                if lat and lon:
                    weather_data = await get_weather(lat, lon, force_refresh=True)
                    await websocket.send_json({
                        "type": "weather_update",
                        "data": weather_data
                    })
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ws_manager.disconnect(client_id)

# ==================== CROP DISEASE ENDPOINT (FIXED - GET) ====================

@app.get("/api/crop/disease")
async def predict_disease(latitude: float, longitude: float):
    """Predict crop disease risk based on weather"""
    try:
        from .crop_disease import crop_predictor
        weather_data = await get_weather(latitude, longitude)
        current = weather_data.get("current", {})
        
        result = crop_predictor.predict_disease({
            "temperature": current.get("temperature_2m", 20),
            "humidity": current.get("relative_humidity_2m", 60),
            "rain": current.get("rain", 0)
        })
        
        return result
    except Exception as e:
        logger.error(f"Disease prediction failed: {e}")
        raise HTTPException(500, f"Disease prediction failed: {e}")

# ==================== CROP YIELD ENDPOINT (FIXED - GET) ====================

@app.get("/api/crop/yield")
async def predict_crop_yield(
    crop: str, 
    latitude: float, 
    longitude: float, 
    soil_quality: str = "medium"
):
    """Predict crop yield based on weather"""
    try:
        from .crop_yield import crop_yield_predictor
        weather_data = await get_weather(latitude, longitude)
        result = crop_yield_predictor.predict_yield(crop, weather_data, soil_quality)
        return result
    except Exception as e:
        logger.error(f"Crop yield prediction failed: {e}")
        raise HTTPException(500, f"Prediction failed: {e}")

# ==================== TRANSLATION ENDPOINT ====================

@app.get("/api/translate")
async def translate_weather(latitude: float, longitude: float, lang: str = "en"):
    """Get weather data in Indian language"""
    try:
        from .language import language_service
        weather_data = await get_weather(latitude, longitude)
        advisory = build_advisory("Weather update", "general", weather_data)
        translated = language_service.translate_weather_data(advisory, lang)
        return translated
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(500, f"Translation failed: {e}")
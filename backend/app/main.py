from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Set, List
from datetime import datetime
import asyncio
import json
from loguru import logger

# Import existing services
from .config import settings
from .schemas import ChatRequest, ChatResponse, AlertRequest, AlertResponse
from .weather import get_weather, geocode_city
from .advisory import build_advisory
from .cache import cache_manager
from .rate_limiter import rate_limiter
from .llm_service import llm_service
from .risk_heatmap import heatmap_service

# Import crop services
from .crop_disease import crop_predictor
from .crop_yield import crop_yield_predictor
from .crop_recommendation import crop_recommender

# Import advanced services
from .flood_risk import flood_analyzer
from .lightning_tracker import lightning_tracker
from .weather_comparison import weather_comparison
from .reliability_score import reliability_calculator

# ===== IMPORT NEW SERVICES =====
from .imd_integration import imd_integration
from .emergency_broadcast import emergency_broadcast
from .disaster_response import disaster_response
from .weather_analytics import weather_analytics

# WebSocket manager
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.location_subscriptions: Dict[str, Set[str]] = {}
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
    logger.info("🚀 Starting WeatherGPT API v3.0...")
    logger.info("📊 Features: Weather, Flood, Lightning, Comparison, Reliability, IMD, Emergency, Disaster, Analytics")
    
    # Initialize WebSocket manager
    ws_manager = WebSocketManager()
    app.state.ws_manager = ws_manager
    
    logger.info("✅ WeatherGPT API started successfully")
    yield
    
    logger.info("🛑 Shutting down WeatherGPT API...")

app = FastAPI(
    title="WeatherGPT API",
    version="3.0.0",
    description="Advanced AI-Powered Weather Intelligence Platform with Real-time Analytics & Disaster Management",
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

# ==================== ROOT & HEALTH ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "name": "WeatherGPT",
        "version": "3.0.0",
        "status": "running",
        "features": [
            "real-time weather analytics",
            "multi-role advisory engine",
            "websocket alerts",
            "trend analysis",
            "risk scoring",
            "interactive map",
            "crop disease prediction",
            "lightning detection",
            "disaster risk assessment",
            "crop recommendations",
            "flood risk analysis",
            "lightning tracking",
            "weather comparison",
            "reliability score",
            "IMD data integration",
            "emergency broadcast",
            "disaster response",
            "historical analytics"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "weather_provider": "Open-Meteo + IMD",
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
    """Get current weather data with analytics"""
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

# ==================== CROP DISEASE ENDPOINT ====================

@app.get("/api/crop/disease")
async def predict_disease(latitude: float, longitude: float):
    """Predict crop disease risk based on weather"""
    try:
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

# ==================== CROP YIELD ENDPOINT ====================

@app.get("/api/crop/yield")
async def predict_crop_yield(
    crop: str, 
    latitude: float, 
    longitude: float, 
    soil_quality: str = "medium"
):
    """Predict crop yield based on weather"""
    try:
        weather_data = await get_weather(latitude, longitude)
        result = crop_yield_predictor.predict_yield(crop, weather_data, soil_quality)
        return result
    except Exception as e:
        logger.error(f"Crop yield prediction failed: {e}")
        raise HTTPException(500, f"Prediction failed: {e}")

# ==================== CROP RECOMMENDATION ENDPOINT ====================

@app.get("/api/crop/recommend")
async def recommend_crops(latitude: float, longitude: float, soil_type: str = "loam"):
    """Get crop recommendations based on weather"""
    try:
        weather_data = await get_weather(latitude, longitude)
        result = crop_recommender.recommend_crops(weather_data, soil_type)
        return result
    except Exception as e:
        logger.error(f"Crop recommendation failed: {e}")
        raise HTTPException(500, f"Crop recommendation failed: {e}")

# ==================== DISASTER ASSESSMENT ENDPOINT ====================

@app.get("/api/disaster/assess")
async def assess_disaster(latitude: float, longitude: float):
    """Assess disaster risks at location"""
    try:
        weather_data = await get_weather(latitude, longitude)
        from .disaster_assessment import disaster_assessor
        result = disaster_assessor.assess_risk(weather_data)
        return result
    except Exception as e:
        logger.error(f"Disaster assessment failed: {e}")
        raise HTTPException(500, f"Disaster assessment failed: {e}")

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

# ==================== LIGHTNING DETECTION ENDPOINT ====================

@app.get("/api/lightning")
async def check_lightning(latitude: float, longitude: float, radius: int = 50):
    """Check lightning risk at location"""
    try:
        result = await lightning_tracker.get_nearby_strikes(latitude, longitude, radius)
        return result
    except Exception as e:
        logger.error(f"Lightning detection failed: {e}")
        raise HTTPException(500, f"Lightning detection failed: {e}")

# ==================== FLOOD RISK ENDPOINT ====================

@app.get("/api/flood-risk")
async def get_flood_risk(latitude: float, longitude: float, name: str = ""):
    """Analyze flood risk at location"""
    try:
        result = await flood_analyzer.analyze_flood_risk(latitude, longitude, name)
        return result
    except Exception as e:
        logger.error(f"Flood risk analysis failed: {e}")
        raise HTTPException(500, f"Flood risk analysis failed: {e}")

# ==================== LIGHTNING TRACKING ENDPOINT ====================

@app.get("/api/lightning-track")
async def track_lightning(latitude: float, longitude: float, radius: int = 50):
    """Track lightning strikes near location"""
    try:
        result = await lightning_tracker.get_nearby_strikes(latitude, longitude, radius)
        return result
    except Exception as e:
        logger.error(f"Lightning tracking failed: {e}")
        raise HTTPException(500, f"Lightning tracking failed: {e}")

# ==================== WEATHER COMPARISON ENDPOINT ====================

@app.post("/api/compare-weather")
async def compare_weather(cities: List[Dict]):
    """Compare weather across multiple cities"""
    try:
        if len(cities) < 2:
            raise HTTPException(400, "Need at least 2 cities for comparison")
        if len(cities) > 5:
            raise HTTPException(400, "Maximum 5 cities can be compared")
        
        result = await weather_comparison.compare_cities(cities)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Weather comparison failed: {e}")
        raise HTTPException(500, f"Weather comparison failed: {e}")

# ==================== RELIABILITY SCORE ENDPOINT ====================

@app.get("/api/reliability")
async def get_reliability(latitude: float, longitude: float):
    """Get weather reliability score using 3-month historical analysis"""
    try:
        weather_data = await get_weather(latitude, longitude)
        result = reliability_calculator.calculate_reliability(weather_data, {
            "latitude": latitude,
            "longitude": longitude
        })
        return result
    except Exception as e:
        logger.error(f"Reliability calculation failed: {e}")
        raise HTTPException(500, f"Reliability calculation failed: {e}")

# ==================== NEW: IMD INTEGRATION ENDPOINT ====================

@app.get("/api/imd-data")
async def get_imd_data(latitude: float, longitude: float, name: str = ""):
    """Get IMD weather data with AI analytics"""
    try:
        result = await imd_integration.get_imd_data(latitude, longitude, name)
        return result
    except Exception as e:
        logger.error(f"IMD data fetch failed: {e}")
        raise HTTPException(500, f"IMD data fetch failed: {e}")

# ==================== NEW: EMERGENCY BROADCAST ENDPOINTS ====================

@app.post("/api/emergency/broadcast")
async def broadcast_emergency(alert: Dict):
    """Broadcast emergency alert"""
    try:
        result = await emergency_broadcast.broadcast_emergency(alert)
        return result
    except Exception as e:
        logger.error(f"Emergency broadcast failed: {e}")
        raise HTTPException(500, f"Emergency broadcast failed: {e}")

@app.get("/api/emergency/alerts")
async def get_active_alerts():
    """Get active emergency alerts"""
    try:
        return emergency_broadcast.get_active_alerts()
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(500, f"Failed to get alerts: {e}")

@app.get("/api/emergency/history")
async def get_alert_history(limit: int = 10):
    """Get alert history"""
    try:
        return emergency_broadcast.get_alert_history(limit)
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(500, f"Failed to get history: {e}")

# ==================== NEW: DISASTER RESPONSE ENDPOINT ====================

@app.post("/api/disaster/assess_response")
async def assess_disaster_response(latitude: float, longitude: float, disaster_type: str):
    """Assess disaster risk and response"""
    try:
        result = await disaster_response.assess_disaster(latitude, longitude, disaster_type)
        return result
    except Exception as e:
        logger.error(f"Disaster assessment failed: {e}")
        raise HTTPException(500, f"Disaster assessment failed: {e}")

# ==================== NEW: HISTORICAL ANALYTICS ENDPOINT ====================

@app.get("/api/analytics/historical")
async def get_historical_analysis(latitude: float, longitude: float, years: int = 10):
    """Get historical weather analytics"""
    try:
        result = await weather_analytics.get_historical_analysis(latitude, longitude, years)
        return result
    except Exception as e:
        logger.error(f"Historical analysis failed: {e}")
        raise HTTPException(500, f"Historical analysis failed: {e}")

# ==================== ERROR HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": 500,
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
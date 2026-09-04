from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime

class Location(BaseModel):
    latitude: float
    longitude: float
    name: str = "Selected location"

class WeatherResponse(BaseModel):
    location: Location
    current: dict
    hourly: dict
    daily: Optional[dict] = None
    derived: Optional[dict] = None
    source: str
    timestamp: Optional[str] = None

class WeatherRequest(BaseModel):
    latitude: float
    longitude: float
    force_refresh: bool = False

class AnalyticsRequest(BaseModel):
    latitude: float
    longitude: float
    hours: int = 24

class ChatRequest(BaseModel):
    question: str = Field(min_length=2)
    latitude: float
    longitude: float
    role: Literal["farmer", "disaster", "urban", "traveler", "general"] = "general"

class ChatResponse(BaseModel):
    answer: str
    evidence: List[str]
    actions: List[str]
    risk: str
    risk_scores: Optional[Dict[str, str]] = None
    confidence: str
    source: str
    trend: Optional[str] = None
    comfort: Optional[str] = None
    heat_index: Optional[float] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    advisory_time: Optional[str] = None

class AlertRequest(BaseModel):
    latitude: float
    longitude: float
    role: str = "general"

class AlertResponse(BaseModel):
    alert: bool
    risk: str
    risk_scores: Optional[Dict[str, str]] = None
    message: str
    evidence: List[str]
    actions: List[str]
    trend: Optional[str] = None
    timestamp: str
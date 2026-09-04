from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
from datetime import datetime
import asyncio
from loguru import logger

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.location_subscriptions: Dict[str, Set[str]] = {}  # client_id -> set of locations
        self.client_locations: Dict[str, dict] = {}  # client_id -> location
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """Connect a client"""
        self.active_connections[client_id] = websocket
        self.location_subscriptions[client_id] = set()
        logger.info(f"Client {client_id} connected")
    
    async def disconnect(self, client_id: str):
        """Disconnect a client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.location_subscriptions:
            del self.location_subscriptions[client_id]
        if client_id in self.client_locations:
            del self.client_locations[client_id]
        logger.info(f"Client {client_id} disconnected")
    
    async def subscribe_to_location(self, client_id: str, location: dict):
        """Subscribe client to location updates"""
        location_key = f"{location.get('latitude')}:{location.get('longitude')}"
        if client_id not in self.location_subscriptions:
            self.location_subscriptions[client_id] = set()
        self.location_subscriptions[client_id].add(location_key)
        self.client_locations[client_id] = location
        logger.info(f"Client {client_id} subscribed to location {location_key}")
    
    async def broadcast_weather_update(self, latitude: float, longitude: float, data: dict):
        """Broadcast weather update to subscribed clients"""
        location_key = f"{latitude}:{longitude}"
        message = {
            "type": "weather_update",
            "location": {"latitude": latitude, "longitude": longitude},
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for client_id, locations in self.location_subscriptions.items():
            if location_key in locations and client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to {client_id}: {e}")
    
    async def broadcast_global_alerts(self):
        """Broadcast global alerts to all connected clients"""
        from .weather import get_weather
        from .advisory import build_advisory
        
        # Check for severe weather at subscribed locations
        for client_id, location in self.client_locations.items():
            if client_id in self.active_connections:
                try:
                    lat = location.get("latitude")
                    lon = location.get("longitude")
                    if lat and lon:
                        weather_data = await get_weather(lat, lon)
                        advisory = build_advisory("Check alerts", "general", weather_data)
                        
                        if advisory.get("risk") in ["MODERATE", "HIGH"]:
                            await self.active_connections[client_id].send_json({
                                "type": "alert",
                                "risk": advisory["risk"],
                                "message": advisory["answer"],
                                "timestamp": datetime.utcnow().isoformat()
                            })
                except Exception as e:
                    logger.error(f"Alert broadcast error: {e}")
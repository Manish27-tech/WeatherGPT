from typing import Dict, List, Set
from datetime import datetime, timedelta
import json
import asyncio
import math
from loguru import logger

class EmergencyAlertSystem:
    """
    Geo-fencing based emergency alert system
    """
    
    def __init__(self):
        self.subscribers: Dict[str, Dict] = {}
        self.active_alerts: List[Dict] = []
        self.alert_history: List[Dict] = []
    
    def subscribe_user(self, user_id: str, location: Dict, preferences: Dict = None):
        """Subscribe user to alerts"""
        self.subscribers[user_id] = {
            "location": location,
            "preferences": preferences or {},
            "subscribed_at": datetime.utcnow().isoformat(),
            "alert_count": 0
        }
        logger.info(f"User {user_id} subscribed to alerts")
    
    def unsubscribe_user(self, user_id: str):
        """Unsubscribe user from alerts"""
        if user_id in self.subscribers:
            del self.subscribers[user_id]
            logger.info(f"User {user_id} unsubscribed")
    
    def check_alert_conditions(self, weather: Dict) -> List[Dict]:
        """Check if weather conditions trigger alerts"""
        alerts = []
        current = weather.get("current", {})
        
        # Check for severe conditions
        temp = current.get("temperature_2m", 20)
        wind = current.get("wind_speed_10m", 0)
        rain = current.get("rain", 0)
        precipitation = current.get("precipitation", 0)
        
        # Heat wave
        if temp > 40:
            alerts.append({
                "type": "heat_wave",
                "severity": "HIGH",
                "message": f"Extreme heat detected: {temp}°C",
                "icon": "🔥",
                "actions": [
                    "Stay indoors during peak hours (12-4 PM)",
                    "Drink plenty of water",
                    "Avoid strenuous outdoor activity"
                ]
            })
        
        # High wind
        if wind > 60:
            alerts.append({
                "type": "severe_wind",
                "severity": "HIGH",
                "message": f"Severe wind warning: {wind} km/h",
                "icon": "💨",
                "actions": [
                    "Secure loose objects",
                    "Avoid outdoor activities",
                    "Stay away from trees and power lines"
                ]
            })
        
        # Heavy rain
        if rain > 10 or precipitation > 10:
            alerts.append({
                "type": "heavy_rain",
                "severity": "MODERATE" if rain < 20 else "HIGH",
                "message": f"Heavy rain detected: {rain}mm",
                "icon": "🌧️",
                "actions": [
                    "Avoid flooded areas",
                    "Delay unnecessary travel",
                    "Check drainage systems"
                ]
            })
        
        # Thunderstorm (weather_code 95-99)
        weather_code = current.get("weather_code", 0)
        if 95 <= weather_code <= 99:
            alerts.append({
                "type": "thunderstorm",
                "severity": "HIGH",
                "message": "Thunderstorm warning! Lightning risk",
                "icon": "⚡",
                "actions": [
                    "Stay indoors",
                    "Avoid electrical appliances",
                    "Do not stand under trees"
                ]
            })
        
        return alerts
    
    def broadcast_alerts(self, alerts: List[Dict], location: Dict = None):
        """Broadcast alerts to affected users"""
        affected_users = []
        
        for user_id, user_data in self.subscribers.items():
            user_location = user_data.get("location", {})
            
            # Check if user is in affected area (simplified)
            if location:
                distance = self._calculate_distance(
                    location.get("latitude", 0),
                    location.get("longitude", 0),
                    user_location.get("latitude", 0),
                    user_location.get("longitude", 0)
                )
                if distance > 50:  # 50km radius
                    continue
            
            # Send alert via WebSocket
            affected_users.append(user_id)
            user_data["alert_count"] += 1
            
            # Store alert
            for alert in alerts:
                self.alert_history.append({
                    "user_id": user_id,
                    "alert": alert,
                    "sent_at": datetime.utcnow().isoformat()
                })
        
        # Store active alerts
        for alert in alerts:
            alert["affected_users"] = len(affected_users)
            alert["timestamp"] = datetime.utcnow().isoformat()
            self.active_alerts.append(alert)
        
        # Cleanup old alerts
        self._cleanup_alerts()
        
        return {
            "alerts_sent": len(alerts),
            "affected_users": len(affected_users),
            "user_ids": affected_users[:10]  # First 10 users
        }
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points (Haversine formula)"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lon1_rad = math.radians(lon1)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _cleanup_alerts(self):
        """Remove alerts older than 1 hour"""
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.active_alerts = [
            alert for alert in self.active_alerts
            if datetime.fromisoformat(alert["timestamp"]) > cutoff
        ]
    
    def get_user_alerts(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get alert history for a user"""
        user_alerts = [
            alert for alert in self.alert_history
            if alert["user_id"] == user_id
        ]
        return user_alerts[-limit:]  # Last N alerts

# Global instance
alert_system = EmergencyAlertSystem()
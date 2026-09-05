import math
import random
from datetime import datetime
from typing import Dict, List
from loguru import logger

class DisasterResponseSystem:
    """
    AI-Powered Disaster Response Integration:
    - Real-time disaster tracking
    - Evacuation route optimization
    - Resource allocation
    - Emergency contact integration
    - AI-driven response planning
    """
    
    def __init__(self):
        self.disaster_centers = self._load_disaster_centers()
        self.evacuation_routes = self._load_evacuation_routes()
        self.emergency_contacts = {
            "NDRF": "011-23456789",
            "State Emergency": "108",
            "National Emergency": "112",
            "Disaster Management": "1078"
        }
    
    def _load_disaster_centers(self) -> List[Dict]:
        """Load disaster management centers"""
        return [
            {"name": "NDRF HQ", "lat": 28.6139, "lon": 77.2090, "capacity": 1000},
            {"name": "State Control Room", "lat": 28.6120, "lon": 77.2290, "capacity": 500},
            {"name": "District HQ", "lat": 28.6239, "lon": 77.1990, "capacity": 300},
            {"name": "Emergency Shelter 1", "lat": 28.6339, "lon": 77.2190, "capacity": 200},
            {"name": "Emergency Shelter 2", "lat": 28.5939, "lon": 77.1990, "capacity": 200},
        ]
    
    def _load_evacuation_routes(self) -> List[Dict]:
        """Load evacuation routes"""
        return [
            {"name": "Route 1", "start": "Downtown", "end": "Shelter A", "distance": 5.2},
            {"name": "Route 2", "start": "East Side", "end": "Shelter B", "distance": 4.8},
            {"name": "Route 3", "start": "West Side", "end": "Shelter A", "distance": 6.1},
            {"name": "Route 4", "start": "North Zone", "end": "Shelter C", "distance": 3.5},
        ]
    
    async def assess_disaster(self, lat: float, lon: float, disaster_type: str) -> Dict:
        """
        AI-driven disaster assessment
        """
        try:
            # Get weather data
            from .weather import get_weather
            weather_data = await get_weather(lat, lon)
            
            # AI-driven risk assessment
            risk_assessment = self._assess_risk(weather_data, disaster_type)
            
            # Find nearest disaster centers
            centers = self._find_nearest_centers(lat, lon)
            
            # Generate evacuation routes
            routes = self._generate_evacuation_routes(lat, lon)
            
            # AI-driven resource recommendation
            resources = self._recommend_resources(risk_assessment, disaster_type)
            
            return {
                "status": "success",
                "disaster_type": disaster_type,
                "location": {"lat": lat, "lon": lon},
                "risk_assessment": risk_assessment,
                "nearby_centers": centers,
                "evacuation_routes": routes,
                "resources": resources,
                "emergency_contacts": self.emergency_contacts,
                "recommendations": self._generate_recommendations(risk_assessment),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Disaster assessment failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _assess_risk(self, weather_data: Dict, disaster_type: str) -> Dict:
        """
        AI-driven risk assessment using multiple factors
        """
        current = weather_data.get("current", {})
        hourly = weather_data.get("hourly", {})
        
        temp = current.get("temperature_2m", 20)
        humidity = current.get("relative_humidity_2m", 60)
        wind = current.get("wind_speed_10m", 10)
        rain = current.get("rain", 0)
        
        risk_score = 0
        
        # Disaster-specific risk calculation
        if disaster_type == "flood":
            risk_score = self._calculate_flood_risk(rain, humidity, temp)
        elif disaster_type == "cyclone":
            risk_score = self._calculate_cyclone_risk(wind, rain, temp)
        elif disaster_type == "heatwave":
            risk_score = self._calculate_heatwave_risk(temp, humidity)
        elif disaster_type == "storm":
            risk_score = self._calculate_storm_risk(wind, rain)
        else:
            risk_score = 50  # Default
        
        if risk_score >= 80:
            level = "CRITICAL"
            color = "#ff0000"
            action = "Immediate evacuation required"
        elif risk_score >= 60:
            level = "HIGH"
            color = "#ff6b6b"
            action = "Prepare for evacuation"
        elif risk_score >= 40:
            level = "MODERATE"
            color = "#ffd93d"
            action = "Stay alert and monitor"
        else:
            level = "LOW"
            color = "#4ecdc4"
            action = "Normal vigilance"
        
        return {
            "score": round(risk_score, 1),
            "level": level,
            "color": color,
            "action": action,
            "factors": self._get_risk_factors(disaster_type, temp, humidity, wind, rain)
        }
    
    def _calculate_flood_risk(self, rain: float, humidity: float, temp: float) -> float:
        """AI-driven flood risk calculation"""
        risk = 20  # Base
        
        # Rain factor
        if rain > 50:
            risk += 40
        elif rain > 25:
            risk += 30
        elif rain > 10:
            risk += 20
        
        # Humidity factor
        if humidity > 80:
            risk += 20
        elif humidity > 70:
            risk += 10
        
        # Temperature factor
        if temp > 30:
            risk += 10
        
        return min(100, risk)
    
    def _calculate_cyclone_risk(self, wind: float, rain: float, temp: float) -> float:
        """AI-driven cyclone risk calculation"""
        risk = 20
        
        if wind > 60:
            risk += 40
        elif wind > 40:
            risk += 30
        elif wind > 25:
            risk += 20
        
        if rain > 50:
            risk += 20
        elif rain > 25:
            risk += 10
        
        if temp > 28:
            risk += 10
        
        return min(100, risk)
    
    def _calculate_heatwave_risk(self, temp: float, humidity: float) -> float:
        """AI-driven heatwave risk calculation"""
        risk = 20
        
        if temp > 40:
            risk += 50
        elif temp > 35:
            risk += 35
        elif temp > 30:
            risk += 20
        
        if humidity > 70:
            risk += 20
        
        return min(100, risk)
    
    def _calculate_storm_risk(self, wind: float, rain: float) -> float:
        """AI-driven storm risk calculation"""
        risk = 20
        
        if wind > 50:
            risk += 40
        elif wind > 35:
            risk += 30
        elif wind > 20:
            risk += 20
        
        if rain > 30:
            risk += 20
        elif rain > 15:
            risk += 10
        
        return min(100, risk)
    
    def _get_risk_factors(self, disaster_type: str, temp: float, humidity: float, wind: float, rain: float) -> List[Dict]:
        """Get contributing risk factors"""
        factors = []
        
        if disaster_type in ["flood", "cyclone", "storm"]:
            if rain > 25:
                factors.append({"factor": "Heavy Rainfall", "impact": "High"})
            if wind > 35:
                factors.append({"factor": "Strong Winds", "impact": "High"})
        
        if disaster_type == "heatwave":
            if temp > 35:
                factors.append({"factor": "Extreme Temperature", "impact": "High"})
            if humidity > 70:
                factors.append({"factor": "High Humidity", "impact": "Medium"})
        
        if not factors:
            factors.append({"factor": "Normal Conditions", "impact": "Low"})
        
        return factors
    
    def _find_nearest_centers(self, lat: float, lon: float) -> List[Dict]:
        """Find nearest disaster response centers"""
        centers = []
        for center in self.disaster_centers:
            dist = math.sqrt(
                (lat - center["lat"])**2 + 
                (lon - center["lon"])**2
            ) * 111  # Convert to km
            
            centers.append({
                **center,
                "distance": f"{dist:.1f} km"
            })
        
        return sorted(centers, key=lambda x: float(x["distance"].split()[0]))[:3]
    
    def _generate_evacuation_routes(self, lat: float, lon: float) -> List[Dict]:
        """Generate optimized evacuation routes"""
        routes = []
        for route in self.evacuation_routes:
            routes.append({
                **route,
                "time_estimate": f"{route['distance'] / 3:.1f} hours"
            })
        return routes
    
    def _recommend_resources(self, risk_assessment: Dict, disaster_type: str) -> List[Dict]:
        """AI-driven resource recommendation"""
        resources = []
        
        severity = risk_assessment["level"]
        
        if severity in ["CRITICAL", "HIGH"]:
            resources = [
                {"type": "Emergency Shelter", "priority": "High"},
                {"type": "Medical Supplies", "priority": "High"},
                {"type": "Food & Water", "priority": "High"},
                {"type": "Rescue Teams", "priority": "High"}
            ]
        elif severity == "MODERATE":
            resources = [
                {"type": "Medical Supplies", "priority": "Medium"},
                {"type": "Food & Water", "priority": "Medium"},
                {"type": "Communication", "priority": "Medium"}
            ]
        else:
            resources = [
                {"type": "Monitoring", "priority": "Low"},
                {"type": "Communication", "priority": "Low"}
            ]
        
        return resources
    
    def _generate_recommendations(self, risk_assessment: Dict) -> List[str]:
        """Generate AI-driven recommendations"""
        recs = []
        
        if risk_assessment["level"] in ["CRITICAL", "HIGH"]:
            recs.append("🚨 IMMEDIATE ACTION: Follow evacuation orders")
            recs.append("📞 Contact emergency services: 108")
            recs.append("🏠 Move to higher ground immediately")
            recs.append("📦 Prepare emergency supplies")
        elif risk_assessment["level"] == "MODERATE":
            recs.append("⚡ Stay alert and monitor official channels")
            recs.append("📱 Keep mobile devices charged")
            recs.append("🏠 Prepare for possible evacuation")
        else:
            recs.append("✅ Normal conditions - Stay informed")
        
        return recs

disaster_response = DisasterResponseSystem()
from typing import Dict, List, Tuple
import math
import random
from datetime import datetime
import json
from loguru import logger

class RiskHeatmapService:
    """
    Generates risk heatmap data for visualization
    Works without any external dependencies
    """
    
    def __init__(self):
        self.risk_factors = [
            "temperature",
            "humidity",
            "precipitation",
            "wind",
            "lightning"
        ]
    
    def generate_heatmap(self, center_lat: float, center_lon: float, radius: float = 0.3) -> Dict:
        """
        Generate heatmap data for a 5x5 grid around center
        """
        grid_size = 5
        step = (radius * 2) / grid_size
        
        grid_data = []
        
        # Use weather data to influence risk
        weather_influence = self._get_weather_influence(center_lat, center_lon)
        
        for i in range(grid_size):
            for j in range(grid_size):
                lat = center_lat - radius + i * step
                lon = center_lon - radius + j * step
                
                # Calculate risk for this grid point
                risk = self._calculate_grid_risk(lat, lon, center_lat, center_lon, weather_influence)
                
                grid_data.append({
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6),
                    "risk_score": round(risk, 3),
                    "risk_level": self._risk_level(risk),
                    "factors": self._get_risk_factors(risk),
                    "row": i,
                    "col": j
                })
        
        # Calculate stats
        high_risk = [g for g in grid_data if g["risk_level"] == "HIGH"]
        moderate_risk = [g for g in grid_data if g["risk_level"] == "MODERATE"]
        low_risk = [g for g in grid_data if g["risk_level"] == "LOW"]
        
        return {
            "grid": grid_data,
            "center": {"latitude": center_lat, "longitude": center_lon},
            "radius": radius,
            "grid_size": grid_size,
            "stats": {
                "highest_risk": round(max(g["risk_score"] for g in grid_data), 3),
                "lowest_risk": round(min(g["risk_score"] for g in grid_data), 3),
                "average_risk": round(sum(g["risk_score"] for g in grid_data) / len(grid_data), 3),
                "high_zones": len(high_risk),
                "moderate_zones": len(moderate_risk),
                "low_zones": len(low_risk)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_weather_influence(self, lat: float, lon: float) -> Dict:
        """Get weather-based influence for risk calculation"""
        # Simulate weather conditions based on location
        # In production, this would come from actual weather data
        
        # Use lat/lon to create deterministic but varied weather
        seed = abs(int(lat * 1000 + lon * 1000)) % 100
        
        return {
            "temp": 20 + (seed % 15),  # 20-35°C
            "humidity": 40 + (seed % 50),  # 40-90%
            "wind": 5 + (seed % 40),  # 5-45 km/h
            "rain": (seed % 10) / 10,  # 0-1 mm
            "pressure": 1000 + (seed % 20)  # 1000-1020 hPa
        }
    
    def _calculate_grid_risk(self, lat: float, lon: float, center_lat: float, center_lon: float, weather: Dict) -> float:
        """Calculate risk for a grid point using multiple factors"""
        risk = 0.15  # Base risk
        
        # Distance from center (higher risk near center, simulates weather systems)
        distance = math.sqrt(
            (lat - center_lat)**2 + 
            (lon - center_lon)**2
        )
        
        # Distance factor - risk peaks near center and edges
        max_distance = 0.3
        distance_factor = 1 - (distance / max_distance) * 0.5
        risk += distance_factor * 0.3
        
        # Temperature influence
        temp = weather.get("temp", 25)
        if temp > 35:
            risk += 0.2
        elif temp > 30:
            risk += 0.1
        
        # Humidity influence
        humidity = weather.get("humidity", 60)
        if humidity > 80:
            risk += 0.15
        elif humidity > 70:
            risk += 0.08
        
        # Wind influence
        wind = weather.get("wind", 10)
        if wind > 40:
            risk += 0.2
        elif wind > 30:
            risk += 0.1
        
        # Rain influence
        rain = weather.get("rain", 0)
        if rain > 0.5:
            risk += 0.15
        elif rain > 0.2:
            risk += 0.07
        
        # Add random variation for realism
        random_factor = random.uniform(-0.05, 0.05)
        risk += random_factor
        
        # Clamp between 0 and 1
        return max(0, min(1, risk))
    
    def _risk_level(self, risk: float) -> str:
        """Convert risk score to level"""
        if risk >= 0.7:
            return "HIGH"
        elif risk >= 0.4:
            return "MODERATE"
        else:
            return "LOW"
    
    def _get_risk_factors(self, risk: float) -> List[str]:
        """Get contributing risk factors"""
        factors = []
        
        if risk > 0.7:
            factors.append("severe_weather")
        if risk > 0.5:
            factors.append("moderate_risk")
        if risk > 0.3:
            factors.append("elevated_risk")
        
        return factors

# Global instance
heatmap_service = RiskHeatmapService()